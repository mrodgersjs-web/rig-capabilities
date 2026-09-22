"""Deterministic TAC workflow envelopes: delegation, expertise, continuation.

These are typed local records over the existing receipt/queue plane. They do not
execute side effects, authorize humans, or resume workflows. A continuation is an
immutable cursor; only a central Gate-D backend may turn it into a real resume.
"""
import hashlib, json


WORKFLOW_STEPS = ("scout", "plan", "build", "review")
MAX_REVIEW_CORRECTIONS = 3
TERMINAL_STATUSES = ("completed", "blocked", "failed", "halted")

SCHEMA = "rig.foundry.tac-workflow.v1"
EXECUTION_SCHEMA = "rig.foundry.execution-envelope.v1"
_APPROVED = "approved"
_REJECTED = "rejected"



def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(obj):
    return hashlib.sha256(_canon(obj).encode()).hexdigest()


def _clone(value):
    """Detach a JSON value from caller-owned mutable containers."""
    return json.loads(_canon(value))


def _sealed(record, field_name):
    sealed = dict(record)
    sealed[field_name] = sha(sealed)
    return sealed


def _verify_sealed(record, field_name, kind):
    record = _as_record(record, kind)
    if record.get("schema") != EXECUTION_SCHEMA or record.get("kind") != kind:
        raise ValueError("invalid-%s" % kind)
    if not _hash_is_current(record, field_name):
        raise ValueError("invalid-%s" % field_name.replace("_", "-"))
    return record


def _verified_expertise_proposal(proposal):
    proposal = _as_record(proposal, "expertise-proposal")
    if proposal.get("kind") != "expertise-proposal":
        raise ValueError("invalid-expertise-proposal")
    if not _hash_is_current(proposal, "proposal_sha256"):
        raise ValueError("invalid-proposal-sha256")
    if not proposal.get("evidence_refs"):
        raise ValueError("evidence-required")
    if not isinstance(proposal.get("delta"), dict):
        raise ValueError("proposal-delta-required")
    return proposal


def _no_effect_fields():
    return {
        "append_only": True,
        "effect": "record-only",
        "source_mutation": False,
        "outward_effect": False,
        "network_called": False,
    }


def _required(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("%s-required" % name)
    return value


def _as_record(value, name):
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    if not isinstance(value, dict):
        raise ValueError("invalid-%s" % name)
    return value


def _hash_is_current(record, field_name):
    expected = record.get(field_name)
    unsigned = dict(record)
    unsigned.pop(field_name, None)
    return isinstance(expected, str) and expected == sha(unsigned)



def ordered_dag_manifest(workflow, nodes=None):
    """Compatibility envelope for a named ordered DAG."""
    _required(workflow, "workflow")
    base = dag_manifest(nodes or WORKFLOW_STEPS)
    manifest = {
        "schema": SCHEMA,
        "kind": "ordered-dag-manifest",
        "workflow": workflow,
        "nodes": base["nodes"],
        "edges": base["edges"],
        "entry_step": base["nodes"][0]["step_id"],
        "terminal_step": base["nodes"][-1]["step_id"],
    }
    manifest["manifest_sha256"] = sha(manifest)
    return manifest
def dag_manifest(nodes):
    """Normalize ordered nodes and seal their forward-only dependency graph."""
    nodes = list(nodes or [])
    if not nodes:
        raise ValueError("dag-nodes-required")
    normalized = []
    seen = set()
    for order, node in enumerate(nodes):
        if isinstance(node, str):
            value = {"step_id": node}
        elif isinstance(node, dict):
            value = dict(node)
        else:
            raise ValueError("invalid-dag-node")
        step_id = value.pop("step_id", None) or value.pop("id", None) or value.pop("step", None)
        value.pop("order", None)
        _required(step_id, "step-id")
        if step_id in seen:
            raise ValueError("duplicate-dag-step:%s" % step_id)
        depends_on = list(value.pop("depends_on", [] if order == 0 else [normalized[-1]["step_id"]]))
        unknown = [dependency for dependency in depends_on if dependency not in seen]
        if unknown:
            raise ValueError("dag-dependency-not-earlier:%s" % unknown[0])
        seen.add(step_id)
        normalized.append(dict(
            {"step_id": step_id, "order": order, "depends_on": depends_on},
            **value))
    manifest = {
        "schema": SCHEMA,
        "kind": "DAGManifest",
        "nodes": normalized,
        "edges": [
            {"from": dependency, "to": node["step_id"]}
            for node in normalized for dependency in node["depends_on"]
        ],
    }
    manifest["manifest_hash"] = sha(manifest)
    return manifest


def _acceptance_list(acceptance):
    values = [acceptance] if isinstance(acceptance, str) else list(acceptance or [])
    if not values:
        raise ValueError("acceptance-required")
    return values


def scout_plan_build_review(task, acceptance):
    """Build the canonical artifact-carrying Scout -> Plan -> Build -> Review DAG."""
    _required(task, "task")
    acceptance = _acceptance_list(acceptance)
    return dag_manifest([
        {
            "step_id": "scout",
            "role": "Scout",
            "task": task,
            "depends_on": [],
            "output_ref": "scout-artifact",
        },
        {
            "step_id": "plan",
            "role": "Plan",
            "task": task,
            "depends_on": ["scout"],
            "input_ref": "scout-artifact",
            "output_ref": "plan-artifact",
        },
        {
            "step_id": "build",
            "role": "Build",
            "task": task,
            "depends_on": ["plan"],
            "input_ref": "plan-artifact",
            "output_ref": "build-artifact",
        },
        {
            "step_id": "review",
            "role": "Review",
            "task": task,
            "acceptance": acceptance,
            "depends_on": ["build"],
            "input_ref": "build-artifact",
            "output_ref": "review-artifact",
            "correction_target": "build",
            "max_corrections": MAX_REVIEW_CORRECTIONS,
        },
    ])




class WorkflowRun:
    """Immutable-by-replacement adapter for a content-addressed local run."""

    def __init__(self, run_id, workflow, goal, dag_manifest_sha256,
                 input_refs=None, context_manifest_sha256=None,
                 parent_run_id=None):
        for value, name in (
                (run_id, "run-id"), (workflow, "workflow"), (goal, "goal"),
                (dag_manifest_sha256, "dag-manifest-sha256")):
            _required(value, name)
        input_refs = list(input_refs or [])
        run = {
            "schema": SCHEMA,
            "kind": "WorkflowRun",
            "run_id": run_id,
            "workflow_id": workflow,
            "workflow": workflow,
            "workflow_version": "local",
            "source_event_id": parent_run_id or "local",
            "goal": goal,
            "input_hash": sha({"goal": goal, "input_refs": input_refs}),
            "input_refs": input_refs,
            "context_manifest_sha256": context_manifest_sha256,
            "parent_run_id": parent_run_id,
            "steps": ordered_dag_manifest(workflow)["nodes"],
            "manifest_hash": dag_manifest_sha256,
            "dag_manifest_sha256": dag_manifest_sha256,
        }
        run["run_hash"] = sha(run)
        self._record = run

    def to_dict(self):
        return json.loads(_canon(self._record))


def workflow_run(run_id, workflow_id, workflow_version, source_event_id,
                 input_hash, steps):
    """Build a deterministic WorkflowRun record from frozen source inputs."""
    for value, name in (
            (run_id, "run-id"), (workflow_id, "workflow-id"),
            (workflow_version, "workflow-version"),
            (source_event_id, "source-event-id"), (input_hash, "input-hash")):
        _required(value, name)
    if isinstance(steps, dict):
        if not _hash_is_current(steps, "manifest_hash"):
            raise ValueError("invalid-dag-manifest-hash")
        step_values = list(steps.get("nodes") or [])
        manifest_hash = steps["manifest_hash"]
    else:
        manifest = dag_manifest(steps)
        step_values = manifest["nodes"]
        manifest_hash = manifest["manifest_hash"]
    run = {
        "schema": SCHEMA,
        "kind": "WorkflowRun",
        "run_id": run_id,
        "workflow_id": workflow_id,
        "workflow_version": workflow_version,
        "source_event_id": source_event_id,
        "input_hash": input_hash,
        "steps": step_values,
        "manifest_hash": manifest_hash,
    }
    run["run_hash"] = sha(run)
    return run




class StepReceipt:
    """Adapter that derives one public StepReceipt from the previous link."""

    def __init__(self, record):
        self._record = dict(record)

    @classmethod
    def chained(cls, run, step, status, previous=None,
                input_artifact_refs=None, output_artifact_refs=None,
                evidence_refs=None, verdict=None, correction_attempt=0):
        run = _as_record(run, "workflow-run")
        previous = None if previous is None else _as_record(
            previous, "step-receipt")
        previous_hash = "GENESIS"
        input_hash = run["input_hash"]
        if previous is not None:
            if not _hash_is_current(previous, "receipt_hash"):
                raise ValueError("invalid-previous-receipt-hash")
            if previous.get("run_id") != run["run_id"]:
                raise ValueError("step-receipt-run-mismatch")
            previous_hash = previous["receipt_hash"]
            input_hash = previous_hash
        outputs = list(output_artifact_refs or [])
        record = step_receipt(
            run_id=run["run_id"],
            step_id=step,
            attempt=correction_attempt + 1,
            status=status,
            input_hash=input_hash,
            output_refs=outputs,
            evidence_refs=evidence_refs,
            artifact_digest=sha(outputs) if outputs else None,
            prev_receipt_hash=previous_hash,
        )
        if input_artifact_refs:
            record["input_artifact_refs"] = list(input_artifact_refs)
        if verdict is not None:
            record["verdict"] = verdict
        if input_artifact_refs or verdict is not None:
            record.pop("receipt_hash")
            record["receipt_hash"] = sha(record)
        return cls(record)

    def to_dict(self):
        return json.loads(_canon(self._record))


def step_receipt(run_id, step_id, attempt, status, input_hash, output_refs=None,
                 evidence_refs=None, artifact_digest=None, gate_d_ref=None,
                 prev_receipt_hash="GENESIS"):
    """Build one chained StepReceipt; callers pass the prior receipt hash."""
    for value, name in (
            (run_id, "run-id"), (step_id, "step-id"),
            (status, "step-status"), (input_hash, "input-hash"),
            (prev_receipt_hash, "prev-receipt-hash")):
        _required(value, name)
    if not isinstance(attempt, int) or attempt < 1:
        raise ValueError("invalid-step-attempt")
    receipt = {
        "schema": SCHEMA,
        "kind": "StepReceipt",
        "run_id": run_id,
        "step_id": step_id,
        "attempt": attempt,
        "status": status,
        "input_hash": input_hash,
        "output_refs": list(output_refs or []),
        "evidence_refs": list(evidence_refs or []),
        "artifact_digest": artifact_digest,
        "gate_d_ref": gate_d_ref,
        "prev_receipt_hash": prev_receipt_hash,
    }
    receipt["receipt_hash"] = sha(receipt)
    return receipt


def artifact_handoff(run, from_receipt, to_step, artifact_refs,
                     previous_handoff=None):
    """Bind produced artifacts to the next local step without moving them."""
    run = _as_record(run, "workflow-run")
    receipt = _as_record(from_receipt, "step-receipt")
    refs = list(artifact_refs or [])
    _required(to_step, "handoff-target-step")
    if not refs:
        raise ValueError("handoff-artifacts-required")
    if not _hash_is_current(run, "run_hash"):
        raise ValueError("invalid-workflow-run-hash")
    if not _hash_is_current(receipt, "receipt_hash"):
        raise ValueError("invalid-step-receipt-hash")
    if receipt.get("run_id") != run["run_id"]:
        raise ValueError("handoff-run-mismatch")
    declared = set(receipt.get("output_refs") or [])
    if declared and not set(refs).issubset(declared):
        raise ValueError("handoff-artifact-not-produced")
    previous_hash = None
    if previous_handoff is not None:
        previous_handoff = _as_record(previous_handoff, "artifact-handoff")
        if not _hash_is_current(previous_handoff, "handoff_hash"):
            raise ValueError("invalid-previous-handoff-hash")
        previous_hash = previous_handoff["handoff_hash"]
    handoff = {
        "schema": SCHEMA,
        "kind": "ArtifactHandoff",
        "run_id": run["run_id"],
        "workflow_id": run["workflow_id"],
        "run_hash": run["run_hash"],
        "from_step": receipt["step_id"],
        "from_receipt_hash": receipt["receipt_hash"],
        "to_step": to_step,
        "artifact_refs": refs,
        "previous_handoff_hash": previous_hash,
    }
    handoff["handoff_hash"] = sha(handoff)
    return handoff


def reviewer_correction(run, review_receipt, artifact_refs, attempt,
                        previous_correction=None):
    """Create one bounded Review -> Build correction instruction."""
    run = _as_record(run, "workflow-run")
    review = _as_record(review_receipt, "step-receipt")
    if review.get("step_id") != "review":
        raise ValueError("review-receipt-required")
    if not _hash_is_current(run, "run_hash"):
        raise ValueError("invalid-workflow-run-hash")
    if not _hash_is_current(review, "receipt_hash"):
        raise ValueError("invalid-review-receipt-hash")
    if review.get("run_id") != run["run_id"]:
        raise ValueError("correction-run-mismatch")
    if not isinstance(attempt, int) or not 1 <= attempt <= MAX_REVIEW_CORRECTIONS:
        raise ValueError("review-correction-limit")
    refs = list(artifact_refs or [])
    if not refs:
        raise ValueError("correction-artifacts-required")
    previous_hash = None
    if previous_correction is not None:
        previous_correction = _as_record(previous_correction, "review-correction")
        if not _hash_is_current(previous_correction, "correction_hash"):
            raise ValueError("invalid-previous-correction-hash")
        if previous_correction.get("attempt") + 1 != attempt:
            raise ValueError("nonsequential-correction-attempt")
        previous_hash = previous_correction["correction_hash"]
    elif attempt != 1:
        raise ValueError("previous-correction-required")
    correction = {
        "schema": SCHEMA,
        "kind": "ReviewerCorrection",
        "run_id": run["run_id"],
        "workflow_id": run["workflow_id"],
        "run_hash": run["run_hash"],
        "review_receipt_hash": review["receipt_hash"],
        "attempt": attempt,
        "max_attempts": MAX_REVIEW_CORRECTIONS,
        "artifact_refs": refs,
        "return_to_step": "build",
        "then_step": "review",
        "previous_correction_hash": previous_hash,
        "on_exhaustion": "blocked",
    }
    correction["correction_hash"] = sha(correction)
    return correction


def _validate_receipt_chain(run, receipts):
    expected_previous = "GENESIS"
    route = []
    corrections = 0
    receipt_hashes = []
    for receipt in receipts:
        receipt = _as_record(receipt, "step-receipt")
        if not _hash_is_current(receipt, "receipt_hash"):
            raise ValueError("invalid-step-receipt-hash")
        if receipt.get("run_id") != run["run_id"]:
            raise ValueError("step-receipt-run-mismatch")
        if receipt.get("prev_receipt_hash") != expected_previous:
            raise ValueError("broken-step-receipt-chain")
        step = receipt.get("step_id")
        if not route:
            if step != "scout":
                raise ValueError("workflow-must-start-with-scout")
        else:
            previous_step = route[-1]
            allowed = {
                "scout": "plan",
                "plan": "build",
                "build": "review",
                "review": "build",
            }
            if step != allowed.get(previous_step):
                raise ValueError("invalid-workflow-step-order")
            if previous_step == "review" and step == "build":
                corrections += 1
                if corrections > MAX_REVIEW_CORRECTIONS:
                    raise ValueError("review-correction-limit")
        route.append(step)
        expected_previous = receipt["receipt_hash"]
        receipt_hashes.append(expected_previous)
    if not route:
        raise ValueError("step-receipts-required")
    return receipt_hashes, route, corrections


def workflow_terminal(run, receipts, status, artifact_refs=None,
                      evidence_refs=None, continuation_cursor=None):
    """Seal one terminal state to the complete chained receipt history."""
    if status not in TERMINAL_STATUSES:
        raise ValueError("invalid-workflow-terminal-status")
    run = _as_record(run, "workflow-run")
    if not _hash_is_current(run, "run_hash"):
        raise ValueError("invalid-workflow-run-hash")
    receipt_hashes, route, corrections = _validate_receipt_chain(
        run, list(receipts or []))
    if status == "completed" and route[-1] != "review":
        raise ValueError("completed-workflow-requires-review")
    continuation_hash = None
    if status == "halted":
        cursor = _as_record(continuation_cursor, "continuation")
        if not verify_continuation(cursor):
            raise ValueError("invalid-continuation")
        if (cursor.get("run_id") != run["run_id"]
                or cursor.get("workflow") != run["workflow_id"]):
            raise ValueError("continuation-run-mismatch")
        continuation_hash = cursor["continuation_sha256"]
    elif continuation_cursor is not None:
        raise ValueError("continuation-only-for-halted-workflow")
    terminal = {
        "schema": SCHEMA,
        "kind": "WorkflowTerminal",
        "run_id": run["run_id"],
        "workflow_id": run["workflow_id"],
        "run_hash": run["run_hash"],
        "status": status,
        "receipt_chain": receipt_hashes,
        "receipt_chain_hash": sha(receipt_hashes),
        "route": route,
        "review_corrections": corrections,
        "artifact_refs": list(artifact_refs or []),
        "artifact_digest": sha(list(artifact_refs or [])),
        "evidence_refs": list(evidence_refs or []),
        "continuation_sha256": continuation_hash,
    }
    terminal["terminal_proof_sha256"] = sha(terminal)
    return terminal


workflow_terminal_proof = workflow_terminal


def delegation(parent_run_id, workflow, step, specialist_id, task, input_refs=None,
               context_manifest_sha256=None, access="read", writer_lease_id=None,
               acceptance=None, depends_on=None):
    if access == "write" and not writer_lease_id:
        raise ValueError("writer-lease-required")
    envelope = {
        "schema": SCHEMA,
        "kind": "delegation",
        "parent_run_id": parent_run_id,
        "workflow": workflow,
        "step": step,
        "specialist_id": specialist_id,
        "task": task,
        "depends_on": list(depends_on or []),
        "input_refs": list(input_refs or []),
        "context_manifest_sha256": context_manifest_sha256,
        "access": access,
        "writer_lease_id": writer_lease_id,
        "acceptance": list(acceptance or []),
    }
    envelope["delegation_id"] = sha(envelope)
    return envelope


def delegation_result(delegation, status, verdict, result=None, evidence_refs=None,
                      artifact_refs=None, usage=None):
    if status not in ("completed", "blocked", "failed"):
        raise ValueError("invalid-delegation-status")
    if not delegation.get("delegation_id"):
        raise ValueError("delegation-id-required")
    envelope = {
        "schema": SCHEMA,
        "kind": "delegation-result",
        "delegation_id": delegation["delegation_id"],
        "status": status,
        "verdict": verdict,
        "result": result or {},
        "evidence_refs": list(evidence_refs or []),
        "artifact_refs": list(artifact_refs or []),
        "usage": usage or {},
    }
    envelope["result_sha256"] = sha(envelope)
    return envelope


def expertise_proposal(expert_id, scope, base_snapshot_sha256, task, evidence_refs,
                       outcome_refs=None, delta=None, asof=None):
    if not base_snapshot_sha256:
        raise ValueError("base-snapshot-required")
    if not evidence_refs:
        raise ValueError("evidence-required")
    proposal = {
        "schema": SCHEMA,
        "kind": "expertise-proposal",
        "expert_id": expert_id,
        "scope": scope,
        "base_snapshot_sha256": base_snapshot_sha256,
        "task": task,
        "evidence_refs": list(evidence_refs),
        "outcome_refs": list(outcome_refs or []),
        "delta": delta or {"add": [], "correct": [], "remove": []},
        "asof": asof,
        "status": "proposed",
    }
    proposal["proposal_sha256"] = sha(proposal)
    return proposal


def _legacy_expertise_snapshot(expert_id, scope, previous_snapshot_sha256,
                               promoted_from_proposal, rules=None, patterns=None,
                               counterexamples=None, limits=None, source_refs=None,
                               verifier_receipt=None):
    """Preserve the original snapshot API and record shape."""
    if not promoted_from_proposal:
        raise ValueError("promotion-proposal-required")
    if not verifier_receipt:
        raise ValueError("verifier-receipt-required")
    snapshot = {
        "schema": SCHEMA,
        "kind": "expertise-snapshot",
        "expert_id": expert_id,
        "scope": scope,
        "previous_snapshot_sha256": previous_snapshot_sha256 or "GENESIS",
        "promoted_from_proposal": promoted_from_proposal,
        "rules": list(rules or []),
        "patterns": list(patterns or []),
        "counterexamples": list(counterexamples or []),
        "limits": list(limits or []),
        "source_refs": list(source_refs or []),
        "verifier_receipt": verifier_receipt,
    }
    snapshot["snapshot_sha256"] = sha(snapshot)
    return snapshot


def expertise_persistence(proposal):
    """Persist one B6 proposal by reference without changing the proposal."""
    proposal = _verified_expertise_proposal(proposal)
    record = {
        "schema": EXECUTION_SCHEMA,
        "kind": "expertise-persistence",
        "phase": "ACT",
        "workflow": "B6",
        "expert_id": proposal.get("expert_id"),
        "scope": proposal.get("scope"),
        "base_snapshot_sha256": proposal.get("base_snapshot_sha256"),
        "proposal_sha256": proposal["proposal_sha256"],
        "delta_sha256": sha(proposal["delta"]),
        "evidence_refs": _clone(proposal["evidence_refs"]),
        "outcome_refs": _clone(proposal.get("outcome_refs") or []),
        "status": "persisted",
        **_no_effect_fields(),
    }
    return _sealed(record, "persistence_hash")


def expertise_review(proposal, verdict):
    """Record an offline expert-proposal review with an explicit terminal verdict."""
    proposal = _verified_expertise_proposal(proposal)
    if isinstance(verdict, str):
        decision = verdict.strip().lower()
        reviewer_id = None
        evidence_refs = []
    elif isinstance(verdict, dict):
        decision = verdict.get("verdict", verdict.get("decision", verdict.get("status")))
        if not isinstance(decision, str):
            raise ValueError("review-verdict-required")
        decision = decision.strip().lower()
        reviewer_id = verdict.get("reviewer_id", verdict.get("verifier_id"))
        evidence_refs = _clone(verdict.get("evidence_refs") or [])
        if reviewer_id is not None:
            reviewer_id = _required(reviewer_id, "reviewer-id").strip()
            if reviewer_id == proposal.get("expert_id"):
                raise ValueError("self-review-refused")
    else:
        raise ValueError("review-verdict-required")
    if decision not in (_APPROVED, _REJECTED):
        raise ValueError("invalid-review-verdict")
    record = {
        "schema": EXECUTION_SCHEMA,
        "kind": "expertise-review",
        "phase": "LEARN",
        "proposal_sha256": proposal["proposal_sha256"],
        "expert_id": proposal.get("expert_id"),
        "scope": proposal.get("scope"),
        "reviewer_id": reviewer_id,
        "evidence_refs": evidence_refs,
        "verdict": decision,
        "status": "reviewed",
        **_no_effect_fields(),
    }
    return _sealed(record, "review_hash")


def expertise_promotion(proposal, review):
    """Record promotion of one independently reviewed proposal; apply nothing."""
    proposal = _verified_expertise_proposal(proposal)
    review = _verify_sealed(review, "review_hash", "expertise-review")
    if review.get("proposal_sha256") != proposal["proposal_sha256"]:
        raise ValueError("review-proposal-mismatch")
    if review.get("verdict") != _APPROVED:
        raise ValueError("proposal-not-approved")
    expertise = _clone(proposal["delta"])
    record = {
        "schema": EXECUTION_SCHEMA,
        "kind": "expertise-promotion",
        "phase": "LEARN",
        "expert_id": proposal.get("expert_id"),
        "scope": proposal.get("scope"),
        "base_snapshot_sha256": proposal.get("base_snapshot_sha256"),
        "proposal_sha256": proposal["proposal_sha256"],
        "review_hash": review["review_hash"],
        "expertise": expertise,
        "expertise_sha256": sha(expertise),
        "verdict": _APPROVED,
        "decision": "promote",
        **_no_effect_fields(),
    }
    return _sealed(record, "promotion_hash")


def _versioned_expertise_snapshot(promotion, version, prior):
    promotion = _verify_sealed(
        promotion, "promotion_hash", "expertise-promotion")
    if promotion.get("verdict") != _APPROVED:
        raise ValueError("promotion-not-approved")
    version = _required(version, "expertise-version").strip()
    previous_hash = "GENESIS"
    if prior not in (None, "GENESIS"):
        prior = _verify_sealed(prior, "snapshot_hash", "expertise-snapshot")
        if (prior.get("expert_id"), prior.get("scope")) != (
                promotion.get("expert_id"), promotion.get("scope")):
            raise ValueError("prior-snapshot-scope-mismatch")
        if prior.get("version") == version:
            raise ValueError("snapshot-version-must-advance")
        previous_hash = prior["snapshot_hash"]
    record = {
        "schema": EXECUTION_SCHEMA,
        "kind": "expertise-snapshot",
        "phase": "LEARN",
        "expert_id": promotion.get("expert_id"),
        "scope": promotion.get("scope"),
        "version": version,
        "prior_snapshot_hash": previous_hash,
        "proposal_sha256": promotion.get("proposal_sha256"),
        "review_hash": promotion.get("review_hash"),
        "promotion_hash": promotion["promotion_hash"],
        "expertise": _clone(promotion["expertise"]),
        "expertise_sha256": promotion["expertise_sha256"],
        "status": _APPROVED,
        **_no_effect_fields(),
    }
    return _sealed(record, "snapshot_hash")


def expertise_snapshot(expertise=None, version=None, prior=None, *legacy_args,
                       **legacy_kwargs):
    """Create a versioned approved snapshot, while retaining the legacy API."""
    if (isinstance(expertise, dict)
            and expertise.get("kind") == "expertise-promotion"):
        if legacy_args or legacy_kwargs:
            raise TypeError("unexpected-snapshot-arguments")
        return _versioned_expertise_snapshot(expertise, version, prior)

    legacy_names = (
        "promoted_from_proposal", "rules", "patterns", "counterexamples",
        "limits", "source_refs", "verifier_receipt",
    )
    if len(legacy_args) > len(legacy_names):
        raise TypeError("too-many-snapshot-arguments")
    for name, value in zip(legacy_names, legacy_args):
        if name in legacy_kwargs:
            raise TypeError("multiple-values-for-%s" % name)
        legacy_kwargs[name] = value
    if expertise is not None and "expert_id" in legacy_kwargs:
        raise TypeError("multiple-values-for-expert-id")
    if version is not None and "scope" in legacy_kwargs:
        raise TypeError("multiple-values-for-scope")
    if prior is not None and "previous_snapshot_sha256" in legacy_kwargs:
        raise TypeError("multiple-values-for-previous-snapshot-sha256")
    expert_id = legacy_kwargs.pop("expert_id", expertise)
    scope = legacy_kwargs.pop("scope", version)
    previous = legacy_kwargs.pop("previous_snapshot_sha256", prior)
    promoted = legacy_kwargs.pop("promoted_from_proposal", None)
    values = {
        name: legacy_kwargs.pop(name, None)
        for name in legacy_names[1:]
    }
    if legacy_kwargs:
        raise TypeError("unexpected-snapshot-argument:%s" % sorted(legacy_kwargs)[0])
    return _legacy_expertise_snapshot(
        expert_id, scope, previous, promoted, **values)


def expertise_rollback(snapshot, reason):
    """Record a rollback proposal without changing either snapshot."""
    snapshot = _verify_sealed(snapshot, "snapshot_hash", "expertise-snapshot")
    reason = _required(reason, "rollback-reason").strip()
    record = {
        "schema": EXECUTION_SCHEMA,
        "kind": "expertise-rollback",
        "phase": "LEARN",
        "snapshot_hash": snapshot["snapshot_hash"],
        "from_version": snapshot["version"],
        "to_snapshot_hash": snapshot["prior_snapshot_hash"],
        "reason": reason,
        "decision": "rollback-proposed",
        "authorization": "none",
        **_no_effect_fields(),
    }
    return _sealed(record, "rollback_hash")


def _outward_requested(record):
    blocked_keys = (
        "send", "publish", "deploy", "upload", "network_called",
        "outward_effect",
    )
    for key in blocked_keys:
        value = record.get(key)
        if value not in (None, False, "none", "disabled", "local"):
            return True
    action = record.get("action", record.get("effect"))
    return (
        isinstance(action, str)
        and action.strip().lower() in (
            "send", "publish", "deploy", "upload", "execute-outward",
        )
    )


def project_expertise(snapshot, manifest):
    """Project approved expertise into a local context payload only."""
    snapshot = _verify_sealed(snapshot, "snapshot_hash", "expertise-snapshot")
    if snapshot.get("status") != _APPROVED:
        raise ValueError("snapshot-not-approved")
    manifest = _as_record(manifest, "context-manifest")
    if not manifest:
        raise ValueError("context-manifest-required")
    if _outward_requested(manifest):
        raise ValueError("outward-effect-refused")
    manifest = _clone(manifest)
    context = {
        "expert_id": snapshot.get("expert_id"),
        "scope": snapshot.get("scope"),
        "version": snapshot["version"],
        "expertise": _clone(snapshot["expertise"]),
        "source_snapshot_hash": snapshot["snapshot_hash"],
    }
    record = {
        "schema": EXECUTION_SCHEMA,
        "kind": "expertise-projection",
        "phase": "REUSE",
        "snapshot_hash": snapshot["snapshot_hash"],
        "manifest": manifest,
        "manifest_sha256": sha(manifest),
        "context": context,
        "context_sha256": sha(context),
        "authorization": "none",
        **_no_effect_fields(),
    }
    return _sealed(record, "projection_hash")


def _calibration_rows(outcomes):
    if isinstance(outcomes, dict):
        outcomes = outcomes.get("outcomes", [outcomes])
    if isinstance(outcomes, (str, bytes)) or not isinstance(outcomes, (list, tuple)):
        raise ValueError("outcomes-required")
    if not outcomes:
        raise ValueError("outcomes-required")
    normalized = []
    for outcome in outcomes:
        if not isinstance(outcome, dict):
            raise ValueError("invalid-outcome")
        prediction = outcome.get("prediction", outcome.get("predicted"))
        actual = outcome.get("outcome", outcome.get("actual",
                         outcome.get("observed")))
        if (isinstance(prediction, bool)
                or not isinstance(prediction, (int, float))
                or not 0 <= prediction <= 1):
            raise ValueError("invalid-outcome-prediction")
        if isinstance(actual, bool):
            actual = int(actual)
        if actual not in (0, 1):
            raise ValueError("invalid-outcome-result")
        row = {"prediction": float(prediction), "outcome": actual}
        if "outcome_ref" in outcome:
            row["outcome_ref"] = _required(
                outcome["outcome_ref"], "outcome-ref").strip()
        normalized.append(row)
    return normalized


def calibrate_expertise(snapshot, outcomes):
    """Record settled outcome calibration for one approved snapshot."""
    snapshot = _verify_sealed(snapshot, "snapshot_hash", "expertise-snapshot")
    if snapshot.get("status") != _APPROVED:
        raise ValueError("snapshot-not-approved")
    rows = _calibration_rows(outcomes)
    brier_score = sum(
        (row["prediction"] - row["outcome"]) ** 2 for row in rows) / len(rows)
    record = {
        "schema": EXECUTION_SCHEMA,
        "kind": "expertise-calibration",
        "phase": "ACT",
        "snapshot_hash": snapshot["snapshot_hash"],
        "version": snapshot["version"],
        "outcomes": rows,
        "outcomes_sha256": sha(rows),
        "settled_count": len(rows),
        "brier_score": brier_score,
        "status": "calibrated",
        **_no_effect_fields(),
    }
    return _sealed(record, "calibration_hash")


def refuse_feedback_loop(record):
    """Seal a no-effect refusal; feedback can propose but cannot self-apply."""
    record = _as_record(record, "feedback-record")
    if not record:
        raise ValueError("feedback-record-required")
    source = _clone(record)
    reasons = ["feedback-requires-independent-review"]
    if source.get("self_verify") is True:
        reasons.append("self-verification-refused")
    if source.get("auto_promote") is True:
        reasons.append("automatic-promotion-refused")
    if source.get("source_mutation") is True or source.get("mutate_prior") is True:
        reasons.append("prior-mutation-refused")
    if _outward_requested(source):
        reasons.append("outward-effect-refused")
    action = source.get("action")
    if isinstance(action, str) and action.strip().lower() in (
            "promote", "self-promote", "auto-promote", "mutate", "overwrite"):
        reasons.append("feedback-application-refused")
    refusal = {
        "schema": EXECUTION_SCHEMA,
        "kind": "feedback-loop-refusal",
        "phase": "LEARN",
        "record_sha256": sha(source),
        "verdict": _REJECTED,
        "decision": "refuse",
        "refused": True,
        "authorization": "none",
        **_no_effect_fields(),
    }
    refusal["effect"] = "none"
    refusal["append_only"] = True
    return _sealed(refusal, "refusal_hash")


def continuation(run_id, workflow, next_step, state_ref, artifact_digest):
    """Create an immutable human waitpoint, never an authorization to resume."""
    if not all((run_id, workflow, next_step, state_ref, artifact_digest)):
        raise ValueError("continuation-fields-required")
    cursor = {
        "schema": SCHEMA,
        "kind": "workflow-continuation",
        "run_id": run_id,
        "workflow": workflow,
        "next_step": next_step,
        "state_ref": state_ref,
        "artifact_digest": artifact_digest,
        "decision_authority": "human",
        "authorization": "none",
        "resumable": False,
        "replacement_only": True,
    }
    cursor["continuation_sha256"] = sha(cursor)
    return cursor


def verify_continuation(cursor):
    """Reject mutation or promotion of a content-addressed waitpoint."""
    if not isinstance(cursor, dict):
        return False
    return (
        cursor.get("kind") == "workflow-continuation"
        and cursor.get("decision_authority") == "human"
        and cursor.get("authorization") == "none"
        and cursor.get("resumable") is False
        and cursor.get("replacement_only") is True
        and _hash_is_current(cursor, "continuation_sha256")
    )
