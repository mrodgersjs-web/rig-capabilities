---
name: "ns-agentic-workflows"
description: "Turn a business SOP into an agent built in three layers (directive, orchestration, execution) that a separate checker can verify. Nick Saraev method. Use for: build an agent for this; turn this SOP into an agent; directive / agents.md; sub-agents; routine on a schedule; Claude Code or Codex workflow."
tier: main
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Turn a business SOP into an agent built in three layers (directive, orchestration, execution) that a separate checker can verify."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: nick-saraev-os
  stage_doctrine: references/doctrine.md
---

# ns-agentic-workflows

Turn a business SOP into an agent built in three layers (directive, orchestration, execution) that a separate checker can verify.

**Use when:** build an agent for this; turn this SOP into an agent; directive / agents.md; sub-agents; routine on a schedule; Claude Code or Codex workflow.

## Laws
- Keep three layers apart: goals in plain-language directives, the model only routes, deterministic scripts do the actions. CLAIM(bA-WmidVSGo@15m) CLAIM(MxyRjL7NG18@62m) CLAIM(Uj-1we7Rew4@1m) CLAIM(hwTz4s_IqgE@2m) CLAIM(c7DKk9xHaaU@0m)
- Put anything repeatable or logical (sorting, math, API calls) in code; keep the model for judgment and synthesis. CLAIM(bA-WmidVSGo@19m) CLAIM(MxyRjL7NG18@66m) CLAIM(sduaTkhIm_w@35m) CLAIM(QufcrM79snw@9m)
- Break work into small units that are each checked on their own, so one failure does not contaminate the rest. CLAIM(oCuttuCQmZg@3m) CLAIM(UPtmKh1vMN8@28m) CLAIM(45K3zHckCnQ@8m)
- Unattended runs need stricter written procedures than chat sessions, because nobody is steering and errors compound. CLAIM(j3aXJNu9804@1m) CLAIM(Uj-1we7Rew4@29m) CLAIM(Ob5Vu-gD3mo@9m)
- Accept nothing without verification: tests, compilers or screenshot checks scored on yes/no criteria. CLAIM(oCuttuCQmZg@15m) CLAIM(UPtmKh1vMN8@45m) CLAIM(QoQBzR1NIqI@39m) CLAIM(lNum1UFDYn0@12m) CLAIM(qKU-e0x2EmE@3m)
- Keep state in files and prune context; pasting raw history into the prompt lowers quality and raises cost. CLAIM(oCuttuCQmZg@8m) CLAIM(EsTrWCV0Ph4@103m) CLAIM(LP7bfT4vOlo@1m) CLAIM(yulWjh3rq28@40m)
- Run each worker in an isolated, short-lived container so every run starts the same and credentials stay narrow. CLAIM(j3aXJNu9804@5m) CLAIM(NF10evwkefM@7m) CLAIM(Ob5Vu-gD3mo@7m)
- Anything outward-facing waits for a human; internal steps may run on their own. CLAIM(8rVQuZlRaqo@4m) CLAIM(rvkjS3YoVio@4m)

## Procedure: Three-layer workflow setup
1. Create a directives/ folder for goals and an executions/ folder for scripts. CLAIM(bA-WmidVSGo@53m) CLAIM(MxyRjL7NG18@96m)
2. Write agents.md with the layer rules and how the agent reports its own errors. CLAIM(bA-WmidVSGo@47m) CLAIM(MxyRjL7NG18@76m)
3. Write the business logic as bullets inside each directive. CLAIM(MxyRjL7NG18@12m) CLAIM(Uj-1we7Rew4@29m)
4. Have the agent generate one deterministic script per action, called by name from the directive. CLAIM(bA-WmidVSGo@55m) CLAIM(MxyRjL7NG18@97m)
5. RIG addition: run the routine on synthetic payloads before any live schedule is turned on. CLAIM(j3aXJNu9804@12m)

## Sub-skills (load one at a time)
- `ns-directive-writer`: Turn an SOP into an unambiguous agent directive and lay out the file-based context it reads.
- `ns-execution-scripts`: Write one deterministic script per tool action so the agent orchestrates and never improvises the action itself.
- `ns-agent-evals-verifier`: Write binary pass/fail evals and run them through a verifier that alone can declare a task done.
- `ns-agent-security`: Review an agent setup for exposed secrets, open ports, broad tool permissions and weak sandbox boundaries before it runs unattended.

## Done-test (fails if any is true)
- The orchestration layer makes any direct API call that is not a script in executions/.
- Any eval is phrased as an opinion instead of a yes/no check.
- The independent verifier's pass rate on held-out cases is below the threshold set for the job.
- Any outward action has no approval gate.
- A secrets scan of the repo finds anything.

## Does not fit RIG
- Self-healing as he describes it (the agent rewrites its own directives after reading its own errors). In RIG the agent proposes a patch, an evaluator scores it and a verifier merges it; no agent approves its own work.
- Rendering long prompts as images to save tokens: single-source and not auditable.
- Screen-coordinate GUI automation as a default: fragile; last resort only when no API exists.

## Deeper doctrine
`references/doctrine.md` holds the full stage doctrine: core laws marked consensus or single-source, procedures, decision rules, failure modes and changed views, all cited. Malformed tags from distillation were removed by the tag validator.

## Where this sits
Layer 2 under `nick-saraev-os`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
