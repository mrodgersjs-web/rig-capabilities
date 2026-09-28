#!/usr/bin/env python3
"""Consolidate the per-channel scrape manifests into the google-ads registry.

Reads .context/google-ads-creators/<slug>/manifest.json (scrape_channel_corpus.py output),
enforces the 1,500-transcript cap with the quota rule fixed in TARGETS.md before capture
(channels with <= 160 catalog videos fully covered; the remainder shared proportionally,
newest first per channel), and writes:
  data/corpora/google-ads/manifest.jsonl   one row per captured transcript (registry)
  data/corpora/google-ads/counts.json      honest capture counts
  data/corpora/google-ads/skipped.json    what the cap skipped, per channel

Fails (exit 2) if the consolidated unique transcript count exceeds the cap.
No network. usage: consolidate.py
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path("/Users/rig128gb/Developer/rig-capabilities")
SRC = REPO / ".context/google-ads-creators"
CORP = REPO / "data/corpora/google-ads"
CAP = 1500
SMALL = 160  # channels with <= this many catalog videos are captured complete

# catalog sizes from data/corpora/google-ads/discovery/<slug>.json (unique videos)
CATALOG = {
    "solutions8": 1014, "surfsideppc": 983, "paid-search-podcast": 612,
    "aaron-young": 472, "jyll-saskin-gales": 385, "optmyzr": 363,
    "growmyads": 158, "ben-heath": 143, "ppcmasterycom": 56,
}


def quotas():
    small = {s: n for s, n in CATALOG.items() if n <= SMALL}
    big = {s: n for s, n in CATALOG.items() if n > SMALL}
    budget = CAP - sum(small.values())
    tot = sum(big.values())
    q = dict(small)
    left = budget
    for i, (s, n) in enumerate(sorted(big.items(), key=lambda kv: -kv[1])):
        share = budget * n // tot if i < len(big) - 1 else left
        q[s] = min(n, share)
        left -= q[s]
    return q


def main():
    q = quotas()
    rows, skipped, seen = [], defaultdict(list), set()
    for slug in sorted(CATALOG):
        mf = SRC / slug / "manifest.json"
        if not mf.exists():
            print(f"missing scrape manifest: {mf}", file=sys.stderr)
            return 1
        doc = json.loads(mf.read_text(encoding="utf-8"))
        vids = [v for v in doc["videos"] if v.get("words")]
        vids.sort(key=lambda v: v.get("timestamp") or 0, reverse=True)  # newest first
        keep, n = [], 0
        for v in vids:
            if v["id"] in seen:
                continue
            if n < q[slug]:
                keep.append(v)
                seen.add(v["id"])
                n += 1
            else:
                skipped.append({"channel": slug, "id": v["id"], "title": v.get("title"),
                                "published": v.get("published")})
        for v in keep:
            rel = (Path(v["transcript"])).relative_to(REPO) if Path(v["transcript"]).is_absolute() \
                else Path(v["transcript"])
            rows.append({
                "video_id": v["id"], "channel": doc.get("channel"), "handle": slug,
                "surface": slug, "url": v.get("url"),
                "title": v.get("title"), "words": v.get("words"),
                "duration_s": v.get("duration"), "published": v.get("published"),
                "caption_track": "en (YouTube auto-generated)",
                "file": str(rel), "sha256": v.get("transcript_sha256"),
            })
    total = len(rows)
    if total > CAP:
        print(f"CAP BREACH: {total} > {CAP}", file=sys.stderr)
        return 2
    rows.sort(key=lambda r: (r["handle"], r["published"] or ""))
    CORP.mkdir(parents=True, exist_ok=True)
    with (CORP / "manifest.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    per_channel = defaultdict(int)
    words = defaultdict(int)
    for r in rows:
        per_channel[r["handle"]] += 1
        words[r["handle"]] += r["words"] or 0
    counts = {
        "cap": CAP, "quota_rule": f"catalogs <= {SMALL} videos complete; remainder proportional, newest first",
        "quota": q, "captured_unique": total,
        "per_channel": dict(per_channel), "words_per_channel": dict(words),
        "total_words": sum(words.values()),
        "skipped_beyond_cap": len(skipped),
        "channels": len(per_channel),
    }
    (CORP / "counts.json").write_text(json.dumps(counts, indent=1) + "\n", encoding="utf-8")
    (CORP / "skipped.json").write_text(json.dumps(skipped, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(counts, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
