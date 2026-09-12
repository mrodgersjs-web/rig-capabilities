"""Build diagnosis packet: the frozen input contract before any build.

The schema is fixed HERE and proven by rejection fixtures in `selftest`:
anything that is not a complete, cell-bound, evidence-bound diagnosis is
refused. No defaults fill semantic gaps — a missing field is a rejection,
not a 0.5.

Usage: python3 rig_capabilities/build_diagnose.py selftest
"""
from __future__ import annotations

import json
import sys

REQUIRED = ("goal", "cell_id", "done_test", "out_of_scope",
            "effort_budget", "evidence_refs")
BUDGET_KEYS = ("cpu_minutes", "usd", "wallclock_seconds")
VALID_CELL_IDS: frozenset[str] | None = None  # lazy from criteria pack


class DiagnoseError(ValueError):
    pass


def _cell_ids() -> frozenset[str]:
    global VALID_CELL_IDS
    if VALID_CELL_IDS is None:
        import pathlib
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
        from rig_capabilities import criteria_pack as cp
        VALID_CELL_IDS = frozenset(r["cell_id"] for r in cp.build_rows())
    return VALID_CELL_IDS

def diagnose(payload: dict, known_cells: set[str] | None = None) -> dict:
    """Validate and normalize a diagnosis packet; raise DiagnoseError."""
    if not isinstance(payload, dict):
        raise DiagnoseError("payload must be a mapping")
    for f in REQUIRED:
        if f not in payload:
            raise DiagnoseError(f"missing required field: {f}")
    goal = payload["goal"]
    if not isinstance(goal, str) or not goal.strip():
        raise DiagnoseError("goal must be a non-empty string")
    cells = known_cells if known_cells is not None else _cell_ids()
    cid = payload["cell_id"]
    if cid not in cells:
        raise DiagnoseError(f"cell_id not in the 588-cell authority: {cid!r}")
    dt = payload["done_test"]
    if not isinstance(dt, list) or not dt or \
            not all(isinstance(c, str) and c.strip() for c in dt):
        raise DiagnoseError("done_test must be a non-empty list of commands")
    oos = payload["out_of_scope"]
    if not isinstance(oos, list) or \
            not all(isinstance(c, str) and c.strip() for c in oos):
        raise DiagnoseError("out_of_scope must be a list of strings")
    eb = payload["effort_budget"]
    if not isinstance(eb, dict) or set(eb) != set(BUDGET_KEYS) or \
            not all(isinstance(eb[k], (int, float)) and eb[k] > 0
                    for k in BUDGET_KEYS):
        raise DiagnoseError(f"effort_budget must be exactly {BUDGET_KEYS}, positive")
    refs = payload["evidence_refs"]
    if not isinstance(refs, list) or not refs or \
            not all(isinstance(r, str) and ":" in r for r in refs):
        raise DiagnoseError("evidence_refs must be non-empty 'kind:value' strings")
    return {
        "goal": goal.strip(),
        "cell_id": cid,
        "done_test": [c.strip() for c in dt],
        "out_of_scope": list(oos),
        "effort_budget": dict(eb),
        "evidence_refs": list(refs),
    }


GOOD = {
    "goal": "ship the pack",
    "cell_id": "L1-D1-A1-I1",
    "done_test": ["python3 rig_capabilities/criteria_pack.py generate --verify "
                  "runs/agentic-stack-buildout/packs/criteria-v1.jsonl"],
    "out_of_scope": ["push"],
    "effort_budget": {"cpu_minutes": 30, "usd": 0.01, "wallclock_seconds": 900},
    "evidence_refs": ["receipt:s4-manifest-gate-fires"],
}


def selftest(argv=None) -> int:
    good = dict(GOOD)
    cases = {
        "unknown cell (vendored dialect)": (
            {**good, "cell_id": "L1-1-A1-I1"}, "authority"),
        "missing field": ({k: v for k, v in good.items() if k != "goal"}, "goal"),
        "empty goal": ({**good, "goal": "  "}, "goal"),
        "unknown cell": ({**good, "cell_id": "L9-9-Z9-X9"}, "authority"),
        "empty done_test": ({**good, "done_test": []}, "done_test"),
        "non-list done_test": ({**good, "done_test": "pytest"}, "done_test"),
        "budget missing key": ({**good, "effort_budget":
                                {"cpu_minutes": 1, "usd": 1}}, "effort_budget"),
        "budget zero": ({**good, "effort_budget": {"cpu_minutes": 0, "usd": 1,
                                                   "wallclock_seconds": 1}},
                        "effort_budget"),
        "ref without kind": ({**good, "evidence_refs": ["justatext"]},
                             "evidence_refs"),
        "not a mapping": ("hello", "mapping"),
    }
    errs = []
    if diagnose(good)["cell_id"] != good["cell_id"]:
        errs.append("valid packet rejected")
    for name, (bad, frag) in cases.items():
        try:
            diagnose(bad)
            errs.append(f"{name}: accepted")
        except DiagnoseError as e:
            if frag not in str(e):
                errs.append(f"{name}: wrong reason {e}")
    print(json.dumps({"ok": not errs, "errors": errs, "rejections": len(cases)}))
    return 0 if not errs else 1


if __name__ == "__main__":
    _a = sys.argv[1:]
    if _a and _a[0] not in ("selftest", "--help"):
        print("usage: build_diagnose.py [selftest|--help]", file=sys.stderr)
        sys.exit(2)
    sys.exit(selftest())
