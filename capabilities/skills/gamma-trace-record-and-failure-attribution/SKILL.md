---
name: gamma-trace-record-and-failure-attribution
description: >-
  Use when long-horizon agent runs must produce diagnosable failures instead of
  'the agent failed'. Every consequential step appends a fixed seven-field gamma
  trace row (believed state, skills delivered, action, observation, proposed
  state change, checker verdict, resulting state); every attempt carries exactly
  one terminal outcome. A RED attempt is then attributed to exactly one of four
  fixed components — skill_missing_or_wrong (E), state_representation_incoherent
  (W), retrieval_policy_inadequate (rho), verifier_missed (C) — citing gamma
  row-ids from that attempt's own rows. Attribution without row evidence is
  recorded as UNATTRIBUTED, never guessed, and genesis skills must cite the
  gamma rows that motivated them. validate_gamma.py enforces every clause
  mechanically: exit 2 on a field-missing row, a double- or zero-class
  attribution, a citation-less guess, an orphan step, or a provenance-less skill.
allowed-tools: Bash Read Write
owner: rig-intelligence
domain: Agent observability / failure attribution
status: Draft
outcome: >-
  agent-engineering: every consequential step is recorded as a gamma row and
  every RED attempt names exactly one responsible component with row-id
  citations — because an unattributed failure cannot be improved
done_when:
  - cmd:python3 capabilities/skills/gamma-trace-record-and-failure-attribution/validate_gamma.py capabilities/skills/gamma-trace-record-and-failure-attribution/fixtures/gamma_valid.jsonl --genesis capabilities/skills/gamma-trace-record-and-failure-attribution/fixtures/genesis_valid.md; test $? -eq 0
  - cmd:python3 capabilities/skills/gamma-trace-record-and-failure-attribution/validate_gamma.py capabilities/skills/gamma-trace-record-and-failure-attribution/fixtures/gamma_missing_field.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/skills/gamma-trace-record-and-failure-attribution/validate_gamma.py capabilities/skills/gamma-trace-record-and-failure-attribution/fixtures/gamma_attr_two_classes.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/skills/gamma-trace-record-and-failure-attribution/validate_gamma.py capabilities/skills/gamma-trace-record-and-failure-attribution/fixtures/gamma_attr_zero_classes.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/skills/gamma-trace-record-and-failure-attribution/validate_gamma.py capabilities/skills/gamma-trace-record-and-failure-attribution/fixtures/gamma_attr_without_evidence.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/skills/gamma-trace-record-and-failure-attribution/validate_gamma.py capabilities/skills/gamma-trace-record-and-failure-attribution/fixtures/gamma_unattributed_honest.jsonl; test $? -eq 0
  - cmd:python3 capabilities/skills/gamma-trace-record-and-failure-attribution/validate_gamma.py capabilities/skills/gamma-trace-record-and-failure-attribution/fixtures/gamma_valid.jsonl --genesis capabilities/skills/gamma-trace-record-and-failure-attribution/fixtures/genesis_missing_provenance.md; rc=$?; test $rc -eq 2
  - file:capabilities/skills/gamma-trace-record-and-failure-attribution/validate_gamma.py
great_example: examples/great/agent-engineering/gamma-trace-record-and-failure-attribution.md
quality_floor: 0.6
---

# gamma-trace-record-and-failure-attribution

THE LAW: **every consequential step is recorded as a fixed-schema γ row; every
failed attempt names exactly one responsible component, citing γ row-ids; a
cause the rows cannot support is written UNATTRIBUTED — never guessed.** An
unattributed failure cannot be improved: "the agent failed" prescribes
rewriting everything, which is indistinguishable from rewriting nothing.

The source names the object and the stakes. The trace is the evaluable object:
"turns here this agent harness execution into what they call here a structured evidence gamma" (F1XqqVNBa4o).
And it is what makes diagnosis local, not wholesale:
"the failed trajectory can be localized to a specific memory component" (F1XqqVNBa4o).

## The record: three row kinds, one JSONL file

### 1. `step` — seven fields, all non-null, every consequential step

| # | field | meaning |
|---|-------|---------|
| 1 | `w_t` | believed state before acting — "it records what the system believed before acting" (F1XqqVNBa4o) |
| 2 | `e_t` | skills/cards actually delivered to context this turn; `[]` is legal and is itself evidence (a routing miss looks identical to a knowledge gap in any score that lacks this field) |
| 3 | `a_t` | the action taken |
| 4 | `o_t` | the environment observation |
| 5 | `proposal` | the proposed state change, stated before anyone may claim it |
| 6 | `checker_verdict` | `accept` \| `reject` against external evidence — the state store is a proposal log until a verdict lands: "the working memory maintains a verified task state all the time" (F1XqqVNBa4o) |
| 7 | `w_next` | resulting state — "which state change was proposed as a result of the observation of the environment feedback" (F1XqqVNBa4o) |

Plus `row_id` (globally unique), `run_id`, `t` (monotone per run). Seven fields
non-null is the done-test's first assertion: a row missing `o_t` is not a
lighter record, it is a hole in the causal chain — the exact row a future
attribution would need.

### 2. `attempt` — the terminal outcome, exactly one per `run_id`

"an attempt is a complete run of the agent on a single task" (1Tlv7XNsPy8):
mint the run at task receipt; it terminates at exactly one of `submitted` /
`verified` / `limit` / `failed` (closed enum) with one binary `reward`. The run
id stamps "every more call, every tool-related event, and any final reward"
(1Tlv7XNsPy8 — caption wording). Validator invariants: one attempt row per
run, every step's `run_id` resolves (orphan count 0), reward ∈ {0,1}.

### 3. `attribution` — exactly one class per RED run, citing rows

The class set is **fixed by design**, one component each:

| class | component | the source's own words |
|-------|-----------|------------------------|
| `skill_missing_or_wrong` | E (skill cards) | "Was it the wrong skill?" (F1XqqVNBa4o) |
| `state_representation_incoherent` | W (working-memory spec) | "Was it that it was not a coherent state representation?" (F1XqqVNBa4o) |
| `retrieval_policy_inadequate` | ρ (delivery policy) | "the retrieval policy for our particular skill selection was not adequate for the complexity of the job" (F1XqqVNBa4o) |
| `verifier_missed` | C (checkers) | the checker accepted progress the evidence did not support — the fourth question the four-component split forces (F1XqqVNBa4o; component named in-quote: "the failed trajectory can be localized to a specific memory component") |

Rules, all enforced by `validate_gamma.py`:
- a RED run carries **exactly one** attribution row with **exactly one** class —
  two classes (`attribution_class_count`) is "rewrite everything" wearing a
  class name; zero is `red_run_unattributed`;
- the named class must cite ≥1 `step` row **of its own run** — a class citing
  nothing is `attribution_without_evidence`; cross-run and dangling cites die;
- a GREEN run gets no attribution (`attribution_of_green_run`): the artifact
  for a green lesson is a card, not an attribution.

### UNATTRIBUTED is a first-class honest terminal state

**Attribution without evidence is written `UNATTRIBUTED`, never guessed.** The
moment "pick one of four" outruns the rows, the diagnosis is noise that
authorizes a patch. `["UNATTRIBUTED"]` is legal iff it carries **no citations**
and **names what is missing** — which rows were read and why none discriminates
a cause (see `fixtures/gamma_unattributed_honest.jsonl`, exit 0). A named class
with zero citations is the guess in disguise and exits 2. A run that stays
UNATTRIBUTED forever is itself a signal: the trace is not discriminating, which
is a W/ρ finding about the harness — but the validator never upgrades the
label for you.

### Genesis provenance

"any validated lesson from the experience becomes simply a reusable external skill" (F1XqqVNBa4o).
And "the meta-agent distills here a general procedure, and this might be a new or revised skill" (F1XqqVNBa4o).
A skill born that way must be deletable
by evidence: `--genesis SKILL.md` requires a non-empty `source:` **and** a
`gamma_provenance:` field whose cited row-ids all exist in the trace. No
provenance → exit 2 → the skill is not admissible; a card nobody can trace to a
failure is a card nobody can decide to delete.

### The fragment axis

Agent Lightning v1.0 deliberately stopped at the terminal reward:
"do not let fragmentation distort you the terminal reward function" (1Tlv7XNsPy8).
The open axis it named, left unsolved by design:
"which fragment actually causes not a success, which fragment is doing the real work to understand and to correct it" (1Tlv7XNsPy8).
γ plus attempt identity lets you actually compute it: correlate per-step
`checker_verdict` rejects and step failures against the attempt's terminal
reward, and when you aggregate across attempts keep the paper's own discipline:
"give every attempt equal total training weight, regardless of how many fragments or tokens it produced" (1Tlv7XNsPy8).
The unit of weighting is the attempt; call counts are a cost axis, never a vote.

## Workflow

1. **Mint** `run_id` at task receipt. Append one `step` row per consequential
   step — proposal and verdict included; skip neither even when both are
   boring. Write the `attempt` row at termination.
2. **Validate** before diagnosing anything: exit 0 or the trace is the failure.
3. **Attribute** on reward 0: read the rows, name one class, cite rows of that
   run, and exonerate the other three *by their rows* — that sentence is what
   separates an attribution from a hunch (see the valid fixture's evidence
   text). If the rows cannot discriminate, write UNATTRIBUTED with the named
   gap.
4. **Patch one component.** The attribution names the file class to edit (a
   card, the state schema, the routing rule, or the checker) — never
   "rewrite everything".
5. **Genesis** a new skill from the patch only with `source:` +
   `gamma_provenance:` citing the motivating rows, validated via `--genesis`.
6. **Correlate** across runs: per-attempt equal weight; step-failure rate vs
   terminal reward per class is the only honest input to the next improvement
   round.

## Commands

```bash
# GREEN: valid trace + provenanced genesis skill
python3 capabilities/skills/gamma-trace-record-and-failure-attribution/validate_gamma.py \
  capabilities/skills/gamma-trace-record-and-failure-attribution/fixtures/gamma_valid.jsonl \
  --genesis capabilities/skills/gamma-trace-record-and-failure-attribution/fixtures/genesis_valid.md   # exit 0

# RED (exit 2, every violation named): try the planted fixtures —
#   gamma_missing_field · gamma_attr_two_classes · gamma_attr_zero_classes
#   gamma_attr_without_evidence · genesis_missing_provenance
# Honest UNATTRIBUTED exits 0 and echoes the gap it refuses to paper over:
python3 .../validate_gamma.py .../fixtures/gamma_unattributed_honest.jsonl   # exit 0
```

Exit codes: `0` valid · `2` any violation (all printed, none swallowed). No
other code is ever emitted. The five planted fixtures are permanent regression
cases.

## RIG delta (the exact gap this attacks)

- ProofPacket (section "PROOF PACKET SHAPE" in `capabilities/loops/doer-checker-validator.md`)
  binds claim → commands → exit codes **per artifact claim**; there is no
  per-step record coupling state + delivered skills + action + observation +
  checker verdict.
- The same loop's failure handling routes a RED with "if FAIL → escalates to Jake-direct + Mike (Telegram)"
  (verbatim from `capabilities/loops/doer-checker-validator.md`) without ever
  naming the responsible component — escalation without attribution re-debates
  the artifact instead of patching the component.
- `rlm_step_record` (Jake PAI MCP surface) logs action/tool/result/duration per
  step, coupled to no checker verdict and no attempt reward; grepping this
  repo's `capabilities/` tree for a γ schema returns nothing (checked
  2026-09-02) — recording existed, the coupling did not.
- `capabilities/harnesses/mh-01-skill-genesis-session.yaml` seeds genesis from
  a declared need (`harness_tuple: H_skillgenesis(need, math_claim, done_test,
  planted_failure, ship)`) and carries no `source:`/`gamma_provenance:`
  requirement — genesis from a diagnosed failure, the source's actual order of
  operations, was structurally unavailable.

## Limitations (stated, not smoothed)

- **The class set is fixed by design**: a fifth failure kind (the "my ontology
  is insufficient" failure the source itself flags as the harder question)
  will be **misfiled rather than named**. UNATTRIBUTED is the only honest
  escape hatch this schema grants, and it escapes to *no patch*, not to a
  fifth class.
- Attribution quality depends on the diagnosing model. The validator proves an
  attribution is single, class-legal, and row-cited — it cannot prove the
  class is *correct*; a confident wrong attribution survives every check.
- The classes are memory components (E/W/ρ/C); a harness without separate ρ or
  C objects must map them onto whatever routing/checking it does have — the
  mapping is interpretation, and per-attempt reward is binary, so fragment
  correlations are per-run rates over few samples, not significance.
- The transcripts are auto-captions; every quote above is a verbatim substring
  of the transcript files (14/14 verified 2026-09-02, control pattern
  confirmed absent), including caption artifacts like "every more call".

## Sources (verified)

- Videos: `.context/discover-ai/tran`,
  `.context/discover-ai/tran` — quote ground truth.
- Papers (verified in `link-verdicts.json`): arXiv:2608.24876 — Recursive
  Experiential-Working Memory Evolution for Long-Horizon Agent Harnesses;
  arXiv:2608.17528 — Agent Lightning v1.0: Towards Harnessed Agentic RL.
- Repo (`exists: true`, Apache-2.0): `Gen-Verse/Recuris`.
