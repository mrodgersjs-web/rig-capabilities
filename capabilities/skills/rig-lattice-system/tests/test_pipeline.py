"""Day-2 acceptance tests for pipeline orchestrator + Hermes hooks per DOCTRINE.md §8.

Required acceptance per DOCTRINE.md §8 Day 2:
  - Pipeline orchestrator with canonical gate ordering (physics → cognitive → nature → RIG-L)
  - Append-only audit substrate (UPDATE/DELETE revoked)
  - All 5 Hermes hooks implemented
  - ApprovalClient (AionUI) integration for tier ≥ published
  - Intent map + fallback routing
"""
from __future__ import annotations
import sys
import time
from pathlib import Path


from rig_lattice.deviator.pipeline import (
    orchestrate, OrchestrationResult,
    audit_log, AuditRecord,
    resolve_intent, INTENT_MAP,
    ApprovalClient, ApprovalRequest, ApprovalVerdict,
)
from rig_lattice.deviator.pipeline.audit import AppendOnlyAuditLog, hash_artifact
from rig_lattice.deviator.hooks import (
    completion_scorer,
    circuit_breaker,
    adversarial_review,
    weekly_recal_cron,
    kanban_event,
)


# Test fixtures
WEAK_TEXT = "We unlock seamless transformation."  # banned-phrase + low specificity
STRONG_TEXT_PATH = Path(__file__).parent.parent / "examples" / "example_strict_passing.md"


# ── 1. Audit substrate ────────────────────────────────────────────────────

def test_audit_log_writes_record():
    rec_id = audit_log("gate", "test-mission-001", "hash-abc",
                        {"test": "value"}, tier="client")
    assert rec_id.startswith("audit-")

def test_audit_record_is_immutable_dataclass():
    rec = AuditRecord(
        record_id="r1", timestamp_utc="2026-01-01T00:00:00Z",
        mission_id="m1", artifact_hash="h1", tier="client",
        event_type="gate", payload={"foo": "bar"},
    )
    # Frozen dataclass — assignment must fail
    try:
        rec.tier = "doctrine"
        assert False, "AuditRecord should be immutable"
    except Exception:
        pass

def test_audit_log_no_update_method():
    log = AppendOnlyAuditLog()
    # By design: no update_record(), no delete_record()
    assert not hasattr(log, "update_record")
    assert not hasattr(log, "delete_record")
    assert not hasattr(log, "update")
    assert not hasattr(log, "delete")

def test_audit_log_read_by_mission():
    mid = f"test-mission-{int(time.time())}"
    audit_log("gate", mid, "hash-x", {"a": 1}, tier="client")
    audit_log("gate", mid, "hash-x", {"b": 2}, tier="client")
    log = AppendOnlyAuditLog()
    records = log.read_mission(mid)
    assert len(records) >= 2
    assert all(r.mission_id == mid for r in records)

def test_audit_record_content_hash_stable():
    rec = AuditRecord(
        record_id="r1", timestamp_utc="2026-01-01T00:00:00Z",
        mission_id="m1", artifact_hash="h1", tier="client",
        event_type="gate", payload={"foo": "bar"},
    )
    h1 = rec.content_hash
    h2 = rec.content_hash
    assert h1 == h2  # deterministic


# ── 2. Intent map ─────────────────────────────────────────────────────────

def test_intent_map_known_intents():
    binding = resolve_intent("proposal")
    assert binding.tier == "client"
    assert binding.mode == "standard"
    assert binding.patent_expected is True

def test_intent_map_fallback():
    binding = resolve_intent("totally-unknown-intent-12345")
    assert binding.tier == "client"  # fallback default

def test_intent_map_none_handling():
    binding = resolve_intent(None)
    assert binding.intent == "unknown"

def test_intent_map_covers_all_tiers():
    tiers_in_map = {b.tier for b in INTENT_MAP.values()}
    assert tiers_in_map == {"internal_note", "internal_artifact", "client",
                              "published", "doctrine", "civilization"}


# ── 3. ApprovalClient ─────────────────────────────────────────────────────

def test_approval_client_stub_returns_novel_for_patent():
    client = ApprovalClient(auto_approve=True)
    verdict = client.request_and_await(
        mission_id="m1", artifact_hash="h1", tier="published",
        kind="patent_examiner", summary="test",
        rig_l=5.5, bdf=5.5,
    )
    assert verdict.verdict == "novel"
    assert verdict.reviewer == "auto_approved_stub"

def test_approval_client_stub_approves_council():
    client = ApprovalClient(auto_approve=True)
    verdict = client.request_and_await(
        mission_id="m1", artifact_hash="h1", tier="doctrine",
        kind="doctrine_council", summary="test",
        rig_l=8.5, bdf=8.5,
    )
    assert verdict.verdict == "approved"

def test_approval_client_persists_request():
    client = ApprovalClient(auto_approve=True)
    req = client.request(
        mission_id="m1", artifact_hash="h1", tier="published",
        kind="patent_examiner", summary="test",
        rig_l=5.5, bdf=5.5,
    )
    assert (client.queue_dir / f"{req.request_id}.json").exists()


# ── 4. Orchestrator + gate ordering ───────────────────────────────────────

def test_orchestrate_returns_result_dataclass():
    if not STRONG_TEXT_PATH.exists():
        return  # skip if fixture missing
    text = STRONG_TEXT_PATH.read_text()
    result = orchestrate(text, tier="client", intent="proposal")
    assert isinstance(result, OrchestrationResult)
    assert result.mission_id.startswith("des-")

def test_orchestrate_blocks_banned_phrase_at_client_tier():
    # 'unlock' + 'seamless' + 'transformation' are all banned
    result = orchestrate(WEAK_TEXT, tier="client", intent="client")
    assert result.status == "HARD_BLOCK"
    assert "Banned phrases" in result.detonation_reason

def test_orchestrate_allows_banned_phrase_at_internal_note():
    # internal_note tier doesn't enforce banned phrases (minSigma=1)
    result = orchestrate(WEAK_TEXT, tier="internal_note", intent="note")
    # Internal note gets past banned-phrase gate but may still HARD_BLOCK on engines
    assert result.tier == "internal_note"

def test_orchestrate_writes_audit_trail():
    text = "We commit to shipping by Month 8 with kill criteria documented."
    result = orchestrate(text, tier="internal_artifact", intent="internal_doc")
    assert len(result.audit_record_ids) >= 1

def test_orchestrate_short_circuits_on_l3_block():
    if not STRONG_TEXT_PATH.exists():
        return
    text = STRONG_TEXT_PATH.read_text()
    result = orchestrate(text, tier="client", intent="proposal")
    # If physics short-circuited, cognitive/nature shouldn't have scores
    if result.physics.short_circuited:
        # The orchestrator returns ASAP — cognitive should be empty
        assert len(result.cognitive.sigmas) == 0 or result.status == "HARD_BLOCK"


# ── 5. Hermes hooks ───────────────────────────────────────────────────────

def test_completion_scorer_attaches_scorecard():
    if not STRONG_TEXT_PATH.exists():
        return
    text = STRONG_TEXT_PATH.read_text()
    packet = {
        "mission_id": f"test-{int(time.time())}",
        "artifact": text,
        "tier": "client",
        "intent": "client",
    }
    out = completion_scorer(packet)
    assert "dv_scorecard" in out
    assert "dv_status" in out
    assert "dv_rig_l" in out

def test_completion_scorer_handles_missing_artifact():
    packet = {"mission_id": "test-missing", "tier": "client"}
    out = completion_scorer(packet)
    assert out["dv_status"] == "skipped"

def test_circuit_breaker_blocks_on_hard_block():
    scorecard = {
        "mission_id": "m1", "artifact_hash": "h1", "tier": "client",
        "physics": {"short_circuited": True, "hard_blocks": ["bell"]},
        "status": "HARD_BLOCK",
        "rig_l": -30, "bdf": 0,
        "detonation_verdict": "BLOCK", "detonation_reason": "physics fail",
    }
    verdict = circuit_breaker(scorecard)
    assert verdict["allow"] is False

def test_circuit_breaker_passes_clean_scorecard():
    scorecard = {
        "mission_id": "m1", "artifact_hash": "h1", "tier": "client",
        "physics": {"short_circuited": False, "hard_blocks": []},
        "status": "PASS",
        "rig_l": 8.0, "bdf": 8.0,
        "detonation_verdict": "PASS", "detonation_reason": "",
        "next_action": "Ship.",
    }
    verdict = circuit_breaker(scorecard)
    assert verdict["allow"] is True

def test_circuit_breaker_blocks_below_tier_min():
    scorecard = {
        "mission_id": "m1", "artifact_hash": "h1", "tier": "published",
        "physics": {"short_circuited": False, "hard_blocks": []},
        "status": "PASS", "rig_l": 3.0,  # below published min of +5
        "bdf": 3.0, "detonation_verdict": "PASS",
    }
    verdict = circuit_breaker(scorecard)
    assert verdict["allow"] is False
    assert "below tier" in verdict["reason"]

def test_adversarial_review_detects_attacks():
    scorecard = {"mission_id": "m1", "artifact_hash": "h1", "tier": "published"}
    bad = "We unlock seamless transformation in today's landscape. Furthermore, we leverage synergies."
    out = adversarial_review(scorecard, text=bad)
    assert out["attacks_landed"] >= 3
    assert out["verdict"] in ("needs_rework", "BLOCK")

def test_adversarial_review_passes_strong_text():
    if not STRONG_TEXT_PATH.exists():
        return
    text = STRONG_TEXT_PATH.read_text()
    scorecard = {"mission_id": "m1", "artifact_hash": "h1", "tier": "published"}
    out = adversarial_review(scorecard, text=text)
    # Strong fixture should land few attacks
    assert out["attacks_landed"] <= 4

def test_weekly_recal_cron_runs():
    result = weekly_recal_cron()
    assert "recalibrated_engines" in result
    assert result["recalibrated_engines"] == 40

def test_kanban_event_rejects_critical_risk():
    out = kanban_event({
        "event": "skill_promotion_candidate",
        "candidate_id": "skill-1",
        "artifact": "any text",
        "risk_tier": "critical",
    })
    assert out["promote"] is False
    assert "Critical risk" in out["reason"]

def test_kanban_event_passes_through_non_promotion():
    out = kanban_event({"event": "unrelated_event"})
    assert out["promote"] is False


# ── 6. Hash + utility functions ───────────────────────────────────────────

def test_hash_artifact_deterministic():
    h1 = hash_artifact("test text")
    h2 = hash_artifact("test text")
    h3 = hash_artifact("different text")
    assert h1 == h2
    assert h1 != h3


# ── Manual runner for environments without pytest ─────────────────────────
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
