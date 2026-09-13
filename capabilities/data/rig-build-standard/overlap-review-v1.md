# Overlap review — the build-standard trio vs existing canonical skills (A56)

Reviewed 2026-09-13 against the live index (`.index.json`, 5060 entries, 114 canonical
skills) **with the bodies read**: `adversarial-verification-loop` in full (71 lines);
`d85-compliance-checklist`, `proof-loop`, `phase-discipline-loop` read to line 26 (all of
frontmatter, hooks, and opening claims) plus targeted greps for the load-bearing terms
(`0.85`, `REALIZED_PASS`, `d85`, `certificate`, `hook stop`) — the rest of those three
bodies is stage tables, so the ratio/certificate question is settled by grep, not
inference. No file outside `capabilities/data/rig-build-standard/` was changed and nothing
was deleted — A56 is resolved by stating ownership, not by removing an agent's asset.

## Where the same job is claimed twice

| asset | what it claims | who actually owns the mechanism | verdict |
|-------|----------------|--------------------------------|---------|
| `rig-build-standard` (skill) | one always-loaded policy: diagnose → classify → score → certify → seal, for four runtimes | **owner of the umbrella and of `bin/rig-build-standard` verbs** (pack / index / commit-gate / packet / surface / check / test) | canonical |
| `rig-determinism-85` (skill) | the admission chain: inventory, classification, four ratios, certifier | **owner of the math** (`d85.py`, `rig-determinism-85/bin/…`, `authority/registry.json`) | canonical |
| `d85-compliance-checklist` (skill) | "load at the start of every coding task" + the five gate phases; at `SKILL.md:58` it also restates `ALL FOUR ratios ≥ 0.85 with REALIZED_PASS` and the exit-2-is-terminal rule | the ritual and the OMP load path are its own; the numbers belong to `rig-determinism-85`, which it already names as its authority ("Where this checklist and a RELEASED authority file disagree, the released file wins") | **canonical for the ritual; one concrete edit owed** — line 58 should point at the scorer instead of re-typing the threshold and ratio names, because a drift in `d85.py` will otherwise leave a stale 0.85 sentence in a skill every OMP session loads |
| `durable-build` (skill + loop) | the one lane whose `d85_certified` / `build_diagnosis` gates cannot be forced | **owner of the durable-build run state machine** (`rig_capabilities/loops.py` halt tier, `advance()` refusing `force`) | canonical; arms **no** hook — it is advanced explicitly, so it adds no per-tool hook cost |
| `proof-loop` (skill + loop) | Honest Completion as an executable loop: done-test → checks green → planted failure RED→GREEN → independent verdict → sealed packet, and it declares a Stop hook (`SKILL.md:32`) | **owner of the no-done-without-proof doctrine and of `proof-loop`'s own loop cases** — it does **not** own the hook: `bin/rig-loop hook stop --format claude` is shared engine machinery declared identically by 9 canonical skills (below) | **sibling, not subordinate.** It gates the *session's* claim in doctrine; `durable-build` gates the *build's* advance in `advance()`. Neither may redefine the other's enforcement, and neither may claim the shared hook as private property |
| `adversarial-verification-loop` (skill + loop) | non-vacuity as a five-stage loop: `G Guard → R Red (plant, expect FAIL) → N Green → K Keep fixture → P Proof`, with `rig-loop plant --red --green` running **both** commands itself and recording exit codes; `red_ok: false` keeps stage R red | **owner of the plant-failure method and its fixture discipline** ("Plant a real defect in the code or data the gate guards, not a `false` command"; K demands the fixture path) | **sibling consumed by `durable-build`**, whose V stage turns that method into a named gate (`planted_failure`). The loop skill defines the method and the tool; the build lane requires its output. Any plant this repo claims should run through `rig-loop plant`, not a hand edit |
| `phase-discipline-loop` (skill + loop) | order phases by dependency, never advance on red, commit on green | owner of ordering doctrine | no conflict, and **already declared**: `durable-build` names it in `relates_to` alongside `proof-loop`, `gate-d-loop`, `git-push-safety-loop` — no new graph edge needed |
| `gate-d-loop`, `git-push-safety-loop`, `north-star-lock-loop` | authorization, push safety, scope lock | each owns its own gate | no conflict — different axis (authorization vs build quality) |
| `rig-build-mcp` (skill) | how to call `capabilities_build_*` correctly | **owner of the call order and refusal-meaning table**; contains no policy | canonical, new |

## The rule this leaves behind

One owner per claim. A surface may *point* at a mechanism; it may not re-define it.
Concretely: the four-ratio threshold, the `d85_certified` non-forceability rule, and the
plant-failure requirement are each defined in exactly one place. If a fourth skill needs
them, it links.

## Hook surface (measured, so the collision question is settled)

9 canonical `SKILL.md` files arm a `PreToolUse` hook, all matching
`Write|Edit|MultiEdit|NotebookEdit|Bash` through `bin/rig-loop hook pre-tool --skill <name>`.
`durable-build` arms none of them. So installing the build lane does **not** add a
per-tool-call hook process; where its gates overlap the loop family's, the overlap is in
gate semantics, and the table above assigns the owner.

**Stop hooks are shared, not owned.** 9 canonical `SKILL.md` files declare a `Stop` hook —
`phase-discipline-loop`, `proof-loop`, `gate-d-loop`, `adversarial-verification-loop`,
`iqrsqpi-v20-slice`, `iqrsqpi-v20`, `iqrsqpi-v11`, `north-star-lock-loop`,
`git-push-safety-loop` — and every one of them runs the *same* command string,
`bin/rig-loop hook stop --format claude`. Whether the runtime dedupes identical commands or
fires nine times per Stop event is **UNVERIFIED**; either way no single loop skill owns
that gate, so the table above assigns ownership of the *doctrine*, not of the hook.

## Discovered catalog constraint (not a defect in anything shipped)

`catalog.py` keys an asset by its directory name (`id = entry.name`) and treats `data` as a
directory-descriptor kind requiring `DATA.md`. Consequences:

1. `capabilities/data/rig-build-standard/policy.md` and
   `capabilities/data/durable-repeatable-index/SCHEMA.md` are **support files, not
   assets** — a loose file under `capabilities/data/` is deliberately never indexed
   (the phantom-asset guard at `catalog.py:49-52`). This is intended, not broken.
2. If either is ever promoted to a real `data` asset, it needs its own `DATA.md` **and** a
   directory name that does not collide with a same-named skill: `data/rig-build-standard`
   would take id `rig-build-standard`, which the skill already holds. Promote as
   e.g. `data/build-standard-policy` instead, and keep `policy.md` byte-identical so the
   sha bound in the sealed Gate-D rows (`8501a8c9…`) stays valid.

Nothing was promoted in this session; the constraint is recorded so the next agent does not
discover it by breaking the index.

## Runtime-format probe (codex agent load, still UNVERIFIED)

`codex` is on PATH at `~/.hermes/node/bin/codex`; `codex --help` exposes `exec`,
`review`, `mcp`, `plugin`, `doctor`, `sandbox`, `debug` and friends — **no agent-listing
surface**. `~/.codex/agents` holds 549 `.toml` and 107 `.md` files, and
`rig-stackwright.md` sits there as `.md` with no `.toml` sibling. Directory presence is
not load evidence (the copied≠loaded trap), and there is no CLI command that answers the
question, so codex markdown-agent load stays **UNVERIFIED** and is decided by Mike under
request NB-03, not inferred from a file count.

## Plant-mechanism note (applies to this repo's own claims)

The publish-residue plant (see `receipts/advisory-wave-addendum-20260913T0732Z.json`) was
done by hand: whole `try/finally` removed, body dedented, RED asserted as leftover scratch
(`AssertionError: [] != ['.index.53107.tmp']`), byte-exact restore, re-GREEN. That is
behavioural evidence, but `adversarial-verification-loop` already owns the house mechanism —
`bin/rig-loop plant <name> --red <cmd> --green <cmd>` runs both sides itself and records the
exit codes. Next plant runs through it so the run record, not a chat transcript, is the
receipt.

Its first attempt deleted only the `finally:` clause and produced a `SyntaxError` at import
— rejected as evidence: a broken import is not a residue finding. Recorded here because the
distinction is the whole point of the K stage.
