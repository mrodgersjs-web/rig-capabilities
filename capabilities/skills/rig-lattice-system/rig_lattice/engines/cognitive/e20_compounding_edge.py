"""e20 CompoundingEdge — Layer 1 Cognitive (OUTPUT, ±20σ).

DOCTRINE.md §1.4 entry #20. Criteria: criteria/compounding_edge.yaml.
"""
from rig_lattice.engines.cognitive._factory import make_cognitive_engine

ENGINE = make_cognitive_engine(20)
