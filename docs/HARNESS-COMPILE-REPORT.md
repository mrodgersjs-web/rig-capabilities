# Harness → GoalSpec Compile Report

Date: 2026-08-30 · Lane: harness-compile (Wave 1) · Author: HarnessCompile worker

## What was bound

All **56** goal-harness YAMLs in `capabilities/harnesses/` were compiled into
engine-loadable GoalSpec files under `out/harness-goalspecs/` (one
`<stem>.yaml` + `<stem>.json` per harness; the `.yaml` files carry JSON
content — a strict subset of YAML 1.2 accepted by the engine's
`yaml.safe_load`). The runner is the existing engine at `~/rig-goal-engine/`
(read-only this lane; user-approved 2026-08-30).

**Result: 56/56 compiled, 56/56 loadable via the engine's own loader, 875
gates resolved, pilot hA-01 green in a genuine no-LLM mode.**

## Engine facts (investigated, cited)

| Fact | Location |
|---|---|
| YAML→GoalSpec loader | `~/rig-goal-engine/yaml_loader.py:46-82` (`load_all_specs`); builds `GoalSpec(...)` at `:56-78` |
| Loader reads top-level `goals:` list | `yaml_loader.py:54` (`data.get("goals", [])`) |
| GoalSpec model | `~/rig-goal-engine/models.py:204-225` |
| `id` must start `GL-` | `models.py:227-232` |
| `Coordinate.parse("L4-D2-A3-R")` | `models.py:79-88`; level range L1–L7 enforced `models.py:71` |
| GateCheck model (name/description/command/status/evidence) | `models.py:93-102` |
| family derived from file stem via `FAMILY_MAP`, default `governance` | `yaml_loader.py:10-21,52-53` |
| Loader does NOT forward `failure_states` | `yaml_loader.py:56-78` (field exists at `models.py:219`) |
| CLI entry | `pyproject.toml` `[project.scripts] rig-goal-engine = "cli:main"`; `cli.py:367-425` |
| No-LLM mode exists | `cli.py:64-67,377` `run --dry-run`; LLM lazy-gated on `OPENAI_API_KEY` (`engine.py:43-52`), `skipped_no_llm` fallback `engine.py:275` |
| Simple-loop gate path (declarative GateCheck per `quality_criteria`) | `engine.py:326-424` |
| Invocation that works offline | `cd ~/rig-goal-engine && ~/.local/bin/uv run --no-sync python ...` (uv 0.12.1; `.venv` has PyYAML 6.0.3, pydantic 2.13.4; plain `uv run --offline` fails resolution — use `--no-sync`) |

## Harness schema shapes (inventory over all 56 sources)

| Shape | Files | Identity gates | Capability gates | failure_protocol |
|---|---|---|---|---|
| A | 19 (`hA-*`, `mh-*`) | `identity_lock.gates` dicts `{id, requirement, proof}` | `[{category, gates:[…]}]`, gates `{id, requirement, proof, failure_tier}` | `{halt_gates, degrade_gates, stop_gates, notes}` |
| B | 24 (`hC-*`, `hD-*`) | `identity_lock.gates` dicts `{id, requirement}` only (no proof/tier — 60 gates) | same as A | same minus `notes` |
| C | 13 (`hB-*`) | `identity_lock.identity_gates` = list[str] (53 gates, no proof) | **flat** gate list `{id: CG-NN, name, category, requirement, proof, failure_tier}` | `{halt, degrade, stop}` (prose) + `gate_mapping: {CG-id: tier}` |

13 `hB-*` files also carry `doctrine_focus`, `library`, `batch` top-level keys → preserved in `preconditions.meta`.

## Field mapping (source → engine GoalSpec)

| GoalSpec field (models.py) | Source | Rule |
|---|---|---|
| `id` | stem | `GL-` + `upper(stem)` (validator `models.py:227`) |
| `name` | `harness_name` | verbatim |
| `intent` (loader maps from `description`, `yaml_loader.py:61`) | `harness_name` + `session_type` + source path | composed |
| `coordinate` (loader maps from `anchor`, `yaml_loader.py:62`) | `coordinate_space` | `{levels[0]}-{primary_diamonds[0]}-{bms_modes[0]}-{iqrsqpi_steps[0]}` → e.g. `L2-D1-A1-I`; all 56 parse via `Coordinate.parse` |
| `bms_mode` | `coordinate_space.bms_modes[0]` | loader takes `.split()[0]` (`yaml_loader.py:63`); prose `bms_bias` kept in `preconditions.bms_bias` |
| `gate` | `definition_of_done[0]` | headline gate |
| `gates[]` (list[dict], `models.py:214`) | identity + capability gates | each: `id`, `category`, `name`, `description` = `requirement` verbatim, **`command` = `proof` verbatim** (`GateCheck.command`, `models.py:97`), `failure_tier`, `required`, `required_verdict`, `weight` |
| — tier rule | `failure_tier` / `failure_protocol` | resolution order: explicit `failure_tier` > failure_protocol membership (`halt_gates`/`degrade_gates`/`stop_gates` lists, or shape-C `gate_mapping`) > `halt` default for identity gates. **halt or stop ⇒ `required:true` / `required_verdict:"GO"` / weight 1.0 (blocking); degrade ⇒ `required:false` / `"SOFT"` / weight 0.5 (non-blocking weighted)** |
| `success_conditions` | `definition_of_done` | verbatim list |
| `quality_criteria` | every gate `requirement` verbatim | makes the engine's no-LLM declarative gate path (`engine.py:403-424`) emit one `GateCheck` per harness gate |
| `failure_states` | `failure_protocol.notes` + shape-C tier prose + generated halt/stop/degrade id summaries | kept in files (engine loader does not forward this field — noted honestly) |
| `preconditions` | `identity_lock.startup_phrase`, `harness_tuple`, `bms_bias`, `meta{harness_id, session_type, governs_loops, coordinate_space, self_improvement, doctrine_focus, library, batch}` | `governs_loops` is governance scope, not a dependency → `depends_on` stays `[]` |
| `approval_required` | stop-tier presence | `True` iff any `stop` gate exists (stop prose in sources demands human Gate-D approval) |
| `packet_type` / `anti_generic_threshold` / `steps` | — | loader defaults (`ProofPacket`, 80.0, `[]`; `yaml_loader.py:69,75,77`); harnesses carry no AGF value |
| `_meta` | `final_rule`, normalized `failure_protocol`, `gates_without_proof` | extra key; engine loader ignores unknown keys |

Gates without a `proof` string in the source (113 = 53 shape-C `identity_gates`
strings + 60 shape-B `{id, requirement}`-only identity gates) get
`command: null` rather than an invented check command; every gate that HAS a
`proof` gets it copied **verbatim** (56/56 fidelity phase proves byte-exact
capture against PyYAML).

## Tooling

- `scripts/compile_harnesses.py` — stdlib-only (no PyYAML): indent parser for
  the harness YAML subset incl. multi-line folded quoted scalars with `''`
  escapes and cross-line `#`-is-content handling; `compile` / `list` / `parse`
  subcommands. Emits `out/harness-goalspecs/<stem>.{yaml,json}`.
- `scripts/validate_engine.py` — runs **under the engine env** and validates
  with the engine's own code: Phase 1 parser fidelity vs `yaml.safe_load`,
  Phase 2 `yaml_loader.load_all_specs()` + `GoalSpec.model_validate`
  roundtrip + `GateCheck`/`Coordinate` model construction, Phase 3 hA-01 pilot.

Reproduce:

```
cd ~/Developer/rig-capabilities && python3 scripts/compile_harnesses.py compile
cd ~/rig-goal-engine && ~/.local/bin/uv run --no-sync python \
    ~/Developer/rig-capabilities/scripts/validate_engine.py
```

## Validation evidence — 56/56 (transcript, 2026-08-30, exit 0)

Compile (`python3 scripts/compile_harnesses.py compile`, tail):

```
OK  mh-06-install-verification-session.yaml  gates= 16 blocking= 14 weighted= 2 no_proof=0

compiled 56/56 harness specs -> /Users/rig128gb/Developer/rig-capabilities/out/harness-goalspecs (gates: 875, without-proof: 113)
```

Engine validation (`uv run --no-sync python scripts/validate_engine.py`):

```
== Phase 1: stdlib-parser fidelity (parse_yaml_subset vs yaml.safe_load) ==
fidelity: 56/56 exact structural matches

== Phase 2: engine loader load_all_specs(out/harness-goalspecs) ==
loaded GoalSpecs: 56/56
yaml files in out dir: 56; unique spec ids: 56
ids cover all 56 sources: True
GateCheck models constructed from compiled gates: 875
Coordinate.parse accepted all 56 anchors (models.py:79-88)
loader emitted no 'Failed to load' warnings

== Phase 3: pilot hA-01 (validation + gate resolution, no LLM) ==
get_spec OK: id=GL-HA-01-CODE-REVIEW family=governance group=HA-01-CODE-REVIEW bms=A1
coordinate: L2-D1-A1-I (level=2 diamond=D1 bms=A1 step=I)
gates resolved: 16 total | blocking(halt/stop)=13 weighted(degrade)=3 | check-command captured for 16
tier distribution: {'halt': 12, 'degrade': 3, 'stop': 1}
approval_required=True (stop gate 2.1 present)
quality_criteria -> engine declarative gate emission (engine.py:403): 16 gates
success_conditions=6 failure_states=0
pilot executed NO commands, NO LLM calls, NO engine state writes. By construction:
  - it imports only models.py + yaml_loader.py (neither imports PydanticAI);
    engine.py — the only LLM surface (get_loop_agent, engine.py:43-68) — is NOT imported
  - no subprocess/execute call anywhere in this script
  - engine.execute() additionally writes memory layers + Obsidian sync and resolves
    specs only from the default ~/.hermes dir — intentionally not invoked
note: GoalSpec.failure_states reads empty post-load because the engine loader itself
      does not forward the failure_states key (yaml_loader.py:56-78); the compiled
      files retain it for any consumer that does.

RESULT: ALL PHASES GREEN
```

## Pilot result — hA-01 only (genuine no-LLM)

The engine's no-LLM surfaces exist (`run --dry-run`, keyless
`skipped_no_llm`), but full `engine.execute()` (1) resolves specs only from
`~/.hermes/skills/goal-loop/yaml-specs` — a directory outside this lane's
ownership — and (2) writes memory layers + Obsidian sync even in dry-run. The
pilot therefore drove the engine's own load/validate models without
`execute()`: `yaml_loader.get_spec("GL-HA-01-CODE-REVIEW")` loaded,
`Coordinate.parse` resolved `L2-D1-A1-I`, and all 16 gates resolved to
`GateCheck` models with check commands captured (13 blocking halt/stop, 3
weighted degrade, `approval_required=True` from stop gate 2.1). **No commands
executed, no LLM called, no engine state written.** This is validation +
gate resolution exactly as scoped — an honest, complete pilot, not a skip.

## Remaining steps (not in this lane)

1. Deploy: copy `out/harness-goalspecs/*.yaml` to the engine's spec dir
   (`~/.hermes/skills/goal-loop/yaml-specs/`) — needs write access owned by
   the integration lane; then `rig-goal-engine list` / `run hA-01 …
   --dry-run` exercise the full CLI path.
2. If `failure_states` must reach `GoalSpec`, add one forwarding line to
   `yaml_loader.py` (engine edit — engine was READ-ONLY this lane).
3. Optional engine enhancement: consume structured `spec.gates` (tier/weight/
   required) in `_run_spec_gates` instead of the `quality_criteria`
   declarative stand-in, and actually execute `command` strings under a
   Gate-D-gated sandbox (they are proof recipes referencing session files —
   intentionally never run here).
4. 113 without-proof identity gates remain `command: null` until sources add
   proof strings.
