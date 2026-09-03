# rig-lattice-system

Coordinate the work before you build it.

```
588 cells      7 levels x 3 diamonds x 4 BMS modes x 7 IQRSQPI steps
 84 primaries  level x diamond x mode
 28 archetypes mode x step
 40 engines    20 cognitive / 10 nature / 10 physics (all 10 physics are gates)
```

One stdlib-only Python package, one CLI. `SKILL.md` is the agent-facing
contract; `PROVENANCE.md` records every source and every deliberate change.

## Quick start

```bash
./bin/rig-lattice doctor                 # is this install intact?
./bin/rig-lattice lattice summary        # the geometry, as numbers
./bin/rig-lattice route "migrate the billing schema"
./bin/rig-lattice audit draft.md
./bin/rig-lattice idea score --title "..." --content "..." --sources 3
python3 tests/run_all.py                 # 403 tests
```

Add `--json` to any subcommand.

## The doctrine in one paragraph

The X-axis is Level/Altitude (L1 mechanical → L7 doctrine). The Y-axis is the
Triple Diamond (D1 Physical, D2 Cognitive, D3 Nature). The **Z-axis is BMS
confidence** (A1 PYTHON_ONLY ≥ 0.75, A2 HYBRID 0.45–0.74, A3 AGENT_BOUNDED
0.25–0.44, A4 LLM_AGENT_FREE < 0.25). IQRSQPI is the seven-step process that
runs *inside* a coordinate — Intent, Question, Research, Solution, Quality,
Proof, Integrate — not an axis of it. A1 is the goal: no model in the decision
path. Escalation is earned by a recorded failure, never chosen for comfort.

## BMS

```
raw   = failure_cost*0.4 + reversibility*0.3 + mechanism_clarity*0.3
final = clamp(raw - past_failure_rate*0.2
                  + (data_volume - 0.5)*0.1
                  + ALTITUDE_BONUS[level], 0.0, 1.0)
mode  = A1 if final >= 0.75 else A2 if >= 0.45 else A3 if >= 0.25 else A4
```

| mode | name | budget | approval | deterministic |
|---|---|---|---|---|
| A1 | PYTHON_ONLY | $0.00 | conditional | yes |
| A2 | HYBRID | $0.10 | conditional | no |
| A3 | AGENT_BOUNDED | $0.50 | **mandatory** | no |
| A4 | LLM_AGENT_FREE | $0.00 | **mandatory** | no (model-free decision, human gate) |

A3 has no runtime in this bundle: `archetype_runner("A3")` raises rather than
running the A1 path and calling the result A3.

## Cell ids

Canonical `L{1-7}-D{1-3}-A{1-4}-{I1|Q1|R|S|Q2|P|I2}`. Two legacy dialects are
accepted and normalized; the pre-Z-axis shape is rejected.

```
L3-D2-A2-R                        canonical
L3-2-A2-R                         bare-digit diamond  -> L3-D2-A2-R
intent.D1_physical.A1.intent      dotted              -> L1-D1-A1-I1
L2-D1-Intent                      REJECTED (no BMS mode)
```

Cell contract files keep the bare-digit filename (`L1-1-A1-I1.yaml`);
`load_cell` maps canonical → filename.

## Layout

```
bin/rig-lattice           the CLI shim (resolves the skill dir from its own path)
rig_lattice/
  _paths.py               PKG_ROOT, CRITERIA_DIR, CELLS_DIR, RUNS_DIR
  lattice/                constants (source of truth), resolver, bms,
                          generator, schema, validator, wire, cells/ (588)
  core/                   registry (40 engines), robust_mad_z, rig_l, bdf
  engines/                cognitive (20) / nature (10) / physics (10)
  criteria/               44 YAML packs + compiled JSON twins
  deviator/               auditor, dv, des_squared, des2_innerloop,
                          pipeline/, hooks/, reports/
  system/                 levels, archetypes, orchestrator, persistence
  enterprise/             iqrsqpi runner, database, cost_ledger, security, ...
  archetypes/             a1_python_only (implemented), a2_hybrid, a3/a4 stubs
  idea/                   booster (V3.1), mapelites, asr, innovation, bridge
  engine_aliases.py       codename -> engine id (GENERATED)
scripts/                  compile_criteria.py, gen_engine_aliases.py
tests/                    run_all.py + 12 suites
runs/                     all runtime output
```

## Compile step

YAML is the human source of truth; JSON is what the runtime reads. PyYAML is a
**compile-time** dependency only — the audit path never needs it.

```bash
python3 scripts/compile_criteria.py          # 44 packs + calibration + 588 cells
python3 scripts/compile_criteria.py --check   # verify in sync
python3 scripts/gen_engine_aliases.py --check # verify the alias table
```

## Tests

```bash
python3 tests/run_all.py            # 403 tests, ~160 s
python3 tests/run_all.py --fast     # 88 tests, ~2 s (the done_when subset)
```

The runner collects both `unittest.TestCase` classes and the vendored
pytest-style `def test_*()` functions, under stdlib unittest only.

## Environment

| variable | default | meaning |
|---|---|---|
| `RIG_LATTICE_LLM_URL` | `http://127.0.0.1:11434/v1/chat/completions` | only the opt-in `--llm` audit path |
| `RIG_LATTICE_LLM_MODEL` | `llama3.3:70b` | model id |
| `RIG_LATTICE_RUNS_DIR` | `<skill>/runs` | runtime output sink |
| `RIG_DV_OFFLINE` | `0` | `1` = no outbound model call |
| `RIG_DV_AUTO_APPROVE` | `0` | `1` = auto-approving stub (tests only) |

## Related assets

- `rig-deviation-engines` — the 40-engine roster and σ ladder (pointer skill)
- `rig-idea-generator` — V3.1 gates, MAP-Elites, ASR stack (pointer skill)
- `/rig-lattice-system` — the slash command
- `rig-lattice-router` — routing sub-agent, returns the contract only
- `mh-07-lattice-application-session` — the gated application harness
