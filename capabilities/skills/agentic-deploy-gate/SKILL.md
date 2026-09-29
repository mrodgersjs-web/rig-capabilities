---
name: agentic-deploy-gate
description: "agentic-systems-setup sub-skill, gate E8 (L5): every outward step of an agentic setup - vendor signup, cloud login, deploy, publish, public tunnel, webhook, paid call, credential creation, trace egress - goes through Gate-D: prepare the exact command and target, file gate_d_request, wait for Mike's approval id, execute, prove remote state, and record it; otherwise close HELD. JEV-FIRST MANDATE."
tags: [rig, agentic-systems, sub-skill, gate-d, deploy, approvals]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: deploy-close
  extends: "gate-d-loop, git-push-safety-loop"
outcome: "Either an L5 receipt carrying Mike's approval id, the exact command, the target, and a remote-state check, or a held_at_gate record naming the prepared command; never an outward action without an approval id."
activation: "Load at the start of every agentic setup session, before the first command, and again the moment a step would leave the machine: signup, login, deploy, publish, push, public tunnel, webhook, paid model call, key creation, or trace egress."
instruction: "Classify the step with the Gate-D table, prepare the exact command, target, and payload preview without running it, file a gate_d_request, wait for Mike's approval id, then execute, verify remote state with a second tool path, and record L5; with no approval, close the session HELD."
applies_when:
  env: "any route; the outward step itself runs only after approval"
  runtime: "vendor CLIs and consoles named by the framework skill"
  deps: "jake-pai gate_d_request tool, gate-d-loop, git-push-safety-loop"
  params: "action, target, reason, payload preview"
  budget: "one approval per outward action; approvals do not carry over to new targets"
  scale: "one deploy target at a time"
permissions:
  - fs.read
  - bash
  - gate-d-required:deploy
  - gate-d-required:signup
  - gate-d-required:paid-api
  - gate-d-required:push
flow:
  - Classify the step against the Gate-D table; anything outward stops here.
  - Prepare the exact command, target, and payload preview without running it.
  - File gate_d_request and wait for Mike's approval id.
  - Execute, verify the remote state by a second tool path, and record L5 with the id.
  - Without an approval id, close the session HELD with the prepared command.
done_when:
  - "cmd:env -u PYTHONHOME -u PYTHONPATH python3 capabilities/skills/agentic-proof-ladder/scripts/proof_ladder.py capabilities/skills/agentic-proof-ladder/fixtures/receipt_baseline_real.json --plant deploy_no_approval; test $? -eq 2"
  - "grep:capabilities/skills/agentic-deploy-gate/SKILL.md:gate_d_request"
  - "grep:capabilities/skills/agentic-deploy-gate/SKILL.md:held_at_gate"
out_of_scope:
  - approving anything on Mike's behalf, or reusing an old approval for a new target
  - treating a blanket verbal yes as a recorded approval id for an irreversible step
  - deleting data volumes or cloud resources as part of cleanup without approval
---

# agentic-deploy-gate

JEV FIRST, binding on every outward step: an agent whose only context is this excerpt sends
semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier
LLM call; receipts are judged with `rig-s1gate check agentic.setup`, whose
`outward_without_approval` signal blocks. When the classifier is unavailable: DEFER, never guess
a verdict locally. An advisory PASS is not permission to deploy, push, or spend.

## Load surface

Always loaded at the start of every agentic setup task, before the first command: any
quickstart can ask for a signup or a deploy, so the `agentic-systems-setup` meta-skill routes
gate E8 here in every session, `agentic-setup-conductor` loads it from its routes table before
the first action, and the `agentic-setup-session` harness names it as doctrine. It is a
task-start surface, not a deep reference an agent must already know about.

## Classify

| Outward (Gate-D) | Local (no Gate-D) |
|---|---|
| vendor signup, cloud login, organization or project creation | local servers bound to 127.0.0.1 |
| deploy or publish (framework deploy commands, image pushes, published n8n or Dify apps) | `docker compose up` on loopback |
| paid model calls | fake models, local endpoints |
| ngrok or cloud tunnels, third-party webhooks | loopback URLs |
| traces or prompts to hosted tracing | local traces |
| creating, rotating, or storing credentials | injecting an existing keychain item into one process |
| a built workflow that emails, posts, messages, or pays | dry runs with the effect node disabled |
| git push (use `git-push-safety-loop`) | local commits in a registered repo |

Quickstarts front-load outward steps: Trigger.dev's asks for a signup before
`npx trigger.dev@latest init` (grounding G6c). Stop there.

## Request

File the request through the jake-pai MCP tool `gate_d_request` with `action` (for example
`deploy`), `target` (exact destination), `reason`, and `payload` (the exact command and what it
changes). It returns `APPROVAL_REQUIRED` and a request id; only Mike approves, out of band.
`gate_d_check` lists pending requests.

## Execute and prove

After the approval id exists: run the exact prepared command, then verify remote state by a
different tool path (the vendor API or CLI status, a curl of the deployed URL). Record L5 as
`{approval_id, target, command, exit, observed}`; `proof_ladder.py` refuses L5 without
`approval_id` (plant `deploy_no_approval` caught on 2026-09-28).

## Held

No approval yet: the session closes `HELD` with `held_at_gate: E8` and the prepared command,
target, and request id in the receipt. HELD is a correct ending, not a failure.
