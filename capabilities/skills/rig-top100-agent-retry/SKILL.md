---
name: rig-top100-agent-retry
description: "Make pipelines survive flaky APIs: classify each failure before retrying, use jittered exponential backoff that honours Retry-After, wrap each dependency in a circuit breaker, fall back to another provider on a stated basis, and escalate to a human when recovery is not automatic. Use when runs die on transient errors, when retries hammer a rate-limited endpoint, or when a duplicate side effect has already been sent."
tags: [rig, top100, agentic-systems, reliability, retries, circuit-breaker, fallback]
metadata:
  tier: canonical
  domain: Agentic Systems
  rank: 12
  status: built-out-2026-10-25
  source_stub: ~/.grok/skills/rig-top100-agent-retry/SKILL.md
outcome: "A run where every failure was classified, only retryable failures were retried, backoff respected the server's own hint, a breaker opened and half-opened on cue, no retry duplicated a side effect, and the escalation target is named in the receipt."
activation: "Load when a job calls an API, model, or scraper that has ever failed; when a pipeline crashed on a transient error; before raising a retry count; and whenever a retried action could double-send or double-write."
instruction: "Classify the error first: transient (backoff and retry), permanent (fail fast, no retry), throttled (respect Retry-After and shed load), unknown (bounded retry with logging). Never retry a write without an idempotency key. Keep consecutive and total attempt budgets, open the breaker after the consecutive threshold, half-open with one probe, and record every attempt so a retry that succeeded hides nothing."
applies_when:
  env: "any outbound call path: model providers, search APIs, scrapers, webhooks, the local queue"
  deps: "attempt log, breaker state store, an idempotency key source, a named escalation target"
  runtime: "worker or agent loop with a per-call timeout and a per-run deadline"
  params: "base delay, jitter factor, max attempts, breaker threshold, fallback chain, budget"
  budget: "retry wall-clock cost at or below 25 percent of the run deadline"
  scale: "per dependency, per provider, per agent; a shared breaker per host, not per call site"
permissions:
  - fs.write
  - bash
  - net.api-calls
flow:
  - Classify the failure before deciding anything else; a permanent error retried is a stall.
  - Retry transient errors with exponential backoff, full jitter, and a cap; honour Retry-After exactly.
  - Attach an idempotency key to every retried side effect so a duplicate is a no-op.
  - Enforce per-attempt timeouts: a hung call is a failure, not a slow success.
  - Track consecutive failures per dependency and open the breaker at the threshold; half-open with one probe.
  - Fall back to the next provider only on the documented basis (unavailable or throttled, never on a validation error).
  - Record every attempt with class, delay, provider, and outcome in the run receipt.
  - Escalate on budget exhaustion with the failing dependency, the attempts, and the smallest useful next step.
done_when:
  - "cmd:jq -e '[.attempts[].class] | length > 0' ${RUN_DIR:-./out/rig-top100-agent-retry}/attempts.jsonl"
  - "cmd:jq -e 'select(.class==\"permanent\") | select(.attempts == 1)' ${RUN_DIR:-./out/rig-top100-agent-retry}/attempts.jsonl"
  - "cmd:jq -e '.max_attempts <= 5 and .jitter == true and .honors_retry_after == true' ${RUN_DIR:-./out/rig-top100-agent-retry}/policy.json"
  - "grep:SKILL.md:circuit breaker"
  - "grep:SKILL.md:idempotency"
out_of_scope:
  - retrying a 4xx validation error with the same payload
  - unlimited retries with no deadline as a reliability strategy
  - falling back to a worse model on a scoring disagreement and calling it resilience
  - silently succeeding on attempt four with no log of attempts one to three
---

# Error Recovery and Retry Logic

## Why this exists

A crash on a 429 costs a rerun; an unbounded retry costs the whole deadline; a blind retry of
a write costs a second email to a client. The difference is classification. Most "the retry
policy is broken" complaints are actually "we never looked at what kind of failure this was".

## Outcome contract

- Why: API failures should not kill a pipeline run
- Baseline: Crash on error
- Target: Exponential backoff, circuit breakers, fallback providers, and escalation chains

## Method

### 1. Four classes, four reactions

| Class | Examples | Reaction |
| --- | --- | --- |
| Transient | 5xx, connection reset, DNS | backoff and retry within budget |
| Throttled | 429, quota window | honour Retry-After, shed concurrency, then retry |
| Permanent | 400, 401, 403, schema mismatch | fail fast; retrying cannot change the input |
| Unknown | a new exception type | bounded retry (max 2), log the signature, then escalate |

Classifying first is the whole skill. Unknown is allowed once and then gets named.

### 2. Backoff that behaves

`delay = min(cap, base * 2^n) * random(0.5, 1.5)`, jittered so a fleet does not retry in
lockstep. Honour `Retry-After` exactly, and treat a missing hint as a signal to slow down, not
to speed up. Add a deadline across all attempts: a retry chain with no deadline turns one slow
dependency into a hung routine.

### 3. Idempotency, or the retry costs a client an email

Any retried side effect carries a key the receiver de-duplicates. For a provider that ignores
keys, split into a check-then-act pair, or move the effect behind a queue where a duplicate is
harmless. A retry that can double-send is not a recovery mechanism, it is a coin flip.

### 4. Circuit breaker

Count consecutive failures per dependency. Open after the threshold: stop calling, serve
cached results or skip the optional enrichment. Half-open with a single probe after a cooloff,
close on success. Breakers are per dependency and per host, and their state transitions are
logged, because an always-open breaker is an outage nobody notices.

### 5. Fallback and escalation

Fallback only on documented grounds: unavailable or throttled. Never fall back on a validation
error, and never silently drop to a weaker model mid-task and let quality slide unnoticed. When
the budget is gone, escalate with the dependency, the attempt list, and the smallest next step
plus a named owner. "Escalated" only counts if a human could act on the message.

## Failure modes

- Retry storms: fixed delays across a fleet, hammering an endpoint already at its limit.
- Retrying a permanent error until the deadline, which looks like a hang.
- A duplicate outward send because the key was generated per attempt, not per intent.
- A breaker that opens and never half-opens: a one-time outage becomes permanent degradation.
- Fallback to a cheaper model, and the quality drop is blamed on the prompt.

## Done-test (executable)

```bash
RUN_DIR=${RUN_DIR:-./out/rig-top100-agent-retry}
r=0
jq -e '.max_attempts <= 5 and .jitter and .honors_retry_after' "$RUN_DIR/policy.json" >/dev/null || { echo "BLOCK backoff policy"; r=1; }
jq -e '[.attempts[].class] | length >= 1' "$RUN_DIR/attempts.jsonl" >/dev/null || { echo "BLOCK no attempt log"; r=1; }
jq -es -e 'all(.[]; select(.class=="permanent") | .attempt <= 1)' "$RUN_DIR/attempts.jsonl" >/dev/null || { echo "BLOCK permanent error retried"; r=1; }
jq -es -e '[.[] | select(.side_effect==true) | .idempotency_key] | all(. != null)' "$RUN_DIR/attempts.jsonl" >/dev/null || { echo "BLOCK side effect without idempotency key"; r=1; }
test -f "$RUN_DIR/breaker-state.json" || echo "WARN no breaker state (single-shot run?)"
[ "$r" -eq 0 ] && echo "PASS" || echo "BLOCK"
```

## Verification

Replay a captured failure trace through the retry wrapper and assert the sequence of delays and
classes. Then force a permanent error and confirm exactly one attempt. Force a throttled
response with a `Retry-After` and confirm the wait matched the header rather than the schedule.
Finally confirm a retried side effect produced one artifact, not two.

## Related

`rig-top100-agent-cost` (retries are spend), `rig-top100-agent-observability` (the attempt
log), `rig-top100-monitoring-alerting` (breaker state as a signal), `rig-top100-consensus-mcp`
(multi-provider fallback with a verdict).
