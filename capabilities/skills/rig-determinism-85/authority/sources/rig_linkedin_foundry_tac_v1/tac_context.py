"""Deterministic execution/context provenance for Foundry lanes.

One compiler owns the source selection envelope, one function owns the execution
receipt envelope, and one helper binds the active prompt contract. The lane may
carry arbitrary task state; the manifest records only source identity, hashes,
freshness, and omission reasons — never raw private content.
"""
import hashlib, json, os, re
from datetime import datetime

CONTEXT_MANIFEST_SCHEMA = "rig.foundry.context-manifest.v1"
EXECUTION_ENVELOPE_SCHEMA = "rig.foundry.execution-envelope.v1"
SCHEMA = CONTEXT_MANIFEST_SCHEMA  # Backward-compatible name for manifest consumers.

_ACTIVE_STATUSES = frozenset(("known", "unknown", "candidate"))
_OMIT_STATUSES = {
    "stale": "stale-source",
    "sensitive": "sensitive-source",
    "private": "sensitive-source",
    "conflict": "conflict-source",
    "conflicted": "conflict-source",
}
_SENSITIVE_LABELS = frozenset(("private", "sensitive", "confidential", "restricted", "secret"))
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_SOURCE_FIELDS = frozenset((
    "ref", "path", "id",
    "sha256", "hash", "content_hash",
    "asof", "fetched_at", "date",
    "rights", "status", "reason",
    "stale", "sensitive", "conflict", "sensitivity",
))
_BUDGET_FIELDS = frozenset(("max_bytes",))


def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha(obj):
    return hashlib.sha256(_canon(obj).encode()).hexdigest()

def _valid_ref(value):
    return (isinstance(value, str) and bool(value.strip())
            and not any(ord(ch) < 32 or ord(ch) == 127 for ch in value))


def _valid_asof(value):
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _alias(item, names, validator, normalize):
    """Return one canonical alias value and reject malformed/disagreeing aliases."""
    present = [item[name] for name in names if name in item and item[name] is not None]
    if not present:
        return None, False, False
    if any(not validator(value) for value in present):
        return None, True, False
    normalized = [normalize(value) for value in present]
    return normalized[0], False, len(set(normalized)) != 1


def _is_sensitive_label(value):
    label = value.strip().lower().replace("_", "-").replace(" ", "-")
    return any(label == token or label.startswith(token + "-")
               for token in _SENSITIVE_LABELS)


def _omitted(index, reason, fields=None):
    row = {"index": index, "reason": reason}
    if fields:
        row["fields"] = sorted(set(fields))
    return row


def _normalize_source(index, item, explicit):
    """Normalize one source without ever carrying raw source content."""
    unknown_fields = sorted(set(item) - _SOURCE_FIELDS)
    if unknown_fields:
        return None, _omitted(index, "invalid-source-metadata", unknown_fields)
    ref, bad_ref, ref_conflict = _alias(
        item, ("ref", "path", "id"), _valid_ref, lambda value: value.strip())
    if ref is None and not bad_ref:
        return None, _omitted(index, "invalid-source-metadata", ["ref"])
    if bad_ref:
        return None, _omitted(index, "invalid-source-metadata", ["ref"])
    if ref_conflict:
        return None, _omitted(index, "conflict-source")

    status = item.get("status", "known" if explicit else "unknown")
    rights = item.get("rights", "explicit" if explicit else "candidate")
    reason = item.get("reason", "selected")
    fields = []
    if not _nonempty_string(status):
        fields.append("status")
    if not _nonempty_string(rights):
        fields.append("rights")
    if not _nonempty_string(reason):
        fields.append("reason")
    for field in ("stale", "sensitive", "conflict"):
        if field in item and not isinstance(item[field], bool):
            fields.append(field)
    sensitivity = item.get("sensitivity")
    if sensitivity is not None and not _nonempty_string(sensitivity):
        fields.append("sensitivity")
    if fields:
        return None, _omitted(index, "invalid-source-metadata", fields)

    status = status.strip().lower()
    rights = rights.strip()
    reason = reason.strip()
    status_reason = _OMIT_STATUSES.get(status)
    if status not in _ACTIVE_STATUSES and status_reason is None:
        return None, _omitted(index, "invalid-source-metadata", ["status"])
    if item.get("conflict") or status_reason == "conflict-source":
        return None, _omitted(index, "conflict-source")
    if (item.get("sensitive") or status_reason == "sensitive-source"
            or _is_sensitive_label(rights)
            or (sensitivity is not None and _is_sensitive_label(sensitivity))):
        return None, _omitted(index, "sensitive-source")
    if item.get("stale") or status_reason == "stale-source":
        return None, _omitted(index, "stale-source")

    digest, bad_digest, digest_conflict = _alias(
        item, ("sha256", "hash", "content_hash"),
        lambda value: isinstance(value, str) and bool(_SHA256_RE.fullmatch(value.strip())),
        lambda value: value.strip().lower())
    if digest_conflict:
        return None, _omitted(index, "conflict-source")
    if digest is None or bad_digest:
        return None, _omitted(index, "invalid-source-metadata", ["sha256"])

    asof, bad_asof, asof_conflict = _alias(
        item, ("asof", "fetched_at", "date"), _valid_asof, lambda value: value.strip())
    if asof_conflict:
        return None, _omitted(index, "conflict-source")
    if asof is None or bad_asof:
        return None, _omitted(index, "invalid-source-metadata", ["asof"])

    return {
        "ref": ref,
        "sha256": digest,
        "asof": asof,
        "rights": rights,
        "status": status,
        "reason": reason,
    }, None


def compile_context(state):
    """Build a deterministic, fail-closed manifest from caller-supplied sources.

    Accepted aliases are ref/path/id, sha256/hash/content_hash, and
    asof/fetched_at/date. Active sources require a stable ref, a full SHA-256,
    an ISO date/time, and non-empty rights/status/reason metadata. Stale,
    sensitive/private, conflicting, and malformed candidates are recorded in
    ``omitted`` by their original candidate index; raw source content is never
    copied into the manifest.
    """
    if state is None:
        state = {}
    if not isinstance(state, dict):
        raise TypeError("context-state-must-be-mapping")

    explicit = state.get("context_sources")
    if explicit is not None:
        if not isinstance(explicit, list):
            raise ValueError("context-sources-must-be-list")
        candidates = explicit
        explicit_mode = True
    else:
        candidates = state.get("sources") or []
        if not isinstance(candidates, list):
            raise ValueError("sources-must-be-list")
        explicit_mode = False

    provisional, omitted = [], []
    for index, item in enumerate(candidates):
        if not isinstance(item, dict):
            omitted.append(_omitted(index, "invalid-source-metadata", ["source"]))
            continue
        entry, exclusion = _normalize_source(index, item, explicit_mode)
        if exclusion is not None:
            omitted.append(exclusion)
        else:
            provisional.append((index, entry))

    by_ref = {}
    for index, entry in provisional:
        by_ref.setdefault(entry["ref"], []).append((index, entry))

    selected = []
    for ref in sorted(by_ref):
        group = sorted(by_ref[ref], key=lambda pair: pair[0])
        if len({_canon(entry) for _, entry in group}) != 1:
            omitted.extend(_omitted(index, "conflict-source") for index, _ in group)
            continue
        selected.append(group[0][1])
        omitted.extend(_omitted(index, "duplicate-source") for index, _ in group[1:])

    selected.sort(key=lambda entry: (entry["ref"], _canon(entry)))
    omitted.sort(key=lambda row: row["index"])
    raw_budget = state.get("context_budget") or {}
    if not isinstance(raw_budget, dict):
        raise ValueError("context-budget-must-be-mapping")
    budget = {field: raw_budget[field] for field in _BUDGET_FIELDS if field in raw_budget}
    if ("max_bytes" in budget
            and (isinstance(budget["max_bytes"], bool)
                 or not isinstance(budget["max_bytes"], int)
                 or budget["max_bytes"] < 0)):
        raise ValueError("context-budget-max-bytes-invalid")
    manifest = {
        "schema": CONTEXT_MANIFEST_SCHEMA,
        "budget": budget,
        "sources": selected,
        "omitted": omitted,
    }
    manifest["manifest_sha256"] = _sha(manifest)
    return manifest


def context_sha(manifest):
    return manifest.get("manifest_sha256")


def prompt_contract_hash(cfg):
    """Canonical content hash over the deployed LLMStep authority."""
    return _sha({
        "task": cfg.task,
        "input_schema": cfg.input_schema,
        "system": cfg.system,
        "template": cfg.template,
        "output_schema": cfg.output_schema,
        "max_retries": cfg.max_retries,
        "escalation": cfg.escalation,
    })


def execution_envelope(workflow, state, context_manifest=None):
    """Small provenance envelope shared by lane output and terminal receipts."""
    manifest = context_manifest or compile_context(state)
    return {
        "schema": EXECUTION_ENVELOPE_SCHEMA,
        "workflow": workflow,
        "source": "trigger" if os.environ.get("FOUNDRY_RUN_ID") else "local",
        "run_id": os.environ.get("FOUNDRY_RUN_ID") or None,
        "model_mode": os.environ.get("FOUNDRY_MODEL_MODE", "mock"),
        "model_ref": os.environ.get("FOUNDRY_MODEL_REF") or None,
        "fixture": os.environ.get("FOUNDRY_MODEL_MODE", "mock") == "mock",
        "context_manifest_sha256": context_sha(manifest),
    }
