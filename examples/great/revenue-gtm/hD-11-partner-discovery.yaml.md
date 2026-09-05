---
name: great-hd-11-partner-discovery-yaml
lane: revenue-gtm
exemplar_of: hD-11-partner-discovery.yaml
description: "Reference exemplar — a partner ecosystem narrowed by public overlap evidence, conflict screening, reproducible fit scores, mutual-value hypotheses, compliant contacts, and dormant outreach."
---

# hD-11 partner discovery — dental integration partners

## Input

Find integration and referral partners that close the distribution gap for multi-site dental groups. Map adjacent vendors, communities, integrators, and platforms; shortlist only candidates with audience overlap and a concrete first joint motion.

## Output

`artifacts/partner/dental-ecosystem-2026-09/` contains a typed thesis, a categorized map of at least ten candidates, public overlap sources, reason-coded competitive/exclusivity exclusions, versioned five-factor scores, shortlist evidence, mutual-value entries, professional public contact paths, individualized drafts, Twenty partner record receipts, and dated follow-up tracking. No personal email is guessed or scraped.

## Acceptance

```console
$ python3 scripts/partner_score.py artifacts/partner/dental-ecosystem-2026-09/ecosystem_map.json --out artifacts/partner/dental-ecosystem-2026-09/scores.json
# expected: exit 0 and reproduce audience-fit, feasibility, brand, reach, and effort scores
$ python3 scripts/draft_similarity.py artifacts/partner/dental-ecosystem-2026-09/drafts/
# expected: similarity below 0.8 for candidate-specific drafts
$ ./bin/rig-capabilities goal-spec --stem hD-11-partner-discovery
# expected: verdict OK
```

Every shortlisted candidate has two concrete evidence URLs, `their_gain`, `our_gain`, and `first_motion`; CRM record count equals shortlist count. Contact sources are limited to company pages, public LinkedIn, or event speaker pages. Without `APPROVE dental-ecosystem-2026-09`, all drafts keep `arm: false` and the run ends safely as `staged`.