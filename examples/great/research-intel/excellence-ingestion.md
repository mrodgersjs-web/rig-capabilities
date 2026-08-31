---
name: great-excellence-ingestion
lane: research-intel
source: jakestudio-vault
exemplar_of: excellence-ingestion
description: Reference exemplar — what great looks like for research-intel (excellence-ingestion).
---

# Excellence Ingestion Agent — What It Does

## Mission
Find the top 1% in any domain. Scrape everything they produce. Reverse-engineer their process. Build the algorithm to replicate it. Then make it 1000x better.

## Pipeline

```
DISCOVER → SCRAPE → DECOMPOSE → SCORE → PATTERN-MATCH → BUILD ALGORITHM → 1000X
```

## 8 Scoring Dimensions

| # | Dimension | Weight | What It Measures |
|---|-----------|--------|-----------------|
| 1 | Specificity | 15% | Named entities, numbers, dates, concrete details |
| 2 | Source Quality | 12% | Every claim backed by evidence |
| 3 | Mechanism | 15% | WHY it works — causal logic |
| 4 | Emotional Resonance | 12% | Does it make the reader FEEL? |
| 5 | Craft | 12% | Structure, rhythm, visual hierarchy |
| 6 | Execution Ready | 12% | Owner, timeline, proof path |
| 7 | Proof Completeness | 10% | Hashes, verification |
| 8 | Originality | 12% | New insight, not recycled wisdom |

## 6 Deviation Engines (1000x)

| Engine | Test | What It Does |
|--------|------|-------------|
| RIG-GLYPH | No clichés | Cannot be compressed into a known phrase |
| RIG-SURPRISE | Has counterintuitive insight | Makes the reader update their model |
| RIG-ECHO | Has quotable line | What the reader remembers in 48 hours |
| RIG-VOLT | Has emotional word | Emotional voltage without manipulation |
| RIG-VISCERA | Has embodied stakes | Felt, not described |
| RIG-LOOP | Has open loop | Open loops the reader must close |

## 1000x Rules

1. Every claim must have a named source (not "studies show")
2. Every recommendation must have a causal mechanism (because/therefore)
3. Every post must have at least one moment that makes the reader FEEL something
4. Every CTA must be specific enough that the reader knows exactly what to do
5. Every hook must pass the "scroll-stop test" — would you stop scrolling?
6. Every story must have a specific detail that proves it's real
7. Every output must have at least one insight not in the top 10 Google results
8. Every output must be graded against the world's best, not our own templates

## Domains Covered

| # | Domain | Top Performers | Status |
|---|--------|---------------|--------|
| 1 | LinkedIn Content | Hormozi, Martell, Gary Vee, Abdaal | ✅ Algorithm built |
| 2 | B2B Sales | Cardone, Blount, Weinberg | 🔄 Pending |
| 3 | Product Strategy | Rachitsky, Doshi, Zhuo | 🔄 Pending |
| 4 | Design Systems | Apple HIG, Material, Polaris | 🔄 Pending |
| 5 | Engineering Docs | Stripe, Vercel, Linear | 🔄 Pending |
| 6 | GTM / Growth | Dunford, Poyar, Gerhardt | 🔄 Pending |
| 7 | Financial Modeling | Bessemer, a16z, Sequoia | 🔄 Pending |
| 8 | Content Strategy | Duolingo, HubSpot, Notion | 🔄 Pending |
| 9 | Security Audits | OWASP, NIST, Trail of Bits | 🔄 Pending |
| 10 | Forecasting | Tetlock, Silver, Superforecasters | 🔄 Pending |

## CLI

```bash
# Discover top performers
python3 scripts/discover.py --domain linkedin_content --count 20

# Score outputs
python3 scripts/score_outputs.py --file output.md --verbose

# Build algorithm
python3 scripts/build_algorithm.py --domain linkedin_content

# Apply 1000x
python3 scripts/1000x.py --input output.md --domain linkedin_content --verbose
```

## Current Scores (Honest)

| Output | Score | Top 1% Benchmark | Gap |
|--------|-------|-----------------|-----|
| Ralph's LinkedIn Batch | 54.4 | 95+ | 40.6 |
| Darius Outreach Batch | 19.9 | 95+ | 75.1 |
| Steve Interview Guide | 39.9 | 95+ | 55.1 |
| Steve Strategy Memo | 39.5 | 95+ | 55.5 |
| Darius GTM Playbook | 32.3 | 95+ | 62.7 |
| Ralph Content Strategy | 35.5 | 95+ | 59.5 |

**1000x check**: Ralph's batch passes 6/6 deviation engines (no clichés, has counterintuitive insights, quotable lines, emotional moments, embodied stakes, open loops).
