---
name: design-studio-os
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate
  (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict.
  RIG Design Studio OS: the single front door for all design work (websites, landing pages, redesigns,
  brand identity, UI systems, UX flows, motion and 3D, imagery, AI design workflows, conversion copy,
  build and ship, critique, design business). Picks the mode (BUILD, REDESIGN, CRITIQUE, FIX, LEARN),
  routes to exactly one of 15 main skills at a time (each with sub-skills), runs the matching harness
  (meta ds-studio-session over 5 mains and 4 sub gates, plus hC-01..hC-12), loops (meta ds-mission-loop,
  4 mains, 3 subs) and dormant hooks (meta ds-session-start, 3 mains, 3 subs), conducted by the
  ds-director meta agent over 7 agents and 8 sub-agents. Backed by ds-doctrine (laws cited
  CLAIM(<videoId>@mm:ss) from the RIG design YouTube corpus: 6,757 captured transcripts across 22 channels
  (Mike's top-10 subscribed design channels weighted 2x), 240 of the densest how-to videos deep-distilled
  into 822 laws and 383 good-versus-bad pairs, with 1,958 eligible videos queued in docs/BACKLOG.md) and
  ds-exemplars (looks like / does not pair cards). Use for /design-studio, "design a site", "redesign this", "critique this page",
  "brand identity", "make this look better", or any design job.
tier: meta
owner: rig-intelligence
status: Stable
acl: internal
outcome: "design-ux: every design job enters one router that fixes the mode, loads one main skill at a time, cites corpus law, is judged by an agent that did not build it, and stops at Gate-D before anything ships"
done_when:
  - cmd:python3 tools/claims_check.py
  - cmd:python3 tools/claims_check.py --plant
  - cmd:python3 tools/check_family.py
  - cmd:python3 tools/check_family.py --self-test
  - cmd:python3 tools/hook_cases.py
quality_floor: 0.6
---

# RIG Design Studio OS (meta-skill)

JEV FIRST, and it binds every design job under this skill: an agent whose only context is this excerpt
sends semantic triage, routing and classification to the rig-s1gate Jev path BEFORE any frontier LLM
call. Mode routing, brief readiness, craft choices, screen verdicts and release readiness are typed
judgments, not vibes. When the fast classifier is unavailable: DEFER, never guess a verdict locally. A
required signal passes only above 0.9; below that the stage does not advance, and an uncalibrated
ESCALATE is a held transition.

## Load surface

This meta-skill is an always-loaded task-start surface for design work: the `/design-studio` command in
`~/.rig/universal-commands/` loads it first, the dormant `ds-session-start` hook prints its path at
session start once wired, `ds-director` loads it before its first action, and `when-designing-interfaces`
plus `when-designing-websites` route design requests here. It is the front door for the family, not a
deep reference an agent must already know about. All paths are relative to the meta repo
`~/Developer/rig-design-studio-os`.

## Decision routing (binding)

First match wins: CODE (contrast math, citation gate, lint, hooks) -> JEV -> SYSTEM 2 (making the design)
-> HUMAN (Gate-D: deploy, publish, push, purchase, client send).

| typed judgment | Jev rubric (nearest existing, advisory until calibrated) |
|---|---|
| which mode, which main skill, which exemplar | jev.skill-router, jev.triage |
| is the brief ready | plan.readiness |
| does the rendered screen pass | ui.design (plus `advisor-plus judge-image`) |
| is the page buyer-ready | website.buyer, web.market |
| is the build diff safe | code.diff, code.review |
| does a studio file still carry its mandate | doctrine.surface |

## Step 0: mode guard

| mode | trigger | main harness | end artifact |
|---|---|---|---|
| BUILD | new site, landing page, new brand | ds-website-build, ds-landing-page, ds-brand-identity-session | served build + critique + Gate-D request |
| REDESIGN | "redo", "modernize", existing URL | ds-redesign | before/after captures, critique, Gate-D request |
| CRITIQUE | "audit", "what's wrong", "does this look like AI slop" | ds-critique-session | findings table with laws cited |
| FIX | one named defect ("type feels off", "contrast") | the gate sub-harness for that stage | fixed artifact + recheck |
| LEARN | "teach me", "what do the creators say about X" | none | answer from ds-doctrine with citations |

The flagship `rodgersintelligence.com` is extended, never rebuilt: any job touching `flagship/` runs
ds-redesign with the locks gate and `ds-locks-guard`.

## Main skills (load one at a time)

| # | main skill | owns | agent | load when |
|---|---|---|---|---|
| 1 | ds-discovery | brief, buyer, references, sitemap, industry adapter | ds-strategist | every BUILD/REDESIGN, first |
| 2 | ds-brand-identity | logo, brand system, visual voice | ds-brand-designer | new brand or rebrand |
| 3 | ds-typography | scale, pairing, readability | ds-brand-designer | any page with text |
| 4 | ds-color | palette, tokens, contrast, dark mode | ds-brand-designer | any page with color |
| 5 | ds-layout | grid, hierarchy, spacing, responsive | ds-ui-designer | any multi-section page |
| 6 | ds-ui-system | components, states, tokens, design system | ds-ui-designer | apps, dashboards, reusable UI |
| 7 | ds-ux | flows, IA, forms, onboarding, usability | ds-ui-designer | anything with a task to complete |
| 8 | ds-motion-3d | interactions, scroll narrative, 3D, motion budget | ds-motion-designer | brief calls for motion |
| 9 | ds-imagery | art direction, photo, illustration, AI images, provenance | ds-brand-designer | any imagery |
| 10 | ds-ai-workflow | AI design tool stack, prompt-to-site, Figma/Framer AI | ds-ai-design-engineer | AI-assisted design or build |
| 11 | ds-conversion-copy | hero, proof, CTA, page copy | ds-copywriter | any page with an ask |
| 12 | ds-build-ship | Webflow/Framer/code build, handoff, responsive QA, performance | ds-ai-design-engineer | before anything leaves the machine |
| 13 | ds-critique | taste, anti-slop, accessibility, screen judging | ds-critic (independent) | always, last |
| 14 | ds-business | pricing, proposals, client process and boundaries | ds-strategist | quotes, clients, positioning |
| 15 | ds-career | portfolio, positioning and getting hired as a designer | ds-strategist | portfolio or career questions |

Reference skills: `ds-doctrine` (every law by stage, cited) and `ds-exemplars` (looks like / does not
cards). Typical BUILD order: 1 -> 2 -> 3, 4, 5 -> 6, 7 -> 8, 9 -> 10 -> 11 -> 12 -> 13.

## Org chart

```
ds-director (META agent: routes and assembles, never designs)
|- ds-strategist          1, 14    sub: ds-reference-hunter
|- ds-brand-designer      2, 3, 4, 9    sub: ds-type-pairer, ds-contrast-checker
|- ds-ui-designer         5, 6, 7
|- ds-motion-designer     8
|- ds-ai-design-engineer  10, 12
|- ds-copywriter          11    sub: ds-slop-linter
|- ds-critic              13 (independent)    sub: ds-screen-capturer, ds-image-judge, ds-citation-verifier
`- ds-exemplar-retriever  (sub, reports to ds-director)
```

| kind | meta | main | sub |
|---|---|---|---|
| skills | design-studio-os | 15 stage skills + ds-doctrine + ds-exemplars | references/*.md inside each main (103 in total) |
| agents | ds-director | 7 | 8 |
| harnesses | ds-studio-session | ds-website-build, ds-landing-page, ds-redesign, ds-brand-identity-session, ds-critique-session (+ hC-01..hC-12 in rig-capabilities) | ds-gate-brief, ds-gate-craft, ds-gate-critique, ds-gate-ship |
| loops | ds-mission-loop | ds-critique-revise-loop, ds-ui-judge-loop, ds-corpus-refresh-loop, ds-exemplar-learning-loop | ds-contrast-fix-loop, ds-slop-rewrite-loop, ds-citation-fix-loop |
| hooks (DORMANT until Mike wires them) | ds-session-start | ds-pre-publish-gate-d, ds-locks-guard, ds-pre-write-slop-lint | ds-citation-check, ds-contrast-check, ds-image-provenance |

## Hard rules
- No brief, no pixels. State the project goal in one sentence before visual work; if it will not fit in one
  sentence the brief is not ready. CLAIM(xM-0aeHbk5Y@01:09, wCiM8jYE5yg@01:54, mXLPMFo6KYM@01:54)
- On a redesign, name the defects in writing first and change only what those defects require; the smallest
  edit that fixes the defect wins over a restyle. CLAIM(k2DWClcoHFI@06:10, XZf5A0wcruE@00:16)
- Cite or label. Doctrine statements carry CLAIM(<videoId>@mm:ss) copied from ds-doctrine; everything else
  is labeled own reasoning. Never cite from memory.
- Creator numbers are claims. Tool tips are dated. Where creators disagree, say so and test.
- The builder never judges its own work. Screens are judged from real captures, never from source.
- Nothing outward without Gate-D. `ds-pre-publish-gate-d` enforces it once wired.
- Raw transcripts never enter a repo (creator copyright). Skills paraphrase and cite.

## Invocation
`/design-studio <mode> <target>`: `/design-studio build "landing page for RIG workflow review"`,
`/design-studio critique https://rodgersintelligence.com`, `/design-studio fix "hero contrast"`,
`/design-studio learn "font pairing"`.

## Maintenance
- Corpus refresh: `ds-corpus-refresh-loop` (harvest.sh for top-10 slugs, build_manifest.py,
  tag_stages.py, distill new dense how-tos).
- Gates: `tools/claims_check.py` (+`--plant`), `tools/check_family.py` (+`--self-test`),
  `tools/hook_cases.py`, `studio-exemplars/scripts/build_pairs.py --check`.
- Publish: `tools/sync_to_capabilities.py` copies this family into rig-capabilities and the Aside skills
  root, then diffs.
