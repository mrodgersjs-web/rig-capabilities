---
name: "ns-agent-evals-verifier"
description: "Write binary pass/fail evals and run them through a verifier that alone can declare a task done. Sub-skill of ns-agentic-workflows (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Write binary pass/fail evals and run them through a verifier that alone can declare a task done."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-agentic-workflows
---

# ns-agent-evals-verifier

Write binary pass/fail evals and run them through a verifier that alone can declare a task done.

## Steps
1. Turn each success criterion into a yes/no check.
2. Hold out cases the builder never saw.
3. Have a separate verifier run the checks and enforce the output schema.
4. Record pass rate per run; block release below the set bar.

## Laws
- Score outputs on binary criteria, not impressions. CLAIM(lNum1UFDYn0@12m) CLAIM(qKU-e0x2EmE@3m)
- Use tests, compilers or screenshots as the evidence, not the agent's own report. CLAIM(oCuttuCQmZg@15m) CLAIM(UPtmKh1vMN8@45m) CLAIM(QoQBzR1NIqI@39m)
- A separate monitor role checks the workers. CLAIM(NF10evwkefM@12m) CLAIM(Xkrfm1VfETA@1m)

## Done-test (fails if any is true)
- Any criterion is not yes/no.
- The builder and the verifier are the same agent.
- There are no held-out cases.

## Where this sits
Layer 3 under `ns-agentic-workflows`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
