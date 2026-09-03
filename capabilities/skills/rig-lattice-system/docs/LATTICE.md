# The RIG 3D Lattice — geometry, cell-id grammar, dialect aliases

This document is the reference for the coordinate system itself. For the
40 engines see `DOCTRINE.md`; for the 28 archetypes see `ARCHETYPES.md`.

Single source of truth in code: `rig_lattice/lattice/constants.py`. Every
number below is asserted at import time in that module — editing an enum
without editing the cardinality assertions fails immediately.

---

## 1. The three axes and the in-cell process

```
X-axis   Level / Altitude        L1 .. L7        (7)
Y-axis   Triple Diamond          D1 / D2 / D3    (3)
Z-axis   BMS Confidence / Mode   A1 .. A4        (4)

  7 levels x 3 diamonds x 4 modes            =  84 primary coordinates
 84 primary coordinates x 7 IQRSQPI steps    = 588 execution cells
  4 modes x 7 steps                          =  28 reusable archetypes
```

**IQRSQPI is not an axis.** It is the seven-step process that runs *inside* a
coordinate. The Z-axis is BMS confidence. This was the correction the OpenClaw
build card enforced, and it is the single most load-bearing fact here: the
earlier arrangement made the process an axis and produced a lattice whose
cells could not be routed to a build mode.

> **Superseded:** an earlier card multiplied 40 engines x 6 audience tiers x
> 7 steps = 1,680 cells. That is wrong. Engines are *scorers inside a cell*,
> not an axis of the lattice. The number is 588.

A second superseded arrangement lived in `enterprise/iqrsqpi.py`, which
described the lattice as "7 IQRSQPI steps x 3 layers x 4 BMS modes x 7 IQRSQPI
steps". It reached 588 by squaring the process axis — the right total for the
wrong reason. That module now re-exports the canonical tables and owns only
the pipeline runner.

### X — Level / Altitude

| level | meaning | altitude bonus |
|---|---|---|
| L1 | Direct, deterministic, repeatable | +0.35 |
| L2 | Structured but parameterized | +0.28 |
| L3 | Workflow with branches | +0.12 |
| L4 | Bounded agentic with checkpoints | 0.00 |
| L5 | Mechanism + tradeoff reasoning | −0.08 |
| L6 | Strategic synthesis required | −0.20 |
| L7 | Doctrine, exploration, novel frame | −0.35 |

The bonus is added to the raw BMS score, so low-altitude mechanical work earns
determinism and high-altitude doctrine work is pushed toward the agentic bands
by arithmetic rather than by preference.

### Y — Triple Diamond

| diamond | plane | owns |
|---|---|---|
| D1 | Physical | operations, assets, logistics, facilities, devices, payments, inventory, scheduling, infrastructure |
| D2 | Cognitive | classification, research, synthesis, reasoning workflows, doctrine, strategy |
| D3 | Nature | feedback loops, cycles, regeneration, resilience, behavior patterns, ecological metaphors |

**Dropped dialect.** strategy_studio's `lattice_wire.py` labelled this axis
`D1_STRATEGY` / `D2_INTELLIGENCE` / `D3_OPERATIONS`. That is not the doctrine
and is not an enum anywhere in this bundle. `constants.LEGACY_DIAMOND_LABELS`
exists as a docstringed lookup only, so a reader of the old artifacts can map
them across. The deterministic keyword sets in `wire.DIAMOND_KEYWORDS` are
derived from `DIAMOND_OWNS` above, which is why "operations" routes to D1 here
and would have routed to D3 under the dropped naming.

### Z — BMS Confidence / Build Mode

| mode | name | band | cost band | budget | approval | deterministic | model in decision path |
|---|---|---|---|---|---|---|---|
| A1 | PYTHON_ONLY | ≥ 0.75 | $0.001 | $0.00 | conditional | yes | no |
| A2 | HYBRID | 0.45–0.74 | $0.05 | $0.10 | conditional | no | yes |
| A3 | AGENT_BOUNDED | 0.25–0.44 | $1 | $0.50 | **mandatory** | no | yes |
| A4 | LLM_AGENT_FREE | < 0.25 | $50 | $0.00 | **mandatory** | no | yes |

Thresholds are sharp: 0.75 is A1, 0.45 is A2, 0.25 is A3, below 0.25 is A4.
Same input, same mode, always.

A4 is **adversarial, model-free decision path, mandatory human approval** — it
returns `UNKNOWN` on thin evidence rather than guessing. Earlier vendored text
described A4 as "free-form multi-agent Opus crews", which contradicts both the
$0.00 budget and the human gate; that phrasing is deleted wherever it appeared.

Escalation chain (`FALLBACK_MAP`): A1 → A3, A2 → A3, A3 → A4, A4 → none.

### The process — IQRSQPI

| code | step | purpose |
|---|---|---|
| `I1` | Intent | Classify the request/event |
| `Q1` | Question | Convert intent to operational question |
| `R` | Research | Retrieve evidence |
| `S` | Solution | Produce artifact |
| `Q2` | Quality | Safety, grounding, mechanism, policy |
| `P` | Proof | Bind sources, gates, signer, timestamp, hash |
| `I2` | Integrate | Execute / save / send / route |

---

## 2. Cell-id grammar

### Canonical form

```
L{1-7}-D{1-3}-A{1-4}-{I1|Q1|R|S|Q2|P|I2}

L3-D2-A2-R     Level 3 / Cognitive / HYBRID / Research
```

Regex: `constants.CELL_ID_PATTERN_STRICT` —
`^L([1-7])-D([1-3])-A([1-4])-([A-Z][0-9]?)$`

Derived forms:

| form | example | produced by |
|---|---|---|
| primary coordinate | `L3-D2-A2` | `CellCoordinate.primary_coordinate` |
| archetype id | `A2.3` | `ARCHETYPE_MAP[(mode, step)]` |
| fallback archetype | `A3.A2.3` | `FALLBACK_MAP` + archetype |
| contract filename | `L3-2-A2-R.yaml` | `CellCoordinate.filename` |

### Accepted input dialects

`resolver.parse_cell_id` accepts three spellings and always returns the
canonical form. This is the fusion's compatibility surface: four source repos
each spelled cell ids differently, and callers in the wild still use all
three.

| dialect | source | example | normalizes to |
|---|---|---|---|
| **canonical** | strategy_studio strict pattern | `L1-D1-A1-I1` | `L1-D1-A1-I1` |
| **bare-digit diamond** | rig-monorepo `CELL_ID_RE` | `L1-1-A1-I1` | `L1-D1-A1-I1` |
| **dotted** | rig-deviator `enterprise/iqrsqpi.py` | `intent.D1_physical.A1.intent` | `L1-D1-A1-I1` |

The dotted dialect carries no level; it resolves to `L1` and the step is taken
from the trailing segment (falling back to the head when the tail is not a
step token).

### Rejected shape

```
L2-D1-Intent        # pre-Z-axis: no BMS mode
```

`OLD_CELL_ID_PATTERN` matches it *specifically so the error can explain it*:

```
error: Invalid cell_id 'L2-D1-Intent'. Accepted shapes:
  canonical  L{1-7}-D{1-3}-A{1-4}-{I1|Q1|R|S|Q2|P|I2}   e.g. L3-D2-A2-R
  bare-digit L{1-7}-{1-3}-A{1-4}-{step}                 e.g. L3-2-A2-R
  dotted     <head>.D{1-3}_<plane>.A{1-4}.<step>        e.g. intent.D1_physical.A1.intent
This is the pre-Z-axis shape (no BMS mode). The Z-axis is BMS confidence,
not IQRSQPI — add the A{1-4} segment.
```

Silently defaulting the missing mode would be the worst available behavior: it
would invent the one axis the caller failed to specify.

### Step aliases

`normalize_step` accepts `I→I1`, `Q→Q1`, `I5→I2` plus the full word forms
(`INTENT`, `QUESTION`, `RESEARCH`, `SOLUTION`, `QUALITY`, `PROOF`,
`INTEGRATE`). Same alias semantics as
`rig_capabilities/iqrsqpi_v10.py:normalize_stage`.

---

## 3. Why filenames keep the bare-digit dialect

The 588 contracts under `lattice/cells/` are named `L1-1-A1-I1.yaml`, not
`L1-D1-A1-I1.yaml`. They are **not renamed**: they were generated that way in
the source monorepo, and renaming 588 files to cosmetically match the
canonical id would break byte-comparison against the originals — which is the
only evidence that the generated set is faithful.

`generator.load_cell` and `CellCoordinate.filename` map canonical → filename.
`DIAMOND_DIGIT` / `DIAMOND_FROM_DIGIT` in `constants.py` are that mapping.

At runtime `load_cell` reads the compiled `lattice/cells.json` index (keyed by
*both* dialects) so the A1 path needs no YAML parser. It falls back to PyYAML
with a one-time warning, and raises naming `scripts/compile_criteria.py` when
neither source is usable.

---

## 4. BMS scoring

```
raw   = failure_cost*0.4 + reversibility*0.3 + mechanism_clarity*0.3
final = clamp(raw
              - past_failure_rate*0.2
              + (data_volume - 0.5)*0.1
              + ALTITUDE_BONUS[level],
              0.0, 1.0)
mode  = BMSMode.from_score(final)
```

Every input is validated to `[0,1]` and raises `ValueError` outside it — a
silently clamped input would produce a mode that looks earned. The altitude
term spans exactly 0.70 between L1 (+0.35) and L7 (−0.35), which is the
largest single lever in the formula: the same criteria at L1 and L7 are two
different build modes, by design.

`BMSResult.to_dict()` reports `raw` and each adjustment separately, so a mode
can always be re-derived from the record rather than trusted.

---

## 5. Cardinality invariants

Asserted at import of `constants.py`:

```python
assert (N_LEVELS, N_DIAMONDS, N_MODES, N_STEPS) == (7, 3, 4, 7)
assert N_PRIMARY_COORDS == 84
assert N_CELLS == 588
assert N_ARCHETYPES == 28
assert len(ARCHETYPE_MAP) == 28
assert set(ALTITUDE_BONUS) == {lv.value for lv in LEVELS}
```

Checked again from the outside by `tests/test_bundle_integrity.py`: 588 unique
canonical ids, each mapping to an existing contract file, each contract's
stored `archetype` / `fallback_archetype` / `deterministic` /
`model_in_decision_path` / `cost_band` agreeing with what `resolve()` computes.

`LATTICE_VERSION = "3.0"` — the version of this fusion.

```
$ bin/rig-lattice lattice summary --json
{"levels":7,"diamonds":3,"bms_modes":4,"steps":7,
 "primary":84,"cells":588,"archetypes":28,"version":"3.0"}
```
