from __future__ import annotations

import hashlib
import importlib
import json
import shutil
import tempfile
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from harness import bench
from harness.bench import BenchReport
from harness.models import get_model
from harness.packet import DesignPacket, Proposal

ROOT = Path(__file__).resolve().parents[1]
MUTATION_LEDGER = ROOT / "mutation_ledger.jsonl"
_COMPONENTS = ("context", "tools", "runtime", "orchestration", "evaluation")


class EvalReport(BaseModel):
    iteration: int
    train: BenchReport
    failing_traces: list[str]


class MutationRecord(BaseModel):
    ts: str
    component: str
    diff_sha: str
    train_before: float
    train_after: float
    dev_before: float
    dev_after: float
    accepted: bool
    cited_traces: list[str]
    refused: bool = Field(default=False, exclude=True)


def build_proposer() -> Agent[None, Proposal]:
    return Agent(
        get_model(),
        output_type=Proposal,
        name="rdh-proposer",
        model_settings={"temperature": 0},
        retries=1,
        instructions=(
            "Propose one unified-diff mutation to exactly one harness component. "
            "Cite failing trace task IDs and never include a second component."
        ),
    )


def propose_live(report: EvalReport, guidance: str | None = None) -> Proposal:
    prompt = report.model_dump_json(indent=2)
    if guidance:
        prompt += f"\n\nHuman guidance:\n{guidance}"
    return build_proposer().run_sync(prompt).output


def _render_all(packet: DesignPacket, root: Path) -> None:
    for name in _COMPONENTS:
        importlib.import_module(f"harness.components.{name}").render(packet, root)


def _component_files(root: Path, component: str) -> list[Path]:
    return [path for path in (root / component).rglob("*") if path.is_file()]


def _touched_components(diff: str, declared: str) -> set[str]:
    touched: set[str] = set()
    for line in diff.splitlines():
        if not line.startswith(("--- ", "+++ ")):
            continue
        raw = line[4:].split("\t", 1)[0]
        if raw == "/dev/null":
            touched.add("/dev/null")
            continue
        path = Path(raw[2:] if raw.startswith(("a/", "b/")) else raw)
        first = path.parts[0] if path.parts else declared
        touched.add(first if first in _COMPONENTS else declared)
    return touched


def _score(
    packet: DesignPacket,
    tasks: Sequence[Mapping[str, Any]],
    root: Path,
) -> BenchReport:
    return bench.run(packet, tasks, packet.evaluation.evaluators, rendered_dir=root, append=False)


def _record(row: MutationRecord) -> None:
    MUTATION_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with MUTATION_LEDGER.open("a") as stream:
        stream.write(row.model_dump_json() + "\n")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row(
    proposal: Proposal,
    *,
    train_before: float,
    train_after: float,
    dev_before: float,
    dev_after: float,
    accepted: bool,
    refused: bool = False,
) -> MutationRecord:
    return MutationRecord(
        ts=_now(),
        component=proposal.component,
        diff_sha=hashlib.sha256(proposal.diff.encode()).hexdigest(),
        train_before=train_before,
        train_after=train_after,
        dev_before=dev_before,
        dev_after=dev_after,
        accepted=accepted,
        cited_traces=proposal.cited_failing_traces,
        refused=refused,
    )


def evolve(
    packet: DesignPacket,
    train_tasks: Sequence[Mapping[str, Any]],
    dev_tasks: Sequence[Mapping[str, Any]],
    propose: Callable[[EvalReport, str | None], Proposal],
    guidance: str | None = None,
    max_iters: int = 5,
) -> list[MutationRecord]:
    if max_iters < 0:
        raise ValueError("max_iters cannot be negative")
    records: list[MutationRecord] = []
    with tempfile.TemporaryDirectory(prefix="rdh-evolve-") as directory:
        workspace = Path(directory)
        current = workspace / "current"
        _render_all(packet, current)
        for iteration in range(1, max_iters + 1):
            train_before_report = _score(packet, train_tasks, current)
            report = EvalReport(
                iteration=iteration,
                train=train_before_report,
                failing_traces=[
                    result.task_id for result in train_before_report.per_task if result.score < 1.0
                ],
            )
            proposal = propose(report, guidance)
            touched = _touched_components(proposal.diff, proposal.component)
            if len(touched) != 1 or touched != {proposal.component}:
                row = _row(
                    proposal,
                    train_before=train_before_report.score_mean,
                    train_after=train_before_report.score_mean,
                    dev_before=0.0,
                    dev_after=0.0,
                    accepted=False,
                    refused=True,
                )
                _record(row)
                records.append(row)
                continue

            candidate = workspace / f"candidate-{iteration}"
            shutil.copytree(current, candidate)
            component = importlib.import_module(f"harness.components.{proposal.component}")
            try:
                component.mutate(_component_files(candidate, proposal.component), proposal)
            except ValueError:
                row = _row(
                    proposal,
                    train_before=train_before_report.score_mean,
                    train_after=train_before_report.score_mean,
                    dev_before=0.0,
                    dev_after=0.0,
                    accepted=False,
                    refused=True,
                )
                _record(row)
                records.append(row)
                continue

            train_after_report = _score(packet, train_tasks, candidate)
            dev_before_report = _score(packet, dev_tasks, current)
            dev_after_report = _score(packet, dev_tasks, candidate)
            accepted = (
                train_after_report.score_mean > train_before_report.score_mean
                and dev_after_report.score_mean >= dev_before_report.score_mean - 0.5
            )
            row = _row(
                proposal,
                train_before=train_before_report.score_mean,
                train_after=train_after_report.score_mean,
                dev_before=dev_before_report.score_mean,
                dev_after=dev_after_report.score_mean,
                accepted=accepted,
            )
            _record(row)
            records.append(row)
            if accepted:
                current = candidate
    return records
