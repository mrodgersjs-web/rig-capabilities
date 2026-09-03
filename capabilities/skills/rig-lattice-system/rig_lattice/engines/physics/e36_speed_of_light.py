"""e36 SpeedOfLightCausality — Layer 3 Physics (STATE, ±30σ HARD GATE).

DOCTRINE.md §1.4 entry #36. Physics formula: see adapters/physics_formulas.py.
Criteria: criteria/speed_of_lumen.yaml. Blend: 0.5·criteria + 0.5·physics.
HARD GATE: failure HARD_BLOCKs the entire pipeline.
"""
from rig_lattice.engines.physics._factory import make_physics_engine

ENGINE = make_physics_engine(36)
