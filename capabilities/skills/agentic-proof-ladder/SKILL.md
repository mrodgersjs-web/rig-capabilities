---
name: agentic-proof-ladder
description: "agentic-systems-setup sub-skill, gates E2 (L0), E5, and E8: the L0-L5 proof ladder for any agentic framework setup - docs fetched today, installed, hello on a deterministic fake, hello on a local endpoint, a durable or observed feature, and deploy only with a Gate-D approval id - with a fail-closed receipt validator and a real plain-code baseline. JEV-FIRST MANDATE."
tags: [rig, agentic-systems, sub-skill, proof, receipts, verification]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: hello-proof
  stages: [select, hello-proof, deploy-close]
  extends: "proof-loop, done-claim-verification, rig-proof-packet-builder"
outcome: "A receipt.json per framework setup that proof_ladder.py accepts (exit 0) at the highest level honestly reached, with blocked levels named by their failing check, and an agentic.setup JEV decision id."
activation: "Load at the start of every agentic setup session, before the first command (to set the target level), before every claim that a level is reached, and before reporting any setup as done."
instruction: "Record one receipt entry per level with the command, exit code, and observed output, validate with proof_ladder.py, prove the validator still bites with a plant, judge the receipt with rig-s1gate agentic.setup, and report the highest proven level, never the intended one."
applies_when:
  env: "any route (Aside sandbox, Orca terminal, Docker)"
  runtime: "Python 3 stdlib for the validator and baseline"
  deps: "scripts/proof_ladder.py, scripts/hello_baseline.py, rig-s1gate with the agentic.setup rubric"
  params: "framework slug, route, target level (default L4)"
  budget: "one receipt per framework setup; three fix attempts per level"
  scale: "one framework per receipt"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - Set the target level and fetch today's official docs for L0.
  - Run each level and write its receipt entry from observed output.
  - Validate the receipt with proof_ladder.py and prove a plant is caught.
  - Judge the receipt with rig-s1gate agentic.setup and record the decision id.
  - Report the highest proven level and every BLOCKED level with its check.
done_when:
  - "cmd:env -u PYTHONHOME -u PYTHONPATH python3 capabilities/skills/agentic-proof-ladder/scripts/proof_ladder.py capabilities/skills/agentic-proof-ladder/fixtures/receipt_baseline_real.json"
  - "cmd:env -u PYTHONHOME -u PYTHONPATH python3 capabilities/skills/agentic-proof-ladder/scripts/proof_ladder.py capabilities/skills/agentic-proof-ladder/fixtures/receipt_bad.json; test $? -eq 2"
  - "cmd:env -u PYTHONHOME -u PYTHONPATH python3 capabilities/skills/agentic-proof-ladder/scripts/proof_ladder.py capabilities/skills/agentic-proof-ladder/fixtures/receipt_baseline_real.json --plant deploy_no_approval; test $? -eq 2"
  - "cmd:env -u PYTHONHOME -u PYTHONPATH python3 capabilities/skills/agentic-proof-ladder/scripts/hello_baseline.py --model fake"
  - "cmd:env -u PYTHONHOME -u PYTHONPATH python3 capabilities/skills/agentic-proof-ladder/scripts/proof_ladder.py capabilities/skills/agentic-setup-prefect/references/proof.json --plant step_row_broken; test $? -eq 2"
out_of_scope:
  - claiming a level from a description, a plan, or a builder's own report
  - reaching L5 without Mike's approval id
  - editing a receipt after the fact to raise its level
---

# agentic-proof-ladder

JEV FIRST, binding on every proof claim: an agent whose only context is this excerpt sends
semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier
LLM call; receipts are judged with `rig-s1gate check agentic.setup`. When the classifier is
unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9;
below that the level does not count. `proof_ladder.py` runs first because it is code.

## Load surface

Always loaded at the start of every agentic setup task, before the first command: every session
ends in a receipt, so the `agentic-systems-setup` meta-skill routes gates E2, E5, and E8 here in
every session, `agentic-setup-conductor` loads it from its routes table before the first action,
`agentic-proof-runner` executes it, and the `agentic-setup-session` harness names it as doctrine.
It is a task-start surface, not a deep reference an agent must already know about.

## The ladder

| Level | Means | Required receipt fields |
|---|---|---|
| L0 | official install or quickstart page fetched today; version pinned | `docs[{url, fetched, sha256_12}]`, `version_pinned` |
| L1 | installed in the named route | `command`, `exit` 0, `version_observed` |
| L2 | hello on a deterministic fake or test model | `command`, `exit` 0, `model` (fake/test/stub), `assertion`, `observed` |
| L3 | the same hello on a local endpoint | `command`, `exit` 0, `endpoint` (loopback or LAN), `model`, `observed` non-empty content |
| L4 | a durable or observed feature exercised | `feature`, `command`, `exit` 0, `observed`, `run_id` |
| L5 | deployed or published | `approval_id` (Gate-D), `target`, `command`, `exit` 0 |

A level that cannot run goes in `blocked[{level, reason, check}]` and ends the ladder there.
Levels not tried go in `not_attempted`. BLOCKED is never PASS.

## Validate (code before judgment)

```sh
S=capabilities/skills/agentic-proof-ladder/scripts
env -u PYTHONHOME -u PYTHONPATH python3 $S/proof_ladder.py <run>/receipt.json
env -u PYTHONHOME -u PYTHONPATH python3 $S/proof_ladder.py <run>/receipt.json --plant skip_level   # must exit 2
```

Step-list receipts (the framework skills' `references/proof.json`: a list of `{step, command,
exit_code, observed, at}`) run in STEP mode: rows must be well-formed (S1; `exit_code` null means
the step never returned and never counts as success) and secret-free (P9), and the report names
the level tokens in exit-0 steps without claiming a ladder level. On 2026-09-28 all 20 framework
receipts were well-formed; a planted broken row was CAUGHT (exit 2).

Rules P1-P9: shape, contiguity, required fields and exit 0, L0 docs dated today with a sha,
L2 model deterministic, L3 endpoint local, L5 approval id, well-formed blocked entries, no
token-shaped secret in the receipt. On 2026-09-28 all seven plants (skip_level, missing_field,
stale_docs, paid_model_l2, paid_endpoint_l3, deploy_no_approval, secret_in_receipt) were CAUGHT;
the broken fixture `receipt_bad.json` produced 10 violations and exit 2.

## Judge (JEV)

```sh
rig-s1gate check agentic.setup --file <run>/receipt.json --subject "agentic:<slug> sha=<12>" --json
```

Record the decision id in the receipt. ESCALATE or BLOCK means fix and re-run; DEFERRED means
the classifier was down and the level stays unjudged.

## The baseline every framework must beat

`hello_baseline.py` is the framework-free hello: one tool, one model turn, one assertion. Real
receipt `fixtures/receipt_baseline_real.json` (2026-09-28): L0 Anthropic guidance fetched
(sha 89870adf27e0), L1 Python 3.13.12, L2 fake model PASS, L3 `127.0.0.1:8771`
`qwen3.8-uncensored:27b` answered `5` with `finish_reason: stop` in 2.02 s. If a framework's
hello needs far more code than this for the same job, say so in the receipt.
