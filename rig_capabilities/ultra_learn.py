"""W10 outcome engine: what to do with a measured candidate.

States are terminal per evaluation: no_change (candidate did not beat incumbent),
insufficient_evidence (trials below the floor -- cannot conclude either way),
candidate_rejected (candidate measurably worse), promotion_candidate (better by
margin AND enough trials). Nothing here ever adopts: adoption is a human act
(the variant_proposal staged-not-adopted invariant holds downstream).
"""
MIN_TRIALS = 20
MARGIN = 0.05

def evaluate(incumbent, candidate):
    """incumbent/candidate: {"wins": int, "trials": int}. Deterministic."""
    ci, cc = incumbent.get("trials", 0), candidate.get("trials", 0)
    if ci < MIN_TRIALS or cc < MIN_TRIALS:
        return {"outcome": "insufficient_evidence",
                "why": "trials %d/%d below floor %d" % (ci, cc, MIN_TRIALS)}
    ri = incumbent["wins"] / ci
    rc = candidate["wins"] / cc
    if rc < ri:
        return {"outcome": "candidate_rejected", "gap": round(ri - rc, 4)}
    if rc - ri <= MARGIN:
        return {"outcome": "no_change", "gap": round(rc - ri, 4), "margin_required": MARGIN}
    return {"outcome": "promotion_candidate", "gap": round(rc - ri, 4), "adopt": "human-only"}

def schedule(t0, horizons=(7, 30, 90)):
    """T+N outcome due dates (seconds); sorted, de-duplicated, positive N only."""
    return sorted({t0 + int(h) * 86400 for h in horizons if int(h) > 0})
