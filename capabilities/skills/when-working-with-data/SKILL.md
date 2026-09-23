---
name: when-working-with-data
description: "When building pipelines, validating data contracts, measuring freshness or latency, or querying stores, use this to route to the right data skill. Routes to 62 skills; read references/routing.md for the full table."
metadata:
  purpose: meta-skill
  generated-by: skillshilp-upgrade
  category: data-analytics
  skill-count: "62"
---

# when-working-with-data

Tier-1 meta-skill. Job to be done: When building pipelines, validating data contracts, measuring freshness or latency, or querying stores, use this to route to the right data skill.

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
1. Scan the quick index below. If nothing obviously matches, read `references/routing.md` for the full 62-skill table with one-line descriptions.
2. Load exactly one child skill. If it names sub-skills, load the one relevant sub-skill.
3. Never load more than one skill plus one sub-skill for a single task step.

## Quick index (top skills)
- **data-contract-validator** — Fail-closed validation that an incoming dataset matches its versioned schema contract (col
- **data-freshness-monitor** — Measure per-table/source data staleness against SLA minutes for Nadia's data department. Q
- **data-manager-api-audience-ingestion** — >-   Guides developers through managing (adding, removing, and clearing) audience members 
- **data-manager-api-event-ingestion** — >-   Guides developers through implementing event and conversion ingestion to   Google pro
- **data-manager-api-setup** — >-   Guides developers through client library installation and authentication setup   step
- **data-quality-frameworks** — Implement data quality validation with Great Expectations, dbt tests, and data contracts. 
- **data-query-latency-audit** — Find and rank the slowest SQL queries, capture p95 not mean, and prove latency improvement
- **data-report-template** —   CSV/Excel/JSON              " tags: ["data", "report", "chart", "  ", "  "] metadata:   
- **data-storytelling** — Transform data into compelling narratives using visualization, context, and persuasive str
- **alloydb-basics** — >-   Manages clusters, instances, and backups for AlloyDB for PostgreSQL, and   integrates
- **android-clean-architecture** — Clean Architecture patterns for Android and Kotlin Multiplatform projects   module structu
- **azure-kusto** — Query and analyze data in Azure Data Explorer (Kusto/ADX) using KQL for log analytics, tel

Full table: `references/routing.md`
