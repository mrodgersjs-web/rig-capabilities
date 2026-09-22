"""packages/transcript-normalizer/src/normalizer.py — Transcript Normalizer.

Cleans, segments, and normalizes YouTube transcripts while preserving
exact time boundaries for provenance.
"""
from __future__ import annotations

import re
from typing import Optional


def clean_text(text: str) -> str:
    """Clean transcript text: remove filler, normalize whitespace."""
    # Remove common filler words/phrases
    text = re.sub(r'\b(um|uh|like|you know|I mean|right)\b', '', text, flags=re.IGNORECASE)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def segment_transcript(transcript: dict, max_segment_seconds: int = 30) -> list:
    """Segment transcript into bounded chunks without duplicating source spans."""
    segments = transcript.get("segments", [])
    if not segments:
        return []
    if max_segment_seconds <= 0:
        raise ValueError("max_segment_seconds must be positive")

    result = []
    current_start = segments[0]["start"]
    current_end = current_start
    current_text = []

    for seg in segments:
        seg_start = seg["start"]
        seg_end = seg_start + seg.get("duration", seg.get("dur", 0))
        if current_text and seg_end - current_start > max_segment_seconds:
            result.append({
                "segment_id": len(result),
                "start": current_start,
                "end": current_end,
                "text": " ".join(current_text),
            })
            current_start = seg_start
            current_text = []

        current_text.append(seg["text"])
        current_end = seg_end

    if current_text:
        result.append({
            "segment_id": len(result),
            "start": current_start,
            "end": current_end,
            "text": " ".join(current_text),
        })

    return result


def normalize_transcript(transcript: dict) -> dict:
    """Normalize a transcript: clean text, segment, compute hash."""
    import hashlib

    raw_segments = transcript.get("segments", [])
    cleaned = []
    for seg in raw_segments:
        cleaned.append({
            **seg,
            "text": clean_text(seg["text"])
        })

    transcript["segments"] = cleaned
    transcript["normalized"] = True

    # Compute content hash
    content = json.dumps(cleaned, sort_keys=True)
    transcript["content_hash"] = hashlib.sha256(content.encode()).hexdigest()

    return transcript


import json
