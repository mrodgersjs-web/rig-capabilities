# App Studio JEV decision map

Every typed decision an app mission forces, routed first match wins:
CODE (a deterministic rule decides) -> JEV (bounded state, fixed answer set, answer consumed
by code) -> SYSTEM 2 (generation, long-horizon) -> HUMAN (Gate-D: outward, paid, destructive).
Command shape: `rig-s1gate check <rubric> --file <artifact> --subject "<kind>:<mission> sha=<sha12>" --json`.
Bar (work-criteria.json): required signals and score or choice confidence must be above 0.9;
0.90 does not pass. All `app.*` rubrics are ADVISORY AND UNCALIBRATED: a tripped rule is
downgraded BLOCK -> ESCALATE, and App Studio treats that ESCALATE as a held transition to
rewrite until clean, never as decoration. Classifier unavailable: DEFER, never guess.

## Tiers

| Tier | Rubric | Kinds (work-criteria.json) | Decides |
|---|---|---|---|
| META | `app.stage-gate` | app.stage-gate, app, app-studio, app-stage, web-app, mobile-app | may this stage close and the next one start |
| SUB | `app.spec` | app.spec, app-spec | is the spec buildable (sourced rows, executable acceptance) |
| SUB | `app.stack` | app.stack, app-stack | does the stack fit the lane and build where it will run |
| SUB | `app.ship` | app.ship, app-ship, app-release | is the Gate-D release request complete |
| SUB | `app.inventory-fit` | app.inventory-fit, app-inventory | does an estate asset belong to App Studio, and at which stage |
| MAIN | `plan.readiness`, `code.diff`, `code.review`, `api.backend`, `ui.design`, `website.buyer`, `mission.completion`, `atomic.claim`, `doctrine.surface` | existing kinds | reused estate criteria per stage |

## Decisions

| Decision | Route | Rubric or rule | Pass | On ESCALATE or BLOCK | On DEFER |
|---|---|---|---|---|---|
| Does an asset belong in the family | CODE then JEV | keyword prefilter, then `app.inventory-fit` | primary_app_building > 0.9 and infra < 0.7 | review bucket, named | row marked deferred |
| Spec ready to build | JEV | `app.spec` + `plan.readiness` | both clean, required signals > 0.9 | rewrite spec, max 3, then Mike | no scaffold |
| Stack sound | JEV | `app.stack` | clean | rewrite stack record | no scaffold |
| Toolchain can build here | CODE | app-sandbox-preflight table, native-binary hook | no FAIL | fix toolchain | not applicable |
| Slice done | CODE then JEV | executed check exit code, then `app.stage-gate` | check green and gate clean | slice loop retry, max 3 | slice stays open |
| Stage transition | JEV | `app.stage-gate` + the stage's rubric | clean, required signals > 0.9 | hold, fix, re-score | transition waits |
| Screen acceptable | JEV (vision) | `advisor-plus judge-image` + `ui.design` | judge clean and ui.design clean | ui judge loop, max 3 | DEFERRED row, never a pass |
| Tests trustworthy | CODE | assertion-verb count, planted failure RED then GREEN | assertions present, plant caught | fix the test | not applicable |
| Release request complete | JEV | `app.ship` | clean | complete the record | no Gate-D request |
| Ship, push, domain, submit | HUMAN | Gate-D, Mike's typed approval | approval id | stays HELD | stays HELD |
| New lesson well-formed | CODE then JEV | `validate_lessons.py`, then `atomic.claim` | exit 0 and atomic | split or complete the lesson | not filed |
| Mission done | JEV | `mission.completion` on the close record | clean | reopen the failing stage | close waits |

## Measured discrimination (2026-09-27, fixtures in capabilities/harnesses/s1gate/fixtures/)

| Rubric | Good fixture | Bad fixture |
|---|---|---|
| app.stage-gate | PASS (evidence 0.95, scaffolding 0.13) | ESCALATE (evidence 0.03, outward without approval 0.73) |
| app.spec | PASS (acceptance 0.95, invented 0.23) | ESCALATE (invented 0.91, sourced 0.05) |
| app.stack | PASS (lane 0.96, local-first 0.97) | ESCALATE (paid without fallback 0.91, lane 0.14) |
| app.ship | PASS (build proof 0.97, Gate-D 0.96) | ESCALATE (build proof 0.07, Gate-D 0.08) |
| app.inventory-fit | fullstack-developer 0.97 | linkedin-viral 0.02 |

Calibration path: label the 335 skill and 186 agent review rows in `inventory.json` with
`rig-s1gate label <decision_id> good|bad`, then `rig-s1gate calibrate app.inventory-fit`.
