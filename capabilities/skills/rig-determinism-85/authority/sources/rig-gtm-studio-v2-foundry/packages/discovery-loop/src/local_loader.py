"""packages/discovery-loop/src/local_loader.py — Local Transcript Loader.

Loads transcripts from local files instead of fetching from YouTube.
Used for offline discovery loop runs and testing.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def load_local_transcripts(transcript_dir: Path, video_ids: list) -> dict:
    """Load transcripts for specified video IDs from local files.

    Returns dict mapping video_id -> transcript dict.
    """
    transcripts = {}
    for video_id in video_ids:
        path = transcript_dir / f"{video_id}.json"
        if path.exists():
            transcripts[video_id] = json.loads(path.read_text())
    return transcripts


def get_local_transcript(transcript_dir: Path, video_id: str) -> Optional[dict]:
    """Load a single transcript from local file."""
    path = transcript_dir / f"{video_id}.json"
    if path.exists():
        return json.loads(path.read_text())
    return None
