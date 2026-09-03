"""e12 PredictiveErrorCalibration — Layer 1 Cognitive (OUTPUT, ±20σ).

DOCTRINE.md §1.4 entry #12. Criteria: criteria/predictive_surprise.yaml.
"""
from rig_lattice.engines.cognitive._factory import make_cognitive_engine

ENGINE = make_cognitive_engine(12)
