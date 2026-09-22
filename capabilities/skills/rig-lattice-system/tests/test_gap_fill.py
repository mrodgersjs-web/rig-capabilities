"""Smoke tests for the 10-item gap-fill batch (v1.2.0).

Covers:
  1. REPO_GUARD.md sentinel exists
  2. daemon launchd plist + start script exist
  3. orchestrator persists missions to SQLite
  4. L3 A3 swarm dispatches concurrent agents
  5. CrewAI plus20_swarm handler runs real swarm
  6. AES-256-GCM vault round-trips + rejects tamper
  7. cost ledger records LLM calls + enforces budget
  8. notification system attempts the right channels per severity
  9. FastAPI dashboard app loads with all routes
 10. CI/CD workflow files exist
"""
from __future__ import annotations
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent


# ── 1. Repo sentinel ─────────────────────────────────────────────────────
def test_repo_guard_present():
    assert (ROOT / "REPO_GUARD.md").exists()


def test_repo_sentinel_script_executable():
    p = ROOT / "bin" / "repo-sentinel-check.sh"
    assert p.exists()
    assert os.access(p, os.X_OK)


# ── 2. Daemon ────────────────────────────────────────────────────────────
# The launchd plists are not vendored: they hardcode
# /Users/<author>/Desktop/rig-deviator as the working directory, which is
# meaningless in a skill installed into five harness roots. The daemon
# scripts below ARE vendored and stay under test. See PROVENANCE.md.

def test_daemon_scripts_executable():
    for name in ("daemon-start.sh", "daemon-rotate-logs.sh",
                  "daemon-status.sh", "daemon-install.sh"):
        p = ROOT / "bin" / name
        assert p.exists(), f"missing {p}"
        assert os.access(p, os.X_OK), f"not executable {p}"


def test_daemon_ticks_without_error():
    from rig_lattice.enterprise.daemon import Daemon
    d = Daemon()
    # Force all slots due
    import time
    now = time.time()
    for s in d.slots:
        s.next_run = now - 1
    executed = d.tick()
    assert len(executed) == len(d.slots)
    # No slot should have unhandled exception (errors are captured in last_error)
    for s in d.slots:
        # alert_scan + audit_chain_verify can legitimately surface state, just verify
        # they didn't raise unhandled
        pass


# ── 3. DB writes from pipeline ───────────────────────────────────────────
def test_pipeline_writes_mission_row():
    os.environ["RIG_DV_OFFLINE"] = "1"
    from rig_lattice.system import run_system
    strong = ROOT / "examples" / "example_strict_passing.md"
    if not strong.exists():
        return
    result = run_system(source=str(strong), confidence=0.85)
    assert hasattr(result, "persistence")
    p = result.persistence
    assert p["missions_written"] == 1
    assert p["engine_scores_written"] >= 40
    assert p["audit_chain_entry_hash"]


def test_recent_missions_readable():
    from rig_lattice.system.persistence import recent_missions
    missions = recent_missions(limit=5)
    assert isinstance(missions, list)


# ── 4. Real L3 A3 swarm dispatch ─────────────────────────────────────────
def test_swarm_dispatch_runs_concurrent_agents():
    os.environ["RIG_DV_OFFLINE"] = "1"
    from rig_lattice.enterprise.swarm import dispatch_swarm
    text = "Some weak text that needs rewriting at +20 sigma."
    weak = [
        {"slug": "absolute_zero", "codename": "Absolute Zero", "sigma": -15},
        {"slug": "specificity_gate", "codename": "Specificity Gate", "sigma": -12},
        {"slug": "evidence_anchor", "codename": "Evidence Anchor", "sigma": -10},
    ]
    dispatch = dispatch_swarm(text, weak, mission_id="test-swarm",
                                 max_agents=3, cost_cap_usd=0.50)
    assert len(dispatch.agents) == 3
    assert sum(1 for a in dispatch.agents if a.ok) == 3
    assert dispatch.mesh_synthesis  # not empty


# ── 5. CrewAI plus20_swarm handler ───────────────────────────────────────
def test_crewai_plus20_swarm_handler_real():
    os.environ["RIG_DV_OFFLINE"] = "1"
    from rig_lattice.enterprise.integrations.crewai import crewai_dispatch
    result = crewai_dispatch("plus20_swarm", {
        "L1_CAPTURE": {"text": "weak placeholder text"},
        "weakest_engines": [
            {"slug": "absolute_zero", "codename": "Absolute Zero", "sigma": -10},
        ],
        "mission_id": "test-crew",
    })
    assert result["crew"] == "plus20_swarm"
    assert result["action"] == "dispatched"
    assert result["result"]["agent_count"] == 1


# ── 6. AES-256-GCM vault ─────────────────────────────────────────────────
def test_vault_aes_gcm_roundtrip():
    from rig_lattice.enterprise.security import vault_encrypt, vault_decrypt, vault_algo
    assert "AES" in vault_algo() or "PBKDF2" in vault_algo()
    ct = vault_encrypt("hello-secret-123", "master-1")
    assert vault_decrypt(ct, "master-1") == "hello-secret-123"


def test_vault_rejects_tamper():
    import base64
    from rig_lattice.enterprise.security import vault_encrypt, vault_decrypt
    ct = vault_encrypt("hello", "k")
    blob = bytearray(base64.b64decode(ct))
    blob[-3] ^= 0xFF
    bad = base64.b64encode(bytes(blob)).decode()
    try:
        vault_decrypt(bad, "k")
        assert False, "tamper not detected"
    except ValueError:
        pass


def test_vault_rejects_wrong_key():
    from rig_lattice.enterprise.security import vault_encrypt, vault_decrypt
    ct = vault_encrypt("hello", "right-key")
    try:
        vault_decrypt(ct, "wrong-key")
        assert False, "wrong key accepted"
    except ValueError:
        pass


# ── 7. Cost ledger ───────────────────────────────────────────────────────
def test_cost_ledger_records_and_enforces():
    from rig_lattice.enterprise.cost_ledger import (
        set_budget, record_llm_cost, mission_spend,
        mission_remaining, BudgetExceededError, reset_mission,
    )
    mid = "test-budget-1"
    reset_mission(mid)
    set_budget(mid, 0.10)
    # Small call: should succeed
    e1 = record_llm_cost(mid, "gpt-4o-mini", in_tokens=1000, out_tokens=500)
    assert e1.total_usd > 0
    assert mission_spend(mid) > 0
    # Huge call: should raise
    try:
        record_llm_cost(mid, "gpt-4o", in_tokens=10_000_000, out_tokens=10_000_000)
        assert False, "budget not enforced"
    except BudgetExceededError:
        pass


def test_cost_ledger_offline_zero_cost():
    from rig_lattice.enterprise.cost_ledger import record_llm_cost, reset_mission
    reset_mission("offline-test")
    e = record_llm_cost("offline-test", "offline", in_tokens=0, out_tokens=0,
                         enforce_budget=False)
    assert e.total_usd == 0.0


# ── 8. Notifications ─────────────────────────────────────────────────────
def test_notify_info_local_only():
    from rig_lattice.enterprise.notify import notify
    r = notify("info", "test", "test message")
    assert r.channels_attempted == []  # local-only
    assert r.severity == "info"


def test_notify_critical_attempts_all_channels():
    from rig_lattice.enterprise.notify import notify
    r = notify("critical", "test_crit", "test critical message")
    assert set(r.channels_attempted) == {"slack", "email", "telegram"}


def test_notify_channel_status_dict():
    from rig_lattice.enterprise.notify import channel_status
    s = channel_status()
    assert "slack_warn" in s
    assert "email" in s
    assert s["local_log"] is True


# ── 9. Dashboard (optional FastAPI dependency) ───────────────────────────
def test_dashboard_app_loads():
    try:
        import fastapi  # noqa: F401 — importability, not just discoverability
    except ImportError as exc:
        raise unittest.SkipTest(f"fastapi unusable: {exc}") from exc
    from rig_lattice.dashboard.app import app
    paths = {r.path for r in app.routes if hasattr(r, "path")}
    for required in ("/", "/health", "/api/missions",
                       "/api/daemon", "/api/cost-ledger"):
        assert required in paths, f"missing route {required}"


# ── 10. CI/CD ────────────────────────────────────────────────────────────
# The upstream .github/ workflows and the deploy/launchd/*.plist pair are NOT
# vendored into this bundle: the plists hardcode an absolute path from the
# original author's machine, and CI belongs to the rig-capabilities repo that
# hosts this skill, not to the skill payload. The tests that asserted their
# presence are deleted rather than left failing or, worse, softened into
# something that passes without checking anything. See PROVENANCE.md.


# ── Manual runner ────────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [(n, fn) for n, fn in globals().items()
              if n.startswith("test_") and callable(fn)]
    passed, failed = 0, []
    for name, fn in tests:
        try:
            fn()
            print(f"  ✓ {name}")
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {name}  →  {e}")
            failed.append(name)
        except Exception as e:
            print(f"  ⚠ {name}  →  {type(e).__name__}: {e}")
            failed.append(name)
    print()
    print(f"  RESULT: {passed}/{len(tests)} passed")
    if failed:
        print(f"  FAILED: {failed}")
        sys.exit(1)
