#!/usr/bin/env python3
"""Compile RIG goal-harness YAMLs into rig-goal-engine GoalSpec files.

Reads every capabilities/harnesses/*.yaml in the hub repo, maps it onto the
field set the engine's own loader builds (~/rig-goal-engine/yaml_loader.py
load_all_specs -> models.GoalSpec), and emits one spec file per harness into
out/harness-goalspecs/ named by harness stem.

Stdlib-only by design: a small indent parser covers the YAML subset used by
the harness files (block mappings/sequences, flow sequences, quoted/plain
scalars incl. multi-line folded continuations, `|`/`>` block scalars, and
cross-line quote state so `#`
inside a quoted scalar is content, not a comment, and `---` alone at column 0
as a document marker — every harness is two documents, catalog frontmatter
then harness body, which land in one map because no key is shared), and
emitted files carry
JSON content — a strict subset of YAML 1.2 accepted by yaml.safe_load
(PyYAML 6.0.3 in the engine venv; per-file structural fidelity vs PyYAML is
proven by scripts/validate_engine.py Phase 1).

Three harness shapes exist (inventory over all 56 files, 2026-08-30):
  A (19: hA-*, mh-*)  identity_lock.gates dicts (id/requirement/proof),
                      capability_gates = [{category, gates:[...]}],
                      failure_protocol {halt_gates, degrade_gates,
                      stop_gates, notes}
  B (24: hC-*, hD-*)  same but identity gates carry only {id, requirement}
                      (no proof / no failure_tier) and no notes field
  C (13: hB-*)        identity_lock.identity_gates = list[str],
                      capability_gates = flat list of gates
                      {id: CG-NN, name, category, requirement, proof,
                      failure_tier}, failure_protocol {halt, degrade, stop
                      (prose), gate_mapping: {CG-id: tier}}

Mapping rules (bound to engine GoalSpec — models.py:204-232):
  id            "GL-" + upper(stem)   (validator requires GL-, models.py:227)
  coordinate    "<L?>{levels[0]}-{primary_diamonds[0]}-{bms_modes[0]}
                 -{iqrsqpi_steps[0]}"  (parseable, models.py:79-88)
  gates[]       identity gates + capability gates, each dict:
                id, category, name, description (requirement verbatim),
                command (proof verbatim; null where source has no proof),
                failure_tier, required (halt|stop -> True), required_verdict
                (GO if required else SOFT), weight (1.0 blocking / 0.5 degrade)
  success_conditions  definition_of_done
  quality_criteria    every gate requirement verbatim (the engine emits one
                declarative GateCheck per quality_criteria in its no-LLM
                simple-loop gate path, engine.py:403-424)
  failure_states      failure_protocol tier prose + generated tier summaries
  approval_required   True iff any stop-tier gate exists
  anti_generic_threshold / packet_type / steps  engine loader defaults
                 (yaml_loader.py:69,75,77); harnesses carry no AGF value

Subcommands:
  compile     parse + compile + write out/harness-goalspecs/ (default)
  list        print emitted spec yaml paths (for the engine-env validator)
  parse FILE  print stdlib-parsed harness YAML as JSON (fidelity check)

Engine-side validation runs under the engine env:
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

def _scan_quotes(text: str, in_q: bool, qc: str):
    """Advance quote state across one line. Handles '' and backslash escapes."""
    i = 0
    while i < len(text):
        ch = text[i]
        if in_q:
            if qc == '"' and ch == "\\":
                i += 2
                continue
            if ch == qc:
                if qc == "'" and i + 1 < len(text) and text[i + 1] == "'":
                    i += 2
                    continue
                in_q = False
        elif ch in "\"'":
            in_q, qc = True, ch
        i += 1
    return in_q, qc


def _strip_comment(line: str, in_q: bool, qc: str):
    """Strip a trailing ` #` comment outside quotes (single full-line scan).

    Returns (visible, in_q, qc, fold_open). fold_open is True when the
    line's VALUE scalar starts with a quote char and leaves a quote open —
    only then may a multi-line quoted scalar begin (unbalanced quotes inside
    a plain scalar, e.g. '#hex' in a grep pattern, must NOT open one).
    A `#` only starts a comment when outside quotes and preceded by
    whitespace (or line start); inside an open quote it is content.
    """
    cut = None
    i = 0
    while i < len(line):
        ch = line[i]
        if in_q:
            if qc == '"' and ch == "\\":
                i += 2
                continue
            if ch == qc:
                if qc == "'" and i + 1 < len(line) and line[i + 1] == "'":
                    i += 2
                    continue
                in_q = False
        elif ch in "\"'":
            in_q, qc = True, ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            cut = i
            break
        i += 1
    visible = (line[:cut] if cut is not None else line).rstrip()
    fold_open = False
    if in_q:
        body = visible.strip()
        if body.startswith("- "):
            body = body[2:].lstrip()
        else:
            kv = _split_key(body)
            if kv:
                body = kv[1].lstrip()
        fold_open = bool(body) and body[0] in "\"'"
    return visible, in_q, qc, fold_open


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


def _looks_key(text: str) -> bool:
    return not text.startswith("- ") and _split_key(text) is not None


def _scalar(raw: str):
    raw = raw.strip()
    if raw == "":
        return None
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        return [] if not inner else [_scalar(p) for p in _split_flow(inner)]
    if raw[0] in "\"'" and raw[-1] == raw[0] and len(raw) >= 2:
        try:
            return json.loads(raw) if raw[0] == '"' else raw[1:-1].replace("''", "'")
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


DOC_MARKER = "---"


def _is_doc_marker(raw: str) -> bool:
    """True for a YAML document-start marker sitting alone at column 0.

    Every harness file is a two-document YAML: document one is the catalog
    frontmatter (`outcome` / `done_when` / `great_example` / `quality_floor`),
    document two is the harness body. The marker is structural, so it is
    dropped at tokenize time and both documents land in one map — no key is
    shared between them in any file of the estate. An indented `---` (a rule
    inside a block scalar) is content and never matches: `rstrip` alone keeps
    the column-0 requirement.
    """
    return raw.rstrip() == DOC_MARKER


def _tokenize(text: str):
    toks = []
    in_fold = False           # inside a multi-line quoted scalar value
    in_q, qc = False, ""
    for n, raw in enumerate(text.splitlines(), 1):
        if in_fold:
            # `#` is content inside an open quoted scalar; no comment strip
            s = raw.rstrip()
            in_q, qc = _scan_quotes(s, in_q, qc)
            if not in_q:
                in_fold = False
        else:
            if _is_doc_marker(raw):
                continue      # never reached mid-scalar: in_fold owns those lines
            s, in_q, qc, fold_open = _strip_comment(raw, False, "")
            if fold_open and in_q:
                in_fold = True
            elif in_q:
                in_q, qc = False, ""  # plain scalar w/ inner quotes: no bleed
        if not s.strip():
            continue
        toks.append((len(s) - len(s.lstrip(" ")), s.strip(), n))
    return toks


def _continuation(toks, i, key_indent, in_q, qc):
    """Absorb folded-scalar continuation lines deeper than key_indent.

    YAML folds a multi-line plain/quoted scalar into space-joined text.
    While a quote is open, absorb unconditionally until the line closing it.
    When unquoted, absorb only lines that are not themselves mapping keys
    or list items. Returns (joined_text_or_None, i, in_q, qc).
    """
    parts = []
    started_in_q = in_q
    while i < len(toks) and toks[i][0] > key_indent:
        content = toks[i][1]
        if not in_q:
            if _looks_key(content) or content.startswith("- "):
                break
        parts.append(content)
        in_q, qc = _scan_quotes(content, in_q, qc)
        i += 1
        if started_in_q and not in_q:
            break  # the quote closed on this line; fold complete
    return (" ".join(parts) if parts else None), i, in_q, qc


BLOCK_INDICATORS = ("|", "|-", "|+", ">", ">-", ">+")


def _absorb_block(toks, i, key_indent, indicator):
    """Absorb a `|` / `>` block scalar's content lines.

    Block-scalar lines are content, not structure: a line carrying `: ` inside
    a literal block is prose, so the `_looks_key` guard that bounds a plain
    scalar must not stop the absorb here. `|` keeps line breaks, `>` folds to
    spaces; a trailing `-` strips the final newline, `+` keeps it (as does the
    default clip). Blank lines are already gone from the token stream, so one
    indentation level per block is the covered subset.
    """
    parts = []
    while i < len(toks) and toks[i][0] > key_indent:
        parts.append(toks[i][1])
        i += 1
    if not parts:
        return indicator, i
    sep = "\n" if indicator[0] == "|" else " "
    text = sep.join(parts)
    return (text if indicator.endswith("-") else text + "\n"), i


def _fold_after_scalar(toks, i, key_indent, value):
    """Fold continuation lines into `value` if any exist at deeper indent."""
    if value.strip() in BLOCK_INDICATORS:
        return _absorb_block(toks, i, key_indent, value.strip())
    in_q, qc = _scan_quotes(value, False, "")
    if in_q:
        fold, i, _, _ = _continuation(toks, i, key_indent, in_q, qc)
        return (value + " " + fold) if fold else value, i
    if i < len(toks) and toks[i][0] > key_indent and not _looks_key(toks[i][1]) \
            and not toks[i][1].startswith("- "):
        fold, i, _, _ = _continuation(toks, i, key_indent, False, "")
        return (value + " " + fold) if fold else value, i
    return value, i


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
            i += 1
            val, i = _fold_after_scalar(toks, i, ind, rest)
            out[key] = _scalar(val)
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
        content = toks[i][1][2:].strip()
        i += 1
        kv = _split_key(content)
        if kv is None:
            val, i = _fold_after_scalar(toks, i, indent, content)
            out.append(_scalar(val))
            continue
        # mapping item: first key inline; sibling keys continue deeper
        m = {}
        key, rest = kv
        if rest:
            m[key] = _scalar(rest)
        else:
            if i < len(toks) and toks[i][0] > indent:
                m[key], i = _parse_block(toks, i, toks[i][0])
            else:
                m[key] = {}
        while i < len(toks) and toks[i][0] > indent and not toks[i][1].startswith("- "):
            sub, i = _parse_map(toks, i, toks[i][0])
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
        raise ValueError(f"{origin}: unparsed content at line {toks[i][2]}: {toks[i][1][:60]!r}")
    return obj


# ── harness -> GoalSpec payload ──────────────────────────────────────────

def harness_goal_id(stem: str) -> str:
    return "GL-" + stem.upper()


def _as_ids(v):
    return [str(x) for x in v] if isinstance(v, list) else []


def _as_prose(v):
    return v.strip() if isinstance(v, str) else ""


def _as_list(v):
    return v if isinstance(v, list) else ([v] if v else [])


def _failure_protocol(h: dict) -> dict:
    fp = h.get("failure_protocol") or {}
    gm = fp.get("gate_mapping") if isinstance(fp.get("gate_mapping"), dict) else {}
    prose = []
    for k in ("notes", "halt", "degrade", "stop"):
        p = _as_prose(fp.get(k))
        if p:
            prose.append(f"{k}: {p}")
    return {
        "halt": _as_ids(fp.get("halt_gates")) or _as_ids(fp.get("halt")),
        "degrade": _as_ids(fp.get("degrade_gates")) or _as_ids(fp.get("degrade")),
        "stop": _as_ids(fp.get("stop_gates")) or _as_ids(fp.get("stop")),
        "gate_mapping": {str(k): str(v) for k, v in gm.items()},
        "prose": prose,
    }


def collect_source_gates(h: dict):
    """Yield (gate_dict, category, auto_id) for every gate in a harness."""
    idl = h.get("identity_lock") or {}
    for n, g in enumerate(idl.get("gates") or [], 1):
        yield g, "Identity Lock", f"IG-{n:02d}"
    for n, s in enumerate(idl.get("identity_gates") or [], 1):
        yield {"id": f"IG-{n:02d}", "requirement": str(s)}, "Identity Lock", f"IG-{n:02d}"
    cg = h.get("capability_gates") or []
    if cg and all("gates" not in c for c in cg):  # shape C: flat gate list
        for g in cg:
            yield g, str(g.get("category", "Capability")), None
    else:
        for cat in cg:
            for g in cat.get("gates") or []:
                yield g, str(cat.get("category", "")), None


def compile_harness(stem: str, h: dict) -> dict:
    """Map one parsed harness dict to an engine-loadable GoalSpec goal payload."""
    errors = []
    cs = h.get("coordinate_space") or {}
    levels = _as_list(cs.get("levels"))
    diamonds = _as_list(cs.get("primary_diamonds") or cs.get("diamonds"))
    bms = _as_list(cs.get("bms_modes"))
    steps = _as_list(cs.get("iqrsqpi_steps"))
    if not (levels and diamonds and bms and steps):
        errors.append("coordinate_space missing an axis")
        anchor = "L1-D1-A1-I"
    else:
        lv = str(levels[0])
        if not lv.startswith("L"):
            lv = "L" + lv
        anchor = f"{lv}-{diamonds[0]}-{bms[0]}-{steps[0]}"
    if levels:
        lvl = int(re.sub(r"\D", "", str(levels[0])))
        if not 1 <= lvl <= 7:
            errors.append(f"coordinate level L{lvl} outside engine range L1-L7 (models.py:71)")

    fp = _failure_protocol(h)
    tier_of = {}
    for tier in ("halt", "degrade", "stop"):
        for gid in fp[tier]:
            tier_of[gid] = tier
    for gid, tier in fp["gate_mapping"].items():
        tier_of[gid] = tier

    gates, no_proof = [], 0
    for g, category, auto_id in collect_source_gates(h):
        gid = str(g.get("id") or auto_id or "")
        req = str(g.get("requirement", ""))
        if not gid or not req:
            errors.append(f"gate {gid or '?'} missing id/requirement")
            continue
        proof = g.get("proof")
        proof = str(proof) if proof is not None else None
        declared = tier_of.get(gid)
        explicit = str(g["failure_tier"]).strip().lower() if g.get("failure_tier") else None
        tier = explicit or declared or "halt"  # explicit > declared > identity/default
        if explicit and declared and declared != explicit:
            errors.append(f"gate {gid}: failure_tier {explicit!r} contradicts failure_protocol {declared!r}")
        if tier not in BLOCKING_TIERS | WEIGHTED_TIERS:
            errors.append(f"gate {gid}: unknown failure_tier {tier!r}")
            continue
        if proof is None:
            no_proof += 1
        blocking = tier in BLOCKING_TIERS
        nm = str(g.get("name", "")).strip()
        gates.append({
            "id": gid,
            "category": category,
            "name": (f"{gid} {nm}" if nm else f"{gid} {req[:60]}").strip(),
            "description": req,
            "command": proof,  # proof string copied verbatim as the check command
            "failure_tier": tier,
            "required": blocking,
            "required_verdict": "GO" if blocking else "SOFT",
            "weight": 1.0 if blocking else 0.5,
        })

    declared_ids = set(tier_of)
    gate_ids = {g["id"] for g in gates}
    for missing in sorted(declared_ids - gate_ids):
        errors.append(f"failure_protocol names gate {missing} with no gate definition")

    dod = [str(x) for x in _as_list(h.get("definition_of_done"))]
    final_rule = [str(x) for x in _as_list(h.get("final_rule"))]
    failure_states = list(fp["prose"])
    if fp["stop"]:
        failure_states.append("stop gate(s) " + ", ".join(fp["stop"]) + ": session halts; human Gate-D approval required before any continuation or outward action")
    if fp["halt"]:
        failure_states.append("halt gate(s) " + ", ".join(fp["halt"]) + ": no progress without gate evidence")
    if fp["degrade"]:
        failure_states.append("degrade gate(s) " + ", ".join(fp["degrade"]) + ": continue with deficit logged in the Definition of Done waiver")

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
            "startup_phrase": str((h.get("identity_lock") or {}).get("startup_phrase", "")),
            "harness_tuple": str(h.get("harness_tuple", "")),
            "bms_bias": str(h.get("bms_bias", "")),
            "meta": {
                "harness_id": str(h.get("harness_id", stem)),
                "session_type": str(h.get("session_type", "")),
                "governs_loops": [str(x) for x in _as_list(h.get("governs_loops"))],
                "coordinate_space": dict(cs),
                "self_improvement": h.get("self_improvement") or {},
                "doctrine_focus": h.get("doctrine_focus"),
                "library": h.get("library"),
                "batch": h.get("batch"),
            },
        },
        "success_conditions": dod,
        "failure_states": failure_states,
        "quality_criteria": [g["description"] for g in gates],
        "anti_patterns": [str(x) for x in _as_list(h.get("anti_patterns"))],
        "anti_generic_threshold": float(h.get("anti_generic_threshold", 80.0)),
        "approval_required": bool(fp["stop"]) or any(g["failure_tier"] == "stop" for g in gates),
        "steps": [],
        "_meta": {
            "source": f"capabilities/harnesses/{stem}.yaml",
            "final_rule": final_rule,
            "failure_protocol": fp,
            "gates_without_proof": [g["id"] for g in gates if g["command"] is None],
        },
    }
    return {"payload": payload, "errors": errors, "n_gates": len(gates),
            "n_blocking": sum(1 for g in gates if g["required"]),
            "n_weighted": sum(1 for g in gates if not g["required"]),
            "n_no_proof": no_proof}


# ── commands ─────────────────────────────────────────────────────────────

def cmd_compile(_: argparse.Namespace) -> int:
    sources = sorted(HARNESS_DIR.glob("*.yaml"))
    if not sources:
        print(f"FAIL: no harness files in {HARNESS_DIR}", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ok, failed = 0, []
    total_gates = no_proof_total = 0
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
        doc = {"goals": [res["payload"]]}  # engine loader reads data["goals"] (yaml_loader.py:54)
        text = json.dumps(doc, indent=2) + "\n"
        (OUT_DIR / f"{src.stem}.json").write_text(text)
        # JSON is a strict subset of YAML 1.2; yaml.safe_load accepts it.
        (OUT_DIR / f"{src.stem}.yaml").write_text(text)
        ok += 1
        total_gates += res["n_gates"]
        no_proof_total += res["n_no_proof"]
        print(f"OK  {src.name:40s} gates={res['n_gates']:3d} "
              f"blocking={res['n_blocking']:3d} weighted={res['n_weighted']:2d} "
              f"no_proof={res['n_no_proof']}")
    print(f"\ncompiled {ok}/{len(sources)} harness specs -> {OUT_DIR} "
          f"(gates: {total_gates}, without-proof: {no_proof_total})")
    for name, why in failed:
        print(f"FAIL {name}: {why}")
    return 0 if not failed and ok == len(sources) else 1


def cmd_list(_: argparse.Namespace) -> int:
    for p in sorted(OUT_DIR.glob("*.yaml")):
        print(p)
    return 0


def cmd_parse(args: argparse.Namespace) -> int:
    obj = parse_yaml_subset(Path(args.file).read_text(), origin=args.file)
    print(json.dumps(obj, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("compile")
    sub.add_parser("list")
    p = sub.add_parser("parse")
    p.add_argument("file")
    args = ap.parse_args()
    if args.cmd == "parse":
        return cmd_parse(args)
    return {"compile": cmd_compile, "list": cmd_list, None: cmd_compile}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
