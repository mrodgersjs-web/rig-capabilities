"""DOCTRINE.md §2.1 — Robust-MAD-Z scoring core.

    rawMAD       = median(|score_i − median(scores)|)
    RobustMADZ   = 0.6745 · (score − median(baselineScores)) / rawMAD

The 0.6745 constant restores standard-normal scale under MAD. All 40 engines
emit RobustMADZ — never raw z-scores, never mean/stdev. Outliers in the
generic-baseline corpus must not contaminate the median.
"""
from __future__ import annotations
import statistics
from typing import Sequence

# Restores standard-normal scale under MAD. Φ⁻¹(0.75) = 0.6745
NORMALITY_CONSTANT = 0.6745

# Floor to prevent division by zero AND to prevent tiny-MAD blow-ups when
# baseline samples cluster too tightly. Raw scores are on a 0-100 scale, so
# a floor of 5.0 represents "baselines vary by at least 5 points either side".
MAD_FLOOR = 5.0


def mad(values: Sequence[float]) -> float:
    """Median absolute deviation from the median (RAW, no floor).

    rawMAD = median(|x_i − median(x)|)

    Returns 0.0 for all-identical inputs. Use `robust_mad_z()` for the
    floor-protected divisor used in σ scoring.
    """
    if not values:
        return 0.0
    med = statistics.median(values)
    deviations = [abs(x - med) for x in values]
    return statistics.median(deviations)


def robust_mad_z(score: float, baseline_scores: Sequence[float]) -> float:
    """Compute the Robust-MAD-Z of `score` against `baseline_scores`.

    Returns the sigma rating per DOCTRINE.md §2.1.
    Applies MAD_FLOOR to prevent division-by-zero AND to prevent tiny-MAD
    baseline distributions from producing impossibly-large σ values.
    """
    if not baseline_scores:
        # No baseline → cannot deviate from nothing. Return 0σ (generic median).
        return 0.0
    baseline_median = statistics.median(baseline_scores)
    raw_mad = max(mad(baseline_scores), MAD_FLOOR)
    return NORMALITY_CONSTANT * (score - baseline_median) / raw_mad


def robust_mad_z_batch(scores: Sequence[float],
                        baseline_scores: Sequence[float]) -> list[float]:
    """Vectorized — score every item in `scores` against the same baseline."""
    return [robust_mad_z(s, baseline_scores) for s in scores]
