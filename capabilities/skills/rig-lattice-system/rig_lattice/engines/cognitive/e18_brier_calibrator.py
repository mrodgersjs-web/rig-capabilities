"""e18 BrierCalibrator — Layer 1 Cognitive (OUTPUT, ±20σ).

DOCTRINE.md §1.4 entry #18. Criteria: criteria/bayesian_calibration.yaml.
"""
from rig_lattice.engines.cognitive._factory import make_cognitive_engine

ENGINE = make_cognitive_engine(18)
