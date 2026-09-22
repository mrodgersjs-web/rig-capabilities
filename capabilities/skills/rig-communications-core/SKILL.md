---
name: rig-communications-core
description: >-
  Executable communication engine (formulas, gates, scoring, swarm, tournament)
  + doctrine for all RIG writing surfaces. Score any draft before it ships.
owner: rig-intelligence
domain: Communications
status: Stable
acl: public
tags: [writing,communications,voice,wounds,gates,scoring]
outcome: "content-publishing: every RIG draft is scored and gated by the rig_comm engine before it ships — ship/block verdicts come from exit codes, never from a reader's vibe"
done_when:
  - cmd:python3 -c "import sys; sys.path.insert(0,'capabilities/skills/rig-communications-core'); import rig_comm; print(rig_comm.__name__)"; test $? -eq 0
  - file:capabilities/skills/rig-communications-core/rig_comm/gates.py
  - cmd:cd capabilities/skills/rig-communications-core && PYTHONPATH=. python3 -m rig_comm.cli score /dev/null; test $? -eq 0
  - cmd:cd capabilities/skills/rig-communications-core && python3 tests/test_gate_stack.py; test $? -eq 0
quality_floor: 0.6
---

# RIG Communications Core

The V10/V11 executable communication engine, canonicalized from
`rodgemd1-lgtm/rig-communications` (see `PROVENANCE.md`). Everything is
stdlib-only Python 3; no installs.

## Engine usage

From this skill directory (`capabilities/skills/rig-communications-core`):

```bash
# Full evaluation (exit 0 = can ship, 2 = blocked)
PYTHONPATH=. python3 -m rig_comm.cli evaluate "Your draft text..." --channel email

# Gate a file: ship/block verdict JSON
PYTHONPATH=. python3 -m rig_comm.cli gate path/to/draft.md --channel linkedin

# Formula values for a file (CommRawScore, channel formula/score, phase detection)
PYTHONPATH=. python3 -m rig_comm.cli score path/to/draft.md --channel email

# Doctrine invariants across artifacts
PYTHONPATH=. python3 -m rig_comm.cli doctrine-check --artifact templates/cold-email.md

# AgentForge workflow run
PYTHONPATH=. python3 -m rig_comm.cli run-workflow path/to/workflow.json --draft "..."
```


## Communications OS runtime (v6-v8): `rig_comms`

The engine above scores text. The **runtime** routes a writing task through
the whole OS: surface → packet (voice v2 + wounds + behavior + corpus +
persona) → draft (agent) → deterministic gate stack → ship packet.

```bash
PYTHONPATH=. python3 -m rig_comms surfaces                    # registry JSON
PYTHONPATH=. python3 -m rig_comms route "cold email to dental group"
PYTHONPATH=. python3 -m rig_comms packet --surface emails --brief brief.md
PYTHONPATH=. python3 -m rig_comms score --surface emails --artifact draft.md   # 0 green · 2 red · 3 privacy-lock
PYTHONPATH=. python3 -m rig_comms voice-check --artifact draft.md
PYTHONPATH=. python3 -m rig_comms loop start|correction|ship|escalate --surface <s> --artifact <f>
PYTHONPATH=. python3 -m rig_comms ship --surface <s> --artifact <f>            # fresh gate + sealed packet
PYTHONPATH=. python3 -m rig_comms ledger predict|resolve|outcome|report        # v10/v11
PYTHONPATH=. python3 -m rig_comms media record ...                             # v14 ledger
PYTHONPATH=. python3 -m rig_comms doctor                                       # v9.9 harness drift
```

Gate stack (v7) = V10 engine + voice v2 + wound authenticity/resonance +
fabrication + rubrics — every gate planted-failure-proven
(`tests/test_gate_stack.py`, runs in `done_when`). Closed-loop discipline:
`references/CLOSED-LOOPS.md`. Surface registry: `rig_comms/surfaces.py` is
the single source of truth (lanes, sigma, rubrics, budgets) — the private
love-notes lock is CODE (exit 3), not policy.

Python API: `from rig_comm import evaluate; report = evaluate(text, channel="email")`
→ `report.can_ship`, `report.blocks`, `report.warnings`, `report.channel_score`.

Modules: `core` (evaluate/Report), `formulas` (8 scoring formulas incl. IDP),
`gates` (GateEngine, banned-phrase/reactance gates), `scoring` (BDF30-style
deviation scoring), `swarm` (Prediction Swarm), `tournament` (50→20→8→4→1
IDEATournament), `doctrine`, `prompt`, `agentforge/runner`, `integrations/`
(langgraph, crewai, autogen, mcp, openai_style, guard).

Channels: email (default), linkedin / linkedin_post / linkedin-comment, plus
the template-driven surfaces under `templates/` (cold-email, follow-up, reply,
proposal, internal, linkedin-post, linkedin-comment).

## Doctrine & references

`references/` carries the full doctrine corpus: `DOCTRINE.md`, `PROTOCOL.md`
(Wound→Mirror→Autonomy→Qualification→Open Loop), `FORMULAS.md`, `GATES.md`,
`IDP_FORMULA-card`, `CHANNELS.md`, `TOURNAMENT.md`, `SIGNAL_DETECTION.md`,
`CONSENSUS_RESEARCH.md`, `DEVIATION_QUESTIONS.md`, `AGENTFORGE.md`,
`BEHAVIORAL_REPOS.md`, `LONG_TERM.md`, `NEAR_TERM.md`, `SUMMARY.md` plus the
five quick-reference cards (`idp-formula-card.md`, `tournament-architecture.md`,
`deviation-questions.md`, `signal-detection-repos.md`,
`consensus-research-mapping.md`).

Templates in `templates/` are the seven ready-to-fill drafting skeletons.
`tests/` runs with `python3 -m pytest tests/` (stdlib-compatible asserts) or
plain `python3 tests/test_v11_core.py`.

For the emotional-IP layer (wounds, euphoria protocol, per-surface doctrine)
load `rig-communications-wounds`. For surface→doctrine routing load
`rig-communications-doctrine`.
