---
id: rig-hq-sub-j2-3-a-model-drifts-to-flash
version: 1
status: draft
tier: sub
department: Engineering (TAC OS)
agent: jordan-jr-ai-engineering
parent: rig-hq-prompt-jordan-jr-ai-engineering
task: Interrupt sub-prompt (J2): a model drifts to Flash — pin the session back and log it
triggers: model drift, flash model, wrong model bound, route drift
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J2 interrupt 3), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md (homophones, model routing)
provenance: first-party RIG design | Reese J2 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: a model drifts to Flash

**Trigger.** A session turns out to be running a Flash model (or any model off the
pinned route).

**Typed inputs.** `session_id`, `expected_model`, `observed_model`, `config_path`.

**Steps.**
1. Verify by auditing the session's actual turns — the banner can lie. Homophone-test
   the observed name first (Quinn38/gemini 3.8 flash = Qwen 3.8 Flash on Blackwell).
2. Pin the session back to the route (mimo-plan/mimo-v2.6-pro -> xai-oauth/grok-4.7
   -> anthropic/claude-opus-5-5; never Flash) and prove the binding on new turns.
3. Log the drift and check sibling sessions for the same leak.

**Output format.**
```
STATUS: PINNED BACK | ESCALATED
Expected: <model> | Observed: <model> (evidence: <turn audit line>)
Proof of fix: <n/n new turns on intended model>
Siblings checked: <ids + verdicts>
Log: <path>
```

**Expected output.** The route restored and proven on live turns.

**Done test.** Post-pin turn audit passes; the drift is logged with evidence.

**Failure handling.** If the pin does not hold (config re-resolves it), escalate with
the re-resolution evidence.

**Persistence.** Drift log appended; siblings' state recorded.

**Redaction.** No endpoint keys.

**Stop / escape hatch.** Never accept "it says the right model in the banner".
