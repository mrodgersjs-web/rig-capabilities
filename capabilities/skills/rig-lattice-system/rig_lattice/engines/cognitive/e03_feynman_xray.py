"""e03 FeynmanXRay — Layer 1 Cognitive (OUTPUT, ±20σ).

DOCTRINE.md §1.4 entry #3. Criteria: criteria/feynman_xray.yaml.
"""
from rig_lattice.engines.cognitive._factory import make_cognitive_engine

ENGINE = make_cognitive_engine(3)
