"""e10 TemporalHorizonIntegrity — Layer 1 Cognitive (OUTPUT, ±20σ).

DOCTRINE.md §1.4 entry #10. Criteria: criteria/temporal_horizon_integrity.yaml.
"""
from rig_lattice.engines.cognitive._factory import make_cognitive_engine

ENGINE = make_cognitive_engine(10)
