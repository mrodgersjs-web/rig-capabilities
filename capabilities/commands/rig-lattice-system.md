---
name: rig-lattice-system
description: Route work to a lattice cell and BMS build mode before building it, audit an artifact through the 40 deviation engines, score an idea against the V3.1 creativity gates, or run the full L1-L7 orchestration — one CLI over the 588-cell RIG Lattice System.
argument-hint: "<summary|cell|cells|bms|route|audit|deviate|des2|idea|run|engines|doctor> [args]"
allowed-tools: Read, Bash
category: agent-engineering
outcome: "agent-engineering: every verb resolves to one deterministic CLI call whose output is the evidence — a cell id, a BMS band, a per-engine sigma, or a verdict — instead of the agent's own account of what it decided"
done_when:
  - file:capabilities/commands/rig-lattice-system.md
  - file:capabilities/skills/rig-lattice-system/bin/rig-lattice
  - grep:capabilities/commands/rig-lattice-system.md:GRAVITON
  - cmd:capabilities/skills/rig-lattice-system/bin/rig-lattice lattice summary --json | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['cells']==588 and d['archetypes']==28"
  - cmd:capabilities/skills/rig-lattice-system/bin/rig-lattice doctor --json | python3 -c "import json,sys; assert json.load(sys.stdin)['ok'] is True"
  - cmd:python3 scripts/gen_engine_aliases.py --check 2>/dev/null || python3 capabilities/skills/rig-lattice-system/scripts/gen_engine_aliases.py --check
  - cmd:python3 -c "import re,sys; sys.path.insert(0,'capabilities/skills/rig-lattice-system'); from rig_lattice.engine_aliases import CODENAME_TO_ENGINE_ID as C; doc=open('capabilities/commands/rig-lattice-system.md').read(); rows=dict(re.findall(r'^\| \`([A-Z-]+)\` \| \`(e\d\d)\`', doc, re.M)); assert rows, 'alias table not found in the command doc'; missing=[k for k,v in rows.items() if C.get(k)!=v]; assert not missing, f'doc disagrees with engine_aliases.py: {missing}'; assert len(rows)==len(C), f'doc has {len(rows)} rows, table has {len(C)}'"
great_example: examples/great/agent-engineering/rig-lattice-system.md.md
acl: public
quality_floor: 0.7
---

# /rig-lattice-system

One CLI over the RIG Lattice System. The binary lives in the skill payload:

```
capabilities/skills/rig-lattice-system/bin/rig-lattice
```

Installed copies resolve the same way from any harness root
(`~/.claude/skills/rig-lattice-system/bin/rig-lattice`, and the same under
`~/.codex`, `~/.hermes`, `~/.agents`, `~/.omp`).

## Verbs

| `/rig-lattice-system <verb>` | CLI subcommand | what you get |
|---|---|---|
| `summary` | `lattice summary` | `{levels:7, diamonds:3, bms_modes:4, steps:7, primary:84, cells:588, archetypes:28, version:"3.0"}` |
| `cell <id>` | `lattice cell <id>` | parse + resolve + the vendored cell contract |
| `cells` | `lattice cells` | all 588 canonical ids |
| `bms <F> <R> <M> [level]` | `bms score --failure-cost F --reversibility R --mechanism-clarity M --level L3` | the `BMSResult`: confidence, mode, budget, approval |
| `route <text>` | `route <text> [--step I1] [--domain d]` | cell id + mode + archetype + budget + rationale |
| `audit <path>` | `audit <path\|-> [--engines ...] [--llm]` | per-engine σ, status, RIG-L, BDF, gate verdict |
| `deviate <path>` | `deviate <path> [--sigma 20]` | the dv patch pipeline |
| `des2 <path>` | `des2 <path>` | the five DES² rigor amplifiers |
| `idea <title>` | `idea score --title T --content C ...` | creativity score + 4 gates + verdict |
| `grid <file>` | `idea grid --candidates FILE --seed N` | the 25-niche MAP-Elites menu |
| `run <path>` | `run <path> --confidence C [--force-a4]` | full L1→L7 orchestration |
| `engines` | `engines` | the 40-engine roster |
| `doctor` | `doctor` | imports, counts, compile freshness, env |

Every subcommand accepts `--json`.

## The route-before-build rule

```bash
SKILL=capabilities/skills/rig-lattice-system

# 1. coordinate BEFORE the first edit
$SKILL/bin/rig-lattice route "migrate the billing table to the new schema" --json
# -> cell_id, mode, archetype, budget_usd, approval_required

# 2. justify the mode
$SKILL/bin/rig-lattice bms score --failure-cost 0.9 --reversibility 0.2 \
  --mechanism-clarity 0.7 --level L5 --json

# 3. build A1-first, then score the artifact
$SKILL/bin/rig-lattice audit migration.sql --json

# 4. prove the installed copy is intact
$SKILL/bin/rig-lattice doctor
```

Cell ids accept three dialects, all normalized to canonical
`L{1-7}-D{1-3}-A{1-4}-{step}`:

| input | normalizes to |
|---|---|
| `L1-D1-A1-I1` | `L1-D1-A1-I1` (canonical) |
| `L1-1-A1-I1` | `L1-D1-A1-I1` (bare-digit diamond) |
| `intent.D1_physical.A1.intent` | `L1-D1-A1-I1` (dotted) |
| `L2-D1-Intent` | **rejected** — pre-Z-axis shape, no BMS mode |

## BMS bands

| mode | band | name | budget | approval | model in decision path |
|---|---|---|---|---|---|
| `A1` | ≥ 0.75 | PYTHON_ONLY | $0.00 | conditional | no |
| `A2` | 0.45–0.74 | HYBRID | $0.10 | conditional | yes |
| `A3` | 0.25–0.44 | AGENT_BOUNDED | $0.50 | **mandatory** | yes |
| `A4` | < 0.25 | LLM_AGENT_FREE | $0.00 | **mandatory** | yes (adversarial, model-free decision) |

## Engine codename aliases

The same aliases the ~40 `rig-<codename>` skills and the Alfred LinkedIn
pipeline already use. Machine-readable twin:
`rig_lattice/engine_aliases.py` — a done-test above asserts this table and
that file agree row for row.

| codename | engine |
|---|---|
| `GRAVITON` | `e01` |
| `ANCHOR` | `e02` |
| `XRAY` | `e03` |
| `FORGE` | `e04` |
| `BREAKER` | `e05` |
| `COLLIDER` | `e06` |
| `VOLT` | `e07` |
| `DARWIN` | `e08` |
| `ECHO` | `e09` |
| `HORIZON` | `e10` |
| `SOVEREIGN` | `e11` |
| `SURPRISE` | `e12` |
| `ANTISLOPAUDITOR` | `e13` |
| `GLYPH` | `e14` |
| `WELLSPRING` | `e15` |
| `FALSIFICATIONPREREG` | `e16` |
| `REBOUND` | `e17` |
| `BAYES` | `e18` |
| `SHIELD` | `e19` |
| `COMPOUNDINGEDGE` | `e20` |
| `SWARM` | `e21` |
| `BEEFORAGINGALLOCATOR` | `e22` |
| `SLIME` | `e23` |
| `CLONAL` | `e24` |
| `ALBATROSS` | `e25` |
| `LUMINA` | `e26` |
| `COLI` | `e27` |
| `HUMPBACK` | `e28` |
| `CUCKOO` | `e29` |
| `REEF` | `e30` |
| `TUNNEL` | `e31` |
| `PAULI` | `e32` |
| `CASIMIR` | `e33` |
| `PARSEC` | `e34` |
| `HORIZON-GATE` | `e35` |
| `LUMEN` | `e36` |
| `KELVIN` | `e37` |
| `CRITICAL` | `e38` |
| `BELL` | `e39` |
| `ZEROPOINT` | `e40` |
| `WITNESS` | `e15` |

`e15` is `hermeneutic_density` / `SourcePerClaim` — per-claim source
weighting, the WITNESS engine. Its criteria pack is labelled `WELLSPRING`
upstream. Both codenames resolve to `e15` rather than dropping one; the
mislabel is recorded in the payload's `PROVENANCE.md`.

## Environment

| variable | default | meaning |
|---|---|---|
| `RIG_LATTICE_LLM_URL` | `http://127.0.0.1:11434/v1/chat/completions` | only the opt-in `--llm` audit path uses it |
| `RIG_LATTICE_RUNS_DIR` | `<skill>/runs` | runtime output sink |
| `RIG_DV_OFFLINE` | `0` | `1` = make no outbound model call |
| `RIG_DV_AUTO_APPROVE` | `0` | `1` = auto-approving stub (tests only) |

## Related

- `rig-lattice-system` — the payload: package, CLI, 588 cell contracts, tests
- `rig-deviation-engines` — the 40-engine roster and σ ladder
- `rig-idea-generator` — the V3.1 gates, MAP-Elites, ASR stack
- `rig-lattice-router` (agent) — returns only the routing contract, no prose
- `mh-07-lattice-application-session` (harness) — makes "apply the lattice to
  this app" a gated session
