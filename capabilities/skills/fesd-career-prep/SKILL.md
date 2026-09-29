---
name: fesd-career-prep
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict. Owns stage S13 of the front-end interview doctrine: the full big-tech front-end loop
  preparation campaign, compensation and leveling reality (tiered market model, dated London
  bands, negotiation by competing offers), and the AI-era engineering positioning that survives
  code generation. Built from 51 laws across 3 Front-End Engineer videos (2Xqu_GNvnxg, 1kO54TT2cbs,
  v4Dt4FalMOA). Use when planning front-end interview preparation, when a candidate asks what
  big-tech front-end rounds actually test, when salary or level questions come up, or when asked
  how AI changes front-end career value. JEV-FIRST MANDATE, findable at task start: typed
  judgments in this stage go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED is the
  only answer when the classifier is down. Child of fe-system-design-os.
owner: rig-intelligence
domain: Engineering / Front-end system design
status: Stable
acl: internal
tags: [frontend, career, interview-prep, compensation, ai-era]
outcome: "code-engineering: a dated, sourced preparation and positioning plan for front-end interview loops"
done_when:
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/claims_check.py capabilities/skills/fesd-career-prep/SKILL.md
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/check_family.py
quality_floor: 0.6
metadata:
  parent: fe-system-design-os
  stage: "S13"
  corpus: "data/corpora/frontend-engineer/manifest.jsonl"
---

# Front-end career and interview preparation

JEV FIRST, and it binds every task under this skill: an agent whose only context is this
excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`).
When the fast classifier is unavailable: DEFER, never guess a verdict locally. A required signal
passes only above 0.9; below that the step does not advance.

## Load surface

This skill is an always-loaded task-start surface, not a deep reference an agent must already know about:
the `fe-system-design-os` meta-skill (loaded first by `/fesd` and routed to by `when-shipping-code`)
names it in its routes and org chart, and fesd-interview-coach loads it before its first action. All paths
are relative to the canonical repo `~/Developer/rig-capabilities`.

## JEV-first mandate

Typed judgments this stage forces, and which go to Jev first:

1. Is this preparation plan matched to the target role's actual loop (UI loop versus generic SWE
   loop) (kind: interview.answer).
2. Is a compensation claim properly dated, market-scoped, and hearsay-flagged (kind:
   interview.answer).
3. Is a candidate answer grounded in true experience rather than a story that will not survive
   probing (kind: interview.answer).

Command shape: `~/.rig/bin/rig-s1gate check interview.answer --file <prep-plan.md> --subject "career <id> sha256:<hash>" --json`.
Nearest existing rubric: interview.answer, advisory until calibrated. A pass needs every required
signal above 0.9. Classifier down, erroring, or rubric missing = DEFERRED, never a guessed
verdict. An advisory PASS is not permission to ship or publish; compensation figures here are
dated observations, never quotes to act on unchanged.

## When to use

- When planning a front-end interview preparation campaign (months, not days).
- When someone asks what big-tech front-end rounds test and how to drill for them.
- When a salary, level, or offer negotiation question needs a market model instead of one number.
- When asked how AI and code generation change front-end career value.

## Inputs and output contract

Input: the candidate's target role, target companies, location and market, level, and time
available per day.

Output artifact: `prep-plan.md` with these headings:

1. Goal and target-company list, with deadline and daily time budget.
2. Round map (algorithmic, front-end coding, system design, behavioral) with per-round drill
   counts and durations.
3. Compensation model for the target market, every number labeled with year and market scope,
   hearsay flagged (references/compensation-and-leveling.md).
4. Leveling target (references/compensation-and-leveling.md).
5. AI-era positioning statement (references/ai-era-engineering.md).

## Procedure

1. Define the goal and write the target-company list before studying anything; the list
   determines what the interviews demand. Load references/big-tech-loop-prep.md.
   CLAIM(2Xqu_GNvnxg@00:59)
2. Set a deadline and a fixed daily study budget; discipline carries the months, not motivation.
   CLAIM(2Xqu_GNvnxg@01:21) CLAIM(2Xqu_GNvnxg@01:44)
3. Learn what the target company's rounds actually ask from people who work there; recruiters
   can misdescribe the loop. CLAIM(v4Dt4FalMOA@19:54)
4. Match practice to the role: UI components and front-end system design for UI loops, LeetCode
   only where generic SWE loops still ask it. CLAIM(v4Dt4FalMOA@19:18)
5. Build the round plan per references/big-tech-loop-prep.md (algorithms, front-end coding,
   system design, behavioral with the stated budgets).
   CLAIM(2Xqu_GNvnxg@17:35) CLAIM(2Xqu_GNvnxg@18:00)
6. Set the compensation and level expectations from the tier model, dated and scoped. Load
   references/compensation-and-leveling.md. CLAIM(1kO54TT2cbs@01:39)
7. Write the AI-era positioning statement. Load references/ai-era-engineering.md.
   CLAIM(v4Dt4FalMOA@49:25)
8. Publish or share the preparation trail as you go; it sustains momentum and doubles as public
   evidence. CLAIM(2Xqu_GNvnxg@01:58) CLAIM(v4Dt4FalMOA@01:04:37)

## Core laws

Campaign shape (consensus):

- Plan interview prep as a months-long campaign alongside a full-time job and expect doubt to
  peak at the end. CLAIM(v4Dt4FalMOA@00:44) consensus with CLAIM(2Xqu_GNvnxg@17:35).
- Budget roughly six to seven months at two to three hours a day: 2-3 months algorithms, about a
  month front-end coding, about three months system design, 3-7 days behavioral.
  CLAIM(2Xqu_GNvnxg@17:35) CLAIM(2Xqu_GNvnxg@18:00) single-source (the podcast's "4-5 months of
  deliberate prep" is the same idea at higher intensity: CLAIM(v4Dt4FalMOA@01:14:52)).
- Treat technical interviewing as a preparation problem, not a talent gate.
  CLAIM(v4Dt4FalMOA@01:14:52) consensus.

Loop and drilling (consensus):

- Solve on the order of 200-300 algorithm problems, then stop and move on.
  CLAIM(2Xqu_GNvnxg@03:48) CLAIM(2Xqu_GNvnxg@05:30) single-source.
- Learn the theory before grinding problems, then group problems by pattern and data structure.
  CLAIM(2Xqu_GNvnxg@04:01) CLAIM(2Xqu_GNvnxg@05:40) single-source.
- Treat the front-end coding round as a fundamentals test (JavaScript, HTML, CSS, browser
  mechanics), not a framework test. CLAIM(2Xqu_GNvnxg@06:28) consensus with
  CLAIM(v4Dt4FalMOA@19:18).
- Prepare for system design by cloning popular apps in vanilla JS and understanding the
  mechanism behind each feature; go deep on the hard ones.
  CLAIM(2Xqu_GNvnxg@10:08) CLAIM(2Xqu_GNvnxg@11:03) single-source.
- For behavioral rounds, prepare two true stories per common question and never lie; offer an
  adjacent story when you have none. CLAIM(2Xqu_GNvnxg@14:29) CLAIM(2Xqu_GNvnxg@14:42) consensus
  with CLAIM(v4Dt4FalMOA@16:08).
- Learn the interview vocabulary precisely when English is not your first language.
  CLAIM(2Xqu_GNvnxg@16:15) consensus with CLAIM(v4Dt4FalMOA@09:21) CLAIM(v4Dt4FalMOA@17:16).

Market and level (all dated, single-source to two videos):

- Model the market as three compensation spikes by company tier, not one average salary.
  CLAIM(1kO54TT2cbs@01:39) single-source.
- Define levels by scope, not years alone. CLAIM(1kO54TT2cbs@03:50) CLAIM(1kO54TT2cbs@04:34)
  consensus with CLAIM(v4Dt4FalMOA@27:36).
- Interview at several companies at once and negotiate with competing offers.
  CLAIM(1kO54TT2cbs@12:22) CLAIM(1kO54TT2cbs@12:36) single-source.

AI-era positioning (single-source, one 2026 podcast):

- Keep CS fundamentals current because you must understand what AI generates to stay employable.
  CLAIM(v4Dt4FalMOA@18:48) single-source.
- Position as the engineer who understands generated code and directs architecture; steer toward
  data-layout efficiency, performance optimization, and polished design systems.
  CLAIM(v4Dt4FalMOA@49:25) CLAIM(v4Dt4FalMOA@44:31) single-source.

## Sub-skills

| Sub-skill | File | Load when |
|---|---|---|
| Big-tech loop prep | references/big-tech-loop-prep.md | Building the study campaign, drilling rounds, behavioral and English prep |
| Compensation and leveling | references/compensation-and-leveling.md | Any salary, band, level, or negotiation question |
| AI-era engineering | references/ai-era-engineering.md | Career positioning under code generation; vibe-coding and spec-engineering views |

## Decision tables

Where to spend prep time, by target loop (cited):

| Target loop | Drill | Budget | Cite |
|---|---|---|---|
| Big-tech generic SWE | Algorithms on LeetCode/HackerRank, company-filtered | 2-3 months, 200-300 problems | CLAIM(2Xqu_GNvnxg@03:48) CLAIM(2Xqu_GNvnxg@04:52) |
| Front-end coding | Fundamentals + bfe.dev set + plain widgets | about 1 month | CLAIM(2Xqu_GNvnxg@06:28) CLAIM(2Xqu_GNvnxg@07:49) |
| Front-end system design | Clone real apps in vanilla JS, run the S01 drills | about 3 months | CLAIM(2Xqu_GNvnxg@13:08) CLAIM(2Xqu_GNvnxg@10:08) |
| Behavioral | Two true stories per question, vocabulary | 3-7 days plus English work | CLAIM(2Xqu_GNvnxg@14:29) CLAIM(2Xqu_GNvnxg@16:15) |
| UI-specific loop | Components and FE system design; drop LeetCode if not asked | match to role | CLAIM(v4Dt4FalMOA@19:18) |

## Anti-patterns

- Grinding problems without theory first, or grinding past the sufficiency point.
  Refuted by CLAIM(2Xqu_GNvnxg@04:01) CLAIM(2Xqu_GNvnxg@05:30).
- Preparing for a loop the recruiter described instead of the loop employees describe. Refuted
  by CLAIM(v4Dt4FalMOA@19:54).
- Fabricated behavioral stories. Refuted by CLAIM(2Xqu_GNvnxg@14:42).
- Taking one offer's number as "the market". Refuted by CLAIM(1kO54TT2cbs@01:39)
  CLAIM(1kO54TT2cbs@10:04).
- Treating a referral as a pass. Refuted by CLAIM(v4Dt4FalMOA@12:21).

## Worked cases

- 2Xqu_GNvnxg "Preparing for Frontend Interview in Big Tech": the whole campaign plan with per-
  round budgets (note: transcript captions are auto-translated; phrasings approximate, numbers
  and named resources as stated).
- 1kO54TT2cbs "The truth about SWE salaries in the UK": the tier model and the London bands
  (2022 figures).
- v4Dt4FalMOA "FAANG engineer on salaries, interviews and hedge funds": leveling, loop reality,
  hedge-fund pay, and AI-era positioning (2026 podcast, Russian captions; wording approximate).

## Dated / contestable

- Every compensation figure in references/compensation-and-leveling.md is dated (2022 London GBP
  bands; 2026 first-hand offer sample) and part hearsay. Do not quote a band without its year
  and market. Distiller note (not the author): re-derive from current postings and offers.
- The 2022 study-resource list (specific free courses and channels) is single-source and ages;
  the pattern (theory first, then structured problem sets) is the transferable part.
  CLAIM(2Xqu_GNvnxg@04:01) CLAIM(2Xqu_GNvnxg@04:52)
- The two videos disagree slightly on total prep length (six to seven months at 2-3 hours/day
  versus 4-5 months deliberate). Distiller note (not the author): treat 4-7 months as the range
  and plan to the shorter end only with prior fundamentals. CLAIM(2Xqu_GNvnxg@17:35)
  CLAIM(v4Dt4FalMOA@01:14:52)

## Hand-off

- Next stage: none inside this corpus family; this is the terminal career stage (S13). Feeds back
  into fesd-interview-framework for mock drills.
- Adjacent estate skills: for Mike's own job search, routing and application work lives in
  traject-os and lucy-skills (plus the aside-job-* family); this skill supplies front-end
  technical interview doctrine only and is not a job-search operator. For UI quality bars that
  the interviews probe, see emil-design-eng, fixing-accessibility, fixing-motion-performance,
  and app-web-frontend for build slices.
