---
name: google-ads-doctrine
description: >-
  Google Ads doctrine distilled from 1,052 captured YouTube transcripts (of 1,500 targeted; the
  throttled remainder documented in TARGETS.md) across 8 Jev-selected Google Ads teaching channels
  (Aaron Young, Jyll Saskin Gales, The Paid Search Podcast, Grow My Ads, Ben Heath, Surfside PPC,
  Solutions 8, Optmyzr; PPC Mastery was selected but YouTube bot-walled its capture), captured
  2026-09-28. Laws are grouped by
  the 11 ga-* stages, each paraphrased and cited CLAIM(videoId), marked consensus or single-source,
  with contested points, dated advice and unverified creator claims kept separate. Use when
  planning, building, auditing or deciding anything about a Google Ads account, or when asked what
  Google Ads practitioners actually say works. JEV-FIRST MANDATE, findable at task start: judgments
  this doctrine drives go to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only
  answer when the classifier is down. Child of google-ads-os.
owner: rig-intelligence
domain: Marketing
status: Stable
acl: internal
tags: [google-ads, doctrine, ppc, growth, corpus]
outcome: "revenue-gtm: Google Ads work applies corpus laws traced to a captured video, never a remembered tactic, a creator's unverified number, or copied transcript text"
done_when:
  - cmd:python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/google-ads-doctrine/references/law-index.md
  - cmd:python3 capabilities/skills/google-ads-os/scripts/check_family.py google-ads-doctrine
  - file:data/corpora/google-ads/TARGETS.md
quality_floor: 0.6
metadata:
  parent: google-ads-os
  corpus: "data/corpora/google-ads/manifest.jsonl"
---

# Google Ads doctrine

## JEV-first mandate (read before applying the doctrine)

**Findability anchor — this is an always-loaded instruction surface, not a deep reference.** This block lives in a skill file whose description Claude Code, Codex, Hermes, OMP, Prime Agent and Aside load into every session at start, and in the front door `google-ads-os` plus Mike's always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"). The text reaches the agent before any Google Ads judgment; an agent whose only context is this excerpt still routes to Jev first.

**JEV FIRST — before any frontier LLM call, on every task.** Inventory the decisions the task forces and route each one, first match wins: CODE (deterministic rule) -> JEV (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`, decision id recorded) -> SYSTEM 2 (frontier LLM for generation) -> HUMAN (Gate-D: outward, paid, destructive). Semantic triage, routing and classification go to the rig-s1gate Jev path BEFORE any frontier LLM call.

Judgments this doctrine drives (plan readiness, structure soundness, keyword/negative calls, ad quality, spend keep/cut, flop cause) go to Jev before any frontier model opinion. DEFERRED when the classifier is down; never a guessed verdict. An advisory PASS never authorizes spend or an outward action; ad spend is Gate-D.

## What this is

- **Corpus**: `data/corpora/google-ads/` holds the derived registry and notes; transcripts themselves stay local under `.context/google-ads-creators/` (creators' copyrighted words, never committed or republished). Counts: `counts.json`; channel selection evidence and Jev decision ids: `TARGETS.md`.
- **Channels** (ranking evidence and Jev decisions in `TARGETS.md`): Aaron Young | Define Digital Academy, Jyll Saskin Gales, The Paid Search Podcast, Grow My Ads, Ben Heath, Surfside PPC, Solutions 8, Optmyzr. PPC Mastery (Miles & Bob) was Jev-ranked and selected but YouTube bot-walled its capture (0 of 56); it is recorded in TARGETS.md as selected-uncaptured.
- **Honest limits**: Jev scored no candidate as a true fit under the strict bar (best composite 0.703; a planted off-subject control scored 0.078, so the rubric discriminates); these are the closest available teachers. Optmyzr is a tool vendor and PPC Mastery is a small channel; both are weighted as single voices. Google's official channel is platform ground truth only and is not in the captured set.
- **Fidelity**: transcripts are YouTube auto-captions, cleaned of the rolling caption window; quotes in the notes are checked verbatim against them by `claims_check.py`.

## How to use a law

1. Find it in `references/law-index.md` by stage.
2. `consensus` (2+ channels) can drive a plan; `single-source` is a hypothesis to test and must be labelled as such when it drives a recommendation.
3. Read the verbatim quotes and the context in `data/corpora/google-ads/notes/<stage>.md`, or open the transcript by id from the manifest.
4. Creator numbers ("we cut CPA 40%") are UNVERIFIED. Never present them to Mike or a buyer as facts.
5. Platform mechanics (settings, UI, policy) age fast: re-verify any mechanics claim in the live account before relying on it; `Dated advice` sections name the eras that already changed.

## Cross-stage laws that carry the most weight

Laws with the widest channel support, across stages (see the index for the full wording and ids):
- Conversion tracking is the fuel; smart bidding without proven conversions is guessing (ga-tracking, ga-bidding).
- Keywords are meaning signals now; structure for intent and message match, and keep control through negatives (ga-structure, ga-keywords).
- Message match (query = ad = landing page H1) is the spine of both quality and conversion (ga-ads, ga-landing).
- Small budgets buy inbound intent first; PMax and outbound formats do not get first claim (ga-campaigns, ga-local-b2b).
- Read the account live; written reports go stale and disagree (ga-reporting).

## References

| File | Contents |
|---|---|
| `references/law-index.md` | every law by stage with CLAIM ids (generated by `google-ads-os/scripts/build_family.py`) |

## Done-test

`claims_check.py` on the law index is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py google-ads-doctrine` is GREEN only when no 12-word transcript run appears here.
