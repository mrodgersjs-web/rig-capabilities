---
name: "ns-directive-writer"
description: "Turn an SOP into an unambiguous agent directive and lay out the file-based context it reads. Sub-skill of ns-agentic-workflows (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Turn an SOP into an unambiguous agent directive and lay out the file-based context it reads."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-agentic-workflows
---

# ns-directive-writer

Turn an SOP into an unambiguous agent directive and lay out the file-based context it reads.

## Steps
1. Write the goal, inputs, outputs and stop condition in plain bullets.
2. Keep the core directive short and move detail into files loaded on demand.
3. Name every script the directive may call; forbid anything not named.
4. State the output schema and the approval point for outward actions.

## Laws
- Business logic goes in plain bullet points inside the directive, not in code comments or chat. CLAIM(MxyRjL7NG18@12m) CLAIM(Uj-1we7Rew4@29m)
- Keep core instructions short; long prompts lose accuracy. CLAIM(CxbHw93oWP0@2m)
- Unattended routines still need full runbooks: filters, formats and limits written out, kept in loadable files. CLAIM(j3aXJNu9804@10m)
- agents.md carries the layer rules every session starts from. CLAIM(bA-WmidVSGo@47m)

## Done-test (fails if any is true)
- A second reader cannot state the stop condition from the directive alone.
- The directive calls a tool or script it does not name.
- No output schema is written.

## Where this sits
Layer 3 under `ns-agentic-workflows`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
