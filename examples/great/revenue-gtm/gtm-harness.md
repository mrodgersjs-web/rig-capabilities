---
name: great-gtm-harness
lane: revenue-gtm
source: canonical-curated
exemplar_of: gtm-harness
description: "Reference exemplar for preparing measurable, personalized outreach for verified ICP targets while keeping every external touch and dollar dormant behind Gate-D."
---

# GTM loop: 15 dormant account messages

## Input

Select 15 accounts in one named vertical and score each against industry, company size, role, pain, timing, and signal freshness. Require at least two factual personalization signals per message. Declare the channel, baseline reply rate, target replies, meetings, pipeline, measurement window, and attribution tag before drafting.

```console
$ python3 scripts/assert_loop_termination.py capabilities/loops/gtm-harness.md
```

## Output

The loop definition validates. The prepared batch reports 15 targets, average ICP score 78, average anti-generic score 87, two or more personalization signals per message, and zero blocklist hits. Each message has one ask, is sized for its channel, and includes campaign attribution. The proof packet distinguishes `touches_prepared: 15` from `touches_sent: 0`; Gate-D evidence confirms all sends and spend remain gated.

## Acceptance

- The command exits 0.
- Every target scores at least 70/100, every message scores at least 85, and blocklist matches are zero.
- KPI targets and a measured baseline exist before launch; results have a route back to the GTM substrate.
- No email, DM, comment, ad, spend, or public brand representation occurs without typed `APPROVE <run_id>`.
