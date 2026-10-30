---
outcome: "learn: the Sunday funnel review maps the week's observed outcomes to the JOB-SYSTEM-v2 lanes and KPIs, promotes typed lessons to the ledger and their sub-skills, and never invents an outcome metric"
done_when:
  - file:capabilities/loops/traject-weekly-learn-loop.md
  - cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/traject-os/references/lessons.jsonl
quality_floor: 0.7
---

# Traject Weekly Learn Loop - SUB loop

Parent: `traject-daily-loop`. Owner: `traject-conductor`. Harness:
`capabilities/harnesses/traject-proof-publish-session.yaml`. Sub-skill: `traject-learn`.
Main loop reused: `capabilities/loops/rig-realign-weekly.md`.

JEV first: the close verdict routes to `rig-s1gate check mission.completion` and each lesson to
`atomic.claim` BEFORE any frontier review. Classifier down: DEFER.

## Loop (Sunday)

```
FUNNEL REVIEW (JOB-SYSTEM-v2 lanes) -> KPI read (observed only) -> LESSON promotion (ledger + sub-skill)
  -> CLAIMS sweep (fix every surface) -> NEXT-WEEK priorities -> CLOSE
```

## Lanes and KPIs (JOB-SYSTEM-v2)

- **A Apply** — K3 100 receipt-backed/wk (reported below target; never inflate).
- **B Direct** — K1 3+ conversations/wk, K4 50 warm touches/wk.
- **C Convert** — K2 advance 30%, K5 human asks <24h.
- **E Market** — profile SEO, proof links. **D Learn** — this review.
- **North star K0** — signed offer ≥$180K base (target $250K). Never report a KPI that was not
  observed; a dashboard number that only informs is not an action.

## Gates

| Gate | Pass Condition | On fail |
|---|---|---|
| G1 | outcomes reported as observed (receipts/ledger), not invented | re-read the source of truth |
| G2 | every new failure is a typed lesson (trigger, mandated check, evidence) filed to the ledger AND its owning sub-skill patched | complete the lesson |
| G3 | validate_lessons.py exits 0 | fix the run.jsonl receipts |
| G4 | claims sweep: any corrected number fixed on every surface | sweep again |

**On-fail:** G1, G2, G3 halt-tier; G4 degrade-tier.

## Definition of Done

The week is done when the funnel maps to the lanes with observed numbers, lessons reached the
ledger and their sub-skills, the claims sweep is clean, and next-week priorities are set.
