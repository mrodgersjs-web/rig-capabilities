# Traject OS JEV decision map

Every typed decision a job-search task forces, routed first match wins:
CODE (a deterministic rule decides) -> JEV (bounded state, fixed answer set, answer consumed
by code) -> SYSTEM 2 (generation, long-horizon) -> HUMAN (Gate-D: outward, paid, destructive,
anything about a minor).
Command shape: `rig-s1gate check <rubric> --file <artifact> --subject "<kind>:<company>-<role> sha=<sha12>" --json`.
Bar (work-criteria.json): required signals and score or choice confidence must be above 0.9;
0.90 does not pass. Every rubric here is ADVISORY AND UNCALIBRATED where work-criteria.json says
so: a tripped rule is a held stage to rewrite until clean, never decoration. Classifier
unavailable: DEFER, never guess. **An advisory PASS is never permission to submit, send, or
publish** — those are HUMAN, under the first-five human-click pilot
(`~/.aside/u/0/projects/rig-job/OPERATING-PLAN.md`).

## Tiers

| Tier | Rubric | Kinds (work-criteria.json) | Decides |
|---|---|---|---|
| META | `job.fit` | job.fit | does this role fit Mike's band and shape at all |
| MAIN | `resume.ats` | resume.ats | does the tailored résumé survive the parser |
| MAIN | `resume.recruiter` | resume.recruiter | does it survive a recruiter first pass |
| MAIN | `resume.screen` | resume.screen | does it survive the screening stack |
| MAIN | `jobhunt.select` | jobhunt.select | is this one of the roles worth an application slot |
| MAIN | `jobhunt.resume` | jobhunt.resume | is the résumé variant right for this hunt lane |
| MAIN | `job.navigate` | job.navigate | is the ATS path the right one and readable |
| MAIN | `interview.answer` | interview.answer | is this answer a pass (number or NONE) |
| MAIN | `outreach.first` | outreach.first | is this first-touch note ready |
| MAIN | `email.outreach` | email.outreach | is this email outreach ready |
| MAIN | `offer.eval` | offer.eval | is this offer/package evaluated honestly |
| MAIN | `story.bank` | story.bank | is the story bank résumé-verified and usable |
| MAIN | `company.fit` | company.fit | does this company match the target profile |
| MAIN | `contact.pick` | contact.pick | is this the right person to contact |
| MAIN | `jd.decode` | jd.decode | is the requirement map faithful to the JD |
| MAIN | `hm.technical` | hm.technical | does the technical answer hold up to the hiring manager |
| MAIN | `screen.pitch` | screen.pitch | does the screen pitch land |
| MAIN | `mission.completion` | mission.completion | did this run actually complete |
| MAIN | `atomic.claim` | atomic.claim | is this claim atomic and evidenced |
| SUB | `job.formfill` | job.formfill | is this filled form faithful to confirmed facts |
| SUB | `form.field` | form.field | is this single field answer confirmed, not invented |
| SUB | `outreach.intro` | outreach.intro | is this intro note ready |
| SUB | `reply.intent` | reply.intent | what does this reply actually want |
| SUB | `jobhunt.warm` | jobhunt.warm | is this warm touch eligible and well-targeted |
| SUB | `followup.note` | followup.note | is this thank-you/nudge ready |
| SUB | `rejection.cause` | rejection.cause | what actually caused this outcome |
| SUB | `training.readiness` | training.readiness | is Mike ready for the real screen |

## Decisions

| Decision | Route | Rubric or rule | Pass | On ESCALATE or BLOCK | On DEFER |
|---|---|---|---|---|---|
| Is this role in band and in shape | JEV | `job.fit` + `jobhunt.select` | both clean, required signals > 0.9 | named reject with a reason | the role is not qualified |
| Is the pay/location decision admissible | CODE | packet_lint A7/A12 with the current $180K base floor and the approved location set; unknown pay with the recorded token MIKE-2026-09-27-GRILL-Q3 | CLEAR | BLOCK: park the role | not applicable |
| Is the target a duplicate | CODE | employer+role+req against `~/.applypilot/applications.sqlite3` and Gmail receipts, deduped by message id | clean | drop as dupe with the receipt id | not applicable |
| Is the tailored résumé admissible | JEV | `resume.ats`, `resume.recruiter`, `resume.screen`, `jobhunt.resume` | all clean, required signals > 0.9 | rewrite, max 3, then escalate to Mike | no upload, no form fill |
| Is this field answer confirmed | JEV | `job.formfill`, `form.field` | clean | leave the field for Mike; never invent | the field is left blank for Mike |
| Is this outreach draft ready | JEV | `outreach.first`, `outreach.intro`, `reply.intent`, `email.outreach`, `jobhunt.warm`, `followup.note` | clean after outreach_lint CLEAR | rewrite only | the draft is held, never sent |
| Is the room's story bank usable | JEV | `story.bank`, `jd.decode`, `company.fit`, `contact.pick` | clean, résumé-verified only | rebuild; never pad with an OWNER-ONLY or BANNED claim | the room is incomplete, named |
| Is this answer a pass | JEV | `interview.answer`, `hm.technical`, `screen.pitch`, `training.readiness` | clean and the answer states a number or NONE | re-drill the card | DEFERRED is never a pass |
| What caused this outcome | JEV | `rejection.cause`, `offer.eval` | clean | re-read the evidence | the cause is recorded unknown |
| Is this claim admissible | CODE then JEV | claims-ledger status (VERIFIED-BY-ARTIFACT / OWNER-ONLY / BANNED-UNSUPPORTED), then `atomic.claim` | VERIFIED-BY-ARTIFACT and clean | classify, never soften | the claim stays out |
| Did the run complete | JEV | `mission.completion` | clean on the close record | reopen the failing stage | the close waits |
| **Submit, send, publish, deploy** | **HUMAN** | Gate-D + the first-five human-click pilot | **Mike's own click** | **stays HELD** | **stays HELD** |

## Non-decisions (CODE, no classifier)

- The 5-line debrief shape (question asked / actual answer / ownership gap sentence / number
  stated or NONE / next question) is deterministic; the shape is checked, the content is judged.
- The dedupe receipt count, the resume sha256, the band arithmetic, and the outbound caps
  (≤10 DMs/day, ≤10 invites/day & 60/week, 3-10 min spacing) are arithmetic.
- The HARD STOP at final Submit is a stop, not a judgment.

## Measured discrimination

Not yet measured. Traject reuses the existing jobhunt.*/job.*/resume.*/interview.* rubric packs
in `capabilities/harnesses/s1gate/rubrics/`; the jobhunt.* packs are recorded `calibrated: false`
in `~/.rig/jake/jobs/JOB-SYSTEM-v2.md`, so every verdict above is ADVISORY and a held stage,
never a permission. Calibration is a named open item, not an assumption.
