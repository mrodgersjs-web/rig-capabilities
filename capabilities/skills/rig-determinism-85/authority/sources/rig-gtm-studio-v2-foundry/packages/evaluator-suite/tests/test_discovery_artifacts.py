"""Contract tests for deterministic discovery-loop artifacts."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def loop():
    path = Path("packages/discovery-loop/src/loop.py")
    spec = importlib.util.spec_from_file_location("discovery_loop", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _claim(claim_id: str, text: str) -> dict:
    return {
        "claim_id": claim_id,
        "video_id": "video00001",
        "channel_id": "channel-1",
        "text": text,
        "epistemic_type": "testable_procedure",
        "start_time": 0,
        "end_time": 1,
        "transcript_hash": "transcript-hash",
    }


def test_capability_delta_is_deterministic_and_content_bound(loop):
    claim = _claim("c1", "First do this")
    args = ([claim], [], [{**claim, "delta_class": "NOVEL"}], "baseline-a", ["v1"])
    first = loop.generate_capability_delta(*args)
    second = loop.generate_capability_delta(*args)
    assert first == second

    changed_claim = _claim("c1", "First do something different")
    changed = loop.generate_capability_delta(
        [changed_claim],
        [],
        [{**changed_claim, "delta_class": "NOVEL"}],
        "baseline-a",
        ["v1"],
    )
    changed_baseline = loop.generate_capability_delta(*args[:-2], "baseline-b", ["v1"])
    assert changed["delta_id"] != first["delta_id"]
    assert changed_baseline["delta_id"] != first["delta_id"]
    changed_provenance = {
        **claim,
        "transcript_hash": "different-transcript-hash",
        "delta_class": "NOVEL",
    }
    changed_provenance_artifact = loop.generate_capability_delta(
        [{k: v for k, v in changed_provenance.items() if k != "delta_class"}],
        [],
        [changed_provenance],
        "baseline-a",
        ["v1"],
    )
    assert changed_provenance_artifact["delta_id"] != first["delta_id"]


def test_upgrade_proposal_is_bound_to_candidates_and_evaluations(loop):
    capabilities = {
        "lessons": [],
        "procedures": [],
        "harnesses": [],
        "skills": [{
            "skill_id": "s1",
            "name": "Skill",
            "confidence": 0.8,
            "content_hash": "candidate-a",
        }],
    }
    evaluations = [{"artifact_id": "s1", "status": "pass"}]
    first = loop.generate_upgrade_proposal(capabilities, evaluations, "delta-a", "1.0.0")
    assert first == loop.generate_upgrade_proposal(
        capabilities, evaluations, "delta-a", "1.0.0"
    )

    changed_capabilities = {**capabilities, "skills": [{
        **capabilities["skills"][0], "content_hash": "candidate-b"
    }]}
    changed_candidate = loop.generate_upgrade_proposal(
        changed_capabilities, evaluations, "delta-a", "1.0.0"
    )
    changed_evaluation = loop.generate_upgrade_proposal(
        capabilities, [{"artifact_id": "s1", "status": "fail"}], "delta-a", "1.0.0"
    )
    assert changed_candidate["proposal_id"] != first["proposal_id"]
    assert changed_evaluation["proposal_id"] != first["proposal_id"]
    changed_evaluation_detail = loop.generate_upgrade_proposal(
        capabilities,
        [{"artifact_id": "s1", "status": "pass", "evidence_hash": "changed"}],
        "delta-a",
        "1.0.0",
    )
    assert changed_evaluation_detail["proposal_id"] != first["proposal_id"]


def test_missing_baseline_blocks_before_discovery(loop, tmp_path):
    with pytest.raises(FileNotFoundError):
        loop.run_discovery_loop(
            "channel-1",
            existing_corpus_path=str(tmp_path / "missing.json"),
            dry_run=True,
        )


def test_atomic_artifact_write_leaves_no_temp_file(loop, tmp_path):
    path = tmp_path / "artifact.json"
    artifact = {"id": "a1", "value": 1}
    loop._write_artifact(path, artifact)
    assert path.exists()
    assert not path.with_suffix(".json.tmp").exists()
    assert path.read_bytes() == loop._canonical_bytes(artifact) + b"\n"
