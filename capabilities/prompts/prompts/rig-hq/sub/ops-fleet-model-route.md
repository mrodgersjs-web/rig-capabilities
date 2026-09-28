---
id: rig-hq-sub-j11-model-route
version: 1
status: draft
tier: sub
department: Ops, Fleet & Security
agent: otto-operations
parent: rig-hq-prompt-otto-operations
task: Recurring sub-prompt (J11): set or repair a model/lane route with probe evidence
triggers: model route, route around the failure, fix the lane, fallback chain
sources: ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md (J11), ~/.rig/jake/aos/maps/aside-links/jtbd.json
provenance: first-party RIG design | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Model route (J11 recurring)

**Trigger.** A model or node needs routing: initial pin, fallback change, or repair.

**Typed inputs.** `target` (agent/run), `model_route` (fixed order:
mimo-plan/mimo-v2.6-pro -> xai-oauth/grok-4.7 -> anthropic/claude-opus-5-5; never
Flash), `config_path`, `bar` (probe must return a real response).

**Steps.**
1. Probe each lane/model in the chain before changing anything; a config entry is not
   a live provider.
2. Apply the route as a saved diff; never blind-overwrite the config.
3. Probe again after; verify the run is actually bound to the intended model (audit
   the session turns, not the banner).
4. Write the receipt: probes, diff hash, fallback state.

**Output format.**
```
STATUS: DONE | BLOCKED <reason>
Probes before: <lane -> result>
Change: <diff hash>
Probes after: <lane -> result>
Binding audit: <n/n turns on intended model>
Receipt: <path>
```

**Expected output.** A route that is proven live, not just configured.

**Done test.** Post-change probe returns a real response and the binding audit passes.

**Failure handling.** Probe failure on every lane -> BLOCKED and file a repair card;
never report success from a start record.

**Persistence.** Receipt + diff saved; the ops state file updated.

**Redaction.** No endpoint keys or tokens in any output.

**Stop / escape hatch.** If no lane in the chain is alive, stop and ask — do not
promote a Flash model to fill the gap.
