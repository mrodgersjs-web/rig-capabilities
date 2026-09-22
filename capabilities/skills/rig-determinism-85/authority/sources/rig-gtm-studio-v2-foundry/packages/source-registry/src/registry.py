"""packages/source-registry/src/registry.py — Source Registry for GTM Studio v2.

Manages channel and video metadata with provenance tracking.
WRAPS: None (new package)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

# Registry storage (computed from REGISTRY_DIR)
REGISTRY_DIR = Path("packages/source-registry/data")


def _get_channels_file():
    return REGISTRY_DIR / "channels.json"


def _get_videos_file():
    return REGISTRY_DIR / "videos.json"


def _load_json(path: Path) -> list:
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save_json(path: Path, data: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def register_channel(channel_id: str, handle: Optional[str] = None,
                     title: Optional[str] = None, video_count: Optional[int] = None,
                     active_90d: Optional[bool] = None, corpus_value: Optional[float] = None,
                     evidence_url: Optional[str] = None) -> dict:
    """Register a channel in the source registry."""
    channels_file = _get_channels_file()
    channels = _load_json(channels_file)

    # Check for existing
    for ch in channels:
        if ch["channel_id"] == channel_id:
            # Update existing
            for key, val in [("handle", handle), ("title", title), ("video_count", video_count),
                             ("active_90d", active_90d), ("corpus_value", corpus_value),
                             ("evidence_url", evidence_url)]:
                if val is not None:
                    ch[key] = val
            _save_json(channels_file, channels)
            return ch

    # New channel
    channel = {
        "channel_id": channel_id,
        "handle": handle,
        "title": title,
        "video_count": video_count,
        "active_90d": active_90d,
        "corpus_value": corpus_value,
        "evidence_url": evidence_url,
        "status": "resolved",
    }
    channels.append(channel)
    _save_json(channels_file, channels)
    return channel


def register_video(video_id: str, channel_id: str, title: str, url: str,
                   published_date: Optional[str] = None, duration_seconds: Optional[int] = None,
                   is_short: Optional[bool] = None, status: str = "discovered") -> dict:
    """Register a video in the source registry."""
    videos_file = _get_videos_file()
    videos = _load_json(videos_file)

    # Check for existing
    for vid in videos:
        if vid["video_id"] == video_id:
            # Update existing
            for key, val in [("title", title), ("url", url), ("published_date", published_date),
                             ("duration_seconds", duration_seconds), ("is_short", is_short),
                             ("status", status)]:
                if val is not None:
                    vid[key] = val
            _save_json(videos_file, videos)
            return vid

    # New video
    video = {
        "video_id": video_id,
        "channel_id": channel_id,
        "title": title,
        "url": url,
        "published_date": published_date,
        "duration_seconds": duration_seconds,
        "is_short": is_short or False,
        "status": status,
    }
    videos.append(video)
    _save_json(videos_file, videos)
    return video


def get_channel(channel_id: str) -> Optional[dict]:
    """Get a channel by ID."""
    for ch in _load_json(_get_channels_file()):
        if ch["channel_id"] == channel_id:
            return ch
    return None


def get_video(video_id: str) -> Optional[dict]:
    """Get a video by ID."""
    for vid in _load_json(_get_videos_file()):
        if vid["video_id"] == video_id:
            return vid
    return None


def list_channels() -> list:
    """List all registered channels."""
    return _load_json(_get_channels_file())


def list_videos(channel_id: Optional[str] = None, status: Optional[str] = None) -> list:
    """List videos, optionally filtered by channel or status."""
    videos = _load_json(_get_videos_file())
    if channel_id:
        videos = [v for v in videos if v["channel_id"] == channel_id]
    if status:
        videos = [v for v in videos if v["status"] == status]
    return videos


def update_video_status(video_id: str, status: str) -> Optional[dict]:
    """Update a video's processing status."""
    videos_file = _get_videos_file()
    videos = _load_json(videos_file)
    for vid in videos:
        if vid["video_id"] == video_id:
            vid["status"] = status
            _save_json(videos_file, videos)
            return vid
    return None
