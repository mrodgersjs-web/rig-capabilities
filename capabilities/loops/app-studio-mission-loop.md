---
outcome: "code-engineering: the outer App Studio loop carries one app mission from request to closed record - gated spec, gated stack, clean preflight, slice loops, judged screens, independent verification, Gate-D hold, lessons promoted - and terminates on done, HELD, or a named halt"
done_when:
  - file:capabilities/loops/app-studio-mission-loop.md
  - cmd:python3 scripts/assert_loop_termination.py capabilities/loops/app-studio-mission-loop.md
  - cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py
quality_floor: 0.7
---

# App Studio Mission Loop - META loop

Owner: `app-studio-conductor`. Harness: `capabilities/harnesses/app-studio-session.yaml`.
Skill: `app-studio`. Sub-loops: `app-slice-loop`, `app-ui-judge-loop`,
`app-lesson-promotion-loop`. Main loops reused: `iqrsqpi-v20` (outer build doctrine),
`phase-discipline-loop`, `proof-loop`, `adversarial-verification-loop`, `gate-d-loop`,
`git-push-safety-loop`, `capabilities/loops/coding-harness.md`.

JEV first: every stage transition is a typed judgment routed to `rig-s1gate check
app.stage-gate` BEFORE any frontier review. Classifier down: DEFER the transition;
the loop waits, it never guesses.

## Loop

```
INTAKE -> SPEC GATE -> STACK GATE -> PREFLIGHT
  -> for each stage 3..9: run app-slice-loop per slice -> STAGE GATE (app.stage-gate)
  -> UI JUDGE (app-ui-judge-loop) -> INDEPENDENT VERIFY
  -> SHIP RECORD (app.ship) -> GATE-D HOLD
  -> CLOSE (app-lesson-promotion-loop) -> DONE | HELD
```

Kill switch: three consecutive halts at the same gate, or any outward action attempted
without an approval id, ends the loop with `status: HALTED` and the gate named.

## Gates

| Gate | Stage | Pass Condition | On fail |
|---|---|---|---|
| G1 | intake-spec | spec rows sourced; app.spec and plan.readiness required signals above 0.9 | rewrite spec, max 3, then ESCALATE |
| G2 | architecture-stack | stack.md cleared app.stack; build-location matrix applied | rewrite stack, max 3, then ESCALATE |
| G3 | scaffold-setup | app-sandbox-preflight has no FAIL | fix toolchain, re-run preflight |
| G4 | each build stage | every slice closed by app-slice-loop with an executed check | slice loop retries, max 3 per slice |
| G5 | each transition | app.stage-gate receipt, required signals above 0.9 | hold transition, fix, re-score; DEFER if classifier down |
| G6 | design-ux | every spec screen judged on the real app, none DEFERRED-as-pass | app-ui-judge-loop |
| G7 | verify-qa | independent verifier re-ran acceptance; planted failure RED then GREEN | fix and re-verify |
| G8 | ship-release | app.ship cleared and the action held at Gate-D | complete the record; wait for Mike |
| G9 | operate-learn | run.jsonl validates; lessons promoted; watchers deleted; ProofPacket sealed | app-lesson-promotion-loop |

**On-fail:** G1, G2, G3, G4, G5, G7 are halt-tier: HALT the mission at that stage and name the failing check.
**On-fail:** G8 is stop-tier: HALT outward work until Mike's approval id exists; the mission may close HELD.
**On-fail:** a third consecutive failure at any gate: HALT and ESCALATE to Mike with the evidence.

## Definition of Done

A mission is done when:
1. every spec row appears in the comparison table as built with a proof line, or as a named stub or gap;
2. every stage transition has an app.stage-gate receipt or an explicit DEFER record;
3. `validate_lessons.py` exits 0 on the mission's run.jsonl;
4. anything public is either approved with an id or recorded in `held_at_gate`;
5. a ProofPacket is sealed and the mission's watcher routines are deleted.
