---
name: fe-system-design-doctrine
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict. Front-end system design doctrine distilled from every video on Evgenii Ray's "Front-End Engineer"
  YouTube channel (@FrontEndEngineer; 15 uploads 2020-2025, about 96K spoken words) plus his 2025 podcast
  interview, captured 2026-09-28: 483 paraphrased laws, each cited CLAIM(<videoId>@mm:ss), grouped by
  the 12 fesd-* stages, and a library of 13 worked designs (News Feed, Pinterest, Netflix, Chat, Google
  Sheets, Google Calendar, Notion, Financial Dashboard, Typeahead x2, Data Table, Poll Widget, HTTP deep
  dive) plus 3 career talks. Use when designing a web front end, preparing for or running a front-end
  system design interview, reviewing a front-end architecture, or asked what this author says about a
  topic. JEV-FIRST MANDATE, findable at task start: judgments this doctrine drives go to rig-s1gate (Jev)
  BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of
  fe-system-design-os.
owner: rig-intelligence
domain: Engineering / Front-end system design
status: Stable
acl: internal
tags: [frontend, system-design, doctrine, corpus, interview]
outcome: "code-engineering: front-end design work applies laws traced to a captured video timestamp, never a remembered tactic or copied transcript text"
done_when:
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/claims_check.py capabilities/skills/fe-system-design-doctrine/references/law-index.md
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/check_family.py
  - file:data/corpora/frontend-engineer/manifest.jsonl
quality_floor: 0.6
metadata:
  parent: fe-system-design-os
  corpus: "data/corpora/frontend-engineer/manifest.jsonl (16 videos); transcripts in gitignored .context/frontend-engineer-yt/"
---

# FE System Design doctrine (Front-End Engineer corpus)

JEV FIRST, and it binds every task under this skill: an agent whose only context is this
excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`).
When the fast classifier is unavailable: DEFER, never guess a verdict locally. A required signal
passes only above 0.9; below that the step does not advance.

## Load surface

This skill is an always-loaded task-start surface, not a deep reference an agent must already know about:
the `fe-system-design-os` meta-skill (loaded first by `/fesd` and routed to by `when-shipping-code`)
names it in its routes and org chart, and every fesd-* agent (fesd-case-retriever first) loads it before its first action. All paths
are relative to the canonical repo `~/Developer/rig-capabilities`.

## JEV-first mandate
This is a reference, not a decision-maker. When a law here drives a typed judgment (is this design complete, does this answer pass, which transport fits), that judgment goes to Jev first: `~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`. Classifier down, erroring or rubric missing = DEFERRED, never a guessed verdict.

## Provenance and limits
- Source: one practitioner (Evgenii Ray, front-end engineer in big tech, London). Single-author doctrine: "consensus" in this family means he repeats it across 2+ videos, not that the industry agrees.
- Coverage is uneven by design of the channel: performance (127 laws) and state/data (61) are deep; security (2) and observability/testing (0) are nearly absent. Stage skills say so and hand off to estate skills for those gaps.
- 2020-2021 episodes contain dated advice (AppCache, ES5 dual bundles, the claim that WebSockets cannot ride HTTP/2, GIF promos). Every stage skill carries a Dated / contestable section; corrections there are labeled distiller notes, not the author.
- Several caption tracks were auto-translated (Arabic dub on LEaiGjffLEs and u6jhTo13_No, Bengali on 2Xqu_GNvnxg, Russian original on v4Dt4FalMOA). Laws from those are paraphrased back to English; wording is approximate, substance was checked against the video context.
- Raw transcripts never enter this repo. They live in `.context/frontend-engineer-yt/transcripts/` (gitignored) and `~/Developer/rig-doctrine-corpora/frontend-engineer-yt/`. `check_family.py` rejects any 12-word run copied from them.

## Stage coverage

| code | stage | laws | videos | owning skill |
|---|---|---|---|---|
| S01 | Interview framework | 33 | 11 | fesd-interview-framework |
| S02 | Requirements | 43 | 12 | fesd-requirements |
| S03 | Architecture | 23 | 9 | fesd-architecture |
| S04 | Component design | 46 | 10 | fesd-component-api |
| S05 | State and data model | 61 | 12 | fesd-state-data |
| S06 | API and network | 34 | 10 | fesd-api-network |
| S07 | Realtime and sync | 20 | 5 | fesd-realtime-sync |
| S08 | Performance | 127 | 13 | fesd-performance |
| S09 | Accessibility and i18n | 37 | 11 | fesd-a11y-i18n |
| S10 | Security | 2 | 1 | fesd-api-network |
| S11 | UX and product states | 6 | 5 | fesd-component-api |
| S13 | Career and interview prep | 51 | 3 | fesd-career-prep |

Full table: references/law-index.md

## Worked-case library

| type | case | video | file | laws |
|---|---|---|---|---|
| career | The truth about SWE salaries in the UK | 1kO54TT2cbs | references/cases/1kO54TT2cbs-the-truth-about-swe-salaries-in-the-uk.md | 14 |
| career | Preparing for Frontend Interview in Big Tech | 2Xqu_GNvnxg | references/cases/2Xqu_GNvnxg-preparing-for-frontend-interview-in-big-.md | 20 |
| career | FAANG engineer on salaries, interviews and hedge funds | v4Dt4FalMOA | references/cases/v4Dt4FalMOA-faang-engineer-on-salaries-interviews-an.md | 25 |
| component-design | [Front-End System Design] - Typeahead Widget | 9aOXGE7wAZo | references/cases/9aOXGE7wAZo-typeahead-widget.md | 27 |
| component-design | Typeahead component, front-end system design | 9mjsRrJYOWE | references/cases/9mjsRrJYOWE-typeahead-component-front-end-system-des.md | 29 |
| component-design | [Front-End System Design] - Design a Poll Widget | lO6GyCvbDm8 | references/cases/lO6GyCvbDm8-design-a-poll-widget.md | 31 |
| component-design | [Front-End System Design] - Data Table Component | u6jhTo13_No | references/cases/u6jhTo13_No-data-table-component.md | 37 |
| concept-deep-dive | Deep dive into HTTP [Part 1] | gxF9fLo5XQw | references/cases/gxF9fLo5XQw-deep-dive-into-http.md | 12 |
| product-design | [Front-End System Design] - Pinterest | 3MADCVqL534 | references/cases/3MADCVqL534-pinterest.md | 43 |
| product-design | [Front End System Design] - Facebook News Feed | 5vyKhm2NTfw | references/cases/5vyKhm2NTfw-facebook-news-feed.md | 39 |
| product-design | Frontend System Design - Financial Dashboard / TradingView | HR2jXy_wPg4 | references/cases/HR2jXy_wPg4-frontend-system-design-financial-dashboa.md | 40 |
| product-design | [Front-End System Design] - Chat application | LEaiGjffLEs | references/cases/LEaiGjffLEs-chat-application.md | 28 |
| product-design | [Front-End Product Design] - Netflix | Tu-hZ6lqNtY | references/cases/Tu-hZ6lqNtY-netflix.md | 43 |
| product-design | [Front-End System Design] - Google Sheets | fmIiDLbLc_s | references/cases/fmIiDLbLc_s-google-sheets.md | 27 |
| product-design | [Front-End System Design] - Google Calendar | leo1FZ6vu1I | references/cases/leo1FZ6vu1I-google-calendar.md | 28 |
| product-design | Frontend System Design - Notion-like editor | tsGarhpWOws | references/cases/tsGarhpWOws-frontend-system-design-notion-like-edito.md | 40 |

How to use a case: load the one closest to the prompt (feed-like, collaborative editor, widget, dashboard), read its framework and worked design, then run the stage skills against YOUR requirements. Never present a case's design as the answer to a different prompt.

## Cross-cutting laws (the ones that show up everywhere)
Pulled verbatim from the paraphrased law index; see stage skills for full context.
- Open the answer by writing the ordered stage plan for the whole design before any component work. CLAIM(5vyKhm2NTfw@01:13)
- Follow a fixed plan order: requirements and mockup, layout, data model, API, data flow, synchronization, multi-window (his 2025 order). CLAIM(HR2jXy_wPg4@02:16)
- Open by driving the real product and naming the two hardest problems before any architecture. CLAIM(HR2jXy_wPg4@00:33)
- Pre-build schemas for well-known prompts so interview minutes go to the hard parts, not drawing. CLAIM(5vyKhm2NTfw@07:38, HR2jXy_wPg4@05:50)
- Bound the data model on purpose; every extra parameter makes the design harder to reason about live. CLAIM(HR2jXy_wPg4@21:06)
- Performance is where his episodes spend the most time (127 of 483 laws); have a named technique for rendering, assets, network and memory. See fesd-performance.
