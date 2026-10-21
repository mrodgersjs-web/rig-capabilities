---
name: "ns-agent-security"
description: "Review an agent setup for exposed secrets, open ports, broad tool permissions and weak sandbox boundaries before it runs unattended. Sub-skill of ns-agentic-workflows (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Review an agent setup for exposed secrets, open ports, broad tool permissions and weak sandbox boundaries before it runs unattended."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-agentic-workflows
---

# ns-agent-security

Review an agent setup for exposed secrets, open ports, broad tool permissions and weak sandbox boundaries before it runs unattended.

## Steps
1. Scan the repo and exports for keys.
2. List every tool and permission the agent holds; remove what the directive does not need.
3. Confirm each worker runs in a short-lived isolated container.
4. Check no service listens on a public port without auth.

## Laws
- Isolated, disposable containers limit what a compromised run can reach. CLAIM(j3aXJNu9804@5m) CLAIM(NF10evwkefM@7m) CLAIM(Ob5Vu-gD3mo@7m)
- Credentials pasted into a workflow canvas leak through exports. CLAIM(JdKC8TOPfJE@16m)

## Done-test (fails if any is true)
- A secrets scan finds anything.
- The agent holds a permission no directive uses.
- A worker shares a long-lived environment with other jobs.

## Where this sits
Layer 3 under `ns-agentic-workflows`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
