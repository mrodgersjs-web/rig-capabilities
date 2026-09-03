---
name: great-rig-lattice-system-command
lane: agent-engineering
source: canonical-curated
exemplar_of: rig-lattice-system.md
description: Reference exemplar — the slash-command surface whose every verb is one deterministic CLI call, with an alias table a done-test parses back out of this doc and compares to the generated module row for row
---

# /rig-lattice-system — reference

Canonical asset `rig-lattice-system.md` (command). Path:
`capabilities/commands/rig-lattice-system.md`.

> Every verb resolves to one deterministic CLI call whose output is the
> evidence — a cell id, a BMS band, a per-engine σ, a verdict — instead of the
> agent's own account of what it decided.

## What good looks like

The command is a thin, honest map from verb to subcommand. No verb does work
the CLI cannot do, and none hides a decision:

| verb | subcommand | evidence returned |
|---|---|---|
| `summary` | `lattice summary` | the 588/84/28 geometry |
| `cell <id>` | `lattice cell <id>` | resolved contract, any of 3 dialects |
| `bms F R M [level]` | `bms score …` | confidence, band, budget, approval |
| `route <text>` | `route <text>` | cell id + mode + archetype + rationale |
| `audit <path>` | `audit <path>` | per-engine σ, RIG-L, BDF, hard_blocks |
| `idea <title>` | `idea score …` | creativity score + 4 gates + verdict |
| `doctor` | `doctor` | imports, counts, compile freshness, env |

## The route-before-build rule, as a runnable sequence

```bash
# 1. coordinate BEFORE the first edit
$ rig-lattice route "migrate the billing table to the new schema" --json
# 2. justify the band
$ rig-lattice bms score --failure-cost 0.9 --reversibility 0.2 \
    --mechanism-clarity 0.7 --level L5 --json
# 3. build A1-first, then score the artifact
$ rig-lattice audit migration.sql --json
# 4. prove the installed copy is intact
$ rig-lattice doctor
```

## The doc cannot drift from the code

The alias table in this command is the human-readable twin of
`rig_lattice/engine_aliases.py`. A `done_when` entry parses the table **out of
the markdown** and compares it to the generated module:

```python
rows = dict(re.findall(r'^\| \`([A-Z-]+)\` \| \`(e\d\d)\`', doc, re.M))
assert rows, 'alias table not found in the command doc'
missing = [k for k, v in rows.items() if C.get(k) != v]
assert not missing, f'doc disagrees with engine_aliases.py: {missing}'
assert len(rows) == len(C), f'doc has {len(rows)} rows, table has {len(C)}'
→ doc rows: 41   table: 41   mismatched: []
```

Deleting a row, renaming a codename, or reordering the registry turns this
red. A documentation table that is checked is documentation that can be
trusted; one that is not is a comment.

## What the name records

This command is `/rig-lattice-system`, not `/rig-lattice`, because
`/rig-lattice` was already a hand-authored command in four harness roots that
opens an unrelated 3,087-cell 3D viewer. The collision was found at install
time — `error: target exists and differs` — and resolved by renaming the new
asset rather than overwriting a file the operator wrote. The install ledger
entry for the superseded path was pruned, and the copy already placed in
`~/.omp` was reverted.

An installer that reports `target exists and differs` instead of clobbering is
the reason that was recoverable.

## Why it is not an alias list

The RIG delta: a slash command that restates what a tool does adds a second
place to be wrong. This one adds a checked mapping (verb → subcommand), a
checked alias table (codename → engine id), and the BMS band table with the
budget and approval columns that decide whether a human is required. Each is
either executed or parsed by a done-test.

Verified: 7 `done_when` entries, 0 unrunnable; installed to all five harness
roots plus `.prime`; `install.sh --verify` → all MCP targets OK.
