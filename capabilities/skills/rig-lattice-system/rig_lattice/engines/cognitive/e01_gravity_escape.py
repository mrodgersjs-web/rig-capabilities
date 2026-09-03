"""e01 GravityEscape — Layer 1 Cognitive (OUTPUT, ±20σ).

DOCTRINE.md §1.4 entry #1. Criteria: criteria/gravity_escape.yaml.
"""
from rig_lattice.engines.cognitive._factory import make_cognitive_engine

ENGINE = make_cognitive_engine(1)
