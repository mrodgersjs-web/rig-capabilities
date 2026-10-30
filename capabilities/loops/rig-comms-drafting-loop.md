---
outcome: communications: every message closes its loop — predicted before delivered, scored against outcome, failures become golden-suite fixtures, winners become skills after 3 wins
done_when:
  - file:capabilities/loops/rig-comms-drafting-loop.md
  - cmd:python3 -c "import sys; sys.path.insert(0,'capabilities/skills/rig-communications-core'); from rig_comms import golden, outcomes, lineage; s=golden.run_suite(); assert s['green'] and s['total']==20; print('OK')"
  - grep:capabilities/loops/rig-comms-drafting-loop.md:R2 golden-set ratchet
  - grep:capabilities/loops/rig-comms-drafting-loop.md:R3 self-breeding
quality_floor: 0.6
---

# Communications drafting loop (Build Card execution workflow, as a loop card)

## Stages (one typed, hash-chained lineage event per pass)

```
INTAKE    comms.intent_check            fails → return named missing field, no drafting
RESEARCH  comms.audience + comms.claims privacy/relevance gate here
ARCHITECT comms.vehicle                 no-send advisory is a valid terminal outcome
GENERATE  prompt:draft → prompt:voice
EVALUATE  prompts sim-*, critic-*, redteam → scores into comms.energy
REVISE    typed defects only; ≥3 cycles for consequential; max-3 latch → escalate
VERIFY    comms.verdict role="verifier" (GEV_LOCK blocks everyone else)
APPROVE   human token when policy requires (external send ALWAYS)
DELIVER   channel adapter; predicted_p recorded BEFORE delivery
LEARN     comms.outcome record → Brier by archetype
```

## The three loops that compound

- **R2 golden-set ratchet** — every shipped failure becomes a permanent must-fail
  case in `rig_comms/golden.py`. The suite is the ratchet: it only ever gets harder.
- **R3 self-breeding** — `comms.outcome promote` surfaces patterns with ≥3 wins;
  minting requires pattern extraction → golden replay → tail-risk test → independent
  meta-eval → version+owner. Machine proposes, verifier/human mints.
- **B1 calibration** — `comms.outcome brier` per archetype; recalibrate weights when
  mean_pred drifts >0.15 from base_rate at n≥30; below n=30 exact Brier only, no sigma.

## Balancing loops (what stops the loop from lying to itself)

B1 GEV separation (B from R: drafter ≠ certifier) · B2 hard floors override energy ·
B3 PRIVACY_LOCK · B4 max-3 revision latch · B5 lineage `verify_chain` catches hidden retries.

## Corpus grounding (how-to manifest — where the loop's patterns were measured)

- `ImPESBftwr8` (David Ondrej, agent-craft, 19k words): INTAKE→ARCHITECT discipline — no draft before
  the vehicle is chosen.
- `j8yGn1v8OgU` (The Futur, comms-craft, 29k words): REVISE cadence — typed objections, not vibes.
- `H2IFv_GBdUQ` (Thomas Frank, comms-craft, 21k words): DELIVER+LEARN — publish, measure, iterate;
  the R2 ratchet in human form.
