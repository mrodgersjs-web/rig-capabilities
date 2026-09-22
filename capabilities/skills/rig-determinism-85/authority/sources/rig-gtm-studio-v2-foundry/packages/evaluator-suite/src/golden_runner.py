"""packages/evaluator-suite/src/golden_runner.py — Behavioral Golden Test Runner.

Loads golden test cases, executes skills, and compares actual vs expected output.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def load_golden_cases(test_dir: Path) -> list:
    """Load golden test cases from a directory."""
    cases = []
    for path in sorted(test_dir.glob("*.json")):
        case = json.loads(path.read_text())
        case["path"] = str(path)
        cases.append(case)
    return cases


def select_skill(skills: list, skill_name: str) -> Optional[dict]:
    """Select a skill by name."""
    for skill in skills:
        if skill["name"] == skill_name:
            return skill
    return None


def execute_skill(skill: dict, input_data: dict) -> dict:
    """Execute a skill's procedure against input data.

    For the seed pipeline, this is a heuristic execution that validates
    the input schema and produces a structured output.
    """
    # Validate input against skill's input schema
    input_schema = skill.get("input_schema", {})
    required_fields = input_schema.get("required", [])
    for field in required_fields:
        if field not in input_data:
            return {
                "status": "error",
                "error": f"Missing required input field: {field}",
            }

    # Execute procedure (heuristic for seed pipeline)
    procedure = skill.get("procedure", [])
    steps_executed = []
    for step in procedure:
        steps_executed.append(step)

    # Generate output based on skill name and input
    context = input_data.get("context", "")
    output = {
        "status": "success",
        "recommendation": f"Based on {skill['name']} analysis of context: {context[:100]}...",
        "confidence": skill.get("confidence", 0.7),
        "steps_executed": len(steps_executed),
        "skill_id": skill["skill_id"],
    }

    return output


def compare_outputs(actual: dict, expected: dict) -> dict:
    """Compare actual vs expected output."""
    errors = []

    # Check status
    if actual.get("status") != expected.get("status", "success"):
        errors.append(f"Status mismatch: expected {expected.get('status')}, got {actual.get('status')}")

    # Check recommendation contains expected key terms
    expected_rec = expected.get("recommendation", "")
    actual_rec = actual.get("recommendation", "")
    if expected_rec and not any(term in actual_rec for term in expected_rec.split()[:5]):
        errors.append("Recommendation does not contain expected key terms")

    # Check confidence range
    expected_conf = expected.get("confidence")
    if expected_conf is not None:
        actual_conf = actual.get("confidence", 0.0)
        if abs(actual_conf - expected_conf) > 0.15:
            errors.append(f"Confidence out of range: expected ~{expected_conf}, got {actual_conf}")

    return {
        "match": len(errors) == 0,
        "errors": errors,
    }


def run_golden_test(skill: dict, test_case: dict) -> dict:
    """Run a single golden test case."""
    input_data = test_case.get("input", {})
    expected_output = test_case.get("expected_output", {})

    # Execute skill
    actual_output = execute_skill(skill, input_data)

    # Compare
    comparison = compare_outputs(actual_output, expected_output)

    return {
        "test_id": test_case.get("test_id", "unknown"),
        "skill_name": skill.get("name", "unknown"),
        "status": "pass" if comparison["match"] else "fail",
        "comparison_errors": comparison["errors"],
        "actual_output": actual_output,
    }


def run_all_golden_tests(skills_dir: Path, test_dir: Path) -> list:
    """Run all golden tests against all skills."""
    # Load skills
    skills = []
    for path in skills_dir.glob("*.json"):
        skills.append(json.loads(path.read_text()))

    # Load test cases
    test_cases = load_golden_cases(test_dir)

    results = []
    for test_case in test_cases:
        skill_name = test_case.get("skill_name")
        if not skill_name:
            continue

        skill = select_skill(skills, skill_name)
        if not skill:
            results.append({
                "test_id": test_case.get("test_id"),
                "skill_name": skill_name,
                "status": "fail",
                "comparison_errors": [f"Skill {skill_name} not found"],
            })
            continue

        result = run_golden_test(skill, test_case)
        results.append(result)

    return results
