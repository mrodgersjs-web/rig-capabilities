---
name: ss-growth-os
description: >-
  Substack Growth OS: the single front door for every Substack job Mike Rodgers runs (rigoperator.substack.com, the RIG publication). It fixes the publication and lane, enforces the hard gates, and routes to exactly one of 12 stage skills (strategy, plan, package, write, publish, gate, notes, network, distribute, convert, bestseller, measure), backed by substack-doctrine: laws distilled from 914 YouTube transcripts across 27 Jev-screened Substack-growth and Substack-bestseller channels, every law cited to a video id. The goal Mike set on 2026-09-28 is the Substack Bestseller badge (100 paid subscribers) within 12 months; ss-bestseller owns that track. JEV-FIRST MANDATE, findable at task start: every typed judgment here (positioning, title ranking, note gate, peer fit, offer check, flop cause) goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Use for /ss-growth-os, "grow my Substack", "amplify my Substack posts", "write a Substack Note", "why is nobody subscribing". Never publishes from here.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [substack, newsletter, growth, meta-skill, router, doctrine]
outcome: "content-publishing: every Substack job enters one router that fixes the publication, loads exactly one stage skill, and applies corpus doctrine and gates before anything goes public"
done_when:
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/claims_check.py
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/claims_check.py --plant
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/check_family.py --self-test
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/build_family.py --check
quality_floor: 0.6
metadata:
  purpose: meta-skill
  parent: when-growing-social-accounts
  stages: "11"
  corpus: "data/corpora/substack: 914 transcripts, 27 channels, 4.6M words (808 growth wave + 106 bestseller wave, 2026-09-28)"
  goal: "Substack Bestseller (100 paid subscribers) within 12 months of 2026-09-28"
---

# Substack Growth OS (meta-skill)

## JEV-first mandate (read before anything else)

Where this rule lives, so an agent meets it before touching Substack work: it is repeated in this skill's description, which Claude Code, Codex, Hermes, OMP, Prime Agent and Aside load into every session at start; Mike's always-loaded `~/.aside/u/0/AGENTS.md` (first section, "JEV before done") mandates Jev for every typed judgment; and `when-growing-social-accounts`, the social router, lists this skill first for any Substack job. Every ss-* stage repeats the mandate as the first section of its body and in its description.

Every typed judgment this family forces goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call: which positioning wins, which title wins, does a note or issue pass, is a peer publication a fit, is an offer sound, is a stats movement real.

- Command: `~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`. No Substack-specific rubric exists yet; each stage names the nearest existing one (`idea.solid`, `plan.readiness`, `post.viral`, `website.buyer`, `offer.eval`, `signal.performance`), all advisory until calibrated.
- A pass needs every required noul and confidence above 0.9; exactly 0.90 fails.
- **Fail closed:** classifier down, erroring or rubric missing = DEFERRED. Never a guessed verdict, never a frontier model's opinion in its place.
- An advisory PASS is not permission to publish, send, restack, recommend or spend.
- A claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

Hierarchy: `when-growing-social-accounts` (all social) → **ss-growth-os** (all Substack) → one stage skill → at most one of its sub-skills. Doctrine: `substack-doctrine`.

## Step 0: Publication and lane guard (always first)

| Publication | Owner account | Status | Route |
|---|---|---|---|
| **rigoperator.substack.com** ("Mike's Substack") | Substack account on rodgemd1@gmail.com | the RIG publication: 9 posts, ~2 subscribers (2026-09-28) | this family |
| **mikerodgers317.substack.com** (also "Mike's Substack") | Substack account on mike@rodgersintelligence.com | duplicate; carries one copy of Wax On. Which publication is canonical is **Mike's open decision** | no growth work until he picks |

| Lane | Rule |
|---|---|
| RIG B2B (default) | evidence-led, receipts, Mike's voice; no Lane A cast (Birch, Unit 7, The Coach) |
| Minor (Jacob) | STOP. The rigoperator post "I named my AI system after my 15-year-old son" is Lane C: never amplified, restacked or scheduled without Mike's per-post yes |
| Client (Ideawake / Coby) | not a Substack lane; never publish client material here |

Assert the signed-in Substack account before any read of owner pages or any write: open https://substack.com/settings and confirm rodgemd1@gmail.com. As of 2026-09-28 21:10 MT the Aside browser is signed in as rodgemd1@gmail.com (the owner); earlier the default was mike@rodgersintelligence.com, which cannot write to rigoperator, so re-check every run. Working owner pages: /publish/home, /publish/subscribers, /publish/stats (tabs), /publish/settings?search=payments; /publish/stats/growth returns Page not found.

## Step 1: Hard gates (every job)

1. **Gate-D**: sending or scheduling an issue, posting a Note, restacking, adding a recommendation, changing settings, the About page, the publication name or prices: each needs Mike's explicit yes for that item. Drafts, briefs and analysis are free.
2. **Jev first** for every typed judgment (mandate above).
3. **Generation belongs to the engines**: `rig-write-substack` (Communications OS) drafts issues; Eden drafts LinkedIn copy and brand imagery. Agents source, brief, gate and measure.
4. **Every number is a sourced receipt.** Creator result claims from the corpus are UNVERIFIED and never repeated as fact.
5. **Never send twice**: check Posts > Published on both publications before any send.
6. **Audience radio**: rigoperator's publish dialog has defaulted to "Paid subscribers only". A public issue sends only when the button reads "Send to everyone now".
7. **LinkedIn link rule**: no raw Substack link in a LinkedIn post body; first comment only.
8. **No fake engagement**: no pods, bought likes, reply rings or recommendation-swap spam.

## Step 2: Route the job to ONE stage

| Job | Stage | Path |
|---|---|---|
| Who it is for, the promise, pillars, name, About page as offer | ss-strategy | `~/Developer/rig-capabilities/capabilities/skills/ss-strategy/SKILL.md` |
| Publishing day, four-week calendar, batching, repurposing LinkedIn | ss-plan | `~/Developer/rig-capabilities/capabilities/skills/ss-plan/SKILL.md` |
| Title, subtitle, cover image, subject line, first lines | ss-package | `~/Developer/rig-capabilities/capabilities/skills/ss-package/SKILL.md` |
| Issue body: format, structure, brief for rig-write-substack | ss-write | `~/Developer/rig-capabilities/capabilities/skills/ss-write/SKILL.md` |
| Welcome emails, sections, SEO, paywall placement, the send itself | ss-publish | `~/Developer/rig-capabilities/capabilities/skills/ss-publish/SKILL.md` |
| Pre-publish gate: claims, Jev, engine score, anti-slop, Gate-D request | ss-gate | `~/Developer/rig-capabilities/capabilities/skills/ss-gate/SKILL.md` |
| Notes, restacks, replies, the daily engagement routine | ss-notes | `~/Developer/rig-capabilities/capabilities/skills/ss-notes/SKILL.md` |
| Recommendations, cross-posts, guest posts, Lives, peer list | ss-network | `~/Developer/rig-capabilities/capabilities/skills/ss-network/SKILL.md` |
| Amplifying each issue on LinkedIn, X, owned surfaces; the archive | ss-distribute | `~/Developer/rig-capabilities/capabilities/skills/ss-distribute/SKILL.md` |
| Paid tier, lead magnets, next steps, readers to clients | ss-convert | `~/Developer/rig-capabilities/capabilities/skills/ss-convert/SKILL.md` |
| Bestseller track: math to 100 paid, membership tier, premium library, paywall cuts, sprint launches, trust cadence, 30/60/90/180 roadmap | ss-bestseller | `~/Developer/rig-capabilities/capabilities/skills/ss-bestseller/SKILL.md` |
| Weekly stats, sources, per-issue numbers, flop diagnosis | ss-measure | `~/Developer/rig-capabilities/capabilities/skills/ss-measure/SKILL.md` |

A whole issue end to end: ss-plan → ss-package → ss-write → ss-gate → ss-publish → ss-notes + ss-distribute → ss-measure. ss-strategy runs first only while positioning is unsettled (it is, as of 2026-09-28). ss-network, ss-convert and ss-bestseller run on their own monthly rhythm; ss-bestseller also owns the quarterly sprint launch.

## Tools and neighbours

| Asset | Role | Path |
|---|---|---|
| substack-doctrine | every law by stage, contested points, corpus provenance | `~/Developer/rig-capabilities/capabilities/skills/substack-doctrine/SKILL.md` |
| rig-write-substack | issue drafting engine and score | `~/Developer/rig-capabilities/capabilities/skills/rig-write-substack/SKILL.md` |
| linkedin-viral / lv-distribute | the LinkedIn side of every route-back | `~/Developer/rig-capabilities/capabilities/skills/linkedin-viral/SKILL.md` |
| xs-growth-os | the X lane (@RodgersRIG) | `~/Developer/rig-capabilities/capabilities/skills/xs-growth-os/SKILL.md` |
| anti-slop | copy lint before the gate | `~/.aside/u/0/skills/user/anti-slop/SKILL.md` |
| s1gate | the Jev gate itself | `~/.aside/u/0/skills/user/s1gate/SKILL.md` |

## Routines (created 2026-09-28 at Mike's request; cost-cut the same day: "cut costs if it is not effective")

| Routine | When (America/Denver) | Tier | Cost gate (checked first, stops before any drafting) |
|---|---|---|---|
| SUBSTACK · Notes stage (`lVk7w9AMWQNDlQfu`) | Mon/Wed/Fri 07:15 (was Mon-Fri) | standard | skips if the last 2 draft files went unposted on substack.com/@mike910931 |
| SUBSTACK · night writer on Blackwell (`5REWM5Q7Rcc7c3Cr`) | Sat 01:30 | standard (drafting itself is local, GPU 1) | skips while the last night draft is unpublished; writes the brief, runs `night_writer.py` |
| SUBSTACK · weekly issue package (`fcDG9Uu079RiLSKq`) | Sat 09:00 | standard | packages the night draft: deviation audit, Jev substack.issue + improve, ranked titles; lists every [RECEIPT NEEDED] for Mike |
| SUBSTACK · Friday scoreboard + cost kill-switch (`K9j5fYjHPpiwHnHa`) | Fri 14:30 | standard | from 2026-10-23: 0 drafted Notes posted and 0 drafted issues published in 4 weeks pauses the Notes and issue routines, with a Kanban card; 8 weeks under 3 new free subscribers recommends pausing itself |
| SUBSTACK · monthly bestseller review (`IRZZhaYovkZ3FN9E`) | 1st of month 09:30 | standard (was deep) | skips if nothing moved and nothing was published in 30 days |

About 6.25 runs a week at most (the night writer adds one, but drafting moved from a cloud model to the local Blackwell), and most runs end at the gate while drafts sit unused. Every tier in `modelCategories` is a paid route (no local tier exists), so frequency and gates are the cost lever. Routines draft and stage only; they never send, post, restack, recommend or change settings.

## Night writing on the Blackwell (2026-09-28)

GPU 1 normally serves the companion (`blackwell-qwen38-uncensored`, :8111). `rig-writer-window start|stop|harden|reap|status` (Blackwell) swaps it for Hemmingway-1 (`blackwell-hemmingway-1`, :8112, vLLM 0.28.0) and back. Two hard rules, both tested live 2026-09-28: (1) **never interrupts in-flight work**: start waits (up to 10 min) until the companion shows running=0 waiting=0, refuses if GPU 1 holds a foreign process or metrics are unreadable (fail closed), and re-checks immediately before the stop; (2) **back by 07:00 Denver every morning**: swaps only open in the 01:00-07:30 machine-local window (box is America/Toronto, Denver+2h year-round), a 15-min reaper closes windows older than 4h or past 08:55 local, and `rig-writer-window-7am.timer` hard-closes daily; `night_writer.py` also refuses a swap outside 01:00-05:59 local. Measured: waited out a live 4-request burst, swapped in ~45 s warm / ~4 min cold, drafted, restored companion healthy in ~80 s; refused correctly under load (exit 4) without touching the in-flight request. Hemmingway needs `chat_template_kwargs.enable_thinking=false` or its reasoning leaks into the text. **License:** CC BY-NC 4.0; the license text requires a separate **written** agreement with Altworld (luka@hemmingway.io) for commercial use. Mike stated 'I have permission' (2026-09-28, owner authorization recorded in `config/hemmingway-license.json`, `written_agreement_on_file: false` until the actual agreement is attached there). If a signed agreement is later found missing, set `commercial_agreement` back to false and RIG briefs fall back to the companion automatically.

## Known conflicts (Mike decides)

- `lv-distribute` treats Substack as a weekly digest of LinkedIn, "never per post". The corpus treats Substack as its own network (native issues plus daily Notes). This family follows the corpus for rigoperator and uses the digest rule only for LinkedIn roundups.
- The corpus baseline is one free plus one paid issue per week. Earlier (morning of 2026-09-28) RIG ran all-free with paid as a filter. **Superseded the same day by Mike's instruction to build toward Bestseller:** the paid tier is now designed as a membership (ss-bestseller) while the $3,500 One-Workflow Review stays the back-end rung. The honest math (100 paid at 1-3% conversion needs ~3,300-10,000 free subscribers, from ~2 today) is in ss-bestseller; do not report the badge as likely without that math.
- ss-convert previously ran Jev with `offer.eval`, which is Mike's job-offer rubric. It now uses `opportunity.money`, the nearest revenue-offer rubric (still advisory, uncalibrated).

## Done-test

`claims_check.py` is GREEN only when every CLAIM id across the family resolves to a captured transcript and every quote in the corpus notes is verbatim in its cited transcript; `--plant` proves a bogus id and a fabricated quote both go RED. `check_family.py` is GREEN only when every stage opens with the JEV section, every sub-skill exists at 400+ bytes, and no 12-word transcript run appears in any skill; `--self-test` plants both defects and requires RED. `build_family.py --check` is GREEN only when the generated stages match the notes (no hand drift).
