"""UltraPlan V2 W02 -- the only durable runtime.

SQLite is canonical state: an ordered event ledger, mission snapshots, and a
transactional outbox. rig-loop is the only transition authority: every legal
state move goes through apply_command(), which appends the event and its outbox
rows in ONE transaction, or writes nothing. A command that was acknowledged can
never be lost, and can never produce a second effect.

Stdlib only. No threads: one writer holds the DB; fencing is by lease token.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
import uuid
from pathlib import Path

SCHEMA_VERSION = 1

LEGAL = {  # mission state machine -- anything else is an illegal transition
    "created":  {"running", "cancelled"},
    "running":  {"parked", "completed", "failed", "cancelled", "abandoned", "uncertain"},
    "parked":   {"running", "cancelled", "abandoned"},
    "uncertain": {"running", "abandoned"},
    "completed": set(),
    "failed":   {"running"},            # retry path only via retry_exhausted check
    "cancelled": set(),
    "abandoned": set(),
}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT UNIQUE NOT NULL,
  mission_id TEXT NOT NULL,
  command_id TEXT NOT NULL UNIQUE,
  type TEXT NOT NULL,
  payload TEXT NOT NULL,
  prev_hash TEXT NOT NULL,
  hash TEXT NOT NULL,
  ts REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS outbox (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mission_id TEXT NOT NULL,
  event_seq INTEGER NOT NULL REFERENCES events(seq),
  effect_kind TEXT NOT NULL,
  payload TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',   -- pending|claimed|done|failed|uncertain
  fence TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS missions (
  mission_id TEXT PRIMARY KEY,
  state TEXT NOT NULL,
  seq INTEGER NOT NULL,
  hash TEXT NOT NULL,
  budget TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS fences (
  key TEXT PRIMARY KEY, token TEXT NOT NULL, epoch INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
"""

# test seam: tests set CRASH_HOOK to a callable that hard-exits the process and
# CRASH_PHASE to the point it fires at, proving transactional atomicity under kill
# -9. Production code never sets them.
CRASH_HOOK = None
CRASH_PHASE = None  # None | "before_commit" | "after_commit"


class LedgerError(Exception):
    pass


class StaleFence(LedgerError): pass
class IllegalTransition(LedgerError): pass
class SequenceConflict(LedgerError): pass
class ReceiptlessClaim(LedgerError): pass


class BudgetExceeded(LedgerError):
    pass


def _h(*parts) -> str:
    return hashlib.sha256("\x1f".join(str(p) for p in parts).encode()).hexdigest()


class Ledger:
    def __init__(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path), isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript(_SCHEMA)
        self.db.execute("INSERT OR IGNORE INTO meta VALUES ('schema_version', ?)", (str(SCHEMA_VERSION),))

    # -- fences -------------------------------------------------------------
    def acquire_fence(self, key: str, token: str) -> int:
        """New holder supersedes the old token; epoch monotonically invalidates it."""
        row = self.db.execute("SELECT token, epoch FROM fences WHERE key=?", (key,)).fetchone()
        epoch = (row["epoch"] + 1) if row else 1
        self.db.execute("INSERT INTO fences(key,token,epoch) VALUES(?,?,?) "
                        "ON CONFLICT(key) DO UPDATE SET token=excluded.token, epoch=excluded.epoch",
                        (key, token, epoch))
        return epoch

    def check_fence(self, key: str, token: str) -> int:
        row = self.db.execute("SELECT token, epoch FROM fences WHERE key=?", (key,)).fetchone()
        if row is None or row["token"] != token:
            raise StaleFence("writer fence %s held by another token" % key)
        return row["epoch"]

    # -- commands -----------------------------------------------------------
    def apply_command(self, mission_id: str, ctype: str, payload: dict, *,
                      command_id: str | None = None, idempotency_key: str | None = None,
                      expected_seq: int | None = None, fence_key: str | None = None,
                      fence_token: str | None = None, effects: list[dict] | None = None,
                      ts: float | None = None) -> dict:
        """One transaction: idempotency -> sequence -> fence -> legality -> event
        + outbox. Returns the event row (duplicate returns the original)."""
        command_id = command_id or str(uuid.uuid4())
        if idempotency_key:
            dup = self.db.execute(
                "SELECT * FROM events WHERE mission_id=? AND payload LIKE ?",
                (mission_id, '%%"idempotency_key": "%s"%%' % idempotency_key)).fetchone()
            if dup:
                return dict(dup)
        cur = self.db.execute("SELECT seq, hash FROM events WHERE mission_id=? ORDER BY seq DESC LIMIT 1",
                              (mission_id,))
        last = cur.fetchone()
        head_seq = last["seq"] if last else 0
        head_hash = last["hash"] if last else _h("genesis", mission_id)
        if expected_seq is not None and expected_seq != head_seq:
            raise SequenceConflict("expected_seq %r but head is %r" % (expected_seq, head_seq))
        if fence_key:
            self.check_fence(fence_key, fence_token or "")
        state = self._mission_state(mission_id)
        etype = self._event_type(ctype, payload)
        if state is None:
            if ctype != "mission.create":
                raise IllegalTransition("no mission %s; only mission.create can birth one" % mission_id)
            new_state = "created"
        elif ctype in ("mission.cancel", "mission.abandon"):
            new_state = {"mission.cancel": "cancelled", "mission.abandon": "abandoned"}[ctype]
        elif ctype == "stage.park":
            new_state = "parked"
        elif ctype == "stage.resume":
            new_state = "running"
        elif ctype == "mission.retry_exhausted":
            new_state = "abandoned"
        elif ctype == "reconcile.uncertain":
            new_state = "uncertain" if state in ("uncertain", "running") else state
        elif ctype in ("approval.grant", "approval.deny", "approval.consume"):
            new_state = state          # approvals never move the mission; asking is
                                       # not starting
        elif ctype in ("stage.advance", "receipt.attach", "forecast.register", "forecast.settle",
                       "cell.dispatch", "worker.report"):
            new_state = "running" if state == "created" else state
            if state in ("completed", "cancelled", "abandoned"):
                raise IllegalTransition("%s is terminal; refusing %s" % (state, ctype))
            if state == "parked" and ctype not in ("approval.grant", "approval.deny"):
                raise IllegalTransition("parked missions need stage.resume first, not %s" % ctype)
        elif ctype == "mission.complete":
            new_state = "completed"
        else:
            raise IllegalTransition("unknown command type %r" % ctype)
        if state is not None and new_state != state and new_state not in LEGAL.get(state, set()):
            raise IllegalTransition("%s -> %s is not a legal transition" % (state, new_state))
        self._policy_check(mission_id, ctype, payload)
        payload = dict(payload)
        payload.setdefault("idempotency_key", idempotency_key or command_id)
        payload.setdefault("target_state", new_state)
        budget = (payload.get("budget") or {}) if ctype == "mission.create" else {}
        seq = head_seq + 1
        event_id = str(uuid.uuid4())
        ts_val = ts if ts is not None else time.time()   # ONE clock read: stored row and hash agree
        ev_hash = _h(event_id, mission_id, command_id, etype, json.dumps(payload, sort_keys=True),
                     head_hash, ts_val)
        try:
            self.db.execute("BEGIN IMMEDIATE")
            self.db.execute(
                "INSERT INTO events(event_id,mission_id,command_id,type,payload,prev_hash,hash,ts) "
                "VALUES(?,?,?,?,?,?,?,?)",
                (event_id, mission_id, command_id, etype, json.dumps(payload, sort_keys=True),
                 head_hash, ev_hash, ts_val))
            for eff in (effects or []):
                self.db.execute(
                    "INSERT INTO outbox(mission_id,event_seq,effect_kind,payload,fence) VALUES(?,?,?,?,?)",
                    (mission_id, seq, eff["kind"], json.dumps(eff, sort_keys=True), fence_key or "none"))
            self.db.execute("INSERT INTO missions(mission_id,state,seq,hash,budget) VALUES(?,?,?,?,?) "
                            "ON CONFLICT(mission_id) DO UPDATE SET "
                            "state=excluded.state, seq=excluded.seq, hash=excluded.hash",
                            (mission_id, new_state, seq, ev_hash, json.dumps(budget, sort_keys=True)))
            if CRASH_PHASE == "before_commit":
                CRASH_HOOK()
            self.db.execute("COMMIT")
            if CRASH_PHASE == "after_commit":
                CRASH_HOOK()
        except sqlite3.IntegrityError as exc:  # duplicate command_id race
            self.db.execute("ROLLBACK")
            row = self.db.execute("SELECT * FROM events WHERE command_id=?", (command_id,)).fetchone()
            if row:
                return dict(row)
            raise LedgerError(str(exc))
        except BaseException:
            try: self.db.execute("ROLLBACK")
            except Exception: pass
            raise
        return {"seq": seq, "event_id": event_id, "mission_id": mission_id, "command_id": command_id,
                "type": etype, "payload": json.dumps(payload, sort_keys=True),
                "prev_hash": head_hash, "hash": ev_hash}

    SPIES = {"worker.report": ("cost_usd", "tool_calls", "wallclock_seconds")}

    def _policy_check(self, mission_id: str, ctype: str, payload: dict) -> None:
        """Budgets, decision counters and approval consumption, evaluated BEFORE
        the event is written. Budgets are inherited: a child without its own
        budget draws from the parent's remaining envelope."""
        if ctype in ("mission.complete", "forecast.settle"):
            # receipts-before-settlement: a score/completion claim with zero
            # attached evidence events is a claim from nothing.
            n = self.db.execute(
                "SELECT COUNT(*) c FROM events WHERE mission_id=? AND type='receipt.attached'",
                (mission_id,)).fetchone()["c"]
            if n == 0:
                raise ReceiptlessClaim("%s refused: mission has zero receipt.attach events -- evidence before the claim" % ctype)
        bud, owner = self._effective_budget(mission_id)
        if bud:
            if ctype == "mission.create":
                return
            spent = self._spent(owner)
            for field, key in (("cost_usd", "usd"), ("tool_calls", "tool_calls"),
                               ("wallclock_seconds", "wallclock_seconds")):
                inc = float((payload.get("meter") or {}).get(field, 0) or 0)
                cap = bud.get(key)
                if cap is not None and spent.get(field, 0) + inc > float(cap):
                    raise BudgetExceeded(
                        "%s would spend %s=%s of budget %s=%s"
                        % (ctype, field, spent.get(field, 0) + inc, key, cap))
        if ctype in ("worker.report", "cell.dispatch", "stage.advance"):
            meter = payload.get("meter") or {}
            for field in self.SPIES[ctype] if ctype in self.SPIES else ():
                pass
        if ctype == "approval.grant":
            nonce = (payload.get("approval") or {}).get("nonce")
            if not nonce:
                raise IllegalTransition("approval.grant without a nonce: nothing to make single-use")
            dup = self.db.execute(
                "SELECT COUNT(*) c FROM events WHERE type='approval.granted' AND payload LIKE ?",
                ('%%"nonce": "%s"%%' % nonce,)).fetchone()
            if dup and dup["c"]:
                raise IllegalTransition("approval nonce already consumed: a used approval is not a standing permission")
            # the decision cap counts grants, enforced AT the grant: a budget of
            # N human decisions means the (N+1)th ask cannot be self-approved
            cap = (bud or {}).get("mike_decisions")
            if cap is not None and self._decisions_used(owner) >= float(cap):
                raise BudgetExceeded("mike_decisions budget %s exhausted before this grant" % cap)

    def _effective_budget(self, mission_id: str):
        """(budget, owner): the mission's own budget, else the nearest ancestor's --
        and spend is measured over the OWNER's whole subtree, so a child cannot
        launder the parent's cap."""
        row = self.db.execute("SELECT budget FROM missions WHERE mission_id=?", (mission_id,)).fetchone()
        own = json.loads(row["budget"]) if row and row["budget"] else None
        if own:
            return own, mission_id
        parent = self.db.execute(
            "SELECT mission_id FROM events WHERE type='mission.created' AND payload LIKE ?",
            ('%%"children": ["%s"%%' % mission_id,)).fetchone()
        return self._effective_budget(parent["mission_id"]) if parent else (None, mission_id)

    def _family(self, root: str, seen=None) -> set:
        seen = seen or set()
        if root in seen:
            return seen
        seen.add(root)
        for r in self.db.execute("SELECT payload FROM events WHERE type='mission.created' AND mission_id=?", (root,)):
            for child in (json.loads(r["payload"]).get("children") or []):
                self._family(str(child), seen)
        return seen

    def _spent(self, root: str):
        tot = {"cost_usd": 0.0, "tool_calls": 0.0, "wallclock_seconds": 0.0}
        for mid in self._family(root):
            for r in self.db.execute(
                    "SELECT payload FROM events WHERE mission_id=? AND type IN "
                    "('worker.reported','cell.dispatched','stage.advanced')", (mid,)):
                m = json.loads(r["payload"]).get("meter") or {}
                for k in tot:
                    tot[k] += float(m.get(k, 0) or 0)
        return tot

    def _decisions_used(self, root: str) -> int:
        return sum(self.db.execute(
            "SELECT COUNT(*) c FROM events WHERE mission_id=? AND type='approval.granted'",
            (mid,)).fetchone()["c"] for mid in self._family(root))

    def set_budget(self, mission_id: str, budget: dict):
        self.db.execute("UPDATE missions SET budget=? WHERE mission_id=?",
                        (json.dumps(budget, sort_keys=True), mission_id))

    def _mission_state(self, mission_id):
        row = self.db.execute("SELECT state FROM missions WHERE mission_id=?", (mission_id,)).fetchone()
        return row["state"] if row else None

    @staticmethod
    def _event_type(ctype, payload):
        return {"mission.create": "mission.created", "stage.advance": "stage.advanced",
                "stage.park": "mission.parked", "stage.resume": "mission.resumed",
                "mission.cancel": "mission.cancelled", "mission.abandon": "mission.abandoned",
                "mission.retry_exhausted": "mission.abandoned",
                "reconcile.uncertain": "mission.uncertain", "receipt.attach": "receipt.attached",
                "forecast.register": "forecast.registered", "forecast.settle": "forecast.settled",
                "cell.dispatch": "cell.dispatched", "worker.report": "worker.reported",
                "approval.grant": "approval.granted", "approval.deny": "approval.denied",
                "approval.consume": "approval.consumed",
                "mission.complete": "mission.completed"}.get(ctype)

    # -- effects ------------------------------------------------------------
    def claim_effects(self, fence_key: str, fence_token: str) -> list[dict]:
        """A worker with a live fence claims pending effects atomically."""
        self.check_fence(fence_key, fence_token)
        rows = self.db.execute(
            "SELECT * FROM outbox WHERE status='pending' AND mission_id IN "
            "(SELECT mission_id FROM missions) ORDER BY id").fetchall()
        out = []
        for r in rows:
            self.db.execute("UPDATE outbox SET status='claimed', fence=? WHERE id=? AND status='pending'",
                            (fence_key + ":" + fence_token, r["id"]))
            if self.db.execute("SELECT changes()").fetchone()[0]:
                out.append(dict(r))
        return out

    def complete_effect(self, outbox_id: int, status: str, evidence: dict | None = None):
        assert status in ("done", "failed", "uncertain")
        self.db.execute("UPDATE outbox SET status=?, payload=json_insert(payload, '$.receipt', ?) WHERE id=?",
                        (status, json.dumps(evidence or {}), outbox_id))

    # -- integrity ----------------------------------------------------------
    def verify_chain(self, mission_id: str) -> bool:
        prev = _h("genesis", mission_id)
        for r in self.db.execute("SELECT * FROM events WHERE mission_id=? ORDER BY seq", (mission_id,)):
            if r["prev_hash"] != prev:
                return False
            if r["hash"] != _h(r["event_id"], r["mission_id"], r["command_id"], r["type"],
                               r["payload"], r["prev_hash"], r["ts"]):
                return False
            prev = r["hash"]
        return True

    def rebuild_projection(self, mission_id: str) -> dict:
        """State is DERIVED from events; this proves the projection can be rebuilt
        to the identical head hash from a cold replay."""
        state, seq, head = None, 0, _h("genesis", mission_id)
        for r in self.db.execute("SELECT * FROM events WHERE mission_id=? ORDER BY seq", (mission_id,)):
            state = json.loads(r["payload"]).get("target_state", state)
            seq, head = r["seq"], r["hash"]
        return {"mission_id": mission_id, "state": state, "seq": seq, "hash": head}
