#!/usr/bin/env python3
"""The write path for estate decisions: worksheet -> canonical Gate-D -> ledger.

Rows come ONLY from human-filled columns in decision-worksheet-*.csv; a recognizable label
is not evidence, so nothing here is inferred (the rejected v1 ingestion path fabricated owners
that way). The action file is the receipt Gate-D consumes: it is written before arming, named
by the hash of its own bytes, created exclusively, and never rewritten — so an armed receipt
cannot be replaced by a later run whose packet, standard, or ledger moved.

Verdict fields are the canonical ones, not a dialect of our own (`d85_gates.py`):
`action_sha256` is the BARE 64-hex `_canonical_hash(action)`; `run_id` is `sha256:<64 hex>`
(the approval's own id); the consumed marker is `run_id[7:23] . action_sha256[7:23]` inside
`authority/gate_d/consumed/`. Envelope file hashes are `sha256:`-prefixed — that is this
envelope's own convention, deliberately a different shape from the canonical action hash.

Authority scope is pinned in code, never in argv: `--verifier`, `--consumed-dir`, and
`--process-id` do not exist, because a flag that can point the importer at a friendly verifier
is a bypass with a `--` in front of it. Tests substitute those three constants in a copy.

Ordering is the security property: read every input exactly once -> build the action and create
its receipt -> take the ledger lock -> re-check each bound hash -> call the verifier exactly
once -> re-check the ledger bytes the approval was computed against -> install the whole
postimage as one atomic, fsynced replace. A refusal before the verifier leaves authority unspent.
A refusal after it always leaves the ledger byte-identical, and says which of two things is true:
the verdict bound, so the approval is spent and must be re-armed; or it did not bind, so the spend
is unknown and a human has to look before arming again. Neither is reported as the other.

Re-score with the collector: collect_automation_estate.py --decisions <ledger>.
Stdlib only; re-run after every worksheet edit.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import fcntl
import hashlib
import importlib.util
import io
import json
import os
import re
import secrets
import stat
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def _err(text: str) -> None:
    """stderr write helper: attribute call site, never a stream handed as data."""
    sys.stderr.write(text + "\n")


ROOT = Path(__file__).resolve().parent.parent
ESTATE = ROOT / "estate"
PACKET = ROOT / "v3" / "automation-estate-review.content.json"
STANDARD = ESTATE / "job-standard.v1.json"
LEDGER = ESTATE / "human-decisions.v1.jsonl"
# Authority scope: this is the trust boundary, so these are constants, not options.
PROCESS_ID = "estate-automation-review"
D85_SKILL = Path("/Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-determinism-85")
VERIFIER = D85_SKILL / "bin" / "rig-determinism-85"
CONSUMED = D85_SKILL / "authority" / "gate_d" / "consumed"
GATE_D_VERDICT_SCHEMA = "rig.d85.gate-d-verdict.v1"
ACTION_SCHEMA = "rig.estate.decision-import.v1"
LEDGER_SCHEMA = "rig.estate.human-decision.v1"
JOURNAL_SCHEMA = "rig.estate.decision-import-journal.v2"
SPEND_STATES = ("pre-verifier", "unknown", "spent")
DECISION_COLUMNS = ("decision_owner", "decision_consumer", "decision_mechanism")
RUN_ID_RE = re.compile(r"sha256:[0-9a-f]{64}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")
_D85 = None


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.new("sha256", data).hexdigest()


def canonical(obj: object) -> str:
    return json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=True)


def authority_hash(obj: object) -> str:
    """The authority's own action hasher, loaded read-only, returning the bare hex it returns.

    `gate_d` compares `_canonical_hash(action)`, so any local re-implementation or prefix drift
    means every legitimate ARMED verdict is refused and the importer sits permanently, quietly
    dormant. Never prefix or re-derive this value.
    """
    global _D85
    if _D85 is None:
        path = D85_SKILL / "d85.py"
        spec = importlib.util.spec_from_file_location("rig_d85_for_import", path)
        if spec is None or spec.loader is None:
            raise SystemExit(f"NO CANONICAL HASH: cannot load {path}")
        module = importlib.util.module_from_spec(spec)
        # d85 defines dataclasses, which resolve their owning module through sys.modules at
        # class-creation time; exec without registering first fails inside the import.
        sys.modules[spec.name] = module
        try:
            spec.loader.exec_module(module)
        except Exception as exc:  # noqa: BLE001 - an unloadable authority is a refusal, never a pass
            raise SystemExit(f"NO CANONICAL HASH: {path} failed to load: {exc}")
        _D85 = module
    return _D85._canonical_hash(obj)


def marker_name(run_id: str, action_sha256: str) -> str:
    """Exactly `d85_gates.py`'s derivation: strip the run id's `sha256:` prefix, take 16 chars
    of each. The action hash is bare, so its slice starts inside the hex."""
    return f"{run_id[7:23]}.{action_sha256[7:23]}"


def fsync_dir(directory: Path) -> None:
    """Without this the os.replace entry can be lost while the approval stays consumed."""
    fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)

def read_regular(path: Path, label: str = "FILE") -> bytes:
    """Read a file through one O_NOFOLLOW descriptor.

    Checking islink/is_file and then opening is a swap window: the path can become a symlink
    between the two. Everything that decides whether bytes are authoritative — the action
    receipt, the ledger preimage, the journal — is read this way, and `label` keeps the refusal
    naming which artifact failed.
    """
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as exc:
        raise SystemExit(f"{label} NOT A REGULAR FILE: {path}: {exc}")
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise SystemExit(f"{label} NOT A REGULAR FILE: {path}")
        chunks = []
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


def read_ledger(data: bytes, path: Path) -> list[dict]:
    """Parse the bytes that were hashed. Parsing a second read of the path would let the
    idempotency/conflict checks describe a preimage other than the one Gate-D approved."""
    records = []
    for number, line in enumerate(data.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"LEDGER CORRUPT: {path}:{number}: {exc}")
        if record.get("schema") != LEDGER_SCHEMA:
            raise SystemExit(f"LEDGER CORRUPT: {path}:{number}: unknown schema")
        if not record.get("gate_d_run_id") or not record.get("action_sha256"):
            raise SystemExit(f"LEDGER CORRUPT: {path}:{number}: no Gate-D binding")
        records.append(record)
    return records


def journal_path(ledger: Path) -> Path:
    return ledger.with_name(ledger.name + ".journal.json")


def write_journal(path: Path, payload: dict) -> None:
    """Exclusive temp write + fsync + replace + dir fsync, so the record survives a crash."""
    tmp = path.with_name(f"{path.name}.{secrets.token_hex(8)}.new")
    fd = os.open(tmp, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)
    fsync_dir(path.parent)


def diagnostic_journal(action: dict, action_path: Path, decisions: list[dict],
                       verdict: dict | None = None, recorded_at: str | None = None,
                       spend_state: str | None = None, bound: bool = True,
                       refused: str | None = None) -> dict:
    """WHAT WAS ATTEMPTED, and after a BOUND ARMED verdict, what was spent. Diagnostic evidence only.

    It is never a replay source. A JSON file plus an unsigned marker in an unprotected
    `consumed/` directory is forgeable by any process running as this user, so nothing here may
    install ledger rows from it: recovery is a fresh, live `gate-d` approval, exactly like the
    read path's refusal to trust a marker without a signed receipt verifier.

    Two fields, deliberately different types. `approval_spent` is `True` only for an ARMED verdict
    that passed every binding check against this exact action — schema, process, action hash, run-id
    derivation, marker name, marker location, marker existence — and `None` otherwise; never a
    string, so `if approval_spent:` can only ever mean "spent" and an unknown can never read truthy.
    An ARMED envelope whose binding failed is NOT recorded as spent: a failed action hash or marker
    name means the consumed marker in hand is not the one this run's own action derives, which says
    nothing about whether our approval was consumed. That is `unknown`, with the raw envelope kept
    under `verdict` and the failing checks under `verdict_refused`.

    `spend_state` carries the closed set: `pre-verifier` for the intent record written before the
    call, `unknown` when the verifier ran and returned anything other than a bound ARMED verdict — a
    canonical BLOCK, junk text, `[]`, nothing at all, or an ARMED envelope that would not bind — and
    `spent` once a bound ARMED verdict is in hand. There is no value meaning "definitely not spent",
    because nothing local can establish that: the marker is written before stdout, is unsigned, and
    lives in a directory D85 does not protect.
    """
    if spend_state is not None and spend_state not in SPEND_STATES:
        raise ValueError(f"unknown spend_state {spend_state!r}, expected one of {SPEND_STATES}")
    claimed = bool(verdict)
    spent = claimed and bound
    entry = {"schema": JOURNAL_SCHEMA, "phase": "armed" if claimed else "intent",
             "installable": False, "ledger": str(action["ledger"]), "action": action,
             "action_path": str(action_path), "action_sha256": authority_hash(action),
             "ledger_preimage_sha256": action["ledger_preimage_sha256"],
             "decisions": decisions,
             # gate_d creates the consumed marker *before* it writes stdout, so a well-formed
             # BLOCK, junk text, or no output at all leaves "did the approval get spent?"
             # genuinely unanswerable from here. gate-d has no receipt operation to settle it.
             "approval_spent": True if spent else None,
             "spend_state": "spent" if spent else (
                 spend_state or ("unknown" if claimed else "pre-verifier")),
             "note": "diagnostic only — recovery requires a fresh gate-d approval, never a replay"}
    if verdict:
        entry["verdict"] = {k: verdict[k] for k in
                            ("verdict", "process_id", "run_id", "action_sha256",
                             "consumed_marker", "approver", "d85_realized_sha256")
                            if k in verdict}
        if recorded_at:  # only the commit path supplies one; nothing here invents a timestamp
            entry["verdict"]["recorded_at"] = recorded_at
    if refused:
        entry["verdict_refused"] = refused
    return entry


def parse_mechanism(text: str, goal_keys: list[str]) -> tuple[str | None, str]:
    """`'qualified_calls: feeds the call funnel'` -> (key, text). No key, no import."""
    head, sep, tail = text.partition(":")
    key = head.strip()
    if sep and tail.strip() and key in goal_keys:
        return key, tail.strip()
    return None, text


def same_decision(prior: dict, entry: dict) -> bool:
    """True when the ledger already holds exactly this decision. Empty goal_keys is [] on both
    sides — never coerced to None, or every owner-only row looks like a conflict."""
    for key in ("owner", "consumer", "mechanism"):
        if (prior.get(key) or None) != entry[key]:
            return False
    return list(prior.get("goal_keys") or []) == list(entry["goal_keys"])


def select(sources: dict[Path, bytes], ledger: list[dict],
           keys: tuple[Path, Path, Path]) -> tuple[list[dict], list[str]]:
    """Decisions from the captured bytes only — never from a second read of a mutable path."""
    worksheet, packet, standard = keys
    rows = list(csv.DictReader(io.StringIO(sources[worksheet].decode(), newline="")))
    if not rows:
        raise SystemExit(f"NO ROWS in {worksheet}")
    payload = json.loads(sources[packet].decode())
    live = {job["id"] for job in payload.get("jobs", [])}
    proposed = {p["id"] for p in payload.get("proposals", [])}
    goal_keys = json.loads(sources[standard].decode())["goal_keys"]
    by_id = {record["id"]: record for record in ledger}

    decisions: list[dict] = []
    refusals: list[str] = []
    seen: set[str] = set()
    for row in rows:
        ident = (row.get("id") or "").strip()
        filled = {c: (row.get(c) or "").strip() for c in DECISION_COLUMNS}
        if not any(filled.values()):
            continue
        if not ident:
            refusals.append("ROW_WITHOUT_ID")
            continue
        if ident in seen:
            refusals.append(f"DUP_ROW {ident}")
            continue
        seen.add(ident)
        if ident in proposed:
            # The collector scores collected jobs. A proposal is assembled later, so the record
            # would abort the read path with DECISION UNKNOWN ROW after spending an approval.
            refusals.append(f"PROPOSAL_ROW {ident}: proposals are not scorable rows yet")
            continue
        if ident not in live:
            refusals.append(f"UNKNOWN_ROW {ident}")
            continue
        entry = {"id": ident, "owner": filled["decision_owner"] or None,
                 "consumer": filled["decision_consumer"] or None,
                 "mechanism": None, "goal_keys": []}
        mechanism = filled["decision_mechanism"]
        if mechanism:
            if not filled["decision_consumer"]:
                refusals.append(f"MECHANISM_WITHOUT_CONSUMER {ident}")
                continue
            key, text = parse_mechanism(mechanism, goal_keys)
            if key is None:
                refusals.append(f"MECHANISM_GOAL_UNKNOWN {ident}: expected '<goal_key>: <mechanism>' "
                                f"with goal_key in {sorted(goal_keys)}")
                continue
            entry["mechanism"] = text
            entry["goal_keys"] = [key]
        prior = by_id.get(ident)
        if prior:
            refusals.append(f"ALREADY_IMPORTED {ident}" if same_decision(prior, entry) else
                            f"CONFLICT {ident}: ledger holds a different decision for this row")
            continue
        decisions.append(entry)

    decisions.sort(key=lambda d: d["id"])
    return decisions, refusals


@contextlib.contextmanager
def ledger_lock(ledger: Path):
    """Hold the ledger exclusive across hash-recheck -> gate-d -> install.

    The approval is one-time, so the window between checking state and spending authority is the
    whole risk. A sibling lock file keeps the ledger inode replaceable; O_NOFOLLOW plus S_ISREG
    stops a swapped symlink from letting two importers hold different locks for one ledger.
    """
    path = ledger.with_name(ledger.name + ".lock")
    try:
        fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    except OSError as exc:
        raise SystemExit(f"LEDGER LOCK UNUSABLE: {path}: {exc}")
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise SystemExit(f"LEDGER LOCK NOT A REGULAR FILE: {path}")
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


class CommitError(RuntimeError):
    """Ledger commit failed, with the one fact that decides what to do next: did it get replaced?"""

    def __init__(self, message: str, replaced: bool):
        super().__init__(message)
        self.replaced = replaced


def install_ledger(ledger: Path, preimage: bytes, records: list[dict]) -> None:
    """Install preimage+records as one file: all rows or none, durable before APPLIED.

    The temp file is built only AFTER the approval is spent, so it is the complete postimage. If
    the rename fails it is kept and named: deleting it would throw away the only copy of work a
    spent approval already paid for. The directory fsync is inside the same guard, because its
    failure means the opposite thing — the rows ARE live, only crash-durability is uncertain.
    Saying "ledger unchanged" there would send the operator to re-approve an already-applied set.
    """
    body = preimage.decode("utf-8")
    if body and not body.endswith("\n"):
        # A JSONL file need not end with a newline. Concatenating onto one would weld two
        # records into `}{` and corrupt the ledger after the approval was already spent.
        body += "\n"
    body += "".join(json.dumps(r, sort_keys=True) + "\n" for r in records)
    tmp = ledger.with_name(f"{ledger.name}.{secrets.token_hex(8)}.new")
    fd = os.open(tmp, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    replaced = False
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, ledger)
        replaced = True
        fsync_dir(ledger.parent)  # the rename must survive the crash, not only its contents
    except BaseException as exc:
        where = ("ledger replaced; durability uncertain" if replaced
                 else f"ledger unchanged; complete postimage kept at {tmp}")
        raise CommitError(f"{type(exc).__name__}: {exc} — {where}", replaced) from exc


def create_receipt(action_dir: Path, payload: str) -> Path:
    """Create the hash-named receipt exclusively. An existing name must already BE this receipt.

    The name is the full content digest, not a prefix: a 12-hex name invites a collision in
    which two different actions claim one receipt. Read-back goes through the same
    O_NOFOLLOW descriptor as everything else, so a swapped symlink cannot be read as content.
    """
    action_dir.mkdir(parents=True, exist_ok=True)
    path = action_dir / ("action-" + sha256_bytes(payload.encode())[7:] + ".json")
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    except FileExistsError:
        if read_regular(path, "ACTION RECEIPT").decode("utf-8") != payload:
            raise SystemExit(f"ACTION COLLISION: {path} holds different bytes — refusing to "
                             "destroy a receipt")
        return path  # this exact receipt already armed these bytes; reuse it, never rewrite it
    except OSError as exc:
        raise SystemExit(f"ACTION RECEIPT UNUSABLE: {path}: {exc}")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    fsync_dir(action_dir)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import human estate decisions through the canonical Gate-D verifier")
    parser.add_argument("--worksheet", type=Path, default=ESTATE / "decision-worksheet-latest.csv")
    parser.add_argument("--packet", type=Path, default=PACKET)
    parser.add_argument("--standard", type=Path, default=STANDARD)
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument("--action-dir", type=Path, default=ESTATE / "gate-d")
    parser.add_argument("--dry-run", action="store_true", help="build the action file, never call the verifier")
    args = parser.parse_args()

    worksheet, packet, standard = (args.worksheet.resolve(), args.packet.resolve(),
                                  args.standard.resolve())
    ledger = args.ledger.resolve()
    keys = (worksheet, packet, standard)
    # Every input is read exactly once, the ledger included: selection, the action's preimage
    # hash and the pre-verifier re-check all consume these same bytes. Parsing one read and
    # hashing another would let idempotency/conflict refusals describe rows Gate-D never saw.
    sources = {path: path.read_bytes() for path in keys}
    ledger_bytes = read_regular(ledger, "LEDGER") if ledger.exists() else b""
    decisions, refusals = select(sources, read_ledger(ledger_bytes, ledger), keys)
    for refusal in refusals:
        print(f"REFUSED: {refusal}")
    if refusals:
        _err("NOTHING IMPORTED — fix every refusal, then re-run (no partial import).")
        return 2
    if not decisions:
        _err("NO DECISIONS — every decision_owner/consumer/mechanism cell is blank; these rows "
              "stay C06/C07/C10 FAIL until you fill them.")
        return 2

    action = {
        "schema": ACTION_SCHEMA,
        "process_id": PROCESS_ID,
        "effect": "append human decisions to the estate ledger; re-score C06/C07/C10/C17",
        "worksheet": str(worksheet), "worksheet_sha256": sha256_bytes(sources[worksheet]),
        "packet": str(packet), "packet_sha256": sha256_bytes(sources[packet]),
        "standard": str(standard), "standard_sha256": sha256_bytes(sources[standard]),
        "ledger": str(ledger),
        "ledger_preimage_sha256": sha256_bytes(ledger_bytes),
        "row_count": len(decisions),
        "decisions": decisions,
    }
    payload = canonical(action) + "\n"
    bound_hash = authority_hash(action)  # bare hex, exactly what gate_d computes
    action_path = create_receipt(args.action_dir, payload)
    if authority_hash(json.loads(read_regular(action_path, "ACTION RECEIPT").decode("utf-8"))) \
            != bound_hash:
        _err(f"ACTION FILE DRIFT: {action_path} does not re-hash to {bound_hash}")
        return 2
    print(f"ACTION {action_path} rows={len(decisions)} sha256={bound_hash[:16]} "
          f"preimage={action['ledger_preimage_sha256'][7:19]}")
    if args.dry_run:
        print("DRY RUN — verifier not called, ledger untouched.")
        return 0
    if not VERIFIER.is_file():
        _err(f"NO VERIFIER at {VERIFIER} — refusing to judge approval locally.")
        return 2

    journal = journal_path(ledger)
    with ledger_lock(ledger):
        # A journal left behind means a previous run spent (or was about to spend) an approval
        # without finishing. Nothing may quietly proceed past that, and nothing may replay it.
        if journal.exists():
            prior = json.loads(read_regular(journal, "JOURNAL").decode("utf-8"))
            _err(f"IMPORT BLOCKED: {journal} is left over from an earlier run "
                  f"(phase={prior.get('phase')}, spend_state={prior.get('spend_state')!r}, "
                  f"approval_spent={prior.get('approval_spent')!r}, "
                  f"action={prior.get('action_sha256', '')[:16]}). It is diagnostic evidence, not "
                  "a replay source. Read it, confirm state, move it aside, then re-run for a "
                  "fresh approval.")
            return 2
        # The verifier runs exactly once per invocation, and only after every byte the action
        # claims to describe is confirmed unchanged. Nothing above may touch the verifier.
        for path in keys:
            if sha256_bytes(path.read_bytes()) != sha256_bytes(sources[path]):
                _err(f"{path.name.upper()} MOVED — verifier not called, approval not spent. "
                      "Re-run.")
                return 2
        preimage = read_regular(ledger, "LEDGER") if ledger.exists() else b""
        if sha256_bytes(preimage) != action["ledger_preimage_sha256"]:
            _err("LEDGER MOVED — verifier not called, approval not spent. Re-run.")
            return 2

        # Intent is written down BEFORE the one-time approval is spent: what was armed, against
        # which preimage, which decisions. Never a staged ledger — the verdict fields do not
        # exist yet and are not invented.
        write_journal(journal, diagnostic_journal(action, action_path, decisions))
        print(f"JOURNAL {journal} phase=intent")

        proc = subprocess.run([str(VERIFIER), "gate-d", PROCESS_ID, "--action", str(action_path)],
                              capture_output=True, text=True)
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        try:
            verdict = json.loads(proc.stdout)
        except json.JSONDecodeError:
            verdict = {}
        if not isinstance(verdict, dict):  # an envelope is an object; nothing else is a verdict
            # Valid JSON that is not an envelope: `[]`, `null`, a bare string a wrapper echoed back.
            # `.get()` on those raises on the way to the controlled refusal below, which would lose
            # both the refusal and the journal rewrite that records the attempt.
            verdict = {}
        if proc.returncode != 0 or verdict.get("verdict") != "ARMED":
            # Nothing here may conclude "not spent". gate_d creates the consumed marker before it
            # writes anything to stdout, so a marker can exist behind an empty, truncated, or
            # entirely absent envelope; the BLOCK shape is unsigned, exactly like the marker, so it
            # cannot prove the negative either. The intent journal is kept, still phase=intent, with
            # the spend state recorded as unknown. It is removed only after a completed commit.
            write_journal(journal, diagnostic_journal(action, action_path, decisions,
                                                      spend_state="unknown"))
            _err(f"DORMANT — verifier exit {proc.returncode}, no ARMED verdict; ledger untouched. "
                  "Whether an approval was spent is UNKNOWN. Journal kept as phase=intent, "
                  "spend_state=unknown, approval_spent=null — it refuses the next run. Read it, and "
                  "request another approval only after moving it aside deliberately. For reference "
                  f"only: this run's marker could be named nothing but *.{bound_hash[7:23]} in "
                  f"{CONSUMED}, and neither finding it nor not finding it settles the question.")
            return 2

        # An ARMED verdict is worth only what it binds. Every field below is canonical gate_d
        # output; a verdict that does not describe THIS action file, with its marker in the
        # canonical consumed directory, is refused instead of trusted for saying "ARMED".
        run_id = str(verdict.get("run_id") or "")
        sha = str(verdict.get("action_sha256") or "")
        marker = str(verdict.get("consumed_marker") or "")
        broken = []
        if verdict.get("schema") != GATE_D_VERDICT_SCHEMA or verdict.get("gate") != "gate_d":
            broken.append(f"not a canonical gate_d verdict (schema={verdict.get('schema')!r}, "
                          f"gate={verdict.get('gate')!r})")
        if verdict.get("process_id") != PROCESS_ID:
            broken.append(f"verdict process_id {verdict.get('process_id')!r} is not {PROCESS_ID!r}")
        if not HEX64_RE.fullmatch(sha) or sha != bound_hash:
            broken.append(f"action_sha256 {sha!r} is not the bare canonical hash of this action "
                          f"({bound_hash})")
        if not RUN_ID_RE.fullmatch(run_id):
            broken.append(f"run_id {run_id!r} is not a canonical approval id (sha256:<64 hex>)")
        if Path(marker).name != marker_name(run_id, sha):
            broken.append(f"consumed_marker {marker!r} does not name {marker_name(run_id, sha)}")
        elif Path(marker).parent != CONSUMED.resolve():
            broken.append(f"{marker} is outside the canonical consumed directory {CONSUMED}")
        elif not Path(marker).is_file():
            broken.append(f"{marker} is absent — no consumed marker for this run+action, so this "
                          "ARMED verdict's spend cannot be established")
        if broken:
            # An ARMED envelope that will not bind is NOT evidence that *this* approval was spent:
            # a mismatched action hash or marker name means the consumed marker in hand is not the
            # one this run's action derives. The envelope CLAIMS something was consumed, and what it
            # claims is exactly what this branch refuses to trust — so the value is `unknown`, with
            # the envelope and the failing checks kept.
            # Keep the journal; never delete the evidence on a non-committed outcome.
            write_journal(journal, diagnostic_journal(action, action_path, decisions, verdict,
                                                      bound=False, refused="; ".join(broken)))
            _err("JOURNAL kept: phase=armed, spend_state=unknown, approval_spent=null — an ARMED "
                  f"verdict arrived but did not bind this action, so whether approval "
                  f"{run_id[:16]} was spent cannot be established here, and the kept journal refuses "
                  "the next run. Ledger untouched. Read the retained evidence, then request a fresh "
                  "approval only after moving that journal aside deliberately.")
            _err("VERDICT UNBOUND: " + "; ".join(broken) + " — ledger untouched")
            return 2

        # gate_d has spent the approval. If anything moved while it ran, refuse and say so loudly:
        # the approval is gone, the decision is not applied, and a fresh approval is required.
        if (read_regular(ledger, "LEDGER") if ledger.exists() else b"") != preimage:
            write_journal(journal, diagnostic_journal(action, action_path, decisions, verdict))
            _err(f"LEDGER MOVED DURING VERIFICATION: {ledger} changed while gate-d ran, so "
                  f"approval {run_id[:16]} was spent without applying it. Journal {journal} is "
                  "diagnostic and refuses the next run — move it aside deliberately, then re-run "
                  "for a new action and approval.")
            return 2

        stamp = datetime.now(timezone(timedelta(0))).isoformat(timespec="seconds").replace("+00:00", "Z")
        # Rows are built here and only here, from the verdict in this process's hand. The journal
        # below records the same rows for diagnosis; the ledger is never rebuilt from the journal.
        records = [dict(entry, schema=LEDGER_SCHEMA, process_id=PROCESS_ID,
                        worksheet_sha256=action["worksheet_sha256"],
                        packet_sha256=action["packet_sha256"],
                        standard_sha256=action["standard_sha256"],
                        ledger_preimage_sha256=action["ledger_preimage_sha256"],
                        action=str(action_path), gate_d_run_id=run_id, action_sha256=sha,
                        consumed_marker=marker, approved_by=verdict.get("approver"),
                        applied_at=stamp)
                   for entry in decisions]
        # The spent verdict is fsynced before the ledger commit: if the commit dies, the evidence
        # of a consumed approval survives the crash.
        write_journal(journal, diagnostic_journal(action, action_path, decisions, verdict,
                                                  recorded_at=stamp))
        try:
            install_ledger(ledger, preimage, records)
        except CommitError as exc:
            # Two different failures, two different instructions — and only one of them may ever
            # mention a fresh approval. After a successful rename the rows are live and re-approving
            # would double-apply them; what is in doubt there is crash durability, not application.
            if exc.replaced:
                _err(f"COMMIT FAILED: {exc}\nJOURNAL {journal} kept: approval {run_id[:16]} is spent "
                      f"and the ledger at {ledger} WAS replaced — its durability is unconfirmed, so "
                      "these rows may already be live. Verify the ledger's contents against this run's "
                      "decisions before anything else. Do NOT request a fresh approval until that is "
                      "settled — approving on top of live rows applies them twice. The journal refuses "
                      "the next run; removing it is decided by what the ledger actually says.")
            else:
                _err(f"COMMIT FAILED: {exc}\nJOURNAL {journal} kept: approval {run_id[:16]} is spent "
                      "and the ledger was not changed. The journal refuses the next run and is "
                      "diagnostic evidence only — move it aside deliberately, then request a fresh "
                      "approval.")
            return 2
        try:  # the ledger is committed; losing the journal must not look like a failed import
            journal.unlink(missing_ok=True)
            fsync_dir(journal.parent)
        except OSError as exc:
            _err(f"NOTE: {journal} could not be removed ({exc}) — it is spent evidence for "
                  f"approval {run_id[:16]}; the ledger itself is committed.")
    print(f"APPLIED rows={len(decisions)} gate_d_run_id={run_id} ledger={ledger}")
    print("Next: re-collect with --decisions " + str(ledger) + " and re-seal the matrix.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
