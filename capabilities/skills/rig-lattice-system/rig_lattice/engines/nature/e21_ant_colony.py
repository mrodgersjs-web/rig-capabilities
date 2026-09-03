"""e21 AntColonyPheromone — Layer 2 Nature (PROCESS, ±20σ).

DOCTRINE.md §1.4 entry #21. Bio-formula: see adapters/bio_formulas.py.
Criteria: criteria/pheromone_swarm.yaml. Blend: 0.7·criteria + 0.3·bio.
"""
from rig_lattice.engines.nature._factory import make_nature_engine

ENGINE = make_nature_engine(21)
