---
name: "rig-revenue-gbp-protocol"
description: "Run the Google Business Profile protocol for a service firm: truthful name/categories/services, every field completed, real photos, weekly posts, and staged edits — with the compliance rules that keep the profile out of suspension. Use when the trigger is 'GBP setup', 'optimize the Business Profile', or 'Google Business Profile audit'."
done_when:
  - grep:capabilities/skills/rig-revenue-gbp-protocol/SKILL.md:real hours \(never inflated
  - grep:capabilities/skills/rig-revenue-gbp-protocol/SKILL.md:Name = legal/registered name exactly
---

# GBP protocol (one mechanism)

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta. Excluded tactics named by clients (fake hours, stuffed
names, seeded reviews) are refused and logged. Completeness itself is the moat: "most businesses
fill out less than 50% of the fields" (CLAIM: aXhO5hhUqeE).

## Step 1. Name and categories

1. Name = legal/registered name exactly (DBA/rename for keyword-bearing names must be real).
   Stuffed names get flagged/suspended (CLAIM: iMQxbHm3HDw).
2. Primary category = the money service in the CUSTOMER's language ("AC repair near me" →
   "air conditioning repair service", not trade jargon — CLAIM: aXhO5hhUqeE). All applicable
   secondary categories, truthfully.
3. Stage category changes over days ("Google does not like a lot of rapid changes" — CLAIM:
   lrmG2i1zvWY).

## Step 2. Complete every field (truthfully)

Services (20-30 real ones grouped under categories — service count stabilizes map-pack presence,
CLAIM: aXhO5hhUqeE), description, real hours (never inflated — CLAIM: OovHMoIIWPg), products,
attributes (only what's true), accessibility, payment, Q&A (seed real questions with honest
answers), buttons. Real photos of the actual business/team/work.

## Step 3. Operating cadence

Weekly: 1 post ("mini SEO blog" — CLAIM: t53ujZ9bj28), 1 real photo, reply to every review
(rig-revenue-review-engine). Blog-to-GBP: compress a governed article to a <1500-char update with
the site link (CLAIM: c_ydTRcDqWs).

## Step 4. Monitoring routine

Check the map pin/address regularly — pin sabotage moves your listing with no notification, and
the repair is via public "suggest an edit", not the dashboard (CLAIM: 2Whv02wqoVY).

## done_when

- file:capabilities/skills/rig-revenue-gbp-protocol/SKILL.md
- grep:capabilities/skills/rig-revenue-gbp-protocol/SKILL.md:^## Step 2. Complete every field
- grep:capabilities/skills/rig-revenue-gbp-protocol/SKILL.md:refused
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-gbp-protocol/SKILL.md

## Provenance (videoIds)

t53ujZ9bj28, OovHMoIIWPg, iMQxbHm3HDw, 7y8MwUs2Sdw, aXhO5hhUqeE, lrmG2i1zvWY, c_ydTRcDqWs,
2Whv02wqoVY, kvrlyPiWxDs, AGPRNTRKBTw.
