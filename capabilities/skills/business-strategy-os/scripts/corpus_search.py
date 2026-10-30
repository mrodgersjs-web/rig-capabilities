#!/usr/bin/env python3
"""BM25 search over the strategy corpus (data/corpora/strategy/business-strategy/<handle>/<videoId>.txt).
Deterministic: fixed tokenizer, k1=1.2, b=0.75, ties broken by video_id. Returns CLAIM-ready rows.

usage: corpus_search.py "query words" [-k 8] [--handle alexmhsmith] [--json]
exit:  0 results | 1 usage or corpus missing | 3 no document matched"""
import argparse, json, math, re, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[4]
BASE = REPO / "data/corpora/strategy"
TOK = re.compile(r"[a-z0-9]+")
STOP = set("the a an and or of to in on for with is are was were be it that this as at by from we you they i our your their".split())
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("query"); ap.add_argument("-k", type=int, default=8)
    ap.add_argument("--handle"); ap.add_argument("--json", action="store_true"); a = ap.parse_args()
    man = BASE / "manifest.jsonl"
    if not man.exists(): print("manifest missing", file=sys.stderr); return 1
    rows = [json.loads(l) for l in man.open() if l.strip()]
    if a.handle: rows = [r for r in rows if r["handle"] == a.handle]
    terms = [t for t in TOK.findall(a.query.lower()) if t not in STOP]
    if not terms: print("empty query", file=sys.stderr); return 1
    N = len(rows); avg = sum(r["words"] for r in rows) / max(1, N)
    tf, df, bodies = {}, {t: 0 for t in terms}, {}
    for r in rows:
        p = BASE / "business-strategy" / r["handle"] / f"{r['video_id']}.txt"
        body = p.read_text(encoding="utf-8", errors="ignore").split("\n---\n", 1)[-1].lower()
        counts = {t: len(re.findall(r"\b%s\b" % re.escape(t), body)) for t in terms}
        if any(counts.values()):
            tf[r["video_id"]] = counts; bodies[r["video_id"]] = body
            for t, c in counts.items(): df[t] += 1 if c else 0
    scored = []
    for r in rows:
        c = tf.get(r["video_id"])
        if not c: continue
        s = 0.0
        for t in terms:
            if not c[t]: continue
            idf = math.log(1 + (N - df[t] + 0.5) / (df[t] + 0.5))
            s += idf * c[t] * 2.2 / (c[t] + 1.2 * (0.25 + 0.75 * r["words"] / avg))
        phrase = " ".join(TOK.findall(a.query.lower()))
        if len(terms) > 1 and phrase in " ".join(TOK.findall(bodies[r["video_id"]])):
            s += 5.0 * " ".join(TOK.findall(bodies[r["video_id"]])).count(phrase)   # exact-phrase boost
        scored.append((round(s, 4), r))
    scored.sort(key=lambda x: (-x[0], x[1]["video_id"]))
    out = []
    for s, r in scored[: a.k]:
        body = bodies[r["video_id"]]; best, bi = -1, 0
        for m in re.finditer(r"\b%s\b" % re.escape(terms[0]), body):
            win = body[max(0, m.start() - 240): m.start() + 240]
            sc = sum(1 for t in terms if t in win)
            if sc > best: best, bi = sc, m.start()
        out.append({"claim": f"CLAIM({r['video_id']})", "score": s, "handle": r["handle"], "channel": r["channel"],
                    "title": r["title"], "url": r["url"], "snippet": " ".join(body[max(0, bi - 240): bi + 240].split())})
    if not out: print("no match", file=sys.stderr); return 3
    if a.json: print(json.dumps(out, indent=1))
    else:
        for o in out: print(f"{o['claim']} {o['score']:.2f} @{o['handle']} | {o['title']}\n    ...{o['snippet'][:300]}...\n")
    return 0
if __name__ == "__main__":
    sys.exit(main())
