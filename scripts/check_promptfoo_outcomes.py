#!/usr/bin/env python3
"""Fail-closed measurement screen for one asset's Promptfoo JSON export.

This does not promote an asset. A separate verifier must validate fixture
quality, actual artifacts and traces, permissions, and source-bound receipts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

MIN_CASES = 30
REQUIRED_KINDS = {"representative", "non_trigger", "adversarial"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measure(payload: dict, *, asset_id: str, source_sha256: str) -> dict:
    failures = []
    result_block = payload.get("results")
    rows = result_block.get("results") if isinstance(result_block, dict) else None
    if not isinstance(rows, list):
        rows = []
        failures.append("missing_results")
    ids: set[str] = set()
    kinds: set[str] = set()
    passed = 0
    hard_block = False
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            failures.append(f"invalid_case:{index}")
            continue
        test_case = row.get("testCase")
        meta = test_case.get("metadata") if isinstance(test_case, dict) else None
        if not isinstance(meta, dict):
            meta = {}
        case_id = meta.get("case_id")
        kind = meta.get("kind")
        if not isinstance(case_id, str) or not case_id.strip() or case_id in ids:
            failures.append(f"missing_or_duplicate_case_id:{index}")
        else:
            ids.add(case_id)
        if kind not in REQUIRED_KINDS:
            failures.append(f"invalid_case_kind:{index}")
        else:
            kinds.add(kind)
        if meta.get("asset_id") != asset_id or meta.get("source_sha256") != source_sha256:
            failures.append(f"source_binding_mismatch:{index}")
        grading = row.get("gradingResult")
        if not isinstance(grading, dict):
            grading = {}
        components = grading.get("componentResults")
        if not isinstance(components, list) or not components:
            failures.append(f"missing_assertion_trace:{index}")
        case_pass = (row.get("success") is True and grading.get("pass") is True
                     and isinstance(components, list) and bool(components)
                     and all(isinstance(c, dict) and c.get("pass") is True for c in components))
        passed += int(case_pass)
        if kind == "adversarial" and not case_pass:
            hard_block = True
    if len(rows) < MIN_CASES:
        failures.append("insufficient_cases")
    if kinds != REQUIRED_KINDS:
        failures.append("missing_required_case_kinds")
    if hard_block:
        failures.append("adversarial_failure_hard_block")
    score = passed / len(rows) if rows else None
    if score is None or score <= 0.90:
        failures.append("observed_score_not_above_0.90")
    return {
        "schema": "rig.promptfoo_outcome_screen.v1",
        "asset_id": asset_id,
        "source_sha256": source_sha256,
        "eval_id": payload.get("evalId"),
        "cases": len(rows),
        "passed": passed,
        "score": score,
        "status": "MEASURED_NOT_VERIFIED" if not failures else "BLOCKED",
        "promotion": "BLOCKED",
        "failures": sorted(set(failures)),
        "note": "Even a clean measurement requires independent fixture, artifact, trace and permission verification.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    args = parser.parse_args()
    result = measure(json.loads(args.results.read_text(encoding="utf-8")),
                     asset_id=args.asset_id, source_sha256=sha256(args.source))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "MEASURED_NOT_VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
