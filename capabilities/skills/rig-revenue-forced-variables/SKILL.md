---
name: "rig-revenue-forced-variables"
description: "Make templated content non-commodity by injecting the firm's own proprietary variables — their data, tests, first-hand cases, specific mistakes, what-they-tell-every-client. Use when the trigger is 'make this non-commodity', 'forced variables', 'this reads like everything else', or before any templated content batch."
done_when:
  - grep:capabilities/skills/rig-revenue-forced-variables/SKILL.md:variable must change the ANSWER, not decorate it
  - grep:capabilities/skills/rig-revenue-forced-variables/SKILL.md:## Step 4. Vary honestly, never deceptively
---

# Forced-variables injection (one mechanism)

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta. Commodity pages get de-indexed or ignored; the variable is
the difference between commodity and citation gold (CLAIM: BAB4lqxBZ6Y, zuV067a21g4). This is
the anti-doorway mechanism — a service×city page without a variable does not ship.

## Step 1. Choose the commodity concept

Name the generic topic explicitly ("seven tips for first-time home buyers" class — CLAIM:
BAB4lqxBZ6Y). If you cannot name it, the draft is probably already generic.

## Step 2. Gather the firm's variables

At least one, prefer three: a proprietary data point ("we reviewed 240 matters; 73% of outcomes
turned on X"), what-we-tested, an unexpected finding, a first-hand story (approved for use), a
specific expensive mistake, or "what I tell every client". YMYL cases need professional sign-off
before use.

## Step 3. Build the template

Template = generation prompt + markdown outline with the variables as forced placeholders. The
variable must change the ANSWER, not decorate it — a number that changes the advice is the bar.

## Step 4. Vary honestly, never deceptively

Per-run variation exists so pages aren't near-duplicates (intro, format, angle, length) — but
variation is never used to disguise template farms or evade detection (excluded tactic). If the
only way to fill the calendar is more template output, stop and re-scope instead.

## done_when

- file:capabilities/skills/rig-revenue-forced-variables/SKILL.md
- grep:capabilities/skills/rig-revenue-forced-variables/SKILL.md:^## Step 2. Gather the firm's variables
- grep:capabilities/skills/rig-revenue-forced-variables/SKILL.md:excluded tactic
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-forced-variables/SKILL.md

## Provenance (videoIds)

BAB4lqxBZ6Y, zuV067a21g4, 5WLczj447Nw, kLvp3dqPT7s, IIUbbh1xtg8, IjmlFzoo5VU, G6nIFhoNSwE.
