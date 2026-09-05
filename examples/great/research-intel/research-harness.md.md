---
name: great-research-harness
lane: research-intel
source: canonical-curated
exemplar_of: research-harness
description: "Reference exemplar for evidence-dense research with source-per-claim traceability, falsification, calibrated confidence, and explicit unknowns."
---

# Research loop: evaluate a market claim

## Input

Lock one decision question and evidence boundary. Consult at least five distinct sources, prioritizing original papers, official documentation, and direct datasets. For each major conclusion, record the observation that would refute it and seek that evidence before assigning confidence.

```console
$ python3 scripts/assert_loop_termination.py capabilities/loops/research-harness.md
```

## Output

The loop contract validates. The research artifact contains an executive summary, numbered findings, recommendations, a source list, and a confidence matrix. All 12 factual claims resolve to sources; at least three sampled URLs return the cited content, exact quotes match verbatim, and every number is dated. One conventional view is challenged with evidence rather than posture. The proof packet records seven sources, four primary sources, 12/12 sourced claims, three falsification attempts, confidence bands, and zero unsourced claims.

## Acceptance

- The command exits 0.
- Claim-source coverage is 100%, with inaccessible evidence labeled rather than invented.
- Conclusions include refutation criteria and justified HIGH/MEDIUM/LOW confidence; contradictions get their own section.
- Findings remain internal unless Gate-D approval authorizes external publication, especially where named individuals could be affected.
