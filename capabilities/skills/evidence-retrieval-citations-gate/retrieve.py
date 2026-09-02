#!/usr/bin/env python3
"""Ranked evidence retrieval over the capability corpus, with a citations gate
and a keyword baseline it must beat — all deterministic, stdlib only.

Three jobs, one file:

  retrieve   BM25-lite ranking of corpus docs for a query. Each returned row
             carries the source ids it cites (video / arXiv / oss).
  gate       every cited id on a returned row MUST resolve in the source
             registry; an unresolvable citation is exit 2. This is the load-
             bearing clause: a retrieval that returns a claim whose evidence
             does not exist is worse than returning nothing.
  benchmark  over a labelled probe set (query -> the doc id that should rank #1),
             BM25 must (a) put the gold doc first for >= the declared hit floor
             and (b) beat a naive keyword-overlap baseline on mean reciprocal
             rank. If retrieval does not beat the baseline, exit 2 — a ranker
             that cannot outscore set-overlap is not earning its complexity.

Corpus  = the capability matrix rows (name + mechanism + rig_delta as the doc).
Registry = the union of every row's sources/papers/oss ids.
Exit codes: 0 clean / 1 usage-or-file-missing / 2 contract violation.
No network, no model, no writes.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

TOKEN = re.compile(r"[a-z0-9]+")


def _tok(text: str) -> list:
    return TOKEN.findall(text.lower())


def load_corpus(matrix_path: Path):
    """Return docs from the matrix. docs: [{id, text, tokens, cites}].

    NOTE: the citation registry is deliberately NOT built here. Resolving a
    returned claim's citations against the same rows being ranked is self-
    vouching — a planted bogus id would be added to the registry and pass. The
    gate loads an INDEPENDENT registry (load_registry) instead.
    """
    mx = json.loads(matrix_path.read_text(encoding="utf-8"))
    rows = mx["capabilities"] if isinstance(mx, dict) else mx
    docs = []
    for r in rows:
        cites = list(r.get("sources") or []) + list(r.get("papers") or []) \
            + list(r.get("oss") or [])
        text = " ".join(str(r.get(k, "")) for k in ("name", "mechanism", "rig_delta"))
        docs.append({"id": r["name"], "text": text, "tokens": _tok(text),
                     "cites": cites})
    return docs


def load_registry(registry_path: Path) -> set:
    """The independent set of resolvable source ids (videos + arXiv + oss)."""
    reg = json.loads(registry_path.read_text(encoding="utf-8"))
    return set(reg.get("videos", [])) | set(reg.get("arxiv", [])) \
        | set(reg.get("oss", []))


def _bm25(docs, query_tokens, k1=1.5, b=0.75):
    N = len(docs)
    avgdl = sum(len(d["tokens"]) for d in docs) / max(N, 1)
    df = Counter()
    for d in docs:
        for t in set(d["tokens"]):
            df[t] += 1
    scores = []
    for d in docs:
        tf = Counter(d["tokens"])
        dl = len(d["tokens"])
        s = 0.0
        for q in query_tokens:
            if q not in tf:
                continue
            idf = math.log(1 + (N - df[q] + 0.5) / (df[q] + 0.5))
            s += idf * (tf[q] * (k1 + 1)) / (tf[q] + k1 * (1 - b + b * dl / avgdl))
        scores.append((s, d["id"]))
    # deterministic tie-break by id
    scores.sort(key=lambda x: (-x[0], x[1]))
    return scores


def _keyword_overlap(docs, query_tokens):
    """The baseline BM25 must beat: raw count of query tokens present."""
    q = set(query_tokens)
    scores = [(len(q & set(d["tokens"])), d["id"]) for d in docs]
    scores.sort(key=lambda x: (-x[0], x[1]))
    return scores


def _rank_of(scores, gold):
    for i, (_, did) in enumerate(scores, 1):
        if did == gold:
            return i
    return len(scores) + 1


def cmd_retrieve(args) -> int:
    docs = load_corpus(Path(args.matrix))
    ranked = _bm25(docs, _tok(args.query))[: args.k]
    by_id = {d["id"]: d for d in docs}
    out = [{"id": did, "score": round(s, 4), "cites": by_id[did]["cites"]}
           for s, did in ranked]
    print(json.dumps({"query": args.query, "results": out}, indent=1))
    return 0


def cmd_gate(args) -> int:
    """Every cited id on every returned row must resolve in the INDEPENDENT
    registry — never in the corpus under test, or a planted id self-vouches."""
    docs = load_corpus(Path(args.matrix))
    registry = load_registry(Path(args.registry))
    ranked = _bm25(docs, _tok(args.query))[: args.k]
    by_id = {d["id"]: d for d in docs}
    unresolved = []
    for _, did in ranked:
        d = by_id[did]
        if not d["cites"]:
            unresolved.append((did, "<no citation>"))
        for c in d["cites"]:
            if c not in registry:
                unresolved.append((did, c))
    if unresolved:
        for did, c in unresolved:
            print(f"UNRESOLVED_CITATION {did}: {c}")
        print(f"\ngate: {len(unresolved)} unresolved citation(s)")
        return 2
    print(f"OK gate: {len(ranked)} result(s), every citation resolves "
          f"in an independent registry of {len(registry)}")
    return 0


def cmd_benchmark(args) -> int:
    docs = load_corpus(Path(args.matrix))
    probes = json.loads(Path(args.probes).read_text(encoding="utf-8"))
    ids = {d["id"] for d in docs}
    bad_gold = [p for p in probes if p["gold"] not in ids]
    if bad_gold:
        for p in bad_gold:
            print(f"PROBE_GOLD_NOT_IN_CORPUS: {p['gold']}")
        return 2
    bm25_rr, kw_rr, hits = [], [], 0
    for p in probes:
        qt = _tok(p["query"])
        rb = _rank_of(_bm25(docs, qt), p["gold"])
        rk = _rank_of(_keyword_overlap(docs, qt), p["gold"])
        bm25_rr.append(1.0 / rb)
        kw_rr.append(1.0 / rk)
        if rb == 1:
            hits += 1
    n = len(probes)
    bm25_mrr = sum(bm25_rr) / n
    kw_mrr = sum(kw_rr) / n
    hit_rate = hits / n
    floor = args.hit_floor
    report = {"probes": n, "bm25_mrr": round(bm25_mrr, 4),
              "keyword_mrr": round(kw_mrr, 4), "hit_at_1": round(hit_rate, 4),
              "hit_floor": floor}
    print(json.dumps(report, indent=1))
    if hit_rate < floor:
        print(f"\nbenchmark: hit@1 {hit_rate:.3f} below floor {floor}")
        return 2
    if not (bm25_mrr > kw_mrr):
        print(f"\nbenchmark: bm25 MRR {bm25_mrr:.4f} does not beat "
              f"keyword baseline {kw_mrr:.4f}")
        return 2
    print(f"\nOK benchmark: bm25 MRR {bm25_mrr:.4f} > keyword {kw_mrr:.4f}, "
          f"hit@1 {hit_rate:.3f} >= {floor}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="evidence retrieval + citations gate")
    sub = ap.add_subparsers(dest="cmd", required=True)
    common = {"matrix": None}
    for name in ("retrieve", "gate"):
        s = sub.add_parser(name)
        s.add_argument("--matrix", required=True)
        s.add_argument("--query", required=True)
        s.add_argument("-k", type=int, default=5)
        if name == "gate":
            s.add_argument("--registry", required=True)
    b = sub.add_parser("benchmark")
    b.add_argument("--matrix", required=True)
    b.add_argument("--probes", required=True)
    b.add_argument("--hit-floor", type=float, default=0.6)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "retrieve":
            return cmd_retrieve(args)
        if args.cmd == "gate":
            return cmd_gate(args)
        if args.cmd == "benchmark":
            return cmd_benchmark(args)
    except FileNotFoundError as e:
        print(f"file not found: {e}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
