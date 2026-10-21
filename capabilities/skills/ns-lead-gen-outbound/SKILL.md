---
name: "ns-lead-gen-outbound"
description: "Build a list of verified contacts keyed by company domain and draft personalized outreach that sends only after approval. Nick Saraev method. Use for: scrape leads; find emails; enrich this list; cold email campaign; write icebreakers."
tier: main
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Build a list of verified contacts keyed by company domain and draft personalized outreach that sends only after approval."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: nick-saraev-os
  stage_doctrine: references/doctrine.md
---

# ns-lead-gen-outbound

Build a list of verified contacts keyed by company domain and draft personalized outreach that sends only after approval.

**Use when:** scrape leads; find emails; enrich this list; cold email campaign; write icebreakers.

## Laws
- The company domain is the key everything hangs on: get domains first and drop leads without one before spending credits. CLAIM(2XHgJXX49Jk@3m) CLAIM(eElnA0mCzXw@8m)
- Look up emails by name plus domain; it finds far more than company name alone. CLAIM(2XHgJXX49Jk@1m) CLAIM(AKNKI9uXjdQ@21m)
- Remove duplicates before any paid lookup. CLAIM(2XHgJXX49Jk@18m)
- Niche directories beat bought marketplace lists because those leads are not yet flooded with outreach. CLAIM(2XHgJXX49Jk@29m)
- Personalization depth comes from reading several pages of a prospect's site, not just the homepage. CLAIM(oAWe5wFwHlo@10m)
- AI fills slots in a script a human wrote and tested; it does not write the message from scratch. CLAIM(5E580yoD4eo@6m) CLAIM(5E580yoD4eo@34m) CLAIM(miYIg4F9aE4@2m)
- The offer and its risk reversal matter more than the list or the tools. CLAIM(IJBp8MAAMGQ@3m)

## Procedure: Scrape to verified list, with a dedupe gate
1. Set location, company size and keyword in the scraper and preview. CLAIM(2XHgJXX49Jk@2m)
2. Load results into a table and resolve domains from the company name. CLAIM(2XHgJXX49Jk@3m)
3. Remove duplicate domains and drop rows with no domain. CLAIM(2XHgJXX49Jk@18m)
4. Run a bulk decision-maker email search; keep only results flagged valid. CLAIM(2XHgJXX49Jk@4m) CLAIM(2XHgJXX49Jk@5m)

## Sub-skills (load one at a time)
- `ns-lead-scraping`: Turn a niche into a raw lead list keyed by domain from directories, maps or sites, inside each source's terms.
- `ns-email-enrichment`: Turn names and domains into verified emails while controlling credit spend.
- `ns-cold-email-personalization`: Write icebreakers with two model calls (facts to JSON, then a styled rewrite) into a human-written template.

## Done-test (fails if any is true)
- Any row has no domain.
- Any duplicate domain reached a paid call.
- Any icebreaker has generic praise or uses only homepage facts.
- Anything sends without approval of the exact text.

## Does not fit RIG
- Deliverability tricks meant to mislead the reader (fake "sent from my phone" lines, fake handwritten formatting).
- Getting around bot detection with proxies or scraping LinkedIn with session cookies; terms-of-service risk a governed build cannot carry.
- High-volume cheap-offer plays (about 1,000 emails a day, micro-niches, posing as a freelancer). RIG sells governed builds, not volume.

## Deeper doctrine
`references/doctrine.md` holds the full stage doctrine: core laws marked consensus or single-source, procedures, decision rules, failure modes and changed views, all cited. Malformed tags from distillation were removed by the tag validator.

## Where this sits
Layer 2 under `nick-saraev-os`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
