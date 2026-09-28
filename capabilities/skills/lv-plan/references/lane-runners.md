# Lane runners: who executes a plan and how they call this stage

Sub-skill of lv-plan. Runners execute briefs; this stage owns the slate, the evidence labels and the
funnel mix. A runner that invents a slot, a number or an approval is a defect, not a shortcut.

## The contract every runner follows

1. Read the slate from the board Mike already uses (or the brief handed over), never from memory.
2. Take pillar, job, format, funnel stage and evidence label per slot as given. Change nothing.
3. Draft or queue only inside the lane's own voice register and approval state.
4. Hold every outward step at its approval gate. Drafts are free; publishing, sending and boosting
   are Mike's call (and on the client lane, Mike's explicit client approval).
5. Report back what actually shipped, what was held and why. Never report a queued item as published.

## Runner table

| runner | lane | what it does | how it calls this stage |
|---|---|---|---|
| linkedin-weekly-rhythm | A | Mike's themed daily post system (Ted Lasso Monday through Saturday themes, Birch Tuesday-only, The Coach from behind or in silhouette), Eden brief plus image render | asks lv-plan for the week's slate and evidence labels, then maps each theme day onto a slot; keeps its rhythm only while it beats baseline |
| rig-daily-linkedin-post | B | daily RIG B2B post: draft, scheduling, queue, reporting | asks lv-plan for slots, jobs and funnel stages; folds to the three-post barbell when the week needs cutting |
| ideawake-linkedin-weekly | client | Coby's weekly engine: publish-and-amplify Mon/Wed/Fri, engagement-only Tue/Thu, plus a new-channel sweep | asks lv-plan for the Mon/Wed/Fri slate in Coby's voice; nothing fires without Mike's explicit client approval, and the browser handle is asserted first |
| alfred-content-planning-cron | Alfred pipeline | builds tomorrow.json when the planning cron fires | asks lv-plan for tomorrow's slot brief before filling tomorrow.json; never fills it from a blank topic |
| alfred-trend-pipeline | Alfred pipeline | daily competitor and industry trend scan (multi-provider fetch with fallback) into a JSON report | feeds lv-plan's trend leg; the report is input to the matrix and the slate, never a slate by itself |
| linkedin-content-planning | Alfred pipeline | the content-planner cron skill | asks lv-plan for the week's slate and writes the planner output from it |
| alfred-linkedin-cron | Alfred pipeline (Prime Agent) | automated daily content drafting and scheduling on cron with an RLM harness | asks lv-plan for the idea and slot brief; drafts held at the approval gate, no unattended publishing |
| prime-alfred | Alfred pipeline (OMP) | OMP agent config driving the Alfred content pipeline | loaded with the Alfred skills; delegates slate questions to lv-plan |
| li-content-cycle | rig-linkedin-virality P1 | the daily cycle from trend ingest through held-approval publish (06:45 MT wake) | asks lv-plan for the idea and slot brief after trend ingest, before drafting; publish stays held for approval |
| li-content-cycler | rig-linkedin-virality P1 | agent config for that daily cycle | loaded with li-content-cycle; same call pattern |

## Runner-specific hard lines

- The client lane asserts the signed-in handle before any action and halts on mismatch; it never
  borrows Mike's voice or RIG's mascots.
- Alfred crons produce artifacts (tomorrow.json, trend JSON, drafts). An artifact is not a publish.
- The P1 cycle's publish step is held at approval even though the cycle runs unattended.
- Any runner whose metric feed returns unparseable state writes what is known, marks the rest null
  and stops; a fail-loud BLOCKED line beats a silent empty run.
- Before producing any artifact, a runner reads the guards of every consumer that reads it.

## Checks before a runner is briefed

- The slate exists on the board with per-slot pillar, job, format, funnel stage and evidence labels.
- The lane's voice register and approval state are stated in the brief.
- The runner's caps (comments, follows, sweeps) are restated in the brief, not assumed.
- The report-back format names shipped versus held.

Absorbed from: linkedin-weekly-rhythm, rig-daily-linkedin-post, ideawake-linkedin-weekly, alfred-content-planning-cron, alfred-trend-pipeline, linkedin-content-planning, alfred-linkedin-cron, prime-alfred, li-content-cycle, li-content-cycler.
