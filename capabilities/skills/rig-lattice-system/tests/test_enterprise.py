"""Day-7 + Enterprise acceptance tests.

Covers:
  - IQRSQPI 7-step pipeline + BMS router + 588-cell math
  - Observability (metrics + 9 health checks)
  - SRE (SLI/SLO + circuit breaker + retry)
  - Security (vault + RBAC + audit chain + secret scanning)
  - Quality gates (banned phrases + length + approval gate)
  - Config & deploy (feature flags + blue-green + canary + rollback)
  - Multi-tenant (token bucket + quota)
  - Database (schema + WAL + integrity)
  - SLA (tracker + credit math + promise report)
  - Daemon (9 slots)
  - Runbooks (8 playbooks)
  - Adversarial (Reviewer + Coherence + Outcome Observer)
"""
from __future__ import annotations
import sys
from pathlib import Path


from rig_lattice.enterprise.iqrsqpi import (
    IQRSQPIStep, IQRSQPI_ORDER, BMSMode, BMS_THRESHOLDS, route_bms,
    Dimension, TOTAL_CELLS, LatticeCell, all_cells, run_iqrsqpi,
)
from rig_lattice.enterprise.observability import (
    counter_inc, gauge_set, histogram_observe, metric_snapshot,
    prometheus_exposition, run_health_checks, health_summary, log_event,
)
from rig_lattice.enterprise.sre import (
    SLOS, SLITracker, record_sli, sli_status,
    CircuitBreaker, CircuitState, get_breaker, retry_with_backoff,
    alert, AlertSeverity, check_slo_alerts,
)
from rig_lattice.enterprise.security import (
    vault_encrypt, vault_decrypt, vault_put, vault_get,
    Role, RBAC_MATRIX, authorize, require_role,
    chain_append, chain_head, chain_verify,
    scan_for_secrets, assert_no_secrets,
)
from rig_lattice.enterprise.quality_gates import (
    BANNED_PHRASES, banned_phrase_violations,
    LENGTH_RULES, length_check,
    ApprovalStatus, request_approval, grant_approval, reject_approval,
    pending_approvals, run_regression,
)
from rig_lattice.enterprise.config_deploy import (
    DEFAULT_FLAGS, get_flag, set_flag, all_flags,
    DeployState, deploy_blue_green, deploy_canary, promote, rollback,
    active_deployments,
)
from rig_lattice.enterprise.multi_tenant import (
    TokenBucket, Tenant, register_tenant, consume_audit, consume_llm_call,
    quota_status,
)
from rig_lattice.enterprise.database import (
    init_db, integrity_check, insert_audit_entry, get_last_audit_hash,
    verify_audit_chain, CANONICAL_TABLE_COUNT,
)
from rig_lattice.enterprise.sla import (
    CANONICAL_SLAS, record_sla_event, promise_report, total_credit_owed,
)
from rig_lattice.enterprise.daemon import (
    Daemon, DEFAULT_SLOTS, SlotState,
)
from rig_lattice.enterprise.runbooks import (
    RUNBOOKS, list_runbooks, get_runbook, execute_runbook,
)
from rig_lattice.enterprise.adversarial import (
    adversarial_review, IndependentReviewerError,
    coherence_score, coherence_alert, COHERENCE_ALERT_THRESHOLD,
    observe_outcome, engine_weight_update, ATTACK_VECTORS,
)


# ── 1. IQRSQPI Lattice ───────────────────────────────────────────────────

def test_iqrsqpi_has_7_steps():
    assert len(IQRSQPI_ORDER) == 7
    assert IQRSQPI_ORDER[0] == IQRSQPIStep.INTENT
    assert IQRSQPI_ORDER[-1] == IQRSQPIStep.INTEGRATE

def test_bms_router_high_confidence_a1():
    assert route_bms(0.90) == BMSMode.A1

def test_bms_router_medium_confidence_a2():
    assert route_bms(0.60) == BMSMode.A2

def test_bms_router_low_confidence_a3():
    assert route_bms(0.30) == BMSMode.A3

def test_bms_router_very_low_confidence_a4():
    assert route_bms(0.10) == BMSMode.A4

def test_bms_router_force_a4_overrides():
    assert route_bms(0.99, force_a4=True) == BMSMode.A4

def test_lattice_has_588_cells():
    cells = all_cells()
    assert len(cells) == 588 == TOTAL_CELLS
    assert TOTAL_CELLS == 7 * 3 * 4 * 7

def test_lattice_cell_unique_ids():
    cells = all_cells()
    ids = [c.cell_id for c in cells]
    assert len(ids) == len(set(ids))

def test_iqrsqpi_run_all_steps():
    handlers = {step: lambda s, st=step: (True, f"output_for_{st.value}", "")
                for step in IQRSQPI_ORDER}
    run = run_iqrsqpi(handlers, confidence=0.85)
    assert run.ok is True
    assert run.bms_mode == BMSMode.A1
    assert len(run.steps) == 7

def test_iqrsqpi_short_circuits_on_handler_failure():
    handlers = {step: lambda s, st=step: (True, "", "") for step in IQRSQPI_ORDER}
    handlers[IQRSQPIStep.RESEARCH] = lambda s: (False, None, "research blocked")
    run = run_iqrsqpi(handlers, confidence=0.85)
    assert run.ok is False
    assert run.short_circuited_at == IQRSQPIStep.RESEARCH
    assert len(run.steps) == 3  # INTENT, QUESTION, RESEARCH


# ── 2. Observability ────────────────────────────────────────────────────

def test_counter_inc_increments():
    counter_inc("test_counter")
    counter_inc("test_counter")
    snap = metric_snapshot()
    assert snap["counters"]["test_counter"] >= 2

def test_gauge_set_records_value():
    gauge_set("test_gauge", 42.0)
    snap = metric_snapshot()
    assert snap["gauges"]["test_gauge"] == 42.0

def test_histogram_observes_samples():
    for v in [1.0, 2.0, 3.0, 4.0, 5.0]:
        histogram_observe("test_hist", v)
    snap = metric_snapshot()
    assert snap["histograms"]["test_hist"]["count"] >= 5

def test_prometheus_exposition_renders():
    counter_inc("prom_test")
    text = prometheus_exposition()
    assert "TYPE" in text or "prom_test" in text

def test_health_checks_run():
    checks = run_health_checks()
    assert len(checks) == 9  # canonical 9 checks

def test_health_summary_passes_on_clean_install():
    s = health_summary()
    assert s["total"] == 9
    assert s["passed"] >= 7  # at least 7/9 must pass even in partial install


# ── 3. SRE ──────────────────────────────────────────────────────────────

def test_slos_defined():
    assert len(SLOS) >= 5
    assert "audit_availability" in SLOS

def test_sli_record_and_status():
    for _ in range(10):
        record_sli("audit_availability", True)
    record_sli("audit_availability", False)
    status = sli_status()
    assert "audit_availability" in status

def test_circuit_breaker_opens_after_threshold():
    cb = CircuitBreaker(name="test", failure_threshold=3)
    for _ in range(3):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    assert cb.state == CircuitState.OPEN

def test_circuit_breaker_closed_on_success():
    cb = CircuitBreaker(name="test_clean")
    ok, val, reason = cb.call(lambda: 42)
    assert ok is True
    assert val == 42
    assert cb.state == CircuitState.CLOSED

def test_retry_with_backoff_succeeds_eventually():
    state = {"n": 0}
    def flaky():
        state["n"] += 1
        if state["n"] < 2:
            raise RuntimeError("flake")
        return "ok"
    ok, val, errors = retry_with_backoff(flaky, max_attempts=3, base_delay=0.01)
    assert ok is True
    assert val == "ok"
    assert len(errors) == 1

def test_retry_with_backoff_fails_after_max():
    ok, val, errors = retry_with_backoff(
        lambda: (_ for _ in ()).throw(RuntimeError("always")),
        max_attempts=2, base_delay=0.01,
    )
    assert ok is False
    assert len(errors) == 2


# ── 4. Security ─────────────────────────────────────────────────────────

def test_vault_roundtrip():
    secret = "ABC123 SECRET KEY"
    key = "test-master-key-do-not-use-in-prod"
    ct = vault_encrypt(secret, key)
    pt = vault_decrypt(ct, key)
    assert pt == secret

def test_vault_tamper_detection():
    secret = "ABC123"
    key = "test-key"
    ct = vault_encrypt(secret, key)
    # Corrupt the ciphertext
    import base64
    blob = bytearray(base64.b64decode(ct))
    blob[-1] ^= 0xFF
    tampered = base64.b64encode(bytes(blob)).decode("ascii")
    try:
        vault_decrypt(tampered, key)
        assert False, "should have raised on tampered ciphertext"
    except ValueError:
        pass

def test_rbac_4_roles():
    assert len(Role) == 4

def test_rbac_authorize_passes():
    ok, _ = authorize("audit.run", Role.OPERATOR)
    assert ok

def test_rbac_authorize_blocks_unauthorized():
    ok, _ = authorize("vault.read", Role.READER)
    assert ok is False

def test_rbac_unknown_capability_blocks():
    ok, _ = authorize("nonexistent.cap", Role.OPERATOR)
    assert ok is False

def test_audit_chain_append_and_verify():
    chain_append("test_event", {"key": "value"})
    chain_append("test_event_2", {"k2": "v2"})
    intact, n, msg = chain_verify()
    assert intact is True
    assert n >= 2

def test_secret_scanner_finds_aws_key():
    findings = scan_for_secrets("AKIAIOSFODNN7EXAMPLE")
    assert any(f.pattern == "AWS_ACCESS_KEY_ID" for f in findings)

def test_secret_scanner_finds_anthropic_key():
    findings = scan_for_secrets("sk-ant-api03-XYZABC123_def456ghi789jklmnop")
    assert any(f.pattern == "ANTHROPIC_API_KEY" for f in findings)

def test_secret_scanner_clean_text():
    findings = scan_for_secrets("This is clean text with no secrets.")
    assert len(findings) == 0


# ── 5. Quality Gates ────────────────────────────────────────────────────

def test_banned_phrases_detected():
    violations = banned_phrase_violations("We unlock seamless transformation.")
    assert len(violations) >= 1

def test_length_rule_pass():
    text = " ".join(["word"] * 100)
    ok, _ = length_check(text, "linkedin_post")
    assert ok is True

def test_length_rule_too_short():
    ok, _ = length_check("short", "linkedin_post")
    assert ok is False

def test_length_rule_too_long():
    text = " ".join(["word"] * 500)
    ok, _ = length_check(text, "linkedin_post")
    assert ok is False

def test_approval_request_grant():
    req = request_approval("hash123", "client", "tester")
    granted = grant_approval(req.request_id, "approver")
    assert granted.status == ApprovalStatus.APPROVED
    assert granted.approved_by == "approver"

def test_approval_reject():
    req = request_approval("h2", "doctrine", "tester")
    rejected = reject_approval(req.request_id, "approver", "not novel")
    assert rejected.status == ApprovalStatus.REJECTED


# ── 6. Config & Deploy ──────────────────────────────────────────────────

def test_feature_flags_have_8_defaults():
    assert len(DEFAULT_FLAGS) == 8

def test_set_and_get_flag():
    set_flag("enable_brier_tracking", True)
    assert get_flag("enable_brier_tracking") is True
    set_flag("enable_brier_tracking", False)
    assert get_flag("enable_brier_tracking") is False
    set_flag("enable_brier_tracking", True)  # restore

def test_blue_green_deployment():
    d = deploy_blue_green("v1.0.0-test")
    assert d.state == DeployState.GREEN
    assert d.version == "v1.0.0-test"

def test_canary_deployment():
    d = deploy_canary("v1.0.1-test", percent=10)
    assert d.state == DeployState.CANARY
    assert d.canary_pct == 10

def test_promote_deployment():
    d = deploy_blue_green("v1.0.2-test")
    promoted = promote(d.deploy_id)
    assert promoted.state == DeployState.PROMOTED

def test_rollback_deployment():
    d = deploy_blue_green("v1.0.3-test")
    rolled = rollback(d.deploy_id, reason="test rollback")
    assert rolled.state == DeployState.ROLLED_BACK


# ── 7. Multi-tenant ─────────────────────────────────────────────────────

def test_token_bucket_consumes():
    b = TokenBucket(capacity=10, refill_rate=1.0)
    ok, _ = b.consume(5.0)
    assert ok is True
    ok, wait = b.consume(10.0)  # over capacity
    assert ok is False
    assert wait > 0

def test_tenant_registration_and_quota():
    register_tenant("tenant-test", name="Test Tenant", audits_per_hour=100)
    ok, _ = consume_audit("tenant-test")
    assert ok is True
    status = quota_status("tenant-test")
    assert status["monthly_audits_used"] >= 1

def test_unknown_tenant_blocked():
    ok, reason = consume_audit("tenant-does-not-exist")
    assert ok is False
    assert "unknown tenant" in reason


# ── 8. Database ─────────────────────────────────────────────────────────

def test_db_init_creates_tables():
    p = init_db()
    assert p.exists()

def test_db_integrity_check_returns_dict():
    check = integrity_check()
    assert "sqlite_integrity_ok" in check
    assert "row_counts" in check

def test_db_audit_chain_append_persists():
    h1 = insert_audit_entry("db_test_event", {"a": 1}, prev_hash=None)
    h2 = insert_audit_entry("db_test_event_2", {"a": 2}, prev_hash=h1)
    last = get_last_audit_hash()
    assert last == h2

def test_canonical_table_count():
    assert CANONICAL_TABLE_COUNT == 7


# ── 9. SLA ──────────────────────────────────────────────────────────────

def test_sla_canonical_set():
    assert len(CANONICAL_SLAS) >= 3

def test_sla_record_event_and_report():
    record_sla_event("audit_availability_99_9", True)
    record_sla_event("audit_availability_99_9", True)
    report = promise_report()
    assert "audit_availability_99_9" in report

def test_credit_owed_when_in_breach():
    # Force a breach by recording many failures
    for _ in range(100):
        record_sla_event("audit_latency_p99_under_10s", False)
    summary = total_credit_owed(monthly_fee_usd=1000.0)
    assert summary["total_credit_usd"] > 0


# ── 10. Daemon ──────────────────────────────────────────────────────────

def test_daemon_has_9_slots():
    assert len(DEFAULT_SLOTS) == 9

def test_daemon_tick_runs_due_slots():
    d = Daemon()
    executed = d.tick()
    # On fresh daemon, all slots are immediately due (staggered 5s)
    # First slot should be due
    assert len(executed) >= 1

def test_daemon_status_shape():
    d = Daemon()
    s = d.status()
    assert s["total_slots"] == 9
    assert "slots" in s


# ── 11. Runbooks ────────────────────────────────────────────────────────

def test_8_runbooks_defined():
    assert len(RUNBOOKS) == 8

def test_runbook_lookup_by_name():
    rb = get_runbook("engine_crash")
    assert rb is not None
    assert len(rb.steps) >= 3

def test_execute_runbook_returns_result():
    result = execute_runbook("amplifier_constant_drift")
    assert "runbook" in result or "error" in result

def test_unknown_runbook_returns_error():
    result = execute_runbook("nonexistent_runbook")
    assert "error" in result


# ── 12. Adversarial Reviewer ────────────────────────────────────────────

def test_attack_vectors_count():
    assert len(ATTACK_VECTORS) == 8

def test_adversarial_review_runs_8_attacks():
    text = "We commit to ship Forge Edge by Month 8 with <50ms latency."
    review = adversarial_review(text, author_persona="claude")
    assert review.attacks_total == 8

def test_independent_reviewer_required():
    try:
        adversarial_review("text", author_persona="same",
                            reviewer_persona="same")
        assert False, "should have raised"
    except IndependentReviewerError:
        pass

def test_adversarial_review_catches_generic_slop():
    text = ("We leverage seamless cutting-edge solutions to unlock world-class "
             "synergies through holistic transformation. Thought leadership delivered.")
    review = adversarial_review(text, author_persona="claude")
    landed_vectors = [a.vector for a in review.attacks if a.landed]
    assert "median_output_or_generic_gravity" in landed_vectors

def test_adversarial_review_serializable():
    import json
    review = adversarial_review("Sample text.", author_persona="claude")
    d = review.to_dict()
    json.dumps(d)
    assert d["attacks_total"] == 8


# ── 13. Coherence Scorer ────────────────────────────────────────────────

def test_coherence_score_single_paragraph_high():
    text = "Just one paragraph here, nothing to compare to."
    assert coherence_score(text) >= 0.99

def test_coherence_score_disjoint_paragraphs_low():
    text = ("This paragraph talks about Helios Technologies and Forge Edge for HED Manufacturing.\n\n"
             "Now this paragraph discusses unrelated agricultural commodities markets in Brazil.")
    c = coherence_score(text)
    assert c < 0.5

def test_coherence_alert_threshold():
    assert COHERENCE_ALERT_THRESHOLD == 0.70


# ── 14. Outcome Observer ────────────────────────────────────────────────

def test_observe_outcome_writes_record():
    rec = observe_outcome(
        mission_id="m-test-outcome",
        engine_name="TestEngObserver",
        predicted_madz=5.0,
        realized_madz=4.5,
    )
    assert rec.engine_name == "TestEngObserver"
    assert abs(rec.delta - 0.5) < 0.01

def test_engine_weight_update_holds_with_no_history():
    update = engine_weight_update("UnknownEngineNoHistory")
    assert update["weight_delta"] == 0.0


# ── Manual runner ───────────────────────────────────────────────────────
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
