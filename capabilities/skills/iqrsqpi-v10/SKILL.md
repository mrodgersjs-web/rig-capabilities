---
name: iqrsqpi-v10
description: "RIG doctrine — IQRSQPI v10 as an executable stdlib runtime, not a prose ritual. The seven canonical stages (Intent, Question, Research, Solution, Quality, Proof, Integrate) are validated by rig_capabilities/iqrsqpi_v10.py: normalize_stage collapses every harness vocabulary onto the canonical order, run_pass refuses a pass whose verifier is its generator, refuses any reached stage whose required artifact is not on disk under .context/iqrsqpi/<walk_id>/, and refuses any number stated without a source. Use when a walk must be recorded and audited against code-enforced stage order. For the engine-driven gated loop use iqrsqpi-v11; for the fractal self-verifying loop use iqrsqpi-v20 (see Relationship to v11/v20)."
allowed-tools: Bash Read Grep
owner: rig-intelligence
domain: Agent engineering / operating doctrine
status: Stable
verified_by: jake
verified_on: 2026-09-01
outcome: agent-engineering: The seven-stage IQRSQPI pass is decided by code — stage order, per-stage artifacts, sourced numbers, and Builder≠Checker — never by the walker's own narration
done_when:
  - file:rig_capabilities/iqrsqpi_v10.py
  - grep:rig_capabilities/iqrsqpi_v10.py:verifier_is_generator
  - cmd:python3 -c "from rig_capabilities.iqrsqpi_v10 import normalize_stage as n; assert n('I')=='Intent' and n('I2')=='Integrate' and n('I5')=='Integrate' and n('Q2')=='Quality'"; test $? -eq 0
quality_floor: 0.6
---

# IQRSQPI v10 — the Executable Seven-Stage Pass

Run the IQRSQPI pass against `rig_capabilities/iqrsqpi_v10.py`. The module is the
contract; this file is the operator's map to it. A stage that cannot point at the
runtime's verdict is not a stage that happened.

The module refuses two things by construction: it never executes a model or a
subprocess, and it never reads outside `repo.root`. The certify `stage_order`
gate is hermetic (law L1) — it reads one committed fixture,
`tests/fixtures/fable2031/iqrsqpi-run.json`, and nothing else.

## The runtime surface

| Call | Contract |
|------|----------|
| `normalize_stage(token)` | Collapse one stage token to its canonical stage. Raises `StageError('stage_token_empty')` / `StageError('unknown_stage_token:…')` — an unknown token never lands on a guess. |
| `stage_order_ok(sequence)` | `(ok, reason)`: the tokens normalize to a strict in-order subsequence of `STAGES`. No backward steps, no repeats. Never raises — a bad token is a `False` with the reason, because a gate must report, not blow up. |
| `run_pass(repo, walk_id, stages, *, verifier, generator)` | Validate one recorded pass. Read-only; raises `StageError` with the reason code. |
| `gate_stage_order(repo)` | The hermetic certify gate over the committed fixture. |

Reason codes `run_pass` raises: `verifier_is_generator`,
`verifier_and_generator_must_be_named`, `stage_out_of_order:<detail>`,
`artifact_missing:<name>`. A walk directory that does not exist at all is
reported as the first artifact its first reached stage demands — no separate
code, no silence.

## The alias law

Two vocabularies describe the same seven stages. `normalize_stage` collapses the
vocabulary, never the order.

Canonical (each name is a valid token for itself): `Intent, Question, Research,
Solution, Quality, Proof, Integrate`.

| Alias(es) | Resolves to |
|-----------|-------------|
| `I`, `I1`, `intake` | Intent |
| `Q`, `Q1`, `question` | Question |
| `R`, `research` | Research |
| `S`, `solution`, `synthesize` | Solution |
| `Q2`, `quantify` | Quality |
| `P`, `produce` | Proof |
| `I2`, `I5`, `iterate` | Integrate |

The law: `I` resolves to Intent, but `I2` and `I5` resolve to Integrate, and
`Q2` to Quality. Resolution is whole-token and case-insensitive (trimmed, then
exact lookup on a table whose canonical names are loaded first and aliases
applied on top), so no token is ever swallowed by a prefix of itself — the
suffix **is** the stage, not noise. A longest alias is never beaten by its own
shortest prefix: `I2` is a key of its own, not `I` with debris.

## A pass may not name its own verifier

`run_pass` raises `StageError('verifier_is_generator')` the moment
`verifier == generator`, and `verifier_and_generator_must_be_named` when either
is blank. This is the Builder≠Checker law in code: the entity that walked the
stages holds no authority to certify them. A recorded pass that cannot name two
different parties does not exist.

## Artifacts: no stage is "reached" without its document

A v10 walk lives at `.context/iqrsqpi/<walk_id>/` and carries up to four
artifacts, in write order: `00-intake`, `01-reality`, `02-decision`, `proof`
(json, markdown, or a directory holding a file). Each reached stage demands:

| Stage | Must find on disk |
|-------|-------------------|
| Intent | `00-intake` |
| Question | `00-intake`, `01-reality` |
| Research | `01-reality` |
| Solution | `02-decision` |
| Quality | `02-decision`, `proof` |
| Proof | `proof` |
| Integrate | `proof` |

Each artifact has exactly one owner stage (`ARTIFACT_OWNER`: intake→Intent,
reality→Research, decision→Solution, proof→Proof). A stage may **demand** a
document it does not own — Question must open the reality document Research
wrote — but a number inside it is audited exactly once, against its owner. A
claim states a number (typed value, numeric string, or a digit embedded in the
claim text) without naming a `source`: the stage is refused. A number without a
source is a fabrication however it arrives.

The walk manifest (`run.json`, schema `rig.iqrsqpi.run.v1`) records `stages[]`,
each with its `stage` token, `artifacts`, and `claims[{claim, value?, source}]`;
claims attributed to a stage are audited against that stage too.

## Commands

```bash
# Hermetic stage-order gate against this repo:
./bin/rig-capabilities certify --only stage_order        # exit 0 green, 1 red

# Plant-failure proof — green -> planted RED -> restored green:
./bin/rig-capabilities self-test --only stage_order

# Validate one recorded pass (two named parties, in-order tokens):
python3 - <<'PY'
from rig_capabilities.iqrsqpi_v10 import run_pass
from rig_capabilities.catalog import Repo
print(run_pass(Repo('.'), 'fable-2031',
               ['I', 'Q', 'R', 'S', 'Q2', 'P', 'I2'],
               verifier='gpt-56', generator='claude-fable-5-1'))
PY
```

Honest current state: the live walk `.context/iqrsqpi/fable-2031/` records only
`00-intake` (Intent reached, artifact on disk). Running the full seven-token
pass against it today raises `artifact_missing:01-reality` — that is the
artifact law working, not a defect. Record the artifact (or the stages that
genuinely have one); never create the artifact to silence the error.

## Relationship to v11/v20

Three IQRSQPI skills coexist, and this is the honest map:

- **`iqrsqpi-v10` (this skill)** — the **stdlib gate runtime**:
  `rig_capabilities/iqrsqpi_v10.py` plus the `stage_order` certify gate. No
  engine, no `rig-loop`, no subprocesses. It decides whether a recorded pass is
  in order, has its artifacts, and has sourced numbers.
- **`iqrsqpi-v11`** — a loop-skill shipped by sibling branches: the gated loop
  driven by the `rig-loop` engine (`loop.yaml`, `closing_loop`, kill switch).
- **`iqrsqpi-v20`** — the fractal self-verifying loop (slices, cross-family
  verifier dispatch), also engine-driven.

v10 does **not** supersede v11 or v20, and this skill does not touch their
files. All three may be installed at once; **which one lives at which harness
root (`~/.claude/skills`, `~/.codex/skills`, `~/.hermes/skills`, …) is a human
decision**, revisited when the fleet policy changes. Where a harness root
carries an older single-pass prose copy of `iqrsqpi-v10`, this canonical
runtime is what the repo's gates audit; distribution is the orchestrator's
serialized pass, not this skill's.

## Rationalizations to Reject

| Shortcut | Why It's Wrong |
|----------|----------------|
| "The stages happened in my head, order need not be recorded" | `stage_order_ok` reads the recorded tokens; an unrecorded walk never happened. |
| "`I2` is basically `I`, same letter" | The suffix is the stage. Reading `I2` as `I` turns Integrate into Intent and launders an unfinished walk into a finished one. |
| "Same agent built and verified, who's checking" | `verifier_is_generator` exists for exactly this. Two named parties or no pass. |
| "64 harnesses — write the number, cite the dir later" | A number without a `source` on disk is refused at audit time. Source first, then the number. |
| "Add the missing artifact file so `run_pass` goes green" | The runner validates a walk that already happened. Fabricating an artifact to silence it is the walk laundering itself into "done". |
| "v11 exists, so v10's gate is redundant" | v11's engine and v10's gate check different things on different data. The `stage_order` certify gate is plant-proven; nothing inherits it. |

## Success Criteria

- [ ] Every stage token in a recorded walk resolves through `normalize_stage` (no hand-mapped stages)
- [ ] `verifier != generator`, both named
- [ ] Every reached stage's demanded artifacts exist under the walk dir before the stage is claimed
- [ ] Every numeric claim names a source resolvable on disk
- [ ] `./bin/rig-capabilities certify --only stage_order` exits 0, and `self-test --only stage_order` shows green → RED on plant → green on restore
