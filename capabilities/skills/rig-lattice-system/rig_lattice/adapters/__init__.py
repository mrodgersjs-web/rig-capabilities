"""DOCTRINE.md §5 adapters package.

  - llm.py             — LiteLLM router for fuzzy-metric scoring
  - criteria_runner.py — convert YAML criteria pack → raw_fn (deterministic)
  - baselines.py       — 10 baseline-type generators per DOCTRINE §9
"""
from rig_lattice.adapters.llm import llm_score, LLMResponse, OFFLINE_MODE, offline_mode
from rig_lattice.adapters.criteria_runner import raw_score_from_criteria, score_one_question
from rig_lattice.adapters.baselines import (
    BASELINE_CORPUS, baseline_scores_for_engine,
    BASELINE_TYPES, get_baseline_samples,
)

__all__ = [
    "llm_score", "LLMResponse", "OFFLINE_MODE", "offline_mode",
    "raw_score_from_criteria", "score_one_question",
    "BASELINE_CORPUS", "baseline_scores_for_engine",
    "BASELINE_TYPES", "get_baseline_samples",
]
