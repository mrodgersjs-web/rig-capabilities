"""DOCTRINE.md §6 — Hermes integration hooks.

Five hooks, all callable from Hermes orchestrator:
  - completion_scorer:  fires on every mission packet completion
  - circuit_breaker:    fires pre-integration; blocks if any L3 gate fails
  - adversarial_review: fires for tier ≥ published artifacts
  - cron:               weekly baseline + Brier recal
  - kanban_event:       fires on skill promotion candidates
"""
from rig_lattice.deviator.hooks.hermes_completion_scorer import completion_scorer
from rig_lattice.deviator.hooks.hermes_circuit_breaker import circuit_breaker
from rig_lattice.deviator.hooks.hermes_adversarial_review import adversarial_review
from rig_lattice.deviator.hooks.hermes_cron import weekly_recal_cron
from rig_lattice.deviator.hooks.hermes_kanban_event import kanban_event

__all__ = [
    "completion_scorer",
    "circuit_breaker",
    "adversarial_review",
    "weekly_recal_cron",
    "kanban_event",
]
