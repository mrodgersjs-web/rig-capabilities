---
name: "ns-api-http-integration"
description: "Connect any service through raw HTTP: auth, request shape, JSON parsing, and hidden APIs found in the browser network tab. Sub-skill of ns-automation-builds (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Connect any service through raw HTTP: auth, request shape, JSON parsing, and hidden APIs found in the browser network tab."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-automation-builds
---

# ns-api-http-integration

Connect any service through raw HTTP: auth, request shape, JSON parsing, and hidden APIs found in the browser network tab.

## Steps
1. Find the endpoint in the docs or the browser network tab.
2. Reproduce the call with curl, then import it into the HTTP module.
3. Map dropdown values to internal ids, not labels.
4. Keep keys in the platform credential store.

## Laws
- Most failed calls are malformed JSON or the wrong data type. CLAIM(JdKC8TOPfJE@24m) CLAIM(898WpSTxbFU@10m)
- Map dropdown fields to the ids the API expects, not the labels you see. CLAIM(vHJH3TShGks@25m)
- Keep credentials out of the canvas. CLAIM(JdKC8TOPfJE@16m)

## Done-test (fails if any is true)
- A call works in curl but not in the flow and nobody logged why.
- A key appears in an export.
- A field is mapped by label where the API wants an id.

## Where this sits
Layer 3 under `ns-automation-builds`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
