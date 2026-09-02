"""P7: anti-fabrication proof — sealing, per-task chains, fabrication ledger.

A seal binds a claim to its payload bytes: proof_hash is the sha256 of the
canonical JSON of the body MINUS any pre-existing proof_hash (stripped before
hashing). Chain scope is PER TASK — previous_hash links a packet only to the
prior packet carrying the same task_id; the first packet of a task, and every
packet without a task_id, chain to the literal "genesis".

Sentinel Prime is SPECIFICATION ONLY. ~/.rig/convergence/sentinel-prime/
SENTINEL_PRIME_SPEC.md is headed "Status: SPECIFICATION — not yet implemented",
so every evidence card written here stamps that honesty and never claims a
gauntlet phase ran.

Ladder law: no PASS may ever derive from a packet whose verify_seal is False,
and nothing in this module emits PASS — see verdict_ladder().

Live paths are resolved AT CALL TIME. RIG_PROOF_ROOT relocates PROOF_DIR and
SENTINEL_DIR (the sentinel tree becomes <root>/convergence/sentinel-prime/
proofpackets); RIG_LEASE_STATE_ROOT relocates the fabrication ledger to
<root>/fabrication-ledger.jsonl. Tests point both at tmpdirs and never touch
the real ~/.rig.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

PROOF_DIR = Path.home() / ".rig" / "proof"
SENTINEL_DIR = (Path.home() / ".rig" / "convergence" / "sentinel-prime"
                / "proofpackets")
LEDGER = Path.home() / ".rig" / "leases" / "fabrication-ledger.jsonl"

PACKET_SUBDIR = "fable2031"
GENESIS = "genesis"
TAC_CLI = "/Users/rig128gb/.hermes/skills/tac-v2-doctrine/bin/tac"
SENTINEL_SPEC = (Path.home() / ".rig" / "convergence" / "sentinel-prime"
                 / "SENTINEL_PRIME_SPEC.md")
# Mirrors dispatcher.VERDICTS; hardcoded so this module never imports a peer.
DISPATCHER_VERDICTS = ("PASS", "FAIL", "BLOCKED", "FABRICATED",
                       "ISOLATION_BREACH")
HONESTY_LINE = "counts measure adjudicated signals, not quality or truth"


def proof_root() -> Path:
    """PROOF_DIR at call time; RIG_PROOF_ROOT overrides."""
    root = os.environ.get("RIG_PROOF_ROOT")
    return Path(root) if root else PROOF_DIR


def packet_dir() -> Path:
    """Where sealed packets live: <proof root>/fable2031/."""
    return proof_root() / PACKET_SUBDIR


def sentinel_dir() -> Path:
    """SENTINEL_DIR at call time; RIG_PROOF_ROOT overrides."""
    root = os.environ.get("RIG_PROOF_ROOT")
    if root:
        return (Path(root) / "convergence" / "sentinel-prime"
                / "proofpackets")
    return SENTINEL_DIR


def ledger_path() -> Path:
    """LEDGER at call time; RIG_LEASE_STATE_ROOT overrides (per lease law)."""
    root = os.environ.get("RIG_LEASE_STATE_ROOT")
    if root:
        return Path(root) / LEDGER.name
    return LEDGER


def _now_iso() -> str:
    return (datetime.now(timezone.utc).isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"))


def _slug(task_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", str(task_id))


def canonical_json(obj) -> bytes:
    """The one canonical form: sorted keys, tight separators, real UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def _digest(payload) -> str:
    return hashlib.sha256(canonical_json(payload)).hexdigest()


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(data, indent=1, sort_keys=True,
                                ensure_ascii=False) + "\n")
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _latest_hash(task_id: str) -> str:
    """proof_hash of the newest sealed packet with this task_id, else genesis."""
    best_key, best_hash = ("", ""), ""
    d = packet_dir()
    if not d.is_dir():
        return GENESIS
    for p in sorted(d.glob("*.json")):
        try:
            pkt = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(pkt, dict) or pkt.get("task_id") != task_id:
            continue
        h = pkt.get("proof_hash")
        if not isinstance(h, str) or not h:
            continue
        key = (str(pkt.get("sealed_at") or ""), p.name)
        if key > best_key:
            best_key, best_hash = key, h
    return best_hash or GENESIS


def seal_packet(kind: str, body: dict, *, task_id: str | None = None) -> dict:
    """Seal body under PROOF_DIR/fable2031/; returns the packet.

    proof_hash = sha256(canonical JSON of body minus any pre-existing
    proof_hash). Same body -> same hash, always. Chains per task_id; no
    task_id means standalone, previous_hash = "genesis".
    """
    if not isinstance(kind, str) or not kind:
        raise ValueError("kind must be a non-empty string")
    if not isinstance(body, dict):
        raise TypeError("body must be a dict")
    payload = {k: v for k, v in body.items() if k != "proof_hash"}
    digest = _digest(payload)
    previous_hash = _latest_hash(task_id) if task_id is not None else GENESIS
    packet = {
        "schema": "rig.proofpacket.v1",
        "kind": kind,
        "task_id": task_id,
        "previous_hash": previous_hash,
        "sealed_at": _now_iso(),
        "payload": payload,
        "proof_hash": digest,
    }
    name = f"{'standalone' if task_id is None else _slug(task_id)}__{digest[:16]}.json"
    _write_json(packet_dir() / name, packet)
    return packet


def verify_seal(packet: dict) -> tuple[bool, str]:
    """Recompute the payload digest and compare.

    Mismatch (or a missing proof_hash / payload) -> (False, 'seal_mismatch').
    A failed seal is inert: no PASS may EVER derive from a packet that fails
    this check — a ROADMAP prefix or a Sentinel card resting on a red seal is
    treated as unsealed evidence, not weak evidence.
    """
    if not isinstance(packet, dict):
        return False, "seal_mismatch"
    h = packet.get("proof_hash")
    if not isinstance(h, str) or not h:
        return False, "seal_mismatch"
    if _digest(packet.get("payload", {})) != h:
        return False, "seal_mismatch"
    return True, "ok"


def write_sentinel_evidence(task_id: str, packet: dict) -> dict:
    """Copy a sealed packet's hash into the Sentinel evidence tree — stamped.

    SENTINEL_PRIME_SPEC.md is headed "Status: SPECIFICATION — not yet
    implemented", so this card states the truth about the system: status
    SPECIFICATION_ONLY, zero gauntlet phases executed, termination authority
    UNIMPLEMENTED. Fleet status stays BLOCKED_PENDING_SENTINEL regardless of
    any task verdict.
    """
    if not isinstance(task_id, str) or not task_id:
        raise ValueError("task_id must be a non-empty string")
    if not isinstance(packet, dict):
        raise TypeError("packet must be a dict")
    sealed, seal_reason = verify_seal(packet)
    ev = {
        "schema": "rig.sentinel-evidence.v1",
        "task_id": task_id,
        "source_proof_hash": str(packet.get("proof_hash") or ""),
        "seal_verified": sealed,
        "seal_reason": seal_reason,
        "sentinel_prime_status": "SPECIFICATION_ONLY",
        "gauntlet_phases_executed": [],
        "termination_authority": "UNIMPLEMENTED",
        "spec_reference": str(SENTINEL_SPEC),
        "written_at": _now_iso(),
    }
    src = str(packet.get("proof_hash") or "unsigned")[:16]
    _write_json(sentinel_dir() / f"{_slug(task_id)}__{src}.json", ev)
    return ev


def log_fabrication(agent_id: str, verdict: str, task_id: str,
                    detail: str = "") -> dict:
    """Append EXACTLY ONE line to the fabrication ledger, TAC telemetry shape.

    One os.open(O_APPEND) + one os.write. An append failure RAISES —
    a fabrication event is never silently dropped.
    """
    rec = {
        "ts": _now_iso(),
        "epoch": int(time.time()),
        "event": "fabrication-signal",
        "pattern": "tac.anti-fabrication",
        "verdict": verdict,
        "session": task_id,
        "agent_id": agent_id,
        "detail": detail,
    }
    path = ledger_path()
    line = (json.dumps(rec, sort_keys=True) + "\n").encode("utf-8")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        try:
            written = os.write(fd, line)
        finally:
            os.close(fd)
        if written != len(line):
            raise OSError(f"short append: wrote {written} of {len(line)} bytes")
    except OSError as exc:
        raise RuntimeError(f"fabrication_ledger_write_failed: {exc}") from exc
    return rec


def fabrication_rates(since_days: int = 30) -> dict:
    """Aggregate the ledger over a trailing window.

    An absent ledger returns zeroed counts with ledger_present: False and
    fabrication_rate: None — never a rate invented out of nothing.
    """
    path = ledger_path()
    if not path.is_file():
        return {"ledger": str(path), "ledger_present": False,
                "window_days": since_days, "total": 0, "fabricated": 0,
                "by_agent": {}, "by_verdict": {}, "fabrication_rate": None,
                "note": "ledger_absent — no rate fabricated from nothing"}
    cutoff = time.time() - since_days * 86400
    total = fabricated = 0
    by_agent: dict[str, int] = {}
    by_verdict: dict[str, int] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            rec = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(rec, dict):
            continue
        ep = rec.get("epoch")
        if isinstance(ep, (int, float)) and not isinstance(ep, bool) \
                and ep < cutoff:
            continue
        total += 1
        v = str(rec.get("verdict") or "unknown")
        a = str(rec.get("agent_id") or "unknown")
        by_verdict[v] = by_verdict.get(v, 0) + 1
        by_agent[a] = by_agent.get(a, 0) + 1
        if v == "FABRICATED":
            fabricated += 1
    return {"ledger": str(path), "ledger_present": True,
            "window_days": since_days, "total": total,
            "fabricated": fabricated, "by_agent": by_agent,
            "by_verdict": by_verdict,
            "fabrication_rate": (fabricated / total) if total else None,
            "note": HONESTY_LINE}


def verdict_ladder() -> dict:
    """The three rungs as data — who may say what, and who may never say PASS."""
    return {
        "schema": "rig.verdict-ladder.v1",
        "rungs": [
            {"rung": 1,
             "name": "tac_close_gate_check",
             "command": f"{TAC_CLI} close-gate check --claim <claim>.json",
             "role": "deterministic evidence prefilter over production "
                     "command records only; canary evidence never enters it",
             "emits": ["GREEN", "RED"],
             "never_emits": ["PASS"]},
            {"rung": 2,
             "name": "dispatcher_admit",
             "callable": "rig_capabilities/dispatcher.py::admit",
             "role": "the ONLY emitter of PASS; must be run by a "
                     "different-family verifier over a `git archive` tree "
                     "materialised at the exact claimed commit",
             "requires": ["verifier family != dispatcher family",
                          "git archive tree at the claimed commit",
                          "verify_seal(packet) is True"],
             "emits": list(DISPATCHER_VERDICTS)},
            {"rung": 3,
             "name": "sentinel_prime_fleet",
             "role": "holds fleet termination authority in SPEC form only; "
                     "weekly fleet status stays BLOCKED_PENDING_SENTINEL "
                     "even when the task verdict is PASS",
             "status": "SPECIFICATION_ONLY",
             "termination_authority": "UNIMPLEMENTED",
             "emits": ["BLOCKED_PENDING_SENTINEL"]},
        ],
        "invariants": [
            f"{TAC_CLI} close-gate check emits GREEN/RED only — never PASS",
            "no PASS derives from a packet whose verify_seal returns False",
            "Sentinel Prime is unimplemented: fleet termination is never "
            "claimed, only BLOCKED_PENDING_SENTINEL",
        ],
    }
