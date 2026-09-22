"""packages/lesson-compiler/src/compiler.py — Lesson Compiler.

Groups related claims into structured, source-addressable lessons.
"""
from __future__ import annotations

import hashlib
import json
from typing import Optional


def group_claims_by_theme(claims: list) -> dict:
    """Group claims by thematic similarity (heuristic: keyword overlap)."""
    themes = {}
    for claim in claims:
        # Simple theme detection based on keywords
        text = claim["text"].lower()
        theme = "general"
        if "offer" in text:
            theme = "offer_architecture"
        elif "pricing" in text or "price" in text:
            theme = "pricing"
        elif "positioning" in text:
            theme = "positioning"
        elif "sales" in text or "sell" in text:
            theme = "sales_process"
        elif "content" in text or "marketing" in text:
            theme = "content_marketing"

        if theme not in themes:
            themes[theme] = []
        themes[theme].append(claim)
    return themes


def compile_lesson(theme: str, claims: list) -> dict:
    """Compile a lesson from a group of related claims."""
    # Derive lesson name from theme
    theme_names = {
        "offer_architecture": "Offer Architecture",
        "pricing": "Pricing Strategy",
        "positioning": "Positioning and Differentiation",
        "sales_process": "Sales Process Design",
        "content_marketing": "Content Marketing Strategy",
        "general": "General GTM Insight",
    }
    name = theme_names.get(theme, "General GTM Insight")

    # Extract problem statement (from first claim)
    problem = claims[0]["text"][:100] + "..." if len(claims[0]["text"]) > 100 else claims[0]["text"]

    # Extract principle (heuristic: look for "should", "must", "always", "never")
    principle = ""
    for claim in claims:
        if any(word in claim["text"].lower() for word in ["should", "must", "always", "never", "the key is"]):
            principle = claim["text"]
            break
    if not principle:
        principle = claims[0]["text"]

    # Build evidence list
    evidence = []
    for claim in claims[:5]:  # Limit to 5 evidence points
        evidence.append({
            "video_id": claim["video_id"],
            "channel_id": claim["channel_id"],
            "start_time": claim["start_time"],
            "end_time": claim["end_time"],
            "transcript_hash": claim["transcript_hash"],
            "claim_ids": [claim["claim_id"]],
        })

    # Compute lesson ID
    lesson_id = hashlib.sha256(
        json.dumps({"theme": theme, "claims": [c["claim_id"] for c in claims]}, sort_keys=True).encode()
    ).hexdigest()[:16]

    # Build lesson payload (without content_hash)
    lesson_payload = {
        "lesson_id": lesson_id,
        "name": name,
        "problem": problem,
        "principle": principle,
        "conditions": [],
        "procedure": [],
        "counterexamples": [],
        "evidence": evidence,
        "source_refs": evidence,  # Schema requires evidence objects
        "compiler_version": "1.0.0",
        "confidence": 0.7,
        "status": "draft",
        "created_at": "2026-09-15T00:00:00Z",
    }

    # Compute content hash on the payload
    lesson_payload["content_hash"] = hashlib.sha256(
        json.dumps(lesson_payload, sort_keys=True).encode()
    ).hexdigest()

    return lesson_payload

def compile_lessons(claims: list) -> list:
    """Compile all lessons from a set of claims."""
    themes = group_claims_by_theme(claims)
    lessons = []
    for theme, theme_claims in themes.items():
        if len(theme_claims) >= 2:  # Need at least 2 claims for a lesson
            lesson = compile_lesson(theme, theme_claims)
            lessons.append(lesson)
    return lessons
