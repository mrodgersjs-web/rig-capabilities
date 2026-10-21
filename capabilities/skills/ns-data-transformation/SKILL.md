---
name: "ns-data-transformation"
description: "Clean and reshape scraped or inbound data: regex for simple extraction, a model for messy text, array and JSON reshaping. Sub-skill of ns-automation-builds (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Clean and reshape scraped or inbound data: regex for simple extraction, a model for messy text, array and JSON reshaping."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-automation-builds
---

# ns-data-transformation

Clean and reshape scraped or inbound data: regex for simple extraction, a model for messy text, array and JSON reshaping.

## Steps
1. Decide per field: regex if the pattern is fixed, a model if it is free text.
2. Normalize to arrays.
3. Validate types before writing anywhere.

## Laws
- Use regex for fixed patterns and a model for messy text. CLAIM(sOSrsYmo0pM@22m) CLAIM(xs10RZU0Gp0@23m) CLAIM(o9AvKxLuCRU@5m)
- Treat every payload as an array. CLAIM(6b442bN0CyI@49m) CLAIM(Ksr_H30Oris@9m)

## Done-test (fails if any is true)
- A model is used where a fixed regex would work, with no reason logged.
- A record is written with an unvalidated type.

## Where this sits
Layer 3 under `ns-automation-builds`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
