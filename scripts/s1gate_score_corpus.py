#!/usr/bin/env python3
"""Score the labelled corpus through the live System One API and label the
resulting decisions, so the calibration sweep has real data to measure.

Scoring and labelling are separate acts: the model never sees the label, and
the label is written only after the answer is recorded.
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rig_capabilities.s1gate import DecisionLog, evaluate, load_rubric  # noqa: E402

CORPUS = Path.home() / "Developer/rig-capabilities/capabilities/golden/s1gate/code-diff-corpus.jsonl"
RUBRIC = "code.diff"
WORKERS = 6


def main() -> int:
    rows = [json.loads(l) for l in CORPUS.read_text(encoding="utf-8").splitlines() if l.strip()]
    rb = load_rubric(RUBRIC)
    print("scoring %d rows against %s (%s)" % (len(rows), RUBRIC, rb.description[:50]))

    done = {"n": 0, "err": 0}
    t0 = time.time()
    first_error = []

    # A sqlite connection cannot cross threads, so scoring fans out WITHOUT the
    # log and every write happens serially on the main thread afterwards.
    def work(row):
        state = "Task: %s\n\nDiff:\n%s" % (row["task_text"], row["diff_text"])
        try:
            res = evaluate(rb, state, subject=row["id"], log=None)
        except Exception as exc:  # noqa: BLE001
            done["err"] += 1
            if not first_error:
                first_error.append("%s: %s" % (type(exc).__name__, exc))
            return None
        done["n"] += 1
        if done["n"] % 25 == 0:
            print("  %d/%d  (%.0fs)" % (done["n"], len(rows), time.time() - t0), flush=True)
        if res.error:
            done["err"] += 1
            if not first_error:
                first_error.append(res.error)
            return None
        return (res, row["label"])

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(work, rows))

    log = DecisionLog()
    labelled = 0
    for r in results:
        if not r:
            continue
        res, label = r
        did = log.record(res)
        log.label(did, label, by="corpus:git-history")
        labelled += 1
    if first_error:
        print("first error: %s" % first_error[0])
    counts = log.counts(RUBRIC)
    log.close()

    print("\nscored  : %d" % done["n"])
    print("errors  : %d" % done["err"])
    print("labelled: %d" % labelled)
    print("elapsed : %.1fs" % (time.time() - t0))
    print("verdicts: %s" % counts)
    return 0 if labelled >= 30 else 1


if __name__ == "__main__":
    sys.exit(main())
