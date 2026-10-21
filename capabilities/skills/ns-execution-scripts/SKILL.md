---
name: "ns-execution-scripts"
description: "Write one deterministic script per tool action so the agent orchestrates and never improvises the action itself. Sub-skill of ns-agentic-workflows (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Write one deterministic script per tool action so the agent orchestrates and never improvises the action itself."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-agentic-workflows
---

# ns-execution-scripts

Write one deterministic script per tool action so the agent orchestrates and never improvises the action itself.

## Steps
1. List every action in the directive.
2. Generate one script per action with typed inputs and a non-zero exit on failure.
3. Test each script alone on a fixed input before wiring it in.
4. Use GUI automation only when no API exists, and flag it as fragile.

## Laws
- Repeatable work belongs in code; the model only decides which script runs. CLAIM(bA-WmidVSGo@19m) CLAIM(sduaTkhIm_w@35m)
- Have the agent write the script, then keep the script, not the conversation. CLAIM(bA-WmidVSGo@55m) CLAIM(MxyRjL7NG18@96m)
- Computer-use style GUI control is a fallback for systems with no API. CLAIM(2u93VTYvG5U@0m)

## Done-test (fails if any is true)
- Any action runs without a script file behind it.
- A script exits 0 on a failed call.
- A script has no standalone test input.

## Where this sits
Layer 3 under `ns-agentic-workflows`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
