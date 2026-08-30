#!/usr/bin/env python3
"""Compile RIG goal-harness YAMLs into rig-goal-engine GoalSpec files.

Reads every capabilities/harnesses/*.yaml in the hub repo, maps it onto the
field set the engine's own loader builds (~/rig-goal-engine/yaml_loader.py
load_all_specs -> models.GoalSpec), and emits one spec file per harness into
out/harness-goalspecs/ named by harness stem.

Stdlib-only by design: a small indent parser covers the known YAML subset used
by the harness files (block mappings/sequences, flow sequences, quoted
strings), and emitted files carry JSON content (a strict subset of YAML,
accepted by yaml.safe_load — verified against PyYAML 6.0.3 in the engine
driver scripts/validate_engine.py).

Mapping rules (bound to engine GoalSpec fields — see docs/HARNESS-COMPILE-REPORT.md):
  id       -> "GL-" + upper(stem)          (GoalSpec id validator requires GL-)
  coordinate <- first entry of each coordinate_space axis, "Lx-Dy-Az-<step>"
  gates[]  <- identity_lock.gates + capability_gates[].gates[]
              failure_tier halt|stop -> required/blocking, weight 1.0
              failure_tier degrade    -> non-blocking weighted,  weight 0.5
              each gate `proof` string copied verbatim as `command`
              (GateCheck.command, models.py GateCheck)
  success_conditions <- definition_of_done
  quality_criteria   <- every gate requirement (feeds the engine's
              declarative gate emission in engine.py:_run_spec_gates)
  approval_required  <- True iff failure_protocol.stop_gates is non-empty

Subcommands:
  compile   parse + compile + write out/harness-goalspecs/ (default)
  list      print the compiled JSON paths (used by the engine-env validator)

Engine-side validation is NOT done here (no PyYAML in system python); run:
  cd ~/rig-goal-engine && uv run --no-sync python \
      ~/Developer/rig-capabilities/scripts/validate_engine.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HUB = Path(__file__).resolve().parent.parent
HARNESS_DIR = HUB / "capabilities" / "harnesses"
OUT_DIR = HUB / "out" / "harness-goalspecs"

BLOCKING_TIERS = {"halt", "stop"}
WEIGHTED_TIERS = {"degrade"}


# ── minimal indent-based YAML subset parser ─────────────────────────────

def _strip_comment(line: str) -> str:
    out, in_q, qc = [], False, ""
    for ch in line:
        if in_q:
            out.append(ch)
            if ch == qc:
                in_q = False
        elif ch in "\"'":
            in_q, qc = True, ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
    return "".join(out).rstrip()


def _split_key(text: str):
    """Split `key: value` respecting quotes; return (key, rest) or None."""
    in_q, qc = False, ""
    for i, ch in enumerate(text):
        if in_q:
            if ch == qc:
                in_q = False
        elif ch in "\"'":
            in_q, qc = True, ch
        elif ch == ":" and (i + 1 == len(text) or text[i + 1] == " "):
            return text[:i].strip(), text[i + 1:].strip()
    return None


def _scalar(raw: str):
    raw = raw.strip()
    if raw == "":
        return None
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        return [] if not inner else [_scalar(p) for p in _split_flow(inner)]
    if raw[0] in "\"'" and raw[-1] == raw[0] and len(raw) >= 2:
        try:
            return json.loads(raw) if raw[0] == '"' else raw[1:-1]
        except json.JSONDecodeError:
            return raw[1:-1]
    if raw in ("true", "false"):
        return raw == "true"
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        pass
    return raw


def _split_flow(inner: str):
    parts, buf, in_q, qc = [], [], False, ""
    for ch in inner:
        if in_q:
            buf.append(ch)
            if ch == qc:
                in_q = False
        elif ch in "\"'":
            in_q, qc = True, ch
            buf.append(ch)
        elif ch == ",":
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf))
    return [p.strip() for p in parts]


def _tokenize(text: str):
    toks = []
    for n, raw in enumerate(text.splitlines(), 1):
        s = _strip_comment(raw)
        if not s.strip():
            continue
        toks.append((len(s) - len(s.lstrip(" ")), s.strip(), n))
    return toks


def _parse_block(toks, i, indent):
    if toks[i][1].startswith("- "):
        return _parse_seq(toks, i, indent)
    return _parse_map(toks, i, indent)


def _parse_map(toks, i, indent):
    out = {}
    while i < len(toks) and toks[i][0] == indent and not toks[i][1].startswith("- "):
        ind, content, ln = toks[i]
        kv = _split_key(content)
        if kv is None:
            raise ValueError(f"line {ln}: expected 'key: value', got: {content!r}")
        key, rest = kv
        if rest:
            out[key] = _scalar(rest)
            i += 1
        else:
            i += 1
            if i < len(toks) and toks[i][0] > ind:
                out[key], i = _parse_block(toks, i, toks[i][0])
            elif i < len(toks) and toks[i][0] == ind and toks[i][1].startswith("- "):
                out[key], i = _parse_seq(toks, i, ind)  # seq at parent indent
            else:
                out[key] = {}
    return out, i


def _parse_seq(toks, i, indent):
    out = []
    while i < len(toks) and toks[i][0] == indent and toks[i][1].startswith("- "):
        item_content = toks[i][1][2:].strip()
        item_ln = toks[i][2]
        i += 1
        kv = _split_key(item_content)
        if kv is None:
            out.append(_scalar(item_content))
            continue
        # mapping item: first key inline; siblings continue at indent+2
        m = {}
        key, rest = kv
        sub_indent = indent + 2
        if rest:
            m[key] = _scalar(rest)
        else:
            if i < len(toks) and toks[i][0] > sub_indent:
                m[key], i = _parse_block(toks, i, toks[i][0])
            else:
                m[key] = {}
        while i < len(toks) and toks[i][0] == sub_indent and not toks[i][1].startswith("- "):
            sub, i = _parse_map(toks, i, sub_indent)
            m.update(sub)
        out.append(m)
    return out, i


def parse_yaml_subset(text: str, origin: str = "<string>"):
    toks = _tokenize(text)
    if not toks:
        return {}
    if toks[0][0] != 0:
        raise ValueError(f"{origin}: unexpected top-level indentation")
    obj, i = _parse_block(toks, 0, 0)
    if i != len(toks):
        raise ValueError(f"{origin}: unparsed content at line {toks[i][2]}")
    return obj


# ── harness -> GoalSpec payload ──────────────────────────────────────────

def harness_goal_id(stem: str) -> str:
    return "GL-" + stem.upper()


def _failure_protocol(h: dict) -> dict:
    fp = h.get("failure_protocol") or {}
    return {
        "halt": [str(x) for x in (fp.get("halt_gates") or [])],
        "degrade": [str(x) for x in (fp.get("degrade_gates") or [])],
        "stop": [str(x) for x in (fp.get("stop_gates") or [])],
        "notes": fp.get("notes", ""),
    }


def compile_harness(stem: str, h: dict) -> dict:
    """Map one parsed harness dict to an engine-loadable GoalSpec goal payload."""
    errors = []
    cs = h.get("coordinate_space") or {}
    levels = cs.get("levels") or []
    diamonds = cs.get("primary_diamonds") or cs.get("diamonds") or []
    bms = cs.get("bms_modes") or []
    steps = cs.get("iqrsqpi_steps") or []
    if not (levels and diamonds and bms and steps):
        errors.append("coordinate_space missing an axis")
    anchor = f"L{levels[0]}-{diamonds[0]}-{bms[0]}-{steps[0]}" if not errors else "L1-D1-A1-I"
    coord_level = int(re.sub(r"\D", "", str(levels[0]))) if levels else 1
    if not 1 <= coord_level <= 7:
        errors.append(f"coordinate level {coord_level} outside engine range L1-L7 (models.py:71)")

    fp = _failure_protocol(h)
    tier_of = {}
    for tier, ids in (("halt", fp["halt"]), ("degrade", fp["degrade"]), ("stop", fp["stop"])):
        for gid in ids:
            tier_of[gid] = tier

    gates = []

    def add_gate(g: dict, category: str, default_tier: str):
        gid = str(g.get("id", ""))
        req = str(g.get("requirement", ""))
        proof = str(g.get("proof", ""))
        if not gid or not req or not proof:
            errors.append(f"gate {gid or '?'} missing id/requirement/proof")
            return
        tier = str(g.get("failure_tier") or default_tier)
        declared = tier_of.get(gid)
        if declared and declared != tier:
            errors.append(f"gate {gid}: failure_tier {tier!r} contradicts failure_protocol {declared!r}")
        if tier not in BLOCKING_TIERS | WEIGHTED_TIERS:
            errors.append(f"gate {gid}: unknown failure_tier {tier!r}")
            return
        blocking = tier in BLOCKING_TIERS
        gates.append({
            "id": gid,
            "category": category,
            "name": f"{gid} {req[:60]}",
            "description": req,
            "command": proof,  # proof string copied verbatim as the check command
            "failure_tier": tier,
            "required": blocking,
            "required_verdict": "GO" if blocking else "SOFT",
            "weight": 1.0 if blocking else 0.5,
        })

    idl = h.get("identity_lock") or {}
    for g in idl.get("gates") or []:
        add_gate(g, "Identity Lock", "halt")
    for cat in h.get("capability_gates") or []:
        for g in cat.get("gates") or []:
            add_gate(g, str(cat.get("category", "")), "halt")

    declared_ids = set(tier_of)
    gate_ids = {g["id"] for g in gates}
    for missing in sorted(declared_ids - gate_ids):
        errors.append(f"failure_protocol names gate {missing} with no gate definition")

    stop_present = bool(fp["stop"])
    dod = [str(x) for x in (h.get("definition_of_done") or [])]
    final_rule = [str(x) for x in (h.get("final_rule") or [])]
    failure_states = []
    if fp["notes"]:
        failure_states.append(fp["notes"])
    if fp["stop"]:
        failure_states.append("stop gate(s) " + ", ".join(fp["stop"]) + ": halt session; human approval required before continuing")
    if fp["halt"]:
        failure_states.append("halt gate(s) " + ", ".join(fp["halt"]) + ": no progress without gate evidence")

    payload = {
        "id": harness_goal_id(stem),
        "name": str(h.get("harness_name", stem)),
        "description": f"{h.get('harness_name', stem)} [{h.get('session_type', '')}] — compiled from capabilities/harnesses/{stem}.yaml",
        "anchor": anchor,
        "bms_mode": str(bms[0]) if bms else "A1",
        "gate": dod[0] if dod else "",
        "gates": gates,
        "packet_type": "ProofPacket",
        "depends_on": [],
        "preconditions": {
            "startup_phrase": str(idl.get("startup_phrase", "")),
            "harness_tuple": str(h.get("harness_tuple", "")),
            "bms_bias": str(h.get("bms_bias", "")),
            "meta": {
                "harness_id": str(h.get("harness_id", stem)),
                "session_type": str(h.get("session_type", "")),
                "governs_loops": [str(x) for x in (h.get("governs_loops") or [])],
                "coordinate_space": {k: v for k, v in cs.items()},
                "self_improvement": h.get("self_improvement") or {},
            },
        },
        "success_conditions": dod,
        "failure_states": failure_states,
        "quality_criteria": [g["description"] for g in gates],
        "anti_patterns": [str(x) for x in (h.get("anti_patterns") or [])],
        "anti_generic_threshold": float(h.get("anti_generic_threshold", 80.0)),
        "approval_required": stop_present,
        "steps": [],
        "_meta": {
            "source": f"capabilities/harnesses/{stem}.yaml",
            "final_rule": final_rule,
            "failure_protocol": fp,
        },
    }
    return {"payload": payload, "errors": errors, "n_gates": len(gates),
            "n_blocking": sum(1 for g in gates if g["required"]),
            "n_weighted": sum(1 for g in gates if not g["required"])}


# ── commands ─────────────────────────────────────────────────────────────

def cmd_compile(_: argparse.Namespace) -> int:
    sources = sorted(HARNESS_DIR.glob("*.yaml"))
    if not sources:
        print(f"FAIL: no harness files in {HARNESS_DIR}", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ok, failed = 0, []
    total_gates = 0
    for src in sources:
        try:
            h = parse_yaml_subset(src.read_text(), origin=src.name)
        except Exception as e:
            failed.append((src.name, f"parse error: {e}"))
            continue
        res = compile_harness(src.stem, h)
        if res["errors"]:
            failed.append((src.name, "; ".join(res["errors"])))
            continue
        payload = res["payload"]
        doc = {"goals": [payload]}  # engine loader reads data["goals"] (yaml_loader.py:54)
        json_path = OUT_DIR / f"{src.stem}.json"
        yaml_path = OUT_DIR / f"{src.stem}.yaml"
        json_path.write_text(json.dumps(doc, indent=2) + "\n")
        # JSON is a strict subset of YAML 1.2; yaml.safe_load accepts it.
        yaml_path.write_text(json.dumps(doc, indent=2) + "\n")
        ok += 1
        total_gates += res["n_gates"]
        print(f"OK  {src.name:40s} -> {yaml_path.name} "
              f"gates={res['n_gates']} (blocking={res['n_blocking']} weighted={res['n_weighted']})")
    print(f"\ncompiled {ok}/{len(sources)} harness specs -> {OUT_DIR} (total gates: {total_gates})")
    for name, why in failed:
        print(f"FAIL {name}: {why}")
    return 0 if not failed and ok == len(sources) else 1


def cmd_list(_: argparse.Namespace) -> int:
    for p in sorted(OUT_DIR.glob("*.yaml")):
        print(p)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("compile")
    sub.add_parser("list")
    args = ap.parse_args()
    return {"compile": cmd_compile, "list": cmd_list, None: cmd_compile}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
