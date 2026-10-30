"""Fail-closed coding-agent completion gate.

Artifact and test observations are recomputed here. Jev screens semantics but
cannot replace independent verification or certify an uncalibrated rubric.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

def _inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def local_completion_jev(state: str, root: Path) -> dict:
    env = os.environ.copy()
    env.update({"S1GATE_JEV_ENDPOINT": "http://127.0.0.1:8080/v1/systemone",
                "TYPESAFE_API_KEY": "local", "S1GATE_STATE_PREVIEW": "0"})
    result = subprocess.run(
        [sys.executable, str(root / "bin/rig-s1gate"), "check", "mission.completion",
         "--stdin", "--json"], input=state, text=True, capture_output=True,
        cwd=root, env=env, timeout=15, check=False)
    if result.returncode not in (0, 2):
        raise RuntimeError("jev_gate_exit_" + str(result.returncode))
    doc = json.loads(result.stdout)
    if doc.get("error") or doc.get("verdict") not in ("PASS", "ESCALATE") or \
            not isinstance(doc.get("decision_id"), int):
        raise RuntimeError("jev_gate_invalid")
    return {"status": doc["verdict"], "decision_id": doc["decision_id"],
            "model": doc.get("model"), "latency_ms": doc.get("latency_ms"),
            "advisory": doc.get("advisory"), "answers": doc.get("answers", {})}


def _run_check(argv: list[str], root: Path) -> dict:
    # Only a controller-supplied, repo-contained explicit unittest target.
    if not isinstance(argv, list) or len(argv) != 4 or argv[:3] != ["python3", "-m", "unittest"] or \
            not isinstance(argv[3], str) or not re.fullmatch(r"tests\.[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)*", argv[3]):
        return {"argv": argv, "exit_code": None, "error": "command_not_permitted"}
    try:
        result = subprocess.run(argv, cwd=root, text=True, capture_output=True,
                                timeout=120, check=False)
        output = (result.stdout + result.stderr).encode("utf-8", "replace")
        # unittest writes its terminal summary to stderr. Ignore test stdout,
        # which can contain a forged summary. Still precheck evidence only.
        summaries = re.findall(r"^Ran ([0-9]+) tests? in ", result.stderr, re.MULTILINE)
        count = int(summaries[-1]) if summaries else 0
        return {"argv": argv, "exit_code": result.returncode,
                "tests_run": count, "output_sha256": hashlib.sha256(output).hexdigest()}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"argv": argv, "exit_code": None, "error": type(exc).__name__}


def check_completion(evidence: dict, root: Path | str, *,
                     controller_contract: dict | None = None,
                     runner: Callable[[list[str], Path], dict] = _run_check,
                     jev_loader: Callable[[str, Path], dict] = local_completion_jev,
                     independent_verifier: Callable[[dict], dict] | None = None) -> dict:
    """Precheck only; this adapter cannot authorize DONE.

    Evidence inside the input is a claim, not a receipt. The independent
    verifier must be supplied by the orchestrator, never from this document.
    """
    root = Path(root).resolve()
    errors: list[str] = []
    if not isinstance(evidence, dict):
        return {"status": "BLOCK", "errors": ["evidence_not_object"]}
    claim = evidence.get("claim")
    if not isinstance(claim, str) or not claim.strip():
        errors.append("claim_missing")
        claim = ""
    artifacts = evidence.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts or len(artifacts) > 50:
        errors.append("artifacts_invalid")
        artifacts = []
    observed = []
    for artifact in artifacts:
        if not isinstance(artifact, dict) or not isinstance(artifact.get("path"), str) or \
                not isinstance(artifact.get("sha256"), str):
            errors.append("artifact_invalid")
            continue
        rel = Path(artifact["path"])
        path = (root / rel).resolve()
        if rel.is_absolute() or not _inside(path, root) or not path.is_file():
            errors.append("artifact_outside_or_missing:" + artifact["path"])
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != artifact["sha256"]:
            errors.append("artifact_drift:" + artifact["path"])
        observed.append({"path": artifact["path"], "sha256": digest})
    if errors:
        return {"status": "BLOCK", "errors": sorted(set(errors)), "artifacts": observed,
                "checks": [], "jev": {"status": "not_called"},
                "verifier": {"status": "not_called"},
                "automatic_completion_authorized": False}
    if not isinstance(controller_contract, dict) or not isinstance(controller_contract.get("intent"), str) or \
            not controller_contract["intent"].strip() or \
            not isinstance(controller_contract.get("acceptance_criteria"), list) or \
            not controller_contract["acceptance_criteria"] or \
            not all(isinstance(x, str) and x.strip() for x in controller_contract["acceptance_criteria"]) or \
            not isinstance(controller_contract.get("required_artifacts"), list) or \
            not controller_contract["required_artifacts"] or \
            not isinstance(controller_contract.get("test_commands"), list) or \
            not controller_contract["test_commands"]:
        return {"status": "BLOCK", "errors": ["trusted_controller_contract_missing"],
                "artifacts": observed, "checks": [], "jev": {"status": "not_called"},
                "verifier": {"status": "not_called"}, "automatic_completion_authorized": False}
    required = controller_contract["required_artifacts"]
    if not all(isinstance(x, str) and x for x in required) or \
            not set(required).issubset({x["path"] for x in observed}):
        errors.append("required_artifacts_missing")
    commands = controller_contract["test_commands"]
    if len(commands) > 5 or evidence.get("test_commands") != commands:
        errors.append("test_commands_not_controller_approved")
    if errors:
        return {"status": "BLOCK", "errors": sorted(set(errors)), "artifacts": observed,
                "checks": [], "jev": {"status": "not_called"},
                "verifier": {"status": "not_called"}, "automatic_completion_authorized": False}
    checks = []
    for argv in commands:
        try:
            checks.append(runner(argv, root))
        except Exception as exc:  # external runner boundary must fail closed
            checks.append({"argv": argv, "exit_code": None, "error": type(exc).__name__})
    if any(not isinstance(r, dict) or r.get("exit_code") != 0 or
           not isinstance(r.get("tests_run"), int) or r["tests_run"] < 1 for r in checks):
        errors.append("behavioral_check_failed")
    if errors:
        return {"status": "BLOCK", "errors": sorted(set(errors)), "artifacts": observed,
                "checks": checks, "jev": {"status": "not_called"},
                "verifier": {"status": "not_called"},
                "automatic_completion_authorized": False}
    if independent_verifier is None:
        verifier = {"status": "pending"}
        errors.append("independent_verifier_missing")
    else:
        try:
            verifier = independent_verifier({"claim": claim, "artifacts": observed,
                                             "checks": checks})
            if not isinstance(verifier, dict):
                verifier = {"status": "invalid"}
            if verifier.get("status") != "VERIFIED" or \
                    not isinstance(verifier.get("observations"), list) or \
                    not verifier["observations"] or \
                    verifier.get("family") == evidence.get("builder_family"):
                errors.append("independent_verifier_not_verified")
        except Exception as exc:  # independent callback must fail closed
            verifier = {"status": "error", "reason": type(exc).__name__}
            errors.append("independent_verifier_error")
    # The model sees a bounded local evidence summary, not source bodies or test logs.
    observations = verifier.get("observations")
    if not isinstance(observations, list):
        observations = []
    state = json.dumps({"intent": controller_contract["intent"],
                        "acceptance_criteria": controller_contract["acceptance_criteria"],
                        "required_artifacts": required, "claim": claim, "artifacts": observed,
                        "checks": [{"argv": x.get("argv"), "exit_code": x.get("exit_code")}
                                   for x in checks if isinstance(x, dict)],
                        "verifier": {"status": verifier.get("status"),
                                     "observations": observations[:5]}},
                       sort_keys=True)
    try:
        jev = jev_loader(state, root)
        if not isinstance(jev, dict) or jev.get("status") not in ("PASS", "ESCALATE") or \
                not isinstance(jev.get("decision_id"), int):
            raise ValueError("jev_response_invalid")
    except Exception as exc:  # model adapter boundary must fail closed
        jev = {"status": "unavailable", "reason": type(exc).__name__}
        errors.append("jev_unavailable")
    # A mutable rubric and model output can never grant completion authority.
    errors.append("certified_completion_adapter_missing")
    if jev.get("status") != "PASS":
        errors.append("jev_semantic_review_required")
    return {"status": "REVIEW_REQUIRED", "errors": sorted(set(errors)),
            "artifacts": observed, "checks": checks, "jev": jev, "verifier": verifier,
            "automatic_completion_authorized": False}
