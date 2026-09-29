---
name: agentic-testing-evals
description: "agentic-systems-setup sub-skill, gate E7: tests and evals for agentic setups that can actually fail - deterministic fake-model unit tests, workflow tests, rig-testlab evals (promptfoo, agentskeptic, tenro adapters in ~/Developer/ai-user-testing-mcp), an assertion-verb check, and a planted failure proven RED then GREEN with bytes moved; BLOCKED is never FAILED and never PASSED. JEV-FIRST MANDATE."
tags: [rig, agentic-systems, sub-skill, testing, evals, rig-testlab, verification]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: test-eval
  extends: "app-verify-evidence, adversarial-verification-loop, testsprite-engineering"
outcome: "A test run with named assertions that pass, a planted defect that turned at least one test RED with a checksum change and GREEN after restore, eval runs recorded through rig-testlab with states passed, failed, blocked, or not_evaluated, and no blocked run counted as passed."
activation: "Load before claiming an agentic setup works beyond its hello, when adding evals or regression tests to an agent or workflow, and whenever a test report shows only passes."
instruction: "Write tests that run on a deterministic fake model, count their assertion verbs, plant one defect with a byte-movement proof, run evals through rig-testlab adapters with evidence verification, and report blocked and not_evaluated runs as such."
applies_when:
  env: "Aside sandbox for fake-model tests; rig-testlab sandbox for evals"
  runtime: "pytest or vitest in the framework's project; rig-testlab CLI (Node 22, pnpm)"
  deps: "~/Developer/ai-user-testing-mcp (rig-testlab), agentic-local-models fake_openai_server.py"
  params: "framework project path, scenario ids, adapters"
  budget: "fake-model tests in seconds; evals capped by the adapter's limits"
  scale: "one framework setup's regression suite"
permissions:
  - fs.read
  - fs.write
  - bash
  - gate-d-required:paid-api
flow:
  - Write unit tests that run the agent on a deterministic fake model and assert outputs.
  - Count assertion verbs and refuse a suite with none.
  - Plant one defect, prove a test goes RED with a checksum change, restore, prove GREEN.
  - Run evals through rig-testlab adapters and verify their evidence.
  - Report passed, failed, blocked, and not_evaluated separately.
done_when:
  - "file:/Users/rig128gb/Developer/ai-user-testing-mcp/adapters/promptfoo/adapter.json"
  - "grep:capabilities/skills/agentic-testing-evals/SKILL.md:not_evaluated"
  - "grep:capabilities/skills/agentic-testing-evals/SKILL.md:planted"
out_of_scope:
  - paid eval providers or hosted eval dashboards without Gate-D
  - rewriting rig-testlab itself (its own repo and owner)
  - counting a blocked or not_evaluated run as passed
---

# agentic-testing-evals

JEV FIRST, binding on every test and eval verdict: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call; receipts are judged with `rig-s1gate check agentic.setup`. When the
classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only
above 0.9.

## Load surface

Always loaded at the start of every agentic setup task that tests or evaluates: the
`agentic-systems-setup` meta-skill routes gate E7 here, `agentic-setup-conductor` loads it from
its routes table, and the `agentic-setup-session` harness names it as doctrine. It is a
task-start surface, not a deep reference.

## Four layers

1. **Unit tests on a fake model.** The agent's logic runs against `fake_openai_server.py` or a
   framework-native fake; assert tool choice, output shape, and state transitions. No network.
2. **Workflow tests.** The engine's own test harness where one exists (Temporal time-skipping
   environment, Prefect's test harness, LangGraph invoked with an in-memory checkpointer); the
   framework skill confirms the import path at L0.
3. **Evals through rig-testlab.** `~/Developer/ai-user-testing-mcp` is the governed suite:
   reviewed adapters only, sandboxed, with evidence receipts and ProofPackets.
4. **Planted failure.** Break one thing the tests guard; checksum the file before and after
   (bytes must move); the suite must go RED; restore; it must go GREEN.

## rig-testlab (observed 2026-09-28)

```sh
cd ~/Developer/ai-user-testing-mcp
PATH="$HOME/.local/bin:$PATH" pnpm --filter @rig-testlab/cli dev doctor      # all blocking checks PASS, 25 adapter descriptors, exit 0
PATH="$HOME/.local/bin:$PATH" pnpm --filter @rig-testlab/cli dev adapter list
PATH="$HOME/.local/bin:$PATH" pnpm --filter @rig-testlab/cli dev suite compile <ScenarioSpec.json>
PATH="$HOME/.local/bin:$PATH" pnpm --filter @rig-testlab/cli dev suite run <RunManifest>
PATH="$HOME/.local/bin:$PATH" pnpm --filter @rig-testlab/cli dev evidence verify <run>
```

Passing `--` before the subcommand printed the help text and exited 2 on 2026-09-28; call the
subcommand directly. The repo's own tests: 22 files, 232 tests passed (vitest, 2.34 s, same day).
Agent-eval adapters: `promptfoo` (`npx promptfoo eval`, credentials from its env store),
`agentskeptic` and `tenro` (`python -m ...`, no credentials); all three are `reviewed` and emit
`model_transcript` and `json_report` evidence. Run states are `queued`, `running`, `passed`,
`failed`, `blocked`, `not_evaluated`, `cancelled`; a blocked or not_evaluated run is never
reported as passed.

## Assertion check

A suite with zero assertion verbs is a dead-button inventory, not a test:

```sh
grep -rEc "\b(assert|expect\(|assertEqual|toBe|toEqual|should)\b" <tests-dir> | awk -F: '{s+=$2} END {print s " assertion verbs"}'
```

Report the count next to the pass count. A dependency missing at run time makes the suite
BLOCKED, not FAILED: it proves nothing is being checked.
