from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class NumericContract(_StrictModel):
    metric: str
    op: Literal["<", "<=", "=", ">=", ">"]
    value: float
    unit: str


class Outcome(_StrictModel):
    statement: str
    numeric_contract: list[NumericContract] = Field(default_factory=list)
    done_event: str


class Persona(_StrictModel):
    bracket: str
    working_view: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    decision_about_to_make: str


class Doctrine(_StrictModel):
    id: str
    statement: str
    discover: str
    propose: str
    proof_signal: str
    mechanism: str


class HumanDecision(_StrictModel):
    who: str
    decides: str
    gate: str


class AskTestLearn(_StrictModel):
    surface: str
    ask_structure: str
    prediction: str
    test_card: str
    response_coding: str
    quality_gate: str
    review_cadence: str


class Proposition(_StrictModel):
    doctrine: str
    evidence: list[str]
    hypothesis: str
    gap: str
    mechanism: str
    proof: str
    surface: str
    prediction: str
    falsifier: str
    result: str | None = None




class Stage(_StrictModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True, serialize_by_alias=True)

    name: str
    kind: Literal["det", "llm"]
    schema_: str | None = Field(default=None, alias="schema")
    fallback: str | None = None
    gate: str | None = None
    serves: str | None = None
    block: Literal["collect", "protect", "work", "learn"] | None = None


class ProcessStart(_StrictModel):
    trigger: str
    source_of_truth: str


class ProcessStop(_StrictModel):
    outcome: str
    receipt: str


class Handoff(_StrictModel):
    to: str
    artifact: str


class Boundaries(_StrictModel):
    start: ProcessStart
    stop: ProcessStop
    handoffs: list[Handoff]


class KpiStage1(_StrictModel):
    stage: str
    signal: str
    source_of_truth: str
    baseline_today: float
    first_target: float


class Angle(_StrictModel):
    lens: Literal["systems", "behavioral", "COLLIDER", "BREAKER", "SURPRISE"]
    text: str
    kept: bool


class LaneSpec(_StrictModel):
    slug: str
    schedule_cron: str
    tz: str = "America/Denver"
    inputs: list[str]
    stages: list[Stage]
    caps: dict[str, int]
    executor: str
    healer_hooks: list[str]
    approval: Literal["standing", "per_action"]
    boundaries: Boundaries | None = None
    kpi_stage1: KpiStage1 | None = None
    angles: list[Angle] = Field(default_factory=list)
    process_map: str | None = None
    human_decisions: list[HumanDecision] = Field(default_factory=list)
    failure_rule: str | None = None
    ask_test_learn: AskTestLearn | None = None

    @property
    def det_ratio(self) -> float:
        return sum(stage.kind == "det" for stage in self.stages) / len(self.stages) if self.stages else 0.0


class Evaluation(_StrictModel):
    golden_dir: str
    evaluators: list[str]
    verifier_family: Literal["codex", "claude", "hermes", "omp"]
    thresholds: dict[str, float]


class Runtime(_StrictModel):
    carrier: Literal["temporal"] = "temporal"
    task_queue: str
    worker_plist: str
    ledger: Literal["phoenix", "langfuse", "local"]


class Context(_StrictModel):
    corpus_paths: list[str]
    memory_ns: str
    personas: list[Persona] = Field(default_factory=list)
    doctrines: list[Doctrine] = Field(default_factory=list)


class Tools(_StrictModel):
    adapters: list[str]
    mcp_manifest: str | None = None
    cap_policy: dict[str, int] = Field(default_factory=dict)


class DesignPacket(_StrictModel):
    instance: str
    cell_id: str
    lanes: list[LaneSpec]
    instance_outcomes: dict[str, Outcome] = Field(default_factory=dict)
    evaluation: Evaluation
    runtime: Runtime
    context: Context
    tools: Tools


class Report(_StrictModel):
    ok: bool
    findings: list[str]


class Proposal(_StrictModel):
    component: Literal["context", "tools", "runtime", "orchestration", "evaluation"]
    diff: str
    rationale: str
    cited_failing_traces: list[str]
