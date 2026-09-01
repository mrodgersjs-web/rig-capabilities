---
name: frontier-self-improvement-loops
description: Frontier research — self-improving agent loops that grow skill libraries from experience (2026)
source: frontier
outcome: research-intel: self-improvement loops
verified_on: 2026-08-31
quality_floor: 0.6
---

# Self-Improvement Loops — Frontier Findings (2026-08-31)

## Verified-skill libraries are the through-line from Voyager to 2026
Voyager's discipline still defines the pattern: the agent writes candidate skills, but
only **verifiably working** programs enter the library (environment feedback + execution
success + self-verification), skills form a dependency-ordered curriculum, and failed
drafts go through a bounded repair loop (execute → read errors → refine).

## 2026 systems: non-parametric self-improvement via external skill memory
- **Memento-Skills** (arXiv 2603.18743): skills (code, prompts, specs) as external
  memory; a Read–Write reflective learning loop autonomously acquires, refines, and
  reuses skills from deployment experience — a frozen LLM self-improves by growing its
  library. Behavior-aligned router selects; evolution engine writes. GAIA/HLE gains with
  cross-task transfer when skills align to structured domain categories (5 atomic →
  hundreds of capabilities).
- **SkillX** (arXiv 2604.04804): fully automated plug-and-play SkillKB with multi-level
  skill design (experience → strategy → pattern levels) for transferability.
- **SAGE** (arXiv 2512.17102): RL specifically *for* skill-library agents — generate and
  use skills in one loop.
- **RAR / Reflexion lineage** (USD-AI-ResearchLab): retrieval-augmented reflexion —
  retrieve semantically similar past trajectories, diversify with MMR, use as
  contrastive reflection context; learning spans a broad failure/success history, not
  just the last attempt.
- **ERL** (arXiv 2603.24639): Experiential Reflective Learning builds a reusable pool of
  heuristics from past traces — fast environment adaptation, no retraining.

## The hard lesson: self-generated ≠ good
SkillsBench (below, evaluation strand) found **self-generated skills give little to no
average benefit** over curated ones. Voyager's answer was verification-gating on green
execution. Every 2026 loop inherits it: draft freely, admit only what passes.

## What this means for rig-capabilities
1. V16's graduate-only-on-green round engine is exactly the Voyager admission gate,
   deterministic version. The frontier-validated extension: pull draft candidates from
   *traces* (SAGE/RAR pattern) — our `traces` table (V14) + `.context/requests.jsonl`
   gap cells are the trajectory corpus; the round engine should mine failed/partial
   traces for new-asset drafts, not just patch existing contracts.
2. Memento's "skills as memory, frozen model" == our catalog+lanes; its Read-Write loop
   maps to context_pack (Read) + rounds (Write).
3. RAR's MMR-diversified retrieval warns against our rounds re-patching the same weakest
   asset every cycle — `pick_candidates` should exclude recently-graduated ids per lane.

## Sources
- https://vibeengines.com/paper/voyager (Voyager skill library mechanics)
- https://arxiv.org/pdf/2603.18743 (Memento-Skills)
- https://arxiv.org/pdf/2604.04804 (SkillX SkillKB)
- https://arxiv.org/html/2512.17102 (SAGE RL + skill library)
- https://github.com/USD-AI-ResearchLab/reflexion (RAR)
- https://arxiv.org/pdf/2603.24639 (ERL)
- https://github.com/ReflexioAI/reflexio (harness turning user corrections into improvements)
