#!/usr/bin/env python3
# PROVENANCE: Communications OS v2 corpus scraper, 2026-09-06.
# Transcript cleaning vendored from ~/.hermes/skills/rig-dept-substrate-intake (scripts/clean_auto_subs.py).
# Substrate sidecar fields follow ~/.hermes/skills/rig-substrate-format-builder v1 schema (tier_A_signal formula).
"""Scrape writing-craft transcripts into data/corpora/writing-craft/.

Input:  data/corpora/writing-craft/TARGETS.md  (## surface sections, `- Name — why URL` bullets)
Output: <surface>/<channel-slug>/<video_id>.txt, manifest.jsonl, errors.jsonl, substrate.json
Rules:  metadata+text only, no downloads; idempotent on manifest video_ids; failures logged, never abort.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import os
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "corpora" / os.environ.get("COMMS_CORPUS", "writing-craft")
TARGETS = DATA / "TARGETS.md"
MANIFEST = DATA / "manifest.jsonl"
ERRORS = DATA / "errors.jsonl"
YTDLP = "yt-dlp"
# Chrome login cookies move requests into the authenticated quota bucket; the
# anonymous egress IP is bot-walled ("Sign in to confirm you're not a bot").
COOKIE_ARGS = ["--cookies-from-browser", "chrome"] if os.environ.get("COMMS_COOKIES") else []
# Public channels can fail yt-dlp's authcheck when Chrome cookies belong to a
# different YouTube account; yt-dlp explicitly recommends skip=authcheck then.
TAB_ARGS = ["--extractor-args", "youtubetab:skip=authcheck"] if COOKIE_ARGS else []
EJS_ARGS = ["--remote-components", "ejs:github"] if COOKIE_ARGS else []
MAX_PER_SOURCE = int(os.environ.get("COMMS_MAX_PER_SOURCE", "25"))
SLEEP = float(os.environ.get("COMMS_SLEEP", "1.0"))

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clean_auto_subs import (collapse_inline_repeats, collapse_macro_repeats,
                             cut_trailing_dup, parse_vtt, sanitize_punct)

BUN = Path.home() / ".bun/bin/bun"
GBRAIN_CLI = Path.home() / "gbrain/src/cli.ts"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:60]


def parse_targets() -> list[dict]:
    out = []
    surface = None
    for line in TARGETS.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            surface = line[3:].strip()
            if surface.lower().startswith("scraping"):
                surface = None
            continue
        m = re.match(r"^-\s+(.+?)\s*(?:—|-)\s*(.*)$", line)
        if not (m and surface):
            continue
        name, rest = m.group(1).strip(), m.group(2)
        um = re.search(r"https?://\S+", rest)
        if not um:
            continue
        url = um.group(0)
        host = urllib.parse.urlparse(url).netloc
        if "youtube.com" not in host and "youtu.be" not in host:
            continue  # non-YouTube lanes documented, not scraped this wave
        out.append({"surface": surface, "name": name, "url": url})
    return out


def yt_ids(url: str) -> list[str]:
    """Video ids for a channel/playlist/watch URL (newest-first, capped)."""
    q = urllib.parse.urlparse(url)
    if q.netloc == "youtu.be":
        return [q.path.strip("/")[:11]]
    if "watch" in q.path:
        return [urllib.parse.parse_qs(q.query).get("v", [""])[0][:11]]
    target = url if "playlist?list=" in url else url.rstrip("/") + "/videos"
    r = subprocess.run([YTDLP, "--flat-playlist", "--print", "id", "--playlist-end",
                        str(MAX_PER_SOURCE), "--no-warnings", *COOKIE_ARGS, *TAB_ARGS, *EJS_ARGS, target],
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip()[:300])
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()][:MAX_PER_SOURCE]


_backoff_used = False


def _hit429(text: str) -> bool:
    global _backoff_used
    if "429" in text or "Too Many" in text or "rate limit" in text.lower():
        if not _backoff_used:
            _backoff_used = True
            print("  429 — backing off 60s once", flush=True)
            time.sleep(60)
            return True  # caller may retry once
        return False
    return True if False else False


def via_yta(vid: str) -> str:
    from youtube_transcript_api import YouTubeTranscriptApi
    fetched = YouTubeTranscriptApi().fetch(vid)
    raw = fetched.to_raw_data()
    return collapse_inline_repeats(" ".join(seg["text"] for seg in raw))


def via_ytdlp(vid: str) -> str:
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "subs"
        r = subprocess.run([YTDLP, "--write-auto-sub", "--sub-lang", "en",
                            "--skip-download", "--sub-format", "vtt", "--no-warnings",
                            *COOKIE_ARGS, *EJS_ARGS,
                            "-o", str(out), f"https://youtu.be/{vid}"],
                           capture_output=True, text=True, timeout=180)
        vtt = next(Path(td).glob("*.vtt"), None)
        if vtt is None:
            raise RuntimeError((r.stderr or "no vtt produced").strip()[:300])
        text = " ".join(" ".join(words) for _, words in parse_vtt(vtt.read_text(encoding="utf-8", errors="replace")))
    return sanitize_punct(cut_trailing_dup(collapse_inline_repeats(collapse_macro_repeats(text))))


def fetch_transcript(vid: str) -> str:
    for attempt in range(2):
        try:
            return via_yta(vid)
        except ImportError:
            break
        except Exception as e:  # noqa: BLE001 — fall through to yt-dlp lane
            if _hit429(str(e)) and attempt == 0:
                continue
            break
    for attempt in range(2):
        text = None
        try:
            text = via_ytdlp(vid)
        except Exception as e:  # noqa: BLE001
            if attempt == 0 and _hit429(str(e)):
                continue
            raise
        if text and len(text.split()) >= 20:
            return text
        raise RuntimeError("transcript too short/empty")
    raise RuntimeError("unreachable")


def load_done() -> set[str]:
    done = set()
    if MANIFEST.exists():
        for line in MANIFEST.read_text(encoding="utf-8").splitlines():
            try:
                done.add(json.loads(line)["video_id"])
            except Exception:
                continue
    return done


def append(path: Path, obj: dict) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


def tier_a_signal(total_bytes: int, n_videos: int) -> int:
    # v1 formula adapted for a channel corpus (no per-file intake/digest siblings)
    size = (8 if total_bytes < 1_000 else 15 if total_bytes < 500_000 else
            25 if total_bytes < 500_000 * 20 else 35)
    return max(0, min(100, 30 + size + min(15, 5 * (1 if n_videos else 0))))


def write_sidecars() -> None:
    for manifest_row in (json.loads(l) for l in MANIFEST.read_text(encoding="utf-8").splitlines() if l.strip()):
        d = DATA / manifest_row["surface"] / slugify(manifest_row["channel"])
        if not d.is_dir():
            continue
        sp = d / "substrate.json"
        files = list(d.glob("*.txt"))
        total = sum(f.stat().st_size for f in files)
        words = sum(int(json.loads(l)["words"]) for l in MANIFEST.read_text(encoding="utf-8").splitlines()
                    if l.strip() and (r := json.loads(l))["channel"] == manifest_row["channel"]
                    and r["surface"] == manifest_row["surface"])
        sp.write_text(json.dumps({
            "schema": "rig-substrate-v1",
            "source_type": "youtube",
            "source_uri": manifest_row["url"].split("/videos")[0],
            "entity": {"kind": "channel", "name": manifest_row["channel"], "slug": d.name},
            "surface": manifest_row["surface"],
            "title": manifest_row["channel"],
            "videos": len(files),
            "words": words,
            "tier_A_signal": tier_a_signal(total, len(files)),
            "tags": ["writing-craft", manifest_row["surface"], "youtube", "transcript"],
            "applicable_to": ["rig-communications-core", "rig-communications-doctrine"],
            "agent_action": f"Mine {manifest_row['channel']} transcripts under {manifest_row['surface']} for craft patterns; score any adoption with rig_comm.",
            "consumption_hint": "Read transcripts as craft exemplars; do not quote verbatim in outbound copy.",
            "ingested_at": now_iso(),
        }, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    done = load_done()
    got = skip = err = 0
    only = [s.strip().lower() for s in os.environ.get("COMMS_ONLY", "").split(",") if s.strip()]
    targets = [t for t in parse_targets()
               if not only or any(o in slugify(t["name"]) for o in only)]
    for t in targets:
        slug = slugify(t["name"])
        try:
            ids = yt_ids(t["url"])
        except Exception as e:  # noqa: BLE001
            err += 1
            append(ERRORS, {"url": t["url"], "channel": t["name"], "surface": t["surface"],
                            "error": f"id-list: {e}", "at": now_iso()})
            print(f"[err ] {t['surface']}/{slug}: ids: {e}", flush=True)
            continue
        new = [v for v in ids if v and v not in done]
        print(f"[scan] {t['surface']}/{slug}: {len(ids)} ids, {len(new)} new", flush=True)
        outdir = DATA / t["surface"] / slug
        outdir.mkdir(parents=True, exist_ok=True)
        for vid in new:
            time.sleep(SLEEP)
            try:
                text = fetch_transcript(vid)
            except Exception as e:  # noqa: BLE001
                err += 1
                append(ERRORS, {"video_id": vid, "channel": t["name"], "surface": t["surface"],
                                "url": f"https://youtu.be/{vid}", "error": f"transcript: {e}", "at": now_iso()})
                print(f"[err ] {vid}: {e}", flush=True)
                continue
            words = len(text.split())
            sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
            (outdir / f"{vid}.txt").write_text(text + "\n", encoding="utf-8")
            append(MANIFEST, {"video_id": vid, "channel": t["name"], "surface": t["surface"],
                              "url": f"https://youtu.be/{vid}", "words": words,
                              "fetched_at": now_iso(), "sha256": sha})
            done.add(vid)
            got += 1
            if got % 20 == 0:
                print(f"[  ..] {got} fetched", flush=True)
            skip += 0
    write_sidecars()
    print(f"DONE fetched={got} skipped_existing={len(done)-got} errors={err}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
