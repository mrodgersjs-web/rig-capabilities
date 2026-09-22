"""v20 C7 — compression & plain-language repair (deterministic pass, stdlib).

Measures: throat-clearing openers, hedges/nominalizations, BLUF latency
(words before the first sentence carrying value/ask, at 160 wpm), reading
load, and a suggested cut %. Cuts stay advisory; the gate is floors in energy.py.
ponytail: heuristic lexicons, upgrade path = per-archetype distributions from the
outcome ledger (outcomes.py) once n>100 per archetype.
"""
from __future__ import annotations
import re

THROAT_CLEARING = (
    "hope you're doing well", "hope you are doing well", "hope this email finds you well",
    "i hope this finds you well", "just circling back", "just checking in",
    "just following up", "i wanted to reach out", "reaching out because",
    "as you know", "in today's fast-paced", "in the world of", "at the end of the day",
    "per my last email", "i know you're busy", "quick question", "sorry to bother",
    "i am writing to", "this is a follow-up", "following up on my previous",
)
HEDGES = ("very", "really", "just", "actually", "basically", "somewhat",
          "quite", "rather", "sort of", "kind of", "a bit", "slightly")
NOMINALIZATIONS = re.compile(
    r"\b\w+(?:ization|isation|ization|ation|ition|ment|ance|ence|ness)\b", re.I)
ASK_MARKERS = re.compile(
    r"\b(please|can you|could you|would you|reply|approve|book|schedule|send|join|"
    r"confirm|decide|review|sign|say yes|say no|what do you think|worth)\b", re.I)
# A value-carrier sentence: names a concrete number ($, %, count) — BLUF may be
# value, not only ask. Ask-only latency mis-scores lead-with-the-pain emails.
VALUE_MARKERS = re.compile(r"[+-]?\d[\d,.]*\s*(%|x\b|k\b)|\$\s?\d|\b\d+\s?(minutes|days|weeks|hours)\b")
WPS = 160.0 / 60.0  # words per second, read-scan pace


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def analyze(text: str, first_value_hint: int | None = None) -> dict:
    words = text.split()
    n = max(len(words), 1)
    low = text.lower()
    openers = [p for p in THROAT_CLEARING if p in low]
    hedges = [w for w in HEDGES if re.search(rf"\b{w}\b", low)]
    nominal = NOMINALIZATIONS.findall(text)
    sents = _sentences(text)
    long_sents = [s for s in sents if len(s.split()) > 25]

    # BLUF latency: first sentence carrying the ask/value. first_value_hint is
    # the harness-supplied index (from the clarity critic); fall back to ASK_MARKERS.
    idx = first_value_hint
    if idx is None:
        idx = next((i for i, s in enumerate(sents) if ASK_MARKERS.search(s) or VALUE_MARKERS.search(s)), len(sents) - 1)
    words_before = sum(len(s.split()) for s in sents[:idx])
    bluf_secs = round(words_before / WPS, 1)

    avg_len = round(n / max(len(sents), 1), 1)
    cut_pct = min(33, round((len(openers) * 8 + len(hedges) * 2 + len(nominal) * 2
                             + len(long_sents) * 6) / n * 100))
    return {
        "words": n, "sentences": len(sents),
        "throat_clearing": openers, "hedges": len(hedges),
        "nominalizations": len(nominal), "long_sentences": len(long_sents),
        "bluf_latency_secs": bluf_secs, "avg_sentence_words": avg_len,
        "suggested_cut_pct": cut_pct,
        "clean": not openers,
    }


def demo() -> bool:
    weak = analyze("Hope you're doing well. I wanted to reach out because I am basically "
                   "a very results-driven person. Our utilization optimization delivered "
                   "a 34% reduction. Please approve by Friday.")
    assert weak["throat_clearing"] == ["hope you're doing well", "i wanted to reach out"]
    assert weak["bluf_latency_secs"] > 5 and weak["suggested_cut_pct"] > 0
    tight = analyze("Your checkout drops 12% of carts at address validation. "
                    "We fixed exactly that at a similar store: 3 days, no replatform. "
                    "Worth 15 minutes this week?")
    assert tight["clean"] and tight["bluf_latency_secs"] <= 4
    return True


if __name__ == "__main__":
    print("compress demo OK" if demo() else "FAIL")
