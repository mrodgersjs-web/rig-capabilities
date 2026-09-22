from __future__ import annotations

import ast
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from harness.components import apply_mutation, render_template, report, validate_python
from harness.packet import DesignPacket, Proposal, Report

_COMPONENT = "evaluation"

_NUMBER = re.compile(r"(?<!\w)[+-]?(?:\d+(?:[.,]\d+)?|\.\d+)%?")


def _value(inputs: Mapping[str, Any], outputs: Mapping[str, Any], name: str, default: Any) -> Any:
    return outputs.get(name, inputs.get(name, default))


def has_numbers(inputs: Mapping[str, Any], outputs: Mapping[str, Any]) -> float:
    return float(len(_NUMBER.findall(str(_value(inputs, outputs, "text", "")))) >= 2)


def has_question(inputs: Mapping[str, Any], outputs: Mapping[str, Any]) -> float:
    return float("?" in str(_value(inputs, outputs, "text", "")))


def has_link(inputs: Mapping[str, Any], outputs: Mapping[str, Any]) -> float:
    text = str(_value(inputs, outputs, "text", "")).casefold()
    link = str(_value(inputs, outputs, "link", "mikerodgers.tech")).casefold()
    return float(link in text)


def has_signature(inputs: Mapping[str, Any], outputs: Mapping[str, Any]) -> float:
    text = str(_value(inputs, outputs, "text", ""))
    signature = str(_value(inputs, outputs, "signature", "— Mike"))
    return float(signature in text)


def no_banned(inputs: Mapping[str, Any], outputs: Mapping[str, Any]) -> float:
    text = str(_value(inputs, outputs, "text", "")).casefold()
    banned = _value(inputs, outputs, "banned", ())
    return float(all(str(term).casefold() not in text for term in banned))


def agf_floor(inputs: Mapping[str, Any], outputs: Mapping[str, Any]) -> float:
    score = float(_value(inputs, outputs, "agf_score", 0.0))
    floor = float(_value(inputs, outputs, "agf_floor", 85.0))
    return float(score >= floor)


def _lane_file(
    inputs: Mapping[str, Any],
    outputs: Mapping[str, Any],
    filename: str,
) -> str | None:
    files = outputs.get("files")
    lane = inputs.get("lane")
    if not isinstance(files, Mapping) or not isinstance(lane, str):
        return None
    suffix = f"lanes/{lane}/{filename}"
    for path, content in files.items():
        if str(path).endswith(suffix):
            return str(content)
    return None


def _assignment(content: str, name: str) -> ast.AST | None:
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            return node.value
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            return node.value
    return None


def gate_present(inputs: Mapping[str, Any], outputs: Mapping[str, Any]) -> float:
    content = _lane_file(inputs, outputs, "gates.py")
    required = inputs.get("required_gate")
    value = _assignment(content, "GATES") if content is not None else None
    if not isinstance(value, ast.Dict) or not isinstance(required, str):
        return 0.0
    keys = [ast.literal_eval(key) for key in value.keys if key is not None]
    return float(required in keys)


def prompt_has_rule(inputs: Mapping[str, Any], outputs: Mapping[str, Any]) -> float:
    content = _lane_file(inputs, outputs, "workflow.py")
    required = inputs.get("required_rule")
    value = _assignment(content, "PROMPT_RULES") if content is not None else None
    if value is None or not isinstance(required, str):
        return 0.0
    try:
        rules = ast.literal_eval(value)
    except (ValueError, TypeError):
        return 0.0
    return float(isinstance(rules, list) and required in rules)


def stage_count_min(inputs: Mapping[str, Any], outputs: Mapping[str, Any]) -> float:
    content = _lane_file(inputs, outputs, "workflow.py")
    minimum = inputs.get("min_stages")
    if content is None or not isinstance(minimum, int):
        return 0.0
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return 0.0
    count = sum(
        isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Stage"
        for node in ast.walk(tree)
    )
    return float(count >= minimum)


def render(packet: DesignPacket, out: Path) -> list[Path]:
    root = out / _COMPONENT
    agf = packet.evaluation.thresholds.get("agf_floor", 85.0)
    rendered = [
        render_template("evaluators.py.j2", root / "evaluators.py", agf_floor=agf),
        render_template("planted_failures.sh.j2", root / "planted_failures.sh", agf_below=agf - 1),
    ]
    rendered[1].chmod(0o755)
    manifest = root / "golden" / "manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({
        "source": packet.evaluation.golden_dir,
        "evaluators": packet.evaluation.evaluators,
        "thresholds": packet.evaluation.thresholds,
        "lanes": [lane.slug for lane in packet.lanes],
    }, indent=2, sort_keys=True) + "\n")
    rendered.append(manifest)
    for lane in packet.lanes:
        rendered.extend([
            render_template(
                "feature.feature.j2",
                root / "features" / f"{lane.slug}.feature",
                slug=lane.slug,
                approval=lane.approval,
                schedule_cron=lane.schedule_cron,
                tz=lane.tz,
            ),
            render_template(
                "test_planted_failure.py.j2",
                root / "tests" / f"test_{lane.slug}_planted_failure.py",
                slug=lane.slug,
            ),
        ])
    return rendered


def validate(files: list[Path]) -> Report:
    findings: list[str] = []
    by_name = {path.name: path for path in files if path.exists()}
    for name in ("evaluators.py", "planted_failures.sh", "manifest.json"):
        if name not in by_name:
            findings.append(f"{name}:missing:file")
    if evaluators := by_name.get("evaluators.py"):
        validate_python(evaluators, findings)
        text = evaluators.read_text()
        for name in ("has_numbers", "has_question", "has_link", "has_signature", "no_banned", "agf_floor"):
            if f"def {name}(" not in text:
                findings.append(f"evaluators.py:missing:{name}")
    if script := by_name.get("planted_failures.sh"):
        if "expect_red()" not in script.read_text():
            findings.append("planted_failures.sh:missing:expect_red")
    features = [path for path in files if path.suffix == ".feature" and path.exists()]
    tests = [path for path in files if path.name.startswith("test_") and path.exists()]
    if not features:
        findings.append("features:missing:any")
    if len(features) != len(tests):
        findings.append(f"planted_tests:count:{len(tests)} != features {len(features)}")
    for path in tests:
        validate_python(path, findings)
    return report(findings)


def mutate(files: list[Path], proposal: Proposal) -> list[Path]:
    return apply_mutation(files, proposal, _COMPONENT)
