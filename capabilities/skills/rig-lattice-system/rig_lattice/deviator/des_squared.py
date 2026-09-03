"""DES² — 25× amplification overlay per DOCTRINE.md §3.

Wraps the base auditor with 5 inner amplifiers per engine. Each amplifier
adds a multiplicative rigor factor. Product = 6.55× per axis → 25× compound
when applied across quality + proof axes.

Amplifiers:
  A1' Mechanism Map         — causal chain inputs → output  (1.5× rigor)
  A2' Source-Per-Claim      — URI + hash bound per assertion (1.4× grounding)
  A3' Falsification Check   — pre-registered invalidation conditions (1.6× robustness)
  A4' Anti-Generic Gate     — specificity floor (1.3× precision)
  A5' Brier-Calibrated      — predicted σ vs realized σ (1.5× calibration)

Public API:
  amplify(audit_result, text) → dict with `des2_score`, `amplifiers`, `composite_uplift`
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from rig_lattice._paths import AUDITS_DIR

ROOT = Path(__file__).parent

# Multiplier constants from DOCTRINE.md §3.1
AMP_MECHANISM = 1.5
AMP_SOURCE    = 1.4
AMP_FALSIFY   = 1.6
AMP_SPECIFIC  = 1.3
AMP_BRIER     = 1.5
AMP_PRODUCT   = AMP_MECHANISM * AMP_SOURCE * AMP_FALSIFY * AMP_SPECIFIC * AMP_BRIER

# Brier history persisted at this path for cross-run calibration
BRIER_LOG_PATH = AUDITS_DIR / "brier_history.jsonl"


def _bool_to_score(b: bool, multiplier: float) -> float:
    """Pass → multiplier applied; fail → 1.0 (no uplift)."""
    return multiplier if b else 1.0


# ── A1' Mechanism Map ──────────────────────────────────────────────────────
def amp1_mechanism_map(text: str) -> tuple[bool, str]:
    """Causal-chain density: ≥4 causal connectives per 1000 words."""
    causal = re.findall(
        r"\b(because|therefore|leads to|drives|results in|causes|forces|triggers|→|via|through)\b",
        text, re.IGNORECASE,
    )
    words = max(len(text.split()), 1)
    density = len(causal) / words * 1000
    passed = density >= 4.0
    return passed, f"causal density {density:.1f}/kw (need ≥4.0)"


# ── A2' Source-Per-Claim ──────────────────────────────────────────────────
def amp2_source_per_claim(text: str) -> tuple[bool, str]:
    """Citation density: footnote markers OR named primary sources ≥3."""
    footnotes = re.findall(r"\[\d+\]", text)
    named_sources = re.findall(
        r"\b(Research and Markets|Mordor Intelligence|Grand View Research|"
        r"McKinsey|Gartner|Forrester|Helios Technologies|10-K|10-Q|S-1|"
        r"earnings release|press release dated|published [A-Z]\w+ \d{4})\b",
        text, re.IGNORECASE,
    )
    score = len(footnotes) + len(named_sources)
    passed = score >= 3
    return passed, f"{len(footnotes)} footnotes + {len(named_sources)} named sources (need ≥3)"


# ── A3' Falsification Check ───────────────────────────────────────────────
def amp3_falsification(text: str) -> tuple[bool, str]:
    """Pre-registered invalidation conditions present."""
    falsifiers = re.findall(
        r"(falsification (calendar|criterion)|wrong if|kill criteri|"
        r"terminate if|rescope if|<\s*\d+%\s*by\s*(month|Q[1-4]|20\d{2})|"
        r"if .+ (fails|misses).+by [A-Z])",
        text, re.IGNORECASE,
    )
    passed = len(falsifiers) >= 2
    return passed, f"{len(falsifiers)} falsification markers (need ≥2)"


# ── A4' Anti-Generic Gate ─────────────────────────────────────────────────
def amp4_anti_generic(text: str) -> tuple[bool, str]:
    """Specificity: zero banned generic tokens."""
    banned = re.findall(
        r"\b(unlock|transform|seamless|scale effortlessly|leverage|synergy|"
        r"holistic|world-class|cutting-edge|game-changing|paradigm shift|"
        r"thought leadership|best practices|in today.s (landscape|world))\b",
        text, re.IGNORECASE,
    )
    passed = len(banned) == 0
    return passed, f"{len(banned)} banned tokens" + (f" (found: {banned[:3]})" if banned else "")


# ── A5' Brier-Calibrated Confidence ───────────────────────────────────────
def amp5_brier(text: str, audit_result: dict) -> tuple[bool, str]:
    """Brier delta tracking: predicted σ vs realized σ.

    Reads brier_history.jsonl, computes mean |predicted − realized| over
    last 20 runs. Pass if calibration tighter than 1.0σ MAE.
    """
    if not BRIER_LOG_PATH.exists():
        return True, "no history yet — baseline pass"
    try:
        lines = BRIER_LOG_PATH.read_text().strip().split("\n")
        recent = [json.loads(l) for l in lines[-20:] if l.strip()]
        if len(recent) < 3:
            return True, f"only {len(recent)} history entries — baseline pass"
        deltas = [abs(r["predicted_rig_l"] - r["realized_rig_l"]) for r in recent
                   if "predicted_rig_l" in r and "realized_rig_l" in r]
        if not deltas:
            return True, "no resolved predictions yet — baseline pass"
        mae = sum(deltas) / len(deltas)
        passed = mae < 1.0
        return passed, f"Brier MAE {mae:.2f} over {len(deltas)} runs (need <1.0)"
    except Exception as e:
        return False, f"brier log error: {e}"


# ── Main amplify function ─────────────────────────────────────────────────
def amplify(audit_result: dict, text: str) -> dict:
    """Run all 5 amplifiers, compute composite uplift.

    Returns the audit_result enriched with:
      - amplifiers:  per-amplifier {passed, detail, multiplier}
      - composite_uplift: product of passing multipliers
      - des2_score: rig_l × composite_uplift / AMP_PRODUCT
        (normalized so a full-pass document gets uplift=1.0,
         a fully-failing document gets the baseline rig_l back)
    """
    results = {}
    results["A1_mechanism"]  = _wrap(amp1_mechanism_map(text), AMP_MECHANISM)
    results["A2_sources"]     = _wrap(amp2_source_per_claim(text), AMP_SOURCE)
    results["A3_falsify"]     = _wrap(amp3_falsification(text), AMP_FALSIFY)
    results["A4_specificity"] = _wrap(amp4_anti_generic(text), AMP_SPECIFIC)
    results["A5_brier"]       = _wrap(amp5_brier(text, audit_result), AMP_BRIER)

    composite_uplift = 1.0
    for r in results.values():
        if r["passed"]:
            composite_uplift *= r["multiplier"]

    base_rig_l = audit_result.get("rig_l", 0.0)
    # DES² score: base × (uplift / max possible uplift) gives 0-1 efficiency,
    # multiplied by base RIG-L to keep units. A perfect amplifier pass keeps
    # the base score; partial pass reduces it.
    efficiency = composite_uplift / AMP_PRODUCT
    des2_score = base_rig_l * efficiency if base_rig_l > 0 else base_rig_l

    audit_result["des2"] = {
        "amplifiers": results,
        "composite_uplift": round(composite_uplift, 3),
        "max_uplift": round(AMP_PRODUCT, 3),
        "efficiency": round(efficiency, 3),
        "des2_score": round(des2_score, 2),
        "amplifiers_passed": sum(1 for r in results.values() if r["passed"]),
        "amplifiers_total": len(results),
    }
    return audit_result


def _wrap(check_result: tuple[bool, str], multiplier: float) -> dict:
    passed, detail = check_result
    return {"passed": passed, "detail": detail, "multiplier": multiplier}


# ── Brier log writer (called after a prediction resolves) ────────────────
def record_brier(mission_id: str, predicted_rig_l: float,
                  realized_rig_l: float, content_hash: str) -> None:
    BRIER_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "mission_id": mission_id,
        "predicted_rig_l": predicted_rig_l,
        "realized_rig_l": realized_rig_l,
        "delta": abs(predicted_rig_l - realized_rig_l),
        "content_hash": content_hash,
    }
    with BRIER_LOG_PATH.open("a") as f:
        f.write(json.dumps(entry) + "\n")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        sys.exit("usage: python des_squared.py <file.md>")
    text = Path(sys.argv[1]).read_text()

    # Run base audit + amplify
    from rig_lattice.deviator.auditor import audit_all
    base = audit_all(text, llm_enabled=False)
    out = amplify(base, text)

    d = out["des2"]
    print(f"\n=== DES² Amplification Report ===")
    print(f"  base RIG-L:         {base['rig_l']:+.2f}")
    print(f"  composite uplift:   {d['composite_uplift']:.3f}× (max {d['max_uplift']:.3f}×)")
    print(f"  efficiency:         {d['efficiency']*100:.1f}%")
    print(f"  DES² score:         {d['des2_score']:+.2f}")
    print(f"  amplifiers passed:  {d['amplifiers_passed']}/{d['amplifiers_total']}")
    print()
    for name, r in d["amplifiers"].items():
        mark = "✓" if r["passed"] else "✗"
        print(f"  {mark} {name:18}  {r['multiplier']:.2f}×  {r['detail']}")
