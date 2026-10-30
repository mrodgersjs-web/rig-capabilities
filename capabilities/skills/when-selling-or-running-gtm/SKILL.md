---
name: when-selling-or-running-gtm
description: "When prospecting, pricing, campaigning, forecasting, or running customer success, use this to route to the right GTM skill so revenue work follows doctrine. Routes to 409 skills; read references/routing.md for the full table."
metadata:
  purpose: meta-skill
  generated-by: skillshilp-upgrade
  category: gtm-sales-revenue
  skill-count: "409"
done_when:
  - 'grep:capabilities/skills/when-selling-or-running-gtm/SKILL.md:[M]UST NOT load a second child to'
  - 'grep:capabilities/skills/when-selling-or-running-gtm/SKILL.md:[M]UST load exactly ONE child skill per task step'
  - 'grep:capabilities/skills/when-selling-or-running-gtm/references/routing.md:^\| Skill \| Source \| One-liner \| Sub-skills \|'
---

# when-selling-or-running-gtm

Tier-1 meta-skill. Job to be done: When prospecting, pricing, campaigning, forecasting, or running customer success, use this to route to the right GTM skill so revenue work follows doctrine.

## Hierarchy
1. **Meta-skill (this file)** — the skill you call up for this job. Routes only; holds no doctrine of its own.
2. **Skills** — load the named child skill's SKILL.md and follow it. Each child is written to route further when it owns a family.
3. **Sub-skills** — a skill whose routing entry lists sub-skills delegates further; load only the one sub-skill the task needs.

## Routing contract (binding)
- MUST route through this meta-skill first for any job in its description; never load a child directly from memory of its name.
- MUST load exactly ONE child skill per task step; never bulk-load children from the index.
- MUST load only the single sub-skill the task needs, only when the loaded child names sub-skills.
- MUST NOT load a second child to "compare"; if two children seem to match, pick by the routing table one-liner in references/routing.md, then load that one.
- The quick index below is a relevance-ordered SAMPLE, not the full set; if no index entry fits the task, scan the full table in references/routing.md before choosing.
- If no child matches the task, load `when-nothing-else-fits` instead of guessing.
- If a child skill fails to load or is missing, report the broken route and stop; do not improvise its content.

## How to route
1. Scan the quick index below. If nothing obviously matches, read `references/routing.md` for the full 409-skill table with one-line descriptions.
2. Load exactly one child skill. If it names sub-skills, load the one relevant sub-skill.
3. Never load more than one skill plus one sub-skill for a single task step.

## Quick index (top skills)
- **blueprintgtm-30k-jobs-prospects** — Use when scaling prospecting to 30K+ contacts. BlueprintGTM's 30K Jobs & Prospects   scale
- **blueprintgtm-ai-lead-enrichment** — Use when enriching leads with AI. BlueprintGTM's AI Lead Enrichment   use ChatGPT/Claude t
- **blueprintgtm-cannonball-method** — Use when building a full GTM motion from scratch. Jordan Crawford's Cannonball method   ze
- **blueprintgtm-company-people-targeting** — Use when targeting specific people at specific companies. BlueprintGTM's Company & People 
- **blueprintgtm-g2-reviews-analysis** — Use when analyzing competitor reviews for GTM insights. BlueprintGTM's G2 Reviews Analysis
- **blueprintgtm-gtm-strategy-ocean** — Use when building GTM strategy with lookalike audiences. Jordan Crawford's Ocean.io strate
- **blueprintgtm-icp-to-inbox** — Use when going from zero knowledge to a shipped outbound campaign. Jordan Crawford's ICP-t
- **blueprintgtm-last-sdr** — Use when automating B2B outbound with AI. The Last SDR   how to use AI to replace manual o
- **blueprintgtm-multi-persona-targeting** — Use when targeting multiple personas in one campaign. BlueprintGTM's multi-persona targeti
- **blueprintgtm-vibe-engineering** — Use when identifying GTM strategy for a new company. Vibe Engineering   Jordan Crawford's 
- **bp-company-search** — Use when applying the BlueprintGTM AI-Powered Company & People Search method. Drops into d
- **bp-custom-gpt-builder** — Use when applying the BlueprintGTM Custom GPT Builder for GTM Operations method. Drops int
- **ms-product-marketing** — Use first on any marketing task: builds `.agents/product-marketing.md`, the product/ICP/positioning context every other marketing skill reads (marketingskills import, MIT).
- **ms-\* family (marketingskills, MIT, 39 GTM skills)** — product-marketing, pricing, offers, cold-email, ads, cro, prospecting, launch, analytics, attribution, seo family, revops, churn, onboarding; full one-liners in references/routing.md.

Full table: `references/routing.md`
