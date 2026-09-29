---
name: agentic-observability
description: "agentic-systems-setup sub-skill, gate E6 (L4 observed): make every agent or workflow run visible locally before anything leaves the machine - the engine's own local UI and API, OpenTelemetry console or file export, self-hosted Langfuse when Docker is up - and treat LangSmith, Langfuse Cloud, and vendor tracing as data egress under Gate-D. JEV-FIRST MANDATE."
tags: [rig, agentic-systems, sub-skill, observability, tracing, langfuse, opentelemetry]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: durable-observe
  extends: "agentic-selfhost-docker, rig-top100-agent-observability"
outcome: "An L4 observed receipt: a run id and its spans or steps read back from a local API with curl, no traces sent off the machine without an approval id, and vendor default tracing switched off or approved."
activation: "Load when a setup adds tracing, dashboards, or run history, when a framework enables vendor tracing by default, and before any trace or prompt leaves the machine."
instruction: "Use the engine's local UI and API or an OpenTelemetry console exporter first, read the run back by id with curl, disable vendor tracing that exports by default, and hold hosted tracing (LangSmith, Langfuse Cloud) at Gate-D as data egress."
applies_when:
  env: "loopback services on Mike's Mac; Docker only when docker info answers"
  runtime: "framework-native run APIs, OpenTelemetry SDKs, self-hosted Langfuse"
  deps: "the framework skill's L3 receipt; curl"
  params: "framework, trace sink, run id"
  budget: "one observed run per setup"
  scale: "local development observability, not production monitoring"
permissions:
  - fs.read
  - bash
  - net.api-calls
  - gate-d-required:data-egress
flow:
  - Pick the local sink in order - engine API, OpenTelemetry console or file, self-hosted Langfuse.
  - Run one traced hello and capture its run id.
  - Read the run back by id from the local API with curl and save the output.
  - Switch off vendor default tracing or hold it at Gate-D.
done_when:
  - "grep:capabilities/skills/agentic-observability/SKILL.md:read back"
  - "grep:capabilities/skills/agentic-observability/SKILL.md:Gate-D"
  - "cmd:python3 capabilities/skills/agentic-systems-setup/scripts/validate_hierarchy.py"
out_of_scope:
  - sending prompts, traces, or outputs to a hosted service without an approval id
  - production alerting and on-call design
  - claiming a run is visible from a screenshot or a statement alone
---

# agentic-observability

JEV FIRST, binding on every observability step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call; L4 receipts are judged with `rig-s1gate check agentic.setup`. When the
classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only
above 0.9.

## Load surface

Always loaded at the start of every agentic setup task that adds tracing: the
`agentic-systems-setup` meta-skill routes gate E6 here, `agentic-setup-conductor` loads it from
its routes table, and the `agentic-setup-session` harness names it as doctrine. It is a
task-start surface, not a deep reference.

## Order of sinks (local first)

1. The engine's own run API and UI (Prefect server, Temporal dev server, Kestra, Dagster,
   Airflow, n8n, Dify), on an instance the setup started itself on a fresh port. Mike's Temporal dev server (pid 7353, 127.0.0.1:7233 and :8233) is not for setup proofs.
   The framework skill confirms the port at L0.
2. OpenTelemetry console or file exporter in the app: zero egress, works for any Python or
   TypeScript framework that emits OTel spans.
3. Self-hosted Langfuse through `agentic-selfhost-docker`: BLOCKED on 2026-09-28 because no Docker
   daemon runs. Colima 0.10.3 and lima 2.1.3 are installed in `~/.homebrew/bin`, not on the sandbox PATH; `colima status` fails "lima not found" unless `~/.homebrew/bin` is on PATH, and then reports "colima is not running"; starting it is Mike's step in a normal terminal. `capabilities_observe` reported `langfuse_configured: false`,
   `langfuse_reachable: false`, 1,132 local traces. Keychain item name present:
   `com.rig.env.LANGFUSE_SECRET_KEY`.
4. Hosted tracing (LangSmith, Langfuse Cloud, a vendor's trace dashboard): prompts and outputs
   leave the machine, so it is Gate-D data egress.

## Evidence standard for L4 observed

The receipt carries the run id and the output of reading that run back from the local API
(for example `curl -s http://127.0.0.1:<port>/<runs endpoint>/<id>` with the state and step
count). "It should show in the UI" and a screenshot without the id are not evidence.

## Vendor defaults to check at L0

Some SDKs trace to the vendor by default when a key is present (the OpenAI Agents SDK sends
traces to OpenAI unless tracing is disabled; LangSmith tracing turns on with its env variables).
The framework skill records the exact switch from today's docs and the receipt states whether it
is off or approved.
