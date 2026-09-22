"""Write-packet assembly (v6.12) — deterministic context assembly.

The engine does not write; it assembles the exact packet an agent needs to
write, and names the gates the artifact must clear afterwards. Generation is
the agent's job (per lane policy); assembly and enforcement are code.
"""

from __future__ import annotations

from . import surfaces


def build_packet(surface_name: str, brief: str, persona: str = "",
                 surface: surfaces.Surface | None = None) -> str:
    s = surface or surfaces.resolve(surface_name)
    if s is None:
        raise KeyError(surface_name)
    lines = [
        f"# Write packet — surface: {s.id}  lane: {s.lane}",
        "",
        "## Brief",
        brief.strip() or "(empty brief — ask for one before drafting)",
        "",
        f"## Voice: fingerprint v2 (MANDATORY)",
        "Load `rig-communications-voice`; draft against FINGERPRINT, then run",
        "`rig-comm voice-check` and iterate until verdict != BLOCK.",
        "",
        "## Wounds (real only): " + ", ".join(("W3", "W4", "W5", "W6", "W8")),
        "Library: `rig-communications-wounds`. W1/W2/W7 are FORBIDDEN (manufactured pain).",
        f"Wound resonance required: {'yes' if s.wounds_required else 'no (exempt surface)'}",
        "",
        "## Behavioral fusion (v4) — load before drafting:",
        *(f"- {b}" for b in s.bx),
        "",
        "## Deviation posture (v13):",
        f"- engines: {', '.join(s.engines)}",
        f"- deviation budget: {s.budget} (candidates before convergence)",
        f"- physics-first short-circuit: {'ON (outward claims must cite mechanism)' if s.physics_first else 'off'}",
        "",
        "## Corpus grounding: `data/corpora/writing-craft/<surface>/` transcripts (manifest.jsonl lists channels)",
        f"## Template: {s.template or '(none registered for this surface)'}",
        "",
    ]
    if persona:
        lines += ["## Persona (v12)", persona.strip(), ""]
    if s.lane == "private":
        lines += ["> PRIVATE LANE: this packet is for a human writing to James.",
                  "> Never autonomous, never federated, never scored by machine gates.",
                  ""]
    else:
        lines += [
            "## Ship gate (run before claiming done):",
            f"`python3 -m rig_comms.gates {s.id} < draft.txt` → exit 0 required.",
            f"AGF >= {s.agf_min}; sigma target {s.sigma_target}; rubric: {s.rubric}."
            + (" Gate-D approval required before publish (public lane)." if s.lane == "public" else
               " Gate-D approval required before send/share (internal lane)."),
        ]
    return "\n".join(lines)
