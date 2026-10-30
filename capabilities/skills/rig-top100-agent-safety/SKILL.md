---
name: rig-top100-agent-safety
description: "Govern agents that can push, email, publish, and spend: pre-action capability checks, a spend ceiling, Gate-D approval on the exact outward text, kill switches, and an append-only audit trail. Use before granting a new tool to an agent, when an agent acted without approval, or when a routine has been left unattended on someone else's account."
tags: [rig, top100, agentic-systems, safety, guardrails, governance, audit]
metadata:
  tier: canonical
  domain: Agentic Systems
  rank: 11
  status: built-out-2026-10-25
  source_stub: ~/.grok/skills/rig-top100-agent-safety/SKILL.md
outcome: "No irreversible or outward action ran without a recorded approval id; every action left an audit line naming the actor, the capability, the target, and the verdict; and one command stops the whole fleet."
activation: "Load before adding a write, spend, publish, or message capability to any agent, when reviewing an action the user did not ask for, and when arming or re-arming a routine."
instruction: "Classify every action by reversibility and audience before the agent runs it. Read-only work is free; local writes need a claim; anything outward, irreversible, or spending money is held at Gate-D until the exact text and amount are approved. Enforce at the harness, not in the prompt. Log the decision even when it is a denial, and keep a kill switch that works on an agent that is mid-call."
applies_when:
  env: "any harness with write, network, or spend capability; production accounts and personal data"
  runtime: "harness hooks or a proxy that can block a call before it fires"
  deps: "an approval ledger, an append-only audit log, a secrets store that hides raw values"
  params: "spend ceiling, approved scopes, quiet hours, protected paths, kill-switch command"
  budget: "policy check must not add more than one round trip to an action"
  scale: "single agent through a fleet; the ceiling is per principal, not per process"
permissions:
  - fs.read
  - fs.write
  - bash
  - gate-d-required:outward-and-spend
flow:
  - Enumerate the agent's capabilities and label each reversible or irreversible, local or outward.
  - Put irreversible and outward actions behind Gate-D: approval of the exact text, amount, target, and timing.
  - Enforce the spend ceiling and quiet hours in the harness, so a confused agent cannot reason around them.
  - Protect files and accounts by explicit path and scope lists; a missing entry is a denial, not a prompt.
  - Keep the kill switch independent of the agent: it stops work while the agent is mid-call.
  - Write one audit line per decision, including denials, with actor, capability, target, verdict, approval id.
  - Re-check a re-armed routine: an unpaused job runs with the permissions it was originally given.
  - Test the guard at least once per change with a deliberate violation; an untested guard is assumed off.
done_when:
  - "cmd:test -f ${RUN_DIR:-./out/rig-top100-agent-safety}/audit.jsonl && wc -l < ${RUN_DIR:-./out/rig-top100-agent-safety}/audit.jsonl"
  - "cmd:jq -e 'select(.verdict==\"approved\") | select(.approval_id != null)' ${RUN_DIR:-./out/rig-top100-agent-safety}/audit.jsonl"
  - "cmd:jq -e '.denylist_paths | length > 0 and (.spend_ceiling_usd > 0)' ${RUN_DIR:-./out/rig-top100-agent-safety}/policy.json"
  - "grep:SKILL.md:Gate-D"
  - "grep:SKILL.md:kill switch"
out_of_scope:
  - trusting a prompt instruction as the enforcement point for a hard floor
  - approving a category ('send the follow-ups') instead of the exact text
  - an agent editing the judge or the policy that governs it
  - treating an untested guardrail as a working one
---

# Agent Guardrails and Safety

## Why this exists

Agents got hands before they got brakes. An agent that can push, email, and spend is a
liability until the limits live outside the agent's own judgment: prompts get reworded,
models get swapped, and a confident wrong read of "go ahead" costs real money and real trust.

## Outcome contract

- Why: Agents can push code, send emails, spend money, so they must be governed
- Baseline: No guardrails
- Target: Multi-layer guardrails with Gate-D approval, kill switches, and audit trails

## Method

### 1. Two axes decide the gate

| | Reversible | Irreversible |
| --- | --- | --- |
| Local | act freely, log it | act with a claim plus backup |
| Outward | act inside a pre-approved scope | Gate-D on the exact text |

Outward plus irreversible is never self-approved. That covers sending, publishing, pushing to
a shared branch, spending, deleting, and editing someone else's account.

### 2. Gate-D is about specificity

Approval covers the exact artifact: the words, the amount, the recipient, the time. "Send the
follow-ups" is not an approval; it is an intention. The ledger stores the artifact hash with
the approval id, so an edited draft is visibly unapproved.

### 3. Enforcement lives in the harness

The check runs before the call: a tool proxy, a hook, or a wrapper. A hard floor stated only
in the system prompt is a preference. Deny by default on paths and scopes not on the list, so
the failure mode of forgetting an entry is a denial rather than an accident.

### 4. Ceilings and quiet hours

Per principal: a daily and per-run spend ceiling, a hard no-spend list (legal, financial, a
minor's accounts), and quiet hours that hold outward messages rather than dropping them. An
agent that hits a ceiling stops and reports; it does not find a cheaper way to do the
disallowed thing.

### 5. Kill switch and audit

The switch is outside the agent: it stops work mid-call and is tested on every policy change.
The audit log is append-only, one line per decision including denials, with actor, capability,
target, verdict, and approval id. A log with only approvals cannot answer what the agent
decided not to do.

## Failure modes

- Approval for a category, then a specific action nobody actually saw.
- Guardrail in the prompt only; a reworded prompt removes the guard.
- Sub-agents inheriting nothing and therefore assuming nothing was allowed, or the reverse.
- Kill switch that needs the agent to cooperate.
- Audit lines that print secrets, trading one exposure for another.

## Done-test (executable)

```bash
RUN_DIR=${RUN_DIR:-./out/rig-top100-agent-safety}
r=0
jq -e '.denylist_paths | length > 0' "$RUN_DIR/policy.json" >/dev/null || { echo "BLOCK no protected paths"; r=1; }
jq -e '.spend_ceiling_usd > 0' "$RUN_DIR/policy.json" >/dev/null || { echo "BLOCK no spend ceiling"; r=1; }
jq -e 'select(.verdict=="approved") | select(.approval_id != null and .artifact_sha != null)' "$RUN_DIR/audit.jsonl" >/dev/null || { echo "BLOCK approval without evidence"; r=1; }
grep -q '"verdict":"denied"' "$RUN_DIR/audit.jsonl" || echo "WARN no denials logged: was the guard ever exercised?"
test -f "$RUN_DIR/kill-switch.sh" && echo "kill switch present" || { echo "BLOCK no kill switch"; r=1; }
[ "$r" -eq 0 ] && echo "PASS" || echo "BLOCK"
```

## Verification

Attempt one deliberately disallowed action and confirm it was blocked at the harness, not
apologised about by the model. Confirm every approved outward line in the audit log has an
approval id and an artifact hash that matches what actually went out. Confirm the kill switch
stops a running job and that quiet hours held a message instead of losing it.

## Related

`rig-top100-agent-evaluation` (quality gates), `rig-top100-agent-cost` (spend enforcement),
`rig-top100-agent-observability` (the audit trail), `rig-top100-agent-orchestration` (what a
child may do unattended).
