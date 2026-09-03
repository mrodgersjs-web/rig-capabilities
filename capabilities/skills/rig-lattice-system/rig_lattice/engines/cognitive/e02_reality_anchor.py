"""e02 RealityAnchor — Layer 1 Cognitive (OUTPUT, ±20σ).

DOCTRINE.md §1.4 entry #2. Criteria: criteria/reality_anchor.yaml.
"""
from rig_lattice.engines.cognitive._factory import make_cognitive_engine

ENGINE = make_cognitive_engine(2)
