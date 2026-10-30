---
name: rig-ops
description: "Run and secure Mike's machines: local and fleet model servers (Ollama, OpenJev, Laya, Blackwell, 96GB, 256GB), the NAS and Docker, installing a tool or repo, Aside/OMP/Orca configuration, launchd jobs, tunnels, drives, routine health, secrets and security incidents. Use when a model, server, install, config, tunnel, drive or routine is down, slow or being set up."
done_when:
  - grep:capabilities/skills/rig-ops/SKILL.md:A claimed fix counts only when a second path confirms it
  - grep:capabilities/skills/rig-ops/SKILL.md:Never print a secret value
---

# rig-ops: run and secure the machine

Full map of children with paths: `LAYERS.md` next to this file. Owner agent: otto-operations (security child: vera-security).

## Route

| Task | Skill |
|---|---|
| Clone, evaluate, install or wire a tool, repo or model | `tool-intake` |
| A model call failed, a gate returned something odd, a routine went silent | `provider-probe-first` |
| Which local model route answers now; wire something to a local model | `agentic-local-models` |
| Probe toolchains, Docker and runtimes before a setup | `agentic-env-probe` |
| Colima, Docker Compose, QNAP container stacks | `agentic-selfhost-docker` |
| New models, catalog drift, a stale gate stack | `model-capability-scout` |
| Something breaks inside the Aside sandbox (native binaries, process list, ports) | `app-sandbox-survival` |
| An agent trace is empty or a harness never launched | `trace-harness-launch-failure` |
| Vulnerabilities, leaked secrets, auth failures, incidents | `when-securing-the-estate` |

## Machine facts (verified 2026-09-29; re-probe before relying on any of them)

- The Aside sandbox cannot register launchd jobs (`launchctl bootstrap` returns error 5) and cannot list processes (`ps`, `pkill` blocked). Host-only commands go through a visible, titled Orca terminal: `orca terminal create --title "<what>" --command "<cmd>" --json`, read it back with `orca terminal read --terminal <handle>`, then close it. Never type into a terminal that is running an agent or the conductor.
- The local Ollama `com.rig.qwen38-27b` (127.0.0.1:11434) and the live-coach Ollama (11436) keep their models on the OWC-DOCKER drive: `~/.ollama/models` is a symlink into `/Volumes/OWC-DOCKER/`. Drive unmounted means both crash-loop; they recover by themselves once it mounts. `com.rig.local-ollama-desktop-guard` kills the Ollama desktop app on purpose; do not start the app.
- OpenJev, the local Jev-compatible System One, runs on the 48GB Mac at `http://100.76.209.22:8080/v1/systemone` (no key). It is the private routing lane and the independent labeler for the skill surface.
- The `com.rig.rowboat-*` launch agents are deliberately disabled. Do not re-enable them.
- `curl` exit 7 means the host is up and the service is down; exit 28 means the host is unreachable or filtered.

## Rules

- Probe with one real call before diagnosing anything (`provider-probe-first`). A config that looks right is not evidence.
- A claimed fix counts only when a second path confirms it (for example `launchctl print` plus a `curl` of the port).
- Never print a secret value; name keychain items (`com.rig.env.*`) instead.
- Paid services, public endpoints, deploys, credential changes and destructive cleanup stop at Gate-D.

## Done-test

`skill-surface route "local ollama is down"` lands on this meta, and every fix reported from here carries the second-path probe output that proves it.
