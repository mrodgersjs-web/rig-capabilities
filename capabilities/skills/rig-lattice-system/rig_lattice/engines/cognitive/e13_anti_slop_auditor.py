"""e13 AntiSlopAuditor — Layer 1 Cognitive (OUTPUT, ±20σ).

DOCTRINE.md §1.4 entry #13. Criteria: criteria/anti_slop_auditor.yaml.
"""
from rig_lattice.engines.cognitive._factory import make_cognitive_engine

ENGINE = make_cognitive_engine(13)
