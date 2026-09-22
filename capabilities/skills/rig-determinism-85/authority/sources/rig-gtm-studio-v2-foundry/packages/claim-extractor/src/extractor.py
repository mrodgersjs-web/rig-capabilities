"""packages/claim-extractor/src/extractor.py — Atomic Claim Extractor.

Extracts atomic claims from normalized transcript segments with epistemic
typing and provenance tracking.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Optional

# Epistemic type keywords
OPINION_KW = ["I think", "I believe", "in my opinion", "I feel", "I'd say"]
ANECDOTE_KW = ["I had a client", "one time", "I remember", "this happened to me"]
OBSERVED_CASE_KW = ["I saw", "I observed", "we saw", "the data showed", "in practice"]
BENCHMARK_KW = ["benchmark", "average", "industry standard", "typical"]
RESEARCH_KW = ["research shows", "study found", "according to", "data indicates"]
PROCEDURE_KW = ["here's how", "step one", "first", "then", "do this", "build", "create"]


def classify_epistemic_type(text: str) -> str:
    """Classify the epistemic type of a claim."""
    text_lower = text.lower()

    for kw in RESEARCH_KW:
        if kw in text_lower:
            return "external_research"
    for kw in BENCHMARK_KW:
        if kw in text_lower:
            return "benchmark"
    for kw in OBSERVED_CASE_KW:
        if kw in text_lower:
            return "observed_case"
    for kw in ANECDOTE_KW:
        if kw in text_lower:
            return "anecdote"
    for kw in PROCEDURE_KW:
        if kw in text_lower:
            return "testable_procedure"
    for kw in OPINION_KW:
        if kw in text_lower:
            return "opinion"

    # Default: opinion
    return "opinion"


def extract_claims(segment: dict, video_id: str, channel_id: Optional[str] = None) -> list:
    """Extract atomic claims from a normalized segment.

    Returns list of claim dicts with provenance.
    """
    text = segment["text"]
    if len(text) < 20:
        return []

    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)

    claims = []
    for sentence in sentences:
        if len(sentence) < 15:
            continue

        epistemic = classify_epistemic_type(sentence)

        # Compute transcript hash
        transcript_hash = hashlib.sha256(
            json.dumps({
                "video_id": video_id,
                "start": segment["start"],
                "end": segment["end"],
                "text": sentence
            }, sort_keys=True).encode()
        ).hexdigest()

        claim = {
            "claim_id": hashlib.sha256(
                json.dumps({
                    "video_id": video_id,
                    "text": sentence,
                    "start": segment["start"]
                }, sort_keys=True).encode()
            ).hexdigest()[:16],
            "video_id": video_id,
            "channel_id": channel_id,
            "text": sentence.strip(),
            "epistemic_type": epistemic,
            "start_time": segment["start"],
            "end_time": segment["end"],
            "transcript_hash": transcript_hash,
            "confidence": 0.7 if epistemic == "opinion" else 0.85,
            "tags": [],
            "status": "extracted",
        }
        claims.append(claim)

    return claims


def deduplicate_claims(claims: list) -> list:
    """Deduplicate near-identical claims by text hash."""
    seen = set()
    unique = []
    for claim in claims:
        text_hash = hashlib.sha256(claim["text"].lower().encode()).hexdigest()
        if text_hash not in seen:
            seen.add(text_hash)
            unique.append(claim)
    return unique
