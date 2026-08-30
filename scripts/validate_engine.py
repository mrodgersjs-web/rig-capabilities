#!/usr/bin/env python3
"""Validate compiled harness specs with the rig-goal-engine itself.

MUST run under the engine env (pyyaml + pydantic available):
  cd ~/rig-goal-engine && uv run --no-sync python \
      ~/Developer/rig-capabilities/scripts/validate_engine.py
  # or: ~/rig-goal-engine/.venv/bin/python <this file>

Phases:
  1 fidelity  — stdlib parser output == yaml.safe_load output, per source
                harness YAML (all 56)
  2 load      — yaml_loader.load_all_specs(out/harness-goalspecs) returns
                56 GoalSpecs, ids round-trip via GoalSpec.model_validate
  3 pilot     — hA-01 no-LLM checks: engine loader get_spec-equivalent,
                Coordinate.parse of anchor, spec.gates -> GateCheck model
                resolution (no command execution, no LLM, no state writes)
"""

import importlib.util
import json
import sys
from pathlib import Path

ENGINE_DIR = Path.home() / "rig-goal-engine"
HUB = Path.home() / "Developer" / "rig-capabilities"
SRC_DIR = HUB / "capabilities" / "harnesses"
OUT_DIR = HUB / "out" / "harness-goalspecs"

sys.path.insert(0, str(ENGINE_DIR))
spec_mod = importlib.util.spec_from_file_location(
    "compile_harnesses", HUB / "scripts" / "compile_harnesses.py")
ch = importlib.util.module_from_spec(spec_mod)
spec_mod.loader.exec_module(ch)

import yaml  # noqa: E402  (engine env)
from models import Coordinate, GateCheck, GateStatus, GoalSpec  # noqa: E402
import yaml_loader  # noqa: E402
from models import BMSMode  # noqa: E402

rc = 0

# ── Phase 1: parser fidelity vs PyYAML ──────────────────────────────────
print("== Phase 1: stdlib-parser fidelity (parse_yaml_subset vs yaml.safe_load) ==")
n_fid = 0
fids = []
for src in sorted(SRC_DIR.glob("*.yaml")):
    mine = ch.parse_yaml_subset(src.read_text(), origin=src.name)
    theirs = yaml.safe_load(src.read_text())
    if mine == theirs:
        n_fid += 1
    else:
        fids.append(src.name)
        rc = 1
print(f"fidelity: {n_fid}/56 exact structural matches")
for name in fids:
    print(f"  MISMATCH {name}")

# ── Phase 2: engine loader roundtrip on compiled specs ──────────────────
print("\n== Phase 2: engine loader load_all_specs(out/harness-goalspecs) ==")
specs = yaml_loader.load_all_specs(OUT_DIR)
print(f"loaded GoalSpecs: {len(specs)}/56")
if len(specs) != 56:
    rc = 1
seen = set()
for s in specs:
    GoalSpec.model_validate(s.model_dump())  # raises on invalid
    seen.add(s.id)
n_yaml = len(list(OUT_DIR.glob("*.yaml")))
print(f"yaml files in out dir: {n_yaml}; unique spec ids: {len(seen)}")
if n_yaml != 56 or len(seen) != 56:
    rc = 1
# every source harness represented
want = {"GL-" + p.stem.upper() for p in SRC_DIR.glob("*.yaml")}
missing = want - seen
if missing:
    rc = 1
print(f"ids cover all 56 sources: {not missing}" + (f" missing={sorted(missing)}" if missing else ""))
# GateCheck model accepts gate payloads the way the engine consumes them
total_gatechecks = 0
for s in specs:
    for g in s.gates:
        gc = GateCheck(name=g.get("name", "?"), description=g.get("description", ""),
                       command=g.get("command"))
        assert gc.status == GateStatus.PENDING
        total_gatechecks += 1
print(f"GateCheck models constructed from compiled gates: {total_gatechecks}")
# anchor coordinates parse with the engine's own parser
for s in specs:
    Coordinate.parse(s.coordinate)
print(f"Coordinate.parse accepted all {len(specs)} anchors (models.py:79-88)")
# loader must not print warnings — load_all_specs prints on failure only
print("loader emitted no 'Failed to load' warnings" if rc == 0 else "see failures above")

# ── Phase 3: pilot hA-01 (no LLM) ───────────────────────────────────────
print("\n== Phase 3: pilot hA-01 (validation + gate resolution, no LLM) ==")
goal_id = "GL-HA-01-CODE-REVIEW"
spec = yaml_loader.get_spec(goal_id)  # engine's own get_spec, default dir is empty on this box
if spec is None:
    # get_spec defaults to ~/.hermes/skills/goal-loop/yaml-specs; point it at compiled dir
    yaml_loader.YAML_SPECS_DIR = OUT_DIR
    spec = yaml_loader.get_spec(goal_id)
assert spec is not None, f"{goal_id} not loadable via engine get_spec"
print(f"get_spec OK: id={spec.id} family={spec.family.value} group={spec.group} bms={spec.bms_mode.value}")
coord = Coordinate.parse(spec.coordinate)
print(f"coordinate: {coord} (level={coord.level} diamond={coord.diamond.value} bms={coord.bms_mode.value} step={coord.step})")
assert BMSMode(spec.bms_mode) in (BMSMode.A1, BMSMode.A2, BMSMode.A3, BMSMode.A4)
blocking = [g for g in spec.gates if g.get("required")]
weighted = [g for g in spec.gates if not g.get("required")]
with_cmd = [g for g in spec.gates if g.get("command")]
checks = [GateCheck(name=g["name"], description=g["description"], command=g["command"]) for g in spec.gates]
print(f"gates resolved: {len(checks)} total | blocking(halt/stop)={len(blocking)} "
      f"weighted(degrade)={len(weighted)} | check-command captured for {len(with_cmd)}")
tiers = {}
for g in spec.gates:
    tiers[g["failure_tier"]] = tiers.get(g["failure_tier"], 0) + 1
print(f"tier distribution: {tiers}")
assert spec.approval_required is True, "hA-01 has stop gate 2.1 -> approval_required must be True"
print(f"approval_required={spec.approval_required} (stop gate 2.1 present)")
print(f"quality_criteria -> engine declarative gate emission (engine.py:403): {len(spec.quality_criteria)} gates")
print(f"success_conditions={len(spec.success_conditions)} failure_states={len(spec.failure_states)}")
print("pilot executed NO commands, NO LLM calls, NO engine state writes. By construction:")
print("  - it imports only models.py + yaml_loader.py (neither imports PydanticAI);")
print("    engine.py — the only LLM surface (get_loop_agent, engine.py:43-68) — is NOT imported")
print("  - no subprocess/execute call anywhere in this script")
print("  - engine.execute() additionally writes memory layers + Obsidian sync and resolves")
print("    specs only from the default ~/.hermes dir — intentionally not invoked")
print(f"note: GoalSpec.failure_states reads empty post-load because the engine loader itself")
print(f"      does not forward the failure_states key (yaml_loader.py:56-78); the compiled")
print(f"      files retain it for any consumer that does.")
print("\nRESULT:", "ALL PHASES GREEN" if rc == 0 else "FAILURES PRESENT")
sys.exit(rc)
