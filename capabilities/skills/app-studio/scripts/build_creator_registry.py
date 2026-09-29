#!/usr/bin/env python3
"""Write committed, metadata-only registries for the App Studio creator corpus.

For every channel folder under .context/app-creators/<slug>/ (gitignored raw captions and
transcripts from scripts/scrape_channel_corpus.py), write
data/corpora/how-to/build-craft/<slug>-registry.jsonl with the same fields as
tubeguruji-registry.jsonl. Transcript text is never copied: rows carry the local path,
sha256 and word count, or a note saying why there is no transcript yet. Also writes
data/corpora/how-to/build-craft/APP-CREATORS.md, the coverage table.

Re-run after the resume scrape adds transcripts; rows are rebuilt from manifests, so the
output is deterministic for a given corpus state.
Usage: build_creator_registry.py [--corpus .context/app-creators] [--out data/corpora/how-to/build-craft]
"""
import argparse, json, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(REPO / ".context/app-creators"))
    ap.add_argument("--out", default=str(REPO / "data/corpora/how-to/build-craft"))
    a = ap.parse_args()
    corpus, out = Path(a.corpus), Path(a.out)
    status = {}
    sp = corpus / "status.json"
    if sp.exists():
        status = json.loads(sp.read_text()).get("channels", {})
    table = []
    for man in sorted(corpus.glob("*/manifest.json")):
        slug = man.parent.name
        doc = json.loads(man.read_text(encoding="utf-8"))
        rows = []
        for v in doc.get("videos", []):
            tpath = man.parent / "transcripts" / f"{v['id']}.txt"
            has = bool(v.get("words")) and tpath.exists()
            notes = [] if has else [f"not_transcribed: {str(v.get('error') or 'pending resume scrape')[:80]}"]
            rows.append({
                "video_id": v["id"], "title": v.get("title"), "url": v.get("url"),
                "duration_seconds": v.get("duration"), "views": v.get("view_count"),
                "published": v.get("published"),
                "transcript": (str(tpath.relative_to(REPO)) if tpath.is_relative_to(REPO) else str(tpath)) if has else None,
                "transcript_sha256": v.get("transcript_sha256") if has else None,
                "words": v.get("words") if has else 0, "thumbnail": None, "notes": notes,
            })
        (out / f"{slug}-registry.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        done = sum(1 for r in rows if r["words"])
        table.append((slug, doc.get("channel") or slug, doc.get("channel_url", ""), len(rows), done,
                      sum(r["words"] for r in rows), status.get(slug, {}).get("missing", len(rows) - done)))
    lines = ["# App Studio creator corpus (10 channels)", "",
             f"Generated {time.strftime('%Y-%m-%d %H:%M')} by capabilities/skills/app-studio/scripts/build_creator_registry.py.",
             "Raw captions and transcripts are local and gitignored under `.context/app-creators/` (creators' copyrighted words);",
             "these registries carry ids, titles, sha256 and word counts only. Scope: each channel's /videos tab;",
             "Shorts and live streams are not enumerated.", "",
             "| channel | url | targets | transcribed | words | still missing |", "|---|---|---|---|---|---|"]
    for slug, name, url, n, d, w, miss in table:
        lines.append(f"| {name} (`{slug}`) | {url} | {n} | {d} | {w:,} | {miss} |")
    tot = [sum(t[i] for t in table) for i in (3, 4, 5)]
    lines += [f"| **total** | | {tot[0]} | {tot[1]} | {tot[2]:,} | |", "",
              "Why coverage is partial: YouTube answered HTTP 429 and a bot check after the first parallel pass",
              "(2026-09-28 ~09:10 MDT). `.context/app-creators/resume_scrape.py` keeps fetching one video at a time",
              "when the block clears (status in `.context/app-creators/status.json`; stop it with a PAUSE file).", ""]
    (out / "APP-CREATORS.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"channels": len(table), "targets": tot[0], "transcribed": tot[1], "words": tot[2]}))
    return 0 if table else 2


if __name__ == "__main__":
    raise SystemExit(main())
