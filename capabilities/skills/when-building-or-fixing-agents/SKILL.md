---
name: when-building-or-fixing-agents
description: "When creating, editing, installing, or evaluating agents, skills, hooks, or harnesses, use this to route to the agent-infrastructure skills so the fleet gets stronger instead of snowflaked. Read references/routing.md for the full table."
metadata:
  purpose: meta-skill
  generated-by: skillshilp-upgrade
  category: agent-infrastructure
  skill-count: "275"
---

# when-building-or-fixing-agents

Tier-1 meta-skill. Job to be done: When creating, editing, installing, or evaluating agents, skills, hooks, or harnesses, use this to route to the agent-infrastructure skills so the fleet gets stronger instead of snowflaked.

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
1. Scan the quick index below. If nothing obviously matches, read `references/routing.md` for the full routing table with one-line descriptions.
2. Load exactly one child skill. If it names sub-skills, load the one relevant sub-skill.
3. Never load more than one skill plus one sub-skill for a single task step.

## Quick index (top skills)
- **JevRouter** (BillionsBobby/JevRouter, replaces retired rig-coding-agent-router) — Select the lead, specialist, subagent, skill, and stored prompt for a coding mission. Lives in each coding-agent harness (Codex/Claude/Cursor/Hermes/OMP/Prime Agent); routes via TypeSafe Jev Choice over the live candidate set with receipts at `~/.jevrouter/decisions/`. Do not re-add rig-coding-agent-router — that path is closed.
- **harness-mh-01-skill-genesis-session** — Canonical RIG harness for meta." ---  # meta  Use this as a hard-gated session contract. R
- **harness-mh-02-harness-forge-session** — Canonical RIG harness for meta." ---  # meta  Use this as a hard-gated session contract. R
- **harness-mh-03-agent-composition-session** — Canonical RIG harness for meta." ---  # meta  Use this as a hard-gated session contract. R
- **harness-mh-04-deviation-expedition-session** — Canonical RIG harness for meta." ---  # meta  Use this as a hard-gated session contract. R
- **harness-mh-05-asset-pruning-session** — Canonical RIG harness for meta." ---  # meta  Use this as a hard-gated session contract. R
- **harness-mh-06-install-verification-session** — Canonical RIG harness for meta." ---  # meta  Use this as a hard-gated session contract. R
- **agency-agents** — Agency Agents roster   232 installable Agency specs exposed to Codex as safe `agency-*` TO
- **agent-bms-band-assigner** — Assign BMS bands to every agent in a roster so routing strictness matches each agent's bla
- **agent-browser** — Drive a real browser via the agent-browser CLI daemon to navigate, fill forms, click, scre
- **agent-chief-claude-code** — Route everything noteworthy through Chief instead of interrupting the user. Use whenever a
- **agent-chief-openclaw** — Route everything noteworthy through Chief instead of messaging the user. Use whenever a he
- **agent-demo-lead-engine** — Package an AI capability demo (dashboard, agent workflow) as a lead magnet: deploy the dem

Full table: `references/routing.md`
