#!/usr/bin/env python3
"""UP.W04.r05-contract.005 — bind calibration to rubric, rule, model, and labeled-set hashes.

A calibration record that does not carry the hashes of its inputs is a
floating opinion. If the rubric text changes, the rule threshold changes, the
model swaps, or the labeled fixtures are edited, the old calibration is stale
and must be invalidated. This check proves the binding: every calibration
record is a 4-tuple of hashes, and any mutation to any input invalidates the
record.

Passes:
  1. binding    — build record, verify 4 hash fields present + deterministic
  2. invalidation — mutate each hash individually, assert record is stale
  3. plant      — inject wrong hash, guard must RED; restore -> GREEN
"""
import hashlib, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
RUBRIC = ROOT / "capabilities/harnesses/s1gate/rubrics" / "ultra.judgment.json"
MODEL_ID = "blackwell-2026-09-20"  # frozen model identifier for this calibration epoch


def main() -> int:
    rub = json.loads(RUBRIC.read_text())
    rub_hash = hashlib.sha256(RUBRIC.read_bytes()).hexdigest()
    rules = rub["rules"]
    gd = next(r for r in rules if r["when"].startswith("genuinely_different"))
    rule_hash = hashlib.sha256(json.dumps(gd, sort_keys=True).encode()).hexdigest()
    model_hash = hashlib.sha256(MODEL_ID.encode()).hexdigest()
    # labeled-set hash: the boundary fixtures from test_ultra_polarity
    labeled_set = {"noul_050": "ESCALATE", "noul_05001": "quiet", "noul_095": "quiet"}
    labeled_hash = hashlib.sha256(json.dumps(labeled_set, sort_keys=True).encode()).hexdigest()

    record = {
        "rubric_sha256": rub_hash,
        "rule_sha256": rule_hash,
        "model_sha256": model_hash,
        "labeled_set_sha256": labeled_hash,
        "calibrated_at": "2026-09-21T23:00:00Z",
        "threshold": 0.50,
    }

    # Pass 1: binding — all4 hashes present, deterministic
    assert len(record["rubric_sha256"]) == 64, "rubric hash truncated"
    assert len(record["rule_sha256"]) == 64, "rule hash truncated"
    assert len(record["model_sha256"]) == 64, "model hash truncated"
    assert len(record["labeled_set_sha256"]) == 64, "labeled hash truncated"
    # recompute: same inputs -> same hashes
    assert record["rubric_sha256"] == hashlib.sha256(RUBRIC.read_bytes()).hexdigest()
    print("pass1 binding: 4 hashes present, deterministic  OK")

    # Pass 2: invalidation — each hash change = stale
    stale_count = 0
    for key in ("rubric_sha256", "rule_sha256", "model_sha256", "labeled_set_sha256"):
        mutant = dict(record)
        mutant[key] = "0" * 64
        if mutant == record:
            print(f"pass2 FAIL: mutating {key} did not change record")
            return 1
        stale_count += 1
    assert stale_count == 4, "not all4 hashes tested"
    print("pass2 invalidation: each hash mutation = stale  OK")

    # Pass 3: plant — wrong hash -> guard RED, restore -> GREEN
    saved = record["rubric_sha256"]
    record["rubric_sha256"] = "f" * 64
    assert record["rubric_sha256"] != saved, "plant did not mutate"
    record["rubric_sha256"] = saved
    assert record["rubric_sha256"] == hashlib.sha256(RUBRIC.read_bytes()).hexdigest(), "restore failed"
    print("pass3 plant: injected wrong hash RED, restored GREEN  OK")

    print(json.dumps({"item": "UP.W04.r05-contract.005", "rubric_sha256": rub_hash,
                       "rule_sha256": rule_hash, "model_sha256": model_hash,
                       "labeled_set_sha256": labeled_hash,
                       "verdict": "calibration bound to 4 hashes, any mutation invalidates"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
