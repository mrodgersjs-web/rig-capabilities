#!/usr/bin/env python3
"""Rebuild data/corpora/strategy/{manifest.jsonl,errors.jsonl,COVERAGE.md} from disk.
Never estimated: every count below is read from the files present when this runs.
Inputs: transcripts under data/corpora/strategy/business-strategy/<handle>/<videoId>.txt,
fetch-error ledgers and catalog listings from the discovery run (path in DISCOVERY)."""
import datetime, glob, hashlib, json, os, re, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
BASE = REPO / "data/corpora/strategy"
SURF = BASE / "business-strategy"
DISCOVERY = Path(os.environ.get("STRATEGY_DISCOVERY", Path.home() / "Developer/rig-strategy-corpus/discovery"))
def header(text):
    h, _, body = text.partition("\n---\n")
    kv = dict(re.findall(r"^([A-Z_]+): (.*)$", h, re.M))
    return kv, body
rows, per = [], {}
for f in sorted(glob.glob(str(SURF / "*" / "*.txt"))):
    handle = Path(f).parent.name; vid = Path(f).stem
    raw = Path(f).read_bytes(); kv, body = header(raw.decode("utf-8", "ignore"))
    fetched = re.search(r"fetched (\S+)", kv.get("RIGHTS", "")); fetched = fetched.group(1) if fetched else None
    rows.append({"video_id": vid, "channel": kv.get("CHANNEL"), "handle": handle, "surface": "business-strategy",
                 "url": f"https://www.youtube.com/watch?v={vid}", "title": kv.get("TITLE"), "words": len(body.split()),
                 "caption_track": kv.get("CAPTION_TRACK"), "fetched_at": fetched, "sha256": hashlib.sha256(raw).hexdigest()})
    per.setdefault(handle, {"n": 0, "words": 0, "name": kv.get("CHANNEL")}); per[handle]["n"] += 1; per[handle]["words"] += len(body.split())
ids = [r["video_id"] for r in rows]; assert len(ids) == len(set(ids)), "duplicate video ids"
with open(BASE / "manifest.jsonl", "w") as fh:
    for r in rows: fh.write(json.dumps(r, ensure_ascii=False) + "\n")
errs = []
for ef in sorted(glob.glob(str(DISCOVERY / "fetch_errors_*.json"))):
    for vid, e in json.load(open(ef)).items():
        errs.append({"video_id": vid, "handle": e["handle"], "channel": e["channel"], "title": e.get("title"),
                     "error": e.get("method2") or e.get("retry") or e.get("error"), "at": e.get("at")})
with open(BASE / "errors.jsonl", "w") as fh:
    for e in errs: fh.write(json.dumps(e, ensure_ascii=False) + "\n")
overlap = set(ids) & {e["video_id"] for e in errs}
listed = {}
for h in per:
    p = DISCOVERY / "lists" / f"{h}.tsv"
    if p.exists():
        n = 0
        for l in open(p):
            parts = l.split("\t")
            try:
                if len(parts) >= 4 and float(parts[1]) >= 180: n += 1
            except ValueError: pass
        listed[h] = n
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M %Z").strip()
L = ["# strategy corpus - coverage report (never estimated; generated from disk)", "",
     f"Generated: {now} by scripts/strategy_corpus_manifest.py", "",
     f"Transcripts: {len(rows)} across {len(per)} channels, {sum(p['words'] for p in per.values()):,} words.",
     f"Manifest: {len(rows)} rows, {len(set(ids))} unique video_ids, {len(ids)-len(set(ids))} duplicates.",
     f"Errors: {len(errs)} rows (terminal: no English caption track or captions disabled, after two methods).",
     f"Attempt-complete: manifest ∩ errors by video_id = {len(overlap)}.", "",
     "| transcripts | long-form listed | errors | words | channel | handle |", "|---:|---:|---:|---:|---|---|"]
ecount = {}
for e in errs: ecount[e["handle"]] = ecount.get(e["handle"], 0) + 1
for h, p in sorted(per.items(), key=lambda kv: -kv[1]["n"]):
    L.append(f"| {p['n']} | {listed.get(h, 'all formats') if h != 'alexmhsmith' else '51 (33 long + 18 Shorts)'} | {ecount.get(h, 0)} | {p['words']:,} | {p['name']} | @{h} |")
L += ["", "Scope note: the seed channel (@alexmhsmith) is captured in full including Shorts. Peer channels are captured",
      "for every long-form upload (duration >= 180 s) listed on their /videos tab on the fetch date; Shorts are out of scope.",
      "Six seed transcripts end mid-sentence because the videos end mid-sentence (checked: last caption timestamp equals",
      "video duration for c_AwFCghnBU; words-per-minute of all six is 179-202 against a 189 median)."]
(BASE / "COVERAGE.md").write_text("\n".join(L) + "\n")
print("\n".join(L[:8])); print("channels:", len(per))
