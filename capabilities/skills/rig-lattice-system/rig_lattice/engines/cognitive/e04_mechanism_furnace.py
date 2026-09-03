"""e04 MechanismFurnace — Layer 1 Cognitive (OUTPUT, ±20σ).

DOCTRINE.md §1.4 entry #4. Criteria: criteria/mechanism_furnace.yaml.
"""
from rig_lattice.engines.cognitive._factory import make_cognitive_engine

ENGINE = make_cognitive_engine(4)
