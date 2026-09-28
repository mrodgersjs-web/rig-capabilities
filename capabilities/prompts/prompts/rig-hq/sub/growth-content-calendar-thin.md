---
id: rig-hq-sub-j6-2-the-calendar-runs-thin
version: 1
status: draft
tier: sub
department: Growth & Content
agent: ralph-linkedin
parent: rig-hq-prompt-steve-content
task: Interrupt sub-prompt (J6): the calendar runs thin — fill next week, schedule only after Mike's yes
triggers: calendar thin, queue running out, fill the content calendar
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J6 interrupt 2), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J6 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: the calendar runs thin

**Trigger.** The content queue has fewer drafts than the next week's cadence needs.

**Typed inputs.** `queue_file`, `slots_next_week`, `lanes_due`, `idea_bank`.

**Steps.**
1. Count the gap from the queue file (never from memory).
2. Pull ideas from the idea bank/trend notes; pick for lane fit first, quality bar
   second.
3. Draft to fill the gap; the Ship step schedules them only after Mike's yes.

**Output format.**
```
STATUS: FILLED <n>/<slots>
Gap: <counted from queue file>
Drafts: <paths, lane-tagged>
Schedule: HELD for yes — proposed slots <list>
```

**Expected output.** Next week covered with lane-clean drafts awaiting approval.

**Done test.** Draft count fills the counted gap; scheduling is held.

**Failure handling.** No fitting ideas -> report the gap honestly instead of padding
with off-lane content.

**Persistence.** Queue file updated with the drafts and proposed slots.

**Redaction.** n/a.

**Stop / escape hatch.** Filling with weak ideas is worse than a thin week — the bar
still applies.
