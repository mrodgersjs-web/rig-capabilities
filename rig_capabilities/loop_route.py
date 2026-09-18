"""rig-loop route -- intent -> loop id via System One (Jev), fail-open.

Contract
--------
- ``route_intent(intent)`` asks Jev to pick the loop whose spec best matches a
  free-text intent, among the registered canonical loop specs.
- Every answer names its source: ``jev``, ``keyword-failopen``, or
  ``jev-abstained`` (Jev answered but below the confidence floors).
- The provider is never load-bearing: on ProviderError the verb falls open to
  a deterministic keyword score over loop ids and stage letters, and on
  abstention it falls open to the same fallback. ``route == "NONE"`` is the
  honest "no confident route" answer; it is never silently upgraded.
- Thresholds are UNCALIBRATED until labelled rows exist. They are
  env-overridable (RIG_ROUTE_TOP1_FLOOR / RIG_ROUTE_MARGIN_FLOOR) and every
  decision is appended to ``~/.rig/s1gate/routes.jsonl`` so the calibration
  corpus accumulates exactly like s1gate's DecisionLog.

Stdlib only. The API key is read through s1gate._api_key and is never
returned to a caller, never logged, never written to disk.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import loops as L
from .s1gate import ProviderError, ask

STATE_DIR = Path(os.environ.get("S1GATE_STATE_DIR", Path.home() / ".rig" / "s1gate"))
ROUTES_JSONL = STATE_DIR / "routes.jsonl"

# UNCALIBRATED floors. Do not raise them by editing code; label routes and
# re-derive (the s1gate_calibrate discipline), then pin the earned numbers.
DEFAULT_TOP1_FLOOR = 0.40
DEFAULT_MARGIN_FLOOR = 0.08
NONE_OF_THE_ABOVE = "none-of-the-above"


def _floor(env_name: str, default: float) -> float:
    raw = os.environ.get(env_name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def loop_options(all_roots: bool = False) -> List[Dict[str, str]]:
    """Registered loop specs as choice criteria. Canonical roots by default."""
    roots = {k: v for k, v in L.SKILL_ROOTS.items()} if all_roots else None
    out = []
    for s in L.list_specs(roots):
        if "error" in s:
            continue
        stages = " ".join(s.get("stages", []))
        out.append({"id": s["id"], "desc": f"stages: {stages}" if stages else s["id"]})
    return out


def _tokens(text: str) -> List[str]:
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if len(t) > 2]


def keyword_fallback(intent: str, options: List[Dict[str, str]]) -> Tuple[Optional[str], float]:
    """Deterministic score: intent-token overlap with loop id + stage letters.

    Returns (loop_id_or_None, score). Stage letters are single characters and
    _tokens drops them, so this mostly matches on loop-id words -- which is
    exactly the shallow signal a fallback is allowed to have.
    """
    want = _tokens(intent)
    if not want:
        return None, 0.0
    best, best_score = None, 0.0
    for opt in options:
        have = _tokens(opt["id"] + " " + opt["desc"])
        if not have:
            continue
        score = sum(1 for t in want if t in have) / len(want)
        if score > best_score:
            best, best_score = opt["id"], score
    return best, round(best_score, 3)


def _margin(probabilities: Dict[str, float]) -> Tuple[str, float, float]:
    ranked = sorted(probabilities.items(), key=lambda kv: kv[1], reverse=True)
    top_id, top_p = ranked[0]
    second_p = ranked[1][1] if len(ranked) > 1 else 0.0
    return top_id, float(top_p), round(float(top_p - second_p), 4)


def route_intent(
    intent: str,
    *,
    all_roots: bool = False,
    log: bool = True,
) -> Dict[str, Any]:
    """Route one intent. Never raises on provider failure -- fail-open."""
    if not intent or not intent.strip():
        raise ValueError("intent must be a non-empty string")
    options = loop_options(all_roots)
    if not options:
        raise ValueError("no loop specs registered")
    if len(options) > 254:  # 254 + none-of-the-above <= 255 (Jev choice cap)
        raise ValueError("too many loops for one choice question: %d" % len(options))

    criteria = {o["id"]: o["desc"] for o in options}
    criteria[NONE_OF_THE_ABOVE] = "No registered loop matches; handle deterministically"
    questions = {
        "loop": {
            "type": "choice",
            "instructions": "Which registered loop best matches this work intent?",
            "criteria": criteria,
        }
    }

    started = time.time()
    meta: Dict[str, Any] = {
        "ts": time.time(),
        "intent": intent[:500],
        "intent_sha256": hashlib.sha256(intent.encode("utf-8")).hexdigest(),
        "top1_floor": _floor("RIG_ROUTE_TOP1_FLOOR", DEFAULT_TOP1_FLOOR),
        "margin_floor": _floor("RIG_ROUTE_MARGIN_FLOOR", DEFAULT_MARGIN_FLOOR),
        "route": "NONE",
        "source": "unrouted",
        "probabilities": None,
        "top1": None,
        "margin": None,
        "keyword_fallback_route": None,
        "keyword_fallback_score": None,
        "model": None,
        "latency_ms": None,
        "error": None,
    }

    try:
        body = ask(intent.strip(), questions)
        ans = body.get("answers", {}).get("loop", {})
        probs = ans.get("probabilities") or {}
        top_id, top_p, margin = _margin(probs)
        meta["model"] = body.get("model")
        meta["latency_ms"] = int((time.time() - started) * 1000)
        meta["probabilities"] = {k: round(float(v), 4) for k, v in probs.items()}
        meta["top1"] = round(top_p, 4)
        meta["margin"] = margin

        if top_id == NONE_OF_THE_ABOVE:
            meta["source"] = "jev-abstained"
        elif top_p < meta["top1_floor"] or margin < meta["margin_floor"]:
            meta["source"] = "jev-abstained"
        else:
            meta["route"] = top_id
            meta["source"] = "jev"
    except ProviderError as exc:
        meta["source"] = "keyword-failopen"
        meta["error"] = str(exc)[:300]
        meta["latency_ms"] = int((time.time() - started) * 1000)

    if meta["route"] == "NONE":
        kw_id, kw_score = keyword_fallback(intent, options)
        meta["keyword_fallback_route"] = kw_id
        meta["keyword_fallback_score"] = kw_score
        # Fail-open only promotes the keyword answer when it carries real
        # signal; a 0.0 score stays NONE.
        if kw_id and kw_score >= 0.34:
            meta["route"] = kw_id

    if log:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with ROUTES_JSONL.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(meta, sort_keys=True) + "\n")
    return meta


def format_brief(meta: Dict[str, Any]) -> str:
    """One human line. route=NONE is always printed as NONE."""
    src = meta.get("source", "?")
    route = meta.get("route", "NONE")
    parts = [f"route={route}", f"source={src}"]
    if meta.get("top1") is not None:
        parts.append("top1=%.2f margin=%.2f" % (meta["top1"], meta["margin"]))
    if meta.get("keyword_fallback_score") is not None and route != "NONE":
        parts.append("kw=%.2f" % meta["keyword_fallback_score"])
    if meta.get("latency_ms") is not None:
        parts.append("%dms" % meta["latency_ms"])
    return "  ".join(parts)
