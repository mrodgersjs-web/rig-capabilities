---
name: "rig-revenue-seo-council"
description: "Run the adversarial five-role review before a keyword target or page ships: intent analyst, SERP competitor, on-page technician, contrarian, searcher — then a judge weighs all five. Use when the trigger is 'roast this keyword', 'audit this page', 'pre-publish review', or 'council'."
done_when:
  - 'grep:capabilities/skills/rig-revenue-seo-council/SKILL.md:[a] single model pretending to be five voices'
  - 'grep:capabilities/skills/rig-revenue-seo-council/SKILL.md:[S]HIP / REVISE / KILL'
---

# SEO Council (one mechanism)

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta. "AI natively wants to give us a rosy, shiny output" — the
contrarian role exists to puncture it (CLAIM: elkBF7ej5pc).

## Step 1. Take the input

A keyword ("roast") or a live page URL ("audit") plus the firm profile and the target buyer.

## Step 2. Run five independent roles

1. **Intent analyst** — what does the searcher actually want; is this target buyer-intent
   (rig-revenue-buyer-intent-screen)?
2. **SERP competitor** — who ranks now, can the firm realistically beat them, on what grounds?
3. **On-page technician** — will the page be built right (titles, links, schema, speed)?
4. **Contrarian** — assume it fails: find the fatal flaw first (commodity risk, compliance risk,
   unsupported claim).
5. **Searcher** — plays the person searching: do they get what they want in seconds?

## Step 3. Judge

The judge weighs all five and delivers a decisive verdict: SHIP / REVISE / KILL, with the fixes
ranked. Roles run independently (separate contexts) — a single model pretending to be five voices
in one breath is not a council.

## Step 4. Feed forward

Verdict + fixes go to the producing skill (rig-revenue-weekly-content-run, rig-revenue-money-pages,
rig-revenue-ai-citation-gaps). Kill verdicts are wins: they stop commodity or risky pages before
the gate.

## done_when

- file:capabilities/skills/rig-revenue-seo-council/SKILL.md
- grep:capabilities/skills/rig-revenue-seo-council/SKILL.md:^## Step 2. Run five independent roles
- grep:capabilities/skills/rig-revenue-seo-council/SKILL.md:Contrarian
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-seo-council/SKILL.md

## Provenance (videoIds)

v8KQk3YVG7w, Z6eG91ZB_HE, elkBF7ej5pc, 3B2W4wCLOYo, _5Nne2mrXIo (sparring-partner rule).
