"""DES core math primitives per DOCTRINE.md §2 and §5.1."""
from rig_lattice.core.robust_mad_z import robust_mad_z, mad
from rig_lattice.core.sigma import sigma_score, patent_examiner_trigger
from rig_lattice.core.escalation import escalation_cost
from rig_lattice.core.bdf import bdf
from rig_lattice.core.thresholds import THRESHOLDS, detonation_gate, PASS, BLOCK
from rig_lattice.core.rig_l import rig_l_composite, rig_l_label
from rig_lattice.core.base import DeviationEngine, EngineResult
from rig_lattice.core.registry import ENGINE_REGISTRY, resolve_engine, list_engines_by_layer

__all__ = [
    "robust_mad_z", "mad",
    "sigma_score", "patent_examiner_trigger",
    "escalation_cost",
    "bdf",
    "THRESHOLDS", "detonation_gate", "PASS", "BLOCK",
    "rig_l_composite", "rig_l_label",
    "DeviationEngine", "EngineResult",
    "ENGINE_REGISTRY", "resolve_engine", "list_engines_by_layer",
]
