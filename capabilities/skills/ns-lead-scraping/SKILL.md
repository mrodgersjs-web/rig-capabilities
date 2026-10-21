---
name: "ns-lead-scraping"
description: "Turn a niche into a raw lead list keyed by domain from directories, maps or sites, inside each source's terms. Sub-skill of ns-lead-gen-outbound (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Turn a niche into a raw lead list keyed by domain from directories, maps or sites, inside each source's terms."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-lead-gen-outbound
---

# ns-lead-scraping

Turn a niche into a raw lead list keyed by domain from directories, maps or sites, inside each source's terms.

## Steps
1. Pick a directory or map source for the niche.
2. Scrape name, company, site and domain.
3. Prefer direct HTTP plus parsing over paid APIs where the terms allow.
4. Hand the list to enrichment only after dedupe.

## Laws
- Domains first; everything else hangs on them. CLAIM(2XHgJXX49Jk@3m)
- Niche directories hold fresher leads than marketplaces. CLAIM(2XHgJXX49Jk@29m)
- Direct requests plus parsing can replace paid scraping APIs. CLAIM(OroDNJl-pyc@2m)

## Done-test (fails if any is true)
- The source's terms were not checked.
- Rows reach enrichment without a domain.

## Where this sits
Layer 3 under `ns-lead-gen-outbound`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
