"""Voice fingerprint v2 — the deterministic core of v5.

Merged from three installed skills (rig-voice-engineering's 7-axis scorecard,
content-voice-fingerprint-extractor's quantification procedure, voice-builder's
interview schema). Axes 1-4 are fully deterministic; axis 5 is a deterministic
heuristic with an agent-judgement escape; axes 6-7 are explicitly AGENT calls.
This module never says PASS on the subjective axes — it refuses.
"""

from __future__ import annotations

import re

FINGERPRINT = {
    "version": 2,
    "hard_banned": [
        "unlock", "empower", "seamless", "game-changer", "game changer",
        "disruptive", "determination", "get started", "learn more",
        "thought leader", "AI strategist", "delve", "unlocking",
        "in today's fast-paced", "revolutionize", "harness the power",
    ],
    # word -> (min, target_lo, target_hi, max) per 1000 words
    "signature_vocab": {
        "median": (0, 3, 5, 12),
        "deviation": (0, 2, 4, 8),
        "production": (0, 2, 3, 6),
        "operator": (0, 3, 5, 10),
    },
    # sentence-length distribution bands (lo%, hi%)
    "sentence_bands": {
        "short_1_7": (15, 25),
        "medium_8_18": (40, 50),
        "long_19_28": (25, 35),
        "architectural_29_plus": (5, 10),
    },
    "max_paragraph_sentences": 4,
    "manifesto_beats": (
        "median is the enemy", "creativity is the gap",
        "deviation is the answer", "production is the proof",
    ),
    "wounds_allowed": ("W3", "W4", "W5", "W6", "W8"),  # Mike's real wounds only
    "wounds_forbidden": ("W1", "W2", "W7"),            # manufactured pain = red
}

_SENT = re.compile(r"[^.!?]+[.!?]*")
_WORD = re.compile(r"[A-Za-z][A-Za-z'-]+")
_BANNED_RE = {w: re.compile(r"\b" + re.escape(w).replace(r"\ ", r"[\s-]+") + r"\b", re.I)
              for w in FINGERPRINT["hard_banned"]}
# generic audience labels do not count as "specific nouns" in the hook
_GENERIC_NOUNS = {"people", "person", "business", "founder", "operator", "company",
                  "team", "leader", "writer", "developer", "everyone", "someone"}


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT.findall(text) if len(s.split()) > 0]


def score_voice(text: str) -> dict:
    """Deterministic voice scorecard. Verdict: PASS_PENDING_AGENT_AXES | REVISE | BLOCK."""
    words = _WORD.findall(text)
    n = max(len(words), 1)
    card: dict = {"word_count": len(words), "flags": []}

    # Axis 1 — banned words (binary, hard)
    found = sorted({w for w, rx in _BANNED_RE.items() if rx.search(text)})
    card["axis_1_banned"] = {"score": "PASS" if not found else "FAIL", "found": found}
    if found:
        card["flags"].append(f"banned words present: {', '.join(found)}")

    # Axis 2 — signature vocab density (WARN only; zero is legal off-topic)
    per1k = {}
    a2 = "PASS"
    for w, (_min, _lo, _hi, mx) in FINGERPRINT["signature_vocab"].items():
        c = len(re.findall(r"\b" + w + r"\b", text, re.I)) * 1000 // n
        per1k[w] = c
        if c > mx:
            a2 = "WARN"
            card["flags"].append(f"signature over-stuffed: {w}={c}/1k (max {mx})")
    card["axis_2_signature"] = {"score": a2, "per_1000_words": per1k}

    # Axis 3 — sentence-length distribution (WARN on monotony)
    lens = [len(s.split()) for s in _sentences(text)]
    buckets = {"short_1_7": 0, "medium_8_18": 0, "long_19_28": 0, "architectural_29_plus": 0}
    for L in lens:
        if L <= 7:
            buckets["short_1_7"] += 1
        elif L <= 18:
            buckets["medium_8_18"] += 1
        elif L <= 28:
            buckets["long_19_28"] += 1
        else:
            buckets["architectural_29_plus"] += 1
    total_s = max(len(lens), 1)
    pct = {k: 100 * v // total_s for k, v in buckets.items()}
    a3 = "PASS"
    if len(lens) >= 8:  # distribution is only meaningful with enough sentences
        for band, (lo, hi) in FINGERPRINT["sentence_bands"].items():
            if pct[band] < lo * 0.5 or pct[band] > hi * 1.5:
                a3 = "WARN"
                card["flags"].append(f"sentence-length clustering at {band} ({pct[band]}% vs {lo}-{hi}%)")
    card["axis_3_distribution"] = {"score": a3, "pct": pct}

    # Axis 4 — paragraph length (hard: >4 sentences = FAIL)
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    worst = max((len(_sentences(p)) for p in paras), default=0)
    a4 = "FAIL" if worst > FINGERPRINT["max_paragraph_sentences"] else "PASS"
    if a4 == "FAIL":
        card["flags"].append(f"paragraph of {worst} sentences (max 4)")
    card["axis_4_paragraphs"] = {"score": a4, "max_sentences": worst}

    # Axis 5 — hook heuristic: specific signal in first 8 words, no bait
    first_words = words[:8]
    first = " ".join(first_words)
    hook_line = text.strip().splitlines()[0] if text.strip() else ""
    specific = bool(re.search(r"\d|\"|\u201c", first)) or bool(
        re.search(r"\b[A-Z][a-z]{2,}\b", " ".join(hook_line.split()[:8])[1:]))
    specific = specific and not all(w.lower() in _GENERIC_NOUNS
                                    for w in first_words if _WORD.fullmatch(w))
    earns = not re.search(r"(?i)most people|everyone knows|secret no one|you won'?t believe",
                          text[:200])
    card["axis_5_hook"] = {"score": "PASS" if (specific and earns) else "REVISE",
                           "first_8_words": first,
                           "note": "heuristic only; agent must confirm audience-disqualifier + operator voice"}

    # Axis 6/7 — manifesto fit + cadence are agent judgement, refused here
    card["axis_6_manifesto"] = {"score": "AGENT", "beats": FINGERPRINT["manifesto_beats"]}
    card["axis_7_cadence"] = {"score": "AGENT"}

    hard_fail = a4 == "FAIL" or bool(found)
    if hard_fail:
        verdict = "BLOCK"
    elif card["axis_5_hook"]["score"] == "REVISE" or a2 == "WARN" or a3 == "WARN":
        verdict = "REVISE"
    else:
        verdict = "PASS_PENDING_AGENT_AXES"
    card["verdict"] = verdict
    return card


def drift(text: str, baseline: dict | None = None) -> dict:
    """Voice-drift delta (v5.10): per-axis scorecard diff against a baseline card."""
    now = score_voice(text)
    if not baseline:
        return {"baseline": None, "delta": None, "scorecard": now}
    delta = []
    for ax in ("axis_1_banned", "axis_2_signature", "axis_3_distribution", "axis_4_paragraphs"):
        b, t = baseline.get(ax, {}).get("score"), now.get(ax, {}).get("score")
        rank = {"PASS": 0, "WARN": 1, "REVISE": 1, "FAIL": 2}
        if rank.get(t, 0) > rank.get(b, 0):
            delta.append(f"{ax}: {b} -> {t}")
    return {"baseline": baseline.get("verdict"), "delta": delta, "scorecard": now}
