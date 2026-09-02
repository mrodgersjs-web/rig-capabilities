#!/usr/bin/env python3
"""Scrape a YouTube channel's recent uploads into a transcript corpus.

Read-only with respect to the repo and to YouTube: the only outbound traffic is
unauthenticated GETs for the channel page, the video page, and its public
auto-captions. Nothing is posted, published, or sent. Members-only videos are
NOT circumvented — they are reported as excluded. The corpus lands in a
gitignored directory because auto-captions are the creator's copyrighted words;
what gets committed downstream is derived analysis with attribution, never the
raw transcript (see docs/CORPUS-DISCOVER-AI.md).

Usage:
    scripts/scrape_channel_corpus.py --channel https://www.youtube.com/@code4AI \
        --since-days 15 --out .context/discover-ai [--from-raw] [--limit N]

  --from-raw  re-derive transcripts/descriptions from already-downloaded files
              (no network, no re-download) — use after changing clean_vtt.

Exit codes: 0 every enumerable target produced a transcript; 1 at least one
target failed or is inaccessible; 2 nothing could be enumerated.
"""

import argparse
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

VTT_SKIP = re.compile(r"^(WEBVTT|Kind:|Language:|NOTE\b|\d{2}:\d{2}:\d{2}\.\d{3} -->|\d+$)")
TAG = re.compile(r"<[^>]+>")


def sh(args, timeout=300):
    """Run an argv list (never a shell string: video ids can start with '-')."""
    r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def clean_vtt(text: str) -> str:
    """Collapse YouTube's rolling caption window into one word stream.

    Auto-captions re-emit a sliding window: "the harness is" / "the harness is
    the loop" / "harness is the loop is tight". Joining cue lines verbatim
    therefore doubles or triples the text, and any frequency-based extractor
    then reads the same phrase three times as though it were emphasised. Each
    cue is appended after its longest word-level overlap with what precedes it,
    so every word appears exactly once, in order.

    The overlap window is bounded by the incoming cue's own word count, which
    keeps the pass linear in caption length: re-splitting the accumulated
    transcript per cue would make a 40-minute video quadratic.
    """
    out = []
    for raw in text.splitlines():
        line = TAG.sub(" ", raw.strip()).strip()
        if not line or VTT_SKIP.match(line) or "-->" in line:
            continue
        words = line.split()
        if not words:
            continue
        keep = 0
        for cand in range(min(len(out), len(words)), 2, -1):
            if out[-cand:] == words[:cand]:
                keep = cand
                break
        out.extend(words[keep:])
    return re.sub(r"\s+", " ", " ".join(out)).strip()


def pick_caption(raw_dir: Path, vid: str):
    """Prefer the translated/`en` track; `en-orig` is the fallback, not the target."""
    for pat in (vid + "*.en.vtt", vid + "*.en-*.vtt", vid + "*.vtt"):
        hits = sorted(p for p in raw_dir.glob(pat) if p.stat().st_size > 200)
        if hits:
            return hits[0]
    return None


def derive(row: dict, out: Path) -> dict:
    """Build transcript + metadata for one video from its cached raw files."""
    raw_dir, rec = out / "raw", dict(row)
    vtt = pick_caption(raw_dir, row["id"])
    if vtt is None:
        rec["error"] = "no_captions"
        return rec
    body = clean_vtt(vtt.read_text(encoding="utf-8", errors="replace"))
    txt = out / "transcripts" / f"{row['id']}.txt"
    txt.parent.mkdir(parents=True, exist_ok=True)
    txt.write_text(body, encoding="utf-8")
    infos = sorted(raw_dir.glob(row["id"] + "*.info.json"))
    meta = json.loads(infos[0].read_text(encoding="utf-8")) if infos else {}
    desc = meta.get("description") or ""
    if desc:
        (out / "descriptions").mkdir(parents=True, exist_ok=True)
        (out / "descriptions" / f"{row['id']}.md").write_text(desc, encoding="utf-8")
    rec.update(
        caption_file=vtt.name, transcript=str(txt), words=len(body.split()),
        bytes=len(body.encode()),
        transcript_sha256=hashlib.sha256(body.encode()).hexdigest(),
        description_sha256=hashlib.sha256(desc.encode()).hexdigest(),
        has_description=bool(desc),
        chapters=[{"title": c.get("title"), "start": c.get("start_time")}
                  for c in (meta.get("chapters") or [])],
        uploader=meta.get("uploader") or meta.get("channel"),
        view_count=meta.get("view_count"), like_count=meta.get("like_count"),
        comment_count=meta.get("comment_count"),
        is_live=meta.get("is_live"),
        error=None if body else "empty_after_clean",
    )
    return rec


def enumerate_videos(channel: str, since_days: int, ytdlp: str, limit: int = 0):
    """Return ([{id,title,timestamp,duration,url}], channel_name)."""
    code, out, err = sh([ytdlp, "--flat-playlist", "--extractor-args",
                         "youtubetab:approximate_date", "-J", channel.rstrip("/") + "/videos"],
                        timeout=1800)
    if code != 0 or not out.strip():
        raise RuntimeError("enumeration failed: " + (err.strip().splitlines() or [""])[-1])
    doc = json.loads(out)
    cut = (datetime.datetime.now(datetime.timezone.utc)
           - datetime.timedelta(days=since_days)).timestamp()
    rows = [e for e in doc.get("entries", []) if e and (e.get("timestamp") or 0) >= cut]
    rows.sort(key=lambda e: e["timestamp"], reverse=True)
    if limit:
        rows = rows[:limit]
    return [{
        "id": e["id"], "title": e.get("title") or "",
        "timestamp": e["timestamp"],
        "published": datetime.datetime.fromtimestamp(
            e["timestamp"], datetime.timezone.utc).strftime("%Y-%m-%d"),
        "duration": e.get("duration") or 0,
        "url": "https://www.youtube.com/watch?v=" + e["id"],
    } for e in rows], doc.get("channel")


def download(row: dict, out: Path, ytdlp: str) -> str:
    """Fetch auto-captions + metadata for one video. Returns '' or a reason."""
    stem = out / "raw" / row["id"]
    code, _, err = sh([ytdlp, "--skip-download", "--write-auto-subs",
                       "--sub-langs", "en,en-.*,orig-.*", "--sub-format", "vtt",
                       "--write-info-json", "--no-write-playlist-metafiles", "--no-part",
                       "-o", f"{stem}%(ext)s", row["url"]], timeout=420)
    if pick_caption(out / "raw", row["id"]) is None:
        tail = (err.strip().splitlines() or [""])[-1]
        if "members" in err or "membership" in err:
            return "members_only"          # paywalled: never circumvented
        return "no_captions: " + tail[:140]
    return ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--channel", required=True)
    ap.add_argument("--since-days", type=int, default=15)
    ap.add_argument("--out", required=True, help="corpus dir (gitignored)")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--from-raw", action="store_true", help="re-derive, no network")
    ap.add_argument("--yt-dlp", default=shutil.which("yt-dlp") or "yt-dlp")
    args = ap.parse_args()

    out = Path(args.out)
    (out / "raw").mkdir(parents=True, exist_ok=True)
    if not args.from_raw and not (Path(args.yt_dlp).exists() or shutil.which(args.yt_dlp)):
        print(json.dumps({"verdict": "NO_YTDLP", "detail": args.yt_dlp}))
        return 2
    prior = out / "manifest.json"
    try:
        if args.from_raw:
            # Re-derive from cached raw files: the target list comes from the last
            # live enumeration so --from-raw never reaches the network at all.
            if not prior.exists():
                raise RuntimeError("--from-raw needs a prior manifest.json")
            old = json.loads(prior.read_text(encoding="utf-8"))
            rows, channel = old["videos"], old.get("channel")
        else:
            rows, channel = enumerate_videos(args.channel, args.since_days,
                                             args.yt_dlp, args.limit)
    except Exception as e:
        print(json.dumps({"verdict": "ENUMERATION_FAILED", "detail": str(e)[:200]}))
        return 2

    manifest, failed = [], []
    for row in rows:
        why = "" if args.from_raw else download(row, out, args.yt_dlp)
        rec = derive(row, out)
        if why:
            rec["error"] = why
        failed.append({"id": row["id"], "title": row["title"], "error": rec.get("error") or why})
        manifest.append({k: v for k, v in rec.items() if k not in ("description",)})
        print(f"{'OK  ' if not rec.get('error') else 'FAIL'} {row['id']} {row['published']} "
              f"{int(row['duration']/60):3d}m {rec.get('words', 0):6d}w "
              f"{'desc ' if rec.get('has_description') else 'NODESC '} {row['title'][:52]}",
              flush=True)
    doc = {
        "schema": "channel-corpus-v1", "channel": channel, "channel_url": args.channel,
        "scraped_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "since_days": args.since_days, "from_raw": args.from_raw,
        "targets": len(rows), "transcribed": sum(1 for m in manifest if m.get("words")),
        "total_words": sum(m.get("words", 0) for m in manifest),
        "total_bytes": sum(m.get("bytes", 0) for m in manifest),
        "with_description": sum(1 for m in manifest if m.get("has_description")),
        "failed": [f for f in failed if f["error"]], "videos": manifest,
    }
    (out / "manifest.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": "OK" if not doc["failed"] else "PARTIAL",
                      "channel": channel, "targets": doc["targets"],
                      "transcribed": doc["transcribed"], "total_words": doc["total_words"],
                      "with_description": doc["with_description"],
                      "failed": [f["error"].split(":")[0] for f in doc["failed"]]}))
    return 0 if not doc["failed"] else 1


if __name__ == "__main__":
    sys.exit(main())
