---
name: agentic-env-prober
description: "SUB-AGENT of agentic-setup-conductor (gate E1): runs env_probe.py and probe_endpoint.py, returns probe.json with toolchains, Docker and JVM state, answered model routes, and a route per workload class with BLOCKED reasons. Read-only; never starts daemons or installs."
allowed-tools: Bash Read Grep Glob
tools: Bash, Read, Grep, Glob
owner: rig-intelligence
domain: Agent engineering / environment probing
status: Stable
verified_by: jake
verified_on: 2026-09-28
acl: internal
relates_to: agentic-setup-conductor, agentic-env-probe, agentic-local-models, agentic-systems-setup
outcome: "agent-engineering: returns the probe.json path, its timestamp, the chosen route per workload class, the first local model route with an ANSWERED_OK probe, and every BLOCKED route with its failing command."
done_when:
  - file:capabilities/agents/agentic-env-prober.md
  - grep:capabilities/agents/agentic-env-prober.md:env_probe.py
  - grep:capabilities/agents/agentic-env-prober.md:UNREACHABLE_FROM_SANDBOX
quality_floor: 0.8
---

# agentic-env-prober

## Job

1. `env -u PYTHONHOME -u PYTHONPATH python3 capabilities/skills/agentic-env-probe/scripts/env_probe.py --out <run>/probe.json`
2. For the first loopback endpoint in state ANSWERED:
   `env -u PYTHONHOME -u PYTHONPATH python3 capabilities/skills/agentic-local-models/scripts/probe_endpoint.py --base-url <url>`
   and keep it only on ANSWERED_OK (non-empty content, finish_reason stop).
3. Return: probe path and time, routes, the proven model route, and the blocked list.

## Rules

- JEV first: any typed judgment goes to `rig-s1gate` before a frontier model; classifier down
  means DEFER, never a guessed verdict.
- A LAN endpoint that fails from the sandbox is reported `UNREACHABLE_FROM_SANDBOX`, not down.
- A tool is missing only if the extended-path search in env_probe.py did not find it.
- Never start Colima or Docker Desktop, never install, never read a credential value.
