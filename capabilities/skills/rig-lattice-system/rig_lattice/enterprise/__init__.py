"""RIG Deviator Enterprise — v1.2 System.

Per the RIG Lattice + LinkedIn Studio enterprise template.

Subsystems (v1.2):
  iqrsqpi         — 7-step meta-pipeline + BMS confidence router + 588-cell math
  observability   — OpenTelemetry-style metrics + Prometheus + 9 health checks
  sre             — SLIs/SLOs, circuit breaker, retry-with-backoff, alerting
  security        — AES-256-GCM vault, RBAC (4 roles), audit hash chain, secret scanning
  quality_gates   — banned phrases, content length, approval gate, regression
  config_deploy   — 8 feature flags, blue-green, canary, rollback
  multi_tenant    — token bucket rate limiter, monthly quota tracking
  database        — SQLite WAL + 7 canonical tables + integrity verification
  sla             — SLA tracker + credit math + promise report
  daemon          — 9-slot long-running scheduler (launchd-wired in v1.2)
  runbooks        — 8 named failure-mode playbooks with auto-remediation
  adversarial     — Reviewer (8 attack vectors) + Coherence Scorer + Outcome Observer
  swarm           — (v1.2) concurrent +20σ agent dispatch + Coral Reef mesh
  cost_ledger     — (v1.2) per-mission budgets + LLM spend tracking
  notify          — (v1.2) Slack + email + Telegram + local-fallback
"""
__version__ = "1.2.0"

from rig_lattice.enterprise import (
    iqrsqpi, observability, sre, security, quality_gates, config_deploy,
    multi_tenant, database, sla, daemon, runbooks, adversarial,
    swarm, cost_ledger, notify,
)

__all__ = ["iqrsqpi", "observability", "sre", "security", "quality_gates",
            "config_deploy", "multi_tenant", "database", "sla", "daemon",
            "runbooks", "adversarial", "swarm", "cost_ledger", "notify",
            "__version__"]
