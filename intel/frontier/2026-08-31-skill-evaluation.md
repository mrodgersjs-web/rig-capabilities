---
name: frontier-skill-evaluation
description: Frontier research — benchmarks and methods for evaluating agent skills (2026)
source: frontier
outcome: research-intel: skill evaluation
verified_on: 2026-08-31
quality_floor: 0.6
---

# Skill Evaluation — Frontier Findings (2026-08-31)

2026 is the year skill evaluation got real. Four results define the field:

## SkillsBench (arXiv 2602.12670)
84 tasks × 11 domains on the Harbor framework; every task ships an environment,
**deterministic verifiers**, and an oracle solution. 7,308 trajectories across 7
agent-model configs comparing no-skills / curated / self-generated:
- Curated skills: **+16.2 pp average pass rate**, domain-dependent.
- **Self-generated skills: little to no average benefit.**
- Focused 2–3 module skills beat broad documentation.
- Smaller models + skills can match larger models without.

## ACES — Agentic Continuous Evaluation of Skills (arXiv 2608.20614)
Evaluates skills *as executable artifacts*. Three interfaces: an evaluation-asset
contract (authoring), an adapter creating paired runtime tasks, and an ATIF trajectory
contract for cross-harness comparison. Protocol: run **paired conditions** (with-skill
vs skill-withheld, prerequisites/decoys fixed). The metric is **Skill Lift** — marginal
value under fixed agent/task/workspace/grader. 947 paired cases across 58 production
skills and 4 harnesses: mean composite lift 0.2134 (95% CI [0.1967, 0.2301]); positive
in 72.8% of cases; per-harness deltas (OpenCode 0.36, Claude Code 0.29, Codex 0.13).
NVIDIA's SkillEvaluator is the open-source implementation.

## The Regression Tax (arXiv 2607.22520)
5,832 task-condition runs: 553 gains vs 324 regressions — **regressions eat 59% of gross
gains**. Three named causes: (1) *skill-description osmosis* — a description in context
shifts behavior even when never invoked; (2) *grounding displacement* — prescribed
procedure overrides the agent's reading of inputs; (3) *verification displacement* —
procedures suppress output checks. Guidance: report **paired gain AND regression
counts**, test description-in-context separately from body invocation.

## Skill-Use (arXiv 2608.04828) + Layer-Isolated Evaluation (arXiv 2606.11686)
Skill-Use measures whether agents can *actually use* skills under progressive disclosure
(name/description revealed, procedure must be retrieved). Layer-Isolated Evaluation
gates the deterministic scaffold of a production agent with a **no-LLM, regression-locked
test harness** — the LLM layer is evaluated separately from routing/safety/decomposition
layers. Anthropic's "Demystifying evals" separates eval-harness from agent-harness.

## What this means for rig-capabilities
1. Our V15 done-tests are static/structural — necessary, not sufficient. The frontier
   unit of evaluation is the *paired run*: with-asset vs withheld. V22's certify.py
   should adopt ACES' lift protocol for the flagship lane (one task, two conditions).
2. Regression Tax → our quality-runs should count regressions explicitly; a round that
   raises pass-rate while introducing description-osmosis risk needs a paired check.
3. SkillsBench's "self-generated skills don't help" is the strongest argument in our
   favor for graduate-only-on-green + curated great_examples — curation is the win.
4. No-LLM regression-locked scaffold tests (Layer-Isolated) = exactly our V29 whole-repo
   certification test; keep that boundary clean (deterministic tests never call LLMs).

## Sources
- https://arxiv.org/abs/2602.12670 (SkillsBench)
- https://arxiv.org/html/2608.20614v1 (ACES / Skill Lift / NVIDIA SkillEvaluator)
- https://arxiv.org/html/2607.22520 (Regression Tax)
- https://arxiv.org/html/2608.04828v1 (Skill-Use)
- https://arxiv.org/html/2606.11686v1 (Layer-Isolated Evaluation)
- https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- https://github.com/nano-step/eval-harness (behavior-regression, 4-class attribution)
