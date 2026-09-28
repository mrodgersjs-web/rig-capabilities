---
name: google-ads-os
description: >-
  Google Ads OS: the single front door for every Google Ads job Mike Rodgers runs (RIG account
  AW-847022079, manager 176-712-0344, and any client local-service account). It fixes the account
  and lane, enforces the hard gates, and routes to exactly one of 11 stage skills (strategy,
  structure, tracking, keywords, campaigns, bidding, ads, landing, budget, reporting, local-b2b),
  backed by google-ads-doctrine: laws distilled from 1,052 captured YouTube transcripts (of 1,500
  targeted; throttled remainder documented) across 8 Jev-selected Google Ads teaching channels,
  every law cited to a video id. JEV-FIRST MANDATE,
  findable at task start: every typed judgment here (plan readiness, structure soundness, keyword
  additions, ad quality, spend keep/cut, flop cause) goes to rig-s1gate (Jev) BEFORE any frontier
  LLM call, and DEFERRED is the only answer when the classifier is down. Use for /google-ads-os,
  "run my Google Ads", "audit this account", "should we spend", or any Google Ads build or review.
owner: rig-intelligence
domain: Marketing
status: Stable
acl: internal
tags: [google-ads, ppc, growth, meta-skill, router, doctrine]
outcome: "revenue-gtm: every Google Ads job enters one router that fixes the account, loads exactly one stage skill, and applies corpus doctrine and gates before anything spends"
done_when:
  - cmd:python3 capabilities/skills/google-ads-os/scripts/claims_check.py
  - cmd:python3 capabilities/skills/google-ads-os/scripts/claims_check.py --plant
  - cmd:python3 capabilities/skills/google-ads-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/google-ads-os/scripts/check_family.py --self-test
  - cmd:python3 capabilities/skills/google-ads-os/scripts/build_family.py --check
quality_floor: 0.6
metadata:
  purpose: meta-skill
  parent: when-selling-or-running-gtm
  stages: "11"
  corpus: "data/corpora/google-ads: 1052 captured transcripts, 8 channels"
---

# Google Ads OS (meta-skill)

## JEV-first mandate (read before anything else)

**Findability anchor — this is an always-loaded instruction surface, not a deep reference.** This block lives in a skill file whose description Claude Code, Codex, Hermes, OMP, Prime Agent and Aside load into every session at start, and in Mike's always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"). The text reaches the agent before any Google Ads task begins; an agent whose only context is this excerpt still routes to Jev first.

**JEV FIRST — before any frontier LLM call, on every task.** Inventory the decisions the task forces and route each one, first match wins: CODE (deterministic rule) -> JEV (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`, decision id recorded) -> SYSTEM 2 (frontier LLM for generation) -> HUMAN (Gate-D: outward, paid, destructive). Semantic triage, routing and classification are System-1 work and go to the rig-s1gate Jev path BEFORE any frontier LLM call. Re-run the inventory when scope shifts.

Every typed judgment this family forces goes to Jev (TypeSafe System One) before any frontier model opinion: is the plan ready, is the structure sound, is this keyword/negative justified, does the ad pass, is this spend worth continuing, what caused this result.

- Command: `~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`. No Google-Ads-specific rubric exists yet; each stage names the nearest existing one (`plan.readiness`, `idea.solid`, `atomic.claim`, `spend.continue`, `ad.search`, `website.buyer`, `signal.performance`), all advisory until calibrated.
- A pass needs every required noul and confidence above 0.9; exactly 0.90 fails.
- **Fail closed:** classifier down, erroring or rubric missing = DEFERRED. Never a guessed verdict, never a frontier model's opinion in its place.
- An advisory PASS is not permission to spend, enable a campaign, raise a budget, change bids or publish.
- A claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

Hierarchy: `when-selling-or-running-gtm` (all GTM) → **google-ads-os** (all Google Ads) → one stage skill → at most one of its sub-skills. Doctrine: `google-ads-doctrine`.

## Step 0: Account and lane guard (always first)

| Account | Owner | Status | Route |
|---|---|---|---|
| **AW-847022079** (493-977-2627) | Mike's Google Ads account | RIG's account; campaigns have been Paused with $0 spend and no evidenced conversions; a live read on 2026-09-28 showed one campaign serving late with unproven tracking | this family |
| manager **176-712-0344** | Mike's manager account | read-only for this family | reporting only |

| Lane | Rule |
|---|---|
| RIG local B2B (default) | eight verticals on mikerodgers.tech (construction, cpa, dentistry, healthcare, law, manufacturing, medspa, professional services); small budgets, calls+forms truth (ga-local-b2b) |
| Client (Ideawake / Coby) | STOP: client ad accounts are separate work with their own written approval |
| Minor (Jacob) | STOP: never buy ads for or about the minor without Mike's explicit per-item yes |

Assert the signed-in Google account before any account write. No sub-agent ever touches budgets, bids or campaign status: they stage, the parent operator acts.

## Step 1: Hard gates (every job)

1. **Gate-D**: enabling a campaign, changing a budget or bid strategy, extending a flight, or any spend is Mike's explicit yes for that item. Drafts, audits, plans and analysis are free. NEEDS-MIKE items also include: account sign-ups, Local Services Ads verification, payment methods, anything with 2FA or passkeys.
2. **Jev first** for every typed judgment (mandate above). DEFERRED blocks "ready to spend".
3. **Tracking before spend**: no money moves until conversion actions are proven firing (ga-tracking). Google prompting "Set up conversion tracking" is an incident.
4. **Every number is a sourced receipt**: live account reads with dates; creator result claims from the corpus are UNVERIFIED and never repeated as fact.
5. **48-hour serving check** after every launch: read the account live at 48 hours and day 5; a campaign at $0 with `Eligible (Limited)` is a bug, not a test.
6. **State claims are live reads**: "we ran ads" must match account state (enabled, serving, spend). Written records disagree; the live read is the truth.
7. **Dated doctrine stays dated**: SKAGs and old match-type surgery are flagged in the doctrine and never executed as current practice.

## Step 2: Route the job to ONE stage

| Job | Stage | Path |
|---|---|---|
| Goal, offer, budget arithmetic, pre-build audit, measurement plan | ga-strategy | `~/Developer/rig-capabilities/capabilities/skills/ga-strategy/SKILL.md` |
| Account architecture, campaign jobs, ad group themes, naming, SKAG questions | ga-structure | `~/Developer/rig-capabilities/capabilities/skills/ga-structure/SKILL.md` |
| Conversion actions, tags, call/form tracking, enhanced/offline conversions, consent | ga-tracking | `~/Developer/rig-capabilities/capabilities/skills/ga-tracking/SKILL.md` |
| Keyword themes, match-type strategy, negatives, search-term mining | ga-keywords | `~/Developer/rig-capabilities/capabilities/skills/ga-keywords/SKILL.md` |
| Campaign types (Search, PMax, Shopping, Demand Gen, local, LSA boundaries) | ga-campaigns | `~/Developer/rig-capabilities/capabilities/skills/ga-campaigns/SKILL.md` |
| Bidding strategies, tCPA/tROAS, learning periods, bid changes | ga-bidding | `~/Developer/rig-capabilities/capabilities/skills/ga-bidding/SKILL.md` |
| RSA copy, headlines/descriptions, assets and extensions, disapprovals | ga-ads | `~/Developer/rig-capabilities/capabilities/skills/ga-ads/SKILL.md` |
| Landing pages, message match, forms, speed, trust | ga-landing | `~/Developer/rig-capabilities/capabilities/skills/ga-landing/SKILL.md` |
| Budget math, scaling, limited-by-budget, experiments and tests | ga-budget | `~/Developer/rig-capabilities/capabilities/skills/ga-budget/SKILL.md` |
| Weekly/monthly reviews, reporting, optimization cadence, flop diagnosis | ga-reporting | `~/Developer/rig-capabilities/capabilities/skills/ga-reporting/SKILL.md` |
| Local service / B2B accounts on small budgets ($1-50/day), calls+forms, what NOT to run | ga-local-b2b | `~/Developer/rig-capabilities/capabilities/skills/ga-local-b2b/SKILL.md` |

A new account end to end: ga-strategy → ga-tracking → ga-structure → ga-keywords → ga-campaigns → ga-ads → ga-landing → ga-budget → ga-reporting, with ga-local-b2b overlaying the whole build for local service work. Reporting runs weekly; budget review monthly.

## Tools and neighbours

| Asset | Role | Path |
|---|---|---|
| google-ads-doctrine | every law by stage, contested points, dated advice, corpus provenance | `~/Developer/rig-capabilities/capabilities/skills/google-ads-doctrine/SKILL.md` |
| pmm-google-ads-local-b2b | the prior local-B2B ads skill; absorbed as ga-local-b2b's parent material (R1-R8 doctrine, 48-hour serving check) | `~/.aside/u/0/skills/user/pmm-google-ads-local-b2b/SKILL.md` |
| pmm-service-landing-pages-cro | the landing-page sibling skill (message match, iceberg effect) | `~/.aside/u/0/skills/user/pmm-service-landing-pages-cro/SKILL.md` |
| s1gate | the Jev gate itself | `~/.aside/u/0/skills/user/s1gate/SKILL.md` |
| rig-crm | lead outcomes close the loop into keywords and geo | `~/Developer/rig-capabilities/capabilities/skills/rig-crm/SKILL.md` |

## Known conflicts and limits (Mike decides where it matters)

- No Google-Ads-specific Jev rubric exists; stages use the nearest existing rubric, advisory until calibrated. `ad.search` is the one purpose-built ads rubric and is calibrated for local B2B service ads.
- The corpus is 2015-2026 and platform mechanics age fast; every mechanics claim is flagged "re-verify in the live product".
- Google's official channel is named in the corpus targets as platform ground truth but is not captured under the transcript cap; mechanics statements cite teaching-corpus windows only.

## Done-test

`claims_check.py` is GREEN only when every CLAIM id across the family resolves to a captured transcript and every quote is verbatim in its cited transcript; `--plant` proves a bogus id and a fabricated quote both go RED. `check_family.py` is GREEN only when every stage opens with the JEV section, every named sub-skill exists at 400+ bytes, and no 12-word transcript run appears in any skill; `--self-test` plants both defects and requires RED. `build_family.py --check` is GREEN only when the generated stages match the notes (no hand drift).
