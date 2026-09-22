---
name: rig-communications-doctrine
description: >-
  Doctrine index for every RIG writing surface: routes a surface (cold email,
  LinkedIn, reply, proposal, song, spec, research) to the governing doctrine
  doc in rig-communications-core/ Load before drafting anything;
  pair with rig-communications-core to score the draft.
owner: rig-intelligence
domain: Communications
status: Stable
acl: public
tags: [writing,communications,doctrine,voice]
outcome: "content-publishing: a writer never guesses which doctrine applies — each surface resolves to exactly the reference doc(s) that govern it"
done_when:
  - file:capabilities/skills/rig-communications-doctrine/SKILL.md
  - grep:capabilities/skills/rig-communications-doctrine/SKILL.md:DOCTRINE.md
  - cmd:python3 -c "import pathlib as p; d=p.Path('capabilities/skills/rig-communications-core/references'); missing=[f for f in ['DOCTRINE.md','PROTOCOL.md','FORMULAS.md','GATES.md','CHANNELS.md','IDP_FORMULA.md','TOURNAMENT.md','SIGNAL_DETECTION.md','CONSENSUS_RESEARCH.md','DEVIATION_QUESTIONS.md','AGENTFORGE.md','BEHAVIORAL_REPOS.md','INTEGRATION.md','LONG_TERM.md','NEAR_TERM.md','SUMMARY.md','idp-formula-card.md','tournament-architecture.md','deviation-questions.md','signal-detection-repos.md','consensus-research-mapping.md'] if not (d/f).exists()]; assert not missing, missing"; test $? -eq 0
quality_floor: 0.6
---

# RIG Communications Doctrine Router

All doctrine text lives in
`capabilities/skills/rig-communications-core/references/` (canonical copy from
`rig_comm` V10/V11; see that skill's `PROVENANCE.md`). This skill is the index:
given a surface, read these docs, in this order.

## Surface → doctrine routing table

| Surface | Governing docs (read in order) |
|---|---|
| Cold email | `PROTOCOL.md` (Wound→Mirror→Autonomy→Qualification→Open Loop) → `DOCTRINE.md` → `GATES.md` (banned phrases/reactance) → `FORMULAS.md` §email → template `templates/cold-email.md` |
| Follow-up / reply | `PROTOCOL.md` → `CHANNELS.md` §reply → `GATES.md` → template `templates/follow-up.md` / `templates/reply.md` |
| LinkedIn post / comment | `CHANNELS.md` §linkedin → `DOCTRINE.md` → `DEVIATION_QUESTIONS.md` → templates `linkedin-post.md` / `linkedin-comment.md` |
| Proposal / internal memo | `CHANNELS.md` → `DOCTRINE.md` → templates `proposal.md` / `internal.md` |
| Any draft being scored | `FORMULAS.md` (8 formulas) → `IDP_FORMULA.md` + `idp-formula-card.md` → `GATES.md` → run `rig_comm.cli score/gate` |
| Idea generation / variants | `TOURNAMENT.md` + `tournament-architecture.md` → `DEVIATION_QUESTIONS.md` + `deviation-questions.md` |
| Prospect signal research | `SIGNAL_DETECTION.md` + `signal-detection-repos.md` + `BEHAVIORAL_REPOS.md` |
| Claims needing sources | `CONSENSUS_RESEARCH.md` + `consensus-research-mapping.md` |
| Workflow/agent wiring | `AGENTFORGE.md` → `INTEGRATION.md` (langgraph/crewai/autogen/mcp) |
| Roadmap / what's next | `NEAR_TERM.md` (V10→V15) → `LONG_TERM.md` → `SUMMARY.md` |

## Rules

1. Never ship a draft without the surface's governing docs read and the
   `rig_comm` gate run (`can_ship` exit 0).
2. Where docs conflict, `DOCTRINE.md` wins; the Python engine in
   `rig_comm/gates.py` is the executable arbiter.
3. The emotional-IP layer (wounds, euphoria, per-vertical voice) is in
   `rig-communications-wounds`; doctrine here is the craft layer.
