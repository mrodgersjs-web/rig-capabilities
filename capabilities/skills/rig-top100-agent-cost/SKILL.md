---
name: rig-top100-agent-cost
description: "Track what the fleet actually spends: per-call token and dollar accounting attributed to agent, task, and harness, per-agent budgets with real alerts, model routing that trades cost against measured quality, and cost per accepted outcome rather than per call. Use when a bill moves without a decision, when a routine looks productive but expensive, or before a model upgrade is justified on price."
tags: [rig, top100, agentic-systems, finops, cost, budgeting, model-routing]
metadata:
  tier: canonical
  domain: Agentic Systems
  rank: 13
  status: built-out-2026-10-25
  source_stub: ~/.grok/skills/rig-top100-agent-cost/SKILL.md
outcome: "Every model and API call has a dated cost row tagged to an agent and a task; budgets alert before breach; and a cost-per-accepted-outcome number is reported next to volume, so spend is judged on results."
activation: "Load when adding a routine that runs unattended, when a monthly bill moves, before routing more work to an expensive model, and whenever an agent is described as productive without a cost line."
instruction: "Record cost at the call, in the same place as the trace, with input and output tokens, model, harness, task id, and the provider price in effect that day. Aggregate daily per agent and per task. Hold each agent to a budget that stops work rather than throttling it silently, and alert at 70 and 90 percent. Route to cheaper models by measured eval score, not by feel, and always report cost per accepted outcome: a cheap run that needs a redo is expensive."
applies_when:
  env: "local accounting file or table plus provider invoices as the external check"
  runtime: "the model client wrapper, hooks around API calls, a daily rollup job"
  deps: "a price table with effective dates, the eval runner (for quality-adjusted cost), the alert channel"
  params: "price table, per-agent budgets, alert thresholds, routing ladder"
  budget: "accounting overhead invisible at the call; rollups daily"
  scale: "one agent to a fleet; per-principal budgets, per-task attribution"
permissions:
  - fs.write
  - bash
  - net.api-calls
flow:
  - Instrument the client wrapper so no call can be made without writing a cost row.
  - Tag every row with agent, harness, task id, model, in and out tokens, and the price version used.
  - Roll up daily per agent, per task, and per harness; keep the raw rows for at least one cycle.
  - Set a per-agent budget that halts work on breach, with alerts at 70 and 90 percent.
  - Compute cost per accepted outcome, not per call, so retries and redos are counted against the run that caused them.
  - Build a routing ladder from eval scores: cheapest model that clears the gate for that task class.
  - Reconcile against the provider invoice monthly; an unexplained delta is a leak.
  - Report the trend with volume alongside it, so growth and waste are distinguishable.
done_when:
  - "cmd:jq -e 'has(\"in_tokens\") and has(\"out_tokens\") and has(\"usd\") and has(\"agent\")' ${RUN_DIR:-./out/rig-top100-agent-cost}/calls.jsonl"
  - "cmd:jq -e '.budget_usd > 0 and .halt_on_breach == true' ${RUN_DIR:-./out/rig-top100-agent-cost}/policy.json"
  - "cmd:jq -e '.cost_per_accepted_outcome != null' ${RUN_DIR:-./out/rig-top100-agent-cost}/rollup.json"
  - "grep:SKILL.md:routing ladder"
out_of_scope:
  - cost per call as a headline metric while redos go uncounted
  - routing to a cheap model without an eval score behind the choice
  - silent throttling that looks like a stall rather than a budget
  - trusting an internal estimate without reconciling against the invoice
---

# Agent Cost Tracking and Budgeting

## Why this exists

Thousands of small LLM calls look free individually and arrive as a real line item. Worse than
the total is the attribution problem: without per-task rows, a spend spike gets blamed on the
new feature instead of the routine that retries on every poll. Cost becomes manageable the
moment it is measured at the call and judged per accepted outcome.

## Outcome contract

- Why: RIG runs 1000s of LLM calls daily and costs compound
- Baseline: No cost tracking
- Target: Real-time cost dashboard with per-agent budgets, model routing, and alerts

## Method

### 1. Measure at the call, in the trace

One row per call: timestamp, agent, harness, task id, model, in and out tokens, cached tokens,
usd, and the price-table version used. Writing it inside the client wrapper means an agent
literally cannot spend without being counted, and the row sits next to the trace id for that
call.

### 2. Prices need effective dates

Provider prices change and cached input is priced differently. Store prices with effective
dates and record which version a row used, so a historical rollup does not silently reprice
itself when the table is updated.

### 3. Budgets that halt, alerts that arrive early

Per principal: a per-run cap and a monthly budget. Alert at 70 and 90 percent; halt on breach
rather than throttling quietly, because a stalled routine is visible and a slowed one is a
mystery. The halt must name the budget, the spend, and the top three cost lines that got there.

### 4. Cost per accepted outcome

Divide by outcomes that passed eval and were actually used, not by calls. This single change
exposes the expensive patterns: poll loops that re-summarize unchanged content, retries on
permanent errors, and a huge model used for a formatting job.

### 5. Routing by measured quality

Rank tasks by the eval score needed, then route to the cheapest model that clears the gate.
Keep a floor for outward-facing text and for judgment calls, and route up when a fast model's
output fails the gate. A routing ladder is a decision table, not vibes; publish it.

## Failure modes

- Estimates reconciling to nothing: the invoice says one thing, the dashboard another.
- Cached tokens priced as fresh, overstating savings from a change that just added cache.
- Budgets on the wrong principal, so one runaway subagent can spend the whole month.
- Cost per call as a trophy metric while redo work goes uncounted.
- Routing down to save money and reading the quality drop as "the model got worse".

## Done-test (executable)

```bash
RUN_DIR=${RUN_DIR:-./out/rig-top100-agent-cost}
r=0
jq -es -e 'all(.[]; .usd != null and .agent != null and .task_id != null)' "$RUN_DIR/calls.jsonl" >/dev/null || { echo "BLOCK unattributed cost rows"; r=1; }
jq -e '.budget_usd > 0 and .halt_on_breach' "$RUN_DIR/policy.json" >/dev/null || { echo "BLOCK no halting budget"; r=1; }
jq -e '.cost_per_accepted_outcome != null' "$RUN_DIR/rollup.json" >/dev/null || { echo "BLOCK no outcome-adjusted cost"; r=1; }
jq -es -e '[.[] | select(.cache_read_tokens > 0)] | length >= 0' "$RUN_DIR/calls.jsonl" >/dev/null
diff <(jq -s '[.[].usd] | add' "$RUN_DIR/calls.jsonl") <(jq '.invoice_usd' "$RUN_DIR/reconcile.json") >/dev/null || echo "WARN dashboard and invoice differ"
[ "$r" -eq 0 ] && echo "PASS" || echo "BLOCK"
```

## Verification

Add up the raw rows and compare against the provider invoice for the same window: a delta over
a few percent is an unpriced call path, usually a subagent using a different key. Then check
the top five cost lines and confirm each is a task someone would defend. Finally trigger a
budget breach in a test lane and confirm the halt message names the lines that caused it.

## Related

`rig-top100-finops` (the org-level view), `rig-top100-agent-retry` (retries as spend),
`rig-top100-agent-evaluation` (quality that justifies the tier), `rig-top100-agent-observability`
(the trace the cost rows hang on).
