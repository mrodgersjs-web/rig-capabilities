# Aside chat brief — Daily Scorecard Loop (DRAFT, never opened by this studio)

Title: Daily Scorecard Loop
Mode: read-only brief; no outward sends. Opening this chat is a human step.

Brief (paste to aside_chat_new):

Every weekday morning, assemble yesterday's scorecard for Mike: lane metrics for LinkedIn, the GTM funnel, and site health, each measured against its target, with misses flagged and one recommended focus for the day. Read-only: it reports, it never posts, sends, or changes anything.
Run every weekly at 07:03 America/Denver.
Steps: Pull yesterday's lane metrics from the read-only sources on disk (LinkedIn lane logs, GTM funnel records, site health checks). | Compare each metric to its recorded target; compute the delta, do not restate the raw number without the target. | Flag every miss with the largest miss first; a miss with no recorded target is listed as UNTARGETED, not guessed. | Pick one recommended focus for the day from the top miss, with the reason in one sentence. | Write the scorecard to the outputs path and stop. Nothing is sent anywhere.
Report: scorecard markdown at ~/.rig/live/prime-aside-driver/jake/conductor/workflow-design-studio/runs/scorecard-<date>.md | run log line with per-metric sources and any missing inputs
Nothing outward without Mike's typed Gate-D approval.
