---
name: linkedin-viral
description: >-
  LinkedIn Viral: the single front door for every LinkedIn job Mike Rodgers runs - viral reach, strategy, hooks, drafting, visuals, scoring, Eden scheduling, golden hour, comments, DMs and lead gen, profile, measurement, events, the Ideawake client lane and the job-search profile. JEV-FIRST MANDATE, findable at task start: every typed judgment here (hook ranking, post gate, comment gate, lane call, flop cause, boost screen) goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Applies the lane guard and hard gates, then routes to exactly one of 161 LinkedIn skills, with the Tommy Clark doctrine (79 videos, 2024-2026) as the playbook. Use for /linkedin-viral, "make this go viral", "write or fix a LinkedIn post", "why did my post flop".
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, viral, growth, meta-skill, router, eden, doctrine]
outcome: "content-publishing: every LinkedIn job enters one router that fixes the lane, loads exactly one right child skill, and applies the current doctrine and gates"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_routes.py
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_routes.py capabilities/skills/linkedin-viral/SKILL.md --min 30
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_routes.py --self-test
  - grep:capabilities/skills/linkedin-viral/SKILL.md:tommy-clark-doctrine
quality_floor: 0.6
metadata:
  purpose: meta-skill
  parent: when-growing-social-accounts
  routable-entries: "161"
---

# LinkedIn Viral (meta-skill)

## JEV-first mandate (read before anything else)

Where this rule lives: it is repeated in this skill's description, which Claude Code, Codex, Hermes, OMP, Prime Agent and Aside load into every session at start, and Mike's always-loaded AGENTS.md sends LinkedIn work through `when-growing-social-accounts`, whose first LinkedIn route is this skill. An agent meets the rule before it touches LinkedIn work.

Every typed judgment this skill forces goes to Jev (TypeSafe's System One) through `rig-s1gate` BEFORE any frontier LLM call. The typed judgments here: which hook wins, does a post pass, does a comment pass, which lane an ambiguous request belongs to, the most likely cause of a flop, and whether a post qualifies as a boost candidate.

- Command: `rig-s1gate check <rubric> --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json` with rubric `post.linkedin` (Lane B), `post.viral`, `post.eden` or `comment.linkedin`.
- A pass needs every required noul and confidence above 0.9; exactly 0.90 does not pass.
- **Fail closed:** if the classifier is down, errors, or the rubric is missing, the verdict is DEFERRED. DEFERRED is never a pass. Do not guess a verdict locally and do not substitute a frontier model's opinion; report DEFERRED and keep the item a draft.
- An advisory PASS is not permission to publish, send, boost or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id from `~/.rig/s1gate/decisions.db`.

One call for all LinkedIn work. This file fixes the lane, enforces the gates and routes; the doctrine lives in the children. Hierarchy: `when-growing-social-accounts` (all social) → **linkedin-viral** (all LinkedIn) → one child skill → at most one of its sub-skills.

## Step 0: Lane guard (always first)

| Lane | What it is | Rules that travel with it | Primary route |
|---|---|---|---|
| **B: RIG B2B** | Rodgers Intelligence Group: fractional CAIO, governed AI build studio | evidence-led, named receipts, no mascots; Mike's proprietary cast (Birch, Unit 7, The Coach, "Be more Birch") never appears | `~/.aside/u/0/skills/user/rig-daily-linkedin-post/SKILL.md` |
| **A: personal brand** | Mike's themed daily stream, generated in Eden | warm Ted Lasso register, pop-culture opening allowed, Birch Tuesday-only, The Coach only from behind or in silhouette | `~/.aside/u/0/skills/user/linkedin-weekly-rhythm/SKILL.md` |
| **Client: Ideawake** | Coby Skonord's account | the browser may be signed in as Coby: assert the handle before acting, never borrow Mike's voice, nothing fires without Mike's explicit client approval | `~/.aside/u/0/skills/user/ideawake-linkedin-weekly/SKILL.md` |
| **Job search** | Mike's profile and activity for recruiters | profile edits shown as exact before/after values, applied only after Mike approves | `~/.aside/u/0/skills/user/lucy-skills/SKILL.md` |
| **Minor (Jacob)** | anything about a 15-year-old | STOP. Not a LinkedIn growth lane; never auto-scheduled; per-post approval | `~/.aside/u/0/skills/user/jacob-x-growth/SKILL.md` |

If the lane is unclear, ask which lane. Never carry one lane's voice into another.

## Step 1: Hard gates (every lane, every job)

1. **Eden is the publisher of record** (`~/.aside/u/0/skills/user/eden-mcp/SKILL.md`). Postiz is retired; never route to the seven retired entries listed in `references/routing.md`.
2. **Gate-D:** publishing or scheduling a live post, sending DMs or connection requests in volume, paid boosts, and profile edits each need Mike's explicit yes for that item. Drafts, briefs and analysis are free.
3. **Generation belongs to Eden.** Agents source facts, rank hooks, write the brief, gate, and measure; Eden drafts copy and images. Feed Eden a real story, interview transcript or receipt, never a bare topic (Clark: no blank-to-draft AI).
4. **Jev first** for every typed judgment, per the mandate at the top of this file. DEFERRED when the classifier is down, never a guessed verdict. See `~/.aside/u/0/skills/user/s1gate/SKILL.md`.
5. **Comments on other people's posts are positive:** validate, add one real insight, optionally point to Mike's related post. Never AI-written comments.
6. **Account safety:** follow `~/.aside/u/0/skills/user/linkedin-site-mechanics/SKILL.md` throttles, assert the signed-in handle before any outward action, and prefer a reasoned refusal over a volume ask that trips limits.
7. **Every number is a sourced receipt.** No invented metrics, clients or quotes.

## Step 2: Route the job (load exactly one child)

| Job | Load this | Sub-skill if needed |
|---|---|---|
| The viral playbook itself: what works in 2026 and why | `~/Developer/rig-capabilities/capabilities/skills/tommy-clark-doctrine/SKILL.md` | its references/ by topic |
| Daily unattended viral run (content, distribution, measurement) | `~/.hermes/skills/rig-linkedin-virality/SKILL.md` | its P1/P2/P3 children; check the routine is actually running first |
| Whole funnel, post through monetization | `~/.aside/u/0/skills/user/linkedin-optimizer/SKILL.md` | its 13 lg-* skills |
| Content process end to end (source, plan, draft, critique, publish, amplify, measure) | `~/.aside/u/0/skills/user/linkedin-growth-os/SKILL.md` | lg-* |
| Hooks, visuals, growth tactics from the creator corpus | `~/.aside/u/0/skills/user/linkedin-influencer-os/SKILL.md` | li-hooks, li-visuals, li-growth |
| Cross-account growth doctrine and lessons library | `~/.aside/u/0/skills/user/linkedin-growth-engine/SKILL.md` | |
| Positioning, pillars, which game to play | tommy-clark-doctrine → `references/positioning.md` | `~/.aside/u/0/skills/user/content-pillar-architect/SKILL.md` |
| Week plan or calendar | Lane A: linkedin-weekly-rhythm; Lane B: rig-daily-linkedin-post; any lane: `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-plan/SKILL.md` | lg-plan/sub/format-mix.md |
| Post ideas | `~/.aside/u/0/skills/user/content-matrix/SKILL.md` | Lane A pop-culture collisions: `~/.aside/u/0/skills/user/rig-collision-engine/SKILL.md` |
| Hooks | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/li-hooks/SKILL.md` | hook-families, hook-selection; lever checklist in tommy-clark-doctrine/references/hooks-and-media.md |
| Draft a post | Lane B: `~/Developer/rig-capabilities/capabilities/skills/rig-write-linkedin/SKILL.md`; Lane A: linkedin-weekly-rhythm into Eden; any lane: `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-draft/SKILL.md` | body-craft, hook-lab |
| Visuals, carousels, video (briefs for Eden) | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/li-visuals/SKILL.md` | eden-brief-templates, carousel-architecture, image-system, video-shorts |
| Score or gate a draft | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-critique/SKILL.md` plus Jev | scorecard; `~/Developer/rig-capabilities/capabilities/harnesses/hB-04-linkedin-post-session.yaml` |
| Voice and de-slop | `~/Developer/rig-capabilities/capabilities/skills/rig-communications-voice/SKILL.md` | `~/.aside/u/0/skills/user/anti-slop/SKILL.md` |
| Schedule or publish | eden-mcp (drafts; live only on Mike's yes) | lg-publish |
| Golden hour and post-launch | `~/.aside/u/0/skills/user/linkedin-post-launch/SKILL.md` | lg-amplify/sub/golden-hour.md; Clark's checklist in distribution-and-algorithm.md |
| Comment on other people's posts | `~/.hermes/commands/comment-engine.md` with linkedin-site-mechanics | lg-amplify/sub/borrowed-attention.md |
| Profile | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-profile/SKILL.md` (brand lanes); lucy-skills (job lane) | headline-formulas, about-and-featured, company-page |
| Qualify leads and warm signals | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-qualify/SKILL.md` | hot-signals, icp-fit-card, intent-tracking |
| DMs and follow-up | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-convert/SKILL.md` | opener-recipes, dm-sequences, followup-cadence, pre-call-nurture; `~/.hermes/skills/linkedin-followup-sequence/SKILL.md` |
| Offer, monetization, lead magnet | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-monetize/SKILL.md` | offer-construction, owned-audience |
| Measure, or diagnose a flop | `~/.aside/u/0/skills/user/linkedin-analytics-tracker/SKILL.md` | lg-measure; Clark's diagnosis order in distribution-and-algorithm.md |
| Scrape posts or creators for evidence | `~/.hermes/skills/rig-linkedin-scrape/SKILL.md` | `~/.aside/u/0/skills/user/scrapers/SKILL.md` |
| Repurpose off LinkedIn | `~/.aside/u/0/skills/user/linkedin-cross-platform/SKILL.md` | lg-distribute subs |
| Conference or event surge | `~/.aside/u/0/skills/user/linkedin-event-engagement/SKILL.md` | |
| Taki marketing rules on RIG posts | `~/.aside/u/0/skills/user/rig-linkedin-taki/SKILL.md` | |

Anything not in this index: `references/routing.md` lists every routable entry by job with its path, plus the retired, broken and adjacent-lane lists.

## Step 3: Apply the viral core

For any create, fix or diagnose job, run `references/viral-core.md` (the post recipe, the week, the daily engine, the weekly review) before the child's own checklist. Where Clark's doctrine and a RIG rule conflict, the RIG rule wins and the conflict is named in the output.

## Duplicates: which one wins

- **Hooks:** li-hooks for LinkedIn. content-hook-generator for cross-platform work. hook-generator (Hermes) produces formula hooks, which Clark's 2026 evidence says now read as AI: raw material only.
- **Drafting:** rig-write-linkedin (Lane B, engine plus gates) first; lg-draft for the process view. post-writer and post-formatter are generic third-party formats: only when Mike asks for them.
- **Virality:** this skill is the front door. rig-linkedin-virality is the daily unattended run beneath it. rig-virality-predictor is an empty folder (broken).
- **Voice:** anti-slop and slopmonster are the same tool; use anti-slop.
- **Profile:** lg-profile for brand lanes, lucy-skills for the job lane, profile-optimizer only on request.
- **Scraping:** rig-linkedin-scrape for LinkedIn data, scrapers for everything else.
- **Studios:** rig-linkedin-agency is the 10-subagent factory; the linkedin-studio and linkedin-agency folders are empty (broken).

## Calling it

- Claude Code, Codex, Hermes, OMP, Desktop Commander: `/linkedin-viral <task>`, or the installed skill loads on LinkedIn tasks.
- Aside: installed account skill `linkedin-viral`.
- Eden: `/linkedin-viral` in Eden chat (imported skill; the single-file Eden edition lives at `eden/linkedin-viral-eden.md`).
- Install paths and the update procedure: `references/harness-usage.md`.

## Done-test

`python3 scripts/check_routes.py` is GREEN only when every path in `references/routing.md` resolves and the table carries at least 40 routes. Run it again against this SKILL.md with `--min 30`. `--self-test` plants a dangling route and a truncated table in temp copies and passes only if both go RED while the real table stays GREEN.
