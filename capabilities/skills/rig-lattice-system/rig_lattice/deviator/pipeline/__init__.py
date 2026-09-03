"""DES pipeline per DOCTRINE.md §4 + §8 Day 2.

Gate ordering (non-negotiable):
  1. Physics State Gates (L3, ±30σ)    → if any BLOCK → short-circuit
  2. Cognitive Output Gates (L1, ±20σ) → score & gate
  3. Nature Process Gates (L2, ±20σ)   → score & gate
  4. Composite RIG-L                   → headline verdict
  5. Detonation Gate (tier × patent × council)
"""
from rig_lattice.deviator.pipeline.orchestrator import orchestrate, OrchestrationResult
from rig_lattice.deviator.pipeline.audit import audit_log, AuditRecord
from rig_lattice.deviator.pipeline.intent_map import resolve_intent, INTENT_MAP
from rig_lattice.deviator.pipeline.approval_client import ApprovalClient, ApprovalRequest, ApprovalVerdict

__all__ = [
    "orchestrate", "OrchestrationResult",
    "audit_log", "AuditRecord",
    "resolve_intent", "INTENT_MAP",
    "ApprovalClient", "ApprovalRequest", "ApprovalVerdict",
]
