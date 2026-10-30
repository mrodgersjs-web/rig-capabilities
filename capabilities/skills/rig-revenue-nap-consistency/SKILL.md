---
name: "rig-revenue-nap-consistency"
description: "Audit and repair name/address/phone/hours consistency across every listing surface character-by-character, because discrepancies make machines uncertain. Use when the trigger is 'NAP audit', 'citations inconsistent', 'listing cleanup', or 'name/address mismatch'."
done_when:
  - 'grep:capabilities/skills/rig-revenue-nap-consistency/SKILL.md:^## Step 2. Character-level diff'
  - 'grep:capabilities/skills/rig-revenue-nap-consistency/SKILL.md:[n]ever silently skip'
---

# NAP consistency audit (one mechanism)

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta. "Instead of company, it's abbreviated to co... leads to
uncertainty when it comes to AI" (CLAIM: t53ujZ9bj28). "Even a minor variation hurts" (CLAIM:
aXhO5hhUqeE).

## Step 1. Inventory every surface

GBP, Bing Places, Apple Maps, Yelp, Foursquare, Yellow Pages, BBB, industry directories
(healthgrades-class for clinics, bar/association directories for law, state boards for CPA),
aggregators, site footer/contact/about, social profiles. 10-15 real directories typical (CLAIM:
7y8MwUs2Sdw).

## Step 2. Character-level diff

Compare name, address, phone, hours across all surfaces against one canonical form. "Suite" vs
"ste", "LLC" on one listing only, a moved office, an old number — each is a defect. Output: table
of surface × defect × exact fix.

## Step 3. Fix and de-dupe

1. Apply fixes surface-by-surface (staged where platforms are change-sensitive).
2. Close/dispute stale duplicates and dead listings. Suppression beats ghosts.
3. Report what cannot be fixed (locked accounts, unresponsive platforms) — never silently skip.

## Step 4. Keep it true

The canonical form is the real business reality. If a client wants the address "adjusted" for
ranking (co-working shell addresses, fake suites), that is the excluded-tactic line — refuse and
log per rig-revenue-meta.

## done_when

- file:capabilities/skills/rig-revenue-nap-consistency/SKILL.md
- grep:capabilities/skills/rig-revenue-nap-consistency/SKILL.md:^## Step 2. Character-level diff
- grep:capabilities/skills/rig-revenue-nap-consistency/SKILL.md:refuse
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-nap-consistency/SKILL.md

## Provenance (videoIds)

t53ujZ9bj28, d0bZYfP4QXw, 0l_weqm-GX4, 7y8MwUs2Sdw, aXhO5hhUqeE, 15s8vD5maPc, ZiH1vVGKXsI,
AGPRNTRKBTw.
