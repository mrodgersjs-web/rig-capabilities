---
name: s1gate
description: "The RIG System-1 Gate. A governed decision layer on TypeSafe's System One model (Jev) that scores artifacts against calibrated rubrics and returns PASS / ESCALATE / BLOCK. Use whenever a stage transition needs a quality bar: a plan before building, a diff before merging, a post before publishing, a comment before sending, a lead before routing. Also use when deciding whether a judgment belongs in code, in a System 1 model, or in a System 2 model."
tags: [rig, doctrine, gates, verification, jev, typesafe, system-one]
metadata:
  verified: "2026-09-18 against jev-1.13.0, live API, 13 rubrics, 25 unit tests"
---

# System-1 Gate (s1gate)

## What Jev actually is

Not a chat model. A **classifier with a fixed answer set** that returns calibrated
probabilities and generates zero text. Three primitives:

| Primitive | Question shape | Returns |
|---|---|---|
| `noul` | yes/no | `noul`: probability the statement is true. **No confidence field.** |
| `choice` | one of N (up to 255) | `choice`, `probabilities` per option, `confidence` |
| `score` | rubric level 0..N (max 11 levels) | `score` (a mean), `probabilities` per level, `confidence` |

Endpoint `POST https://api.typesafe.ai/v1/systemone`, model `jev-latest`,
key in keychain item `com.rig.env.TYPESAFE_API_KEY`. **Measured 202-910ms** per call
from Denver on 2026-09-18.

## Why it earns its place in RIG

RIG law is *deterministic before agentic*. Jev is the missing rung between them:
the judgment is probabilistic, but it is consumed by an `if` statement **in our code**.
"Agent proposes, code disposes" becomes literal. A whole class of "spin up an agent to
look at this" collapses into a threshold check that costs a fraction of a cent.

It does **not** replace a System 2 model. It decides *what deserves one*.

## The six laws

1. **Fail closed.** Provider error, timeout, or unparseable answer is a BLOCK.
   Silence is not consent. An undecidable rule ESCALATES; it never passes quietly.
2. **Confidence is a second axis.** The first live probe returned `score: 1.39` off a
   distribution split `0.46 / 0.42` across *opposite ends* of the rubric, with
   `confidence: 0.0`. The mean was noise. Every Score/Choice rule is therefore also
   subject to a confidence floor. Below the floor: ESCALATE, never PASS.
   Noul answers carry no confidence — absence must not be read as zero.
3. **No uncalibrated enforcement.** A rubric ships `calibrated: false` and runs
   **advisory**: it annotates, it cannot BLOCK. Only `s1gate calibrate`, measuring
   against labelled decisions, flips it to enforcing.
4. **Optimise against the false block, not accuracy.** A gate that lets a bad artifact
   through costs one bad artifact. A gate that blocks good work **gets switched off**,
   and then you have no gate. Default operating point: maximise recall subject to
   `false_block_rate <= 0.05`. If no threshold qualifies, the honest answer is
   "this gate is not ready" — do not ship it.
5. **The gate never grades its own homework.** The artifact's author may see the rubric
   questions; it never sees the thresholds or the calibration set.
6. **A machine PASS is not an authorisation.** Gate-D is unchanged. `never_auto: true`
   rubrics (Lane C) downgrade even a clean PASS to ESCALATE, because the decision was
   always a human's.

## Evidence that the design is load-bearing

On first live run, 4 adversarial artifacts were caught and **3 of 4 good artifacts were
false-blocked**:

- a first-person audit post flagged `unverified_claim 0.81` — the question demanded an
  external citation for the author's own measurement. *Rubric wording defect.*
- an agreeing comment flagged `contains_pushback 0.41` against a 0.35 threshold.
  *Threshold too tight.*
- an auth-boundary diff escalated at `risk 2.7`. *Correct by design, not a defect.*

Both defects were reworded, re-tested, and recorded in each rubric's `notes` field with
the decision id that exposed them. **Had these gates shipped enforcing, they would have
blocked good work on day one.** That is what law 3 exists to prevent.

## Usage

Three verbs. Reach for them in this order: **rank** (no calibration needed), **improve**
(no calibration needed), **check** (blocks only once calibrated). See INTEGRATION.md
for the routine-by-routine map.

```bash
# make the number DO something
cat draft.md | rig-s1gate improve post.linkedin --stdin --context "Lane B, author audited 9 automations" --max 3
rig-s1gate rank comment.linkedin --file candidates.txt        # candidates separated by a '---' line

# inspect and measure
rig-s1gate list                                  # all rubrics + enforcing/advisory mode
rig-s1gate show code.diff                        # questions, rules, calibration record
cat diff.txt | rig-s1gate check code.diff --stdin --subject PR-482
rig-s1gate check post.linkedin --file draft.md --json
rig-s1gate label 42 bad                          # build the calibration corpus
rig-s1gate calibrate code.diff --signal weakened_test.noul --write
rig-s1gate stats code.diff
```

Exit codes are the contract — hooks and CI read these, not stdout:
`0` PASS · `1` BLOCK (enforced) · `2` ESCALATE · `3` usage/config error.
An advisory rubric never returns 1.

## Rubric packs

| Rubric | Stage | Lane |
|---|---|---|
| `plan.readiness` | plan | is this good enough to *start* building |
| `code.diff` | verify | the gate an agent cannot walk past |
| `code.review` | verify | cheap broad screen → shortlist for System 2 |
| `api.backend` | build | contracts, failure paths, destructive guards |
| `ui.design` | build | states, accessibility, primary action |
| `gtm.lead` | distribute | fit band + motion routing |
| `email.outreach` | distribute | outbound is irreversible |
| `post.linkedin` | distribute | Lane B, RIG B2B |
| `post.eden` | distribute | Lane A, personal brand |
| `post.instagram` | distribute | fitness/mindset lane |
| `comment.linkedin` | distribute | positive-only house rule |
| `nil.jacob` | distribute | **Lane C, minor, `never_auto`** |
| `signal.performance` | measure | turn "what's working" into a counted claim |

## Writing a new rubric

1. Ask **atomic** questions. "Is this good?" is unanswerable; "does the diff weaken a
   test" is answerable. Composite judgments are built in *code* by combining atomic
   scores with weights you control.
2. Prefer `noul` for anything binary — it is the cheapest and has no confidence trap.
   Use `score` only when the levels are genuinely ordered along one dimension. If a
   score comes back bimodal, the rubric is measuring two things: split it.
3. Write the question so a **good** artifact reads clean. The false-block defects above
   both came from a question that punished a legitimate pattern.
4. Every rule needs a `reason`. The reason is what a human reads at 11pm.
5. Ship `calibrated: false`. Collect labels. Measure. Then enforce.

## Where this integrates

- **Aside (the browser agent) and every other MCP harness**:
  `capabilities_s1gate` on the `rig-capabilities` server — one tool, actions
  `list / show / check / rank / improve / stats / recent / review / label /
  calibrate / selftest`. It calls the same library functions as the CLI, so a
  tool answer cannot disagree with `bin/rig-s1gate`. Guards baked in: closed
  schema, `calibrate` is dry-run only (no caller key can turn a gate enforcing),
  25-candidate and 5-iteration spend caps, provider failure comes back as
  `fail_closed` data rather than a pass, and nothing prints on stdout (that is
  the JSON-RPC channel). Ask "is it wired?" with `{"action":"selftest"}` — free,
  no API call. Tests: `tests/test_mcp_s1gate.py`.
- **Raw Jev questions outside the rubrics**: the `typesafe-jev` skill (same repo,
  symlinked into the Aside skills dir) has the request shapes that validate —
  including the one that costs everyone a 422: a `noul` takes **no** `criteria`.
- **Coding agents**: `capabilities/hooks/s1gate-stage-gate.sh` — a Claude Code / OMP
  Stop hook. Exit 2 blocks the agent and feeds the reasons back as stderr.
- **Decision log**: `~/.rig/s1gate/decisions.db`. Every call recorded with the state
  hash, answers, verdict and latency. This is both the ProofPacket and the calibration
  corpus — it is what lets a System 2 model retune System 1 later.
- **Content lanes**: gate the draft *before* it reaches Eden's scheduler or a browser
  automation. The gate advises; publication authority is unchanged.

## What this is not

Not a replacement for tests, types, or linters — it catches what those structurally
cannot see. Not a security boundary. Not an approval: a PASS from a calibrated rubric
means "the measured bar was met", never "you may publish, spend, or deploy."

## ULTRA studio packs and two schema traps (measured 2026-09-18)

`capabilities/harnesses/s1gate/rubrics/ultra.{questioning,research,forecasting,judgment,
execution,proof,learning}.json` — 37 questions, 38 rules, all `calibrated: false`. The
routing layer is `rig_capabilities/ultra_gates.py`: 10 declared gates, 11 deterministic
code checks, 8 routes, ordered **code → Jev → human**. `rig-ultra`-style consumers call
`ultra_gates.route(gate_id, state, facts, live=True)`; `live=False` returns
`offline_code_only` and `cleared: false` on purpose, so a code-only check can never be
read as a cleared gate.

Two traps that cost real debugging time, both now asserted by `tests/test_ultra_gates.py`:

1. **A `choice` question's options are a `criteria` dict of `slug -> description`**, not
   a list and not prose. Rules compare against the slug (`shape.choice == fact`). A slug
   with a space is unreachable: `attribution.choice == 'task was impossible'` parses, but
   no provider answer can ever equal it. Test: `test_rule_literals_address_declared_options`.
2. **A rule's left side is `<question>.<attr>`, exactly one dot.** An option probability
   is `source_grade.p.MED`. Written as `p.source_grade.MED` it is an unparseable string
   that `eval_condition` returns as *undecidable* — which silently escalates forever
   instead of ever firing. Test: `test_rules_parse_and_are_answerable`, which evaluates
   every rule against a synthetic answer set and asserts the result is not `None`.

Trap 2 is the general lesson: **an invalid rule is a valid string.** Syntax checks pass;
the defect only appears at first real use. Any new pack must be loaded and every rule
evaluated, not merely parsed.

Question names may not contain a dot, so the ULTRA doc names collapse to their last
token (`pm.cause_is_testable` → `cause_is_testable`) or were renamed (`q.class` → `cls`).
`dq.information` is **computed in code** (`ultra_gates.information()`: the weakest of the
14 angle classes, `None` when a class is unanswered) and is deliberately not a question —
a mean would hide the one class that is unresolved.
