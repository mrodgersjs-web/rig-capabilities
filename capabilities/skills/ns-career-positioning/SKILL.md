---
name: "ns-career-positioning"
description: "Triage model releases, apply the business-formula test, and check skills are learned by hand before automating them. Sub-skill of ns-ai-career-and-content (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Triage model releases, apply the business-formula test, and check skills are learned by hand before automating them."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-ai-career-and-content
---

# ns-career-positioning

Triage model releases, apply the business-formula test, and check skills are learned by hand before automating them.

## Steps
1. Log each release as a minor bump or a new class.
2. Test only new classes.
3. Before automating a task, confirm you can do it by hand.
4. Tie each project to a named formula.

## Laws
- Business judgment is the durable edge. CLAIM(S3kdxriOESk@13m)
- Test new capability classes, not every bump. CLAIM(x55Fj_syFcI@0m)
- Hand-learn before automating. CLAIM(iqfA2vfbKUY@3m)
- Work backward from a goal with a driver tree. CLAIM(Ozp3k4qzmHo@2m)

## Done-test (fails if any is true)
- A release was tested without a class label.
- A project has no named formula.

## Where this sits
Layer 3 under `ns-ai-career-and-content`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
