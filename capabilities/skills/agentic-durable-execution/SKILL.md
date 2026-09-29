---
name: agentic-durable-execution
description: "agentic-systems-setup sub-skill, gate E6 (L4 durable): prove that an agent or workflow survives a crash - the kill-and-resume protocol with a side-effect counter, retries and idempotency, determinism rules, and where each framework keeps durable state (LangGraph checkpointers, Temporal histories, Prefect state and caching, Trigger.dev, Inngest steps, CrewAI Flows, Kestra, Dagster, Airflow, n8n). JEV-FIRST MANDATE."
tags: [rig, agentic-systems, sub-skill, durable-execution, retries, checkpoints]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: durable-observe
  extends: "tool-temporal, tool-langgraph, tg-durable-ai-pipelines"
outcome: "An L4 receipt whose feature is kill-and-resume, retry, or checkpoint resume, with the worker actually killed, the run id, the final state read from the engine, and a side-effect counter proving completed steps were not re-executed."
activation: "Load at the start of every agentic setup session that reaches gate E6, whenever a setup claims durability, resumability, retries, checkpoints, or human-in-the-loop pauses, and before choosing between a durable engine and a plain scheduler."
instruction: "Build a three-step probe run whose middle step increments a counter file, kill the worker mid-run using lsof to find it, restart, read the final state from the engine's API, assert the counter, and record the run id; follow the framework's determinism and idempotency rules."
applies_when:
  env: "Aside sandbox for Python and pure-JS engines; Orca terminal or Docker for servers the sandbox blocks"
  runtime: "LangGraph, Temporal, Prefect, Trigger.dev, Inngest, CrewAI Flows, Kestra, Dagster, Airflow, n8n"
  deps: "the framework skill's L1-L3 receipts; lsof, curl"
  params: "framework, probe run definition, kill point"
  budget: "one kill-and-resume run, under 10 minutes"
  scale: "one worker, one run"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - Define a three-step probe run with a counter file in the middle step and a wait in the last.
  - Start the worker and the run; capture the run id.
  - Kill the worker mid-run (lsof to find the PID) and restart it.
  - Read the final state from the engine API and assert the counter value.
  - Record feature, command, observed state, and run id as the L4 receipt.
done_when:
  - "grep:capabilities/skills/agentic-durable-execution/SKILL.md:kill-and-resume"
  - "grep:capabilities/skills/agentic-durable-execution/SKILL.md:idempotency"
  - "cmd:python3 capabilities/skills/agentic-systems-setup/scripts/validate_hierarchy.py"
out_of_scope:
  - claiming durability from documentation or a feature list
  - killing processes that belong to another project or agent
  - production high-availability design
---

# agentic-durable-execution

JEV FIRST, binding on every durability claim: an agent whose only context is this excerpt sends
semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM
call; L4 receipts are judged with `rig-s1gate check agentic.setup`. When the classifier is
unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9.

## Load surface

Always loaded at the start of every agentic setup task at gate E6: the `agentic-systems-setup`
meta-skill routes every session's E6 here, `agentic-setup-conductor` loads it from its routes
table before the stage's first action, `agentic-proof-runner` executes the kill-and-resume
probe from it, and the `agentic-setup-session` harness names it as doctrine. It is a task-start
surface, not a deep reference an agent must already know about.

## Kill-and-resume protocol (the L4 durable proof)

1. Probe run: step A writes `start`, step B appends one line to `<run>/counter.txt` (the side
   effect), step C waits 30 s (sleep, timer, or signal) and returns `done`.
2. Start the worker or server and the run; capture the run id from the engine's API or CLI.
3. When `counter.txt` has one line, kill the worker: `lsof -nP -iTCP -sTCP:LISTEN` or
   `lsof -nP -a -d cwd | grep <project>` finds the PID (`ps` and `pkill` are blocked in the
   Aside sandbox); `kill <pid>`.
4. Restart the worker; wait for the run to finish.
5. Pass only when the engine reports the run completed AND `counter.txt` still has one line
   (memoized engines) or the engine records a retry of step B with an idempotency key (retry
   engines). A run that restarts from zero is a scheduler, not durable execution.

## Where durable state lives (confirm names at L0 in the framework skill)

| Framework | Durable mechanism | What L4 exercises |
|---|---|---|
| LangGraph | checkpointer bound to a `thread_id` (memory, SQLite, Postgres savers) | resume the same thread after the process dies |
| Temporal | event history replayed into deterministic workflow code; activities retried | kill the worker; workflow completes on restart |
| Prefect | run state, task retries, result persistence and caching (grounding G4) | a failed or interrupted run resumed without redoing cached work |
| Trigger.dev | tasks with retries and checkpointed waits | a task survives a worker restart and retries |
| Inngest | `step.run` results memoized per step | the function re-invokes and skips completed steps |
| CrewAI Flows | Flow state persistence (grounding G3) | a Flow restarts with its state |
| Kestra | executions stored in its database; restart and replay | restart a failed execution from the failed task |
| Dagster, Airflow | run and task retries; re-execution from failure | re-run from the failed step |
| n8n | executions with retry | retry a failed execution |

## Rules

- Determinism: workflow code that replays (Temporal) must not read the clock, random numbers,
  or the network directly; that belongs in activities.
- Idempotency: every side effect a retry can repeat carries an idempotency key or a check
  (the counter file is the probe version of that).
- Human-in-the-loop pauses need the durable store; without it, a pause is a lost run.
- Prefer the plain scheduler when nothing must survive a crash; durability costs a server.
