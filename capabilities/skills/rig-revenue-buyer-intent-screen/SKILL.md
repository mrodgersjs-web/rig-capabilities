---
name: "rig-revenue-buyer-intent-screen"
description: "Score keyword/prompt candidates on buyer intent — 'where/how much/hire/book' beats 'how' — so content targets money, not vanity traffic. Use when the trigger is 'which keywords', 'is this keyword worth it', 'prioritize these queries', or 'buyer intent check'."
done_when:
  - grep:capabilities/skills/rig-revenue-buyer-intent-screen/SKILL.md:## Step 1. Classify each candidate
  - grep:capabilities/skills/rig-revenue-buyer-intent-screen/SKILL.md:## Step 2. Score and rank
---

# Buyer-intent screen (one mechanism)

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta. "The real metric that you need to focus on is money" —
"how much" and "where" searchers want to hire; "how" searchers want to DIY (CLAIM:
-miheonBtb0, Xc7L0UWLS54).

## Step 1. Classify each candidate

- TRANSACTIONAL (keep, top priority): "where to [service]", "how much does [service] cost",
  "[service] near me", "book/hire/consult", "emergency/urgent", "price/cost/estimate"
- COMMERCIAL (keep): "best [service] in [city]", "X vs Y", "X alternatives", "[firm type] for
  [client type]", reviews/trust queries
- INFORMATIONAL (deliberate only): "how to...", explainers — publish only with a named purpose
  (top-of-funnel for a silo, or the question is the buyer's pre-hire research)
- DIY (skip for service firms): anything the searcher wants to do themselves

## Step 2. Score and rank

Rank by intent first, volume second ("volume is the applause, intent is the cash register" —
CLAIM: drbVubTciUw). Ghost keywords — zero-volume high-intent phrases — convert with no
competition (CLAIM: 0KncRcCsO7A); keep them.

## Step 3. Map to assets

Each kept query maps to exactly one asset type: money page (transactional), comparison/decision
page (commercial), answer page (informational with purpose). Feed the map into
rig-revenue-weekly-content-run and rig-revenue-money-pages.

## done_when

- file:capabilities/skills/rig-revenue-buyer-intent-screen/SKILL.md
- grep:capabilities/skills/rig-revenue-buyer-intent-screen/SKILL.md:^## Step 1. Classify each candidate
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-buyer-intent-screen/SKILL.md

## Provenance (videoIds)

8UuWerWzHzI, Xc7L0UWLS54, -miheonBtb0, gZpTGHowQ0Q, drbVubTciUw, 0KncRcCsO7A, 0uM4My9AITw,
hYR-_LSXbI0, qU_11OMBhPM.
