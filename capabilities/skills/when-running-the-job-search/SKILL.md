---
name: when-running-the-job-search
description: "When sourcing roles, tailoring resumes, applying, prepping interviews, or filing unemployment certifications, use this to route to the Operation Get a Job skills. Routes to 12 skills; read references/routing.md for the full table."
metadata:
  purpose: meta-skill
  generated-by: skillshilp-upgrade
  category: job-career
  skill-count: "12"
done_when:
  - 'grep:capabilities/skills/when-running-the-job-search/SKILL.md:[M]UST NOT load a second child to'
  - 'grep:capabilities/skills/when-running-the-job-search/SKILL.md:[M]UST load exactly ONE child skill per task step'
  - 'grep:capabilities/skills/when-running-the-job-search/references/routing.md:^\| Skill \| Source \| One-liner \| Sub-skills \|'
---

# when-running-the-job-search

Tier-1 meta-skill. Job to be done: When sourcing roles, tailoring resumes, applying, prepping interviews, or filing unemployment certifications, use this to route to the Operation Get a Job skills.

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
1. Scan the quick index below. If nothing obviously matches, read `references/routing.md` for the full 12-skill table with one-line descriptions.
2. Load exactly one child skill. If it names sub-skills, load the one relevant sub-skill.
3. Never load more than one skill plus one sub-skill for a single task step.

## Quick index (top skills)
- **aside-job-browser** — Execute one approved job application visibly in Aside with fresh form state, single-writer
- **aside-job-learning** — Turn verified job-search and interview outcomes into bounded improvements without invented
- **aside-job-operator** — Run Mike's job search directly in Aside: ApplyPilot sourcing, source-bound resume tailorin
- **aside-job-recovery** — Reconcile application receipts and recover browser/portal failures without duplicates or f
- **aside-job-resume** — Tailor and review resumes against authoritative source claims, exact employer requirements
- **aside-job-source** — Qualify and deduplicate job candidates from existing ApplyPilot/Luca discovery and officia
- **application-packet-builder** — Batch-generate job application packets (dossier.md + cover_letter.md) from a scraped job l
- **co-unemployment-certification** — File Mike Rodgers' Colorado UI weekly certification (MyUI+ / CDLE) from inside Aside   ID.
- **co-unemployment-filing** — File CO UI-2014 weekly certs via EGO + ID.me + Luca queue. metadata:   version: "0.6.0"   
- **julie-w2-applypilot** — Run Mike Rodgers's application-first job search in Hermes using ApplyPilot state, Ego brow
- **pre-interview-meta** — Load this skill when Mike asks for any of: pre-interview, mock interview, intake for an in
- **resume-screening-stack** — Grade and repair Mike's resume against the real hiring stack - parse, knockout, literal se

Full table: `references/routing.md`
