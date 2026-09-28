---
id: rig-hq-sub-j1-2-a-day-is-overloaded
version: 1
status: draft
tier: sub
department: Office of the CEO
agent: prime-jake-pai
parent: rig-hq-prompt-prime-jake-pai
task: Interrupt sub-prompt (J1): a day is overloaded — cut to 3 items and park the rest
triggers: day overloaded, too much work, collapsing, cut the day down
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J1 interrupt 2), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J1 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: a day is overloaded

**Trigger.** The day's open items exceed what can be finished (WIP cap breached, or
Mike says it is too much).

**Typed inputs.** `open_items` (from the queue file), `wip_cap` (default 3),
`priorities` (fitness > James > learning, then revenue-critical).

**Steps.**
1. Rank by the priority order and what unblocks the most work.
2. Keep the top 3; park everything else with a reason and a re-review date.
3. Tell Mike what was parked — parking is visible, never silent.

**Output format.**
```
STATUS: CUT TO 3
Keep: <3 items with owners>
Parked: <items + reason + re-review date>
Nothing dropped silently: confirmed
```

**Expected output.** A 3-item day and an honest parked list.

**Done test.** Open items needing Mike == 3; every parked item has a reason and date.

**Failure handling.** If even the top 3 exceed capacity, cut deeper and say so.

**Persistence.** Queue file updated; parked items keep their rows.

**Redaction.** n/a.

**Stop / escape hatch.** If two items are truly load-bearing for money, say so and
ask which to displace — never quietly drop one.
