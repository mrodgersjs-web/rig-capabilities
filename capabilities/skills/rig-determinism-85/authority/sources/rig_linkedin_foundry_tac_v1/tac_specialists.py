"""Deterministic TAC specialist registry over the live Foundry LLMStep inventory.

Descriptors are policy, not a second prompt authority.  Each one binds a single
live prompt to its lane owner, model boundary, KPI, tools, context, and receipt
contract.  Validation is deliberately fail closed: a new or duplicated prompt,
an unpinned contract, or an undeclared capability makes the registry invalid.
"""
import importlib
import json
import os
import re

from tac_context import prompt_contract_hash


SCHEMA = "rig.foundry.specialist-registry.v2"

# TAC's seven-level hierarchy.  A Foundry LLMStep is level 4: it is a
# domain-specialized prompt inside a deterministic harness.  Higher levels own
# prompt systems or learning loops and therefore are never inferred from verbs.
PROMPT_HIERARCHY = (
    "simple",
    "templated",
    "agentic",
    "specialized",
    "meta",
    "self-improving",
    "agent-experts",
)
PROMPT_LEVELS = {level: name for level, name in enumerate(PROMPT_HIERARCHY, 1)}

LANE_MODULES = (
    "lane_a_deep",
    "lane_a1_deep",
    "lane_b_deep",
    "lane_c_deep",
    "lane_s_deep",
    "oo_bridge",
)
LANE_OWNERS = {
    "A": "lane-a-agent",
    "B": "lane-b-agent",
    "C": "lane-c-agent",
    "S": "lane-s-agent",
}
MODEL_POLICIES = frozenset(("configured-foundry-adapter",))
OUTWARD_CLASSES = frozenset(("none", "gated", "external"))

CAPABILITY_TO_TOOLS = {
    "local-model": frozenset(("harness.run_step", "model.get_model_fn")),
    "receipt": frozenset(("tac_context.prompt_contract_hash", "foundry_trace.local")),
    "gate-d": frozenset(("gate-d",)),
}
DEFAULT_TOOLS = (
    "harness.run_step",
    "model.get_model_fn",
    "tac_context.prompt_contract_hash",
    "foundry_trace.local",
)
CONTEXT_REQUIREMENTS = (
    "context_manifest_sha256",
    "expected_prompt_contract_sha256",
)
RECEIPT_FIELDS = (
    "schema",
    "agent_id",
    "task",
    "model_mode",
    "model_ref",
    "prompt_hash",
    "prompt_contract_sha256",
    "context_manifest_sha256",
    "attempts",
    "status",
    "verdict",
    "trace_id",
)

REQUIRED = {
    "task", "specialist_id", "specialist_roster", "lane", "lane_module",
    "workflow", "prompt_level", "prompt_name", "domain", "purpose",
    "allowed_capabilities", "tools", "evaluator", "owner", "model", "kpi",
    "context_requirements", "receipt_fields", "outward_class",
    "expected_prompt_contract_sha256",
}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_WORKFLOW_RE = re.compile(r"^([abcs])(\d{1,2})$", re.IGNORECASE)


def _sequence(value):
    return isinstance(value, (tuple, list)) and not isinstance(value, (str, bytes))


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _workflow(task):
    return task.split(".", 1)[0].lower() if _nonempty(task) and "." in task else None


def _lane_metadata(task):
    if task == "oo.qualify":
        return {
            "workflow": "c4",
            "lane": "C",
            "lane_module": "oo_bridge",
            "owner": LANE_OWNERS["C"],
        }
    workflow = _workflow(task)
    match = _WORKFLOW_RE.fullmatch(workflow or "")
    if not match:
        return {"workflow": workflow, "lane": None, "lane_module": None, "owner": None}
    lane = match.group(1).upper()
    module = {
        "A": "lane_a1_deep" if workflow in ("a2", "a13") else "lane_a_deep",
        "B": "lane_b_deep",
        "C": "lane_c_deep",
        "S": "lane_s_deep",
    }[lane]
    return {
        "workflow": workflow,
        "lane": lane,
        "lane_module": module,
        "owner": LANE_OWNERS[lane],
    }


def classify_prompt(step):
    """Return the deterministic TAC hierarchy coordinate for a prompt contract."""
    explicit_level = getattr(step, "prompt_level", None)
    explicit_name = getattr(step, "prompt_name", getattr(step, "prompt_level_name", None))
    if explicit_level is not None or explicit_name is not None:
        if explicit_level not in PROMPT_LEVELS or PROMPT_LEVELS[explicit_level] != explicit_name:
            raise ValueError("invalid-prompt-classification")
        return {"level": explicit_level, "name": explicit_name}

    task = step if isinstance(step, str) else getattr(step, "task", "")
    is_registered = _lane_metadata(task)["lane"] is not None
    is_llm_step = step.__class__.__name__ == "LLMStep" if not isinstance(step, str) else False
    if is_registered and (isinstance(step, str) or is_llm_step):
        return {"level": 4, "name": "specialized"}
    raise ValueError("unclassified-prompt:" + (task or "?"))


def _kpi_contract():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(root, "payloads", "kpi", "contract.json")
    with open(path, encoding="utf-8") as handle:
        rows = json.load(handle)
    result = {}
    for row in rows:
        workflow, metric = row.get("workflow"), row.get("metric")
        if not (_nonempty(workflow) and _nonempty(metric)):
            raise ValueError("invalid-kpi-contract")
        if workflow in result:
            raise ValueError("duplicate-kpi-workflow:" + workflow)
        result[workflow] = metric
    return result


def descriptor(task, domain, purpose, allowed_capabilities, evaluator, owner, outward_class,
               **metadata):
    """Build a descriptor while retaining the original seven positional arguments.

    New metadata may be overridden explicitly for negative tests or migrations;
    validation remains the authority and rejects any mismatch with the live lane.
    """
    lane = _lane_metadata(task)
    try:
        classification = classify_prompt(task)
    except ValueError:
        classification = {"level": None, "name": None}
    level = metadata.pop("prompt_level", classification["level"])
    prompt_name = metadata.pop("prompt_name", classification["name"])
    tools = metadata.pop("tools", DEFAULT_TOOLS)
    kpi = metadata.pop("kpi") if "kpi" in metadata else _kpi_contract().get(lane["workflow"])
    row = {
        "task": task,
        "specialist_id": metadata.pop(
            "specialist_id",
            (task.replace(".", "-") + "-specialist") if _nonempty(task) else None,
        ),
        "specialist_roster": metadata.pop("specialist_roster", lane["owner"]),
        "lane": metadata.pop("lane", lane["lane"]),
        "lane_module": metadata.pop("lane_module", lane["lane_module"]),
        "workflow": metadata.pop("workflow", lane["workflow"]),
        "prompt_level": level,
        "prompt_name": prompt_name,
        "domain": domain,
        "purpose": purpose,
        "allowed_capabilities": tuple(allowed_capabilities or ()),
        "tools": tuple(tools or ()),
        "evaluator": evaluator,
        "owner": owner,
        "model": metadata.pop("model", "configured-foundry-adapter"),
        "kpi": kpi,
        "context_requirements": tuple(metadata.pop("context_requirements", CONTEXT_REQUIREMENTS) or ()),
        "receipt_fields": tuple(metadata.pop("receipt_fields", RECEIPT_FIELDS) or ()),
        "outward_class": outward_class,
        "expected_prompt_contract_sha256": metadata.pop("expected_prompt_contract_sha256", None),
    }
    # Unknown keys are retained so validation can report descriptor-field-unknown
    # instead of descriptor() hiding a misspelling.
    row.update(metadata)
    return row


def _lane_modules():
    """Backward-compatible accessor for callers that patched the old function."""
    return list(LANE_MODULES)


def collect_llm_steps(lanes=None):
    """Collect every live module-level LLMStep, rejecting conflicting task ids."""
    steps = {}
    origins = {}
    for name in lanes if lanes is not None else _lane_modules():
        mod = importlib.import_module(name)
        for attr, value in vars(mod).items():
            if not (attr.isupper() and value.__class__.__name__ == "LLMStep"):
                continue
            task = getattr(value, "task", None)
            if not _nonempty(task):
                raise ValueError("LLMStep without task:%s.%s" % (name, attr))
            if task in steps:
                if steps[task] is value:
                    continue  # a same-object re-export is one live step
                raise ValueError(
                    "duplicate LLMStep task '%s': %s and %s.%s"
                    % (task, origins[task], name, attr)
                )
            steps[task] = value
            origins[task] = "%s.%s" % (name, attr)
    return steps


def _duplicates(values):
    seen, dupes = set(), set()
    for value in values:
        if value in seen:
            dupes.add(value)
        seen.add(value)
    return sorted(dupes)


def validate_descriptors(descriptors, steps=None):
    """Validate exact live coverage and every specialist execution boundary."""
    steps = collect_llm_steps() if steps is None else steps
    descriptors = list(descriptors)
    errors = []
    seen_tasks = set()
    seen_specialists = set()
    kpis = _kpi_contract()
    known_fields = REQUIRED | {"prompt_contract_sha256"}

    for key, step in steps.items():
        if key != getattr(step, "task", None):
            errors.append("live-step-key-mismatch:%s:%s" % (key, getattr(step, "task", "?")))

    for index, item in enumerate(descriptors):
        if not isinstance(item, dict):
            errors.append("descriptor-invalid:%d" % index)
            continue
        task = item.get("task", "?")
        missing = sorted(REQUIRED - set(item))
        if missing:
            errors.append("descriptor-missing:%s:%s" % (task, ",".join(missing)))
        unknown_fields = sorted(set(item) - known_fields)
        if unknown_fields:
            errors.append("descriptor-field-unknown:%s:%s" % (task, ",".join(unknown_fields)))

        if not _nonempty(task):
            errors.append("descriptor-task-invalid:%d" % index)
            continue
        if task in seen_tasks:
            errors.append("descriptor-duplicate:" + task)
        seen_tasks.add(task)

        specialist_id = item.get("specialist_id")
        if not _nonempty(specialist_id):
            errors.append("descriptor-specialist-invalid:" + task)
        elif specialist_id in seen_specialists:
            errors.append("descriptor-specialist-duplicate:" + specialist_id)
        else:
            seen_specialists.add(specialist_id)

        step = steps.get(task)
        if step is None:
            errors.append("descriptor-unknown-task:" + task)
            continue

        lane = _lane_metadata(task)
        for field in ("lane", "lane_module", "workflow"):
            if item.get(field) != lane[field]:
                errors.append("descriptor-%s-drift:%s" % (field.replace("_", "-"), task))
        if item.get("domain") != lane["workflow"]:
            errors.append("descriptor-domain-drift:" + task)
        if item.get("owner") != lane["owner"]:
            errors.append("descriptor-owner-drift:" + task)
        if item.get("specialist_roster") != lane["owner"]:
            errors.append("descriptor-specialist-roster-drift:" + task)
        if not _nonempty(item.get("purpose")):
            errors.append("descriptor-purpose-invalid:" + task)
        if item.get("evaluator") != task:
            errors.append("descriptor-evaluator-drift:" + task)

        try:
            expected_classification = classify_prompt(step)
        except ValueError:
            expected_classification = {"level": None, "name": None}
            errors.append("descriptor-prompt-unclassified:" + task)
        level = item.get("prompt_level")
        if level not in PROMPT_LEVELS:
            errors.append("descriptor-prompt-level-invalid:" + task)
        elif level != expected_classification["level"]:
            errors.append("descriptor-prompt-level-drift:" + task)
        if item.get("prompt_name") != expected_classification["name"]:
            errors.append("descriptor-prompt-name-drift:" + task)

        model = item.get("model")
        if model not in MODEL_POLICIES:
            errors.append("descriptor-model-invalid:" + task)
        expected_kpi = kpis.get(lane["workflow"])
        if not expected_kpi:
            errors.append("descriptor-kpi-unknown:" + task)
        elif item.get("kpi") != expected_kpi:
            errors.append("descriptor-kpi-drift:" + task)

        capabilities = item.get("allowed_capabilities")
        if not _sequence(capabilities):
            errors.append("descriptor-capabilities-invalid:" + task)
            capabilities = ()
        for duplicate in _duplicates(capabilities):
            errors.append("descriptor-capability-duplicate:%s:%s" % (task, duplicate))
        unknown_capabilities = sorted(set(capabilities) - set(CAPABILITY_TO_TOOLS))
        for capability in unknown_capabilities:
            errors.append("descriptor-capability-unknown:%s:%s" % (task, capability))

        tools = item.get("tools")
        if not _sequence(tools):
            errors.append("descriptor-tools-invalid:" + task)
            tools = ()
        for duplicate in _duplicates(tools):
            errors.append("descriptor-tool-duplicate:%s:%s" % (task, duplicate))
        declared_tools = set().union(
            *(CAPABILITY_TO_TOOLS[cap] for cap in capabilities if cap in CAPABILITY_TO_TOOLS)
        )
        for tool in sorted(set(tools) - declared_tools):
            errors.append("descriptor-tool-undeclared:%s:%s" % (task, tool))
        for tool in sorted(set(DEFAULT_TOOLS) - set(tools)):
            errors.append("descriptor-tool-missing:%s:%s" % (task, tool))

        context = item.get("context_requirements")
        if not _sequence(context):
            errors.append("descriptor-context-invalid:" + task)
            context = ()
        for duplicate in _duplicates(context):
            errors.append("descriptor-context-duplicate:%s:%s" % (task, duplicate))
        for field in sorted(set(CONTEXT_REQUIREMENTS) - set(context)):
            errors.append("descriptor-context-missing:%s:%s" % (task, field))
        for field in sorted(set(context) - set(CONTEXT_REQUIREMENTS)):
            errors.append("descriptor-context-unknown:%s:%s" % (task, field))

        receipt = item.get("receipt_fields")
        if not _sequence(receipt):
            errors.append("descriptor-receipt-invalid:" + task)
            receipt = ()
        for duplicate in _duplicates(receipt):
            errors.append("descriptor-receipt-duplicate:%s:%s" % (task, duplicate))
        for field in sorted(set(RECEIPT_FIELDS) - set(receipt)):
            errors.append("descriptor-receipt-missing:%s:%s" % (task, field))
        for field in sorted(set(receipt) - set(RECEIPT_FIELDS)):
            errors.append("descriptor-receipt-unknown:%s:%s" % (task, field))

        outward_class = item.get("outward_class")
        if outward_class not in OUTWARD_CLASSES:
            errors.append("descriptor-outward-invalid:" + task)
        elif outward_class == "none":
            if "gate-d" in capabilities or "gate-d" in tools:
                errors.append("descriptor-outward-excess-authority:" + task)
            if level == 7:
                errors.append("descriptor-outward-ungated:" + task)
        else:
            if "gate-d" not in capabilities or "gate-d" not in tools:
                errors.append("descriptor-outward-ungated:" + task)
            if level != 7:
                errors.append("descriptor-outward-classification:" + task)

        actual_hash = prompt_contract_hash(step)
        item["prompt_contract_sha256"] = actual_hash
        pinned_hash = item.get("expected_prompt_contract_sha256")
        if not isinstance(pinned_hash, str) or not _SHA256_RE.fullmatch(pinned_hash):
            errors.append("descriptor-prompt-contract-unpinned:" + task)
        elif pinned_hash != actual_hash:
            errors.append("descriptor-prompt-drift:" + task)

    for task in sorted(set(steps) - seen_tasks):
        errors.append("descriptor-missing-live-task:" + task)

    return {
        "schema": SCHEMA,
        "ok": not errors,
        "errors": errors,
        "descriptors": descriptors,
        "steps": sorted(steps),
    }


def default_descriptors(steps=None):
    """Build one pinned, least-privilege descriptor per live LLMStep."""
    steps = collect_llm_steps() if steps is None else steps
    kpis = _kpi_contract()
    out = []
    for task, step in sorted(steps.items()):
        lane = _lane_metadata(task)
        try:
            classification = classify_prompt(step)
        except ValueError:
            classification = {"level": None, "name": None}
        level = classification["level"]
        capabilities = ("local-model", "receipt") + (("gate-d",) if level == 7 else ())
        tools = DEFAULT_TOOLS + (("gate-d",) if level == 7 else ())
        out.append(descriptor(
            task=task,
            domain=lane["workflow"],
            purpose=step.task,
            allowed_capabilities=capabilities,
            evaluator=task,
            owner=lane["owner"],
            outward_class="gated" if level == 7 else "none",
            lane=lane["lane"],
            lane_module=lane["lane_module"],
            workflow=lane["workflow"],
            prompt_level=level,
            prompt_name=classification["name"],
            model="configured-foundry-adapter",
            kpi=kpis.get(lane["workflow"]),
            tools=tools,
            context_requirements=CONTEXT_REQUIREMENTS,
            receipt_fields=RECEIPT_FIELDS,
            expected_prompt_contract_sha256=prompt_contract_hash(step),
        ))
    return out
