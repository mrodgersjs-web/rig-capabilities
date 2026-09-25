---
name: "rig-revenue-ai-citation-gaps"
description: "Close AI-citation gaps: inventory the buyer prompts a firm should be cited for, measure per-model visibility, publish one governed answer-page per gap with answer-first structure and FAQ silos, then re-measure. Use when the trigger is 'not showing up in ChatGPT/AI overviews', 'AI visibility', 'GEO/AEO', or 'get cited by AI answers' for a professional-service firm."
---

# AI-citation gap closer

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta. Selling "AI-detection evasion" or "manipulating AI answers"
is refused; this skill builds retrievable, reviewable answer pages — the compliant version of the
corpus's citation play.

## Inputs

- Firm profile: services, cities, buyer personas, credentials, published pricing (or the explicit
  decision not to publish it — record which)
- Current site + sitemap; access to the AI tools/brand-monitor surface the client approved

## Outputs

- Target-prompt inventory (grouped: pricing, process, comparison, trust/credentials, local,
  urgency) — this doubles as the content plan and the monitoring plan
- Per-model visibility baseline (which prompts cite the firm, per LLM/search surface)
- Gap pages: one governed answer page per gap prompt (answer-first, FAQ block, named expert)
- Re-measurement deltas + next-quarter gap list

## Step 1. Build the prompt inventory (rig-revenue-ai-faq-silo)

1. Generate ~60 questions across six groups (pricing/financing, process/timeline, scope/comparisons,
   service area/availability, credentials/fit, urgent scenarios) in the buyer's own words — full
   sentences, the way people type to an assistant.
2. Screen for buyer intent (rig-revenue-buyer-intent-screen). Flag the ~10 highest-value gaps
   (questions competitors answer poorly or not at all).
3. Publish prices/ranges and direct answers where the firm approves it: "if your pricing isn't
   published, the AI has nothing to reference and sends people elsewhere" (CLAIM: KqX-7CfxoaM).

## Step 2. Measure baseline

1. Run the prompts through the client-approved answer surfaces (ChatGPT/Perplexity/Gemini/AI
   overviews) and record: is the firm cited? by which model? sentiment? which sources are cited
   instead? (rig-revenue-llm-citation-closer mechanics.)
2. If a corpus-endorsed brand monitor is proposed (Arvow/Journalist AI LLM monitors), label it
   PAID ENDORSEMENT and require client tooling approval — the measurement can also be done
   manually and should be shown either way.

## Step 3. Close gaps with answer pages

1. One page per gap prompt; the H1 is the question. Answer-first structure (question headings →
   1-2 sentence standalone link-free answers → detail). Pass the "pulled out of context" self-test
   (rig-revenue-answer-first).
2. Structure so answers are quoteable: comparison blocks ("X vs Y"), who-it's-for / who-it's-not,
   explicit differentiators in plain language, FAQ block, correct FAQ/HowTo/LocalBusiness schema
   (ship it; never promise it as a citation driver — contradiction #8 in rig-revenue-meta).
3. E-E-A-T: named expert author, credential verified, professional review before publish
   (YMYL). rig-revenue-publish-gate holds the approval record.

## Step 4. Retrievability check

Every gap page must be crawlable and indexed (AI-crawl settings not blocking; URL inspection
requested). Crawlable → indexed → ranked → cited. A page that isn't retrievable cannot be cited.

## Step 5. Re-measure and iterate

Re-run the prompt inventory at a fixed cadence (monthly). Move recovered prompts to the report
(rig-revenue-monthly-report); open new gaps. The AI-overview mirror variant (rig-revenue-ai-overview-mirror)
is a per-page add-on when a live AI Overview exists for the query.

## Tools

- Answer surfaces (ChatGPT, Perplexity, Gemini, Google AI overviews) — neutral (n)
- GSC (AI-mode data where available) — neutral (n)
- Arvow / Journalist AI LLM brand monitors and article generation — PAID ENDORSEMENT (source
  channel affiliate)
- Blotato distribution — PAID ENDORSEMENT (source channel affiliate)

## done_when

- file:capabilities/skills/rig-revenue-ai-citation-gaps/SKILL.md
- grep:capabilities/skills/rig-revenue-ai-citation-gaps/SKILL.md:^## Step 2. Measure baseline
- grep:capabilities/skills/rig-revenue-ai-citation-gaps/SKILL.md:PAID ENDORSEMENT
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-ai-citation-gaps/SKILL.md

## Provenance (videoIds)

oyc-XSLRbBE, vb9SMtUiAIw, IZyBUAkzfp8, 5it1VVQjya0, Hc2Q4BH4G6k, bckxn4Jfkgk, PmeIDWXPcFw,
KqX-7CfxoaM, ssBZ2L3vvYI, MH6B51jrDOA, UAD7_NO6cdw, NAASPeprKPc, ME2YKp2y4Ug. All corpus
figures are unverified creator claims (CLAIM: per rig-revenue-meta).
