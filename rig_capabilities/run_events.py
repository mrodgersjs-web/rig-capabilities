"""Append-only run-events ledger (s7).

SQLite enforces the contract natively — DB constraints over app code:
  * PRIMARY KEY (run_id, seq): one row per sequence number, per run.
  * BEFORE UPDATE / BEFORE DELETE triggers RAISE(ABORT): even the DBA role
    over this connection cannot rewrite or drop a row.
  * a SHA-256 hash chain (prev_hash -> canonical row bytes): replay
    reconstruction detects ANY out-of-band tampering with the file itself.
Transition validation happens at append AND verify time: a transition is
legal only if replay of the current ledger says so (stage order, no skips,
no un-doing a done run, park/resume coherence), and verify_chain revalidates
every stored row — a directly-INSERTed illegal event blocks seal/verify.
ProofPacket binding: seal() pins head seq/hash/state, canonical-hashes the
whole packet body, and appends that digest to an OUT-OF-TREE anchor ledger
(default ~/.rig/run_events/, outside the DB's write boundary); verify()
re-reads and recomputes everything and requires the anchor.

GUARANTEE (precise): the ledger is append-only against anything that
cannot DDL (DB-level triggers), tamper-evident against partial/out-of-band
edits (hash chain revalidated row-by-row by verify_chain), and re-hash
forgery of a sealed packet is caught by the out-of-tree anchor.
RESIDUAL TRUST (honest): hashes are unkeyed; an attacker with full write
access to BOTH the database file and the out-of-tree anchor (i.e. the
whole filesystem/user) can recompute everything. Defeating that needs a
keyed signature or a second machine — the same named residual as
commit_gate's certifier anchor.

Idempotence: writers retry on PRIMARY KEY collision (concurrent appends get
distinct seqs, never a lost or duplicated event).
"""
from __future__ import annotations
import hashlib
import hmac
import json
import sqlite3
import time
from pathlib import Path

SCHEMA_VERSION = 1
GENESIS = "0" * 64
KINDS = {"declare", "stage_pass", "stage_fail", "park", "resume", "commit"}


class TransitionError(ValueError):
    pass

def _norm(sql: str) -> str:
    return " ".join(sql.split()).rstrip(";").strip()


# Single source of truth: the SAME statements connect() executes define
# the canonical shapes. IF NOT EXISTS trusts whatever already occupies
# these names — a hostile or older database can carry same-named no-op
# triggers and every mutation sails through — so connect() validates the
# actual sqlite_master definitions and fails closed on divergence.
_DDL_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS run_events (
    run_id TEXT    NOT NULL,
    seq    INTEGER NOT NULL,
    ts     REAL    NOT NULL,
    kind   TEXT    NOT NULL,
    stage  TEXT,
    payload TEXT   NOT NULL DEFAULT '',
    prev_hash TEXT NOT NULL,
    hash      TEXT NOT NULL,
    PRIMARY KEY (run_id, seq)
)""",
    """CREATE TRIGGER IF NOT EXISTS run_events_no_update
BEFORE UPDATE ON run_events
BEGIN SELECT RAISE(ABORT, 'run_events is append-only'); END""",
    """CREATE TRIGGER IF NOT EXISTS run_events_no_delete
BEFORE DELETE ON run_events
BEGIN SELECT RAISE(ABORT, 'run_events is append-only'); END""",
]
# sqlite strips "IF NOT EXISTS" from the stored schema text; strip it from
# the source before comparison so identical schemas compare identical.
_CANON = {s.split()[5]: _norm(s.replace(" IF NOT EXISTS", ""))
          for s in _DDL_STATEMENTS}


def _verify_schema(con: sqlite3.Connection) -> None:
    have = {name: _norm(sql) for name, sql in con.execute(
        "SELECT name, sql FROM sqlite_master "
        "WHERE name IN ('run_events','run_events_no_update','run_events_no_delete')")}
    for name, canon in _CANON.items():
        if have.get(name) is None:
            raise RuntimeError(f"ledger schema object {name!r} is missing")
        if have[name] != canon:
            raise RuntimeError(f"ledger schema object {name!r} is not canonical")
    # an EXTRA trigger (e.g. BEFORE INSERT RAISE(IGNORE)) silently voids
    # appends while returning a valid-looking receipt: no surprises allowed
    extra = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='trigger' "
        "AND tbl_name='run_events' AND name NOT IN "
        "('run_events_no_update','run_events_no_delete')")]
    if extra:
        raise RuntimeError(f"unexpected trigger(s) on run_events: {extra}")


def connect(path: str) -> sqlite3.Connection:
    """Open an append-only ledger; fail closed on any schema divergence.

    Inspect BEFORE touching DDL: a pre-existing schema must already be
    fully canonical (a dropped trigger is tampering, not something to
    silently repair; a poisoned one must not be half-fixed on the way to
    the raise). Only a pristine database with no ledger objects at all
    gets created.
    """
    con = sqlite3.connect(path)
    con.isolation_level = None  # manual BEGIN IMMEDIATE in append()
    con.execute("PRAGMA synchronous=FULL")   # durability before ack
    con.execute("PRAGMA busy_timeout=5000")
    existing = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master "
        "WHERE name IN ('run_events','run_events_no_update','run_events_no_delete')")]
    if existing:
        _verify_schema(con)  # verify the COMPLETE set; no DDL executed
    else:
        con.executescript(";\n".join(_DDL_STATEMENTS) + ";")
        _verify_schema(con)
    return con

def _canon(row: tuple) -> str:
    return json.dumps({"run_id": row[0], "seq": row[1], "ts": row[2],
                       "kind": row[3], "stage": row[4], "payload": row[5],
                       "prev_hash": row[6]},
                      sort_keys=True, separators=(",", ":"))


def _row_hash(row: tuple) -> str:
    return hashlib.sha256(_canon(row).encode()).hexdigest()


def _head(con: sqlite3.Connection, run_id: str) -> tuple[int, str]:
    r = con.execute(
        "SELECT seq, hash FROM run_events WHERE run_id=? "
        "ORDER BY seq DESC LIMIT 1", (run_id,)).fetchone()
    return (r[0], r[1]) if r else (0, GENESIS)


def _apply(st: dict, kind: str, stage: str | None, payload: str) -> None:
    """Fold one event into state (validation is separate)."""
    if kind == "declare":
        st.update(stages={s: None for s in json.loads(payload)},
                  parked=False, done=False, commits=[])
    elif kind == "stage_pass":
        st.setdefault("stages", {})[stage] = "pass"
        if st["stages"] and all(v == "pass" for v in st["stages"].values()):
            st["done"] = True
    elif kind == "stage_fail":
        st.setdefault("stages", {})[stage] = "fail"
        st["done"] = False
    elif kind == "park":
        st["parked"] = True
    elif kind == "resume":
        st["parked"] = False
    elif kind == "commit":
        st.setdefault("commits", []).append(
            json.loads(payload)["commit_sha"])


def replay(con: sqlite3.Connection, run_id: str, up_to: int | None = None) -> dict:
    """Reconstruct run state by folding events in seq order."""
    st: dict = {}
    q = ("SELECT seq, kind, stage, payload FROM run_events "
         "WHERE run_id=? AND (? IS NULL OR seq<=?) ORDER BY seq")
    for seq, kind, stage, payload in con.execute(q, (run_id, up_to, up_to)):
        st["seq"] = seq
        _apply(st, kind, stage, payload)
    return st


def _check_transition(st: dict, kind: str, stage: str | None, payload: str) -> None:
    if kind not in KINDS:
        raise TransitionError(f"unknown kind {kind!r}")
    if kind == "declare":
        if st.get("stages"):
            raise TransitionError("already declared")
        if stage is not None:
            raise TransitionError("declare carries no stage")
        try:
            names = json.loads(payload)
        except json.JSONDecodeError as e:
            raise TransitionError(f"declare payload not json: {e}")
        # an empty list folds to stages={} — falsy — so a SECOND declare
        # would sail past the guard above; duplicates collapse invisibly
        # in the fold dict. Both are shape violations, refused at the door.
        if (not isinstance(names, list) or not names
                or not all(isinstance(n, str) and n for n in names)
                or len(set(names)) != len(names)):
            raise TransitionError(
                "declare needs a non-empty list of unique stage names")
        return
    if not st.get("stages"):
        raise TransitionError("no declare event for this run")
    if kind != "commit" and st["done"]:
        raise TransitionError("run is done; only commits may follow")
    if kind in ("stage_pass", "stage_fail") and st["parked"]:
        raise TransitionError("run parked; resume before stage transitions")
    if kind == "park" and st["parked"]:
        raise TransitionError("already parked")
    if kind == "resume" and not st["parked"]:
        raise TransitionError("not parked")
    if kind == "stage_pass":
        if stage not in st["stages"]:
            raise TransitionError(f"stage {stage!r} not declared")
        if st["stages"][stage] is not None:
            raise TransitionError(f"stage {stage} already {st['stages'][stage]}")
        names = list(st["stages"])
        # no skipping: every earlier stage must be pass; no un-passing a later one
        if any(st["stages"][s] is not None for s in names[names.index(stage) + 1:]):
            raise TransitionError(f"cannot pass {stage}: a later stage already resolved")
        if any(st["stages"][s] != "pass" for s in names[:names.index(stage)]):
            raise TransitionError(f"cannot pass {stage}: earlier stage unresolved")
    elif kind == "stage_fail":
        if stage not in st["stages"]:
            raise TransitionError(f"stage {stage!r} not declared")
        if st["stages"][stage] is None:
            raise TransitionError(f"cannot fail {stage} before it is resolved")
        names = list(st["stages"])
        # an ordered pipeline cannot retroactively fail a stage whose
        # successors already resolved — that state is fabrication, not fact
        if any(st["stages"][s] is not None for s in names[names.index(stage) + 1:]):
            raise TransitionError(f"cannot fail {stage}: a later stage already resolved")
    elif kind == "commit":
        if not st["done"]:
            raise TransitionError("commit before all stages pass")
        try:
            sha = json.loads(payload).get("commit_sha", "")
        except json.JSONDecodeError as e:
            raise TransitionError(f"commit payload not json: {e}")
        if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
            raise TransitionError("commit_sha must be 40 hex chars")
        if sha in st["commits"]:
            raise TransitionError(f"commit {sha[:12]} already recorded")


def append(con: sqlite3.Connection, run_id: str, kind: str,
           stage: str | None = None, payload=None) -> dict:
    """Validate and insert as ONE atomic step under BEGIN IMMEDIATE.

    The write lock is taken before replay, so validation always sees the
    state the insert will land on — across connections and processes.
    """
    body = "" if payload is None else json.dumps(payload, sort_keys=True)
    for attempt in range(32):
        # BEGIN IMMEDIATE takes the write lock FIRST: validation and insert
        # are one atomic unit across connections and processes. A second
        # writer cannot validate against stale state and slip in after.
        con.execute("BEGIN IMMEDIATE")
        try:
            _verify_schema(con)  # connect->append drift: triggers can be
            # added by another connection in between
            seq, prev_hash = _head(con, run_id)
            _check_transition(replay(con, run_id), kind, stage, body)
            row = (run_id, seq + 1, time.time(), kind, stage, body, prev_hash)
            row = (*row, _row_hash(row))
            con.execute("INSERT INTO run_events VALUES (?,?,?,?,?,?,?,?)", row)
            if con.execute("SELECT changes()").fetchone()[0] != 1:
                raise TransitionError("INSERT voided by schema (0 rows landed)")
            con.commit()
            return {"run_id": run_id, "seq": row[1], "hash": row[7]}
        except sqlite3.IntegrityError:
            con.rollback()  # should be impossible under IMMEDIATE; retry
            time.sleep(0.01 * (attempt + 1))
        except Exception:
            con.rollback()
            raise
    raise TransitionError("could not acquire next seq (writer starvation)")


def verify_chain(con: sqlite3.Connection, run_id: str) -> str | None:
    """Return a description of the first anomaly, or None if pristine.

    Hash linkage alone is NOT validity: a client may INSERT a correctly
    hashed ILLEGAL event directly (bypassing append), so every row is
    revalidated through _check_transition against the replayed prefix
    before it is applied. seal()/verify() inherit this refusal.
    """
    prev_seq, prev_hash = 0, GENESIS
    st: dict = {}
    for r in con.execute(
            "SELECT run_id, seq, ts, kind, stage, payload, prev_hash, hash "
            "FROM run_events WHERE run_id=? ORDER BY seq", (run_id,)):
        if r[1] != prev_seq + 1:
            return f"seq gap/duplication at {r[1]}"
        if r[6] != prev_hash:
            return f"chain break at seq {r[1]}"
        if _row_hash(r[:7]) != r[7]:
            return f"row hash mismatch at seq {r[1]}"
        try:
            _check_transition(st, r[3], r[4], r[5])
        except TransitionError as e:
            return f"illegal transition at seq {r[1]}: {e}"
        _apply(st, r[3], r[4], r[5])
        prev_seq, prev_hash = r[1], r[7]
    return None


DEFAULT_ANCHOR_DIR = Path.home() / ".rig" / "run_events"


def _anchor_file(anchor_dir) -> Path:
    return Path(anchor_dir if anchor_dir is not None else DEFAULT_ANCHOR_DIR)


def _anchor_name(run_id: str) -> str:
    """run_id is caller data: '../x' must not traverse out of the anchor
    root. The filename is a hash of the id; the raw id lives inside."""
    return hashlib.sha256(run_id.encode()).hexdigest() + ".anchors"


def _write_anchor(pkt: dict, anchor_dir) -> None:
    """Append the packet's digest to an OUT-OF-TREE ledger of seals. An
    attacker who can rewrite the SQLite file AND recompute the packet hash
    still cannot make verify() pass without writing this file — which sits
    outside the ledger's write boundary, exactly like commit_gate's
    certifier anchor. A full filesystem-privileged attacker is the named
    residual trust (keyed signatures = upgrade path), same as commit_gate.
    """
    d = _anchor_file(anchor_dir)
    d.mkdir(parents=True, exist_ok=True)
    line = json.dumps({"run_id": pkt["run_id"], "seq": pkt["seq"],
                       "packet_hash": pkt["packet_hash"], "ts": time.time()},
                      sort_keys=True)
    with open(d / _anchor_name(pkt["run_id"]), "a") as f:
        f.write(line + "\n")


def _anchored(pkt_hash: str, run_id: str, anchor_dir) -> bool:
    f = _anchor_file(anchor_dir) / _anchor_name(run_id)
    try:
        lines = f.read_text().splitlines()
    except OSError:
        return False
    for line in lines:
        try:
            rec = json.loads(line)
            if rec.get("run_id") == run_id and rec.get("packet_hash") == pkt_hash:
                return True
        except json.JSONDecodeError:
            continue
    return False


def seal(con: sqlite3.Connection, run_id: str, extra: dict | None = None,
         *, anchor_dir: str | Path | None = None) -> dict:
    anomaly = verify_chain(con, run_id)
    if anomaly:
        raise TransitionError(f"refusing to seal: {anomaly}")
    seq, head = _head(con, run_id)
    if seq == 0:
        raise TransitionError("refusing to seal: run has no events")
    pkt = {"schema": "rig.run_events.packet.v" + str(SCHEMA_VERSION),
           "run_id": run_id, "seq": seq, "head_hash": head,
           "state": replay(con, run_id, up_to=seq)}
    if extra:
        pkt["extra"] = extra
    # canonical hash over the WHOLE body (extra included): a packet is one
    # indivisible claim; editing any field breaks the digest.
    pkt["packet_hash"] = hashlib.sha256(
        json.dumps(pkt, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    _write_anchor(pkt, anchor_dir)
    return pkt


def verify(con: sqlite3.Connection, pkt: dict, *,
           anchor_dir: str | Path | None = None) -> str | None:
    """Recompute everything the packet claims. None = holds."""
    if pkt.get("schema") != "rig.run_events.packet.v" + str(SCHEMA_VERSION):
        return f"packet schema {pkt.get('schema')!r}"
    body = {k: v for k, v in pkt.items() if k != "packet_hash"}
    want = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if not hmac.compare_digest(want, str(pkt.get("packet_hash"))):
        return "packet_hash does not match packet body (field was edited)"
    run_id, seq = pkt.get("run_id"), pkt.get("seq")
    anomaly = verify_chain(con, run_id)
    if anomaly:
        return anomaly
    head_seq, head_now = _head(con, run_id)
    if head_seq < seq:
        return f"ledger has only {head_seq} rows, packet seals {seq}"
    got = replay(con, run_id, up_to=seq)
    if got != pkt.get("state"):
        return "replayed state does not match packet state"
    sealed_hash = con.execute(
        "SELECT hash FROM run_events WHERE run_id=? AND seq=?",
        (run_id, seq)).fetchone()
    if not sealed_hash or sealed_hash[0] != pkt.get("head_hash"):
        return "head_hash does not match the row at that seq"
    if not _anchored(str(pkt.get("packet_hash")), str(run_id), anchor_dir):
        return ("packet hash is not anchored out-of-tree "
                "(missing anchor file, or the packet was re-hashed after sealing)")
    return None


# -- selftest ---------------------------------------------------------------
def selftest(argv=None) -> int:
    import os
    import subprocess
    import sys
    import tempfile

    errs = []
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, "events.sqlite")
        con = connect(db)
        run = "r-1"

        def ok(name, fn):
            try:
                fn()
            except TransitionError:
                return
            except Exception as e:  # noqa: BLE001
                errs.append(f"{name}: wrong error {e!r}")
                return
            errs.append(f"{name}: illegal transition accepted")

        append(con, run, "declare", payload=["B", "V", "C"])
        append(con, run, "stage_pass", "B")
        ok("pass C before V", lambda: append(con, run, "stage_pass", "C"))
        ok("V pass twice", lambda: (append(con, run, "stage_pass", "V"),
                                    append(con, run, "stage_pass", "V")))
        st = replay(con, run)
        if st["stages"] != {"B": "pass", "V": "pass", "C": None} or st["done"]:
            errs.append(f"replay wrong: {st['stages']}")
        append(con, run, "stage_pass", "C")
        ok("pass after done", lambda: append(con, run, "stage_pass", "B"))
        ok("park after done", lambda: append(con, run, "park"))
        sha = "a" * 40
        append(con, run, "commit", payload={"commit_sha": sha})
        ok("duplicate commit", lambda: append(
            con, run, "commit", payload={"commit_sha": sha}))
        ok("bad sha", lambda: append(con, run, "commit",
                                     payload={"commit_sha": "zz"}))
        ok("undeclared stage", lambda: append(con, "r-other", "stage_pass", "B"))

        # advisor freeze: retroactively failing B after V passed (C still
        # unresolved, so this is the ordering rule, not the done guard)
        r5 = "r-failorder"
        append(con, r5, "declare", payload=["B", "V", "C"])
        append(con, r5, "stage_pass", "B")
        append(con, r5, "stage_pass", "V")
        ok("fail B after V passed",
           lambda: append(con, r5, "stage_fail", "B"))

        # advisor freeze: declare payload shape
        ok("empty declare",
           lambda: append(con, "r-d0", "declare", payload=[]))
        ok("duplicate stages",
           lambda: append(con, "r-d1", "declare", payload=["B", "B"]))
        ok("declare with stage",
           lambda: append(con, "r-d2", "declare", stage="X", payload=["B"]))
        dbad = "r-declareforgery"
        row = (dbad, 1, time.time(), "declare", None, "[]", GENESIS)
        row = (*row, _row_hash(row))
        con.execute("INSERT INTO run_events VALUES (?,?,?,?,?,?,?,?)", row)
        row2 = (dbad, 2, time.time(), "declare", None,
                json.dumps(["B"]), row[7])
        row2 = (*row2, _row_hash(row2))
        con.execute("INSERT INTO run_events VALUES (?,?,?,?,?,?,?,?)", row2)
        con.commit()
        if verify_chain(con, dbad) is None:
            errs.append("empty-declare redeclare forgery verified clean")
        try:
            seal(con, dbad)
            errs.append("seal accepted declare forgery")
        except TransitionError:
            pass

        # pre-existing same-named NO-OP triggers must not fool connect():
        # IF NOT EXISTS accepts them silently, so the schema check fails closed
        poisoned = os.path.join(td, "poisoned.sqlite")
        pcon = sqlite3.connect(poisoned)
        pcon.executescript(
            "CREATE TABLE run_events (run_id TEXT, seq INTEGER, ts REAL,"
            " kind TEXT, stage TEXT, payload TEXT DEFAULT '',"
            " prev_hash TEXT, hash TEXT, PRIMARY KEY (run_id, seq));"
            "CREATE TRIGGER run_events_no_update BEFORE UPDATE ON run_events"
            " BEGIN SELECT 1; END;"
            "CREATE TRIGGER run_events_no_delete BEFORE DELETE ON run_events"
            " BEGIN SELECT 1; END;")
        pcon.commit()
        pcon.close()
        try:
            connect(poisoned)
            errs.append("connect accepted no-op trigger impostor")
        except RuntimeError:
            pass

        # a silently DROPPED trigger must fail closed too — no auto-repair
        dropped = os.path.join(td, "dropped.sqlite")
        dcon = connect(dropped)
        append(dcon, "r", "declare", payload=["B"])
        dcon.close()
        dcon = sqlite3.connect(dropped)
        dcon.execute("DROP TRIGGER run_events_no_update")
        dcon.commit()
        dcon.close()
        try:
            connect(dropped)
            errs.append("connect silently repaired dropped trigger")
        except RuntimeError:
            pass

        # park/resume lifecycle on a live run
        r3 = "r-park"
        append(con, r3, "declare", payload=["B", "V", "C"])
        append(con, r3, "stage_pass", "B")
        append(con, r3, "park")
        ok("double park", lambda: append(con, r3, "park"))
        ok("stage_pass while parked",
           lambda: append(con, r3, "stage_pass", "V"))
        ok("stage_fail while parked",
           lambda: append(con, r3, "stage_fail", "B"))
        ok("resume twice", lambda: (append(con, r3, "resume"),
                                    append(con, r3, "resume")))
        append(con, r3, "stage_pass", "V")
        # atomic validate-insert: 6 processes racing to park the same run
        # legally park exactly once (stale-state double-park is the bug)
        r4 = "r-race"
        append(con, r4, "declare", payload=["B"])
        code = ("import sys; sys.path.insert(0, %r);"
                "from rig_capabilities.run_events import connect, append;"
                "append(connect(%r), %r, 'park')") % (os.getcwd(), db, r4)
        codes = sorted(p.wait() for p in
                       [subprocess.Popen([sys.executable, "-c", code])
                        for _ in range(6)])
        n_park = con.execute(
            "SELECT COUNT(*) FROM run_events WHERE run_id=? AND kind='park'",
            (r4,)).fetchone()[0]
        if n_park != 1 or codes[:1] != [0] or codes[-1] not in (0, 1):
            errs.append(f"racy park: {n_park} inserted, codes {codes}")

        # UPDATE/DELETE are refused at the DB level
        for stmt in ("UPDATE run_events SET kind='park' WHERE run_id='r-1'",
                     "DELETE FROM run_events WHERE run_id='r-1'"):
            try:
                con.execute(stmt)
                con.commit()
                errs.append(f"mutation accepted: {stmt[:20]}")
            except sqlite3.IntegrityError:
                con.rollback()

        # out-of-band tampering: rewrite a row via a rogue trigger-less copy
        # (simulates file-level forgery; chain must catch it)
        import shutil
        tam = os.path.join(td, "tampered.sqlite")
        shutil.copy(db, tam)
        tcon = sqlite3.connect(tam)
        tcon.execute("DROP TRIGGER run_events_no_update")
        tcon.execute("UPDATE run_events SET kind='park' "
                     "WHERE run_id='r-1' AND seq=2")
        tcon.commit()
        if verify_chain(tcon, "r-1") is None:
            errs.append("tampered chain verified clean")
        tcon.close()


        # direct INSERT bypassing append: valid chain hash, ILLEGAL
        # transition (pass C with nothing resolved) — must be refused by
        # verify_chain, hence by seal
        bad = "r-bad"
        d = append(con, bad, "declare", payload=["B", "V", "C"])
        row = (bad, 2, time.time(), "stage_pass", "C", "", d["hash"])
        row = (*row, _row_hash(row))
        con.execute("INSERT INTO run_events VALUES (?,?,?,?,?,?,?,?)", row)
        con.commit()
        if verify_chain(con, bad) is None:
            errs.append("hashed illegal insert verified clean")
        try:
            seal(con, bad)
            errs.append("seal accepted ledger with illegal insert")
        except TransitionError:
            pass
        # seal/verify: honest seal holds; packet then tampered -> caught
        anchors = os.path.join(td, "anchors")
        pkt = seal(con, run, {"done_test": "s7"}, anchor_dir=anchors)
        if verify(con, pkt, anchor_dir=anchors) is not None:
            errs.append(f"honest packet failed: {verify(con, pkt, anchor_dir=anchors)}")
        if verify(con, pkt) is None:
            errs.append("packet verified against an anchor root that never saw it")
        # append after sealing: packet must still verify at its own point
        append(con, run, "commit", payload={"commit_sha": "b" * 40})
        if verify(con, pkt, anchor_dir=anchors) is not None:
            errs.append("packet broken by later append")
        # state forgery in the packet itself
        forgery = dict(pkt)
        forgery["state"] = {**pkt["state"], "stages": {"B": "pass"}}
        if verify(con, forgery, anchor_dir=anchors) is None:
            errs.append("forged packet state verified clean")
        # extra forgery: checks/artifacts edited after sealing
        forgery = {**dict(pkt),
                   "extra": {**pkt["extra"], "done_test": "s7-tampered"}}
        if verify(con, forgery, anchor_dir=anchors) is None:
            errs.append("forged packet extra verified clean")

        # FinalVerifier freeze: forged extra + RE-HASHED packet_hash must
        # still fail verify — the ledger holds no matching seal event
        rehash = {**dict(pkt), "extra": {**pkt["extra"], "done_test": "x"}}
        rehash["packet_hash"] = hashlib.sha256(
            json.dumps({k: v for k, v in rehash.items()
                        if k != "packet_hash"},
                       sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if verify(con, rehash, anchor_dir=anchors) is None:
            errs.append("re-hashed forged packet verified clean")

        # FinalVerifier freeze: an EXTRA BEFORE INSERT RAISE(IGNORE)
        # trigger voids appends while the receipt looks valid
        ig = os.path.join(td, "ignore.sqlite")
        icon = connect(ig)
        icon.execute("CREATE TRIGGER void BEFORE INSERT ON run_events "
                     "BEGIN SELECT RAISE(IGNORE); END")
        icon.commit()
        try:
            append(icon, "r", "declare", payload=["B"])
            errs.append("append acknowledged a voided insert")
        except (RuntimeError, TransitionError):
            pass
        icon.close()
        try:
            connect(ig)
            errs.append("connect accepted void-trigger schema")
        except RuntimeError:
            pass
        ok("seal empty run", lambda: seal(con, "r-never-exists"))

        # advisor freeze: run_id traversal must not escape the anchor root
        esc = os.path.join(td, "escroot")
        econ = connect(os.path.join(td, "esc.db"))
        erid = "../escaped-run"
        append(econ, erid, "declare", payload=["B"])
        epkt = seal(econ, erid, anchor_dir=esc)
        if verify(econ, epkt, anchor_dir=esc) is not None:
            errs.append("traversal-id honest verify failed")
        roots = (Path(esc), Path(anchors))
        stray = [str(p) for p in Path(td).rglob("*.anchors")
                 if not any(r in p.parents for r in roots)]
        if stray:
            errs.append(f"anchor escaped its root: {stray}")
        names = list(Path(esc).glob("*.anchors"))
        if not names or not all(len(p.stem) == 64 for p in names):
            errs.append("anchor filename not hash-derived")
        if _anchored(epkt["packet_hash"], "different-run", esc):
            errs.append("anchor matched a different run_id")

        # seq monotone + unique per run
        seqs = [r[0] for r in con.execute(
            "SELECT seq FROM run_events WHERE run_id='r-1' ORDER BY seq")]
        if seqs != list(range(1, len(seqs) + 1)):
            errs.append(f"seqs not contiguous: {seqs}")
    print(json.dumps({"ok": not errs, "errors": errs}))
    return 0 if not errs else 1


if __name__ == "__main__":
    import sys
    sys.exit(selftest())
