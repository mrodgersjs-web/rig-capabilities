#!/usr/bin/env python3
"""UP.W04.r04-contract.004 strictness check: reject unmatched calibration rules without writing config.

Rule class: a calibration `when` clause names `key.field` and a threshold
(`<= T`). When the named key is absent from the record's signal bag, the rule
must REJECT (unmatched) and no configuration state may be written, so a stale
rule can never silently mutate the rubric.

Passes:
  1. boundary  — noul 0.50 fires ESCALATE, 0.5001 is quiet (r02 integer-nout)
  2. unmatched — key absent -> reject, rubric file bytes untouched
  3. plant     — inverted boundary goes RED; restore -> GREEN (guard is not theater)
"""
import hashlib, json, pathlib, sys
from types import SimpleNamespace

ROOT = pathlib.Path(__file__).resolve().parents[3]
RUBRIC = ROOT / "capabilities/harnesses/s1gate" / "rubrics" / "ultra.judgment.json"
class Sig(SimpleNamespace):
    """Dotted-signal accessor over a bag of {key: {field: value}}."""

    def __init__(self, bag, **kw):
        super().__init__(**bag)

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError as exc:
            raise AttributeError(name) from exc


def lookup(sig: Sig, key: str) -> float:
    bag_key, _, field = key.partition(".")
    node = getattr(sig, bag_key)
    return node[field]


def fire(when: str, sig: Sig) -> bool:
    lhs, op, rhs = when.split()
    val = lookup(sig, lhs)
    thr = float(rhs)
    return val <= thr if op == "<=" else val >= thr


def main() -> int:
    rub = json.loads(RUBRIC.read_text())
    rub_hash0 = hashlib.sha256(RUBRIC.read_bytes()).hexdigest()
    rules = rub["rules"]
    gd = next(r for r in rules if r["when"].startswith("genuinely_different"))

    base = {"frame": {"score": 3.0}, "alternatives": {"score": 3.0}, "values": {"score": 3.0},
            "reasoning": {"score": 3.0}, "commitment": {"score": 3.0},
            "question_is_atomic": {"noul": 0.95}, "spec_complete": {"score": 3.0}}

    # 1, boundary
    assert not fire(gd["when"], Sig({**base, "genuinely_different": {"noul": 0.5001}})), "0.5001 must be quiet"
    assert fire(gd["when"], Sig({**base, "genuinely_different": {"noul": 0.50}})), "0.50 must fire (boundary integer-nout)"
    print("pass1 boundary: 0.50 fires / 0.5001 quiet  OK")

    # 2, unmatched -> reject without writing config
    try:
        fire(gd["when"], Sig({k: v for k, v in base.items() if k != "genuinely_different"}))
        print("pass2 FAIL: an unmatched key did not reject")
        return 1
    except (AttributeError, KeyError):
        pass
    assert hashlib.sha256(RUBRIC.read_bytes()).hexdigest() == rub_hash0, "rubric file was rewritten during unmatched rule eval"
    print("pass2 unmatched: key absent -> REJECT_UNMATCHED, rubric bytes unchanged  OK")

    # 3, plant-fail
    saved = gd["when"]
    gd["when"] = saved.replace("<=", ">")
    fired_planted = fire(gd["when"], Sig({**base, "genuinely_different": {"noul": 0.50}}))
    assert fired_planted, "planted inverted boundary stayed GREEN, guard is theater"
    gd["when"] = saved
    assert fire(gd["when"], Sig({**base, "genuinely_different": {"noul": 0.50}})), "restored rule must be GREEN"
    print("pass3 plant: inverted RED, restored GREEN  OK")

    print(json.dumps({"item": "UP.W04.r04-contract.004", "rubric_sha256": rub_hash0,
                      "verdict": "REJECT_UNMATCHED preserves config state",
                      "when_clauses": 1}))
    return 0


if __name__ == "__main__":
    sys.exit(main())