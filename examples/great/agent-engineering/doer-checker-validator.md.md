---
name: great-doer-checker-validator
lane: agent-engineering
source: canonical-curated
exemplar_of: doer-checker-validator
description: Reference exemplar — the validator output contract refusing twelve validator responses by shape, including "looks good", evidence with no claim attached, an unrecorded model family and a single lucky run, and accepting the two complete reports that actually close the Builder→Verifier loop
---

# doer-checker-validator — reference

Canonical asset `doer-checker-validator` (loop). Path: `capabilities/loops/doer-checker-validator.md`.

> A validator answer is a record with seven required slots, not a sentence. `verdict` from a closed
> six-label vocabulary, evidence that names the claim it bears on, repair tuples with a route, a recorded
> independence predicate, k-of-n attempts under recorded conditions, a named falsifier, and a confidence with
> a basis. Anything missing is **NOT A VERDICT**: the loop stays open and the response routes back to the
> validator that wrote it, never to the Doer.

All output below is real, 2026-09-02. Every judgment comes from the shipped checker,
`capabilities/loops/verifier_contract_check.py` — the same `check_report` its `done_when` guards invoke, run
here over its own `CLEAN` and `PLANTED` tables so each response prints on its own line.

## Twelve answers, two of them verdicts

```console
$ python3 -c "import importlib.util,pathlib;s=importlib.util.spec_from_file_location('vcc','capabilities/loops/verifier_contract_check.py');…"
COMPLETE verdict (resolved) -> VERDICT
COMPLETE verdict (regression) -> VERDICT
looks good                 -> NOT A VERDICT  outcome_label_outside_vocabulary
evidence no claim          -> NOT A VERDICT  claim_with_no_evidence
no evidence                -> NOT A VERDICT  claim_with_no_evidence
tuple no patch delta       -> NOT A VERDICT  unroutable_finding_tuple
family absent              -> NOT A VERDICT  model_family_absent
same family                -> NOT A VERDICT  same_family_collusion
single run                 -> NOT A VERDICT  attempts_below_declared_k
no environment             -> NOT A VERDICT  environment_unrecorded
no falsifier               -> NOT A VERDICT  incomplete_not_a_verdict
confidence no basis        -> NOT A VERDICT  incomplete_not_a_verdict
```

`looks_good` is refused because the label is off-vocabulary, not because it is red or green. That is the whole
move: the loop cannot close on an adjective, and it cannot close on a *complete-looking* record whose
independence was never written down.

## What a closing verdict looks like

```json
{
  "contract": "rig.verifier.v1",
  "verdict": "regression",
  "evidence_refs": [
    {"ref": "gate.log#L9", "bears_on": "Doer claim that the suite is green"}
  ],
  "findings": [
    {"target": "parser.py", "action": "modify", "patch_delta": "-1 guard removed",
     "diagnosed_reason": "test green at parent", "route": "doer"}
  ],
  "validator_model_family": "claude",
  "doer_model_family": "gpt",
  "attempts_declared": 3,
  "attempts_executed": 4,
  "environment": {"temperature": 0.2},
  "what_would_change_verdict": "green at the parent too means target-missed",
  "confidence": 0.9,
  "confidence_basis": "4 of 4 reproduced"
}
```

Read the slots as answers to questions someone can check without the writer in the room:

| Slot | The question it answers |
|---|---|
| `verdict` | Which of six things happened — not how bad it felt |
| `evidence_refs[].bears_on` | Where, and **which claim** that piece of evidence decides — a `ref` with no claim attached is refused |
| `findings[].route` | Who acts next, split by target — the consumer that keeps labels from being decoration |
| `validator_model_family` ≠ `doer_model_family` | Whether this second opinion can be correlated with the first |
| `attempts_executed` ≥ `attempts_declared` ≥ 3 | Whether one lucky sample is being reported as a score |
| `what_would_change_verdict` | What the writer would have had to see to say something else |
| `confidence_basis` | Where the number came from, so the ceiling can be enforced |

## The document is gated too — and its gates have a byte budget

The contract in the loop file is checked by `done_when`, not by reading it. The plants are mutations the
checker applies to its own document in memory, and each guard asserts a non-zero exit:

```console
$ python3 capabilities/loops/verifier_contract_check.py check capabilities/loops/doer-checker-validator.md
verifier-contract missing: []                                                    # exit 0
$ python3 capabilities/loops/verifier_contract_check.py plant capabilities/loops/doer-checker-validator.md schema_key
plant schema_key -> verifier-contract missing: ['what_would_change_verdict@schema']   # exit 2
$ python3 capabilities/loops/verifier_contract_check.py plant capabilities/loops/doer-checker-validator.md router_row
plant router_row -> verifier-contract missing: ['evaluator-gap@route']                # exit 2
$ python3 capabilities/loops/verifier_contract_check.py plant capabilities/loops/doer-checker-validator.md law_line
plant law_line -> verifier-contract missing: ['NOT-A-VERDICT@rule']                   # exit 2
$ ./bin/rig-capabilities test doer-checker-validator.md | head -4
{"id": "doer-checker-validator.md", "pass": true, "ran": 16, "unrunnable": 0, …}      # exit 0
```

Deleting the router row while leaving the label declared is the plant that matters most. A vocabulary nobody
consumes is the failure the capability row warned about, and here it is a red gate instead of a paragraph.

**The lesson the checker now enforces on itself.** These guards used to be inline programs inside the loop's
frontmatter, which ended at byte 8606. `catalog._pick_main_text` reads 4096, so the loader parsed a truncated
buffer, `_quality_block` returned `{}`, and `test` answered `pass=false` with zero results — a gate nobody
could see. Frontmatter is now 2714 bytes and `verifier_contract_check.py` re-checks its own host asset through
the loader's real code path, so inflating the header again fails this asset rather than silently unloading it.
This is the same class of failure as the contract it enforces: **a record nobody can read is not a record.**

## Why "incomplete" routes to the grader

The old loop punished the Doer for a validator's vague answer: `WEAK` became a retry, and the builder lost a
cycle to a form nobody filled in. Under the contract the defect travels to whoever caused it — a missing slot
is the validator's bug, so the validator is re-run, and twice in a row on one artifact files *that validator*
`evaluator-gap`. The Doer is not punished for the grader's gap.

## What would make this exemplar wrong

A validator that fills all seven slots and is still wrong is possible — the contract buys decidability, not
correctness. The falsifier slot is what makes that disagreement addressable: it names the observation that
would have flipped the label, so the next cycle tests *that*, instead of re-running the same judgment and
hoping for a different adjective.
