---
name: great-immutable-surface-guard
lane: agent-engineering
source: canonical-curated
exemplar_of: immutable-surface-guard.sh
description: Reference exemplar — a self-improvement run that edits its own gate is denied at pre-write time; only the declared mutable surface moves, and every denial names its clause
---

# immutable-surface-guard — reference

Canonical asset `immutable-surface-guard.sh` (hook). Path: `capabilities/hooks/immutable-surface-guard.sh`. Checker: `capabilities/hooks/fixtures/immutable-surface/check_surface.py`.

## What it gates

Recursive self-improvement loops score a delta and credit the mutable layer — memory, config, prompts. That credit is only real if nothing outside the mutable layer moved. The corpus names the failure exactly: an improver that can rewrite its own validation gate produces a "passing" loop whose score means nothing, because the definition of passing moved with it.

Mechanism source (per `.context/discover-ai/capability-matrix.json`, row `immutable-surface-guard`):

- **Recursive Experiential-Working Memory Evolution for Long-Horizon Agent Harnesses (Recuris)**, `arXiv:2608.24876` (repo `Gen-Verse/Recuris`), video `F1XqqVNBa4o`: the harness declares a mutable surface (its experiential/working memory and config); model weights, tools, the meta-agent, the failure-localization procedure, the patching procedure, and the validation gate are FIXED by declaration — a pre-write check denies writes outside the declared set, so any score delta is attributable to the mutable layer alone.

The RIG delta this closes: no RIG loop declares an editable-surface boundary. `mh-01-skill-genesis-session.yaml` and `mh-02-harness-forge-session.yaml` constrain OUTPUTS by gates, not which files the improver may edit — today any loop can rewrite its own gate. RED for this asset means exactly that: the "immutable" machinery is prose, and the improver's score is self-reported from inside the thing it edited.

## Contract

House stdin-JSON convention (`guard-secret-write.sh`, `working-memory-commit-gate.sh`): PreToolUse payload on stdin; the write path comes from `tool_input.{file_path,path,target_file,notebook_path}`. The surface manifest is `$SURFACE_MANIFEST` (YAML); the checker is `$SURFACE_CHECKER`, defaulting to the canonical copy next to the hook — installing the hook alone without either pointer fails CLOSED with a named reason. The manifest is a flat YAML subset:

```yaml
harness_id: recuris-style-experience-loop
root: harness
mutable_surface:
  - memory/*.md
  - memory/archive/*.jsonl
  - config/notes.yaml
  - runs/*.jsonl
immutable:
  - machine/self_improver.py
  - machine/check_gate.py
  - machine/validate_run.py
```

Globs match across `/`; a write path is harness-relative or root-prefixed. Empty stdin or a payload with no file path exits 0 — nothing was proposed; that is not a verdict.

| Named denial | Exit | Fires when |
|---|---|---|
| `OUTSIDE_SURFACE` | 2 | no `mutable_surface` glob covers the (normalized) path — including absolute paths outside the declared root |
| `SURFACE_EMPTY` | 2 | `mutable_surface` declared with zero entries — an allowlist that allows nothing denies, it never permits |
| `SURFACE_MISSING` | 2 | the manifest declares no `mutable_surface` at all — a missing allowlist is denial, not licence |
| `MANIFEST_MALFORMED` | 2 | structure the guard will not guess (e.g. `mutable_surface` as a scalar) — a manifest rejected here judges no write |
| `WRITE_MALFORMED` | 2 | a proposed-write row that is not JSON or carries no non-empty `path` |
| `SELF_TOUCH` | 2 | the write targets declared-immutable machinery — **wins even when a widened allowlist would cover it** |
| `PATH_ESCAPE` | 2 | the RAW string matches a glob but the normalized path does not (`memory/archive/../weights.jsonl`) — traversal is not a side door |
| refusal | 1 | manifest or writes file not found / usage — a refusal to judge, never a verdict; at runtime the hook converts it to exit 2 (fail closed) |

## The done_when proves each clause separately

Fixtures: `capabilities/hooks/fixtures/immutable-surface/`. Twelve checks; the planted failures are permanent regression cases:

1. `writes_in.jsonl` × `surface_valid.yaml` → **0** (four harness-relative writes inside the surface).
2. `writes_root.jsonl` × `surface_valid.yaml` → **0** (root-prefixed paths judge identically).
3. `writes_outside.jsonl` → **2** `OUTSIDE_SURFACE` — `src/policy/patcher.py` and `harness/weights/final_adapter.safetensors`: the improver's own code and weights are not memory.
4. `surface_empty.yaml` → **2** `SURFACE_EMPTY`.
5. `surface_nokey.yaml` → **2** `SURFACE_MISSING`.
6. `surface_malformed.yaml` → **2** `MANIFEST_MALFORMED` — the guard refuses to coerce a scalar into an allowlist.
7. **The plant-failure**: `surface_widened.yaml` + `writes_gate_touch.jsonl` → **2** `SELF_TOUCH` — the run widened its own allowlist to `machine/*.py` and then edited `machine/check_gate.py`. The memory write in the same run stays `ALLOW`: the denial is the gate edit, not a blanket block.
8. `writes_escape.jsonl` → **2** `PATH_ESCAPE` while the benign traversal `runs/2026-09/../2026-08/notes.jsonl` stays allowed — the clause bites the side door, not honest `..`.
9. `writes_malformed.jsonl` → **2** `WRITE_MALFORMED`.
10–11. the hook end-to-end: a payload writing `harness/memory/lesson_001.md` → **0**; a payload writing `harness/machine/check_gate.py` → **2**.
12. `file:` on the checker.

`tests/test_immutable_surface_guard.py` adds the refusal contract (exit 1 for missing files/usage; runtime fail-closed for a configured guard whose manifest or checker is missing) and proves the checker mutates nothing (fixture-tree digest identical after every verdict).

## What RED means operationally

- `SELF_TOUCH` on a live improvement run: the loop reached for its own gate — the exact condition that makes every prior score unattributable. The run stops before the bytes move, not after the "improvement" ships.
- `SURFACE_MISSING`/`SURFACE_EMPTY`: someone pointed a loop's `SURFACE_MANIFEST` at a file that declares nothing editable. The guard reads that as "nothing may move," so a gutted allowlist cannot quietly become a blank cheque.
- `PATH_ESCAPE`: an optimizer tried `memory/archive/../weights.jsonl` to land outside a glob that literally covers `memory/archive/*`. Membership is decided on the normalized path.
- Runtime fail-closed: a configured-but-broken guard denies instead of defaulting open — the guard-secret precedent deliberately inverted, because an unguarded improver is worse than a stalled one.

## Ceiling

The hook validates what the payload **declares** — it sees proposed tool writes, not every process-level `write(2)`; a harness that lets arbitrary shell escape the pre-write boundary keeps that surface outside this guard (the named risk from the source row stays open: allowlists drift as harnesses gain legitimate files, so manifest changes are versioned with the harness and themselves a Gate-D action).
