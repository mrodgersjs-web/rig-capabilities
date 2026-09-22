"""packages/youtube-adapter/src/adapter.py — YouTube Adapter for GTM Studio v2.

WRAPS: src/services/youtube_ingest.py (existing repo ingestion layers)
Provides a clean interface for channel enumeration, video metadata, and transcript fetching.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Optional

from youtube_transcript_api import YouTubeTranscriptApi


def resolve_channel(handle: str) -> Optional[dict]:
    """Resolve a YouTube @handle to channel ID and title.

    Uses page fetch + HTML parsing (no API key required).
    """
    import urllib.request

    url = f"https://www.youtube.com/@{handle}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    try:
        html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")
    except Exception as e:
        return None

    ids = set(re.findall(r'"(?:channelId|externalId)":"(UC[\w-]{22})"', html))
    if not ids:
        return None

    channel_id = ids.pop()
    title_match = re.search(r"<title>(.*?)</title>", html)
    title = title_match.group(1).replace(" - YouTube", "") if title_match else None

    return {"channel_id": channel_id, "handle": handle, "title": title}


def enumerate_uploads(channel_id: str, max_videos: int = 1000) -> list:
    """Enumerate a channel's uploads via yt-dlp flat playlist.

    Returns list of {video_id, title, duration_seconds}.
    """
    import subprocess

    uploads_playlist = "UU" + channel_id[2:]  # UC -> UU
    url = f"https://www.youtube.com/playlist?list={uploads_playlist}"

    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--playlist-end", str(max_videos),
             "--print", "%(id)s|%(duration)s|%(title)s", url],
            capture_output=True, text=True, timeout=300
        )
    except Exception as e:
        return []

    videos = []
    for line in result.stdout.splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3 and parts[0]:
            duration = int(parts[1]) if parts[1].isdigit() else None
            videos.append({
                "video_id": parts[0],
                "title": parts[2],
                "duration_seconds": duration,
            })
    return videos


def fetch_transcript(video_id: str) -> Optional[dict]:
    """Fetch transcript for a video via youtube_transcript_api.

    Returns {video_id, segments: [{start, duration, text}], language, is_generated}.
    """
    api = YouTubeTranscriptApi()
    try:
        tracks = list(api.list(video_id))
        if not tracks:
            return None

        # Prefer manual English, then any English, then first available
        tr = None
        for t in tracks:
            if t.language_code.startswith("en") and not t.is_generated:
                tr = t
                break
        if tr is None:
            for t in tracks:
                if t.language_code.startswith("en"):
                    tr = t
                    break
        if tr is None:
            tr = tracks[0]

        fetched = tr.fetch()
        segments = [
            {
                "start": round(float(s.start), 2),
                "duration": round(float(getattr(s, "duration", 0.0) or 0.0), 2),
                "text": s.text,
            }
            for s in fetched
        ]

        return {
            "video_id": video_id,
            "language": tr.language_code,
            "is_generated": bool(tr.is_generated),
            "segment_count": len(segments),
            "segments": segments,
        }
    except Exception as e:
        return None


def store_transcript(video_id: str, transcript: dict, output_dir: Path) -> Path:
    """Store a transcript to the restricted evidence layer."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{video_id}.json"
    path.write_text(json.dumps(transcript, ensure_ascii=False))
    return path
