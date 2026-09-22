"""The deterministic gate stack (v7) — one JSON envelope, stable exit codes.

0 = green (can_ship) · 2 = red (named blocks) · 3 = privacy lock (private lane,
human-only). Every gate is red-capable: tests/planted-failures prove each one
fires (adversarial-verification-loop). This stack calls rig_comm.evaluate for
the scoring core and adds the comms-OS gates: voice v2, wound authenticity,
wound resonance, fabrication, rubric, sigma floor, Gate-D flag.
"""

import json
import re
import sys

from . import surfaces, voice

try:  # package-relative first (repo + installed skill dir)
    from rig_comm import evaluate as _evaluate
except ImportError:  # pragma: no cover — only when rig_comm not on path
    _evaluate = None

_WOUND_RE = re.compile(r"\bW[1-8]\b")
_NUMBER = re.compile(r"(?<![\w.])(?!19\d\d|20\d\d)\d[\d,.]*%?(?![\w])")  # metrics, not bare years
_SOURCED = re.compile(r"(?i)https?://|\[\d+\]|\(source|per |from |according to")

# surface -> rig_comm V10 channel key
_CHANNEL = {"emails": "email", "linkedin": "linkedin", "substack": "proposal",
            "resumes": "proposal", "songs": "artifact", "film-scripts": "artifact",
            "novels": "artifact", "specs": "artifact", "code": "artifact",
            "prompts": "artifact"}


def _gate(name: str, ok: bool, detail: str) -> dict:
    return {"gate": name, "status": "PASS" if ok else "RED", "detail": detail}

def evaluate_stack(surface: surfaces.Surface, text: str) -> dict:
    checks: list[dict] = []
    meta: dict = {"sigma_target": surface.sigma_target,
                  "sigma_status": "META — composite sigma comes from rig-lattice scoring, not this stack"}

    if _evaluate is not None:
        r = _evaluate(text, channel=_CHANNEL.get(surface.id, "artifact"))
        agf = round(r.score.anti_generic_force * 100)
        checks.append(_gate("agf", agf >= surface.agf_min,
                            f"AGF {agf} >= {surface.agf_min} (V10 anti_generic_force)"))
        checks.append(_gate("rig_comm_v10", r.can_ship,
                            "; ".join(r.blocks) if r.blocks else "V10 gate engine green"))
        if surface.rubric == "eas":
            ev = round(r.score.emotional_voltage, 2)
            checks.append(_gate("eas_proxy", ev >= 0.75,
                                f"emotional_voltage {ev} >= 0.75 (EAS v1 proxy; full Emotional Symphony is agent-scored)"))
    else:  # scoring core missing is RED, never skipped silently
        checks.append(_gate("scoring_core", False, "rig_comm import failed — stack cannot certify"))

    v = voice.score_voice(text)
    checks.append(_gate("voice_v2", v["verdict"] != "BLOCK",
                        v["verdict"] + ("; " + "; ".join(v["flags"]) if v["flags"] else "")))

    hits = sorted(set(_WOUND_RE.findall(text)))
    forbidden = [w for w in hits if w in voice.FINGERPRINT["wounds_forbidden"]]
    checks.append(_gate("wound_authenticity", not forbidden,
                        f"forbidden wounds present: {forbidden}" if forbidden else "no manufactured pain"))
    if surface.wounds_required:
        checks.append(_gate("wound_resonance", bool(hits),
                            f"named wounds: {hits or 'none'} (>=1 required for '{surface.id}')"))

    unsourced = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if _NUMBER.search(sentence) and not _SOURCED.search(sentence):
            unsourced.append(sentence.strip()[:80])
    fab_ok = bool(unsourced) is False or surface.lane == "internal"
    checks.append(_gate("fabrication", fab_ok,
                        f"{len(unsourced)} unsourced numbers" +
                        ("" if fab_ok else " — public lane blocks: " + " | ".join(unsourced[:3]))))

    if surface.rubric == "bdf30":  # email: WMAQO skeleton present
        # canonical signal is V10 phase_detection (WMAQO cues); label regex is
        # the fallback only when the scoring core could not run.
        if _evaluate is not None:
            ph = r.phase_detection
            need = ("mirror", "autonomy", "qualification", "open_loop")
            weak = [k for k in need if ph.get(k, 0) < 0.7]
            checks.append(_gate("rubric_bdf30", not weak,
                                f"weak WMAQO phases: {weak or 'none'}" if weak else "WMAQO cues present"))
        else:
            need = ("mirror", "autonomy", "qualif", "open loop")
            low = text.lower()
            missing = [n for n in need if n not in low]
            checks.append(_gate("rubric_bdf30", not missing, f"missing WMAQO stages: {missing or 'none'}"))
    elif surface.rubric == "beats":  # screenplay: sluglines
        n = len(re.findall(r"^(?:INT|EXT)\.", text, re.M))
        checks.append(_gate("rubric_beats", n >= 1, f"{n} sluglines (INT./EXT.) >= 1"))

    red = [c for c in checks if c["status"] == "RED"]
    out = {"surface": surface.id, "lane": surface.lane, "checks": checks,
           "can_ship": not red, "blocks": [f"{c['gate']}: {c['detail']}" for c in red],
           "gate_d_required": surface.lane == "public",
           "voice_scorecard": v["verdict"], "meta": meta}
    return out


def run(surface_name: str, text: str) -> int:
    """CLI entry. Returns process exit code."""
    s = surfaces.resolve(surface_name)
    if s is None:
        print(json.dumps({"error": f"unknown surface '{surface_name}'",
                          "known": sorted(surfaces.SURFACES)}))
        return 4
    if s.lane == "private":
        print(json.dumps({"surface": s.id, "can_ship": False,
                          "blocks": ["private lane: scoring a love note by machine is refused (v19.6). "
                                     "Human writes, human ships. No automated gate runs here."]}))
        return 3
    out = evaluate_stack(s, text)
    print(json.dumps(out, indent=2))
    return 0 if out["can_ship"] else 2


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1] if len(sys.argv) > 1 else "linkedin",
                         sys.stdin.read()))
