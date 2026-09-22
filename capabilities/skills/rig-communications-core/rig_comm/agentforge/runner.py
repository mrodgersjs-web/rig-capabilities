from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List
import json

from ..core import evaluate
from ..integrations.guard import CommunicationGuard


@dataclass
class StepResult:
    step: str
    status: str
    output: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowRun:
    workflow_name: str
    status: str
    steps: List[StepResult]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_name": self.workflow_name,
            "status": self.status,
            "steps": [{"step": s.step, "status": s.status, "output": s.output} for s in self.steps],
        }


def load_workflow(path: str | Path) -> Dict[str, Any]:
    payload = Path(path).read_text(encoding="utf-8")
    return json.loads(payload)


def run_workflow(path: str | Path, inputs: Dict[str, Any] | None = None) -> WorkflowRun:
    spec = load_workflow(path)
    ctx: Dict[str, Any] = dict(inputs or {})
    results: List[StepResult] = []

    for step in spec.get("steps", []):
        name = step["name"]
        action = step.get("action")
        if action == "evaluate":
            text = str(ctx.get(step.get("input", "draft"), ""))
            report = evaluate(text, channel=step.get("channel", "email")).to_dict()
            key = step.get("output", "score")
            ctx[key] = report
            results.append(StepResult(step=name, status="ok", output=report))
        elif action == "guard":
            text = str(ctx.get(step.get("input", "draft"), ""))
            guard = CommunicationGuard(channel=step.get("channel", "email"), max_attempts=step.get("max_attempts", 2))
            guarded = guard.guard(text).to_dict()
            key = step.get("output", "verdict")
            ctx[key] = guarded
            results.append(StepResult(step=name, status="ok", output=guarded))
        elif action == "set":
            values = step.get("values", {})
            ctx.update(values)
            results.append(StepResult(step=name, status="ok", output=values))
        elif action == "human_approval":
            approved = bool(ctx.get(step.get("input", "approved"), False))
            out = {"approved": approved}
            results.append(StepResult(step=name, status="ok" if approved else "blocked", output=out))
            if not approved:
                return WorkflowRun(workflow_name=spec.get("name", "workflow"), status="blocked", steps=results)
        else:
            results.append(StepResult(step=name, status="skipped", output={"reason": f"unknown action '{action}'"}))

    return WorkflowRun(workflow_name=spec.get("name", "workflow"), status="ok", steps=results)
