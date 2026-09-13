"""Ledger consistency validator — every estate action must equal the decision
table's output for that job's evidence, and the authority standard's enums
must match the code's closed enums, or the ledger refuses to certify.

Exit 0: ledger consistent. Exit 2: typed BLOCK_LEDGER_INCONSISTENT JSON.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from tool_selection import LEGACY_MAP, RESOURCE_KINDS, ToolSelectionBlock, select_framework  # noqa: E402

SKILL_DIR = Path(__file__).resolve().parent
LEDGER = SKILL_DIR / "authority/standards/estate_ledger.v1.json"
STANDARD = SKILL_DIR / "authority/standards/tool_selection.v1.json"
EXPECTED_ACTIONS = {
    ("resident", "keep"),
    ("periodic", "move"),
    ("needs_review", "review"),
}


def _fail(problems: list[str]) -> int:
    print(json.dumps({
        "schema": "rig.d85.estate-ledger-block.v1",
        "code": "BLOCK_LEDGER_INCONSISTENT",
        "problems": problems,
    }, indent=2))
    return 2


def _authority_matches_code() -> list[str]:
    """The authority standard's resource_kind enum must equal the code's closed enum."""
    try:
        standard = json.loads(STANDARD.read_text(encoding="utf-8"))
        declared = standard["property_definitions"]["resident_service"]["evidence_schema"]["resource_kind"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        return [f"authority standard unreadable at resident_service.evidence_schema: {exc}"]
    kinds = {part.strip() for part in declared.replace("one of", "").split("|")}
    if kinds != set(RESOURCE_KINDS):
        return [f"authority enum {sorted(kinds)} != code RESOURCE_KINDS {sorted(RESOURCE_KINDS)}"]
    return []


def _launcher_epoch():
    """Missing epoch disables the retrofit cutoff; unreadable config does not."""
    home = Path(os.environ.get("RIG_D85_HOME") or Path.home() / ".rig" / "d85")
    raw = json.loads((home / "enforcement.json").read_text(encoding="utf-8"))
    return raw.get("launcher_epoch")


def _parse_ts(v) -> datetime | None:
    try:
        if isinstance(v, bool) or v is None:
            return None
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(v, timezone.utc)
        parsed = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
    except (ValueError, TypeError, OverflowError, OSError):
        return None


def validate(ledger: dict) -> list[str]:
    problems: list[str] = list(_authority_matches_code())
    jobs = ledger.get("jobs")
    if not isinstance(jobs, list):
        return problems + ["ledger.jobs is not a list"]
    try:
        epoch = _launcher_epoch()
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        return problems + [f"launcher enforcement config unreadable: {exc}"]
    ledger["_grandfathered_launcher_missing"] = 0
    if epoch is not None:
        epoch_ts = _parse_ts(epoch)
        if epoch_ts is None:
            problems.append(f"launcher_epoch invalid: {epoch!r}")
        else:
            for job in jobs:
                if not isinstance(job, dict):
                    continue
                modified = _parse_ts(job.get("modified_at"))
                if modified is not None and modified < epoch_ts:
                    if not job.get("launcher"):
                        ledger["_grandfathered_launcher_missing"] += 1
                    continue
                launcher = job.get("launcher")
                if not launcher or not Path(str(launcher)).is_file():
                    problems.append(
                        f"{job.get('job_id', '<missing>')}: modified_at is unknown or at/after launcher_epoch {epoch}; "
                        f"launcher missing or not a file: {launcher!r} — register via admit-request --launcher, fail closed."
                    )
    seen_ids: set[str] = set()
    for job in jobs:
        if not isinstance(job, dict):
            problems.append("ledger job is not an object")
            continue
        jid = job.get("job_id", "<missing>")
        if jid in seen_ids:
            problems.append(f"{jid}: duplicate job_id")
        seen_ids.add(jid)
        pair = (job.get("class"), job.get("action"))
        if pair not in EXPECTED_ACTIONS:
            problems.append(f"{jid}: class/action pair {pair} is not a known honest state")
            continue
        evidence = job.get("evidence")
        expected = job.get("expected_framework")
        if pair == ("needs_review", "review"):
            if expected is not None:
                problems.append(f"{jid}: review record carries expected_framework — review must stay undecided")
            continue
        expected = LEGACY_MAP.get(expected, expected)
        # Decided records must carry evidence and their framework verdict must be
        # the decision table's output for exactly that evidence.
        # {} is legitimate evidence: the decision-table default row (no qualifying
        # properties) is exactly what a periodic record claims.
        if not isinstance(evidence, dict):
            problems.append(f"{jid}: decided record without dict evidence")
            continue
        try:
            verdict = select_framework(evidence)["framework"]
        except ToolSelectionBlock as exc:
            problems.append(f"{jid}: evidence rejected by decision table: {exc}")
            continue
        if verdict != expected:
            problems.append(f"{jid}: action says {expected} but decision table says {verdict}")
    return problems


def main() -> int:
    if not LEDGER.exists():
        return _fail([f"ledger missing: {LEDGER}"])
    try:
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return _fail([f"ledger is not valid JSON: {exc}"])
    if ledger.get("schema") != "rig.d85.estate-ledger.v1":
        return _fail([f"unknown ledger schema: {ledger.get('schema')!r}"])
    jobs = ledger.get("jobs", [])
    problems = validate(ledger)
    summary = {
        "schema": "rig.d85.estate-ledger-validate.v1",
        "jobs": len(jobs),
        "unresolved": ledger.get("unresolved_count"),
        "grandfathered_launcher_missing": ledger.get("_grandfathered_launcher_missing"),
        "consistent": not problems,
        "problems": problems,
    }
    print(json.dumps(summary, indent=2))
    return 0 if not problems else 2


if __name__ == "__main__":
    raise SystemExit(main())
