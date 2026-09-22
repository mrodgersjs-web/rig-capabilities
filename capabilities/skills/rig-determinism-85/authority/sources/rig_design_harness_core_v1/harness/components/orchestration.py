from __future__ import annotations

from pathlib import Path

from harness.components import apply_mutation, render_template, report, validate_python
from harness.packet import DesignPacket, Proposal, Report

_COMPONENT = "orchestration"


def render(packet: DesignPacket, out: Path) -> list[Path]:
    root = out / _COMPONENT / "lanes"
    rendered: list[Path] = []
    for lane in packet.lanes:
        lane_root = root / lane.slug
        stages = [{
            "name_repr": repr(stage.name),
            "kind_repr": repr(stage.kind),
            "schema_repr": repr(stage.schema_),
            "fallback_repr": repr(stage.fallback),
            "gate_repr": repr(stage.gate),
        } for stage in lane.stages]
        gate_names = sorted({name.strip() for stage in lane.stages for name in (stage.gate or "").split("|") if name.strip()})
        gates = [{
            "name_repr": repr(name),
            "callable_repr": "_question" if name == "question" else f"_gate_result({name!r})",
        } for name in gate_names]
        rendered.extend([
            render_template(
                "workflow.py.j2",
                lane_root / "workflow.py",
                slug_repr=repr(lane.slug),
                stages=stages,
                prompt_rules_repr=repr([]),
            ),
            render_template("activities.py.j2", lane_root / "activities.py", stage_names_repr=repr(tuple(stage.name for stage in lane.stages))),
            render_template("gates.py.j2", lane_root / "gates.py", gates=gates),
            render_template("healer_hooks.py.j2", lane_root / "healer_hooks.py", healer_hooks_repr=repr(tuple(lane.healer_hooks))),
        ])
    return rendered


def validate(files: list[Path]) -> Report:
    findings: list[str] = []
    lane_roots = sorted({path.parent for path in files if path.parent.name != "lanes"})
    if not lane_roots:
        findings.append("lanes:missing:any")
    for lane_root in lane_roots:
        by_name = {path.name: path for path in files if path.parent == lane_root and path.exists()}
        for name in ("workflow.py", "activities.py", "gates.py", "healer_hooks.py"):
            path = by_name.get(name)
            if path is None:
                findings.append(f"{lane_root.name}/{name}:missing:file")
            else:
                validate_python(path, findings)
        workflow = by_name.get("workflow.py")
        if workflow:
            text = workflow.read_text()
            for token in ("class Stage:", "class Workflow:", "PROMPT_RULES:", "gates_fn=evaluate_gates", "gate=stage.gate", "prompt_rules=PROMPT_RULES"):
                if token not in text:
                    findings.append(f"{lane_root.name}/workflow.py:missing:{token}")
        gates = by_name.get("gates.py")
        if gates and "GATES:" not in gates.read_text():
            findings.append(f"{lane_root.name}/gates.py:missing:GATES")
        activities = by_name.get("activities.py")
        if activities and ("evaluate_gates(payload, gate)" not in activities.read_text() or "prompt_rules: list[str]" not in activities.read_text()):
            findings.append(f"{lane_root.name}/activities.py:missing:gate_execution")
    return report(findings)


def mutate(files: list[Path], proposal: Proposal) -> list[Path]:
    return apply_mutation(files, proposal, _COMPONENT)
