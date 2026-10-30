---
outcome: "Every weekday morning, assemble yesterday's scorecard for Mike: lane metrics for LinkedIn, the GTM funnel, and site health, each measured against its target, with misses flagged and one recommended focus for the day. Read-only: it reports, it never posts, sends, or changes anything."
done_when:
  - file:out/daily-scorecard-loop/aside/routine.json
  - file:out/daily-scorecard-loop/grokbot/lanes.fragment.yaml
  - file:out/daily-scorecard-loop/jake/loop-card.md
  - cmd:python3 compiler/compile_workflow.py registry/daily-scorecard-loop.yaml --check
  - grep:out/daily-scorecard-loop/aside/routine.json:Every
  - grep:out/daily-scorecard-loop/aside/routine.json:Every
state: DORMANT
gate_d_required: true
cadence: "3 7 * * 1,2,3,4,5"
quality_floor: 0.7
---

# Daily Scorecard Loop — loop card (DRAFT, workflow-design-studio)

**Cadence:** `3 7 * * 1,2,3,4,5` (America/Denver) — compiled from `registry/daily-scorecard-loop.yaml`.
**Mode:** DRAFT. Staging this card into `capabilities/loops/` or registering the recurring job is a Gate-D action.

## Body (shared with the routine prompt — single source, compiled)

# Daily Scorecard Loop

Intent: Every weekday morning, assemble yesterday's scorecard for Mike: lane metrics for LinkedIn, the GTM funnel, and site health, each measured against its target, with misses flagged and one recommended focus for the day. Read-only: it reports, it never posts, sends, or changes anything.

Steps:
1. Pull yesterday's lane metrics from the read-only sources on disk (LinkedIn lane logs, GTM funnel records, site health checks).
2. Compare each metric to its recorded target; compute the delta, do not restate the raw number without the target.
3. Flag every miss with the largest miss first; a miss with no recorded target is listed as UNTARGETED, not guessed.
4. Pick one recommended focus for the day from the top miss, with the reason in one sentence.
5. Write the scorecard to the outputs path and stop. Nothing is sent anywhere.

Stop and report when:
- Every metric row shows value, target, and delta, or names the missing input.
- Every miss is flagged with its size; untargeted metrics are labeled UNTARGETED.
- The scorecard file exists at the outputs path and contains exactly one recommended focus.
- No outbound action was taken; the run log shows read-only tool use.

Produce:
- scorecard markdown at ~/.rig/live/prime-aside-driver/jake/conductor/workflow-design-studio/runs/scorecard-<date>.md
- run log line with per-metric sources and any missing inputs

Boundary: read-only run. Nothing outward. Any outward action waits for a human Gate-D approval.


## Termination

A run that cannot produce every `outputs` item names the missing item and FAILs. No prose-only completions. Nothing outward without a human Gate-D approval id.
