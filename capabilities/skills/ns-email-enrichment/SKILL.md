---
name: "ns-email-enrichment"
description: "Turn names and domains into verified emails while controlling credit spend. Sub-skill of ns-lead-gen-outbound (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Turn names and domains into verified emails while controlling credit spend."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-lead-gen-outbound
---

# ns-email-enrichment

Turn names and domains into verified emails while controlling credit spend.

## Steps
1. Dedupe by domain.
2. Use single-domain search for large companies, bulk search for small ones.
3. Keep only verified results; log the found rate.

## Laws
- Name plus domain beats company name alone. CLAIM(2XHgJXX49Jk@1m) CLAIM(AKNKI9uXjdQ@21m)
- Dedupe before paying. CLAIM(2XHgJXX49Jk@18m)
- One domain search can return many contacts at a large company. CLAIM(2XHgJXX49Jk@9m)

## Done-test (fails if any is true)
- A duplicate reached a paid lookup.
- The found rate is far under benchmark with no reason logged.

## Where this sits
Layer 3 under `ns-lead-gen-outbound`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
