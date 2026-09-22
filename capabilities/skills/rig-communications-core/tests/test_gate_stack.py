"""rig_comms gate stack — planted-failure suite (adversarial-verification-loop).

Every load-bearing gate MUST be shown to go RED on a planted defect, then GREEN
on restore. Run: python3 tests/test_gate_stack.py  (exit 0 = every gate red-capable).
No pytest — stdlib asserts, house style.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # rig-communications-core/
from rig_comms import gates, surfaces, voice  # noqa: E402


def _green(surface):
    """A draft clean for the gates we test (agf/sigma excluded — text-shape only)."""
    if surface.rubric == "bdf30":
        return ("I saw the 3 open ops seats on your careers page (source: careers page) — "
                "the cost of those gaps shows up as friction on every Thursday escalation.\n\n"
                "Mirror: your team is hiring while the backlog grows; no pressure.\n\n"
                "Only if this fits your quarter; if useful, one question worth testing first: "
                "which seat breaks first. The W4 gap between what a founder says and what the "
                "calendar shows is where production gets proven, per the 2026 RIG operator study [1].")
    return ("The W4 gap shows up in the numbers [1], per the 2026 study. The 2026 RIG operator "
            "baseline proves deviation beats the median. Production is proof. The operator "
            "builds the thing that ships at 3am and holds it up under audit.")


def _red_each_gate():
    """One planted defect per gate; returns gate -> RED-check assertion pairs."""
    s = surfaces.resolve("emails")
    clean = _green(s)

    # voice_v2 RED: plant a banned word
    banned = voice.score_voice(clean + " This seamless solution will empower you.")
    assert banned["verdict"] == "BLOCK", "voice gate missed banned words"

    # wound_authenticity RED: plant a forbidden wound (W1 = manufactured pain)
    fab = gates.evaluate_stack(s, clean.replace("W4", "W1"))
    wa = next(c for c in fab["checks"] if c["gate"] == "wound_authenticity")
    assert wa["status"] == "RED", "authenticity gate accepted W1"

    # wound_resonance RED: strip every wound tag from a wound-required surface
    nowound = gates.evaluate_stack(s, re.sub(r"\bW\d\b", "gap", clean))
    wr = next(c for c in nowound["checks"] if c["gate"] == "wound_resonance")
    assert wr["status"] == "RED", "resonance gate passed with zero wounds"

    # fabrication RED on public lane: plant an unsourced number
    li = surfaces.resolve("linkedin")
    lie = _green(li) + " We grew revenue 412% last quarter."
    pub = gates.evaluate_stack(li, lie)
    fabg = next(c for c in pub["checks"] if c["gate"] == "fabrication")
    assert fabg["status"] == "RED", "fabrication gate passed an unsourced public number"

    # rubric_bdf30 RED: strip the autonomy cue so V10's phase_detection goes weak
    bare = gates.evaluate_stack(s, clean.replace("no pressure", "whatever"))
    rb = next(c for c in bare["checks"] if c["gate"] == "rubric_bdf30")
    assert rb["status"] == "RED", "bdf30 rubric passed without the autonomy phase"
    spec = gates.evaluate_stack(surfaces.resolve("specs"),
                                "The gate is a pure function; it short-circuits on red. "
                                "Speed of light: publish waits on verify. See mechanism per §2.")
    assert not any(c["gate"] == "wound_resonance" for c in spec["checks"]), \
        "specs should be wound-exempt"

    # private lane RED (privacy lock): love-notes never scored by machine
    assert gates.run("love-notes", "anything") == 3, "private lane was machine-scorable"


def _clean_green():
    for name in ("emails", "linkedin", "substack"):
        s = surfaces.resolve(name)
        out = gates.evaluate_stack(s, _green(s))
        # only require the text-shape gates green; scoring-core gates may block
        # on AGF/sigma depending on the corpus baseline — those are reported, not faked.
        for gate in ("voice_v2", "wound_authenticity", "wound_resonance",
                     "fabrication", "rubric_bdf30"):
            c = next((c for c in out["checks"] if c["gate"] == gate), None)
            if c:
                assert c["status"] == "PASS", f"{name} {gate} unexpectedly RED: {c['detail']}"


if __name__ == "__main__":
    _red_each_gate()
    _clean_green()
    print("OK: voice_v2, wound_authenticity, wound_resonance, fabrication, rubric_bdf30 "
          "all proven red-capable; specs exemption + private lock hold.")
