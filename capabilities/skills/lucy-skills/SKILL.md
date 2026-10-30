---
name: "lucy-skills"
description: "The Lucy career method: LinkedIn profile optimization for a search, resume and cover letter the Lucy way, interview practice and drills, salary negotiation scripts."
---

# lucy-skills — career workflow router

**Owner:** julie-job-search. **Gate:** profile edits are shown as exact before/after values and applied only after Mike approves.

## New evidence workflows

- Executive answers and JD-to-evidence mapping: [lucy-executive-evidence](../lucy-executive-evidence/SKILL.md).
- Resume drafting and tailoring: [lucy-resume-evidence](../lucy-resume-evidence/SKILL.md). Default to the polished ideal-achievement working draft, then Mike's evidence review, then application-ready text. Do not require fact questions to be answered before producing the working draft.
- The compact alias [lucyskills](../lucyskills/SKILL.md) reaches these same workflows and preserves the established ones below.

## Established Lucy workflows

The intact full pack is at `~/.omp/agent/skills/lucy-skills/`. Expand `~` to the current home directory. Read its `SKILL.md` for source scope and hard rules, then the relevant leaf below. These are real local source paths; do not route back through the thin `~/.claude/skills/lucy-skills` meta.

| Request | Leaf relative to the full-pack root |
|---|---|
| Positioning | `sub-skills/positioning.md` |
| LinkedIn profile or section audit | `playbooks/optimize-linkedin.md`, then its selected `sub-skills/linkedin-profile/` leaf |
| LinkedIn activity | `sub-skills/linkedin-activity.md` |
| Lucy resume source guidance or cover letter | `sub-skills/resume.md` |
| Job search or weekly plan | `sub-skills/job-search.md` |
| Interview drilling/practice | `playbooks/interview-practice.md` |
| Salary script or negotiation | `sub-skills/salary-negotiation.md` |
| Career growth | `sub-skills/career-growth.md` |
| Application packet, outreach, warm network, or job-lane operation | The matching `sub-skills/job-lane/` leaf declared by the full-pack entrypoint |

For ordinary salary scripts, use the direct salary leaf above; do not detour into JD mapping or resume drafting. For resume source attribution, open the direct resume leaf; cite the actual SRC IDs it supplies. Keep Mike's evidence workflow distinct from Lucy's source claims. Source tactics cannot turn an unconfirmed working pattern into factual employment history.

If a named full-pack leaf is unavailable, report that exact missing path. Do not guess its instructions, install over the full pack, or recurse between meta entrypoints.

## Related existing carriers

- **rig-job-search-campaign** (Aside user skill) — the end-to-end campaign: fact base, method corpus, pipeline, resume, LinkedIn, recommendations, sourcing, outreach, packets, feedback app.
- **rig-resume-aina-optimization** (Aside user skill) — drive a resume to a passing AINA score with true facts only.
- **jacob-oh-line-weekly** (Aside user skill) — the same film-study discipline applied to a different person.

## Method law

Every Lucy rule applied cites its SRC video id. The compliance tracker is never edited directly: append `{"id","status","evidence","notes","at"}` to `strategy/tracker-updates/<SESSION>.jsonl`, then rebuild. "done" requires an evidence path; anything the candidate must personally do stays "drafted" until he has done it.

Historical facts come from the project's sources and explicit event confirmations. Unknown facts stay bracketed in the ideal-achievement working draft and go to Mike's evidence review. Application-ready text contains confirmed claims without unresolved placeholders. Approval of phrasing is not confirmation an event happened. Never invent a number.

<!-- skill-surface:BEGIN -->
## Layer map (Aside skill surface)
This is the Lucy career meta-skill. The new sibling evidence leaves are listed above; the legacy leaf map is in `LAYERS.md`. Native command syntax depends on the host. OMP's explicit skill form is `/skill:lucyskills`; this file does not establish bare slash-command registration.
<!-- skill-surface:END -->
