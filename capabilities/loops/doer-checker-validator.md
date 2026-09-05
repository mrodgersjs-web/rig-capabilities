---
outcome: "agent-engineering: the Validator answers with a typed rig.verifier.v1 record — closed six-label vocabulary, evidence that names the claim it bears on, repair tuples with a route, recorded independence, k-of-n attempts under recorded conditions, a named falsifier, a confidence with a basis — and an incomplete response is NOT-A-VERDICT: the loop does not close and the response routes to the grader that wrote it, never to the Doer"
done_when:
  - file:capabilities/loops/doer-checker-validator.md
  - file:capabilities/loops/verifier_contract_check.py
  - cmd:python3 capabilities/loops/verifier_contract_check.py check capabilities/loops/doer-checker-validator.md; test $? -eq 0
  - cmd:python3 capabilities/loops/verifier_contract_check.py self-test capabilities/loops/doer-checker-validator.md; test $? -eq 0
  - cmd:python3 capabilities/loops/verifier_contract_check.py plant capabilities/loops/doer-checker-validator.md schema_key; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/loops/verifier_contract_check.py plant capabilities/loops/doer-checker-validator.md router_row; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/loops/verifier_contract_check.py plant capabilities/loops/doer-checker-validator.md law_line; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/loops/verifier_contract_check.py plant capabilities/loops/doer-checker-validator.md marker_renamed; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/loops/verifier_contract_check.py plant capabilities/loops/doer-checker-validator.md slots_declaration; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/loops/verifier_contract_check.py plant capabilities/loops/doer-checker-validator.md labels_declaration; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/loops/verifier_contract_check.py plant capabilities/loops/doer-checker-validator.md negative_declaration; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/loops/verifier_contract_check.py plant capabilities/loops/doer-checker-validator.md route_consumers; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/loops/verifier_contract_check.py report tests/fixtures/fable2031/verifier-report-clean.json; test $? -eq 0
  - cmd:python3 capabilities/loops/verifier_contract_check.py report tests/fixtures/fable2031/verifier-report-looks-good.json; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/loops/verifier_contract_check.py report tests/fixtures/fable2031/verifier-report-same-family.json; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/loops/verifier_contract_check.py report tests/fixtures/fable2031/verifier-report-single-run.json; rc=$?; test $rc -eq 2
great_example: examples/great/agent-engineering/doer-checker-validator.md
quality_floor: 0.6
---

# 3-Tier Quality Gate Architecture — DOER / CHECKER / VALIDATOR

**Owner:** Jake PAI
**Date:** 2026-07-05 · **Revised:** 2026-09-02 (verifier output contract)
**Status:** DESIGN — building 5+ cron jobs to enforce

After every build cycle, no artifact ships until **three independent agents** each inspect it. This is the
**maker-never-grades doctrine** applied as a fleet, not a single verifier.

**The 2026-09-02 delta:** the loop said the Validator must be independent and that evidence decides. It never
said what a validator's *answer* has to contain — so a Validator could return "looks good" and the loop closed
on an opinion. Below, the Validator's output is a typed record with required slots, a closed outcome
vocabulary with named consumers, and one law: **an incomplete verdict is not a verdict and the loop does not
close on it.**

---

## THE THREE ROLES

### 🛠️ DOER — the builder
- Produces artifacts (code, scrapes, posts, proposals, designs)
- Runs on the build cron lane
- Writes proof of what it did (hashes, gates passed)
- **Does NOT grade itself**

### 🔍 CHECKER — the spec inspector
- Reads the Doer's proof
- Runs the **mechanical / syntactic** checks: did the file exist? does it parse? does it lint? does it import? does the schema match?
- Fast, deterministic, no LLM in the loop (or minimal LLM)
- Returns PASS/FAIL with concrete errors
- **Independent of the Doer** — runs in its own context window
- Its PASS is an **input** to the Validator, not a gate. A green Checker over the wrong artifact is exactly
  what the Validator exists to catch.

### ⚖️ VALIDATOR — the semantic / business-judgment inspector
- Reads the Checker's PASS report + the Doer's proof
- Runs the **semantic** checks: does the code do what it claims? does the post match Mike's voice? does the GTM lead match ICP? does the price change violate guardrails?
- Slower, often LLM-backed
- **Returns a typed `VerifierReport` (`rig.verifier.v1`) — never a sentence.** `PASS/WEAK/FAIL/CRITICAL with
  citations` is retired: it is a severity adjective standing in for a finding, and it collapses a near-miss, a
  regression and an evaluator gap into the same red.
- **Independent of both Doer and Checker** — and independence is a **recorded predicate**
  (`independence.validator_model_family != doer_model_family` plus a distinct evidence route), not the prose
  "separate model if needed". See [INDEPENDENCE](#independence-is-a-recorded-predicate-not-a-vibes-check).

---

## THE VALIDATOR OUTPUT CONTRACT — `rig.verifier.v1`

A verdict is a record. Seven slots are **required**; the loop's closing condition is that all seven are
present and well-formed, not that the Validator felt comfortable.

| # | Slot (JSON key) | What it must contain | What it replaces |
|---|---|---|---|
| 1 | `"verdict"` | Exactly one label from the closed vocabulary below, computed over the task, the **full trajectory**, the **workspace delta**, the test evidence and the policy trail — not over the Doer's `self_report` | `PASS/WEAK/FAIL/CRITICAL`, `looks good` |
| 2 | `"evidence_refs"` + `"bears_on"` | One entry per **load-bearing claim** in the Doer's proof: `ref` = an addressable artifact (file + line, log line, command + exit code, commit SHA) and `bears_on` = the single claim that piece of evidence decides. An adjective is not a `ref`; a general vibe is not a `bears_on` | `"citations": ["..."]` |
| 3 | `"findings"` | Repair tuples `(target, action, patch_delta, diagnosed_reason)`, **partitioned by target**, each with a `route` naming the component that receives it. Verdicts without tuples cannot be acted on by anything but a human | prose critique |
| 4 | `"independence"` | `validator_model_family`, `doer_model_family`, `evidence_route` — recorded values, evaluated by rule | "separate context, separate model if needed" |
| 5 | `"attempts_declared"` / `"attempts_executed"` / `"environment"` | The k-of-n basis and the recorded conditions of the attempts (temperature, harness/config sha, node) | one lucky green run |
| 6 | `"what_would_change_verdict"` | A named, checkable counterfactual: the observation that would flip this label to a **different label**. Must name an artifact/command/attempt outcome — "more evidence" is not a counterfactual | nothing (slot did not exist) |
| 7 | `"confidence"` + `"confidence_basis"` | A number plus the observed thing it came from (attempt agreement count, deterministic exit code, single-model read). A confidence with no basis is the opinion the whole contract exists to remove | nothing (slot did not exist) |

NOT-A-VERDICT — a validator response with any slot missing, empty, or off-vocabulary is not a verdict: the loop does not close, nothing is logged green, no retry is charged to the Doer, and the response bounces back to the validator that wrote it.

Two non-verdicts in a row on one artifact ⇒ that validator is itself filed `evaluator-gap` and escalated.
The defect is in the grader, so **the grader is what gets routed** — the Doer is never punished for a form the
Validator failed to fill. The rule is stated here, on this line, because an implied rule is the same hole
wearing a hat: the plant in FIXTURES below deletes this exact line and the check goes RED.

**Claim coverage:** the set of `bears_on` values must cover every claim in the Doer's `claimed_outputs`. A
claim no evidence bears on is not a pass and not a fail — it is `evaluator-gap` (there is no check that can
decide it), routed to whoever owns the check, never to the builder.

**Confidence ceiling:** `confidence` may not exceed what its evidence class supports. Deterministic check with
recorded exit code ⇒ up to 0.95. Single-model semantic read on one attempt ⇒ ceiling 0.6 and `confidence_basis`
must contain the literal `single_run`. A 0.9 attached to a `single_run` is a contradiction and the report is
treated as incomplete.

---

## THE OUTCOME VOCABULARY AND ITS CONSUMERS (the router)

The label is not a mood; it is a routing key. The source law, from the HELIX video (`USEk7F9GIZk`) — each quote
in this file sits on one physical line and is a verbatim substring of the caption transcript:

> "the output Y that is now generated from all of this is a structured outcome label but not necessarily a binary success value"

> "the resolved or the target miss or the regression or the new action or the policy evaluation or noisy patch or the evaluator gap"

Those are the records the next loop needs; `PASS/FAIL` throws six of them away. Structured labels with no
consumer are decoration, so every label below names its consumer **in the same breath**.

| `verdict` | What it distinguishes (that one red could not) | Loop consequence | Route |
|---|---|---|---|
| `resolved` | done-test green on ≥ k of n attempts, every claim covered, no blocking finding | Loop closes; evidence folded into the training/round corpus | route: `close_loop` → Round loop (`commands/capabilities-round.md`) |
| `target-missed` | The artifact does not satisfy the stated objective; nothing previously green broke | Doer cycle re-spawn, `retry_count += 1` | route: `doer` (same target, same ladder) |
| `regression` | The target moved **and** a check that was green at the parent commit is red now | Blocks merge/close; Doer cycle + named parent SHA recorded in the tuple | route: `doer` + `block_close`, escalate at 2× |
| `noisy-patch` | It passed, but not reproducibly: the k-of-n attempts split, or the pass is not attributable to the delta | Does **not** count toward a gate; resample under recorded environment, then re-judge | route: `checker` (resample), not `doer` |
| `evaluator-gap` | Nothing in the check set can decide the claim — done-test absent, `unrunnable`, or vacuously green | The **check** is the work item, not the artifact; a `new-action` tuple against the Checker/evaluator surface | route: `evaluator` (owner of the done-test), never `doer` |
| `new-action` | The verdict is fine but an untried action/parameter/config would change the outcome | Logged as an improvement candidate; loop may close, round may not | route: `round` (`commands/capabilities-round.md`, `rlm_improve`) |

**Partition rule:** `findings` are grouped by `target`, and one target's tuples go to exactly one component.
A tuple whose `route` is absent or names no component above is dropped into `evaluator-gap` for the *verifier*
itself — an unroutable finding is an evaluator gap wearing a finding's clothes.

**Precedence when several labels are true:** `evaluator-gap` (the call cannot be trusted) > `regression` >
`target-missed` > `noisy-patch` > `new-action` > `resolved`. `resolved` is never emitted while any claim is
uncovered or any attempt budget is unmet.

**Severity is a separate field.** The old `CRITICAL` was a severity wearing an outcome label. It is now
`"halt": true` — orthogonal to the six labels — so "stop all depts that touched this artifact" no longer
overwrites the information about *what* went wrong. `halt: true` keeps its old meaning: STOP + Telegram + Mike
`APPROVE` to resume.

---

## INDEPENDENCE IS A RECORDED PREDICATE, NOT A VIBES CHECK

The Discover AI channel's own critique of the multi-agent literature (`Z90xlttVx3Y`) is the reason independence is
a recorded field and not an adjective:

> "Just because you have a coder agent and a reviewer agent here, two instances may create some organizational separation without some genuine epistemic independence at all and it might even harm the result of the complete system."

Correlated blind spots survive a context-window split. Separate context is **necessary and not sufficient**.

So the Validator's report carries the predicate, and the gate evaluates it:

- `independence.validator_model_family` **must be present, non-empty, and ≠** `independence.doer_model_family`.
  Either field absent ⇒ the report is incomplete. Equal ⇒ `same_family_collusion`.
- `independence.evidence_route` must differ from the Doer's own reporting channel. A validator that reads only
  the Doer's `self_report` re-grades the claim instead of testing it, and is scored `evaluator-gap`.
- **A verdict whose independence predicate does not evaluate true does not count toward any gate.** It is not
  red (the artifact is not on trial); it is *not a verdict*, and it routes back to the validator.

This is the loop-file half of doctrine already enforced elsewhere in the estate: `rig_capabilities/dispatcher.py`
requires `verifier_and_dispatcher_families_required` and returns `BLOCKED / same_family_collusion` on equality,
and `commands/capabilities-dispatch-verify.md` states that only the full cross-family ladder may ever say PASS,
with a closed verdict vocabulary and "nothing else, never a bare 'looks fine'". The Checker and Validator cron
rows in the fleet table below are assignments against this rule — `ornith:35b` on `rig-128gb-local` for Checkers
and `rig-256gb-strategy` on `rig-256gb-lan` for Validators are different families from the Doer lanes.

---

## ATTEMPTS, NOT RUNS

One run of a stochastic system is a sample, not a score. The HELIX video (`USEk7F9GIZk`) on why:

> "since this is a statistical system you will not get the absolute identical answer at high temperature. So you need to run this here for repeated attempts in a predefined environmental interval"

and on what has to be recorded for the comparison to mean anything:

> "We need the temperature, we need all the parameters environment, everything"

- `attempts_declared` (k) is fixed **before** judging, and any verdict that counts toward a gate needs
  `k >= 3` (a RIG floor, not a paper claim — stated so the floor is arguable rather than invisible).
- `attempts_executed < attempts_declared` ⇒ incomplete. Nothing is logged green.
- A split outcome (some attempts green, some red) is `noisy-patch`, never `resolved` and never
  `target-missed`; the split itself is the finding.
- `environment` records at minimum `temperature`, the harness/config sha256, and the node. A verdict without
  it cannot be reproduced, so it cannot be compared, so it is `noisy-patch` by definition.

---

## PROOF PACKET SHAPE

Each cycle produces one ProofPacket per layer. Only the `validator` block changed on 2026-09-02; the `doer`
and `checker` blocks are unchanged.

```json
{
  "schema_version": "rig.proof.v1",
  "run_id": "<uuid>",
  "cycle": 1,
  "artifact_path": "...",
  "artifact_hash": "sha256:...",
  "doer": {
    "cron_id": "...",
    "ran_at": "<iso>",
    "claimed_outputs": ["..."],
    "self_report": "..."
  },
  "checker": {
    "cron_id": "...",
    "ran_at": "<iso>",
    "mechanical_checks": [
      {"name": "file_exists", "pass": true},
      {"name": "imports_ok", "pass": true},
      {"name": "schema_valid", "pass": true},
      {"name": "blocklist_clean", "pass": true}
    ],
    "verdict": "PASS | FAIL",
    "errors": []
  },
  "validator": {
    "contract": "rig.verifier.v1",
    "cron_id": "...",
    "ran_at": "<iso>",
    "verdict": "resolved | target-missed | regression | noisy-patch | evaluator-gap | new-action",
    "evidence_refs": [
      {
        "ref": "gate.log#L41",
        "bears_on": "Doer claim that parse() now refuses empty keys"
      }
    ],
    "findings": [
      {
        "target": "rig_capabilities/parser.py",
        "action": "modify",
        "patch_delta": "-1 line: guard dropped in parse()",
        "diagnosed_reason": "test_empty_key_rejected was green at parent sha256:ab12",
        "route": "doer"
      }
    ],
    "independence": {
      "validator_model_family": "kimi",
      "doer_model_family": "glm",
      "evidence_route": "gate-runner log + clean checkout, not the Doer self_report"
    },
    "attempts_declared": 3,
    "attempts_executed": 5,
    "environment": {"temperature": 0.0, "config_sha": "sha256:...", "node": "rig-256gb-lan"},
    "what_would_change_verdict": "if the gate-runner log shows the suite green at the parent AND here, the label is target-missed, not regression",
    "confidence": 0.8,
    "confidence_basis": "4 of 5 attempts reproduced the break; deterministic exit code + 1 semantic read",
    "halt": false
  },
  "loop_close": "closed | open",
  "halt": false,
  "proof_hash": "sha256:..."
}
```

`loop_close` is computed, not asserted: `closed` only if the `validator` block satisfies all seven slots, the
independence predicate evaluates true, `attempts_executed >= attempts_declared`, and no claim is uncovered.
Anything else writes `open` with the missing slot named.

---

## MACHINE-READABLE CONTRACT

The three lines below are the machine interface (slot list, closed vocabulary, negative marker) that
`capabilities/loops/verifier_contract_check.py` parses. The checker **names its own copy** of the contract and
checks this document against it, so this file cannot satisfy its own gate by quietly deleting a requirement:
deleting a declaration, deleting a schema key, or deleting a label's consumer row each goes RED.

```text
#contract-slots: verdict|evidence_refs|bears_on|findings|target|action|patch_delta|diagnosed_reason|independence|validator_model_family|doer_model_family|evidence_route|attempts_declared|attempts_executed|environment|what_would_change_verdict|confidence|confidence_basis
#contract-labels: resolved|target-missed|regression|noisy-patch|evaluator-gap|new-action
#contract-negative: NOT-A-VERDICT
```

---

## FIXTURES — the checker, its plants, and the byte budget that hid them

The programs live in **`capabilities/loops/verifier_contract_check.py`** (stdlib; modes `check` / `plant` /
`report` / `self-test`); planted reports live in `tests/fixtures/fable2031/verifier-report-*.json`; the unit
suite is `tests/test_verifier_contract.py`. `done_when` is **16 short one-line guards** — 2 `file:`, one green
`check`, one green `self-test`, 8 document plants, 1 accepting report and 3 refusing ones. Every plant guard
asserts its own non-zero exit (`rc=$?; test $rc -eq 2`), so an always-red gate cannot masquerade as a passing
test and an escaped plant cannot masquerade as a passing checker.

**Why the move was forced.** `catalog._pick_main_text` reads `HEAD_BYTES = 4096`. These guards used to be
inline programs in this file's frontmatter, which ended at **byte 8606**: the loader parsed a truncated buffer,
`_quality_block` returned `{}`, and `./bin/rig-capabilities test doer-checker-validator.md` answered
`pass=false` with **zero results**. The gate was not red — it was *unloaded*, which is worse, because nothing
looked broken. Frontmatter is now **2714 bytes**, and the checker checks its own host asset for that failure
through the loader's own code path (`visibility()` calls `_pick_main_text` rather than a copy of it), so a
future edit that re-inflates the header turns this asset's own guard RED.

| Guard | What it proves |
|---|---|
| `check` | 18 slots declared *and* present as schema keys; 6 labels each with a consumer row; 3 declaration lines; law line present; host asset loadable |
| `self-test` | Counts (2 clean / 8 doc plants / 10 report plants), both clean cases accepted, all 18 plants behaving |
| `plant schema_key` | Declared slot missing from the packet schema ⇒ `what_would_change_verdict@schema` |
| `plant router_row` | Label declared, consumer deleted ⇒ `evaluator-gap@route` — the capability row's own risk, planted |
| `plant law_line` / `marker_renamed` | Law stated, not implied: delete the line, or keep the prose and rename the marker ⇒ `NOT-A-VERDICT@rule` |
| `plant slots_declaration` / `labels_declaration` / `negative_declaration` | Deleting one declaration cannot be soothed by the two that remain |
| `plant route_consumers` | Renaming every consumer ⇒ all six labels `@route`; structured labels with no consumer are decoration |
| `report …-clean.json` | A complete `rig.verifier.v1` record counts: `not_a_verdict: []` |
| `report …-looks-good / same-family / single-run` | Off-vocabulary label, validator==doer family, and 1 attempt against declared k=3, each refused |

```console
$ ./bin/rig-capabilities test doer-checker-validator.md      # 2026-09-02, after reindex
{"id": "doer-checker-validator.md", "pass": true, "ran": 16, "unrunnable": 0, …}
$ python3 capabilities/loops/verifier_contract_check.py plant capabilities/loops/doer-checker-validator.md router_row
plant router_row -> verifier-contract missing: ['evaluator-gap@route']          # exit 2
$ python3 capabilities/loops/verifier_contract_check.py report tests/fixtures/fable2031/verifier-report-single-run.json
not_a_verdict: ['attempts_below_declared_k']                                     # exit 2
$ python3 capabilities/loops/verifier_contract_check.py self-test capabilities/loops/doer-checker-validator.md
self_test fails: []
doc_plants=8 report_plants=10 clean_reports=2                                    # exit 0
```

**Two ways this gate was theater before it wasn't.** (1) The first checker asked "does the file contain
`NOT-A-VERDICT` *and* `not a verdict`" — and the plant came back GREEN, because the fixture's own `cmd:` lived
inside this file and supplied both strings. Anchors became *line shapes*: declaration lines start with
`#contract-`, the law line *starts* with the marker, a label's router row *starts* with that label in the
first cell, schema keys sit on lines whose stripped form starts with a quote. (2) The gates themselves were
invisible at 8606 bytes. A test that cannot be loaded cannot fail, and a test that cannot fail is not a test —
`scripts/frontmatter_visibility.py` now reports `truncation_hidden=0` for the estate.

`tests/test_verifier_contract.py` (16 tests) additionally proves the *checker* can fail: widening `LABELS`
makes `looks_good` pass, retargeting the marker makes the law rule miss, and emptying the plant table makes
`self-test` return 2 rather than "pass" forever.


**RED for the loop:** without these, `Builder → Verifier` closes only if a human re-reads prose and decides.
With them, an incomplete verdict is refused by the shape of the record, the label names the component that
acts next, and a flaky single green cannot pass.

---

## THE FIVE+ CRON JOBS (each enforces a different slice)

| Cron | Role | Cadence | What it inspects | Independent of |
|---|---|---|---|---|
| **1. Code Syntax Checker** | CHECKER | every 30m | All code in `~/.rig/departments/**/workers/` + `~/.rig/dept-meta-harness/` | Doer, Validator |
| **2. Doctype & Schema Validator** | CHECKER | every 60m | Every `pai.json` + `contract.yaml` matches the schema registry | Doer, Validator |
| **3. Business Rules Validator** | VALIDATOR | every 60m | Blocklist, tier, gate_d_required, fabrications across all dept outputs | Doer, Checker |
| **4. AntiGenericForce Scorer** | VALIDATOR | every 4h | All public-facing artifacts score ≥ 85 | Doer, Checker |
| **5. Drift Watchdog** | VALIDATOR | every 30m | Provider drift, model drift, schedule drift, output drift | Doer, Checker |
| **6. Substrate Integrity Checker** | CHECKER | every 4h | Each dept's 5GB target on track, scraper output byte count | Doer |
| **7. End-to-End Pipeline Validator** | VALIDATOR | every 6h | Full pipeline test: scrape → entity → pattern → L7 → verifier → dashboard | Doer, Checker |

That's **7 cron jobs** enforcing the doer / checker / validator separation — **exceeds your "at least 5" ask.**
Each validator cron emits `rig.verifier.v1` reports, so a validator that drifts into prose is caught by its own
report shape, not by someone noticing.

---

## SEPARATION OF CONCERNS

```
DOER layer:    5 GTM crons + 8 scraper crons + 1 monitor (already running)
CHECKER layer: 3 new crons (syntax, schema, substrate)
VALIDATOR layer: 4 new crons (business rules, AntiGeneric, drift, e2e)
```

**No cron is both a builder and a grader.** Each is a separate context with separate model assignments, and the
family pair (doer, validator) is written into every report so the predicate is checkable after the fact:

| Cron | Model assignment |
|---|---|
| Doers (existing 14 crons) | minimax/MiniMax-M3 or fleet nodes |
| Checkers (3 new) | rig-128gb-local ornith:35b (fast, local, cheap) |
| Validators (4 new) | rig-256gb-lan rig-256gb-strategy (deeper reasoning) |

---

## DOER → CHECKER → VALIDATOR FLOW

```
Doer cron runs cycle:
  produces artifact (file, JSON, MD)
  writes proof to /Users/rig128gb/.rig/state/{dept}-proof.json

Checker cron runs (after Doer, 15-60m later):
  reads /Users/rig128gb/.rig/state/{dept}-proof.json
  runs mechanical checks on the artifact
  writes /Users/rig128gb/.rig/state/{dept}-checker-{cycle}.json
  returns PASS / FAIL with error list
  if FAIL → returns artifact to Doer with retry instructions

Validator cron runs (after Checker, 1-6h later):
  reads Checker PASS + Doer proof
  runs the semantic checks over task + trajectory + workspace delta + test evidence + policy trail
  runs attempts_declared attempts under a recorded environment
  writes /Users/rig128gb/.rig/state/{dept}-validator-{cycle}.json  (rig.verifier.v1)
  if any slot missing / label off-vocabulary / independence predicate false → NOT A VERDICT:
      loop stays open, retry NOT charged to the Doer, report routed back to the validator;
      2 consecutive non-verdicts on one artifact → this validator filed evaluator-gap + escalate
  else route each finding tuple by its target and its route
  resolved + k-of-n met + claims covered → loop_close = closed
  target-missed / regression → Doer cycle, retry_count += 1
  noisy-patch → checker resamples, re-judge under the recorded environment
  evaluator-gap → the check is the work item; owner of the done-test gets the tuple
  halt == true → STOP all depts that touched artifact + Telegram + Mike APPROVE to resume
```

## FAILURE HANDLING (legacy verdicts mapped, 2026-09-02)

| Old verdict | Now | Action |
|---|---|---|
| PASS | `resolved` | Log + continue; loop closes only on k-of-n + claim coverage |
| WEAK | `target-missed` (or `noisy-patch` when attempts disagree) | Flag in next Doer cycle as known-issue to address |
| FAIL | `target-missed` / `regression` / `evaluator-gap` — **the label says which** | Re-spawn Doer cycle for the first two; file a check fix for the third; `retry_count` only for the first two |
| FAIL × 3 in 24h | same label, ×3 | Escalate to Jake-direct + Mike Telegram |
| CRITICAL | `"halt": true` (orthogonal to the label) | STOP all depts that touched artifact + Telegram + require Mike APPROVE to resume |
| *(new)* NOT A VERDICT | incomplete / off-vocabulary / same-family | Loop stays open; validator is re-run; the Doer is not punished for the grader's gap |

---

## SELF-HEALING MONITOR (existing, 15m cron)

The monitor cron watches all of this and self-heals:
- If Checker FAIL × 3 → auto-rebuild substrate, retry
- If Validator `halt` → halt dept + telegram Mike
- If Validator reports keep arriving incomplete (`NOT A VERDICT` × 2 on one artifact) → that validator is
  quarantined and filed `evaluator-gap`; a grader that cannot fill its own form does not get a third cycle
- If any cron drifts off schedule → restart
- If proof file empty > 2h → skip cycle, log

---

## DELIVERABLE

7 new cron jobs (3 checkers + 4 validators) wired into the 36h sprint, each pinned to a different node + model
so they can't accidentally use the same context as the Doer — and each validator pinned to a model **family**
that differs from the Doer it judges, recorded in the report that its verdict depends on.

---

## SOURCE PROVENANCE

Quotes below were verified as verbatim substrings of the auto-caption transcripts (word-level captions, so
stutters and missing punctuation are the transcript's, not mine):
`.context/discover-ai/transcripts/<id>.txt`. Verified links only (present and resolved in
`.context/discover-ai/link-verdicts.json`).

| Claim in this file | Source | Status |
|---|---|---|
| Verifier output is a structured label, not a binary success value | `USEk7F9GIZk` — "the output Y that is now generated from all of this is a structured outcome label but not necessarily a binary success value" | verbatim HIT |
| The label vocabulary | `USEk7F9GIZk` — "the resolved or the target miss or the regression or the new action or the policy evaluation or noisy patch or the evaluator gap" | verbatim HIT — note: the spoken list includes "the policy evaluation", which this contract keeps **out** of the closed vocabulary (the capability row fixes six labels); the transcript wording is reported, not adopted |
| What V is computed over (task + trajectory + workspace delta + test evidence + policy/safety evidence) | `USEk7F9GIZk` — "the verify let's call it V for verify receives not original task the complete trajectory set of whatever the accumulated workspace delta to test evidence and the policy and the safety evidence" | verbatim HIT |
| Repeated attempts under recorded conditions, not one run | `USEk7F9GIZk` — "since this is a statistical system you will not get the absolute identical answer at high temperature. So you need to run this here for repeated attempts in a predefined environmental interval" and "We need the temperature, we need all the parameters environment, everything" | verbatim HIT ×2 |
| Why one red is not enough (four configs, four different failures) | `USEk7F9GIZk` — "The harness C fixed the target test, but broke another test." | verbatim HIT |
| Findings are typed repair tuples, not prose | `bnpNJmCwGlo` — "a particular action A, a proposed patch delta, or some diagnosed reasoning row" and "this judge then proposes here repairs because sometimes it is not working at a very first run. So, you have now structured repairs" | verbatim HIT ×2 |
| The judge is a separate, external model | `bnpNJmCwGlo` — "you have an external judge LLM" | verbatim HIT |
| Evidence must be localized to a specific claim to be actionable | `LEsKxMfRFjA` — "receives now some localized evidence such as in the section three, this contains excessive blank spaces" | verbatim HIT |
| The validator is itself an editable component (so `evaluator-gap` is a real label) | `LEsKxMfRFjA` — "a validator that detects now a specific clipping, or the critiques evaluation criteria itself" | verbatim HIT |
| Multiple instances ≠ independence; independence must be substantive | `Z90xlttVx3Y` — "just having multiple agents like presented in a paper does not guarantee independent" / "two instances may create some organizational separation without some genuine epistemic independence" / "does not mean that this system has a better performance" | verbatim HIT ×3 |
| Grounding is external, not self-reported | `Z90xlttVx3Y` — "grounded by external evidence" | verbatim HIT |

**Not claimed, on purpose:**
- The transcripts never say `model_family`, `k-of-n`, or `attempts_executed`. Those names are RIG's. The
  **family-inequality rule** is RIG estate doctrine already enforced in `rig_capabilities/dispatcher.py`
  (`same_family_collusion`, `verifier_and_dispatcher_families_required`); the videos supply the *reason*
  (organizational separation without epistemic independence), not the field name.
- `k >= 3`, the `single_run` 0.6 ceiling, the label precedence order, and the `halt` split are **RIG design
  decisions** made in this file, arguable and named as such — not findings from any paper.
- Papers cited (verified: arXiv ids resolve): `arXiv:2608.13951` HELIX (repo `HKUDS/HELIX`, exists),
  `arXiv:2608.13560` AutoDesign (repo `Yaxin9Luo/AutoDesign`, exists), `arXiv:2608.22974` Dynamic Ontology
  (no repo found for this one — none is asserted), `arXiv:2608.21156` Graph Engineering.
- I read the papers **only** through the corpus dossiers (`.context/discover-ai/dossiers/`), not the arXiv
  full text. Anything the dossier asserts beyond the transcript is dossier-mediated, which is why the table
  above attributes to the video and the transcript, never to the paper's prose.
- **Quote verification is run here, not gated here.** Every attributed quote in this file — the 5 blockquote
  lines plus the 15 quoted spans in the table above, 20 spans total — was checked as an exact substring of the
  transcript of the video it is attributed to: **20/20 HIT, zero paraphrases**, 2026-09-02. Three deliberate
  controls were run against the same checker and all three went RED: rewording a table quote
  (`broke another test` → `broke some other test`), rewording a blockquote, and re-attributing a real quote to
  a different video id (`grounded by external evidence` → `Z90xlttVx3Y` → `bnpNJmCwGlo`).
- It is **not** a `done_when` entry on purpose: `.context/` is gitignored (`.gitignore:13`), so a `cmd:` that
  opens those transcripts is permanently RED in any checkout without the corpus. A gate that can only go red
  off one machine is the same theater as a gate that can never go red. The verbatim-quote gate belongs to the
  corpus job that owns `.context/`; this asset carries the quotes, the hit rate, and the controls that prove
  the checker distinguishes a paraphrase.

---

*Signed: Jake PAI, 2026-07-05 · verifier output contract added 2026-09-02 · gates moved out of frontmatter
into `verifier_contract_check.py` the same day, after the 4096-byte head proved them unloaded*
*Companion to: 36h-gtm-sprint.md, what-great-looks-like.md, commands/capabilities-dispatch-verify.md, commands/capabilities-round.md*
