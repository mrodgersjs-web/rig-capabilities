"""Acceptance identity: every acceptance record must say WHO ran it and WHO judged it.

Why this exists (sources verified against .context/discover-ai/dossiers/):
- 5S9NemR7Fwo — HELIX: Model–Harness Co-evolution for Recursive Self-Improvement,
  arXiv:2608.13951. The unit of evaluation is the coupled (model, harness) state:
  "the real agent configuration is a combined interlink state" — a PASS earned by
  model+HarnessA says nothing about model+HarnessB, so an acceptance record that
  does not pin both cannot be joined, compared, or trusted across variants.
- TA5QzGTQU_U — Agent Skills Can Be Harmful, arXiv:2608.11888 (capability 9:
  external-verifier override of skill self-validation). The failure signature is
  "The skill performs the internal validation": a self-consistent certificate
  from inside the context that produced the error, while an external evaluation
  judges the output wrong.

Contract (owner: capabilities/commands/capabilities-done-test.md):

    python3 rig_capabilities/acceptance_identity.py <record.json|-> --stamp <out.json>

Reads a done-test result record (identity fields grafted onto it by the harness
that ran the checks), and on success writes EXACTLY ONE file — the identity
stamp at --stamp — and echoes the stamp on stdout. On refusal it writes nothing,
prints one named refusal per defect on stderr, and exits 1.

The record must carry:
  executed_by.model / executed_by.model_version / executed_by.process_id
  harness_ref.harness_id / harness_ref.config_hash   (fingerprint: [sha256:]hex 16-64)
  verifier.model / verifier.process_id / verifier.harness_id
`executed_by.model_family` / `verifier.model_family` are optional explicit
overrides; otherwise the family is derived deterministically from the model id
(last '/'-segment, first '[-:@_]' token) — a normalization of an existing
field, never an invention of a missing one.

Never-fabricate rule: there is NO environment, config, or heuristic fallback.
A field the record does not carry is reported as `identity_unavailable:<field>`
— the honest output of a run whose environment exposed no identity is a named
refusal, never a guess.

Self-verification rule: acceptance must come from outside the context that
produced the output. The verifier is EXTERNAL iff it is not the producer's
process AND differs from the producer on at least one axis — model family or
harness id. Same process, or same model family AND same harness, is the same
run grading itself and is refused as `self_verification:...` even when the
verdict says pass. That is what stops a skill whose done_when is satisfied by
its own validation section from certifying itself.

Exit codes: 0 stamped · 1 refused (identity_unavailable / self_verification /
stamp_write_failed) · 2 usage (argparse).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "rig.acceptance_identity/1"

# Dotted paths are the refusal vocabulary: identity_unavailable:<this string>.
REQUIRED = (
    ("executed_by", "model"),
    ("executed_by", "model_version"),
    ("executed_by", "process_id"),
    ("harness_ref", "harness_id"),
    ("harness_ref", "config_hash"),
    ("verifier", "model"),
    ("verifier", "process_id"),
    ("verifier", "harness_id"),
)

# A config hash is only *verifiable* offline in shape: a hex fingerprint
# (optionally sha256-prefixed). Free-text like "green" or "main" pins nothing.
_CONFIG_HASH = re.compile(r"^(?:sha256:)?[0-9a-f]{16,64}$")


def _norm(value: str) -> str:
    return value.strip().lower()


def model_family(model_id: str, explicit: str | None = None) -> str:
    """Deterministic family token of a model id: last '/'-segment, then the
    first '[-:@_]' token ("openrouter/anthropic/claude-opus-4" -> "claude",
    "gpt-5-codex" -> "gpt"). An explicit non-empty family overrides."""
    if explicit is not None and explicit.strip():
        return _norm(explicit)
    seg = _norm(model_id).rsplit("/", 1)[-1]
    return re.split(r"[-:@_]", seg, 1)[0]


def _pick(record: dict, *keys: str):
    """First key that is a non-empty string, else None (never coerced, never
    invented)."""
    for k in keys:
        v = record.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def evaluate(record, raw: bytes | None = None) -> dict:
    """Pure verdict over one record. Returns
    {"ok": bool, "refusals": [str, ...], "stamp": dict | None}.
    Writes nothing; the caller decides what a stamp costs."""
    if not isinstance(record, dict):
        return {"ok": False,
                "refusals": [f"identity_unavailable:record (not a JSON object)"],
                "stamp": None}

    refusals: list[str] = []
    vals: dict[str, str] = {}
    for section, key in REQUIRED:
        path = f"{section}.{key}"
        sec = record.get(section)
        if not isinstance(sec, dict):
            refusals.append(
                f"identity_unavailable:{path} ({section} missing or not an object)")
            continue
        v = sec.get(key)
        if not isinstance(v, str) or not v.strip():
            refusals.append(
                f"identity_unavailable:{path} (missing, not a string, or empty)")
            continue
        v = v.strip()
        if key == "config_hash" and not _CONFIG_HASH.match(_norm(v)):
            refusals.append(
                f"identity_unavailable:{path} "
                "(not a fingerprint: want [sha256:]hex of 16-64 chars)")
            continue
        vals[path] = v

    for section in ("executed_by", "verifier"):
        sec = record.get(section)
        if isinstance(sec, dict) and "model_family" in sec:
            fam = sec["model_family"]
            if not isinstance(fam, str) or not fam.strip():
                refusals.append(
                    f"identity_unavailable:{section}.model_family "
                    "(present but not a non-empty string)")

    # No comparison on incomplete identity: refusing to guess also means
    # refusing to *judge* what was never pinned.
    if refusals:
        return {"ok": False, "refusals": refusals, "stamp": None}

    prod_fam = model_family(vals["executed_by.model"],
                            record["executed_by"].get("model_family"))
    ver_fam = model_family(vals["verifier.model"],
                           record["verifier"].get("model_family"))
    same_process = _norm(vals["executed_by.process_id"]) == _norm(vals["verifier.process_id"])
    same_family = prod_fam == ver_fam
    same_harness = _norm(vals["harness_ref.harness_id"]) == _norm(vals["verifier.harness_id"])

    if same_process:
        return {"ok": False,
                "refusals": [f"self_verification:producer_and_verifier_are_one_process"
                             f"({vals['executed_by.process_id']})"],
                "stamp": None}
    if same_family and same_harness:
        return {"ok": False,
                "refusals": [f"self_verification:same_model_family_and_harness"
                             f"({prod_fam}+{vals['harness_ref.harness_id']})"],
                "stamp": None}

    basis = ["different_process"]
    if not same_family:
        basis.append("different_model_family")
    if not same_harness:
        basis.append("different_harness")

    raw_bytes = raw if raw is not None else \
        json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
    stamp = {
        "schema": SCHEMA,
        "asset_id": _pick(record, "asset_id", "id"),
        "verdict": _pick(record, "verdict") or
                   (None if "pass" not in record else
                    ("pass" if record["pass"] is True else "fail")),
        "executed_by": {
            "model": vals["executed_by.model"],
            "model_version": vals["executed_by.model_version"],
            "model_family": prod_fam,
            "process_id": vals["executed_by.process_id"],
        },
        "harness_ref": {
            "harness_id": vals["harness_ref.harness_id"],
            "config_hash": vals["harness_ref.config_hash"],
        },
        "verifier": {
            "model": vals["verifier.model"],
            "model_family": ver_fam,
            "process_id": vals["verifier.process_id"],
            "harness_id": vals["verifier.harness_id"],
        },
        "externality_basis": basis,
        "record_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "stamped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return {"ok": True, "refusals": [], "stamp": stamp}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="acceptance_identity.py",
        description="Stamp WHO ran a done-test and WHO verified it; refuse "
                    "unpinned or self-graded acceptance. Writes only --stamp.")
    ap.add_argument("record", help="done-test result record: path, or '-' for stdin")
    ap.add_argument("--stamp", required=True,
                    help="output path for the identity stamp (the only write)")
    args = ap.parse_args(argv)

    if args.record == "-":
        raw = sys.stdin.buffer.read()
    else:
        try:
            raw = Path(args.record).read_bytes()
        except OSError as e:
            print(f"identity_unavailable:record (cannot read {args.record}: {e.strerror})",
                  file=sys.stderr)
            return 1
    try:
        record = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        print("identity_unavailable:record (not valid JSON — no identity can be "
              "read from an unreadable record)", file=sys.stderr)
        return 1

    res = evaluate(record, raw)
    if not res["ok"]:
        for r in res["refusals"]:
            print(r, file=sys.stderr)
        return 1

    text = json.dumps(res["stamp"], indent=2, sort_keys=True) + "\n"
    try:
        Path(args.stamp).write_text(text, encoding="utf-8")
    except OSError as e:
        print(f"stamp_write_failed:{args.stamp} ({e.strerror}) — nothing was accepted",
              file=sys.stderr)
        return 1
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
