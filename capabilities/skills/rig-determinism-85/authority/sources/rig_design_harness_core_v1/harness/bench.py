from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from time import perf_counter
from typing import Any

from pydantic import BaseModel

from harness.components import evaluation
from harness.ledger import get_ledger
from harness.packet import DesignPacket

ROOT = Path(__file__).resolve().parents[1]
Evaluator = Callable[[Mapping[str, Any], Mapping[str, Any]], float]


class TaskResult(BaseModel):
    task_id: str
    score: float
    cost_usd: float
    latency_s: float
    tool_calls: int


class BenchReport(BaseModel):
    per_task: list[TaskResult]
    score_mean: float
    pareto: list[TaskResult]


def load_tasks(path: Path) -> list[dict[str, Any]]:
    return [json.loads(task.read_text()) for task in sorted(path.glob("*.json"))]


def _resolve(values: Iterable[str | Evaluator]) -> dict[str, Evaluator]:
    resolved: dict[str, Evaluator] = {}
    for value in values:
        if callable(value):
            resolved[value.__name__] = value
            continue
        evaluator = getattr(evaluation, value, None)
        if not callable(evaluator):
            raise ValueError(f"unknown evaluator: {value}")
        resolved[value] = evaluator
    return resolved


def _outputs(inputs: Mapping[str, Any], rendered_dir: Path | None) -> dict[str, Any]:
    declared = inputs.get("outputs")
    outputs = dict(declared) if isinstance(declared, Mapping) else dict(inputs)
    if rendered_dir is not None:
        outputs["files"] = {
            str(path.relative_to(rendered_dir)): path.read_text(errors="replace")
            for path in sorted(rendered_dir.rglob("*"))
            if path.is_file()
        }
    return outputs


def _sum_numbers(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, Mapping):
        return sum(_sum_numbers(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return sum(_sum_numbers(item) for item in value)
    return 0.0


def _trace_metrics(packet: DesignPacket, inputs: Mapping[str, Any]) -> tuple[float, int]:
    run_id = inputs.get("run_id")
    if not isinstance(run_id, str):
        return 0.0, 0
    try:
        spans = get_ledger(packet.runtime.ledger).fetch(run_id)["spans"]
    except (FileNotFoundError, ValueError, KeyError, json.JSONDecodeError):
        return 0.0, 0
    cost = sum(_sum_numbers(span.get("attrs", {}).get("usage", 0)) for span in spans)
    calls = 0
    for span in spans:
        tool_calls = span.get("attrs", {}).get("tool_calls", 0)
        calls += len(tool_calls) if isinstance(tool_calls, list) else int(tool_calls or 0)
    return cost, calls


def _meets(value: float, expected: Any) -> bool:
    if isinstance(expected, bool):
        return bool(value) is expected
    if isinstance(expected, Mapping) and "value" in expected:
        return value == float(expected["value"])
    threshold = expected.get("threshold") if isinstance(expected, Mapping) else expected
    return value >= float(threshold)


def _pareto(results: list[TaskResult]) -> list[TaskResult]:
    return [
        result
        for result in results
        if not any(
            other is not result
            and other.score >= result.score
            and other.cost_usd <= result.cost_usd
            and other.latency_s <= result.latency_s
            and (
                other.score > result.score
                or other.cost_usd < result.cost_usd
                or other.latency_s < result.latency_s
            )
            for other in results
        )
    ]


def run(
    packet: DesignPacket,
    tasks: Sequence[Mapping[str, Any]],
    evaluators: Iterable[str | Evaluator],
    *,
    rendered_dir: Path | None = None,
    append: bool = True,
) -> BenchReport:
    resolved = _resolve(evaluators)
    results: list[TaskResult] = []
    for task in tasks:
        started = perf_counter()
        inputs = task.get("inputs", {})
        expected = task.get("expected", {})
        if not isinstance(inputs, Mapping) or not isinstance(expected, Mapping):
            raise ValueError("task inputs and expected must be objects")
        outputs = _outputs(inputs, rendered_dir)
        checks = []
        for name, target in expected.items():
            if name not in resolved:
                raise ValueError(f"task {task.get('task_id')} expects unavailable evaluator {name}")
            checks.append(_meets(float(resolved[name](inputs, outputs)), target))
        cost, tool_calls = _trace_metrics(packet, inputs)
        results.append(
            TaskResult(
                task_id=str(task["task_id"]),
                score=sum(checks) / len(checks) if checks else 0.0,
                cost_usd=cost,
                latency_s=perf_counter() - started,
                tool_calls=tool_calls,
            )
        )
    report = BenchReport(
        per_task=results,
        score_mean=sum(result.score for result in results) / len(results) if results else 0.0,
        pareto=_pareto(results),
    )
    if append:
        target = Path(packet.evaluation.golden_dir)
        if not target.is_absolute():
            target = ROOT / target
        target.mkdir(parents=True, exist_ok=True)
        with (target / "bench.jsonl").open("a") as stream:
            for result in results:
                stream.write(result.model_dump_json() + "\n")
    return report
