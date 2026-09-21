"""ULTRA cell contract -- the validator for ARCHITECTURE.md section 2.

A cell is the unit at every level of ULTRA (L0 meta, L1 phase, L2 stage,
L3 tactic, L4 leaf, X studio). It is valid only when all eight slots exist and
its harness declares a red path. This module decides that with code, so a
directory that merely looks like a cell cannot be counted as one.

Slots (identical at every level):
    SKILL.md      what it does, when to use, outcome, done_when, quality_floor
    agent.md      identity, model ladder (local-first + fallback), autonomy tier
    harness.yaml  inputs, outputs, gates (code + jev gate id), red_path,
                  effort_budget (usd, wallclock_seconds, mike_decisions),
                  kill_criteria
    loop.yaml     entry, body, exit_gate, max_iterations, park, close
    hooks/        exit-code scripts; a `stop` hook that refuses completion
    context/      hydrate.yaml naming what the cell needs before it runs
    prompts/      copy-ready leaves
    routes.yaml   when <cond> -> call <child cell>; children or studios only

Refusals are named, never averaged: a cell with seven slots is invalid, and a
cell whose routes name a sibling is invalid, because the routing rule (a cell
may call only its declared children and the studios) is what makes the process
auditable. Findings carry a code so a test can assert on the reason.

Nothing here calls a provider. Validation is deterministic.
"""
from __future__ import annotations

import hashlib
import os
import re
import stat
import subprocess
import tempfile
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - the repo pins pyyaml; be honest if absent
    yaml = None

SLOTS = ("SKILL.md", "agent.md", "harness.yaml", "loop.yaml",
         "hooks", "context", "prompts", "routes.yaml")
DIR_SLOTS = ("hooks", "context", "prompts")
LEVELS = ("L0", "L1", "L2", "L3", "L4", "X")
AUTONOMY_TIERS = (0, 1, 2)
BUDGET_KEYS = ("usd", "wallclock_seconds", "mike_decisions")
LOOP_KEYS = ("entry", "body", "exit_gate", "max_iterations", "park", "close")
STUDIO_PREFIX = "studio:"


class CellError(RuntimeError):
    pass


def _load_yaml(path: Path):
    if yaml is None:
        raise CellError("pyyaml is not importable; cannot validate yaml slots")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # malformed yaml is a finding, not a crash
        return None, f"{path.name}: yaml parse error: {str(exc).splitlines()[0]}"
    return data, None


def _frontmatter(path: Path):
    """Return (dict, error) for a markdown file's YAML frontmatter."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, f"{path.name}: missing YAML frontmatter"
    if yaml is None:
        raise CellError("pyyaml is not importable")
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except Exception as exc:
        return None, f"{path.name}: frontmatter parse error: {str(exc).splitlines()[0]}"
    return data, None


def declared_gate_ids():
    """Gate ids the router actually declares. Read live, never remembered."""
    try:
        from rig_capabilities.ultra_gates import GATES  # local import: optional coupling
        return set(GATES.keys())
    except Exception:
        return set()


def _finding(code, msg):
    return {"code": code, "msg": msg}


def validate_cell(path, root=None, known_gates=None):
    """Validate one cell directory. Returns a dict; `ok` is the only verdict."""
    path = Path(path).resolve()
    root = Path(root).resolve() if root else path
    findings = []
    known_gates = declared_gate_ids() if known_gates is None else set(known_gates)

    if not path.is_dir():
        return {"cell": str(path), "ok": False, "level": None,
                "findings": [_finding("not_a_dir", f"{path} is not a directory")]}

    # 1. all eight slots exist; directory slots must be non-empty
    missing = [s for s in SLOTS if not (path / s).exists()]
    for s in missing:
        findings.append(_finding("slot_missing", f"missing slot {s}"))
    for s in DIR_SLOTS:
        d = path / s
        if d.is_dir() and not any(p.is_file() for p in d.rglob("*")):
            findings.append(_finding("slot_empty", f"{s}/ has no files"))

    level = None
    children_declared = []
    # 2. SKILL.md frontmatter carries the quality contract
    if (path / "SKILL.md").exists():
        fm, err = _frontmatter(path / "SKILL.md")
        if err:
            findings.append(_finding("skill_frontmatter", err))
        else:
            for k in ("name", "outcome", "done_when", "quality_floor"):
                if k not in fm:
                    findings.append(_finding("skill_field_missing", f"SKILL.md frontmatter lacks `{k}`"))
            if isinstance(fm.get("done_when"), list) and not fm["done_when"]:
                findings.append(_finding("skill_done_when_empty", "done_when is an empty list"))

    # 3. agent.md: model ladder (>=2, first local), autonomy tier, verifier constraint
    if (path / "agent.md").exists():
        fm, err = _frontmatter(path / "agent.md")
        if err:
            findings.append(_finding("agent_frontmatter", err))
        else:
            ladder = fm.get("model_ladder")
            if not isinstance(ladder, list) or len(ladder) < 2:
                findings.append(_finding("agent_ladder", "model_ladder must list >=2 routes (local-first + fallback)"))
            else:
                first = ladder[0] if isinstance(ladder[0], str) else str((ladder[0] or {}).get("route", ""))
                if not first.startswith("local/"):
                    findings.append(_finding("agent_ladder_not_local_first",
                                             f"first ladder route is `{first}`; policy is local-first"))
            tier = fm.get("autonomy_tier")
            if tier not in AUTONOMY_TIERS:
                findings.append(_finding("agent_autonomy_tier", f"autonomy_tier must be one of {AUTONOMY_TIERS}, got {tier!r}"))
            if fm.get("verifier_family_differs") is not True:
                findings.append(_finding("agent_verifier_family", "agent.md must set verifier_family_differs: true (maker is not grader)"))

    # 4. harness.yaml: gates, red path, effort budget with mike_decisions, kill criteria
    if (path / "harness.yaml").exists():
        h, err = _load_yaml(path / "harness.yaml")
        if err:
            findings.append(_finding("harness_yaml", err))
        elif not isinstance(h, dict):
            findings.append(_finding("harness_yaml", "harness.yaml is not a mapping"))
        else:
            level = h.get("level")
            if level not in LEVELS:
                findings.append(_finding("harness_level", f"level must be one of {LEVELS}, got {level!r}"))
            gates = h.get("gates")
            if not isinstance(gates, list) or not gates:
                findings.append(_finding("harness_gates", "gates must be a non-empty list"))
            else:
                for i, g in enumerate(gates):
                    if not isinstance(g, dict):
                        findings.append(_finding("harness_gate_shape", f"gates[{i}] is not a mapping"))
                        continue
                    if not g.get("code"):
                        findings.append(_finding("harness_gate_code", f"gates[{i}] declares no deterministic `code` check"))
                    jev = g.get("jev")
                    if jev in (None, ""):
                        findings.append(_finding("harness_gate_jev_missing",
                                                 f"gates[{i}] names no `jev` gate id (use `none` with `why`)"))
                    elif jev == "none":
                        if not g.get("why"):
                            findings.append(_finding("harness_gate_jev_none_unjustified",
                                                     f"gates[{i}] sets jev: none without `why`"))
                    elif known_gates and jev not in known_gates:
                        findings.append(_finding("harness_gate_jev_unknown",
                                                 f"gates[{i}] jev `{jev}` is not a declared rig-ultra gate"))
            rp = h.get("red_path")
            if not isinstance(rp, dict) or not rp.get("plant") or not rp.get("expect"):
                findings.append(_finding("harness_red_path", "red_path needs `plant` (what is broken) and `expect` (the red you must see)"))
            eb = h.get("effort_budget")
            if not isinstance(eb, dict):
                findings.append(_finding("harness_budget", "effort_budget missing"))
            else:
                for k in BUDGET_KEYS:
                    v = eb.get(k)
                    if not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0:
                        findings.append(_finding("harness_budget_key", f"effort_budget.{k} must be a non-negative number"))
            kc = h.get("kill_criteria")
            if not isinstance(kc, list) or not kc:
                findings.append(_finding("harness_kill", "kill_criteria must list >=1 condition"))
            for k in ("inputs", "outputs"):
                if not isinstance(h.get(k), list):
                    findings.append(_finding("harness_io", f"{k} must be a list"))

    # 5. loop.yaml: the six loop keys, integer max_iterations
    if (path / "loop.yaml").exists():
        lp, err = _load_yaml(path / "loop.yaml")
        if err:
            findings.append(_finding("loop_yaml", err))
        elif not isinstance(lp, dict):
            findings.append(_finding("loop_yaml", "loop.yaml is not a mapping"))
        else:
            for k in LOOP_KEYS:
                if k not in lp:
                    findings.append(_finding("loop_key_missing", f"loop.yaml lacks `{k}`"))
            mi = lp.get("max_iterations")
            if not isinstance(mi, int) or isinstance(mi, bool) or mi < 1:
                findings.append(_finding("loop_max_iterations", "max_iterations must be an int >= 1"))

    # 6. routes.yaml: children or studios only; every child must exist; no siblings
    if (path / "routes.yaml").exists():
        r, err = _load_yaml(path / "routes.yaml")
        if err:
            findings.append(_finding("routes_yaml", err))
        elif not isinstance(r, dict):
            findings.append(_finding("routes_yaml", "routes.yaml is not a mapping"))
        else:
            children_declared = r.get("children") or []
            if not isinstance(children_declared, list):
                findings.append(_finding("routes_children", "children must be a list"))
                children_declared = []
            routes = r.get("routes")
            if not isinstance(routes, list) or not routes:
                findings.append(_finding("routes_empty", "routes must be a non-empty list"))
                routes = []
            for c in children_declared:
                if not (path / str(c)).resolve().is_dir():
                    findings.append(_finding("routes_child_absent", f"declared child `{c}` does not resolve to a directory"))
            for i, rt in enumerate(routes):
                if not isinstance(rt, dict) or not rt.get("when") or not rt.get("call"):
                    findings.append(_finding("routes_shape", f"routes[{i}] needs `when` and `call`"))
                    continue
                call = str(rt["call"])
                if call.startswith(STUDIO_PREFIX):
                    # studio: targets must resolve to an existing implementation --
                    # the 2026 blind spot was `continue` here plus `studios` in
                    # SKIP_DIRS: every studio: call was trusted unchecked and the
                    # whole subtree was invisible to discovery.
                    name = call[len(STUDIO_PREFIX):].strip("/")
                    base = Path(root) if root is not None else path
                    target = (base / "studios" / name)
                    if not target.is_dir():
                        alt = (path / "studios" / name)
                        target = alt if alt.is_dir() else target
                    if not is_cell_dir(target):
                        findings.append(_finding("studio_target_unresolved",
                                                 f"routes[{i}] calls `{call}` but {os.path.relpath(target, base)} is not a cell-shaped studio"))
                    allowed = r.get("studios_allowed")
                    if isinstance(allowed, list) and call not in [str(a) for a in allowed]:
                        findings.append(_finding("studio_not_allowed",
                                                 f"routes[{i}] calls `{call}` which this cell's studios_allowed does not grant"))
                    continue
                if call in ("self", "parent", "close", "park"):
                    continue
                if call not in [str(c) for c in children_declared]:
                    # a sibling is any non-child; the parent decides siblings
                    findings.append(_finding("routes_sibling_call",
                                             f"routes[{i}] calls `{call}` which is not a declared child or studio"))

    # 7. hooks/: an executable stop hook that refuses when required sections are absent
    hooks = path / "hooks"
    if hooks.is_dir():
        stop = next((p for p in hooks.iterdir() if p.name in ("stop", "stop.sh")), None)
        if stop is None:
            findings.append(_finding("hooks_stop_missing", "hooks/ has no `stop` hook"))
        else:
            if not os.access(stop, os.X_OK):
                findings.append(_finding("hooks_stop_not_executable", f"{stop.name} is not executable"))
            else:
                with tempfile.TemporaryDirectory() as td:
                    try:
                        proc = subprocess.run([str(stop)], cwd=td, capture_output=True, text=True, timeout=10)
                        if proc.returncode == 0:
                            findings.append(_finding("hooks_stop_vacuous",
                                                     "stop hook exited 0 in an empty directory; it refuses nothing"))
                    except Exception as exc:
                        findings.append(_finding("hooks_stop_error", f"stop hook could not run: {exc}"))

    # 8. context/hydrate.yaml names sources
    ctx = path / "context" / "hydrate.yaml"
    if (path / "context").is_dir():
        if not ctx.exists():
            findings.append(_finding("context_hydrate_missing", "context/hydrate.yaml missing"))
        else:
            c, err = _load_yaml(ctx)
            if err:
                findings.append(_finding("context_yaml", err))
            elif not isinstance(c, dict) or not isinstance(c.get("sources"), list) or not c["sources"]:
                findings.append(_finding("context_sources", "hydrate.yaml must list >=1 source"))

    rel = os.path.relpath(path, root) if root != path else "."
    return {"cell": rel, "path": str(path), "level": level, "ok": not findings,
            "children": [str(c) for c in children_declared], "findings": findings}


def is_cell_dir(p: Path) -> bool:
    """A directory claims to be a cell when it has routes.yaml or agent.md or harness.yaml."""
    return p.is_dir() and any((p / s).exists() for s in ("routes.yaml", "agent.md", "harness.yaml"))


# `studios` was removed from this set 2026-09-20 (W01): skipping it made nine
# operational studios invisible -- unrouted studio trees could not be reported
# as orphans, and `26/26 valid` covered a tree that omitted them entirely.
SKIP_DIRS = set(DIR_SLOTS) | {"ui", "node_modules", "tools", "agents", "commands", "__pycache__"}


def discover_cells(root):
    """Walk from root along declared routes only.

    Returns (order, orphans, leaves):
      order   -- cell directories reached from root by routes.yaml `children`
      orphans -- cell-shaped directories under root that no route reaches;
                 a cell nobody routes to is dead weight the graph cannot draw
      leaves  -- declared children that exist but are not cells yet (a bare
                 SKILL.md tactic, for example); reported, never counted as cells
    """
    root = Path(root).resolve()
    seen, order, leaves = set(), [], []

    def declared_children(p):
        r = p / "routes.yaml"
        if not (r.exists() and yaml is not None):
            return []
        try:
            data = yaml.safe_load(r.read_text(encoding="utf-8")) or {}
            kids = [str(c) for c in (data.get("children") or [])]
            for rt in (data.get("routes") or []):
                if isinstance(rt, dict):
                    call = str(rt.get("call", ""))
                    if call.startswith(STUDIO_PREFIX):
                        kids.append("studios/" + call[len(STUDIO_PREFIX):].strip("/"))
            for a in (data.get("studios_allowed") or []):
                if str(a).startswith(STUDIO_PREFIX):
                    kids.append("studios/" + str(a)[len(STUDIO_PREFIX):].strip("/"))
            return kids
        except Exception:
            return []

    def walk(p):
        if p in seen:
            return
        seen.add(p)
        order.append(p)
        for c in declared_children(p):
            cp = (p / c).resolve()
            if not cp.is_dir():
                continue  # validate_cell reports routes_child_absent
            if is_cell_dir(cp):
                walk(cp)
            else:
                leaves.append(os.path.relpath(cp, root))

    walk(root)

    orphans = []
    for dirpath, dirnames, _files in os.walk(root):
        dirnames[:] = [d for d in sorted(dirnames) if d not in SKIP_DIRS and not d.startswith(".")]
        p = Path(dirpath).resolve()
        if p != root and is_cell_dir(p) and p not in seen:
            orphans.append(os.path.relpath(p, root))
    return order, orphans, sorted(set(leaves))


def find_cycles(root):
    """A route edge back to an ancestor is a cycle: the walk terminates (seen-set)
    but the graph is a lie -- report it as a defect instead of quietly surviving."""
    root = Path(root).resolve()
    cycles = []

    def declared_children(p):
        r = p / "routes.yaml"
        if not (r.exists() and yaml is not None):
            return []
        try:
            data = yaml.safe_load(r.read_text(encoding="utf-8")) or {}
            return [str(c) for c in (data.get("children") or [])]
        except Exception:
            return []

    def walk(p, stack):
        sp = str(p)
        if sp in stack:
            cycles.append(" -> ".join(stack[stack.index(sp):] + [sp]))
            return
        for c in declared_children(p):
            cp = (p / c).resolve()
            if cp.is_dir():
                walk(cp, stack + [sp])
    walk(root, [])
    return cycles


def validate_tree(root):
    root = Path(root).resolve()
    gates = declared_gate_ids()
    order, orphans, leaves = discover_cells(root)
    cycles = find_cycles(root)
    cells = [validate_cell(p, root=root, known_gates=gates) for p in order]
    by_level = {}
    for c in cells:
        by_level.setdefault(c["level"] or "?", []).append(c["cell"])
    return {
        "root": str(root),
        "cells": cells,
        "valid": sum(1 for c in cells if c["ok"]),
        "total": len(cells),
        "orphans": orphans,
        "leaves": leaves,
        "by_level": by_level,
        "ok": bool(cells) and all(c["ok"] for c in cells) and not orphans and not cycles,
        "cycles": cycles,
        "declared_gates_seen": bool(gates),
    }


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def plant_failure(cell_path, slot="routes.yaml", root=None):
    """The M1 red path made executable: remove one slot, prove the validator goes
    red, restore byte-identical. Refuses to report a plant whose bytes did not
    move (the vacuous-plant lesson). Never leaves the tree modified.
    root= gives the tree context so cells whose routes call `studio:` targets
    validate green standalone exactly as they do inside validate_tree."""
    cell = Path(cell_path).resolve()
    target = cell / slot
    if not target.is_file():
        return {"ok": False, "reason": f"{slot} is not a file in {cell}"}
    before = validate_cell(cell, root=root)
    sha0 = _sha(target)
    data = target.read_bytes()
    tmp = target.with_suffix(target.suffix + ".planted")
    try:
        target.rename(tmp)
        if target.exists():
            return {"ok": False, "reason": "plant did not move the file"}
        during = validate_cell(cell, root=root)
    finally:
        if tmp.exists():
            tmp.rename(target)
        if not target.exists():
            target.write_bytes(data)
    sha1 = _sha(target)
    went_red = before["ok"] and not during["ok"] and any(
        f["code"] == "slot_missing" and slot in f["msg"] for f in during["findings"])
    return {
        "ok": went_red and sha0 == sha1,
        "cell": str(cell), "slot": slot,
        "green_before": before["ok"], "red_during": not during["ok"],
        "red_findings": [f["msg"] for f in during["findings"]],
        "restored_byte_identical": sha0 == sha1,
        "sha256": sha0,
    }


def tree_lines(report):
    """Render by level for a shell. Deterministic order."""
    out = []
    for lvl in list(LEVELS) + ["?"]:
        ids = report["by_level"].get(lvl)
        if not ids:
            continue
        out.append(f"{lvl}")
        for cid in ids:
            c = next(x for x in report["cells"] if x["cell"] == cid)
            mark = "ok " if c["ok"] else "RED"
            out.append(f"  {mark} {cid}" + (f"  -> {', '.join(c['children'])}" if c["children"] else ""))
            for f in c["findings"]:
                out.append(f"       {f['code']}: {f['msg']}")
    if report["leaves"]:
        out.append(f"leaves (routed to, not yet cells): {len(report['leaves'])}  " + ", ".join(report["leaves"]))
    if report["orphans"]:
        out.append("orphans (cell-shaped, routed by nobody): " + ", ".join(report["orphans"]))
    return out
