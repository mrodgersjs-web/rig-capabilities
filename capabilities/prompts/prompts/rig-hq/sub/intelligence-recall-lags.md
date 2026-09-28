---
id: rig-hq-sub-j4-2-recall-api-lags-the-app-853-vs-2
version: 1
status: draft
tier: sub
department: Intelligence
agent: iris-jr-os-intelligence
parent: rig-hq-prompt-iris-strategy
task: Interrupt sub-prompt (J4): recall API lags the app (853 vs 21,987) — flag the gap and route to the app export
triggers: recall lag, recall api gap, memory index stale
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J4 interrupt 2), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J4 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: recall API lags the app

**Trigger.** The recall API's visible count is materially smaller than the app's
(e.g. 853 vs 21,987).

**Typed inputs.** `api_count`, `app_count`, `query`, `export_path`.

**Steps.**
1. Flag the gap explicitly in the answer header: what the API could see vs what
   exists. A retrieval over 853 of 21,987 is a partial search, and is labeled one.
2. Route to the app export path for the missing span; note which surfaces were
   searched and which were not.
3. Retry the query against the wider source; report coverage numbers with the answer.

**Output format.**
```
STATUS: GAP FLAGGED — API <n> vs app <n>
Coverage: searched <surfaces> — <counts>
Answer: <path> (claims carry per-surface provenance)
Missing span: <what the API could not see>
```

**Expected output.** An honest partial-coverage answer, never a silent short search.

**Done test.** The header states both counts; every claim names its surface.

**Failure handling.** If the export is unavailable -> report the retrieval as
unavailable/pending refresh and retry next turn; never claim memory was loaded.

**Persistence.** Gap record saved for the next recall run.

**Redaction.** No secrets in exports.

**Stop / escape hatch.** Silence about the gap is the failure mode this interrupt
exists to prevent.
