"""e22 BeeForagingAllocator — Layer 2 Nature (PROCESS, ±20σ).

DOCTRINE.md §1.4 entry #22. Bio-formula: see adapters/bio_formulas.py.
Criteria: criteria/bee_foraging.yaml. Blend: 0.7·criteria + 0.3·bio.
"""
from rig_lattice.engines.nature._factory import make_nature_engine

ENGINE = make_nature_engine(22)
