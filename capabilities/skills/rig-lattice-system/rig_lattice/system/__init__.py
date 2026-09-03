"""RIG Deviator System — full 7-level enterprise pipeline.

L1 CAPTURE      — pull artifact from any source (file / URL / stdin / scraper)
L2 PROCESS      — clean, normalize, hash, route into auditor
L3 CREATE       — generate +20σ variants per weak engine (deviate)
L4 DISTRIBUTE   — render reports (HTML / markdown / JSON receipts)
L5 ENGAGE       — surface failed gates, return actionable next-step copy
L6 CONVERT      — apply patches; produce strict-passing artifact
L7 AUTONOMIZE   — daemon-driven continuous audit + Brier outcome observation

Each level has 4 A-mode archetypes (A1 / A2 / A3 / A4) per the BMS router:
  A1  Python-only      ≥ 0.75 confidence  → deterministic path
  A2  Hybrid            0.45-0.74          → Python + light LLM grading
  A3  Bounded           0.25-0.44          → LLM with cost cap
  A4  Agent-free        < 0.25             → human gate mandatory

7 levels × 4 archetypes = 28 archetypes. Each one is a callable.
"""
from rig_lattice.system.levels import (
    L1_CAPTURE, L2_PROCESS, L3_CREATE, L4_DISTRIBUTE,
    L5_ENGAGE, L6_CONVERT, L7_AUTONOMIZE,
    Level, LEVELS,
)
from rig_lattice.system.archetypes import (
    ARCHETYPES, get_archetype, list_archetypes_for_level,
    ArchetypeId, Archetype,
)
from rig_lattice.system.orchestrator import (
    SystemRun, run_system, run_level,
)

__all__ = [
    "L1_CAPTURE", "L2_PROCESS", "L3_CREATE", "L4_DISTRIBUTE",
    "L5_ENGAGE", "L6_CONVERT", "L7_AUTONOMIZE",
    "Level", "LEVELS",
    "ARCHETYPES", "get_archetype", "list_archetypes_for_level",
    "ArchetypeId", "Archetype",
    "SystemRun", "run_system", "run_level",
]
