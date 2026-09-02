---
name: great-skill-preload-precondition-gate-sh
lane: agent-engineering
source: canonical-curated
exemplar_of: skill-preload-precondition-gate.sh
description: Reference exemplar — a skill whose body reaches context because it was *relevant* is the bug; this prefilter refuses with three non-collapsible classes (exit 2 MISSING / exit 3 UNSATISFIABLE / exit 4 CONFLICT), accepts a compatible pack at exit 0, and never says PASS
---

# skill-preload-precondition-gate.sh — reference

Canonical asset `skill-preload-precondition-gate.sh` (hook). Path: `capabilities/hooks/skill-preload-precondition-gate.sh`.

## What it gates

The estate picks what enters context by **similarity** and nothing else: `capabilities_search`, `capabilities_context_pack`, and `capabilities_route` rank with BM25 + dense embeddings + outcome-lane routing + graph expansion and evaluate zero preconditions at the moment of injection. `rig_capabilities/skill_contract.py` proves an asset *declared* its `activation` + `applies_when` slots at authoring time (`ABSENT`/`MALFORMED` → not loadable) — declaredness, never evaluation. Nothing anywhere asked the two questions this gate asks before a body reaches the prompt: **(1) does the declared predicate actually HOLD against live state and the active goal, and (2) is every default the asset carries COMPATIBLE with this task's binding requirements?**

Mechanism sources (all verified in `.context/discover-ai/link-verdicts.json`): *Towards a Systems Foundation for Agentic Skills*, `arXiv:2608.29596`, video `Kbxg-_CXs78`; *Agent Skills Can Be Harmful*, `arXiv:2608.11888`, video `TA5QzGTQU_U`; *WikiSkill*, `arXiv:2608.27454`, video `sHeITqLW2BY`; *Steering-Tool-Use-Propensity*, `arXiv:2608.25198`, video `C-Mk88De36M`. Verbatim caption quotes (each grep-verified as a substring of the named transcript under `.context/discover-ai/transcripts/`, 2026-09-02):

> "a skill activates conditional based on the agent state x of t and the activation goal g" — `Kbxg-_CXs78.txt`. A skill is the six-tuple `<A, I, C, P, π, E>`; `alpha(s, x_t, g) == 1` is the only thing that makes it loadable, and similarity is not `alpha`.

> "relevance is not compatibility of the system" — `TA5QzGTQU_U.txt`

> "we have to have skill task compatability checks" — `TA5QzGTQU_U.txt`

> "this defaults may be in conflict with the required AP API with the calculation with the output format with the file path with the installed dependencies with the runtime environment or with the available budget" — `TA5QzGTQU_U.txt`. That enumeration is the `requirements` axis of this gate's request grammar, field for field.

> "307 confirmed cases of skill induced agent failures" — `TA5QzGTQU_U.txt`. 125 functional (24 wrong artifact locations, 13 environment mismatches) and 182 high-confidence efficiency regressions, all from skills that had already passed a relevance filter.

> "the frozen LLM receives the final accepted skills directly in its prompt from the harness" — `sHeITqLW2BY.txt`. Admission is a harness act, which is why the gate lives in the harness and emits a named reasons list rather than a bare refusal.

`C-Mk88De36M.txt` (residual-stream tool-use propensity) is the deliberate **counter-example**: a model-level `alpha` knob raises or suppresses tool calls with no adjudication whatsoever. The admission decision must be deterministic code, which is why this sits beside `guard-dangerous-commands.sh` and `guard-secret-write.sh`.

## Contract

JSON request on stdin, `set -uo pipefail`, validator embedded in the hook and run by `/usr/bin/python3 -c` (same loader shape as `rail-registry-four-way-gate.sh`, loaded with `read -r -d ''` so apostrophes in the heredoc body cannot break bash's scanner). Exit code **is** the class:

| exit | verdict | meaning |
|---|---|---|
| 0 | `PREFILTER_CLEAR` / `NO_REQUEST` | every candidate cleared both checks — a prefilter verdict, **never PASS** |
| 1 | `GATE_MALFORMED` | payload unparseable or outside the condition grammar (fail CLOSED) |
| 2 | `REFUSED:MISSING_PRECONDITION` | cannot be adjudicated: slot absent, no predicate declared, condition names an unsupplied field, unparseable band, counterpart absent |
| 3 | `REFUSED:UNSATISFIABLE_PRECONDITION` | complete, evaluable, and **false**: condition fails vs `x_t`/`g`, band provably empty, live version violates the band |
| 4 | `REFUSED:CONFLICT` / `PREFILTER_DROPPED:CONFLICT` | applicable but incompatible: a carried default contradicts a binding requirement, or a **present** counterpart is outside the band |

Three disciplines make it more than a validator:

- **The classes never collapse.** Absent counterpart → `MISSING:counterpart.rig-doctor` (supply the dependency). Present-but-out-of-band counterpart → `CONFLICT:counterpart.rig-capabilities` (refuse the pairing). Same target, different remedy, different exit code.
- **`PASS` is unconstructible.** The verdict vocabulary is closed and regex-asserted in `emit()`, and stdout always carries `"never_pass": true`.
- **A pack that filtered nothing looks different.** `drop_count` is always emitted and `filtered_nothing: true` lands in pack provenance, so a zero-drop prefilter is distinguishable from one that never ran.

Mixed packs keep their class: the *first* refusal in candidate order sets the exit code, so a partially-loadable pack still exits non-zero without laundering `CONFLICT` into a generic invalid.

## The nine fixtures (all four directions proven, 2026-09-02)

`done_when` carries 11 items — nine `cmd:` fixtures plus `cmd:test -x …` and `file:…` as separate entries. `done_tests.run_asset` ANDs them, so the asset cannot look green while any class is blind. Note `ran=11, unrunnable=0, unrunnable_forms=[]` on every run below: nothing is silently skipped.

| fixture | payload shape | live state | raw hook exit | fixture asserts |
|---|---|---|---|---|
| `pack_compatible` | 2 candidates, predicates hold, defaults `build/reports/` + `output-format json` + `budget-tokens 1800`, counterpart band `>=2.0,<3.0` | python 3.13.1, npm, docker, rig-capabilities 2.4.1 | **0** `PREFILTER_CLEAR`, `"filtered_nothing": true` | `rc -eq 0` + both greps |
| `pack_missing_applies_when` | candidate with `activation` + `defaults`, **no `applies_when` key** | npm, docker, 3.13.1 | **2** `MISSING_PRECONDITION:slot.applies_when` | `rc -eq 2` |
| `pack_missing_state_field` | condition on `container_runtime`; state omits it | npm, python only | **2** `MISSING_PRECONDITION:state.container_runtime` | `rc -eq 2` |
| `pack_missing_counterpart` | asset needs `rig-doctor`; run carries only `rig-capabilities` | npm, 3.13.1 | **2** `MISSING_PRECONDITION:counterpart.rig-doctor` | `rc -eq 2` |
| `pack_unsat_all` | 3 candidates, each one false condition; **no `state` key** — read via `$RIG_PRELOAD_STATE` | `state_live.json`: npm, docker, python **3.9.6** | **3** `"loadable": 0`, `"drop_count": 3` | `rc -eq 3` + both greps |
| `pack_band_empty` | band `"<3.0,>=3.12"` — provably empty | python 3.13.1 | **3** `UNSATISFIABLE_PRECONDITION:version_band.python_version` | `rc -eq 3` |
| `pack_conflict_artifact_path` | the study's named failure: skill mandates `dist/`, task bound to `build/`; 2nd candidate compatible | npm, docker, 3.13.1 | **4** `CONFLICT:artifact-path`, `loadable_ids: ["vite-bundle-audit"]` | `rc -eq 4` |
| `pack_conflict_counterpart` | `rig-capabilities` present at **1.4.0**, asset needs `>=2.0,<3.0` | npm, 3.13.1 | **4** `CONFLICT:counterpart.rig-capabilities` | `rc -eq 4` |
| `pack_malformed` | one condition carrying two operators | npm, 3.13.1 | **1** `"verdict": "GATE_MALFORMED"` | `rc -eq 1` |

Observed refusal text (verbatim, stderr of the artifact-path fixture):

```
PRELOAD-GATE: CONFLICT:artifact-path webpack-bundle-audit — the skill mandates dist/, this task is bound to build/ (path-prefix)
PRELOAD-GATE: PREFILTER_DROPPED:CONFLICT — 1 of 2 asset(s) refused pre-load; this is a prefilter verdict, never PASS
```

and of the zero-loadable pack built against the live-state seam:

```
PRELOAD-GATE: UNSATISFIABLE_PRECONDITION:state.repo_kind cargo-migration — condition #0 wants repo_kind=cargo, live repo_kind=npm
PRELOAD-GATE: UNSATISFIABLE_PRECONDITION:version_band.python_version modern-python-only — live python_version=3.9.6 violates the asset's band >=3.11,<4
PRELOAD-GATE: UNSATISFIABLE_PRECONDITION:state.container_runtime podman-compose-run — condition #0 wants container_runtime=podman, live container_runtime=docker
PRELOAD-GATE: REFUSED:UNSATISFIABLE_PRECONDITION — 3 of 3 asset(s) refused pre-load; this is a prefilter verdict, never PASS
```

Negative controls also run clean: empty stdin → `NO_REQUEST` exit 0; `defaults: {}` is a legal declaration while `applies_when: []` is not (an empty predicate set can never yield `alpha == 1`).

## Plant-failure proof (every class proven falsifiable, 2026-09-02)

Each plant edits only the guard that names the class, runs `./bin/rig-capabilities test skill-preload-precondition-gate.sh`, then restores. Baseline and post-restore runs: **exit 0, `pass=true`, `ran=11`, `unrunnable=0`**.

| plant | guard removed | `test` exit | `pass` | items that went RED |
|---|---|---|---|---|
| 1 | `if empty:` → `if empty and False:` (declaredness) | **1** | false | `pack_missing_applies_when` |
| 2 | `if True: continue` after `label =` (conditions can never fail) | **1** | false | `pack_unsat_all`, `pack_band_empty` |
| 3 | `if not holds:` → `if False and not holds:` and `elif not band_satisfies(actual, clauses):` → `elif False:` | **1** | false | `pack_conflict_artifact_path`, `pack_conflict_counterpart` |

Each plant reddened exactly its own class and left the other classes green — the checks are independent, not three views of one flag.

## Why this shape is the right one

- It closes the estate's only remaining admission gap. `skill_contract.py` asks "did it declare C?"; this asks "does C hold **here, now, for this task**?" and adds the leg the harmful-skills study names and RIG had in neither place: default-vs-requirement compatibility.
- The three exit codes are the deliverable. A single `invalid` would reproduce the exact failure the study measured — 24 wrong-artifact-location and 13 environment-mismatch cases were all "rejected" for reasons nobody could act on. `MISSING` means supply the input, `UNSATISFIABLE` means the state is wrong for this asset, `CONFLICT` means this pairing is unsafe.
- Path matching encodes the study's dominant case as an invariant: a required path must be a **prefix** of the skill's default, so a skill that mandates `dist/` cannot satisfy a task bound to `build/` even though both strings look "close".
- The grammar is closed and fails CLOSED: a condition with two operators exits 1 rather than silently picking one. An ambiguity that loads a skill is worse than a pack that refuses to run.
- `$RIG_PRELOAD_STATE` keeps the state axis honest: the `pack_unsat_all` fixture carries **no** `state` key, so the green run proves the harness seam is real and not fixture-only evaluation.

## Ceiling and wiring status (honest)

- **Declared state, not observed state.** The gate evaluates what the request (or `$RIG_PRELOAD_STATE`) declares. It cannot itself probe the repo, the container, or an installed version — a state document that lies will admit an asset this gate should drop. Real adversarial robustness needs the harness to *measure* `x_t` before calling this hook.
- **Band emptiness is pairwise, not a solver.** Lower/upper contradiction and pinned-`==` consistency are detected; `>=1,<2,==3` is caught via the pin, but a band that is non-empty with no installed satisfier is only reported through the live-version check, i.e. the same exit class by a different route.
- **Unwired.** Hooking this into a session-start / pre-injection point is a **Gate-D action staged separately**; it ships unwired. The saving it protects is real but unbanked: the study's 182 high-confidence efficiency regressions all came from skills a relevance filter had already admitted (114 of them excessive procedure), and no always-loaded token is recovered until something refuses a body before injection.
- The gate sees the declaration, not the body: an asset whose `defaults` understate what its instruction actually forces will pass compatibility. Closing that needs the skill body parsed into requirements, which is `skill_contract.py` territory, not a pre-load hook's.
