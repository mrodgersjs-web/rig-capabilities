"""e08 EvolutionaryMemoryFlywheel — Layer 1 Cognitive (OUTPUT, ±20σ).

DOCTRINE.md §1.4 entry #8. Criteria: criteria/darwinian_selection.yaml.
"""
from rig_lattice.engines.cognitive._factory import make_cognitive_engine

ENGINE = make_cognitive_engine(8)
