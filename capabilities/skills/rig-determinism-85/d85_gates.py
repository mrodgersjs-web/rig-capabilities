"""Authority-owned D85 gates downstream of the realized inventory.

Classification binds one runtime kind and taxonomy to every provisional
inventory ID, mints final operation identities from remapped graph bindings,
and enforces CODE ownership of critical controls plus typed model necessity
with reachable CODE validator, fallback, and failure-state nodes. Scoring
requires all four ratios at or above the threshold. Gate-D is a separate
exact-action authorization gate with signed append-only approvals and atomic
one-time consumption. Surface wiring requires every coding-agent surface to
carry the same doctrine marker. Every gate fails closed.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from pathlib import Path
from typing import Any

import d85
from d85 import (
    AdmissionBlock,
    AUTHORITY_REGISTRY,
    _block,
    _build_inventory_from_registry,
    _canonical_hash,
    _exact_keys,
    _load_json,
    _nonempty,
    _resolve_relative,
    _sha256_bytes,
)

CLASSIFICATION_SCHEMA = "rig.d85.classification.v1"
CLASSIFIED_SCHEMA = "rig.d85.classified-inventory.v1"
REALIZED_VERDICT_SCHEMA = "rig.d85.realized-verdict.v1"
APPROVAL_SCHEMA = "rig.d85.gate-d-approval.v1"
GATE_D_VERDICT_SCHEMA = "rig.d85.gate-d-verdict.v1"
SURFACES_SCHEMA = "rig.d85.surfaces.v1"
WIRING_VERDICT_SCHEMA = "rig.d85.wiring-verdict.v1"

CLASSIFICATION_KEYS = {
    "schema",
    "process_id",
    "inventory_sha256",
    "operations",
    "model_necessity",
}
CLASSIFIED_OPERATION_KEYS = {
    "inventory_id",
    "runtime_kind",
    "taxonomy",
    "predecessors",
    "successors",
}
NECESSITY_KEYS = {
    "inventory_id",
    "necessity_claim",
    "deterministic_alternative",
    "expected_improvement",
    "input_schema",
    "output_schema",
    "attempt_ceiling",
    "tool_ceiling",
    "token_ceiling",
    "time_ceiling_seconds",
    "cost_ceiling_usd",
    "validator_operation",
    "fallback_operation",
    "failure_state_operation",
}
SURFACE_KEYS = {"schema", "doctrine_sha256", "surfaces"}
REQUIRED_SURFACES = frozenset(
    {"claude_code", "hermes", "omp", "prime_agent"}
)

RUNTIME_KINDS = frozenset({"CODE", "MODEL", "MODEL_AGENT", "MIXED", "HUMAN"})
MODEL_KINDS = frozenset({"MODEL", "MODEL_AGENT", "MIXED"})
TAXONOMY_WEIGHTS = {
    "control plane": 5,
    "side effect": 5,
    "decision": 3,
    "transformation": 2,
    "retrieval": 1,
    "presentation": 1,
}
CRITICAL_TAXONOMIES = frozenset({"control plane", "side effect"})
D85_THRESHOLD = 0.85
# ponytail: bounded DFS path enumeration; topological ratio DP if graphs exceed this
MAX_CLASSIFIED_OPERATIONS = 512
GATE_D_MAX_LIFETIME_SECONDS = 24 * 3600


def _load_process(registry_path: Path, process_id: str) -> dict[str, Any]:
    registry, _ = _load_json(registry_path.resolve(strict=False), "AUTHORITY_REGISTRY_MISSING")
    if set(registry) != d85.REGISTRY_KEYS or registry.get("schema") != d85.REGISTRY_SCHEMA:
        _block("AUTHORITY_MALFORMED", "invalid registry grammar")
    processes = registry.get("processes")
    if not isinstance(processes, dict) or process_id not in processes:
        _block("UNKNOWN_PROCESS", process_id)
    authority_root = registry_path.resolve(strict=False).parent
    process_path = _resolve_relative(authority_root, processes[process_id], "AUTHORITY_ROOT_ESCAPE")
    process, _ = _load_json(process_path, "AUTHORITY_PROCESS_MISSING")
    return process


def _load_classification(
    process: dict[str, Any], authority_root: Path, process_id: str
) -> dict[str, Any]:
    relative = process.get("classification_path")
    if relative is None:
        _block("CLASSIFICATION_MISSING", "process record lacks classification_path")
    path = _resolve_relative(authority_root, relative, "AUTHORITY_ROOT_ESCAPE")
    classification, _ = _load_json(path, "AUTHORITY_CLASSIFICATION_MISSING")
    _exact_keys(classification, CLASSIFICATION_KEYS, str(path))
    if classification.get("schema") != CLASSIFICATION_SCHEMA:
        _block("CLASSIFICATION_MALFORMED", f"{path}: schema mismatch")
    if classification.get("process_id") != process_id:
        _block("CLASSIFICATION_MALFORMED", f"{path}: process_id mismatch")
    return classification


def _id_list(value: Any, where: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        _block("CLASSIFICATION_MALFORMED", f"{where}: expected list of ids")
    return list(value)


def _positive_int(value: Any, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        _block("MODEL_NECESSITY_MALFORMED", f"{where}: expected positive integer")
    return value


def _positive_number(value: Any, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        _block("MODEL_NECESSITY_MALFORMED", f"{where}: expected positive number")
    return float(value)


def classify_inventory(registry_path: Path, process_id: str) -> dict[str, Any]:
    registry_path = Path(registry_path)
    inventory = _build_inventory_from_registry(registry_path, process_id)
    authority_root = registry_path.resolve(strict=False).parent
    process = _load_process(registry_path, process_id)
    classification = _load_classification(process, authority_root, process_id)
    if classification.get("inventory_sha256") != inventory["inventory_sha256"]:
        _block(
            "CLASSIFICATION_STALE",
            "classification is not bound to the current extracted inventory",
        )

    extracted_ids = [operation["inventory_id"] for operation in inventory["operations"]]
    extracted_set = set(extracted_ids)
    if len(extracted_set) != len(extracted_ids):
        _block("AUTHORITY_DUPLICATE_BINDING", "extracted inventory has duplicate ids")

    records = classification.get("operations")
    if not isinstance(records, list) or not records:
        _block("CLASSIFICATION_MALFORMED", "operations must be a non-empty list")
    kinds: dict[str, str] = {}
    taxonomies: dict[str, str] = {}
    successors: dict[str, list[str]] = {}
    predecessors: dict[str, list[str]] = {}
    seen: set[str] = set()
    for index, record in enumerate(records):
        where = f"classification.operations[{index}]"
        if not isinstance(record, dict):
            _block("CLASSIFICATION_MALFORMED", f"{where}: expected object")
        _exact_keys(record, CLASSIFIED_OPERATION_KEYS, where)
        inventory_id = _nonempty(record.get("inventory_id"), f"{where}.inventory_id")
        if inventory_id in seen:
            _block("CLASSIFICATION_DUPLICATE_ID", inventory_id)
        seen.add(inventory_id)
        if inventory_id not in extracted_set:
            _block("CLASSIFICATION_UNKNOWN_ID", inventory_id)
        runtime_kind = record.get("runtime_kind")
        if runtime_kind not in RUNTIME_KINDS:
            _block("CLASSIFICATION_MALFORMED", f"{where}: unknown runtime kind {runtime_kind!r}")
        taxonomy = record.get("taxonomy")
        if taxonomy not in TAXONOMY_WEIGHTS:
            _block("CLASSIFICATION_MALFORMED", f"{where}: unknown taxonomy {taxonomy!r}")
        if taxonomy in CRITICAL_TAXONOMIES and runtime_kind != "CODE":
            _block(
                "CRITICAL_CONTROL_NOT_CODE",
                f"{where}: critical control {taxonomy!r} must be CODE",
            )
        kinds[inventory_id] = runtime_kind
        taxonomies[inventory_id] = taxonomy
        preds = _id_list(record.get("predecessors"), f"{where}.predecessors")
        succs = _id_list(record.get("successors"), f"{where}.successors")
        if inventory_id in preds or inventory_id in succs:
            _block("CLASSIFICATION_SELF_EDGE", inventory_id)
        if len(set(preds)) != len(preds) or len(set(succs)) != len(succs):
            _block("CLASSIFICATION_MALFORMED", f"{where}: duplicate graph bindings")
        predecessors[inventory_id] = preds
        successors[inventory_id] = succs
    missing = extracted_set - seen
    if missing:
        _block("CLASSIFICATION_MISSING_ID", f"unclassified operations: {sorted(missing)}")

    for inventory_id, succs in successors.items():
        for target in succs:
            if target not in extracted_set:
                _block("CLASSIFICATION_UNKNOWN_ID", f"successor {target}")
            if inventory_id not in predecessors[target]:
                _block(
                    "CLASSIFICATION_GRAPH_ASYMMETRIC",
                    f"{target} successors do not mirror {inventory_id} predecessors",
                )
    if len(inventory["operations"]) > MAX_CLASSIFIED_OPERATIONS:
        _block("CLASSIFICATION_GRAPH_TOO_LARGE", f"over {MAX_CLASSIFIED_OPERATIONS} operations")

    roots = sorted(
        inventory_id for inventory_id in extracted_set if not predecessors[inventory_id]
    )
    terminals = sorted(
        inventory_id for inventory_id in extracted_set if not successors[inventory_id]
    )
    if not roots or not terminals:
        _block("CLASSIFICATION_GRAPH_EMPTY", "realized graph needs roots and terminals")

    state: dict[str, int] = {}

    def visit(node: str, stack: tuple[str, ...]) -> None:
        mark = state.get(node, 0)
        if mark == 1:
            _block("CLASSIFICATION_GRAPH_CYCLIC", "->".join((*stack, node)))
        if mark == 2:
            return
        state[node] = 1
        for target in successors[node]:
            visit(target, (*stack, node))
        state[node] = 2

    for root in roots:
        visit(root, ())

    reachable: set[str] = set()
    frontier = list(roots)
    while frontier:
        node = frontier.pop()
        if node in reachable:
            continue
        reachable.add(node)
        frontier.extend(successors[node])
    unreachable = extracted_set - reachable
    if unreachable:
        _block("CLASSIFICATION_UNREACHABLE_NODE", f"no root path reaches {sorted(unreachable)}")

    necessity_records = classification.get("model_necessity")
    if not isinstance(necessity_records, list):
        _block("CLASSIFICATION_MALFORMED", "model_necessity must be a list")
    necessity_by_id: dict[str, dict[str, Any]] = {}
    model_ids = {inventory_id for inventory_id, kind in kinds.items() if kind in MODEL_KINDS}
    for index, record in enumerate(necessity_records):
        where = f"classification.model_necessity[{index}]"
        if not isinstance(record, dict):
            _block("MODEL_NECESSITY_MALFORMED", f"{where}: expected object")
        _exact_keys(record, NECESSITY_KEYS, where)
        inventory_id = _nonempty(record.get("inventory_id"), f"{where}.inventory_id")
        if inventory_id not in extracted_set:
            _block("CLASSIFICATION_UNKNOWN_ID", inventory_id)
        if inventory_id not in model_ids:
            _block("MODEL_NECESSITY_MALFORMED", f"{where}: not a model operation")
        if inventory_id in necessity_by_id:
            _block("CLASSIFICATION_DUPLICATE_ID", f"{where}: duplicate necessity")
        _nonempty(record.get("necessity_claim"), f"{where}.necessity_claim")
        _nonempty(record.get("deterministic_alternative"), f"{where}.deterministic_alternative")
        improvement = record.get("expected_improvement")
        if isinstance(improvement, bool) or not isinstance(improvement, (int, float)):
            _block("MODEL_NECESSITY_MALFORMED", f"{where}: expected_improvement must be numeric")
        if not 0 < float(improvement) <= 1:
            _block("MODEL_NECESSITY_MALFORMED", f"{where}: expected_improvement must be in (0, 1]")
        for field in ("input_schema", "output_schema"):
            schema = record.get(field)
            if not isinstance(schema, dict) or not schema:
                _block("MODEL_NECESSITY_MALFORMED", f"{where}.{field} must be a non-empty object")
        _positive_int(record.get("attempt_ceiling"), f"{where}.attempt_ceiling")
        _positive_int(record.get("tool_ceiling"), f"{where}.tool_ceiling")
        _positive_int(record.get("token_ceiling"), f"{where}.token_ceiling")
        _positive_number(record.get("time_ceiling_seconds"), f"{where}.time_ceiling_seconds")
        _positive_number(record.get("cost_ceiling_usd"), f"{where}.cost_ceiling_usd")
        for field, code in (
            ("validator_operation", "MODEL_VALIDATOR_UNREACHABLE"),
            ("fallback_operation", "MODEL_FALLBACK_UNREACHABLE"),
            ("failure_state_operation", "MODEL_FAILURE_STATE_UNREACHABLE"),
        ):
            support = _nonempty(record.get(field), f"{where}.{field}")
            if support not in extracted_set:
                _block("CLASSIFICATION_UNKNOWN_ID", support)
            if kinds[support] != "CODE":
                _block("CRITICAL_CONTROL_NOT_CODE", f"{where}.{field} must be CODE")
            closure: set[str] = set()
            frontier2 = [inventory_id]
            while frontier2:
                current = frontier2.pop()
                if current in closure:
                    continue
                closure.add(current)
                frontier2.extend(successors[current])
            if support not in closure:
                _block(code, f"{where}.{field} not reachable from {inventory_id}")
        necessity_by_id[inventory_id] = record
    missing_necessity = model_ids - set(necessity_by_id)
    if missing_necessity:
        _block("MODEL_NECESSITY_MISSING", f"model operations without necessity: {sorted(missing_necessity)}")

    def operation_id(inventory_id: str) -> str:
        return "sha256:" + _canonical_hash(
            {
                "inventory_id": inventory_id,
                "runtime_kind": kinds[inventory_id],
                "taxonomy": taxonomies[inventory_id],
                "predecessors": sorted(predecessors[inventory_id]),
                "successors": sorted(successors[inventory_id]),
            }
        )

    id_map = {inventory_id: operation_id(inventory_id) for inventory_id in sorted(extracted_set)}
    operations = []
    for inventory_id in sorted(extracted_set):
        operations.append(
            {
                "operation_id": id_map[inventory_id],
                "inventory_id": inventory_id,
                "runtime_kind": kinds[inventory_id],
                "taxonomy": taxonomies[inventory_id],
                "predecessors": sorted(id_map[item] for item in predecessors[inventory_id]),
                "successors": sorted(id_map[item] for item in successors[inventory_id]),
            }
        )
    counts = {
        kind: sum(1 for value in kinds.values() if value == kind)
        for kind in sorted(RUNTIME_KINDS)
    }
    core = {
        "schema": CLASSIFIED_SCHEMA,
        "process_id": process_id,
        "inventory_sha256": inventory["inventory_sha256"],
        "roots": sorted(id_map[item] for item in roots),
        "terminals": sorted(id_map[item] for item in terminals),
        "kind_counts": counts,
        "critical_control_all_code": True,
        "d85_admission": False,
        "operations": operations,
    }
    return {**core, "classification_sha256": _canonical_hash(core)}


def _enumerate_paths(
    roots: list[str], successors: dict[str, list[str]]
) -> list[list[str]]:
    paths: list[list[str]] = []
    stack: list[tuple[str, tuple[str, ...]]] = [(root, (root,)) for root in roots]
    while stack:
        node, path = stack.pop()
        if not successors[node]:
            paths.append(list(path))
            continue
        for target in successors[node]:
            stack.append((target, (*path, target)))
    return paths


def score_realized(registry_path: Path, process_id: str) -> dict[str, Any]:
    registry_path = Path(registry_path)
    classified = classify_inventory(registry_path, process_id)
    kinds: dict[str, str] = {}
    weights: dict[str, int] = {}
    successors: dict[str, list[str]] = {}
    roots: list[str] = []
    for operation in classified["operations"]:
        operation_id = operation["operation_id"]
        kinds[operation_id] = operation["runtime_kind"]
        weights[operation_id] = TAXONOMY_WEIGHTS[operation["taxonomy"]]
        successors[operation_id] = operation["successors"]
        if not operation["predecessors"]:
            roots.append(operation_id)

    scored = [oid for oid, kind in kinds.items() if kind != "HUMAN"]
    code = [oid for oid in scored if kinds[oid] == "CODE"]
    aggregate_unweighted = len(code) / len(scored) if scored else 0.0
    code_weight = sum(weights[oid] for oid in code)
    total_weight = sum(weights[oid] for oid in scored)
    aggregate_weighted = code_weight / total_weight if total_weight else 0.0

    min_path_unweighted = 1.0
    min_path_weighted = 1.0
    for path in _enumerate_paths(roots, successors):
        members = [oid for oid in path if kinds[oid] != "HUMAN"]
        if not members:
            min_path_unweighted = 0.0
            min_path_weighted = 0.0
            continue
        path_code = [oid for oid in members if kinds[oid] == "CODE"]
        min_path_unweighted = min(min_path_unweighted, len(path_code) / len(members))
        path_weight = sum(weights[oid] for oid in members)
        path_code_weight = sum(weights[oid] for oid in path_code)
        min_path_weighted = min(min_path_weighted, path_code_weight / path_weight)

    ratios = {
        "aggregate_unweighted": aggregate_unweighted,
        "aggregate_weighted": aggregate_weighted,
        "min_path_unweighted": min_path_unweighted,
        "min_path_weighted": min_path_weighted,
    }
    below = sorted(name for name, value in ratios.items() if value < D85_THRESHOLD)
    if below:
        _block(
            "BLOCK_DETERMINISM_RATIO",
            f"ratios below {D85_THRESHOLD}: "
            + ", ".join(f"{name}={ratios[name]:.6f}" for name in below),
        )
    return {
        "schema": REALIZED_VERDICT_SCHEMA,
        "verdict": "REALIZED_PASS",
        "gate": "d85_realized",
        "process_id": process_id,
        "inventory_sha256": classified["inventory_sha256"],
        "classification_sha256": classified["classification_sha256"],
        "threshold": D85_THRESHOLD,
        "ratios": ratios,
        "credit_operation_count": len(code),
        "scored_operation_count": len(scored),
        "d85_admission": True,
    }


def _gate_root(registry_path: Path, test_gate_root: Path | None) -> Path:
    if test_gate_root is not None:
        return Path(test_gate_root)
    if os.environ.get("RIG_LOOP_STATE"):
        _block(
            "BLOCK_GATE_D_ROOT_OVERRIDE",
            "production Gate-D rejects the RIG_LOOP_STATE override",
        )
    return registry_path.resolve(strict=False).parent / "gate_d"

def _load_key(gate_root: Path) -> bytes:
    path = gate_root / "key"
    try:
        raw = path.read_bytes().strip()
    except OSError as exc:
        _block("BLOCK_GATE_D_MISSING", f"gate-d key: {exc}")
    try:
        return bytes.fromhex(raw.decode("ascii"))
    except (UnicodeDecodeError, ValueError) as exc:
        _block("BLOCK_GATE_D_CORRUPT", f"gate-d key: {exc}")


def mint_approval(
    gate_root: Path,
    *,
    process_id: str,
    inventory_sha256: str,
    classification_sha256: str,
    realized_sha256: str,
    action: dict[str, Any],
    approver: str,
    lifetime_seconds: int = 3600,
) -> dict[str, Any]:
    gate_root = Path(gate_root)
    gate_root.mkdir(parents=True, exist_ok=True)
    (gate_root / "consumed").mkdir(exist_ok=True)
    key_path = gate_root / "key"
    if not key_path.exists():
        import secrets

        key_path.write_text(secrets.token_hex(32), encoding="ascii")
        os.chmod(key_path, 0o600)
    if lifetime_seconds > GATE_D_MAX_LIFETIME_SECONDS:
        _block("BLOCK_GATE_D_CORRUPT", "approval lifetime exceeds 24 hours")
    issued_at = int(time.time())
    action_sha256 = _canonical_hash(action)
    record = {
        "schema": APPROVAL_SCHEMA,
        "run_id": "sha256:"
        + _canonical_hash(
            {
                "process_id": process_id,
                "action_sha256": action_sha256,
                "issued_at": issued_at,
                "approver": approver,
            }
        ),
        "process_id": process_id,
        "inventory_sha256": inventory_sha256,
        "classification_sha256": classification_sha256,
        "realized_sha256": realized_sha256,
        "action_sha256": action_sha256,
        "approver": approver,
        "issued_at": issued_at,
        "expires_at": issued_at + lifetime_seconds,
    }
    key = _load_key(gate_root)
    signature = hmac.new(key, _canonical_hash(record).encode("utf-8"), hashlib.sha256).hexdigest()
    entry = {**record, "signature": signature}
    with (gate_root / "approvals.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry


def gate_d(
    registry_path: Path,
    process_id: str,
    action: dict[str, Any],
    *,
    test_gate_root: Path | None = None,
    now: int | None = None,
) -> dict[str, Any]:
    registry_path = Path(registry_path)
    proof = score_realized(registry_path, process_id)
    realized_sha256 = _canonical_hash(proof)
    gate_root = _gate_root(registry_path, test_gate_root)
    key = _load_key(gate_root)
    approvals_path = gate_root / "approvals.jsonl"
    try:
        raw_lines = approvals_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        _block("BLOCK_GATE_D_MISSING", f"approvals: {exc}")

    action_sha256 = _canonical_hash(action)
    current_time = int(time.time() if now is None else now)
    matching: list[dict[str, Any]] = []
    expired_seen = False
    for index, line in enumerate(raw_lines):
        if not line.strip():
            continue
        try:
            record = json.loads(line, object_pairs_hook=d85._closed_json_object)
        except (json.JSONDecodeError, d85.AdmissionBlock) as exc:
            _block("BLOCK_GATE_D_CORRUPT", f"approvals.jsonl line {index}: {exc}")
        if not isinstance(record, dict):
            _block("BLOCK_GATE_D_CORRUPT", f"approvals.jsonl line {index}: expected object")
        expected_signature = hmac.new(
            key, _canonical_hash(
                {item: record[item] for item in record if item != "signature"}
            ).encode("utf-8"), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(record.get("signature", ""), expected_signature):
            _block("BLOCK_GATE_D_CORRUPT", f"approvals.jsonl line {index}: bad signature")
        if record.get("process_id") != process_id:
            continue
        if (
            record.get("inventory_sha256") != proof["inventory_sha256"]
            or record.get("classification_sha256") != proof["classification_sha256"]
            or record.get("realized_sha256") != realized_sha256
        ):
            _block("BLOCK_GATE_D_MISMATCH", f"approval bound to a different proof: line {index}")
        if record.get("action_sha256") != action_sha256:
            continue
        lifetime = record.get("expires_at", 0) - record.get("issued_at", 0)
        if lifetime > GATE_D_MAX_LIFETIME_SECONDS or lifetime <= 0:
            _block("BLOCK_GATE_D_CORRUPT", f"approvals.jsonl line {index}: bad lifetime")
        if current_time > record.get("expires_at", 0):
            expired_seen = True
            continue
        matching.append(record)

    if not matching:
        if expired_seen:
            _block("BLOCK_GATE_D_EXPIRED", "every matching approval is expired")
        _block("BLOCK_GATE_D_UNAPPROVED", f"no approval binds {action_sha256}")

    record = matching[0]
    marker = gate_root / "consumed" / f"{record['run_id'][7:23]}.{action_sha256[7:23]}"
    try:
        descriptor = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        _block("BLOCK_GATE_D_CONSUMED", str(marker))
    os.write(descriptor, json.dumps({"consumed_at": current_time}, sort_keys=True).encode("utf-8"))
    os.close(descriptor)
    return {
        "schema": GATE_D_VERDICT_SCHEMA,
        "verdict": "ARMED",
        "gate": "gate_d",
        "process_id": process_id,
        "run_id": record["run_id"],
        "approver": record["approver"],
        "action_sha256": action_sha256,
        "d85_realized_sha256": realized_sha256,
        "consumed_marker": str(marker),
    }


def _surface_marker(doctrine_sha256: str) -> str:
    return f"rig-determinism-85@{doctrine_sha256}"


def check_wiring(registry_path: Path) -> dict[str, Any]:
    registry_path = Path(registry_path)
    authority_root = registry_path.resolve(strict=False).parent
    surfaces_path = authority_root / "surfaces.json"
    surfaces, _ = _load_json(surfaces_path, "BLOCK_WIRING_SURFACE_MISSING")
    _exact_keys(surfaces, SURFACE_KEYS, str(surfaces_path))
    if surfaces.get("schema") != SURFACES_SCHEMA:
        _block("BLOCK_WIRING_SURFACE_DIVERGENT", f"{surfaces_path}: schema mismatch")
    doctrine_sha256 = _nonempty(surfaces.get("doctrine_sha256"), "doctrine_sha256")
    marker = _surface_marker(doctrine_sha256)
    records = surfaces.get("surfaces")
    if not isinstance(records, dict) or set(records) != set(REQUIRED_SURFACES):
        _block(
            "BLOCK_WIRING_SURFACE_DIVERGENT",
            f"surfaces must be exactly {sorted(REQUIRED_SURFACES)}",
        )
    checked: dict[str, str] = {}
    for name in sorted(REQUIRED_SURFACES):
        surface_path = Path(_nonempty(records[name], f"surfaces.{name}")).expanduser()
        try:
            content = surface_path.read_text(encoding="utf-8")
        except OSError as exc:
            _block("BLOCK_WIRING_SURFACE_MISSING", f"{name}: {surface_path}: {exc}")
        if marker not in content:
            _block(
                "BLOCK_WIRING_SURFACE_DIVERGENT",
                f"{name}: {surface_path} lacks doctrine marker {marker}",
            )
        checked[name] = str(surface_path)
    return {
        "schema": WIRING_VERDICT_SCHEMA,
        "verdict": "WIRING_PASS",
        "gate": "surface_wiring",
        "doctrine_sha256": doctrine_sha256,
        "surfaces": checked,
    }


def classify_process(process_id: str) -> dict[str, Any]:
    return classify_inventory(AUTHORITY_REGISTRY, process_id)


def score_process(process_id: str) -> dict[str, Any]:
    return score_realized(AUTHORITY_REGISTRY, process_id)


def arm_gate_d(process_id: str, action: dict[str, Any]) -> dict[str, Any]:
    return gate_d(AUTHORITY_REGISTRY, process_id, action)


def verify_surfaces() -> dict[str, Any]:
    return check_wiring(AUTHORITY_REGISTRY)
