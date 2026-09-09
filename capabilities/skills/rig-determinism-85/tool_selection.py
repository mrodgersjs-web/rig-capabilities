"""Tool-selection standard — the authority-owned decision table for RIG automation.

Pydantic AI thinks, Kestra schedules, Temporal clocks, Orca reasons, launchd
serves. LangChain for graphs, Flowise for visuals (prototype only). Default to
Pydantic AI. Always.

Tool selection is a control-plane decision, so this module is pure deterministic
code. A property is never a bare boolean: claiming it requires a closed-schema
evidence record, and CODE derives the boolean from that record. A record whose
evidence fails its acceptance predicate is a contradicted claim and blocks —
it is never silently read as FALSE. An absent property is simply not claimed.

No model input, no environment overrides, no defaults beyond the declared
properties.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
from pathlib import Path

STANDARD_VERSION = "rig.d85.tool-selection.v1"

PROPERTY_KEYS = frozenset(
    {
        "clock_critical",
        "resident_service",
        "non_engineer_surface",
        "multi_agent_graph",
        "agent_reasoning",
    }
)

FRAMEWORKS = frozenset(
    {"kestra_pydantic", "temporal", "orca_pydantic", "langchain", "flowise", "launchd"}
)

# Closed evidence schemas: a property claim is a record over exactly these
# fields. Acceptance predicates are enforced in _accepts_* below.
RESOURCE_KINDS = frozenset(
    {"listening_socket", "watched_directory", "hardware_connection", "os_event_sub_second"}
)
GRAPH_SHAPES = frozenset(
    {"cycle", "dynamic_router", "distributed_tracing", "context_compression"}
)
EVIDENCE_FIELDS = {
    "clock_critical": ("named_consumer", "failure_mode", "sla_start_latency_seconds", "recovery_policy"),
    "resident_service": ("resource_kind", "resource_detail"),
    "non_engineer_surface": ("maintainer", "maintainer_is_engineer", "expiry_date"),
    "multi_agent_graph": ("graph_shape", "description", "agent_count"),
    "agent_reasoning": ("unstructured_input", "deterministic_alternative", "alternative_rejected_because"),
}


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
        _nonempty(record["named_consumer"], "clock_critical.named_consumer")
        _nonempty(record["failure_mode"], "clock_critical.failure_mode")
        sla = record["sla_start_latency_seconds"]
        if not isinstance(sla, int) or isinstance(sla, bool):
            raise ToolSelectionBlock("TOOL_SELECTION_MALFORMED", "clock_critical.sla_start_latency_seconds must be an integer")
        _enum(record["recovery_policy"], frozenset({"catch_up", "skip"}), "clock_critical.recovery_policy")
        if not (1 <= sla <= 60):
            raise ToolSelectionBlock(
                "TOOL_SELECTION_MALFORMED",
                f"clock_critical claim contradicted: sla_start_latency_seconds={sla} is outside 1..60; a looser SLA is not clock-critical (use Kestra)",
            )
        if record["recovery_policy"] != "catch_up":
            raise ToolSelectionBlock(
                "TOOL_SELECTION_MALFORMED",
                "clock_critical claim contradicted: recovery_policy must be 'catch_up'; skip-on-miss is an ordinary schedule (use Kestra)",
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
        if count < 3:
            raise ToolSelectionBlock(
                "TOOL_SELECTION_MALFORMED",
                f"multi_agent_graph claim contradicted: agent_count={count} < 3; a linear chain is not a graph (use Pydantic AI)",
            )
        return True
    if prop == "agent_reasoning":
        _nonempty(record["unstructured_input"], "agent_reasoning.unstructured_input")
        _nonempty(record["deterministic_alternative"], "agent_reasoning.deterministic_alternative")
        _nonempty(record["alternative_rejected_because"], "agent_reasoning.alternative_rejected_because")
        return True
    raise ToolSelectionBlock("TOOL_SELECTION_MALFORMED", f"no acceptance predicate for {prop!r}")  # pragma: no cover


def derive_properties(properties: dict) -> dict:
    """Validate every claimed evidence record and derive the five booleans.

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


def select_framework(properties: dict) -> dict:
    """Return the one framework for the declared evidence, with D85 obligations.

    Precedence is fixed: clock > resident > non-engineer surface > graph >
    agent reasoning > default. First match wins; no property combination
    produces two verdicts.
    """
    derived = derive_properties(properties)

    if derived["clock_critical"]:
        return _verdict(
            "temporal",
            "clock-critical: tight start-latency SLA with mandatory catch-up; chosen for durable-execution semantics, not a wall-clock promise",
            {"deterministic_ownership": "schedule, retry, timeout, and overlap policy live in Temporal workflow code (CODE control plane); deployment evidence must show measured start latency and recovery meeting the declared SLA"},
        )
    if derived["resident_service"]:
        return _verdict(
            "launchd",
            "resident service: long-lived daemon holding a socket/watch/hardware/event resource, not a scheduled job",
            {"deterministic_ownership": "keepalive and activation semantics in the plist (CODE control plane)"},
        )
    if derived["non_engineer_surface"]:
        return _verdict(
            "flowise",
            "non-engineer surface: visual build or client demo",
            {
                "durable_admissible": False,
                "note": "visual-builder output is not closed-grammar Python source under an authority root; it cannot pass the D85 inventory and is therefore a prototype or demo, never a durable system",
            },
        )
    if derived["multi_agent_graph"]:
        return _verdict(
            "langchain",
            "multi-agent graph with a cycle, dynamic router, distributed tracing, or context compression",
            {"deterministic_ownership": "graph topology, branching, and loop bounds in code; every LLM node is a MODEL op with a necessity record"},
        )
    if derived["agent_reasoning"]:
        return _verdict(
            "orca_pydantic",
            "agent-driven: the job needs an agent to reason, interpret, or decide",
            {"deterministic_ownership": "orchestration and dispatch in code; Pydantic AI gives every MODEL op typed input/output schemas"},
        )
    return _verdict(
        "kestra_pydantic",
        "default: schedule plus typed logic; the overwhelming majority of jobs",
        {"deterministic_ownership": "trigger, retry, timeout, and concurrency in the Kestra flow (CODE control plane); Pydantic AI for typed MODEL ops"},
    )


def _verdict(framework: str, rationale: str, extra: dict) -> dict:
    result = {
        "schema": STANDARD_VERSION,
        "framework": framework,
        "rationale": rationale,
        "d85_obligations": {
            "model_ops_need": ["typed pydantic schemas", "necessity record", "CODE validator/fallback/failure-state ops"],
            "four_ratios_at_least": 0.85,
            "critical_controls_code_only": True,
        },
    }
    result["d85_obligations"].update(extra)
    return result


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
    }
)


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

    checks: list[dict] = []

    def record(name: str, ok: bool, detail: str) -> None:
        checks.append({"check": name, "pass": ok is True, "detail": detail})

    expected = select_framework(build["properties"])
    framework = build["framework"]
    record(
        "framework_matches_standard",
        framework == expected["framework"],
        f"declared {framework!r}, standard requires {expected['framework']!r}",
    )

    record(
        "flowise_not_durable",
        framework != "flowise" or build.get("durable_system") is not True,
        "flowise verdicts are prototypes; a durable system must not declare flowise",
    )

    derived = derive_properties(build["properties"])
    needs_models = bool(
        derived["agent_reasoning"] or derived["multi_agent_graph"]
    ) or "pydantic" in str(framework)
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
