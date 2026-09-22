#!/usr/bin/env python3
"""Extract frozen-backbone last-token latents from an OpenJEV checkpoint on Apple MPS.

Mirrors openjev/code/latent_mlp.py::extract exactly (same pooling, same template, same
npz schema) but runs on mps in float32 and can resume: an existing complete .npz is skipped.

Output per task: {out}/{task}_{split}.npz with X (fp16 latents), nli (3 logits), qid, gold, nopts.
"""
import argparse
import os
import sys
import time

import numpy as np
import torch

OPENJEV = "/Users/rig128gb/.rig/openjev"
sys.path.insert(0, f"{OPENJEV}/code")
os.chdir(OPENJEV)  # eval.load_gpqa reads relative data/gpqa_diamond.csv

import eval as E          # noqa: E402
import latent_mlp as LM   # noqa: E402

ALL_TASKS = ["chess", "gsm8k_mc10", "gsm8k_mc4", "hellaswag", "winogrande",
             "arc_challenge", "arc_easy", "gpqa", "mmlu"]


def build_texts(items, template):
    texts, qid, gold, nopts = [], [], [], []
    for i, it in enumerate(items):
        hyp = it.get("hyp") or (lambda o: f"The correct answer is: {o}")
        nopts.append(len(it["opts"]))
        for j, o in enumerate(it["opts"]):
            texts.append(template.format(premise=it["q"].strip(), hypothesis=hyp(o).strip()))
            qid.append(i)
            gold.append(int(j == it["gold"]))
    return texts, np.array(qid), np.array(gold), np.array(nopts)


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default=f"{OPENJEV}/qwen3.5-0.8b-nli-v2s-long")
    ap.add_argument("--out", default="/Users/rig128gb/.rig/openjev-rig/latents")
    ap.add_argument("--tasks", nargs="+", default=ALL_TASKS)
    ap.add_argument("--splits", nargs="+", default=["train", "test"])
    ap.add_argument("--bs", type=int, default=64)
    ap.add_argument("--max_len", type=int, default=384)
    ap.add_argument("--big", action="store_true")
    ap.add_argument("--limit_pairs", type=int, default=0, help="debug: stop after N pairs")
    ap.add_argument("--max_test_q", type=int, default=0,
                    help="cap test questions (deterministic head slice); 0 = full set")
    ap.add_argument("--max_train_q", type=int, default=0,
                    help="cap train questions (deterministic head slice); 0 = full set")
    args = ap.parse_args()

    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.ckpt)
    model = AutoModelForSequenceClassification.from_pretrained(args.ckpt, dtype=torch.float32).to("mps").eval()
    template = getattr(model.config, "nli_template", None) or "Premise: {premise}\nHypothesis: {hypothesis}"
    if model.config.get_text_config().pad_token_id is None:
        model.config.get_text_config().pad_token_id = tok.pad_token_id
    tok.padding_side = "right"
    backbone = getattr(model, model.base_model_prefix)
    os.makedirs(args.out, exist_ok=True)

    def run(items, path, tag):
        if os.path.exists(path):
            print(f"  SKIP {tag} (exists)", flush=True)
            return
        texts, qid, gold, nopts = build_texts(items, template)
        if args.limit_pairs:
            texts = texts[:args.limit_pairs]
        # longest-first batching keeps padding waste low, then restore original order
        order = np.argsort([-len(t) for t in texts])
        X = np.zeros((len(texts), model.config.get_text_config().hidden_size), dtype=np.float16)
        L = np.zeros((len(texts), 3), dtype=np.float32)
        t0, done = time.time(), 0
        for s in range(0, len(order), args.bs):
            idx = order[s:s + args.bs]
            enc = tok([texts[i] for i in idx], truncation=True, max_length=args.max_len,
                      padding=True, return_tensors="pt").to("mps")
            h = backbone(**enc).last_hidden_state
            last = enc["attention_mask"].sum(1) - 1
            pooled = h[torch.arange(h.shape[0], device=h.device), last]
            X[idx] = pooled.float().cpu().numpy().astype(np.float16)
            L[idx] = model.score(pooled).float().cpu().numpy()
            done += len(idx)
            if s % (args.bs * 20) == 0:
                el = time.time() - t0
                print(f"    {tag} {done}/{len(texts)} pairs  {done/max(el,1e-9):.1f} pairs/s  "
                      f"eta {(len(texts)-done)/max(done/max(el,1e-9),1e-9)/60:.1f}m", flush=True)
        np.savez(path, X=X, nli=L, qid=qid[:len(texts)], gold=gold[:len(texts)], nopts=nopts)
        print(f"  WROTE {path}: {len(nopts)} questions, {len(texts)} pairs, "
              f"{time.time()-t0:.0f}s", flush=True)

    for task in args.tasks:
        print(f"== {task}", flush=True)
        for split in args.splits:
            try:
                items = LM.train_items(task, big=args.big) if split == "train" else LM.test_items(task)
            except Exception as e:
                print(f"  FAIL {task}/{split}: {type(e).__name__}: {str(e)[:160]}", flush=True)
                continue
            if split == "train" and getattr(args, "max_train_q", 0) and len(items) > args.max_train_q:
                print(f"  CAP {task}/train {len(items)} -> {args.max_train_q} questions", flush=True)
                items = items[:args.max_train_q]
            if split == "test" and args.max_test_q and len(items) > args.max_test_q:
                # deterministic head slice: same items for every checkpoint, so the
                # baseline and ours are always compared on an identical set
                print(f"  CAP {task}/test {len(items)} -> {args.max_test_q} questions", flush=True)
                items = items[:args.max_test_q]
            run(items, f"{args.out}/{task}_{split}.npz", f"{task}/{split}")


if __name__ == "__main__":
    main()
