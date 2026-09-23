---
name: when-securing-the-estate
description: "When triaging vulnerabilities, sweeping secrets, investigating auth failures, or handling incidents, use this to route to the right security skill. Routes to 7 skills; read references/routing.md for the full table."
metadata:
  purpose: meta-skill
  generated-by: skillshilp-upgrade
  category: security-ops
  skill-count: "7"
---

# when-securing-the-estate

Tier-1 meta-skill. Job to be done: When triaging vulnerabilities, sweeping secrets, investigating auth failures, or handling incidents, use this to route to the right security skill.

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
1. Scan the quick index below. If nothing obviously matches, read `references/routing.md` for the full 7-skill table with one-line descriptions.
2. Load exactly one child skill. If it names sub-skills, load the one relevant sub-skill.
3. Never load more than one skill plus one sub-skill for a single task step.

## Quick index (top skills)
- **sec-auth-failure-investigation** — Investigate spikes in authentication failures for Vera's security department: distinguish 
- **sec-dependency-vuln-triage** — Turn raw dependency scan output (npm audit, trivy, gh advisories, semgrep) into a ranked a
- **sec-secret-leak-sweep** — Sweep a repo and its git history for committed credentials, classify true vs false positiv
- **red-team** — Military-grade adversarial analysis that deploys 32 parallel expert agents (engineers, arc
- **rig-top100-deployment-automation** — RIG Top 100 capability #44: Deployment & Infrastructure. Ship fast, ship safe" ---  # Depl
- **rig-top100-monitoring-alerting** — RIG Top 100 capability #45: Monitoring & Alerting. Downtime kills trust" ---  # Monitoring
- **rig-top100-security-hardening** — RIG Top 100 capability #46: Security & Compliance. Enterprise clients require it" ---  # S

Full table: `references/routing.md`
