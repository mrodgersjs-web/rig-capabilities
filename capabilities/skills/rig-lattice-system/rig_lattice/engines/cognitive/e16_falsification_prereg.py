"""e16 FalsificationPrereg — Layer 1 Cognitive (OUTPUT, ±20σ).

DOCTRINE.md §1.4 entry #16. Criteria: criteria/falsification_prereg.yaml.
"""
from rig_lattice.engines.cognitive._factory import make_cognitive_engine

ENGINE = make_cognitive_engine(16)
