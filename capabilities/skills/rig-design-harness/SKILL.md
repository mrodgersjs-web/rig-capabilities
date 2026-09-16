---
name: rig-design-harness
description: Route reusable design-harness work to the canonical rig-design-harness package without copying its runtime or virtual environment. Use for studio-to-PRD compilation, lane evaluation, independent verification, and evidence sealing.
outcome: "design-ux: approved design intent becomes a repeatable governed harness with replayable evidence"
source_root: /Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness
done_when:
  - "cmd:cd /Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness && bin/rdh doctor"
  - "cmd:cd /Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness && .venv/bin/pytest -q"
  - "cmd:cd /Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness && test -f harness/compiler.py"
  - "cmd:cd /Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness && grep -q mutation_ledger harness/outer_loop.py"
great_example: /Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/golden/linkedin/example-designs.json
quality_floor: 0.7
relates_to: rig-lattice-system, iqrsqpi-v20, systems-thinking-studio, rig-jtbd-packs
---

# RIG Design Harness

Canonical code lives at `source_root`; invoke its `bin/rdh` CLI in place.

Run intent → studios → PRD → compile → slice → bench → evolve → verify → seal. A RED studio, held-out regression, same-family verifier, or failed D85 command stops advancement.
