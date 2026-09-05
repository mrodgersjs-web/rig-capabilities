---
name: great-iqrsqpi-v10
lane: agent-engineering
source: canonical-curated
exemplar_of: iqrsqpi-v10
description: Reference exemplar — IQRSQPI v10 stdlib stage-order runtime
---

# iqrsqpi-v10 — reference

Canonical asset `iqrsqpi-v10` (skill). Path: `capabilities/skills/iqrsqpi-v10`.

A great v10 pass names two parties (`verifier != generator`), records in-order stage tokens, and has on-disk artifacts for every reached stage. `certify --only stage_order` is the green; fabricating a missing artifact to silence `run_pass` is the anti-pattern.
