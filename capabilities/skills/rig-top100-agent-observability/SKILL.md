---
name: rig-top100-agent-observability
description: "Make every agent run reconstructable: a run id, spans for each step, the decision that was taken and the evidence behind it, tool inputs and outputs, and a replay that reproduces the run locally. Use whenever 'no proof, no confidence' has to be satisfied, when a run behaved oddly and print statements were not enough, or before any hosted tracing service sees the trace."
tags: [rig, top100, agentic-systems, observability, tracing, opentelemetry, replay]
metadata:
  tier: canonical
  domain: Agentic Systems
  rank: 14
  status: built-out-2026-25
  source_stub: ~/.grok/skills/rig-top100-agent-observability/SKILL.md
outcome: "Any past run can be pulled up by id and read back from a local API: spans, decisions, evidence paths, cost, and verdict, with the option to replay it; and no trace left the machine without an approval id."
activation: "Load when a run needs to be defended later, when debugging a run that is already over, when adding tracing to a new agent, and whenever a vendor SDK would export prompts by default."
instruction: "Emit structured spans, not prose logs: one per step with run id, parent id, start and end, inputs, outputs, model, tokens, and cost. Record decisions as explicit rows (options considered, rule applied, verdict, evidence path). Keep the sink local first: engine API, an OpenTelemetry console or file exporter, self-hosted Langfuse. Hosted tracing is data egress and waits at Gate-D. Verify by reading the run back by id with curl, not by trusting the writer's summary."
applies_when:
  env: "local loopback services; file or SQLite trace store; Docker only when available"
  runtime: "OpenTelemetry SDK, framework-native run APIs, self-hosted Langfuse"
  deps: "curl, a trace store, a run id minted at entry, retention policy"
  params: "run id, span naming convention, sampling rate, retention window, redaction list"
  budget: "tracing overhead under 5 percent of step latency; sampled, not dropped, on bulk paths"
  scale: "single agent to fleet-wide trace correlation by correlation id"
permissions:
  - fs.write
  - bash
  - net.api-calls
  - gate-d-required:hosted-trace-egress
flow:
  - Mint a run id at the entry point and propagate it into every child, tool call, and file written.
  - Emit one span per step with parent id, timings, inputs, outputs, model, tokens, and cost.
  - Write decision rows separately from spans: options, rule, verdict, evidence path, confidence.
  - Redact secrets and personal data at emit time, so nothing sensitive is ever in the store.
  - Send to a local sink first: engine API, OTel console or file, self-hosted Langfuse.
  - Disable vendor default tracing that exports, or hold it at Gate-D with an approval id.
  - Prove it by reading the run back by id with curl and saving the output next to the receipt.
  - Keep enough retention to answer last month's question; archive spans, keep decision rows.
done_when:
  - "cmd:jq -es -e 'all(.[]; has(\"run_id\") and has(\"trace_id\") and has(\"span_id\"))' ${RUN_DIR:-./out/rig-top100-agent-observability}/spans.jsonl"
  - "cmd:jq -e '(.spans[] | select(.parent_id != null) | .parent_id) as $p | true' ${RUN_DIR:-./out/rig-top100-agent-observability}/spans.jsonl"
  - "cmd:jq -es -e 'all(.[]; .verdict != null and .evidence != null)' ${RUN_DIR:-./out/rig-top100-agent-observability}/decisions.jsonl"
  - "cmd:test -f ${RUN_DIR:-./out/rig-top100-agent-observability}/readback.txt"
  - "grep:SKILL.md:Gate-D"
out_of_scope:
  - prose logs and print statements as the audit record
  - hosted tracing that exports prompts without an approval id
  - claiming a run was visible from a screenshot or a restatement
  - unredacted secrets sitting in the trace store
---

# Agent Observability and Tracing

## Why this exists

"No proof, no confidence" fails at the trace level: if the only record of a run is the agent's
summary, an error is indistinguishable from a lie. Tracing turns "it seemed fine" into a
retrievable sequence of steps, decisions, and evidence, and it is the substrate that makes
eval, cost, and safety auditable rather than asserted.

## Outcome contract

- Why: 'No proof, no confidence' requires traceable evidence
- Baseline: Print statements
- Target: Distributed tracing with OpenTelemetry, decision trees, and replay capability

## Method

### 1. Spans, with the run id everywhere

Mint a run id at entry and propagate it into children, tool calls, and every file the run
writes. One span per step: parent id, timings, inputs, outputs, model, tokens, cost. A span
with no parent is a bug in propagation, not a root step, unless it is the entry point.

### 2. Decision rows, not just timings

Latency tells you what was slow, not what was chosen. Write a separate row per decision: the
options considered, the rule or gate applied, the verdict, the evidence path, and a confidence.
This is what lets a run be second-guessed months later by someone who was not there.

### 3. Redact at emit

Secrets, tokens, and personal text get scrubbed before they hit the store. Redaction at query
time leaks, because the raw value already sits on disk. Keep the redaction list next to the
exporter config and test it with a deliberate secret.

### 4. Local first, hosted at Gate-D

Order of preference: the engine's own run API, an OTel console or file exporter, self-hosted
Langfuse when Docker is up. Hosted tracing (LangSmith, Langfuse Cloud) sends prompts off the
machine, which is egress and needs an approval id. Frameworks that enable vendor tracing by
default get that switched off explicitly.

### 5. Replay

Because inputs are recorded, the run can be replayed against the same inputs. Replay is the
test that the trace is complete: if you cannot reconstruct the run from its spans and decision
rows, the observability is decorative.

## Failure modes

- Logs full of text, empty of structure: no way to filter by agent, task, or verdict.
- Vendor tracing quietly exporting, discovered on an egress review.
- Traces kept, decision rows dropped, so the artefact exists and the reasoning does not.
- Sampling at 100 percent on a bulk path until tracing itself becomes the bottleneck.
- A trace that only the writer's prompt style can interpret, with no span naming convention.

## Done-test (executable)

```bash
RUN_DIR=${RUN_DIR:-./out/rig-top100-agent-observability}
r=0
jq -es -e 'all(.[]; .run_id and .trace_id and .span_id)' "$RUN_DIR/spans.jsonl" >/dev/null || { echo "BLOCK spans missing ids"; r=1; }
jq -es -e 'all(.[]; .verdict != null and .evidence != null)' "$RUN_DIR/decisions.jsonl" >/dev/null || { echo "BLOCK decisions without evidence"; r=1; }
grep -qE '(api[_-]?key|Bearer [A-Za-z0-9]{12})' "$RUN_DIR/spans.jsonl" && { echo "BLOCK secret in trace"; r=1; }
test -s "$RUN_DIR/readback.txt" || { echo "BLOCK trace never read back by id"; r=1; }
[ "$r" -eq 0 ] && echo "PASS" || echo "BLOCK"
```

## Verification

Pick a run at random from the previous day and answer three questions from the store alone:
which agent, which decision, which evidence. Then read the run back over the local API with
curl and save the output; that file is the proof, not the dashboard. Finally plant a known
secret in a call and confirm the stored span contains a redaction marker instead of the value.

## Related

`rig-top100-agent-cost` (rows hang on spans), `rig-top100-agent-evaluation` (judged runs need
traces), `rig-top100-agent-safety` (the audit trail), `rig-top100-monitoring-alerting` (live
signals, as opposed to post-hoc reconstruction).
