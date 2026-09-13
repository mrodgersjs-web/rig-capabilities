"""Tool-selection standard — the authority-owned T1-T8 owner table.

Carrier ownership is evidence-driven with NO default owner. Work facts select
the carrier in precedence order: clock/catch-up recovery (T3 Temporal),
resident held resources (T4 launchd), genuine graph cycles/backtracking
(T6 LangGraph), human judgment coordination (T5 Orca + Pydantic AI), ordinary
cadence (T2 Kestra), pure computation (T1 Plain Python). Missing, absent, or
unconverting facts raise TOOL_SELECTION_UNRESOLVED naming the missing facts —
never a silent Kestra default.

LangChain is never a carrier: it may attach as an optional integration library
only to a T6 LangGraph selection with an explicit integration fact. Model
necessity (MODEL operation allowance) is granted only by the source-inventoried
``model_necessity_claims`` list plus an evidenced ``agent_reasoning`` record —
never by a framework name containing "pydantic".

Operation ownership is separate: deterministic work is ``code`` and justified
typed Pydantic-AI work is ``model``. Outward effects select no framework: an
evidenced ``outward_effect`` fact names the deterministic executor behind
Gate-D (T8). T7 controls are deterministic code, never selected here.

This module is pure deterministic code. Evidence claims use closed records;
contradicted claims block rather than becoming silent FALSE. There is no model
input, no environment override, and no caller override of the rule chain.

The T1-T8 owner table and carrier precedence are read at runtime from
``authority/standards/tool_selection.v2.json`` (the machine-readable
contract). The code holds no inline table; a missing or schema-mismatched
standard is a named refusal, never a fallback to code-resident defaults.
"""


from __future__ import annotations

import datetime as _dt
import hashlib
import json
import math
import re
import sys
from pathlib import Path

STANDARD_VERSION = "rig.d85.tool-selection.v4"

# The authority standard is the runtime contract that select_framework
# executes. Cached per resolved source path; re-read if the path changes.
STANDARD_FILE = (Path(__file__).resolve().parent
                 / "authority" / "standards" / "tool_selection.v2.json")
_STANDARD_CACHE: tuple[str, dict] | None = None

PROPERTY_KEYS = frozenset(
    {
        "clock_critical",
        "resident_service",
        "non_engineer_surface",
        "multi_agent_graph",
        "agent_reasoning",
        "deterministic_step",
        "ordinary_schedule",
        "outward_effect",
        "langchain_integration",
    }
)

FRAMEWORKS = frozenset(
    {"kestra", "temporal", "launchd", "orca_pydantic", "langgraph", "plain_python"}
)
LEGACY_MAP = {
    "kestra_pydantic": "kestra",
    "flowise": "kestra",
    "langchain": "langgraph",
}
_LEGACY_MAP = LEGACY_MAP

# Closed evidence schemas: a property claim is a record over exactly these
# fields. Acceptance predicates are enforced in _accepts_* below.
RESOURCE_KINDS = frozenset(
    {"listening_socket", "watched_directory", "hardware_connection", "os_event_sub_second"}
)
GRAPH_SHAPES = frozenset(
    {"cycle", "dynamic_router", "distributed_tracing", "context_compression"}
)
OVERLAP_POLICIES = frozenset({"forbid", "allow", "queue"})
EVIDENCE_FIELDS = {
    "clock_critical": (
        "consumer",
        "start_latency_ms",
        "catch_up_policy",
        "mechanism",
        "deployment_evidence",
    ),
    "resident_service": ("resource_kind", "resource_detail"),
    "non_engineer_surface": ("maintainer", "maintainer_is_engineer", "expiry_date"),
    "multi_agent_graph": ("graph_shape", "description", "agent_count", "genuine_cycles"),
    "agent_reasoning": ("unstructured_input", "deterministic_alternative", "alternative_rejected_because"),
    "deterministic_step": ("steps", "model_countermeasures"),
    "ordinary_schedule": ("cadence", "overlap_policy", "missed_run_policy"),
    "outward_effect": ("channel", "effect_detail", "gate_d_class"),
    "langchain_integration": ("reason", "integration_point"),
}

# T7 (controls) and T8 (effects) are never selected as frameworks here:
# controls are deterministic code; effects route to this executor behind Gate-D.
OUTWARD_EFFECT_EXECUTOR = "gate-d-deterministic-executor"



def _standard_contract() -> dict:
    """Load and validate the machine-readable owner contract.

    Returns {"precedence": [(fact, carrier, rule, work_type), ...],
             "contradictions": [(facts, code, detail), ...]}.
    Fail-closed: a missing, unreadable, or schema-mismatched standard raises
    TOOL_STANDARD_UNAVAILABLE — there is no code-resident fallback table.
    """
    global _STANDARD_CACHE
    source = str(STANDARD_FILE)
    if _STANDARD_CACHE is not None and _STANDARD_CACHE[0] == source:
        return _STANDARD_CACHE[1]
    try:
        raw = json.loads(Path(source).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ToolSelectionBlock(
            "TOOL_STANDARD_UNAVAILABLE",
            f"authority tool-selection standard unreadable at {source}: {exc}",
        ) from exc
    if not isinstance(raw, dict) or raw.get("schema") != "rig.d85.tool-selection.standard.v2":
        raise ToolSelectionBlock(
            "TOOL_STANDARD_UNAVAILABLE",
            f"unexpected authority standard schema: {raw.get('schema') if isinstance(raw, dict) else type(raw).__name__!r}",
        )
    if raw.get("selection_contract") != STANDARD_VERSION:
        raise ToolSelectionBlock(
            "TOOL_STANDARD_UNAVAILABLE",
            f"standard names selection_contract {raw.get('selection_contract')!r} but this runtime is {STANDARD_VERSION!r}",
        )
    rows = raw.get("owner_table")
    if not isinstance(rows, list) or not rows:
        raise ToolSelectionBlock("TOOL_STANDARD_UNAVAILABLE", "owner_table must be a non-empty list")
    by_rule: dict[str, dict] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or not isinstance(row.get("rule"), str):
            raise ToolSelectionBlock(
                "TOOL_STANDARD_UNAVAILABLE", f"owner_table[{index}] must be an object with a rule"
            )
        by_rule[row["rule"]] = row
    precedence = raw.get("precedence")
    if not isinstance(precedence, list) or not precedence:
        raise ToolSelectionBlock("TOOL_STANDARD_UNAVAILABLE", "precedence must be a non-empty list")
    order: list[tuple[str, str, str, str]] = []
    seen: set[str] = set()
    for index, entry in enumerate(precedence):
        _nonempty_entry(entry, f"precedence[{index}]")
        fact = entry.split(" ", 1)[0]
        if fact not in PROPERTY_KEYS:
            raise ToolSelectionBlock(
                "TOOL_STANDARD_UNAVAILABLE", f"precedence[{index}] names unknown fact {fact!r}"
            )
        if fact in seen:
            raise ToolSelectionBlock(
                "TOOL_STANDARD_UNAVAILABLE", f"precedence[{index}] repeats fact {fact!r}"
            )
        seen.add(fact)
        rule_match = re.search(r"\((T[1-6])\)", entry)
        if rule_match is None:
            raise ToolSelectionBlock(
                "TOOL_STANDARD_UNAVAILABLE", f"precedence[{index}] names no rule (T1..T6)"
            )
        rule = rule_match.group(1)
        row = by_rule.get(rule)
        carrier = row.get("carrier") if row else None
        if carrier not in FRAMEWORKS:
            raise ToolSelectionBlock(
                "TOOL_STANDARD_UNAVAILABLE",
                f"owner_table rule {rule} carries no selectable carrier: {carrier!r}",
            )
        order.append((fact, carrier, rule, str(row.get("work_type", ""))))
    contradictions: list[tuple[tuple[str, ...], str, str]] = []
    for index, pair in enumerate(raw.get("contradictory_fact_pairs") or []):
        if (not isinstance(pair, dict) or not isinstance(pair.get("facts"), list)
                or not pair["facts"] or any(f not in PROPERTY_KEYS for f in pair["facts"])
                or not isinstance(pair.get("code"), str) or not pair["code"].strip()
                or not isinstance(pair.get("detail"), str) or not pair["detail"].strip()):
            raise ToolSelectionBlock(
                "TOOL_STANDARD_UNAVAILABLE",
                f"contradictory_fact_pairs[{index}] must name known facts, a code, and a detail",
            )
        contradictions.append((tuple(pair["facts"]), pair["code"], pair["detail"]))
    contract = {"precedence": order, "contradictions": contradictions}
    _STANDARD_CACHE = (source, contract)
    return contract


def _nonempty_entry(entry: object, where: str) -> None:
    if not isinstance(entry, str) or not entry.strip():
        raise ToolSelectionBlock(
            "TOOL_STANDARD_UNAVAILABLE", f"{where} must be a non-empty string"
        )


class ToolSelectionBlock(Exception):
    """Fail-closed tool-selection verdict."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail

    def as_dict(self) -> dict:
        return {"schema": "rig.d85.tool-selection-block.v1", "code": self.code, "detail": self.detail}


def _nonempty(value: object, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ToolSelectionBlock("TOOL_SELECTION_MALFORMED", f"{where} must be a non-empty string")
    return value

def _enum(value: object, allowed: frozenset, where: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise ToolSelectionBlock(
            "TOOL_SELECTION_MALFORMED", f"{where} must be one of {sorted(allowed)}"
        )
    return value


def _boolean_field(value: object, where: str) -> bool:
    if not isinstance(value, bool):
        raise ToolSelectionBlock("TOOL_SELECTION_MALFORMED", f"{where} must be boolean")
    return value


def _string_list(value: object, where: str) -> list:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ToolSelectionBlock("TOOL_SELECTION_MALFORMED", f"{where} must be a list of non-empty strings")
    return value


def _validate_record(prop: str, record: object) -> dict:
    if not isinstance(record, dict):
        raise ToolSelectionBlock(
            "TOOL_SELECTION_MALFORMED",
            f"property {prop!r} must be an evidence record object, not {type(record).__name__}",
        )
    expected = set(EVIDENCE_FIELDS[prop])
    missing = expected - set(record)
    unknown = set(record) - expected
    if missing or unknown:
        parts = []
        if missing:
            parts.append(f"missing fields {sorted(missing)}")
        if unknown:
            parts.append(f"unknown fields {sorted(unknown)}")
        raise ToolSelectionBlock(
            "TOOL_SELECTION_MALFORMED", f"evidence record {prop!r}: " + "; ".join(parts)
        )
    return record


def _accepts(prop: str, record: dict) -> bool:
    """The CODE-derived acceptance predicate for a well-formed record."""
    if prop == "clock_critical":
        _nonempty(record["consumer"], "clock_critical.consumer")
        latency = record["start_latency_ms"]
        if not isinstance(latency, int) or isinstance(latency, bool):
            raise ToolSelectionBlock(
                "TOOL_SELECTION_MALFORMED",
                "clock_critical.start_latency_ms must be an integer",
            )
        _nonempty(record["catch_up_policy"], "clock_critical.catch_up_policy")
        _nonempty(record["mechanism"], "clock_critical.mechanism")
        _nonempty(record["deployment_evidence"], "clock_critical.deployment_evidence")
        if not (1 <= latency <= 60000):
            raise ToolSelectionBlock(
                "TOOL_SELECTION_MALFORMED",
                f"clock_critical claim contradicted: start_latency_ms={latency} is outside 1..60000; a looser SLA is not clock-critical (use Kestra)",
            )
        if record["catch_up_policy"] != "catch_up":
            raise ToolSelectionBlock(
                "TOOL_SELECTION_MALFORMED",
                "clock_critical claim contradicted: catch_up_policy must be 'catch_up'; skip-on-miss is an ordinary schedule (use Kestra)",
            )
        return True
    if prop == "resident_service":
        _enum(record["resource_kind"], RESOURCE_KINDS, "resident_service.resource_kind")
        _nonempty(record["resource_detail"], "resident_service.resource_detail")
        return True
    if prop == "non_engineer_surface":
        _boolean_field(record["maintainer_is_engineer"], "non_engineer_surface.maintainer_is_engineer")
        _nonempty(record["maintainer"], "non_engineer_surface.maintainer")
        expiry = record["expiry_date"]
        if expiry is not None:
            if not isinstance(expiry, str):
                raise ToolSelectionBlock("TOOL_SELECTION_MALFORMED", "non_engineer_surface.expiry_date must be 'YYYY-MM-DD' or null")
            try:
                _dt.date.fromisoformat(expiry)
            except ValueError as exc:
                raise ToolSelectionBlock("TOOL_SELECTION_MALFORMED", f"non_engineer_surface.expiry_date: {exc}") from exc
        if record["maintainer_is_engineer"] and expiry is None:
            raise ToolSelectionBlock(
                "TOOL_SELECTION_MALFORMED",
                "non_engineer_surface claim contradicted: engineer maintainer with no expiry date is an internal tool, not a non-engineer surface (rerun selection without the claim)",
            )
        return True
    if prop == "multi_agent_graph":
        _enum(record["graph_shape"], GRAPH_SHAPES, "multi_agent_graph.graph_shape")
        count = record["agent_count"]
        if not isinstance(count, int) or isinstance(count, bool):
            raise ToolSelectionBlock("TOOL_SELECTION_MALFORMED", "multi_agent_graph.agent_count must be an integer")
        _nonempty(record["description"], "multi_agent_graph.description")
        genuine = _boolean_field(record["genuine_cycles"], "multi_agent_graph.genuine_cycles")
        if count < 3:
            raise ToolSelectionBlock(
                "TOOL_SELECTION_MALFORMED",
                f"multi_agent_graph claim contradicted: agent_count={count} < 3; a linear chain is not a graph (use Pydantic AI)",
            )
        if record["graph_shape"] == "cycle" and not genuine:
            raise ToolSelectionBlock(
                "TOOL_SELECTION_MALFORMED",
                "multi_agent_graph claim contradicted: genuine_cycles=false on a claimed cycle — without real "
                "cycles/backtracking this is a pipeline (schedule it or run it in plain code); "
                "multiple agents alone do not qualify LangGraph",
            )
        return genuine
    if prop == "agent_reasoning":
        _nonempty(record["unstructured_input"], "agent_reasoning.unstructured_input")
        _nonempty(record["deterministic_alternative"], "agent_reasoning.deterministic_alternative")
        _nonempty(record["alternative_rejected_because"], "agent_reasoning.alternative_rejected_because")
        return True
    if prop == "ordinary_schedule":
        _nonempty(record["cadence"], "ordinary_schedule.cadence")
        _enum(record["overlap_policy"], OVERLAP_POLICIES, "ordinary_schedule.overlap_policy")
        missed = _nonempty(record["missed_run_policy"], "ordinary_schedule.missed_run_policy")
        if missed == "catch_up":
            raise ToolSelectionBlock(
                "TOOL_SELECTION_MALFORMED",
                "ordinary_schedule claim contradicted: missed_run_policy 'catch_up' is durable clock-critical recovery — "
                "file a clock_critical claim (T3 Temporal), not an ordinary schedule (T2 Kestra)",
            )
        return True
    if prop == "outward_effect":
        _nonempty(record["channel"], "outward_effect.channel")
        _nonempty(record["effect_detail"], "outward_effect.effect_detail")
        _nonempty(record["gate_d_class"], "outward_effect.gate_d_class")
        return True
    if prop == "langchain_integration":
        _nonempty(record["reason"], "langchain_integration.reason")
        _nonempty(record["integration_point"], "langchain_integration.integration_point")
        return True
    if prop == "deterministic_step":
        steps = record["steps"]
        if not isinstance(steps, list):
            raise ToolSelectionBlock(
                "TOOL_SELECTION_MALFORMED",
                "deterministic_step.steps must be a list of {step, mechanism} objects",
            )
        for index, step in enumerate(steps):
            if not isinstance(step, dict) or set(step) != {"step", "mechanism"}:
                raise ToolSelectionBlock(
                    "TOOL_SELECTION_MALFORMED",
                    f"deterministic_step.steps[{index}] must contain exactly step and mechanism",
                )
            _nonempty(step["step"], f"deterministic_step.steps[{index}].step")
            _nonempty(step["mechanism"], f"deterministic_step.steps[{index}].mechanism")
        _string_list(
            record["model_countermeasures"],
            "deterministic_step.model_countermeasures",
        )
        return True
    raise ToolSelectionBlock("TOOL_SELECTION_MALFORMED", f"no acceptance predicate for {prop!r}")  # pragma: no cover


def derive_properties(properties: dict) -> dict:
    """Validate every claimed evidence record and derive the nine booleans.

    Absent property -> False (not claimed). Present property -> complete record
    whose evidence satisfies the CODE predicate, else BLOCK.
    """
    if not isinstance(properties, dict):
        raise ToolSelectionBlock("TOOL_SELECTION_MALFORMED", "properties must be an object")
    unknown = set(properties) - PROPERTY_KEYS
    if unknown:
        raise ToolSelectionBlock(
            "TOOL_SELECTION_MALFORMED", f"unknown properties: {sorted(unknown)}"
        )
    derived = {key: False for key in PROPERTY_KEYS}
    for prop, record in properties.items():
        derived[prop] = _accepts(prop, _validate_record(prop, record))
    return derived


def select_framework(
    evidence: dict | str,
    *,
    model_necessity_claims: list | None = None,
) -> dict:
    """Select trigger and operation owners from closed evidence.

    There is no default carrier. A direct token input is compatibility
    metadata only: it never overrides the evidence chain, so a token with no
    facts raises TOOL_SELECTION_UNRESOLVED naming the missing carrier facts.
    """
    if model_necessity_claims is not None:
        _string_list(model_necessity_claims, "model_necessity_claims")
    claims = model_necessity_claims or []

    token = None
    remap = None
    if isinstance(evidence, str):
        token = _nonempty(evidence, "framework")
        if token not in FRAMEWORKS and token not in LEGACY_MAP:
            raise ToolSelectionBlock(
                "TOOL_SELECTION_MALFORMED",
                f"framework must be one of {sorted(FRAMEWORKS | set(LEGACY_MAP))}",
            )
        remap = LEGACY_MAP.get(token)
        properties = {}
    elif isinstance(evidence, dict):
        properties = evidence
    else:
        raise ToolSelectionBlock(
            "TOOL_SELECTION_MALFORMED",
            "evidence must be a closed property object or framework token",
        )

    if "clock_critical" in properties:
        record = properties["clock_critical"]
        required = set(EVIDENCE_FIELDS["clock_critical"])
        missing = sorted(required - set(record)) if isinstance(record, dict) else sorted(required)
        if missing:
            raise ToolSelectionBlock(
                "temporal_evidence_incomplete",
                "missing fields "
                f"{missing}; the temporal claim needs consumer, start_latency_ms, "
                "catch_up_policy, mechanism, deployment_evidence",
            )

    derived = derive_properties(properties)
    # MODEL allowance comes only from the source-inventoried claims list plus
    # an evidenced agent_reasoning record — never from a framework name.
    operation_owner = (
        "model"
        if derived["agent_reasoning"] and claims
        else None
        if derived["agent_reasoning"]
        else "code"
    )

    # Owner precedence is the authority contract's, read at runtime:
    # clock/recovery -> resident -> genuine graph -> human coordination ->
    # ordinary schedule -> pure computation. No default row exists.
    contract = _standard_contract()
    for facts, code, detail in contract["contradictions"]:
        if all(derived[fact] for fact in facts):
            raise ToolSelectionBlock(code, detail)
    framework = None
    for fact, carrier, _rule, _work_type in contract["precedence"]:
        if derived[fact]:
            framework = carrier
            break
    if framework is None:
        missing_facts = "; ".join(
            f"{fact} — {work_type} [{rule} -> {carrier}]"
            for fact, carrier, rule, work_type in contract["precedence"]
        )
        detail = (
            "carrier UNRESOLVED: no required carrier fact is claimed, and no default owner exists. "
            f"Supply exactly the facts that apply: {missing_facts}"
        )
        if derived["outward_effect"]:
            detail += (
                " (outward_effect names the Gate-D deterministic executor for its effects; "
                "it is not a carrier fact)"
            )
        if derived["langchain_integration"]:
            detail += (
                " (langchain_integration attaches only to a T6 LangGraph carrier; "
                "LangChain is never a carrier)"
            )
        raise ToolSelectionBlock("TOOL_SELECTION_UNRESOLVED", detail)

    integration_library = None
    if derived["langchain_integration"]:
        if framework != "langgraph":
            raise ToolSelectionBlock(
                "TOOL_SELECTION_MALFORMED",
                "langchain_integration claim contradicted: LangChain is an optional integration "
                f"library for the T6 LangGraph carrier, never a carrier — the selected carrier is {framework!r}; "
                "drop the integration claim or resolve the graph facts",
            )
        integration_library = "langchain"

    executor = OUTWARD_EFFECT_EXECUTOR if derived["outward_effect"] else None

    canonical = json.dumps(
        {
            "evidence": properties,
            "model_necessity_claims": claims,
            "legacy": {
                "token": token,
                "remap": remap,
                "non_canonical": token == "flowise",
            },
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return {
        "framework": framework,
        "operation_owner": operation_owner,
        "owner_evidence_digest": "sha256:" + hashlib.sha256(canonical).hexdigest(),
        "legacy_remap": token if remap is not None else None,
        "executor": executor,
        "integration_library": integration_library,
    }


CHECKLIST_KEYS = frozenset(
    {
        "process_id",
        "properties",
        "framework",
        "durable_system",
        "pydantic_models",
        "model_necessity_claims",
        "archify_diagram_path",
        "inventory_sha256",
        "d85_realized_pass",
        "orchestration_is_code",
        "lattice",
    }
)


def validate_lattice(context: object, *, root: Path | None = None) -> dict:
    if not isinstance(context, dict) or set(context) != {"cell_id", "bms", "a1_failure"}:
        raise ToolSelectionBlock("LATTICE_MALFORMED", "lattice requires exactly cell_id, bms, a1_failure")
    criteria = context["bms"]
    fields = {"failure_cost", "reversibility", "mechanism_clarity", "past_failure_rate", "data_volume", "level"}
    if not isinstance(criteria, dict) or set(criteria) != fields:
        raise ToolSelectionBlock("LATTICE_MALFORMED", "bms must contain all five numeric criteria and level")
    cell_id = _nonempty(context["cell_id"], "lattice.cell_id")
    canonical_root = Path(__file__).resolve().parent.parent / "rig-lattice-system"
    if str(canonical_root) not in sys.path:
        sys.path.insert(0, str(canonical_root))
    try:
        from rig_lattice.lattice import bms, validator
        if any(not Path(module.__file__).resolve().is_relative_to(canonical_root)
               for module in (bms, validator)):
            raise ValueError("lattice implementation is not the canonical installed capability")
        cell = validator.parse_cell_id(cell_id)
        if cell.cell_id != cell_id or criteria["level"] != cell.level.value:
            raise ValueError("cell must be canonical and its level must match bms.level")
        result = bms.compute_bms(**criteria)
        if result.mode != cell.bms_mode:
            raise ValueError("cell mode does not match recomputed BMS mode")
    except (ImportError, TypeError, ValueError, AttributeError) as exc:
        raise ToolSelectionBlock("LATTICE_BLOCK", str(exc)) from exc
    failure = context["a1_failure"]
    if failure is not None:
        if not isinstance(failure, dict) or set(failure) != {"command", "exit_code", "evidence_path", "evidence_sha256"}:
            raise ToolSelectionBlock("LATTICE_MALFORMED", "a1_failure requires command, exit_code, evidence_path, evidence_sha256")
        _nonempty(failure["command"], "a1_failure.command")
        if type(failure["exit_code"]) is not int or failure["exit_code"] == 0:
            raise ToolSelectionBlock("LATTICE_BLOCK", "A1 failure must record a nonzero integer exit code")
        base = (root or Path.cwd()).resolve()
        evidence_path = (base / _nonempty(failure["evidence_path"], "a1_failure.evidence_path")).resolve()
        if not evidence_path.is_relative_to(base):
            raise ToolSelectionBlock("LATTICE_BLOCK", "A1 failure evidence escapes the build root")
        try:
            raw = evidence_path.read_bytes()
            evidence = json.loads(raw)
            if hashlib.sha256(raw).hexdigest() != failure["evidence_sha256"]:
                raise ValueError("recorded A1 failure evidence hash changed")
            if (not isinstance(evidence, dict) or evidence.get("command") != failure["command"]
                    or type(evidence.get("exit_code")) is not int
                    or evidence["exit_code"] != failure["exit_code"]
                    or not isinstance(evidence.get("output"), str) or not evidence["output"].strip()):
                raise ValueError("recorded A1 failure must match command/exit and contain output")
        except (OSError, ValueError, TypeError) as exc:
            raise ToolSelectionBlock("LATTICE_BLOCK", str(exc)) from exc
    if not cell.is_a1:
        raise ToolSelectionBlock(
            "LATTICE_BLOCK",
            "higher-mode certification requires a trusted A1 execution receipt; "
            "recorded failure files are reference evidence only and cannot authorize escalation",
        )
    return {"cell_id": cell.cell_id, "bms": result.to_dict(), "a1_failure": failure}


def check_build_checklist(build: dict, *, root: Path | None = None) -> dict:
    """The gate before going forward. Every item must be checked off.

    `root` resolves relative archify_diagram_path values (defaults to cwd).
    A missing or failing item blocks; there is no partial pass.
    """
    if not isinstance(build, dict):
        raise ToolSelectionBlock("TOOL_SELECTION_MALFORMED", "build must be an object")
    missing = CHECKLIST_KEYS - set(build)
    if missing:
        raise ToolSelectionBlock(
            "TOOL_SELECTION_MALFORMED", f"missing checklist fields: {sorted(missing)}"
        )
    unknown = set(build) - CHECKLIST_KEYS
    if unknown:
        raise ToolSelectionBlock(
            "TOOL_SELECTION_MALFORMED", f"unknown checklist fields: {sorted(unknown)}"
        )

    # Typed field validation: no untrusted shape may crash or pass via truthiness.
    if not isinstance(build["properties"], dict):
        raise ToolSelectionBlock("TOOL_SELECTION_MALFORMED", "properties must be an object")
    _enum(build["framework"], FRAMEWORKS, "framework")
    _boolean_field(build["durable_system"], "durable_system")
    _string_list(build["pydantic_models"], "pydantic_models")
    _string_list(build["model_necessity_claims"], "model_necessity_claims")
    _nonempty(build["process_id"], "process_id")
    if not re.fullmatch(r"[0-9a-f]{64}", _nonempty(build["inventory_sha256"], "inventory_sha256")):
        raise ToolSelectionBlock(
            "TOOL_SELECTION_MALFORMED",
            "inventory_sha256 must be a 64-character lowercase hex digest of the "
            "inventory snapshot this checklist was generated against",
        )
    _nonempty(build["archify_diagram_path"], "archify_diagram_path")
    _boolean_field(build["d85_realized_pass"], "d85_realized_pass")
    _boolean_field(build["orchestration_is_code"], "orchestration_is_code")
    lattice = validate_lattice(build["lattice"], root=root)

    checks: list[dict] = []

    def record(name: str, ok: bool, detail: str) -> None:
        checks.append({"check": name, "pass": ok is True, "detail": detail})

    record("rig_lattice", True, json.dumps(lattice, sort_keys=True, separators=(",", ":")))
    expected = select_framework(
        build["properties"],
        model_necessity_claims=build["model_necessity_claims"],
    )
    framework = build["framework"]
    record(
        "framework_matches_standard",
        framework == expected["framework"],
        f"declared {framework!r}, standard requires {expected['framework']!r}",
    )

    record(
        "flowise_not_durable",
        not (
            build["properties"].get("framework") == "flowise"
            and build["durable_system"] is True
        ),
        "flowise maps to kestra and is prototype-only; a durable system must not carry the legacy flowise token",
    )

    derived = derive_properties(build["properties"])
    needs_models = bool(
        derived["agent_reasoning"]
        or derived["multi_agent_graph"]
        or expected["operation_owner"] == "model"
    )
    record(
        "pydantic_models_present",
        bool(build["pydantic_models"]) or not needs_models,
        "every MODEL op needs typed pydantic input/output schemas",
    )

    record(
        "model_necessity_claims_present",
        bool(build["model_necessity_claims"]) or not needs_models,
        "every MODEL op needs a D85 necessity record",
    )

    diagram = Path(build["archify_diagram_path"])
    escaped = False
    if root is not None:
        base = root.resolve()
        candidate = (root / diagram).resolve() if not diagram.is_absolute() else diagram.resolve()
        if candidate.is_relative_to(base):
            diagram = candidate
        else:
            # A submission pointing outside its declared root is traversal, not evidence.
            escaped = True
            diagram_detail = f"{build['archify_diagram_path']}: escapes the declared root {base}"
    declared = build["archify_diagram_path"]
    diagram_ok = False
    diagram_detail = diagram_detail if escaped else f"{declared}: unreadable"
    if not escaped:
        try:
            raw = diagram.read_bytes()
            parsed = json.loads(raw.decode("utf-8"))
            diagram_ok = isinstance(parsed, dict) and "diagram_type" in parsed
            diagram_detail = (
                f"{declared}: missing diagram_type" if not diagram_ok
                else "{}: {} sha256:{}".format(
                    declared,
                    parsed.get("diagram_type"),
                    hashlib.sha256(raw).hexdigest(),
                )
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            diagram_ok = False
            diagram_detail = f"{declared}: {exc}"
    record("archify_diagram_present", diagram_ok, diagram_detail)

    record(
        "d85_realized_pass",
        build["d85_realized_pass"] is True,
        "four-ratio D85 score must be REALIZED_PASS before the build goes forward",
    )
    record(
        "orchestration_is_code",
        build["orchestration_is_code"] is True,
        "schedule, retry, timeout, cancellation, and dispatch must be deterministic code, never model-decided",
    )

    passed = all(item["pass"] for item in checks)
    return {
        "schema": "rig.d85.build-checklist.v1",
        "verdict": "CHECKLIST_PASS" if passed else "CHECKLIST_BLOCK",
        "expected_framework": expected["framework"],
        "inventory_binding": "unbound",
        "inventory_sha256": None,
        "checks": checks,
    }


def checklist_digest(build: dict) -> str:
    """Deterministic digest over the full closed-schema build record.

    Canonical JSON (sorted keys, compact separators) so key order in the
    submitted file cannot change what a certificate names.
    """

    canonical = json.dumps({key: build[key] for key in sorted(CHECKLIST_KEYS)},
                           sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def certify_build(build: dict, process_id: str | None, *, root: Path | None = None) -> dict:
    """Enforcement certification: a checklist verdict bound to an inventory hash.

    This is the only path that produces inventory_binding="bound". A direct
    check_build_checklist() PASS is always self-described as unbound and is not
    an enforcement verdict.
    """
    result = check_build_checklist(build, root=root)
    result["checklist_sha256"] = checklist_digest(build)
    if not process_id:
        result["verdict"] = "CHECKLIST_BLOCK"
        result["binding_reason"] = (
            "enforcement verdicts must be bound to an inventory hash: "
            "pass --process-id so this pass names the exact code snapshot it certifies"
        )
        return result
    if build["process_id"] != process_id:
        result["inventory_binding"] = "mismatched"
        result["verdict"] = "CHECKLIST_BLOCK"
        result["binding_reason"] = (
            f"checklist declares process_id {build['process_id']!r} but the certification "
            f"target is {process_id!r} — a build may only be certified against "
            "the process it claims to describe"
        )
        return result
    from d85 import build_inventory
    current = build_inventory(process_id)["inventory_sha256"]
    if build["inventory_sha256"] != current:
        result["inventory_binding"] = "stale"
        result["verdict"] = "CHECKLIST_BLOCK"
        result["binding_reason"] = (
            f"checklist was generated against inventory {build['inventory_sha256'][:12]}… "
            f"but the live inventory is {current[:12]}… — regenerate the checklist "
            "against the current snapshot before certifying"
        )
        return result
    result["inventory_sha256"] = current
    result["inventory_binding"] = "bound"
    from d85_gates import score_process
    try:
        score = score_process(process_id)
        ratios = score.get("ratios", {})
        score_ok = (
            score.get("verdict") == "REALIZED_PASS"
            and score.get("process_id") == process_id
            and score.get("inventory_sha256") == current
            and set(ratios) == {"aggregate_unweighted", "aggregate_weighted", "min_path_unweighted", "min_path_weighted"}
            and all(type(value) in (int, float) and math.isfinite(value) and 0.85 <= value <= 1
                    for value in ratios.values())
            and type(score.get("scored_operation_count")) is int
            and score["scored_operation_count"] > 0
        )
        detail = json.dumps(score, sort_keys=True, separators=(",", ":"))
    except Exception as exc:
        score_ok = False
        detail = f"live source-derived D85 scoring failed: {exc}"
    result["checks"].append({"check": "source_derived_d85", "pass": score_ok, "detail": detail})
    if not score_ok:
        result["verdict"] = "CHECKLIST_BLOCK"
        result["binding_reason"] = "source-derived D85 score did not prove all four ratios >= 0.85"
    # A12: MODEL allowance keys off the source-inventoried classification,
    # never off a framework name or the checklist's own claim count. A build
    # that claims model necessity with no MODEL-family operation in the live
    # inventory is refused fail-closed.
    claims = build.get("model_necessity_claims") or []
    if claims:
        from d85_gates import MODEL_KINDS, classify_process
        try:
            counts = classify_process(process_id).get("kind_counts", {})
            model_ops = sum(counts.get(kind, 0) for kind in MODEL_KINDS)
            model_ok = model_ops >= len(claims)
            model_detail = (f"{len(claims)} model_necessity_claims vs "
                            f"{model_ops} MODEL-family operations in the live inventory")
        except Exception as exc:
            model_ok = False
            model_detail = f"live source classification failed, refusing MODEL claims: {exc}"
        result["checks"].append({"check": "model_claims_inventoried", "pass": model_ok, "detail": model_detail})
        if not model_ok:
            result["verdict"] = "CHECKLIST_BLOCK"
            result["binding_reason"] = (
                "model_necessity_claims refused: the source-inventoried classification "
                f"does not carry them ({model_detail})"
            )
    return result


def verify_certification(build: dict, certificate: dict, *, root: Path | None = None) -> dict:
    """The consumer-side boundary: a saved certificate re-presented with a build.

    BLOCKs when the build itself is malformed (typed, never a KeyError), when
    the certificate is not an exact-schema bound CHECKLIST_PASS, when it does
    not name this exact build (post-cert mutation), or when the certificate's
    snapshot hash disagrees with the build's declared or the live inventory.
    """
    # Validate the build through the closed checklist schema first — a malformed
    # build raises a typed TOOL_SELECTION_MALFORMED before any digest is taken.
    check_build_checklist(build, root=root)

    CERTIFICATE_KEYS = frozenset(
        {
            "schema",
            "verdict",
            "expected_framework",
            "inventory_binding",
            "inventory_sha256",
            "checklist_sha256",
            "checks",
        }
    )
    if not isinstance(certificate, dict):
        raise ToolSelectionBlock("CERTIFICATION_MALFORMED", "certificate must be an object")
    unknown = set(certificate) - CERTIFICATE_KEYS
    missing = CERTIFICATE_KEYS - set(certificate)
    if unknown or missing:
        parts = []
        if missing:
            parts.append(f"missing fields {sorted(missing)}")
        if unknown:
            parts.append(f"unknown fields {sorted(unknown)}")
        raise ToolSelectionBlock("CERTIFICATION_MALFORMED", "certificate: " + "; ".join(parts))
    if certificate["schema"] != "rig.d85.build-checklist.v1":
        raise ToolSelectionBlock("CERTIFICATION_MALFORMED", "certificate schema mismatch")

    def block(reason: str) -> dict:
        return {
            "schema": "rig.d85.certification-verify.v1",
            "verdict": "CERTIFICATION_BLOCK",
            "binding_reason": reason,
            "checklist_sha256": checklist_digest(build),
        }

    if certificate["verdict"] != "CHECKLIST_PASS" or certificate["inventory_binding"] != "bound":
        return block(
            "only a bound CHECKLIST_PASS is an enforceable certificate "
            f"(saw verdict={certificate['verdict']!r}, binding={certificate['inventory_binding']!r})"
        )
    digest = checklist_digest(build)
    if digest != certificate["checklist_sha256"]:
        return block(
            "certificate does not name this build: the closed-schema build changed "
            "after certification (post-cert mutation replay)"
        )
    if certificate["inventory_sha256"] != build["inventory_sha256"]:
        return block(
            "certificate snapshot hash does not match the build's declared "
            "inventory_sha256 — tampered or mispaired certificate"
        )
    live = certify_build(build, build["process_id"], root=root)
    if live["verdict"] != "CHECKLIST_PASS":
        return block(f"re-certification against the live inventory failed: {live.get('binding_reason', live['verdict'])}")
    if certificate["inventory_sha256"] != live["inventory_sha256"]:
        return block(
            "certificate names inventory "
            f"{certificate['inventory_sha256'][:12]}… but the live inventory is "
            f"{live['inventory_sha256'][:12]}… — stale or tampered certificate"
        )
    if certificate["expected_framework"] != live["expected_framework"]:
        return block(
            "certificate expected_framework does not match re-certification "
            "— tampered certificate"
        )
    if certificate["checks"] != live["checks"]:
        return block(
            "certificate checks payload does not match re-certification "
            "— tampered certificate"
        )
    return {
        "schema": "rig.d85.certification-verify.v1",
        "verdict": "CERTIFICATION_VERIFIED",
        "checklist_sha256": digest,
        "inventory_sha256": live["inventory_sha256"],
    }
