#!/usr/bin/env python3
"""Emit and verify the HARNESS ASSEMBLY CONTRACT for canonical harness YAMLs.

A harness YAML today is an ordered pile of gate ids. Nothing in it declares
WHICH REQUIRED BEHAVIOUR each stage exposes as a socket, WHICH named atom fills
that socket, WHERE a compatible atom may be swapped in, or WHAT data crosses
between stages — so two harness variants cannot be diffed mechanically, gate
dependency stays implied across the whole estate, and a policy denial cannot be
attributed to the policy that produced it.

This script turns each canonical harness YAML into a contract:

  stages[]        the canonical stage list (document order of declared gates)
  ports[]         one socket per stage: the stage's required behaviour declared
                  as an interface (kind, data_kind, failure_tier), not an
                  implementation; a `stop`-tier gate's port is kind=permission,
                  so permission policy is a NAMED port whose bound atom is on
                  the record and a denial is attributable
  bindings[]      which named atom currently fills which port (harness::stage),
                  plus whether the port sits on a swap interface
  swap_points[]   every (kind, data_kind, failure_tier) interface carrying two
                  or more ports — the places one compatible atom may replace
                  another
  fingerprint     "sha256:" + sha256 over the canonical stage list joined by
                  newlines — the stable identity two variants are diffed by
  edges[]         the flow graph: sequence edges between consecutive stages
                  plus consume/produce edges (an artifact path a stage's
                  requirement/proof cites that an upstream stage's proof
                  produces), each carrying data kind and hook-chain order

Deterministic: contracts sort by source path; ports, bindings and swap points
sort by port id; edges sort by (from-ordinal, to-ordinal, data_kind, artifact);
the stage list is document order and the fingerprint anchors it. The same bytes
in always give the same bytes out.

Commands:
  --emit FILE...              print the contract document for every harness
                              YAML given (this is the diffable artifact)
  --verify CONTRACT YAML      recompute the stage list and fingerprint from the
                              YAML and hold the contract against it

Exit codes (the honesty contract):
  0  emit: every file parsed and contract built; verify: contract matches YAML
  1  usage / file-not-found / unparsable input (a refusal to judge, not a verdict)
  2  a contract violation: a stage with no declared port, an orphan port, a
     binding referencing an undeclared port, a fingerprint that does not match
     the YAML content, an edge to a nonexistent stage, a duplicated stage id,
     or a harness declaring no stages at all

Stdlib only. Reads only the paths it is given. Writes only to stdout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compile_harnesses import parse_yaml_subset  # noqa: E402

EMITTER = "harness-assembly-contract/v1"

_EXTENSIONS = (
    "jsonl|json|ya?ml|txt|md|log|csv|tsv|xml|html|pdf|sql|toml|ini|ipynb"
    "|py|sh|ts|tsx|go|rb|rs|js|jsx"
)
# A path with at least one slash and a known extension, or a bare filename with
# one. Leftmost-longest is not automatic in Python regex, so the path branch
# comes first and a word boundary closes the extension list.
ARTIFACT_RE = re.compile(
    r"(?:[\w.~*+-]+/)+[\w.~*+-]*\.(?:%s)\b|[\w][\w.~*+-]*\.(?:%s)\b"
    % (_EXTENSIONS, _EXTENSIONS)
)
LOG_RE = re.compile(r"\blog\b", re.IGNORECASE)
TIER_LISTS = {"halt_gates": "halt", "degrade_gates": "degrade",
              "stop_gates": "stop"}


def harness_body(text: str) -> str:
    """Strip the frontmatter block (a `---` document marker at column 0 at the
    top, closed by the next one) so the body YAML parses as one mapping."""
    lines = text.splitlines()
    markers = [i for i, ln in enumerate(lines) if ln.rstrip() == "---"]
    if len(markers) >= 2 and markers[0] == 0:
        return "\n".join(lines[markers[1] + 1:])
    return text


def _stage_from_gate(gate, category: str, auto_id: str, via: str) -> dict:
    if isinstance(gate, dict):
        req = gate.get("requirement")
        proof = gate.get("proof")
        sid = gate.get("id")
        tier = gate.get("failure_tier")
    else:  # a bare-string gate: requirement-only, defect of the harness, not of this emitter
        req, proof, sid, tier = gate, None, None, None
    return {
        "stage": str(sid) if sid is not None else auto_id,
        "category": category,
        "requires": str(req).strip() if req is not None else "",
        "proof": str(proof).strip() if proof is not None else "",
        "tier": str(tier).strip() if tier else "",
        "via": via,
    }


def harness_stages(h: dict) -> list:
    """Canonical stage list: every declared gate, in document order, across the
    five shapes the estate uses (identity_lock.gates, identity_lock.identity_
    gates, grouped capability_gates, flat capability_gates, top-level gates)."""
    stages: list = []
    idl = h.get("identity_lock") or {}
    if isinstance(idl, dict):
        for n, g in enumerate(idl.get("gates") or [], 1):
            stages.append(_stage_from_gate(g, "Identity Lock",
                                           f"IG-{n:02d}",
                                           f"identity_lock.gates[{n - 1}]"))
        for n, g in enumerate(idl.get("identity_gates") or [], 1):
            stages.append(_stage_from_gate(g, "Identity Lock",
                                           f"IG-{n:02d}",
                                           f"identity_lock.identity_gates[{n - 1}]"))
    cg = h.get("capability_gates") or []
    grouped = bool(cg) and all(isinstance(c, dict) and "gates" in c for c in cg)
    if grouped:
        for ci, cat in enumerate(cg):
            for gi, g in enumerate(cat.get("gates") or []):
                stages.append(_stage_from_gate(
                    g, str(cat.get("category") or "Capability"),
                    f"C{ci + 1}-{gi + 1}",
                    f"capability_gates[{ci}].gates[{gi}]"))
    elif isinstance(cg, list):
        for gi, g in enumerate(cg):
            stages.append(_stage_from_gate(g, "Capability",
                                           f"C{gi + 1}",
                                           f"capability_gates[{gi}]"))
    if not stages and isinstance(h.get("gates"), list):
        for gi, g in enumerate(h["gates"]):
            stages.append(_stage_from_gate(g, "Capability",
                                           f"G-{gi + 1:02d}",
                                           f"gates[{gi}]"))
    return stages


def apply_protocol_tiers(h: dict, stages: list) -> None:
    """A gate without an inline failure_tier takes its tier from the
    failure_protocol id lists, so the interface is the harness's real one."""
    fp = h.get("failure_protocol")
    if not isinstance(fp, dict):
        return
    for key, label in TIER_LISTS.items():
        ids = {str(x) for x in (fp.get(key) or [])}
        for s in stages:
            if not s["tier"] and s["stage"] in ids:
                s["tier"] = label


def artifacts_of(*texts: str) -> list:
    found = set()
    for t in texts:
        if t:
            found.update(ARTIFACT_RE.findall(t))
    return sorted(found)


def classify(stage: dict) -> str:
    if stage["produces"] or stage["consumes"]:
        return "artifact"
    if LOG_RE.search(stage["requires"] + " " + stage["proof"]):
        return "session-log"
    return "assertion"


def fingerprint_of(stages: list) -> str:
    joined = "\n".join(s["stage"] for s in stages)
    return "sha256:" + hashlib.sha256(joined.encode("utf-8")).hexdigest()


def build_contract(path: Path) -> tuple:
    """Derive the assembly contract for one harness YAML.
    Returns (contract_or_None, violations)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, [f"REFUSE {path}: unreadable ({exc})"]
    try:
        h = parse_yaml_subset(harness_body(text), origin=str(path))
    except Exception as exc:  # unparsable input is a refusal, not a verdict
        return None, [f"REFUSE {path}: unparsable YAML subset ({exc})"]
    if not isinstance(h, dict):
        h = {}
    violations = []
    stages = harness_stages(h)
    if not stages:
        violations.append(f"RED [NO_STAGES] {path}: harness declares no gates "
                          "at all — there is no flow graph to contract")
    seen = set()
    for s in stages:
        if s["stage"] in seen:
            violations.append(f"RED [DUPLICATE_STAGE] {path}: stage id "
                              f"{s['stage']!r} declared twice — socket names "
                              "must be unique for edges to resolve")
        seen.add(s["stage"])
    if violations:
        return None, violations

    harness_id = str(h.get("harness_id") or path.stem)
    apply_protocol_tiers(h, stages)
    for i, s in enumerate(stages):
        s["ordinal"] = i
        s["tier"] = s["tier"] or "unspecified"
        s["kind"] = "permission" if s["tier"] == "stop" else "capability"
        s["produces"] = artifacts_of(s["proof"])
        own_basenames = {a.rsplit("/", 1)[-1] for a in s["produces"]}
        cand = artifacts_of(s["requires"], s["proof"])
        s["consumes"] = [a for a in cand
                         if a not in s["produces"]
                         and a.rsplit("/", 1)[-1] not in own_basenames]
        s["data_kind"] = classify(s)

    ports = [{
        "port": f"p::{s['stage']}",
        "category": s["category"],
        "consumes": s["consumes"],
        "data_kind": s["data_kind"],
        "failure_tier": s["tier"],
        "kind": s["kind"],
        "produces": s["produces"],
        "requires": s["requires"],
        "stage": s["stage"],
    } for s in stages]
    ports.sort(key=lambda p: p["port"])

    # swap interfaces: (kind, data_kind, failure_tier) -> ports sharing them
    interfaces: dict = {}
    for s in stages:
        key = (s["kind"], s["data_kind"], s["tier"])
        interfaces.setdefault(key, []).append(f"p::{s['stage']}")
    swap_points = [{
        "interface": {"failure_tier": k[2], "data_kind": k[1], "kind": k[0]},
        "port_count": len(v),
        "ports": sorted(v),
    } for k, v in sorted(interfaces.items(), key=lambda kv: repr(kv[0]))
        if len(v) > 1]

    bindings = [{
        "bound_atom": f"{harness_id}::{s['stage']}",
        "interface": {"data_kind": s["data_kind"], "failure_tier": s["tier"],
                      "kind": s["kind"]},
        "port": f"p::{s['stage']}",
        "swappable": len(interfaces[(s["kind"], s["data_kind"], s["tier"])]) > 1,
        "via": s["via"],
    } for s in stages]
    bindings.sort(key=lambda b: b["port"])

    edges = []
    for i in range(len(stages) - 1):
        a, b = stages[i], stages[i + 1]
        edges.append({
            "artifact": None,
            "data_kind": "sequence",
            "from_port": f"p::{a['stage']}",
            "from_stage": a["stage"],
            "hook_order": b["ordinal"],
            "to_port": f"p::{b['stage']}",
            "to_stage": b["stage"],
        })
    for consumer in stages:
        for token in consumer["consumes"]:
            base = token.rsplit("/", 1)[-1]
            producer = None
            for upstream in stages[: consumer["ordinal"]]:
                for produced in upstream["produces"]:
                    if produced == token or produced.rsplit("/", 1)[-1] == base:
                        producer = (upstream, produced)
            if producer is not None:  # nearest upstream producer wins
                upstream, produced = producer
                edges.append({
                    "artifact": produced,
                    "data_kind": "artifact",
                    "from_port": f"p::{upstream['stage']}",
                    "from_stage": upstream["stage"],
                    "hook_order": consumer["ordinal"],
                    "to_port": f"p::{consumer['stage']}",
                    "to_stage": consumer["stage"],
                })
    edges.sort(key=lambda e: (e["hook_order"], e["from_stage"],
                              e["to_stage"], e["data_kind"],
                              e["artifact"] or ""))

    contract = {
        "edges": edges,
        "fingerprint": fingerprint_of(stages),
        "harness": harness_id,
        "ports": ports,
        "bindings": bindings,
        "schema": EMITTER,
        "source": str(path),
        "stages": [s["stage"] for s in stages],
        "swap_points": swap_points,
    }
    return contract, []


def cmd_emit(files: list) -> int:
    paths = [Path(f) for f in files]
    refusals = [f"REFUSE {p}: not a readable file" for p in paths
                if not p.is_file()]
    if refusals or not paths:
        for line in refusals:
            print(line)
        return 1
    contracts, violations = [], []
    for p in paths:
        contract, viols = build_contract(p)
        violations.extend(viols)
        if contract is not None:
            contracts.append(contract)
    if violations:
        for line in violations:
            print(line)
        return 2
    contracts.sort(key=lambda c: c["source"])
    doc = {"contracts": contracts, "emitter": EMITTER,
           "n_contracts": len(contracts)}
    print(json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


def cmd_verify(contract_path: Path, harness_path: Path) -> int:
    if not contract_path.is_file() or not harness_path.is_file():
        for p in (contract_path, harness_path):
            if not p.is_file():
                print(f"REFUSE {p}: not a readable file")
        return 1
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"REFUSE {contract_path}: unreadable contract ({exc})")
        return 1
    if not isinstance(contract, dict) or "ports" not in contract:
        print(f"REFUSE {contract_path}: not a single assembly contract "
              "(emit a --emit document's contract object, not the document)")
        return 1
    try:
        h = parse_yaml_subset(harness_body(harness_path.read_text(
            encoding="utf-8")), origin=str(harness_path))
    except (OSError, Exception) as exc:
        print(f"REFUSE {harness_path}: unparsable YAML subset ({exc})")
        return 1
    if not isinstance(h, dict):
        h = {}
    stages = harness_stages(h)
    stage_ids = [s["stage"] for s in stages]
    known = set(stage_ids)
    declared = {p.get("port") for p in contract.get("ports") or []
                if isinstance(p, dict)}

    violations = []
    want_fp = fingerprint_of(stages)
    if contract.get("fingerprint") != want_fp:
        violations.append(
            f"RED [FINGERPRINT_MISMATCH] {harness_path}: contract fingerprint "
            f"{contract.get('fingerprint')!r} does not match the YAML content "
            f"(recomputed {want_fp!r}) — never edit the fingerprint to close "
            "a mismatch; fix the stage list it describes")
    for sid in stage_ids:
        if f"p::{sid}" not in declared:
            violations.append(
                f"RED [STAGE_NO_PORT] {harness_path}: stage {sid!r} has no "
                "declared port — a required behaviour no socket exposes "
                "cannot be bound, swapped, or diffed")
    for p in contract.get("ports") or []:
        if isinstance(p, dict) and p.get("stage") not in known:
            violations.append(
                f"RED [ORPHAN_PORT] {harness_path}: port {p.get('port')!r} "
                f"declares stage {p.get('stage')!r} which the YAML does not "
                "contain — contract and YAML gate ids have diverged")
    for b in contract.get("bindings") or []:
        if isinstance(b, dict) and b.get("port") not in declared:
            violations.append(
                f"RED [DANGLING_BINDING] {harness_path}: binding "
                f"{b.get('bound_atom')!r} references undeclared port "
                f"{b.get('port')!r}")
    for e in contract.get("edges") or []:
        if not isinstance(e, dict):
            continue
        for end in ("from_stage", "to_stage"):
            if e.get(end) not in known:
                violations.append(
                    f"RED [EDGE_TO_NONEXISTENT_STAGE] {harness_path}: edge "
                    f"{e.get('from_stage')!r} -> {e.get('to_stage')!r} "
                    f"references stage {e.get(end)!r} that does not exist")
    if violations:
        for line in violations:
            print(line)
        return 2
    print(f"GREEN {contract.get('harness', harness_path.stem)}: "
          f"{len(stage_ids)} stages, {len(declared)} ports, "
          f"{len(contract.get('bindings') or [])} bindings, "
          f"{len(contract.get('swap_points') or [])} swap points, "
          f"{len(contract.get('edges') or [])} edges, {want_fp}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="emit/verify the harness assembly contract")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--emit", nargs="+", metavar="HARNESS.yaml",
                      help="print the contract document for each harness YAML")
    mode.add_argument("--verify", nargs=2, metavar=("CONTRACT.json",
                                                    "HARNESS.yaml"),
                      help="check one emitted contract against its YAML")
    args = ap.parse_args(argv)
    if args.emit is not None:
        return cmd_emit(args.emit)
    return cmd_verify(Path(args.verify[0]), Path(args.verify[1]))


if __name__ == "__main__":
    raise SystemExit(main())
