"""Enterprise Config & Deploy — feature flags, CI/CD hooks, blue-green, canary, rollback.

Per the LinkedIn Studio template Config & Deploy subsystem.
"""
from __future__ import annotations
import json
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from rig_lattice._paths import AUDITS_DIR

ROOT = Path(__file__).parent.parent
FLAGS_FILE = ROOT / "config" / "feature_flags.json"
DEPLOYS_LOG = AUDITS_DIR / "deployments.jsonl"


# ── Feature Flags (8 per LinkedIn Studio template) ──────────────────────
DEFAULT_FLAGS = {
    "enable_llm_judge":       False,
    "enable_brier_tracking":  True,
    "enable_des2_amplifier":  True,
    "enable_physics_short_circuit": True,
    "enable_adversarial_review": True,
    "enable_outcome_observer": True,
    "enable_baseline_recal":  False,   # weekly cron, off until Day 7+
    "enable_hermes_hooks":    True,
}


def _load_flags() -> dict[str, bool]:
    """Read flags from disk, falling back to defaults."""
    if FLAGS_FILE.exists():
        try:
            disk = json.loads(FLAGS_FILE.read_text())
            return {**DEFAULT_FLAGS, **disk}
        except json.JSONDecodeError:
            pass
    return dict(DEFAULT_FLAGS)


def _save_flags(flags: dict[str, bool]) -> None:
    FLAGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    FLAGS_FILE.write_text(json.dumps(flags, indent=2, sort_keys=True))


def get_flag(name: str) -> bool:
    """Read a feature flag. Env override: RIG_DV_FLAG_<NAME>=1/0."""
    env_name = f"RIG_DV_FLAG_{name.upper()}"
    if env_name in os.environ:
        return os.environ[env_name].lower() in ("1", "true", "yes", "on")
    flags = _load_flags()
    return flags.get(name, False)


def set_flag(name: str, value: bool) -> None:
    flags = _load_flags()
    flags[name] = bool(value)
    _save_flags(flags)


def all_flags() -> dict[str, bool]:
    return _load_flags()


# ── Deployment patterns ─────────────────────────────────────────────────
class DeployState(str, Enum):
    PENDING = "pending"
    BLUE = "blue"          # current production
    GREEN = "green"        # new candidate
    CANARY = "canary"      # partial rollout (10% / 50%)
    PROMOTED = "promoted"  # green → new blue
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


@dataclass
class Deployment:
    deploy_id: str
    version: str           # git sha or semver
    state: DeployState = DeployState.PENDING
    canary_pct: int = 0    # 0-100
    promoted_at: float = 0.0
    rolled_back_at: float = 0.0
    rollback_reason: str = ""
    created_at: float = field(default_factory=time.time)


_DEPLOYS: dict[str, Deployment] = {}


def deploy_blue_green(version: str) -> Deployment:
    """Stand up `version` as GREEN (candidate). Existing prod stays BLUE."""
    d = Deployment(
        deploy_id=f"deploy-{int(time.time()*1000)}",
        version=version,
        state=DeployState.GREEN,
    )
    _DEPLOYS[d.deploy_id] = d
    _log_deploy(d, action="deploy_green")
    return d


def deploy_canary(version: str, percent: int = 10) -> Deployment:
    """Stand up `version` as CANARY at `percent`% traffic."""
    d = Deployment(
        deploy_id=f"canary-{int(time.time()*1000)}",
        version=version,
        state=DeployState.CANARY,
        canary_pct=max(1, min(100, percent)),
    )
    _DEPLOYS[d.deploy_id] = d
    _log_deploy(d, action="deploy_canary", percent=percent)
    return d


def promote(deploy_id: str) -> Deployment | None:
    """Promote a GREEN or CANARY deployment to PROMOTED (new prod)."""
    d = _DEPLOYS.get(deploy_id)
    if not d:
        return None
    if d.state not in (DeployState.GREEN, DeployState.CANARY):
        return None
    d.state = DeployState.PROMOTED
    d.promoted_at = time.time()
    _log_deploy(d, action="promote")
    return d


def rollback(deploy_id: str, reason: str = "") -> Deployment | None:
    """Roll back a deployment. Returns the deployment with new state."""
    d = _DEPLOYS.get(deploy_id)
    if not d:
        return None
    d.state = DeployState.ROLLED_BACK
    d.rolled_back_at = time.time()
    d.rollback_reason = reason
    _log_deploy(d, action="rollback", reason=reason)
    return d


def get_deployment(deploy_id: str) -> Deployment | None:
    return _DEPLOYS.get(deploy_id)


def active_deployments() -> list[Deployment]:
    return [d for d in _DEPLOYS.values()
            if d.state in (DeployState.GREEN, DeployState.CANARY, DeployState.PROMOTED)]


def _log_deploy(d: Deployment, **extra) -> None:
    DEPLOYS_LOG.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "deploy_id": d.deploy_id,
        "version": d.version,
        "state": d.state.value,
        "canary_pct": d.canary_pct,
        **extra,
    }
    with DEPLOYS_LOG.open("a") as f:
        f.write(json.dumps(rec, default=str) + "\n")
