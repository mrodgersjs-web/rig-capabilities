"""e28 WhaleSpiral — Layer 2 Nature (PROCESS, ±20σ).

DOCTRINE.md §1.4 entry #28. Bio-formula: see adapters/bio_formulas.py.
Criteria: criteria/humpback_spiral.yaml. Blend: 0.7·criteria + 0.3·bio.
"""
from rig_lattice.engines.nature._factory import make_nature_engine

ENGINE = make_nature_engine(28)
