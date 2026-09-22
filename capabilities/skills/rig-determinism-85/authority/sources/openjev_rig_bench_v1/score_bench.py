#!/usr/bin/env python3
"""Score an evidence packet with the JEV jev.bench rubric and report per-category means on 0-10.

JEV returns a level index in [0,9] per question. The gate contract is expressed on a 0-10
scale, so each answer is rescaled score10 = score9 * 10/9. A category passes only if the
mean of its five questions is >= 9.5/10.

Usage: score_bench.py <evidence-file> [--json out.json]
"""
import argparse
import collections
import json
import subprocess
import sys

RUBRIC = "jev.bench"
THRESHOLD = 9.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("evidence")
    ap.add_argument("--json", dest="out", default="")
    args = ap.parse_args()

    proc = subprocess.run(["rig-s1gate", "check", RUBRIC, "--file", args.evidence, "--json"],
                          capture_output=True, text=True)
    try:
        d = json.loads(proc.stdout)
    except json.JSONDecodeError:
        print("s1gate did not return JSON:", proc.stdout[:400], proc.stderr[:400])
        return 3
    answers = d.get("answers") or {}
    if not answers:
        print(f"NO ANSWERS. verdict={d.get('verdict')} reasons={d.get('reasons')}")
        return 3

    cats = collections.defaultdict(dict)
    for qid, a in answers.items():
        cat, arch = qid.split("__", 1)
        cats[cat][arch] = float(a["score"]) * 10.0 / 9.0

    rows, failing = [], []
    for cat in sorted(cats):
        qs = cats[cat]
        mean = sum(qs.values()) / len(qs)
        ok = mean >= THRESHOLD
        if not ok:
            failing.append((cat, mean, min(qs.items(), key=lambda kv: kv[1])))
        rows.append((cat, mean, ok, qs))

    width = max(len(c) for c in cats)
    print(f"{'category':<{width}}  mean/10  verdict   weakest question")
    for cat, mean, ok, qs in rows:
        weak_k, weak_v = min(qs.items(), key=lambda kv: kv[1])
        print(f"{cat:<{width}}  {mean:7.2f}  {'PASS' if ok else 'FAIL':<8}  {weak_k}={weak_v:.2f}")

    overall = min(m for _, m, _, _ in rows)
    n_pass = sum(1 for _, _, ok, _ in rows if ok)
    print(f"\ncategories passing >= {THRESHOLD}/10: {n_pass}/{len(rows)}   worst category mean: {overall:.2f}")
    print(f"s1gate verdict={d.get('verdict')} model={d.get('model')} decision_id={d.get('decision_id')} "
          f"state_sha256={d.get('state_sha256')}")

    if args.out:
        json.dump({"threshold": THRESHOLD, "s1gate_verdict": d.get("verdict"), "model": d.get("model"),
                   "decision_id": d.get("decision_id"), "state_sha256": d.get("state_sha256"),
                   "categories": {c: {"mean_10": m, "pass": ok, "questions": qs} for c, m, ok, qs in rows},
                   "categories_passing": n_pass, "n_categories": len(rows), "worst_mean": overall},
                  open(args.out, "w"), indent=2)
        print("wrote", args.out)
    return 0 if n_pass == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
