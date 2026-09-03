---
name: rig-lattice-system
description: "RIG Lattice System — a 588-cell coordinate lattice (7 levels x 3 diamonds x 4 BMS modes x 7 IQRSQPI steps), 28 archetypes, 40 deviation engines, DES² amplification, and a deterministic idea generator, shipped as one installed stdlib Python package with a single CLI. Use when asked to install or apply the RIG lattice system, route a unit of work to a cell and build mode before building it, score or deviate an artifact through the 40 engines, evaluate an idea against the V3.1 creativity gates, or refactor an application A1-first."
allowed-tools: Bash Read Grep Write Edit
owner: rig-intelligence
domain: Agent engineering / deterministic build doctrine
status: Stable
verified_by: jake
verified_on: 2026-09-02
acl: public
relates_to: iqrsqpi-v10, rig-deviation-engines, rig-idea-generator
outcome: "agent-engineering: work is routed to an explicit lattice cell and BMS mode before it is built, and the artifact is scored by 40 engines with a sealed verdict — never by the agent's own narration"
done_when:
  - file:capabilities/skills/rig-lattice-system/rig_lattice/lattice/constants.py
  - grep:capabilities/skills/rig-lattice-system/rig_lattice/core/registry.py:ENGINE_REGISTRY
  - cmd:python3 capabilities/skills/rig-lattice-system/tests/run_all.py --fast
  - cmd:capabilities/skills/rig-lattice-system/bin/rig-lattice lattice summary --json | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['cells']==588 and d['archetypes']==28 and d['primary']==84 and d['version']=='3.0'"
  - cmd:capabilities/skills/rig-lattice-system/bin/rig-lattice engines --json | python3 -c "import json,sys; e=json.load(sys.stdin); assert len(e)==40; assert sum(1 for x in e if x['layer']=='physics')==10"
  - cmd:capabilities/skills/rig-lattice-system/bin/rig-lattice lattice cell L1-1-A1-I1 --json | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['cell_id']=='L1-D1-A1-I1' and d['archetype']=='A1.1' and d['deterministic'] is True"
  - cmd:capabilities/skills/rig-lattice-system/bin/rig-lattice doctor --json | python3 -c "import json,sys; assert json.load(sys.stdin)['ok'] is True"
great_example: examples/great/agent-engineering/rig-lattice-system.md
quality_floor: 0.7
---

# RIG Lattice System

Coordinate the work before you build it.

```
588 cells      7 levels x 3 diamonds x 4 BMS modes x 7 IQRSQPI steps
 84 primaries  level x diamond x mode
 28 archetypes mode x step
 40 engines    20 cognitive / 10 nature / 10 physics (all 10 physics are gates)
```

IQRSQPI is the process that runs *inside* a coordinate, not an axis of it. The
Z-axis is BMS confidence. An earlier card multiplied 40 engines x 6 audience
tiers x 7 steps = 1,680 cells; that is wrong, and `docs/DOCTRINE.md` records
the correction. Engines are scorers inside a cell.

## activation

Fires when a request contains any of:

- "put in the RIG lattice system", "install the lattice", "apply the lattice"
- "route this to a cell", "what cell is this", "which BMS mode"
- "score this artifact", "audit this with the 40 engines", "deviate this"
- "refactor this A1-first", "build this deterministically"
- "score this idea", "run the creativity gates", "is this idea generic"

## instruction

Route, then score, then build A1-first, then prove. Take the unit of work and
resolve it to one canonical cell id with `rig-lattice route`, which yields the
level, diamond, BMS mode, archetype, and per-mission budget; record that cell
id and the `BMSResult` that produced it **before** editing a file. Build inside
the A1 band — deterministic code, no model in the decision path — and escalate
to A2/A3/A4 only after a recorded A1 failure with the failing command's output.
When the artifact exists, score it with `rig-lattice audit`: no `HARD_BLOCK`
from the 10 physics gates, and every engine below threshold carries either a
patch or a named reason. Close with a ProofPacket: commands, exit codes,
artifact sha256.

## applies_when

```yaml
env: any POSIX shell; no network required for the A1 path
runtime: python3 >= 3.11
deps: stdlib only (PyYAML optional, compile-time only for scripts/compile_criteria.py)
params:
  cell_id: canonical L{1-7}-D{1-3}-A{1-4}-{I1|Q1|R|S|Q2|P|I2}, or the
    bare-digit (L1-1-A1-I1) or dotted (intent.D1_physical.A1.intent) dialect
  confidence: 0.0-1.0, or the BMS criteria triple (failure_cost,
    reversibility, mechanism_clarity) plus level
budget:
  A1: $0.00   # no model in the decision path
  A2: $0.10
  A3: $0.50
  A4: $0.00   # human gate, not a model call
scale: 588 cells resolved in-process; the 40-engine audit is O(packs) and
  runs in seconds on a single artifact
```

## permissions

Bash Read Grep Write Edit

## flow

1. **Coordinate.** `rig-lattice route "<task>" --step I1` → cell id, mode,
   archetype, budget. Or resolve a known id: `rig-lattice lattice cell <id>`.
2. **Score the confidence.** `rig-lattice bms score --failure-cost F
   --reversibility R --mechanism-clarity M --level L3` → the `BMSResult` that
   justifies the mode. Record both lines before the first edit.
3. **Build A1-first.** Implement inside the deterministic band. No model in the
   decision path. A1 that cannot decide returns UNKNOWN and escalates; it never
   guesses.
4. **Escalate only on evidence.** A2/A3/A4 require the failing A1 command and
   its exit code in the log. A3 needs an agent runtime this bundle does not
   ship and raises `NotImplementedError`; A4 is a mandatory human gate.
5. **Audit the artifact.** `rig-lattice audit <path>` → per-engine σ, RIG-L,
   BDF, gate verdict. Zero `HARD_BLOCK` from the physics layer.
6. **Amplify or deviate if short.** `rig-lattice des2 <path>` for the five
   rigor amplifiers; `rig-lattice deviate <path> --sigma 20` for the patch
   pipeline (`RIG_DV_OFFLINE=1` keeps it deterministic and offline).
7. **Seal.** ProofPacket with the command list, exit codes, and artifact
   sha256. `rig-lattice doctor` proves the installed copy is intact.

## done_when

- `rig-lattice lattice summary --json` reports 588 cells / 84 primaries /
  28 archetypes / version 3.0
- `rig-lattice engines --json` reports 40 engines, 10 of them physics gates
- `tests/run_all.py` prints `RESULT: n/n passed` and exits 0
- `rig-lattice doctor --json` reports `ok: true`
- the session log carries a canonical cell id and its `BMSResult` recorded
  before the first file edit

## out_of_scope

- **The LinkedIn content chaos pipeline.** `alfred/deviation_pipeline.py` in
  rig-linkedin-studio-luca is a *consumer* of engine codenames, not an engine
  implementation. It stays in the GTM repo; this bundle ships only the
  codename→engine-id alias table it needs (`rig_lattice/engine_aliases.py`).
- **An A3 agent runtime.** A3 needs a bounded state machine with tool and cost
  budgets. This bundle is stdlib-only and does not carry one, so
  `archetype_runner("A3")` raises rather than silently running the A1 path and
  reporting an A3 result.
- **The private `rig-creative-booster` package.** Both known owners 404. The
  deterministic V3.1 core was rebuilt from the build card and is the offline
  default; the optional import path stays so a recovered clone wins
  automatically.
- **Writing outside `runs/`.** All runtime output goes to `runs/`, overridable
  with `RIG_LATTICE_RUNS_DIR`. Nothing writes to `$HOME/Desktop`.
- **Outward actions without approval.** The approval client refuses by default
  (`RIG_DV_AUTO_APPROVE` unset → `(False, "approval_required_no_client")`).

## CLI

| command | behavior |
|---|---|
| `lattice summary` | the geometry as numbers |
| `lattice cell <id>` | parse + resolve + dump the vendored cell contract |
| `lattice cells` | all 588 canonical ids |
| `bms score --failure-cost F --reversibility R --mechanism-clarity M [--past-failure-rate --data-volume --level L3]` | `BMSResult` |
| `route <intent> [--step I1] [--domain d]` | cell id + mode + archetype + budget |
| `audit <path\|-> [--engines ...] [--llm]` | 40-engine audit: σ, status, RIG-L, BDF |
| `deviate <path\|-> [--sigma 20]` | dv pipeline (`RIG_DV_OFFLINE=1` for offline) |
| `des2 <path>` | DES² amplification report |
| `idea score --title T --content C [--sources n --claims n --mechanisms n --corpus PATH]` | booster score + 4 gates + verdict |
| `idea grid --candidates FILE --seed N` | 25-niche MAP-Elites menu |
| `run <path> --confidence C [--force-a4]` | full L1→L7 orchestration |
| `engines` | the 40-engine roster |
| `doctor` | imports, counts, compile freshness, env |

Every subcommand accepts `--json`.

## Layout

```
rig_lattice/
  lattice/      constants (single source of truth), resolver, bms, generator,
                schema, validator, wire, cells/ (588 contracts)
  core/         registry (40 engines), robust_mad_z, rig_l, bdf, sigma
  engines/      cognitive (20) / nature (10) / physics (10)
  criteria/     44 YAML packs + their compiled JSON twins
  deviator/     auditor, dv, des_squared, des2_innerloop, pipeline, hooks
  system/       levels, archetypes, orchestrator (run_system), persistence
  enterprise/   iqrsqpi runner, database, cost_ledger, security, notify, ...
  archetypes/   a1_python_only (implemented), a2_hybrid, a3/a4 (contracts)
  idea/         booster (V3.1), mapelites, asr, innovation, bridge
scripts/        compile_criteria.py, gen_engine_aliases.py
tests/          run_all.py + 12 suites (403 tests)
runs/           all runtime output
```

## Environment

| variable | default | meaning |
|---|---|---|
| `RIG_LATTICE_LLM_URL` | `http://127.0.0.1:11434/v1/chat/completions` | llm_judge endpoint; only the optional `--llm` audit path uses it |
| `RIG_LATTICE_LLM_MODEL` | `llama3.3:70b` | model id |
| `RIG_LATTICE_RUNS_DIR` | `<skill>/runs` | runtime output sink |
| `RIG_DV_OFFLINE` | `0` | `1` = make no outbound model call |
| `RIG_DV_AUTO_APPROVE` | `0` | `1` = enable the auto-approving stub (tests only) |
| `RIG_DV_LLM_URL` | — | deprecated alias for `RIG_LATTICE_LLM_URL`, read first |

## Compile step

The 44 criteria packs and the 588 cell contracts are YAML for humans and JSON
for the runtime. PyYAML is a **compile-time** dependency only:

```
python3 scripts/compile_criteria.py          # write the JSON
python3 scripts/compile_criteria.py --check  # verify the pair is in sync
```

`tests/test_bundle_integrity.py` proves the audit path still scores all 44
packs with PyYAML blocked.

See `PROVENANCE.md` for every source, what was excluded, and why.
