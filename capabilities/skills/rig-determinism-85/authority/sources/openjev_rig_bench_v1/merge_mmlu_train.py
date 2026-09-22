#!/usr/bin/env python3
"""Merge the two MMLU training latent sets into one training file.

OpenJEV's published 0.8B run trained the MMLU head on validation+dev only (1816 questions).
Their own code also offers `--big`, which draws from MMLU auxiliary_train. Neither alone is
obviously best: validation+dev is in-domain but tiny, auxiliary_train is large but is
ARC/OBQA/RACE-style rather than MMLU-style. This merges both so the head sees each.

Question ids are re-based so the two sets never collide, which matters because the head's
validation split and the per-question argmax metric both group by qid.
"""
import argparse
import os
import sys

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--small", default="/Users/rig128gb/.rig/openjev-rig/latents/mmlu_train.small.npz")
    ap.add_argument("--big", default="/tmp/mmlu_big_lat/mmlu_train.npz")
    ap.add_argument("--out", default="/Users/rig128gb/.rig/openjev-rig/latents/mmlu_train.npz")
    args = ap.parse_args()

    for p in (args.small, args.big):
        if not os.path.exists(p):
            print(f"FAIL: missing {p}")
            return 1

    a, b = np.load(args.small), np.load(args.big)
    off = int(a["qid"].max()) + 1
    out = {
        "X":     np.concatenate([a["X"], b["X"]]),
        "nli":   np.concatenate([a["nli"], b["nli"]]),
        "qid":   np.concatenate([a["qid"], b["qid"] + off]),
        "gold":  np.concatenate([a["gold"], b["gold"]]),
        "nopts": np.concatenate([a["nopts"], b["nopts"]]),
    }
    np.savez(args.out, **out)
    print(f"merged {len(a['nopts'])} + {len(b['nopts'])} = {len(out['nopts'])} questions "
          f"({len(out['qid'])} pairs) -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
