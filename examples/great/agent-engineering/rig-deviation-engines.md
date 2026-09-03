---
name: great-rig-deviation-engines
lane: agent-engineering
source: canonical-curated
exemplar_of: rig-deviation-engines
description: Reference exemplar — 40 engines split 20/10/10 with all ten physics engines as gates, the physics-first short-circuit rule, and a codename alias table generated from the registry rather than retyped
---

# rig-deviation-engines — reference

Canonical asset `rig-deviation-engines` (skill, pointer). Implementation:
`capabilities/skills/rig-lattice-system/rig_lattice/core/registry.py`.

> An artifact's quality is a per-engine σ against a calibrated baseline with a
> named blocking gate — not an adjective the author chose for their own work.

## What good looks like

The roster is a cardinality the registry asserts at import time, so a
mis-edit fails loudly rather than quietly shipping 39 engines:

```python
ENGINE_REGISTRY: list[EngineSpec] = COGNITIVE + NATURE + PHYSICS
assert len(ENGINE_REGISTRY) == 40, f"Expected 40 engines, got {len(...)}"
```

```
$ bin/rig-lattice engines --json | ...
40 engines   cognitive 20 / nature 10 / physics 10
all 10 physics engines: is_gate = true
```

| layer | count | range | role |
|---|---|---|---|
| cognitive | 20 | ±20σ | output scoring |
| nature | 10 | ±20σ | process scoring |
| physics | 10 | ±30σ | **gates** — one HARD_BLOCK blocks the artifact |

## Physics-first short-circuit

A real audit of this bundle's own doctrine file, read as the doctrine says to
read it — gates before scores:

```
$ bin/rig-lattice audit docs/DOCTRINE.md --json
rig_l -3.00   bdf -21.56   status HARD_BLOCK   hard_blocks 36
weakest   SOVEREIGN         σ -30.00
strongest AntiSlopAuditor   σ +25.00
```

`hard_blocks 36` is the verdict. The other 30 engines' scores do not buy a
pass, and no amount of prose about the artifact's merits changes the count.

## The alias table is generated, not typed

The ~40 `rig-<codename>` skills and the Alfred pipeline address engines by
short codename. Retyping that mapping is how it drifts, so it is generated
from the registry plus the criteria packs, and a done-test refuses a stale
copy:

```
$ python3 scripts/gen_engine_aliases.py --check
OK: engine_aliases.py in sync (40 engines)

$ resolve_codename('COLLIDER') → e06   (frame_collision)
$ resolve_codename('ZEROPOINT') → e40  (vacuum_zeropoint)
```

A second done-test parses the alias table out of the command doc's markdown
and asserts it agrees with the module row for row — 41 rows, zero mismatches.
Deleting either the table or a row turns it red.

## An upstream conflict preserved rather than guessed

Engine `e15` is `hermeneutic_density` / `SourcePerClaim` — per-claim source
weighting, which is the **WITNESS** engine. Its criteria pack is labelled
`codename: WELLSPRING`, a different concept entirely (hedonic adaptation).

Both codenames resolve to `e15` so either caller works, and the test asserts
that `e15` is the **only** shared id:

```python
KNOWN_SHARED_IDS = {"e15"}
shared = {eid for eid, names in seen.items() if len(names) > 1}
self.assertEqual(shared, KNOWN_SHARED_IDS)
```

A new accidental collision therefore fails the suite; the one deliberate
collision is named, tested, and recorded in PROVENANCE.md. Nobody guessed
which artifact was wrong.

## Why it is not a linter

The RIG delta: a linter reports style. These engines score *deviation from a
calibrated corpus* and ten of them are gates with a hard block, so the output
is a decision — ship, patch, or escalate — with the failed criterion's
question id and evidence quote attached. Every engine below threshold must
leave the session with a patch or a named reason, and the calibration ladder
is under a `git diff --exit-code` gate so no one clears a gate by moving it.

Verified: `bin/rig-lattice engines --json` → 40/20/10/10, physics all gates;
`tests/test_bundle_integrity.py::TestEngines` → every `module_path` imports.
