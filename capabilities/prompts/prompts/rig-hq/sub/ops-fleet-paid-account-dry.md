---
id: rig-hq-sub-j11-2-a-paid-account-runs-dry
version: 1
status: draft
tier: sub
department: Ops, Fleet & Security
agent: eleanor-finance
parent: rig-hq-prompt-otto-operations
task: Interrupt sub-prompt (J11): a paid account runs dry — catch it with a one-token probe and stop the spend
triggers: paid account dry, credits exhausted, quota out
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J11 interrupt 2), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J11 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: a paid account runs dry

**Trigger.** A paid provider account nears or hits its credit/quota limit.

**Typed inputs.** `account` (item name, never values), `spent`, `limit`,
`probe_result`.

**Steps.**
1. Catch it with a one-token probe — the probe's real response is the evidence, not
   the billing page's last cached number.
2. Pause spend on that account immediately; reroute to the next probed lane or stop.
3. Report: what is left, what is running where now, and the ask (top up / switch
   plan / stop) held for Mike.

**Output format.**
```
STATUS: SPEND PAUSED <account>
Probe: <result + ts> — remaining <n/limit>
Rerouted: <runs -> lane | stopped>
Ask: top up <n> | switch plan | stop — HELD for Gate-D
```

**Expected output.** No silent spend failure; a decidable money question.

**Done test.** The account is provably not spending; the ask carries exact values.

**Failure handling.** Probe inconclusive -> treat as dry until proven otherwise (fail
closed).

**Persistence.** Finance report row updated with the receipt path.

**Redaction.** Account item names only — never keys or card values.

**Stop / escape hatch.** Topping up is a money action: Mike only.
