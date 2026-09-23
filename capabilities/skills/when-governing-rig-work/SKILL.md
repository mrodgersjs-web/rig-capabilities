---
name: when-governing-rig-work
description: "When doing any RIG-internal build, review, or claim, use this to route to the governing doctrine (IQRSQPI, gates, ProofPackets, lattice, deviation engines) so the work follows hard law instead of vibes. Routes to 32 skills; read references/routing.md for the full table."
metadata:
  purpose: meta-skill
  generated-by: skillshilp-upgrade
  category: rig-core-doctrine
  skill-count: "32"
---

# when-governing-rig-work

Tier-1 meta-skill. Job to be done: When doing any RIG-internal build, review, or claim, use this to route to the governing doctrine (IQRSQPI, gates, ProofPackets, lattice, deviation engines) so the work follows hard law instead of vibes.

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
1. Scan the quick index below. If nothing obviously matches, read `references/routing.md` for the full 32-skill table with one-line descriptions.
2. Load exactly one child skill. If it names sub-skills, load the one relevant sub-skill.
3. Never load more than one skill plus one sub-skill for a single task step.

## Quick index (top skills)
- **iqrsqpi-v10** — RIG doctrine   IQRSQPI v10 as an executable stdlib runtime, not a prose ritual. The seven 
- **iqrsqpi-v11** — RIG doctrine   IQRSQPI v11, the gated loop. Intent   Question   Research   Solution   Qual
- **iqrsqpi-v20** — RIG doctrine   IQRSQPI v20, the fractal self-verifying loop. Intent (executable done-tests
- **iqrsqpi-v20-slice** — RIG doctrine   the child loop of IQRSQPI v20: one context-sized slice, Build   Verify (che
- **adversarial-verification-loop** — RIG doctrine   Adversarial Verification (non-vacuity) as a code-enforced loop. For every g
- **gate-d-loop** — RIG doctrine   Gate-D as a code-enforced loop. Wrap any outward or irreversible action (se
- **jake-lessons-ledger** — Consult Mike's distilled lesson ledger before coding, scraping, fleet, extension, or dispa
- **jake-pai-doctrine** —     Jake PAI Operating Doctrine   the soul of the RIG agent ecosystem.   Merged intelligen
- **jake-pai-doctrine-loader** — Load the canonical Jake PAI substrate for Jake, RIG, Hermes, OpenClaw, founder, co-founder
- **north-star-lock-loop** — RIG doctrine   North-Star Lock + Anchor as a code-enforced loop. Lock a Goal Card (GOAL, b
- **phase-discipline-loop** — RIG doctrine   Phase Discipline as a code-enforced loop. Order phases by dependency (rever
- **prime-jake-coding-fleet** — Prime Jake control plane for native Prime RLM children plus Claude, OMP, Codex, Hermes, an

Full table: `references/routing.md`
