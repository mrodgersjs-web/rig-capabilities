from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from harness.packet import Context, DesignPacket, Evaluation, LaneSpec, Report, Runtime, Stage, Tools
from harness.canvas.mapping import MapValidationError, validate_map

_ROOT = Path(__file__).resolve().parents[1]


CRITERIA_IDS = tuple(f"C{i:02d}" for i in range(1, 24))
DEFAULT_EVALUATORS = [
    "has_numbers",
    "has_question",
    "has_link",
    "has_signature",
    "no_banned",
    "agf_floor",
    "gate_present",
    "prompt_has_rule",
    "stage_count_min",
]


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}

def validate_process_map(lane: LaneSpec, path: Path) -> list[str]:
    prefix = f"{lane.slug}:process_map:"
    try:
        value = json.loads(path.read_text())
    except json.JSONDecodeError:
        return [prefix + "invalid_json"]
    except OSError:
        return [prefix + "missing"]
    try:
        process_map = validate_map(value)
    except MapValidationError as exc:
        message = str(exc)
        if "unique" in message:
            rule = "duplicate_node_id"
        elif "unknown kind" in message:
            rule = "unknown_kind"
        elif "endpoint missing" in message:
            rule = "edge_endpoint"
        else:
            rule = "schema"
        return [prefix + rule]

    nodes = process_map["nodes"]
    edges = process_map["edges"]
    starts = [node for node in nodes if node["kind"] == "start"]
    stops = [node for node in nodes if node["kind"] == "stop"]
    findings: list[str] = []
    if len(starts) != 1:
        findings.append(prefix + "start_count")
    if len(stops) != 1:
        findings.append(prefix + "stop_count")
    stage_labels = [node["label"] for node in nodes if node["kind"] == "stage"]
    if stage_labels != [stage.name for stage in lane.stages]:
        findings.append(prefix + "stage_order")
    if len(starts) == len(stops) == 1:
        adjacency: dict[str, list[str]] = {}
        for edge in edges:
            adjacency.setdefault(edge["from"], []).append(edge["to"])
        reachable = {starts[0]["id"]}
        pending = [starts[0]["id"]]
        while pending:
            for target in adjacency.get(pending.pop(), []):
                if target not in reachable:
                    reachable.add(target)
                    pending.append(target)
        if stops[0]["id"] not in reachable:
            findings.append(prefix + "unreachable_stop")
    return findings




def compile_designs(
    path: Path,
    *,
    instance: str | None = None,
    cell_id: str | None = None,
    maps_dir: Path = Path("design/maps"),
) -> DesignPacket:
    designs = json.loads(path.read_text())
    instance = instance or str(designs.get("instance") or path.parent.name or "generic")
    decisions = _mapping(designs.get("decisions"))
    lanes: list[LaneSpec] = []
    for workflow in designs.get("workflows", []):
        if workflow.get("fate") != "keep":
            continue
        spec = dict(workflow["lane_spec"])
        spec["slug"] = workflow["slug"]
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
                spec[key] = workflow[key]
        if "process_map" not in workflow:
            resolved_maps = maps_dir.expanduser()
            if not resolved_maps.is_absolute():
                resolved_maps = Path.cwd() / resolved_maps
            spec["process_map"] = str((resolved_maps / f"{workflow['slug']}.map.json").resolve())
        spec["stages"] = [Stage.model_validate(stage) for stage in spec.get("stages", [])]
        lanes.append(LaneSpec.model_validate(spec))

    evaluation_data = {
        "golden_dir": f"golden/{instance}",
        "evaluators": DEFAULT_EVALUATORS,
        "verifier_family": decisions.get("verifier_family", "codex"),
        "thresholds": {"det_ratio": 0.85, "agf_floor": 85.0},
        **_mapping(decisions.get("evaluation")),
    }
    runtime_data = {
        "carrier": "temporal",
        "task_queue": f"rig-{instance}-design",
        "worker_plist": f"com.rig.{instance}.worker",
        "ledger": decisions.get("ledger", "phoenix"),
        **_mapping(decisions.get("runtime")),
    }
    context_data = {
        "corpus_paths": list(decisions.get("corpus_paths", [])),
        "memory_ns": decisions.get("memory_ns", instance),
        **_mapping(decisions.get("context")),
    }
    inferred_adapters = sorted({lane.executor.split(".", 1)[0] for lane in lanes})
    tools_data = {
        "adapters": list(decisions.get("adapters", inferred_adapters)),
        "mcp_manifest": decisions.get("mcp_manifest"),
        **_mapping(decisions.get("tools")),
    }
    return DesignPacket(
        instance=instance,
        cell_id=cell_id or str(decisions.get("cell_id", "L1-D2-A1-I1")),
        lanes=lanes,
        instance_outcomes=_mapping(designs.get("instance_outcomes")),
        evaluation=Evaluation.model_validate(evaluation_data),
        runtime=Runtime.model_validate(runtime_data),
        context=Context.model_validate(context_data),
        tools=Tools.model_validate(tools_data),
    )


def validate_packet(
    packet: DesignPacket,
    designs: dict[str, Any] | None = None,
    *,
    allow_no_lanes: bool = False,
) -> Report:
    findings: list[str] = []
    if not packet.lanes and not allow_no_lanes:
        findings.append("packet:lanes:none")

    declared_targets = set(packet.instance_outcomes) | {doctrine.id for doctrine in packet.context.doctrines}
    for outcome_key, outcome in packet.instance_outcomes.items():
        if not outcome.numeric_contract:
            findings.append(f"{outcome_key}:numeric_done:missing")
    if any(lane.caps for lane in packet.lanes) and not packet.tools.cap_policy:
        findings.append("packet:cap_policy:missing")

    seen: set[str] = set()
    for lane in packet.lanes:
        if lane.slug in seen:
            findings.append(f"{lane.slug}:slug:duplicate")
        seen.add(lane.slug)
        if declared_targets:
            for stage in lane.stages:
                if not stage.serves:
                    findings.append(f"{lane.slug}:{stage.name}:serves:missing")
                elif stage.serves not in declared_targets:
                    findings.append(f"{lane.slug}:{stage.name}:serves:unknown:{stage.serves}")
        if lane.ask_test_learn is not None and not packet.context.personas:
            findings.append(f"{lane.slug}:prior_before_test:missing")
        if lane.det_ratio < 0.85:
            findings.append(f"{lane.slug}:det_ratio:{lane.det_ratio:.3f} < 0.850")
        llm_count = sum(stage.kind == "llm" for stage in lane.stages)
        if llm_count > 1:
            findings.append(f"{lane.slug}:llm_stages:{llm_count} > 1")
        for action, cap in lane.caps.items():
            maximum = packet.tools.cap_policy.get(action)
            if maximum is not None and cap > maximum:
                findings.append(f"{lane.slug}:caps:over_policy:{action}={cap}>{maximum}")
        if lane.approval not in {"standing", "per_action"}:
            findings.append(f"{lane.slug}:approval:{lane.approval}")
        if lane.boundaries is None:
            findings.append(f"{lane.slug}:boundaries:missing")
        if lane.kpi_stage1 is None:
            findings.append(f"{lane.slug}:kpi_stage1:missing")
        process_map = Path(lane.process_map).expanduser() if lane.process_map else None
        if process_map is not None and not process_map.is_absolute():
            process_map = _ROOT / process_map
        if process_map is None or not process_map.is_file():
            findings.append(f"{lane.slug}:process_map:missing")
        elif designs is not None:
            findings.extend(validate_process_map(lane, process_map))

    if designs is not None:
        workflows = designs.get("workflows", [])
        slugs = {
            str(workflow.get("slug"))
            for workflow in workflows
            if isinstance(workflow, dict) and workflow.get("slug")
        }
        for workflow in workflows:
            slug = str(workflow.get("slug", "unknown"))
            fate = workflow.get("fate")
            if fate in {"keep", "kill", "park"}:
                pass
            elif isinstance(fate, str) and fate.startswith("merge_into:"):
                if fate.removeprefix("merge_into:") not in slugs:
                    findings.append(f"{slug}:fate:merge_target_missing")
            else:
                findings.append(f"{slug}:fate:unknown:{fate}")
            if fate != "keep":
                continue
            criteria = _mapping(workflow.get("criteria"))
            missing = [criterion for criterion in CRITERIA_IDS if criteria.get(criterion, {}).get("status") != "decided"]
            if missing:
                findings.append(f"{slug}:criteria:not_decided={','.join(missing)}")
            examples = _mapping(workflow.get("done_looks_like"))
            great = examples.get("great", [])
            not_good = examples.get("not_good", [])
            if not isinstance(great, list) or len(great) < 3:
                findings.append(f"{slug}:great_examples:{len(great) if isinstance(great, list) else 0} < 3")
            if not isinstance(not_good, list) or len(not_good) < 3:
                findings.append(f"{slug}:not_good_examples:{len(not_good) if isinstance(not_good, list) else 0} < 3")
            all_examples = [
                entry
                for group in (great, not_good)
                if isinstance(group, list)
                for entry in group
            ]
            evidence_count = sum(
                isinstance(entry, dict)
                and isinstance(entry.get("evidence"), str)
                and bool(entry["evidence"].strip())
                for entry in all_examples
            )
            if all_examples and evidence_count == 0:
                findings.append(f"{slug}:researched_done:open")
    return Report(ok=not findings, findings=findings)
