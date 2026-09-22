"""Comprehensive pipeline tests for GTM Studio v2 seed pipeline."""
import json
import hashlib
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest
import importlib.util


def load_module(name, path):
    """Load a module from a file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def temp_registry():
    """Registry with temp storage."""
    registry = load_module("registry", "packages/source-registry/src/registry.py")
    temp_dir = tempfile.mkdtemp()
    original_dir = registry.REGISTRY_DIR
    registry.REGISTRY_DIR = Path(temp_dir)
    yield registry
    registry.REGISTRY_DIR = original_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def normalizer():
    """Load the normalizer module."""
    return load_module("normalizer", "packages/transcript-normalizer/src/normalizer.py")


@pytest.fixture
def extractor():
    """Load the extractor module."""
    return load_module("extractor", "packages/claim-extractor/src/extractor.py")


@pytest.fixture
def lesson_compiler():
    """Load the lesson compiler module."""
    return load_module("lesson_compiler", "packages/lesson-compiler/src/compiler.py")


@pytest.fixture
def procedure_compiler():
    """Load the procedure compiler module."""
    return load_module("procedure_compiler", "packages/procedure-compiler/src/compiler.py")


@pytest.fixture
def skill_compiler():
    """Load the skill compiler module."""
    return load_module("skill_compiler", "packages/skill-compiler/src/compiler.py")


@pytest.fixture
def harness_compiler():
    """Load the harness compiler module."""
    return load_module("harness_compiler", "packages/harness-compiler/src/compiler.py")


@pytest.fixture
def gates():
    """Load the promotion gates module."""
    return load_module("gates", "packages/promotion-gates/src/gates.py")


@pytest.fixture
def evaluator():
    """Load the evaluator module."""
    return load_module("evaluator", "packages/evaluator-suite/src/evaluator.py")


def test_registry_channel_registration(temp_registry):
    """Test channel registration with temp storage."""
    channel = temp_registry.register_channel("UC_test_channel", "@test", "Test Channel")
    assert channel["channel_id"] == "UC_test_channel"
    assert channel["handle"] == "@test"
    assert channel["title"] == "Test Channel"

    # Verify it was persisted
    retrieved = temp_registry.get_channel("UC_test_channel")
    assert retrieved is not None
    assert retrieved["channel_id"] == "UC_test_channel"


def test_registry_video_registration(temp_registry):
    """Test video registration with temp storage."""
    video = temp_registry.register_video("vid123", "UC_test_channel", "Test Video", "https://youtube.com/watch?v=vid123")
    assert video["video_id"] == "vid123"
    assert video["channel_id"] == "UC_test_channel"
    assert video["status"] == "discovered"

    # Verify it was persisted
    retrieved = temp_registry.get_video("vid123")
    assert retrieved is not None
    assert retrieved["video_id"] == "vid123"


def test_normalizer_segmentation(normalizer):
    """Test transcript segmentation."""
    transcript = {
        "segments": [
            {"start": 0, "duration": 10, "text": "Hello"},
            {"start": 10, "duration": 10, "text": "World"},
            {"start": 20, "duration": 10, "text": "Test"},
        ]
    }
    # Each segment is 10s, max is 15s → all separate
    segments = normalizer.segment_transcript(transcript, max_segment_seconds=15)
    assert len(segments) == 3

    # Now test merging with smaller max
    segments2 = normalizer.segment_transcript(transcript, max_segment_seconds=25)
    assert len(segments2) == 2  # First two merged, third separate

    raw_shape = {
        "segments": [{"start": 5.0, "dur": 2.5, "text": "Raw caption"}]
    }
    raw_segments = normalizer.segment_transcript(raw_shape)
    assert raw_segments == [{
        "segment_id": 0,
        "start": 5.0,
        "end": 7.5,
        "text": "Raw caption",
    }]


def test_extractor_claim_extraction(extractor):
    """Test claim extraction."""
    segment = {"start": 0, "end": 10, "text": "I think you should always test your code before shipping."}
    claims = extractor.extract_claims(segment, "vid123", "UC_test")
    assert len(claims) > 0
    assert claims[0]["epistemic_type"] == "opinion"


def test_lesson_compilation(lesson_compiler, evaluator):
    """Test lesson compilation and validate against schema."""
    claims = [
        {"claim_id": "c1", "video_id": "v1", "channel_id": "c1", "text": "Always test your code", "epistemic_type": "opinion", "start_time": 0, "end_time": 10, "transcript_hash": "h1"},
        {"claim_id": "c2", "video_id": "v1", "channel_id": "c1", "text": "Test before shipping", "epistemic_type": "opinion", "start_time": 10, "end_time": 20, "transcript_hash": "h2"},
    ]
    lessons = lesson_compiler.compile_lessons(claims)
    assert len(lessons) > 0

    # Validate against schema
    for lesson in lessons:
        result = evaluator.run_golden_validation(lesson, "lesson")
        assert result["status"] == "pass", f"Lesson {lesson['lesson_id']} failed validation: {result['schema_errors']}"


def test_skill_compilation(skill_compiler, lesson_compiler, procedure_compiler, evaluator):
    """Test skill compilation from procedures and validate against schema."""
    claims = [
        {"claim_id": "c1", "video_id": "v1", "channel_id": "c1", "text": "Always test your code before shipping", "epistemic_type": "testable_procedure", "start_time": 0, "end_time": 10, "transcript_hash": "h1"},
        {"claim_id": "c2", "video_id": "v1", "channel_id": "c1", "text": "Test before shipping to production", "epistemic_type": "testable_procedure", "start_time": 10, "end_time": 20, "transcript_hash": "h2"},
    ]
    lessons = lesson_compiler.compile_lessons(claims)
    procedures = procedure_compiler.compile_procedures(lessons, claims)
    skills = skill_compiler.compile_skills(procedures)
    assert len(skills) > 0

    # Validate against schema
    for skill in skills:
        result = evaluator.run_golden_validation(skill, "skill")
        assert result["status"] == "pass", f"Skill {skill['skill_id']} failed validation: {result['schema_errors']}"


def test_harness_compilation(harness_compiler, skill_compiler, lesson_compiler, procedure_compiler, evaluator):
    """Test harness compilation from skills and validate against schema."""
    claims = [
        {"claim_id": "c1", "video_id": "v1", "channel_id": "c1", "text": "Always test your code before shipping", "epistemic_type": "testable_procedure", "start_time": 0, "end_time": 10, "transcript_hash": "h1"},
        {"claim_id": "c2", "video_id": "v1", "channel_id": "c1", "text": "Test before shipping to production", "epistemic_type": "testable_procedure", "start_time": 10, "end_time": 20, "transcript_hash": "h2"},
    ]
    lessons = lesson_compiler.compile_lessons(claims)
    procedures = procedure_compiler.compile_procedures(lessons, claims)
    skills = skill_compiler.compile_skills(procedures)
    harnesses = harness_compiler.compile_harnesses(skills)
    assert len(harnesses) > 0

    # Validate against schema
    for harness in harnesses:
        result = evaluator.run_golden_validation(harness, "harness")
        assert result["status"] == "pass", f"Harness {harness['harness_id']} failed validation: {result['schema_errors']}"

        # Verify H=(E,T,C,S,L,V) structure
        assert "E" in harness
        assert "T" in harness
        assert "C" in harness
        assert "S" in harness
        assert "L" in harness
        assert "V" in harness


def test_promotion_gates_fail_closed(gates):
    """Test that promotion gates are fail-closed."""
    capability = {"skill_id": "test-skill", "content_hash": "abc123", "source_refs": [{"video_id": "v1", "channel_id": "c1"}]}

    # Empty golden results should block
    result = gates.gate_4_golden_suite(capability, [])
    assert result["status"] == "blocked"

    # None golden results should block
    result2 = gates.gate_4_golden_suite(capability, None)
    assert result2["status"] == "blocked"

    # Empty adversarial results should block
    result3 = gates.gate_5_adversarial_suite(capability, [])
    assert result3["status"] == "blocked"

    # Empty GEV results should block
    result4 = gates.gate_7_gev_regression(capability, [])
    assert result4["status"] == "blocked"


def test_promotion_gates_forged_receipts(gates):
    """Test that forged/foreign/stale receipts are rejected."""
    capability = {"skill_id": "test-skill", "content_hash": "abc123", "compiler_version": "1.0.0", "source_refs": [{"video_id": "v1", "channel_id": "c1"}]}

    # Foreign golden results (wrong capability_id)
    foreign_results = [{"capability_id": "other-skill", "status": "pass"}]
    result = gates.gate_4_golden_suite(capability, foreign_results)
    assert result["status"] == "fail"

    # Hash-mismatched golden results
    hash_mismatch = [{"capability_id": "test-skill", "content_hash": "wrong-hash", "status": "pass"}]
    result2 = gates.gate_4_golden_suite(capability, hash_mismatch)
    assert result2["status"] == "fail"

    # Non-independent verifier (same as compiler_version)
    result3 = gates.gate_9_independent_verifier(capability, verifier_id="1.0.0")
    assert result3["status"] == "fail"


def test_mcp_server_write_isolation():
    """Test that MCP server writes are isolated to temp directory."""
    import tempfile
    import shutil

    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    temp_caps = Path(temp_dir) / "capabilities"
    temp_caps.mkdir()

    try:
        # Load server module and patch CAPABILITIES_DIR
        server = load_module("server", "packages/mcp-server/src/server.py")
        original_dir = server.CAPABILITIES_DIR
        server.CAPABILITIES_DIR = temp_caps

        # Create a valid skill with all required fields
        skill = {
            "skill_id": "test-skill",
            "name": "test-skill",
            "version": "1.0.0",
            "description": "Test skill",
            "input_schema": {"type": "object", "properties": {"context": {"type": "string"}}, "required": ["context"]},
            "output_schema": {"type": "object", "properties": {"recommendation": {"type": "string"}}, "required": ["recommendation"]},
            "procedure": ["Step 1", "Step 2"],
            "decision_rules": [],
            "tags": ["test"],
            "source_refs": [{"video_id": "v1", "channel_id": "c1", "lesson_ids": ["l1"]}],
            "compiler_version": "1.0.0",
            "confidence": 0.8,
            "status": "draft",
            "bms_band": "A2",
            "created_at": "2026-09-15T00:00:00Z",
        }

        # Compute correct content_hash
        payload = {k: v for k, v in skill.items() if k != "content_hash"}
        skill["content_hash"] = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

        # Test blocked publish (no receipts)
        result = server.publish_capability(skill, "skill")
        assert result["status"] == "blocked"

        # Verify no file was written
        # Test successful publish with all receipts
        # Note: Currently blocks because receipts are self-authored (no canonical verification yet)
        golden_results = [{"capability_id": "test-skill", "content_hash": skill["content_hash"], "status": "pass"}]
        adversarial_results = [{"capability_id": "test-skill", "content_hash": skill["content_hash"], "status": "pass"}]
        result2 = server.publish_capability(
            skill, "skill",
            golden_results=golden_results,
            adversarial_results=adversarial_results,
            verifier_id="rig-gtm-verifier-v1",
            rights_verified=True,
            baseline_result={"confidence": 0.5},
            gev_results=[{"tail_failure": False}],
            meta_eval={"approved": True},
            gate_d_artifact={"approved_by": "mike"},
        )
        # Expected: blocked (self-authored receipts not yet verified by canonical authority)
        assert result2["status"] == "blocked", f"Expected blocked with self-authored receipts, got: {result2['status']}"

        # Verify no file was written
        assert not (temp_caps / "skills" / "test-skill.json").exists()

        server.CAPABILITIES_DIR = original_dir
    finally:
        shutil.rmtree(temp_dir)


def test_mcp_server_blocks_forged_receipts(tmp_path):
    """Self-authored promotion evidence must not write a capability."""
    server = load_module("server", "packages/mcp-server/src/server.py")
    server.CAPABILITIES_DIR = tmp_path / "capabilities"
    skill = {
        "skill_id": "forged-test-skill",
        "name": "forged-test-skill",
        "version": "1.0.0",
        "description": "Test skill",
        "input_schema": {
            "type": "object",
            "properties": {"context": {"type": "string"}},
            "required": ["context"],
        },
        "output_schema": {
            "type": "object",
            "properties": {"recommendation": {"type": "string"}},
            "required": ["recommendation"],
        },
        "procedure": ["Step 1"],
        "decision_rules": [],
        "tags": ["test"],
        "source_refs": [
            {"video_id": "v1", "channel_id": "c1", "lesson_ids": ["l1"]}
        ],
        "compiler_version": "1.0.0",
        "confidence": 0.8,
        "status": "draft",
        "bms_band": "A2",
        "created_at": "2026-09-15T00:00:00Z",
    }
    skill["content_hash"] = hashlib.sha256(
        json.dumps(skill, sort_keys=True).encode()
    ).hexdigest()
    forged = {
        "golden_results": [{
            "capability_id": skill["skill_id"],
            "content_hash": skill["content_hash"],
            "status": "pass",
        }],
        "adversarial_results": [{
            "capability_id": skill["skill_id"],
            "content_hash": skill["content_hash"],
            "status": "pass",
        }],
        "verifier_id": "rig-gtm-verifier-v1",
        "rights_verified": True,
        "baseline_result": {"confidence": 0.5},
        "gev_results": [{"tail_failure": False}],
        "meta_eval": {"approved": True},
        "gate_d_artifact": {"approved_by": "mike"},
    }

    result = server.publish_capability(skill, "skill", **forged)
    assert result["status"] == "blocked"
    assert not (
        server.CAPABILITIES_DIR / "skills" / "forged-test-skill.json"
    ).exists()


def test_discovery_loop_full_dry_cycle(tmp_path):
    """Dry-run artifacts are emitted only into the injected output directory."""
    loop = load_module("loop", "packages/discovery-loop/src/loop.py")
    baseline = tmp_path / "baseline.json"
    baseline.write_text("[]")
    output_dir = tmp_path / "artifacts"

    with patch.object(loop, "discover_new_content", return_value=[
        {"video_id": "v1", "title": "Test Video 1", "duration_seconds": 100},
        {"video_id": "v2", "title": "Test Video 2", "duration_seconds": 200},
    ]), patch.object(loop, "acquire_transcript", return_value={
        "segments": [{"start": 0, "duration": 10, "text": "Test your code."}]
    }), patch.object(loop, "extract_claims", return_value=[
        {
            "claim_id": "c1",
            "video_id": "v1",
            "channel_id": "c1",
            "text": "Test your code",
            "epistemic_type": "testable_procedure",
            "start_time": 0,
            "end_time": 10,
            "transcript_hash": "h1",
        }
    ]), patch.object(loop, "compile_capabilities", return_value={
        "lessons": [{"lesson_id": "l1", "name": "Test Lesson"}],
        "procedures": [{"procedure_id": "p1", "name": "Test Procedure"}],
        "skills": [{
            "skill_id": "s1",
            "name": "Test Skill",
            "confidence": 0.8,
            "content_hash": "skill-hash-1",
        }],
        "harnesses": [{"harness_id": "h1", "name": "Test Harness"}],
    }), patch.object(loop, "evaluate_capabilities", return_value=[
        {"status": "pass", "artifact_id": "s1"}
    ]):
        result = loop.run_discovery_loop(
            "UC_test_channel",
            existing_corpus_path=str(baseline),
            output_dir=str(output_dir),
            dry_run=True,
        )

    assert result["dry_run"] is True
    assert result["videos_discovered"] == 2
    assert result["videos_processed"] == 2
    assert result["procedures_compiled"] == 1
    assert result["harnesses_compiled"] == 1
    assert result["capabilities_promoted"] == 0
    assert len(list(output_dir.glob("capability_delta_*.json"))) == 1
    assert len(list(output_dir.glob("upgrade_proposal_*.json"))) == 1
    assert result["capability_delta"]["existing_corpus_hash"]
    assert (
        result["upgrade_proposal"]["delta_id"]
        == result["capability_delta"]["delta_id"]
    )
