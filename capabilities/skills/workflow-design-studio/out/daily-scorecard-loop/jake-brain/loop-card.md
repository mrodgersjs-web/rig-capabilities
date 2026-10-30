---
outcome: "Every weekday morning, assemble yesterday's scorecard for Mike: lane metrics for LinkedIn, the GTM funnel, and site health, each measured against its target, with misses flagged and one recommended focus for the day. Read-only: it reports, it never posts, sends, or changes anything."
done_when:
  - file:registry/daily-scorecard-loop.yaml
  - cmd:python3 compiler/compile_workflow.py registry/daily-scorecard-loop.yaml --check
state: DORMANT
gate_d_required: true
cadence: "3 7 * * 1,2,3,4,5"
quality_floor: 0.7
---

# Daily Scorecard Loop — jake-brain loop card (DRAFT)

**Cadence:** `3 7 * * 1,2,3,4,5` (America/Denver). Compiled, not hand-written.
**Placement:** by the worker who owns `app/jake_brain/**` (see COORD.md). This studio writes
nothing into app/jake_brain/** or app/jake_brain_nightly/**.

## Body (shared compiled source)

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

