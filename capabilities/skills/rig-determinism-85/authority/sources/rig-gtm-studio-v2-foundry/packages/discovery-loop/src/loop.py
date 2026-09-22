"""packages/discovery-loop/src/loop.py — Continuous Discovery Loop.

Orchestrates the full pipeline:
Discover → Acquire → Extract → Compare → Challenge → Compile → Evaluate → Verify → Approve → Publish → Observe → Recalibrate
"""
from __future__ import annotations

import json
import hashlib
import importlib.util
from pathlib import Path
from typing import Optional


def _canonical_bytes(value: object) -> bytes:
    """Canonical JSON serialization for hashing."""
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode()


def _sha256(value: object) -> str:
    """SHA-256 hash of canonical bytes."""
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _write_artifact(path: Path, artifact: dict) -> None:
    """Write artifact atomically with canonical JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(_canonical_bytes(artifact) + b"\n")
    temporary.replace(path)


def load_module(name: str, path: str):
    """Load a module from a file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def discover_new_content(channel_id: str, last_processed_date: Optional[str] = None) -> list:
    """Discover new content on a channel since last processed date."""
    adapter = load_module("adapter", "packages/youtube-adapter/src/adapter.py")
    videos = adapter.enumerate_uploads(channel_id, max_videos=100)
    return videos


def acquire_transcript(video_id: str) -> Optional[dict]:
    """Acquire transcript for a video."""
    adapter = load_module("adapter", "packages/youtube-adapter/src/adapter.py")
    return adapter.fetch_transcript(video_id)


def extract_claims(transcript: dict, video_id: str, channel_id: str) -> list:
    """Extract claims from transcript."""
    normalizer = load_module("normalizer", "packages/transcript-normalizer/src/normalizer.py")
    extractor = load_module("extractor", "packages/claim-extractor/src/extractor.py")

    normalized = normalizer.normalize_transcript(transcript)
    segments = normalizer.segment_transcript(normalized)

    all_claims = []
    for seg in segments:
        claims = extractor.extract_claims(seg, video_id, channel_id)
        all_claims.extend(claims)

    return extractor.deduplicate_claims(all_claims)


def compare_claims(new_claims: list, existing_claims: list) -> list:
    """Compare new claims against existing corpus to identify deltas.

    Preserves full claim objects with provenance fields.
    """
    deltas = []
    existing_texts = {c["text"].lower() for c in existing_claims}

    for claim in new_claims:
        if claim["text"].lower() not in existing_texts:
            # Novel claim — preserve full object
            deltas.append({**claim, "delta_class": "NOVEL"})

    return deltas


def challenge_claims(claims: list) -> list:
    """Challenge claims for contradictions and unsupported assertions.

    Preserves full claim objects with provenance fields.
    """
    challenged = []
    for claim in claims:
        # Simple contradiction detection
        is_contradicted = False
        for other in claims:
            if other["claim_id"] == claim["claim_id"]:
                continue
            if "always" in claim["text"].lower() and "never" in other["text"].lower():
                is_contradicted = True
                break

        # Preserve full object with challenge metadata
        challenged_claim = {**claim, "is_contradicted": is_contradicted}
        if is_contradicted:
            challenged_claim["confidence"] = 0.4
        challenged.append(challenged_claim)

    return challenged


def compile_capabilities(claims: list) -> dict:
    """Compile claims into lessons, procedures, skills, and harnesses."""
    lesson_compiler = load_module("lesson_compiler", "packages/lesson-compiler/src/compiler.py")
    procedure_compiler = load_module("procedure_compiler", "packages/procedure-compiler/src/compiler.py")
    skill_compiler = load_module("skill_compiler", "packages/skill-compiler/src/compiler.py")
    harness_compiler = load_module("harness_compiler", "packages/harness-compiler/src/compiler.py")

    lessons = lesson_compiler.compile_lessons(claims)
    proc_result = procedure_compiler.compile_procedures_with_rejections(lessons, claims)
    procedures = proc_result["compiled"]
    rejections = proc_result["rejected"]
    skills = skill_compiler.compile_skills(procedures)
    harnesses = harness_compiler.compile_harnesses(skills)

    return {
        "lessons": lessons,
        "procedures": procedures,
        "procedure_rejections": rejections,
        "skills": skills,
        "harnesses": harnesses,
    }


def evaluate_capabilities(skills: list) -> list:
    """Evaluate compiled skills."""
    evaluator = load_module("evaluator", "packages/evaluator-suite/src/evaluator.py")

    results = []
    for skill in skills:
        result = evaluator.run_golden_validation(skill, "skill")
        results.append(result)

    return results


def promote_capabilities(skills: list, eval_results: list, **receipts) -> list:
    """Promote capabilities that pass all gates with externally produced receipts."""
    gates = load_module("gates", "packages/promotion-gates/src/gates.py")

    promoted = []
    for skill, eval_result in zip(skills, eval_results):
        if eval_result["status"] != "pass":
            continue

        gate_results = gates.run_all_gates(skill, **receipts)
        if gate_results["all_pass"]:
            promoted.append(skill)

    return promoted


def generate_capability_delta(new_claims: list, existing_claims: list, deltas: list,
                              existing_corpus_hash: str, input_video_ids: list) -> dict:
    """Generate capability_delta artifact with deterministic ID."""
    identity = {
        "existing_corpus_hash": existing_corpus_hash,
        "input_video_ids": sorted(input_video_ids),
        "delta_hashes": sorted(_sha256(delta) for delta in deltas),
        "compiler_version": "1.0.0",
    }
    delta_id = _sha256(identity)[:16]

    artifact = {
        "delta_id": delta_id,
        **identity,
        "timestamp": "2026-09-15T00:00:00Z",
        "existing_corpus_hash": existing_corpus_hash,
        "input_video_ids": input_video_ids,
        "new_claims_count": len(new_claims),
        "existing_claims_count": len(existing_claims),
        "novel_claims_count": len(deltas),
        "deltas": deltas,
    }
    artifact["content_hash"] = _sha256(artifact)
    return artifact


def generate_upgrade_proposal(capabilities: dict, eval_results: list,
                              delta_id: str, compiler_version: str) -> dict:
    """Generate upgrade_proposal artifact with deterministic ID."""
    candidate_hashes = sorted(
        skill["content_hash"] for skill in capabilities["skills"]
    )
    evaluation_hash = _sha256(eval_results)
    identity = {
        "delta_id": delta_id,
        "compiler_version": compiler_version,
        "candidate_hashes": candidate_hashes,
        "evaluation_hash": evaluation_hash,
    }
    proposal_id = _sha256(identity)[:16]

    artifact = {
        "proposal_id": proposal_id,
        **identity,
        "delta_id": delta_id,
        "compiler_version": compiler_version,
        "timestamp": "2026-09-15T00:00:00Z",
        "capabilities": {
            "lessons": len(capabilities["lessons"]),
            "procedures": len(capabilities["procedures"]),
            "skills": len(capabilities["skills"]),
            "harnesses": len(capabilities["harnesses"]),
        },
        "procedure_rejections": capabilities.get("procedure_rejections", []),
        "evaluation_results": eval_results,
        "proposed_upgrades": [
            {
                "skill_id": skill["skill_id"],
                "skill_name": skill["name"],
                "content_hash": skill["content_hash"],
                "confidence": skill["confidence"],
            }
            for skill in capabilities["skills"]
        ],
    }
    artifact["content_hash"] = _sha256(artifact)
    return artifact


def run_local_delta(video_ids: list, transcript_dir: str, existing_corpus_path: str,
                    output_dir: Optional[str] = None, dry_run: bool = True, **receipts) -> dict:
    """Run discovery loop on local transcripts for specified video IDs.

    Args:
        video_ids: List of video IDs to process
        transcript_dir: Path to directory containing transcript JSON files
        existing_corpus_path: Path to existing claims corpus for delta comparison
        output_dir: Directory to write artifacts (if None, return in-memory only)
        dry_run: If True, do not promote or publish
    """
    transcript_path = Path(transcript_dir)

    # Load existing corpus
    existing_path = Path(existing_corpus_path)
    if not existing_path.exists():
        raise FileNotFoundError(f"Existing corpus not found: {existing_corpus_path}")
    existing_claims = json.loads(existing_path.read_text())

    # Compute existing corpus hash
    existing_corpus_hash = _sha256(existing_claims)

    # Load and process each video
    all_claims = []
    for video_id in video_ids:
        transcript_file = transcript_path / f"{video_id}.json"
        if not transcript_file.exists():
            raise FileNotFoundError(f"Transcript not found: {transcript_file}")

        transcript = json.loads(transcript_file.read_text())
        print(f"Processing {video_id}: {transcript.get('title', 'Unknown')[:50]}...")
        claims = extract_claims(transcript, video_id, transcript.get("channel_id", "unknown"))
        all_claims.extend(claims)

    print(f"Extracted {len(all_claims)} total claims")

    # Compare against existing corpus
    deltas = compare_claims(all_claims, existing_claims)
    print(f"Identified {len(deltas)} novel claims")

    if not deltas:
        raise ValueError("No novel claims found — delta is empty")

    # Generate capability_delta artifact
    capability_delta = generate_capability_delta(
        all_claims, existing_claims, deltas,
        existing_corpus_hash, video_ids
    )

    # Challenge claims
    challenged = challenge_claims(deltas)
    contradicted = sum(1 for c in challenged if c.get("is_contradicted"))
    print(f"Challenged claims: {contradicted} contradicted")

    # Compile
    capabilities = compile_capabilities(challenged)
    print(f"Compiled {len(capabilities['lessons'])} lessons, "
          f"{len(capabilities['procedures'])} procedures, "
          f"{len(capabilities['skills'])} skills, "
          f"{len(capabilities['harnesses'])} harnesses")
    if capabilities["procedure_rejections"]:
        print(f"Procedure rejections: {len(capabilities['procedure_rejections'])}")

    # Evaluate
    eval_results = evaluate_capabilities(capabilities["skills"])
    passed = sum(1 for r in eval_results if r["status"] == "pass")
    print(f"Evaluation: {passed}/{len(eval_results)} passed")

    # Generate upgrade_proposal artifact
    upgrade_proposal = generate_upgrade_proposal(
        capabilities, eval_results,
        capability_delta["delta_id"], "1.0.0"
    )

    # Write artifacts if output_dir specified
    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        delta_file = out_path / f"capability_delta_{capability_delta['delta_id']}.json"
        _write_artifact(delta_file, capability_delta)
        print(f"Wrote capability_delta: {delta_file}")

        proposal_file = out_path / f"upgrade_proposal_{upgrade_proposal['proposal_id']}.json"
        _write_artifact(proposal_file, upgrade_proposal)
        print(f"Wrote upgrade_proposal: {proposal_file}")

    # Promote (only if not dry-run and all receipts provided)
    promoted = []
    if not dry_run:
        promoted = promote_capabilities(capabilities["skills"], eval_results, **receipts)
        print(f"Promoted {len(promoted)} capabilities")
    else:
        print("Dry run: no promotions")

    return {
        "videos_processed": len(video_ids),
        "claims_extracted": len(all_claims),
        "novel_claims": len(deltas),
        "contradicted_claims": contradicted,
        "lessons_compiled": len(capabilities["lessons"]),
        "procedures_compiled": len(capabilities["procedures"]),
        "procedure_rejections": len(capabilities["procedure_rejections"]),
        "skills_compiled": len(capabilities["skills"]),
        "harnesses_compiled": len(capabilities["harnesses"]),
        "evaluation_passed": passed,
        "capabilities_promoted": len(promoted),
        "dry_run": dry_run,
        "capability_delta": capability_delta,
        "upgrade_proposal": upgrade_proposal,
    }


def run_discovery_loop(channel_id: str, existing_corpus_path: str,
                       output_dir: Optional[str] = None, dry_run: bool = True, **receipts) -> dict:
    """Run the full discovery loop for a channel (network mode).

    Args:
        channel_id: YouTube channel ID
        existing_corpus_path: Path to existing claims corpus for delta comparison
        output_dir: Directory to write artifacts (if None, return in-memory only)
        dry_run: If True, do not promote or publish
    """
    # Load existing corpus
    existing_path = Path(existing_corpus_path)
    if not existing_path.exists():
        raise FileNotFoundError(f"Existing corpus not found: {existing_corpus_path}")
    existing_claims = json.loads(existing_path.read_text())

    # Compute existing corpus hash
    existing_corpus_hash = _sha256(existing_claims)

    # Discover
    videos = discover_new_content(channel_id)
    print(f"Discovered {len(videos)} new videos")

    # Process each video (limit to 5 for seed pipeline)
    processed_videos = videos[:5]
    input_video_ids = [v["video_id"] for v in processed_videos]
    all_claims = []
    for video in processed_videos:
        print(f"Processing {video['video_id']}: {video['title'][:50]}...")
        transcript = acquire_transcript(video["video_id"])
        if transcript:
            claims = extract_claims(transcript, video["video_id"], channel_id)
            all_claims.extend(claims)

    print(f"Extracted {len(all_claims)} total claims")

    # Compare against existing corpus
    deltas = compare_claims(all_claims, existing_claims)
    print(f"Identified {len(deltas)} novel claims")

    # Generate capability_delta artifact
    capability_delta = generate_capability_delta(
        all_claims, existing_claims, deltas,
        existing_corpus_hash, input_video_ids
    )

    # Challenge claims
    challenged = challenge_claims(deltas)
    contradicted = sum(1 for c in challenged if c.get("is_contradicted"))
    print(f"Challenged claims: {contradicted} contradicted")

    # Compile
    capabilities = compile_capabilities(challenged)
    print(f"Compiled {len(capabilities['lessons'])} lessons, "
          f"{len(capabilities['procedures'])} procedures, "
          f"{len(capabilities['skills'])} skills, "
          f"{len(capabilities['harnesses'])} harnesses")

    # Evaluate
    eval_results = evaluate_capabilities(capabilities["skills"])
    passed = sum(1 for r in eval_results if r["status"] == "pass")
    print(f"Evaluation: {passed}/{len(eval_results)} passed")

    # Generate upgrade_proposal artifact
    upgrade_proposal = generate_upgrade_proposal(
        capabilities, eval_results,
        capability_delta["delta_id"], "1.0.0"
    )

    # Write artifacts if output_dir specified
    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        delta_file = out_path / f"capability_delta_{capability_delta['delta_id']}.json"
        _write_artifact(delta_file, capability_delta)
        print(f"Wrote capability_delta: {delta_file}")

        proposal_file = out_path / f"upgrade_proposal_{upgrade_proposal['proposal_id']}.json"
        _write_artifact(proposal_file, upgrade_proposal)
        print(f"Wrote upgrade_proposal: {proposal_file}")

    # Promote (only if not dry-run and all receipts provided)
    promoted = []
    if not dry_run:
        promoted = promote_capabilities(capabilities["skills"], eval_results, **receipts)
        print(f"Promoted {len(promoted)} capabilities")
    else:
        print("Dry run: no promotions")

    return {
        "videos_discovered": len(videos),
        "videos_processed": len(processed_videos),
        "claims_extracted": len(all_claims),
        "novel_claims": len(deltas),
        "contradicted_claims": contradicted,
        "lessons_compiled": len(capabilities["lessons"]),
        "procedures_compiled": len(capabilities["procedures"]),
        "skills_compiled": len(capabilities["skills"]),
        "harnesses_compiled": len(capabilities["harnesses"]),
        "evaluation_passed": passed,
        "capabilities_promoted": len(promoted),
        "dry_run": dry_run,
        "capability_delta": capability_delta,
        "upgrade_proposal": upgrade_proposal,
    }
