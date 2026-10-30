---
name: skool-growth-os
description: >-
  JEV-FIRST MANDATE, findable at task start: every typed judgment here (positioning, offer shape,
  lesson publishability, gate verdict, channel fit, growth tactic) goes to rig-s1gate (Jev) BEFORE
  any frontier LLM call, and DEFERRED is the only answer when the classifier is down.
  Skool Community OS: the single front door for every Skool community job Mike Rodgers runs
  (RIG Intelligence Lab, skool.com/rig-intelligence-lab-8888, the "AI ops lab for real bottlenecks"
  where a member brings one workflow and leaves with owner, sources, gates, approval boundary,
  ProofPacket and agent routing). It fixes the community and lane, enforces the hard gates, and
  routes to exactly one of 12 stage skills (strategy, launch, content, engagement, growth,
  monetization, ads, lessons, gate, distribute, measure, ops), backed by skool-doctrine: laws
  distilled from Skool-community creator videos (corpus: data/corpora/skool - 1,405 videos
  enumerated across 10 channels, transcripts captured incrementally; 42 laws from the seed
  interview fXiFlwKvB3U as of 2026-09-28), every law cited to a video id. The lesson engine
  (sk-lessons) harvests from Mike's memory ledgers, chat history, the Jake Studio vault and a
  daily internet scout. Use for /skool-growth-os, "grow my Skool community", "set up the
  lessons learned", "why is nobody engaging", "redesign the community". Never publishes from here.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [skool, community, growth, meta-skill, router, doctrine, lessons-learned]
outcome: "content-publishing: every Skool community job enters one router that fixes the community, loads exactly one stage skill, and applies corpus doctrine and gates before anything goes public"
done_when:
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/claims_check.py
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/claims_check.py --plant
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/check_family.py --self-test
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/build_family.py --check
quality_floor: 0.6
metadata:
  purpose: meta-skill
  parent: when-growing-social-accounts
  stages: "12"
  corpus: "data/corpora/skool: 1,405 videos enumerated across 10 channels (2026-09-28); transcripts captured incrementally; 42 laws from fXiFlwKvB3U"
  community: "RIG Intelligence Lab (skool.com/rig-intelligence-lab-8888), owner Michael Rodgers, private/free as of 2026-09-28"
---

# Skool Community OS (meta-skill)

## JEV-first mandate (read before anything else)

Where this rule lives, so an agent meets it before touching Skool work: it is repeated in this skill's description, which Claude Code, Codex, Hermes, OMP, Prime Agent and Aside load into every session at start; Mike's always-loaded `~/.aside/u/0/AGENTS.md` (first section, "JEV before done") mandates Jev for every typed judgment; and `when-growing-social-accounts`, the social router, lists this skill first for any Skool job. Every sk-* stage repeats the mandate as the first section of its body and in its description.

Every typed judgment this family forces goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call: which positioning wins, does a lesson pass for publication, does an item pass the gate, is a channel a fit, is a growth tactic honest, is a price right.

- Command: `~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`. No Skool-specific rubric exists yet; each stage names the nearest existing one (`idea.solid`, `offer.eval`, `post.viral`, `atomic.claim`, `signal.performance`, `plan.readiness`), all advisory until calibrated.
- A pass needs every required noul and confidence above 0.9; exactly 0.90 fails.
- **Fail closed:** classifier down, erroring or rubric missing = DEFERRED. Never a guessed verdict, never a frontier model's opinion in its place.
- An advisory PASS is not permission to publish, post, advertise, price or spend.
- A claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

Hierarchy: `when-growing-social-accounts` (all social) → **skool-growth-os** (all Skool) → one stage skill → at most one of its sub-skills. Doctrine: `skool-doctrine`. Agent tree: `skool-community-conductor` (meta) → stage agents → sub-agents (`capabilities/agents/sk-*.md`).

## Step 0: Community and lane guard (always first)

| Community | Owner | Status | Route |
|---|---|---|---|
| **RIG Intelligence Lab** (skool.com/rig-intelligence-lab-8888) | Skool account "Michael Rodgers" (@michael-rodgers-8261) | the RIG community: AI ops lab for real bottlenecks - bring one workflow, leave with owner, sources, gates, approval boundary, ProofPacket, agent routing. Private, free, 1 member (2026-09-28) | this family |

| Lane | Rule |
|---|---|
| RIG B2B (default) | evidence-led, receipts, Mike's voice; lessons learned from real work; no Lane A cast (Birch, Unit 7, The Coach) |
| Minor (Jacob) | STOP. Never any content about the minor in this community |
| Client (Ideawake / Coby) | never publish client material here; client-lane accounts never advertise this community |
| Member stories | de-identify always; republishing a member's situation needs that member's yes |

Assert the signed-in Skool account before any write: the avatar menu shows "Michael Rodgers". As of 2026-09-28 the Aside browser is signed in as Michael Rodgers (the owner). Re-check every run.

**Known state (2026-09-28):** the community has no cover photo, no description ("Add your group description here"), no classroom content, and a **"Your payment has been declined"** banner on the owner view - billing is Mike's action (Gate-D), the community is not monetizable until it clears.

## Step 1: Hard gates (every job)

1. **Gate-D**: publishing a classroom item, lesson, community post or About change; setting or changing price; spending on ads; sending invites or outreach; any comment or reply on other people's spaces: each needs Mike's explicit yes for that item. Drafts, briefs, audits and analysis are free.
2. **Jev first** for every typed judgment (mandate above).
3. **Generation belongs to the engines**: agents draft; the lessons engine (sk-lessons) harvests and generalizes; nothing publishes from this router.
4. **Every number is a sourced receipt.** Creator revenue claims from the corpus ($61K/mo, $100K/mo, $18K/mo and similar) are UNVERIFIED self-reports and never repeated as fact or as a promise.
5. **No fake engagement**: no bought members, pods, reply rings, fake reviews, or manufactured urgency.
6. **Minor lane**: content about Jacob is never cleared here, under any wording.

## Step 2: Route the job to ONE stage

**Routing rule:** no stage work begins before the JEV-first mandate above is met. Every route below forces typed judgments listed in its stage skill; those go to `rig-s1gate` BEFORE any frontier LLM call, DEFERRED when the classifier is down. A router that skips this step is in violation of this skill.

| Job | Stage | Path |
|---|---|---|
| Who it is for, the promise, free vs paid, the About page as offer | sk-strategy | `~/Developer/rig-capabilities/capabilities/skills/sk-strategy/SKILL.md` |
| Validation test, first 10-30 members, the kill/continue call | sk-launch | `~/Developer/rig-capabilities/capabilities/skills/sk-launch/SKILL.md` |
| Classroom design, weekly value loop, cases from community work | sk-content | `~/Developer/rig-capabilities/capabilities/skills/sk-content/SKILL.md` |
| Onboarding, conversation, retention, gamification | sk-engagement | `~/Developer/rig-capabilities/capabilities/skills/sk-engagement/SKILL.md` |
| Traffic, lead magnets, filling the room, referral loops | sk-growth | `~/Developer/rig-capabilities/capabilities/skills/sk-growth/SKILL.md` |
| Pricing, offer ladder, free-to-paid conversion | sk-monetization | `~/Developer/rig-capabilities/capabilities/skills/sk-monetization/SKILL.md` |
| Paid acquisition, capped ad tests, spend discipline | sk-ads | `~/Developer/rig-capabilities/capabilities/skills/sk-ads/SKILL.md` |
| The lessons-learned engine: harvest, generalize, daily scout | sk-lessons | `~/Developer/rig-capabilities/capabilities/skills/sk-lessons/SKILL.md` |
| The pre-publish gate: claims, lane check, Jev, Gate-D request | sk-gate | `~/Developer/rig-capabilities/capabilities/skills/sk-gate/SKILL.md` |
| Multi-channel advertising of community content | sk-distribute | `~/Developer/rig-capabilities/capabilities/skills/sk-distribute/SKILL.md` |
| Weekly numbers, the funnel, what each number makes you do | sk-measure | `~/Developer/rig-capabilities/capabilities/skills/sk-measure/SKILL.md` |
| Running the room: routines, automations, time budget | sk-ops | `~/Developer/rig-capabilities/capabilities/skills/sk-ops/SKILL.md` |

## Step 3: Cross-stage rules

- **Community-first**: the classroom is the byproduct of real work done with members (corpus consensus, fXiFlwKvB3U). Build the room before the curriculum.
- **Lessons learned is a first-class product**: internal lessons (memory ledgers, chat history, Jake Studio vault) generalized for public consumption plus a dated daily internet scout, published into the classroom's Lessons Learned section with lineage labels (member-observed / RIG-internal / public-source).
- **Light theme**: the community's visual identity is light, not black-and-gold; redesign changes are drafted and staged, applied only after Mike's yes.
- **Corpus honesty**: 1,405 videos enumerated across 10 channels, transcripts captured incrementally (YouTube caption access is rate-limited and gated; capture status lives in `data/corpora/skool/BUILD-LOG.md`). Single-source laws are hypotheses.
- **Public-repo boundary**: raw transcripts and harvest notes stay in `data/corpora/skool/` (gitignored); only paraphrased, cited laws enter the skills.

## Done-test

`claims_check.py --plant` proves the claim gate goes RED on a bogus id; `check_family.py --self-test` proves the structural gate goes RED on a copied transcript run and a missing sub-skill; `build_family.py --check` proves the generated skills match the notes. All three run green before this family is called done.
