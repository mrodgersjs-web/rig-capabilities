#!/usr/bin/env python3
"""Extract latents for the RIG-native NLI corpus using the same frozen OpenJEV backbone.

RIG rows are (premise, hypothesis, label) with label 0=contradiction, 1=entailment, 2=neutral.
The decision head is a binary scorer over options grouped per question, so rows are grouped by
premise: each premise group becomes one synthetic question whose "correct option" is the
entailment hypothesis and whose distractors are that premise's contradiction/neutral rows.
Groups without at least one entailment and one non-entailment are dropped (they carry no
ranking signal).
"""
import argparse
import collections
import json
import os
import sys
import time

import numpy as np
import torch

OPENJEV = "/Users/rig128gb/.rig/openjev"
sys.path.insert(0, f"{OPENJEV}/code")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="/Users/rig128gb/.rig/openjev-rig/rig_nli_corpus.jsonl")
    ap.add_argument("--ckpt", default=f"{OPENJEV}/qwen3.5-0.8b-nli-v2s-long")
    ap.add_argument("--out", default="/Users/rig128gb/.rig/openjev-rig/latents/rig_train.npz")
    ap.add_argument("--bs", type=int, default=64)
    ap.add_argument("--max_len", type=int, default=384)
    args = ap.parse_args()

    rows = [json.loads(l) for l in open(args.corpus) if l.strip()]
    groups = collections.defaultdict(list)
    for r in rows:
        groups[r["premise"]].append(r)

    texts, qid, gold, kept, dropped = [], [], [], 0, 0
    for prem, members in groups.items():
        ent = [m for m in members if int(m["label"]) == 1]
        neg = [m for m in members if int(m["label"]) != 1]
        if not ent or not neg:
            dropped += 1
            continue
        for m in ([ent[0]] + neg):
            texts.append((prem, m["hypothesis"]))
            qid.append(kept)
            gold.append(1 if int(m["label"]) == 1 else 0)
        kept += 1
    print(f"corpus rows={len(rows)} premise_groups={len(groups)} usable_questions={kept} "
          f"dropped_groups={dropped} pairs={len(texts)}", flush=True)
    if not texts:
        print("FAIL: no usable RIG questions; corpus needs >=1 entailment and >=1 non-entailment per premise")
        return 1

    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.ckpt)
    model = AutoModelForSequenceClassification.from_pretrained(args.ckpt, dtype=torch.float32).to("mps").eval()
    template = getattr(model.config, "nli_template", None) or "Premise: {premise}\nHypothesis: {hypothesis}"
    if model.config.get_text_config().pad_token_id is None:
        model.config.get_text_config().pad_token_id = tok.pad_token_id
    tok.padding_side = "right"
    backbone = getattr(model, model.base_model_prefix)

    flat = [template.format(premise=p.strip(), hypothesis=h.strip()) for p, h in texts]
    order = np.argsort([-len(t) for t in flat])
    X = np.zeros((len(flat), model.config.get_text_config().hidden_size), dtype=np.float16)
    L = np.zeros((len(flat), 3), dtype=np.float32)
    t0 = time.time()
    with torch.no_grad():
        for s in range(0, len(order), args.bs):
            idx = order[s:s + args.bs]
            enc = tok([flat[i] for i in idx], truncation=True, max_length=args.max_len,
                      padding=True, return_tensors="pt").to("mps")
            h = backbone(**enc).last_hidden_state
            last = enc["attention_mask"].sum(1) - 1
            pooled = h[torch.arange(h.shape[0], device=h.device), last]
            X[idx] = pooled.float().cpu().numpy().astype(np.float16)
            L[idx] = model.score(pooled).float().cpu().numpy()
            if s % (args.bs * 20) == 0:
                el = time.time() - t0
                print(f"  {s+len(idx)}/{len(flat)} pairs {(s+len(idx))/max(el,1e-9):.1f}/s", flush=True)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    np.savez(args.out, X=X, nli=L, qid=np.array(qid), gold=np.array(gold),
             nopts=np.array([sum(1 for q in qid if q == i) for i in range(kept)]))
    print(f"WROTE {args.out}: {kept} questions, {len(flat)} pairs, {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
