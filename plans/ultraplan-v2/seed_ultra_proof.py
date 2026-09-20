#!/usr/bin/env python3
"""Seed the ultra.proof calibration corpus with ground-truth-by-construction labels.

GOOD rows: an atomic claim, a done-test that genuinely discriminates (a real
assertion that goes RED when the named outcome breaks), command-output evidence.
BAD rows: the three named defects the pack asks about -- a vacuous done-test that
passes whatever ships, a compound claim bundling several checks, narrative
evidence ("it works, trust me") instead of a command result.

Ground truth here is construction, not opinion: each row's artifact was authored
to exhibit (bad) or avoid (good) the defect. Labels are written by --apply only.
"""
import argparse
import sys

sys.path.insert(0, "/Users/rig128gb/Developer/rig-capabilities")
from rig_capabilities import s1gate  # noqa: E402

GOOD_CLAIMS = [
    "python3 -m unittest tests.test_ultra_polarity exits 0",
    "the JEX gate re-executes every done-test assertion at verdict time",
    "ultra_gates routes proof.gate_before_register to rework when an executed assertion exits nonzero",
    "the route schema refuses an empty routes list",
    "the event schema refuses a non-hex chain hash",
    "the approval schema refuses a nonce shorter than 16 chars",
    "the projection schema refuses stale as a string",
    "validate_cell refuses a studio: call whose target directory does not exist",
]
BAD_CLAIMS = [
    "the schemas are done and the validator works and the tests all pass",
    "everything in W01 was fully implemented",
    "the system is production ready and verified end to end",
    "the gate is fixed, the tree validates, and JEX is live",
    "all envelope schemas and cell checks and studio discovery are complete",
]
GOOD_TESTS = [
    "cmd:cd /Users/rig128gb/Developer/rig-capabilities && python3 -m unittest tests.test_ultra_polarity",
    "cmd:python3 -c \"assert sum(range(4)) == 6, 'arithmetic broken'\"",
    "cmd:bash -c \"test $(seq 5 | wc -l) -eq 5\"",
    "cmd:python3 -m unittest tests.test_schemas",
    "cmd:git -C /Users/rig128gb/Developer/ultraplan rev-parse 665e59e --verify",
]
BAD_TESTS = [
    "cmd:echo ok",
    "cmd:true",
    "cmd:ls schemas/",
    "cmd:echo 'all good'",
    "cmd:test -f README.md",
    "cmd:echo done",
]
GOOD_EV = [
    "Ran 4 tests in 0.001s\\nOK",
    "665e59e8716543d9039d138a3e16a3d1f471c0aa",
    "33/33 cells valid, 0 orphans (rig-ultra cell tree exit 0)",
    "sha256 bc9809149c490034 recorded in manifest header",
    "assertion exited 3 after 5ms: exit 3 (route=rework)",
]
BAD_EV = [
    "the team confirmed it looks right in review",
    "trust me, I ran it",
    "it works fine on my machine, Jake signed off",
    "we believe the feature is complete",
    "looks good per the transcript",
]


def build_rows():
    rows = []
    for i, claim in enumerate(GOOD_CLAIMS):
        for j in range(3):
            rows.append(("good", claim, GOOD_TESTS[(i + j) % len(GOOD_TESTS)], GOOD_EV[(i + j) % len(GOOD_EV)]))
    for i, claim in enumerate(BAD_CLAIMS):
        for j in range(2):
            rows.append(("bad", claim, BAD_TESTS[(i + j) % len(BAD_TESTS)], BAD_EV[(i + j) % len(BAD_EV)]))
    return rows


def state_for(claim, test, ev):
    return ("CLAIM: %s\nDONE-TEST: %s\nEVIDENCE: %s" % (claim, test, ev))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually call JEV and label (live, costs provider calls)")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    rows = build_rows()
    if args.limit:
        rows = rows[: args.limit]
    rb = s1gate.load_rubric("ultra.proof")
    log = s1gate.DecisionLog()
    n = 0
    for label, claim, test, ev in rows:
        state = state_for(claim, test, ev)
        if not args.apply:
            print("[%s] %s | %s" % (label, claim[:60], test[:50]))
            n += 1
            continue
        res = s1gate.evaluate(rb, state, subject="seed:%s" % claim[:40])
        if res.error:
            print("provider error, stop:", res.error)
            break
        did = log.record(res, subject="seed:%s" % claim[:40])
        log.label(did, label, by="construction")
        n += 1
        print("%3d %s id=%s answers=%s" % (n, label, did, {k: v.get("noul") for k, v in res.answers.items()}))
    print("seeded:", n, "(dry run)" if not args.apply else "LABELLED")


if __name__ == "__main__":
    main()
