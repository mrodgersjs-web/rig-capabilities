"""e27 ResourceAllocator — Layer 2 Nature (PROCESS, ±20σ).

DOCTRINE.md §1.4 entry #27. Bio-formula: see adapters/bio_formulas.py.
Criteria: criteria/chemotaxis_gradient.yaml. Blend: 0.7·criteria + 0.3·bio.
"""
from rig_lattice.engines.nature._factory import make_nature_engine

ENGINE = make_nature_engine(27)
