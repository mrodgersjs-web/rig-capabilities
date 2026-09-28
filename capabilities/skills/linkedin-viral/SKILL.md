---
name: linkedin-viral
description: >-
  LinkedIn Viral: the single front door for every LinkedIn job Mike Rodgers runs. It fixes the lane (RIG B2B, personal brand, Ideawake client, job search), enforces the hard gates, and routes to exactly one of 12 stage skills (strategy, plan, hooks, draft, visuals, gate, launch, engage, outreach, profile, measure, distribute) that merge 257 audited LinkedIn assets, with the Tommy Clark doctrine (79 videos, 2024-2026) as the playbook. JEV-FIRST MANDATE, findable at task start: every typed judgment here (hook ranking, post gate, comment gate, lane call, flop cause, boost screen) goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Use for /linkedin-viral, "make this go viral", "write or fix a LinkedIn post", "why did my post flop".
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, viral, growth, meta-skill, router, eden, doctrine]
outcome: "content-publishing: every LinkedIn job enters one router that fixes the lane, loads exactly one right child skill, and applies the current doctrine and gates"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_routes.py
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_routes.py capabilities/skills/linkedin-viral/SKILL.md --min 20
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py --all
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_routes.py --self-test
  - grep:capabilities/skills/linkedin-viral/SKILL.md:tommy-clark-doctrine
quality_floor: 0.6
metadata:
  purpose: meta-skill
  parent: when-growing-social-accounts
  stages: "12"
  audited-assets: "257"
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

## Step 2: Route the job to ONE stage

Every LinkedIn job belongs to exactly one of 12 stage skills. Each stage merged the best of every legacy skill for its job (125 sources, conflicts resolved and logged in its `references/ledger.md`) and lists the tools, agents and runners it calls. Load the stage, follow its procedure, and load at most one of its sub-skills.

| Job | Stage | Path |
|---|---|---|
| Positioning, golden question, content-market fit, pillars, lanes, voice, the 2026 doctrine | lv-strategy | `~/Developer/rig-capabilities/capabilities/skills/lv-strategy/SKILL.md` |
| Sourcing ideas and facts, idea engines, weekly and monthly calendar, cadence, lane rhythms | lv-plan | `~/Developer/rig-capabilities/capabilities/skills/lv-plan/SKILL.md` |
| Openings: levers, three variants, cold-reader rule, Jev ranking, A/B pairs | lv-hooks | `~/Developer/rig-capabilities/capabilities/skills/lv-hooks/SKILL.md` |
| Body, post architecture, format catalog, CTA, threads, the Eden brief | lv-draft | `~/Developer/rig-capabilities/capabilities/skills/lv-draft/SKILL.md` |
| Media: real photo first, Eden image briefs, carousels, video, Lane A cast rules | lv-visuals | `~/Developer/rig-capabilities/capabilities/skills/lv-visuals/SKILL.md` |
| Pre-publish gate: Jev rubrics, post gate, scorecard and critic, voice law, anti-slop, claim hygiene | lv-gate | `~/Developer/rig-capabilities/capabilities/skills/lv-gate/SKILL.md` |
| Eden scheduling, posting slot, golden hour, algorithm model, save assets, boosts, planned peaks | lv-launch | `~/Developer/rig-capabilities/capabilities/skills/lv-launch/SKILL.md` |
| Comments on other people's posts, replies on Mike's posts, pinned first comment, target lists | lv-engage | `~/Developer/rig-capabilities/capabilities/skills/lv-engage/SKILL.md` |
| Connections, lead sourcing and qualification, warm signals, DMs, follow-up, campaigns, offers | lv-outreach | `~/Developer/rig-capabilities/capabilities/skills/lv-outreach/SKILL.md` |
| Profile as landing page, headline, About and Featured, company page, job-search profile | lv-profile | `~/Developer/rig-capabilities/capabilities/skills/lv-profile/SKILL.md` |
| Daily and weekly tracker, KPI loop, attribution, outlier review, scraping for evidence | lv-measure | `~/Developer/rig-capabilities/capabilities/skills/lv-measure/SKILL.md` |
| Beyond the feed: LinkedIn Groups, Reddit, Substack, X, trade press, newsletter | lv-distribute | `~/Developer/rig-capabilities/capabilities/skills/lv-distribute/SKILL.md` |

A whole post end to end runs: lv-plan → lv-hooks → lv-draft → lv-visuals → lv-gate → lv-launch → lv-engage → lv-measure (lv-strategy first only when positioning is unsettled). Each stage hands the next a named artifact.

## Runners: lanes and schedules that call the stages

| Runner | Lane or schedule | Path |
|---|---|---|
| rig-daily-linkedin-post | Lane B daily post | `~/.aside/u/0/skills/user/rig-daily-linkedin-post/SKILL.md` |
| linkedin-weekly-rhythm | Lane A themed days (Eden) | `~/.aside/u/0/skills/user/linkedin-weekly-rhythm/SKILL.md` |
| ideawake-linkedin-weekly | client lane (Coby's account) | `~/.aside/u/0/skills/user/ideawake-linkedin-weekly/SKILL.md` |
| lucy-skills | job-search lane | `~/.aside/u/0/skills/user/lucy-skills/SKILL.md` |
| linkedin-event-engagement | conference surges | `~/.aside/u/0/skills/user/linkedin-event-engagement/SKILL.md` |
| rig-linkedin-virality | daily unattended run (Hermes: P1 content, P2 distribution, P3 measurement) | `~/.hermes/skills/rig-linkedin-virality/SKILL.md` |

Runners keep working as they are. Each stage's Tools and runners table says which runners should call it; re-pointing a runner is a separate, approved change.

## Doctrine

`~/Developer/rig-capabilities/capabilities/skills/tommy-clark-doctrine/SKILL.md` holds the dated rule ledger behind every stage (current 2026 rules vs superseded ones, each tied to a video ID).

## What happened to the old skills

- **125 legacy skills:** content merged into a stage; superseded for routing; still on disk because agents and crons load some of them by name.
- **67 tools and 35 runners:** still called, now listed inside their stage.
- **16 old routers** (linkedin-growth-os, linkedin-optimizer, linkedin-influencer-os and others): superseded by this file.
- **7 Postiz-era skills:** retired. **6 broken or phantom entries:** reported, never routed.
- **Nothing was deleted.** The proposed deletions wait for Mike's approval in `~/.rig/prune/linkedin-viral-2026-09-28/condemnation.md`.
- Full map: `references/routing.md` (every asset with its stage and role) and `references/stage-map.json`.

## Calling it

- Claude Code, Codex, Hermes, OMP, Desktop Commander: `/linkedin-viral <task>`, or the installed skill loads on LinkedIn tasks.
- Aside: installed account skill `linkedin-viral`.
- Eden: `/linkedin-viral` in Eden chat (imported skill; the single-file Eden edition lives at `eden/linkedin-viral-eden.md`).
- Install paths and the update procedure: `references/harness-usage.md`.

## Done-test

`python3 scripts/check_routes.py` is GREEN only when every path in `references/routing.md` resolves and the table carries at least 40 routes. Run it again against this SKILL.md with `--min 20`. `python3 scripts/check_ledger.py --all` is GREEN only when all 12 stages account for every asset assigned to them. `--self-test` plants a dangling route and a truncated table in temp copies and passes only if both go RED while the real table stays GREEN.
