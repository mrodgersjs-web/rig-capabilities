from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from harness.packet import LaneSpec, Stage

_ACTION_STAGES = {"connect", "dispatch", "execute", "fire", "publish", "reply", "send"}

def lane_from_workflow(workflow: Mapping[str, Any]) -> LaneSpec:
    lane_spec = workflow.get("lane_spec")
    if not isinstance(lane_spec, Mapping):
        raise ValueError("workflow lane_spec must be an object")
    values = dict(lane_spec)
    values["slug"] = workflow.get("slug")
    for key in (
        "boundaries",
        "kpi_stage1",
        "angles",
        "process_map",
        "human_decisions",
        "failure_rule",
        "ask_test_learn",
    ):
        if key in workflow:
            values[key] = workflow[key]
    return LaneSpec.model_validate(values)


def _stage_tool(lane: LaneSpec, stage: Stage) -> str | None:
    if stage.kind == "llm":
        return "pydantic_ai.Agent"
    leaf = lane.executor.rsplit(".", 1)[-1]
    if stage.name == leaf or stage.name in _ACTION_STAGES:
        return lane.executor
    return None


def lane_to_map(lane: LaneSpec) -> dict[str, list[dict[str, Any]]]:
    nodes: list[dict[str, Any]] = [
        {"id": "start", "kind": "start", "label": "START", "x": 0, "y": 120}
    ]
    edges: list[dict[str, str]] = []
    chain = ["start"]
    for index, stage in enumerate(lane.stages, start=1):
        stage_id = f"stage-{index}"
        x = index * 240
        tool = _stage_tool(lane, stage)
        stage_node: dict[str, Any] = {
            "id": stage_id,
            "kind": "stage",
            "label": stage.name,
            "x": x,
            "y": 120,
        }
        if tool:
            stage_node["tool"] = tool
        nodes.append(stage_node)
        chain.append(stage_id)
        if stage.gate:
            gate_id = f"gate-{index}"
            kind = "approval" if "approval" in stage.gate or stage.name == "approval" else "gate"
            nodes.append({"id": gate_id, "kind": kind, "label": stage.gate, "x": x, "y": 0})
            edges.append({"from": stage_id, "to": gate_id})
        if tool:
            tool_id = f"tool-{index}"
            nodes.append({"id": tool_id, "kind": "tool", "label": tool, "x": x, "y": 260})
            edges.append({"from": stage_id, "to": tool_id})
    stop_x = (len(lane.stages) + 1) * 240
    nodes.append({"id": "stop", "kind": "stop", "label": "STOP", "x": stop_x, "y": 120})
    chain.append("stop")
    edges.extend({"from": source, "to": target} for source, target in zip(chain, chain[1:]))
    return {"nodes": nodes, "edges": edges}


def write_lane_map(lane: LaneSpec, out_dir: Path = Path("design/maps")) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{lane.slug}.map.json"
    path.write_text(json.dumps(lane_to_map(lane), indent=2, sort_keys=True) + "\n")
    return path


def has_numeric_done(answer: str) -> bool:
    return re.search(r"\d", answer) is not None



def discovery_questions(
    lane: LaneSpec,
    process_map: Mapping[str, Any],
) -> list[dict[str, Any]]:
    nodes = process_map.get("nodes")
    if not isinstance(nodes, list):
        raise ValueError("process map nodes must be an array")
    start = next((node for node in nodes if node.get("kind") == "start"), None)
    stop = next((node for node in nodes if node.get("kind") == "stop"), None)
    if not isinstance(start, Mapping) or not isinstance(stop, Mapping):
        raise ValueError("process map requires START and STOP nodes")
    questions: list[dict[str, Any]] = [
        {
            "id": "outcome_kpi_numeric_done",
            "node_id": str(start["id"]),
            "question": "What outcome, KPI, numeric contract, and observable done event govern this workflow?",
            "options": ["State KPI + number + unit + done event", "Mark OPEN"],
            "requires_numeric": True,
        },
        {
            "id": "processes",
            "node_id": str(start["id"]),
            "question": "Which business processes can influence that outcome, and which run in parallel?",
            "options": ["Name processes and dependencies", "Mark OPEN"],
        },
        {
            "id": "workflows",
            "node_id": str(start["id"]),
            "question": "Which repeatable workflows implement each process?",
            "options": ["Name workflow boundaries", "Mark OPEN"],
        },
        {
            "id": "cadence",
            "node_id": str(start["id"]),
            "question": "Which workflows are daily, weekly, event-driven, or manual?",
            "options": ["Lock cadence by workflow", "Mark OPEN"],
        },
    ]
    for node in (node for node in nodes if node.get("kind") == "stage"):
        questions.append(
            {
                "id": f"block:{node['label']}",
                "node_id": str(node["id"]),
                "question": f"Which block owns {node['label']}: collect, protect, work, or learn?",
                "options": ["collect", "protect", "work", "learn", "Mark OPEN"],
            }
        )
    questions.extend(
        [
            {
                "id": "start",
                "node_id": str(start["id"]),
                "question": "What event truly starts this process before any scheduled poll?",
                "options": ["Keep current START", "Insert an upstream event", "Mark OPEN"],
            },
            {
                "id": "stop",
                "node_id": str(stop["id"]),
                "question": "What observable receipt proves this process is finished?",
                "options": ["Keep current STOP", "Name a stronger receipt", "Mark OPEN"],
            },
        ]
    )
    if lane.kpi_stage1:
        kpi_node = next(
            (
                node for node in nodes
                if node.get("kind") == "stage" and node.get("label") == lane.kpi_stage1.stage
            ),
            start,
        )
        questions.append(
            {
                "id": "kpi_stage1",
                "node_id": str(kpi_node["id"]),
                "question": f"What KPI stage 1 signal proves {lane.kpi_stage1.stage} is working?",
                "options": ["Keep current KPI", "Replace the signal or source", "Mark OPEN"],
            }
        )
    for node in (node for node in nodes if node.get("kind") == "stage"):
        questions.append(
            {
                "id": f"tool:{node['label']}",
                "node_id": str(node["id"]),
                "question": f"Which real tool owns stage {node['label']}?",
                "options": ["Keep mapped tool", "Name a different tool", "Mark OPEN"],
            }
        )
    questions.extend(
        [
            {
                "id": "human_decisions",
                "node_id": str(start["id"]),
                "question": "Who makes each human decision, what do they decide, and what gate binds it?",
                "options": ["Name owner, decision, and gate", "Mark OPEN"],
            },
            {
                "id": "failure_rule",
                "node_id": str(stop["id"]),
                "question": "What does failed look like, and how is it distinguished from a valid zero result?",
                "options": ["Name the failure discriminator", "Mark OPEN"],
            },
            {
                "id": "prior",
                "node_id": str(start["id"]),
                "question": "What persona bracket and evidence-backed working prior apply before any test?",
                "options": ["State bracket, confidence, evidence, and decision", "Mark OPEN"],
            },
            {
                "id": "gap_intelligence",
                "node_id": str(start["id"]),
                "question": "What evidence-backed gap must be known before novelty or distinctive value is proposed?",
                "options": ["Name gap and evidence", "Mark OPEN"],
            },
        ]
    )
    for lens in ("systems", "behavioral", "COLLIDER", "BREAKER", "SURPRISE"):
        questions.append(
            {
                "id": f"lens:{lens}",
                "node_id": str(start["id"]),
                "question": f"What {lens} angle survives the gap-intelligence reality filter?",
                "options": ["Keep the current angle", "Revise the angle", "Drop the angle"],
            }
        )
    questions.append(
        {
            "id": "ask_test_learn",
            "node_id": str(stop["id"]),
            "question": "What surface, ask, prediction, test card, response code, quality gate, and review cadence close the learning loop?",
            "options": ["Lock the ask/test/learn card", "Mark OPEN"],
        }
    )
    return questions


def discovery_checklist(lane: LaneSpec) -> str:
    boundaries = lane.boundaries
    kpi = lane.kpi_stage1
    lines = [
        "DISCOVERY CHECKLIST",
        f"START: {boundaries.start.trigger} @ {boundaries.start.source_of_truth}" if boundaries else "START: OPEN",
        f"STOP: {boundaries.stop.outcome} @ {boundaries.stop.receipt}" if boundaries else "STOP: OPEN",
    ]
    if boundaries and boundaries.handoffs:
        lines.extend(f"HANDOFF: {handoff.to} <- {handoff.artifact}" for handoff in boundaries.handoffs)
    else:
        lines.append("HANDOFFS: OPEN")
    lines.append(
        f"KPI STAGE 1: {kpi.stage} | {kpi.signal} | {kpi.source_of_truth} | {kpi.baseline_today:g}->{kpi.first_target:g}"
        if kpi
        else "KPI STAGE 1: OPEN"
    )
    lines.append("TOOLS PER STAGE:")
    lines.extend(f"- {stage.name}: {_stage_tool(lane, stage) or 'OPEN'}" for stage in lane.stages)
    lines.append("BLOCKS:")
    lines.extend(f"- {stage.name}: {stage.block or 'OPEN'}" for stage in lane.stages)
    lines.append("HUMAN DECISIONS:")
    lines.extend(
        f"- {decision.who}: {decision.decides} @ {decision.gate}"
        for decision in lane.human_decisions
    )
    if not lane.human_decisions:
        lines.append("- OPEN")
    lines.append(f"FAILURE RULE: {lane.failure_rule or 'OPEN'}")
    lines.append(f"ASK/TEST/LEARN: {'LOCKED' if lane.ask_test_learn else 'OPEN'}")
    lines.append("ANGLES:")
    by_lens = {angle.lens: angle for angle in lane.angles}
    for lens in ("systems", "behavioral", "COLLIDER", "BREAKER", "SURPRISE"):
        angle = by_lens.get(lens)
        lines.append(f"- {lens}: {angle.text} ({'KEEP' if angle.kept else 'DROP'})" if angle else f"- {lens}: OPEN")
    return "\n".join(lines)
