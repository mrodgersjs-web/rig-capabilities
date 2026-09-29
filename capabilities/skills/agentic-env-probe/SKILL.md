---
name: agentic-env-probe
description: "agentic-systems-setup sub-skill, gate E1 (and the route half of E2): probe this machine before any agentic framework setup - toolchains and versions outside the sandbox PATH, Docker daemon, Java runtime, PYTHONHOME leakage, and which local model routes answer right now - and choose the route (Aside sandbox, Orca host shell, Docker) from observed facts. JEV-FIRST MANDATE."
tags: [rig, agentic-systems, sub-skill, environment, probe, routes]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: probe
  extends: "app-sandbox-survival, provider-probe-first, jake-lessons-ledger"
outcome: "A dated probe.json that names every toolchain with its path and version, the Docker and JVM state, the model routes that answered, and a route per workload class with BLOCKED reasons instead of guesses."
activation: "Load at the start of every agentic framework setup, before the first install command, and again whenever a tool looks missing, a daemon looks down, or a model route is about to be named."
instruction: "Run env_probe.py with PYTHONHOME unset, read its routes and blocked lists, pick the route per workload from that file, and cite the probe path in the setup receipt; never name a route or declare a tool absent from memory."
applies_when:
  env: "the Aside bash sandbox or an Orca terminal on Mike's Mac"
  runtime: "Python 3 stdlib (the probe itself); probes uv, node, pnpm, docker, java, colima, temporal, n8n"
  deps: "capabilities/skills/agentic-env-probe/scripts/env_probe.py"
  params: "optional --endpoint base URLs, --no-lan, --timeout seconds"
  budget: "under 20 seconds per probe"
  scale: "one machine per probe"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - Run env_probe.py with PYTHONHOME and PYTHONPATH unset and save probe.json in the run folder.
  - Read tools, docker, java_runtime, endpoints, routes, and blocked from the file.
  - Choose the route per workload class from the route table below.
  - Record BLOCKED routes with their failing check instead of retrying blindly.
  - Cite the probe path and time in the setup receipt.
done_when:
  - "cmd:env -u PYTHONHOME -u PYTHONPATH python3 capabilities/skills/agentic-env-probe/scripts/env_probe.py --no-lan --no-libval --timeout 2"
  - "cmd:env -u PYTHONHOME -u PYTHONPATH python3 capabilities/skills/agentic-env-probe/scripts/env_probe.py --selftest-libval"
  - "cmd:env -u PYTHONHOME -u PYTHONPATH python3 capabilities/skills/agentic-env-probe/scripts/env_probe.py --libval-only --libval-plant | grep -q ABSENT"
  - "file:capabilities/skills/agentic-env-probe/references/probe-2026-09-28-final.json"
  - "grep:capabilities/skills/agentic-env-probe/SKILL.md:UNREACHABLE_FROM_SANDBOX"
out_of_scope:
  - starting, stopping, or reconfiguring daemons (colima start, Docker Desktop) from the sandbox
  - installing toolchains; this skill only observes
  - reading credential values
---

# agentic-env-probe

JEV FIRST, binding on every probe and route decision: an agent whose only context is this
excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE
any frontier LLM call; setup receipts are judged with `rig-s1gate check agentic.setup`. When the
classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only
above 0.9; below that the gate does not advance.

## Load surface

Always loaded at the start of every agentic setup task: the `agentic-systems-setup` meta-skill
routes gate E1 here, `agentic-setup-conductor` loads it from its routes table before the first
action, `agentic-env-prober` executes it, and the `agentic-setup-session` harness names it as
doctrine. It is a task-start surface, not a deep reference an agent must already know about.

## Run it

```sh
cd ~/Developer/rig-capabilities
env -u PYTHONHOME -u PYTHONPATH python3 capabilities/skills/agentic-env-probe/scripts/env_probe.py \
  --out <run>/probe.json            # add --endpoint http://HOST:PORT/v1 for extra routes
```

It searches `~/.local/bin`, `~/.homebrew/bin` (Mike's Homebrew prefix), `/usr/local/bin`, and
`/opt/homebrew/bin` as well as PATH, because the Aside sandbox PATH omits them (lessons AS-03,
AS-13); `on_sandbox_path: false` means "call it by absolute path or prepend PATH", never "not
installed". It also lists keg-only JDKs (`~/.homebrew/opt/openjdk*`, AS-05), runs `colima status`,
probes library validation (AS-11), and lists TCP listeners on framework ports (AS-12).

## Library validation (AS-11)

The sandbox stamps `com.apple.quarantine` on every file it writes, and macOS then refuses to load
freshly written native code ("library load disallowed by system policy"). The probe copies the
interpreter's own `_json` extension into a temp dir, loads the original (control) and the copy:
`PRESENT` = copy refused while the original loads; `LIKELY` = copy quarantined and its load hung
past `--libval-timeout` (denials took 6 s, 10 s, and over 100 s on 2026-09-28); `ABSENT` = copy
loaded. RED/GREEN proof (2026-09-28): live run PRESENT; `--libval-plant` (no quarantined copy)
ABSENT; `--selftest-libval` classifier fixtures 4/4. When PRESENT, native-extension dependencies
go to a pure-Python fallback, a pin, a stub, or the host shell; stripping the quarantine attribute
made one refused `.so` load in a throwaway venv, but that bypasses a sandbox protection and is
Mike's call (AS-18), not a route.

## Listeners (AS-12)

`listeners_on_framework_ports` names pid, command, and bind address for known framework ports;
`listeners_all_interfaces` flags anything bound to `*`. A bound port is a stray to report, never a
server you own. Processes started in an earlier bash call cannot be killed from a later one, so
strays go to Mike for a normal terminal.

## Route table (read from probe.json)

| Probe field | Route |
|---|---|
| `tools.uv.present` | Python frameworks: `uv venv` + `uv pip install` in the sandbox, PYTHONHOME unset (AS-02) |
| `tools.node.present` | pure-JS Node frameworks in the sandbox; anything loading a native `.node` addon in an Orca terminal (AS-06) |
| `docker.daemon == false` | every Docker-route step is BLOCKED with `docker info`'s error (AS-04); `colima start` or Docker Desktop is a host action |
| `jdks` | the macOS `java` stub fails, but keg-only JDKs work via JAVA_HOME: JDK 26 at `~/.homebrew/opt/openjdk@26` (`JAVA_HOME=~/.homebrew/opt/openjdk@26/libexec/openjdk.jdk/Contents/Home`); JVM routes are BLOCKED only when `jdks` is empty (AS-05) |
| `endpoints[].state == ANSWERED` | first answered loopback route is the local model route; confirm with `agentic-local-models` probe_endpoint.py |
| endpoint `UNREACHABLE` or `TIMEOUT` on a LAN address | record `UNREACHABLE_FROM_SANDBOX`, not "down"; re-probe from an Orca terminal before calling it dead (AS-08) |
| endpoint `KEYED` (401/403) | alive and keyed; needs a keychain item name via `agentic-secrets` |

## Observed 2026-09-28 14:30 MDT (references/probe-2026-09-28-final.json)

- Found under `~/.homebrew/bin`: colima 0.10.3 (not running), docker 29.6.1, limactl, ollama,
  temporal 1.7.2; keg-only JDK 17.0.20.1,
  21.0.12, 26.0.2 in `~/.homebrew/opt`. The 09:25 probe below missed all of them.
- Colima 0.10.3 and lima 2.1.3 are installed in `~/.homebrew/bin`, not on the sandbox PATH; `colima status` fails "lima not found" unless `~/.homebrew/bin` is on PATH, and then reports "colima is not running". Starting Colima is Mike's step in a normal terminal.
- Mike's Temporal dev server (pid 7353, 127.0.0.1:7233 and :8233) is not for setup proofs; a proof starts its own with `~/.homebrew/bin/temporal server start-dev --port <fresh> --ui-port <fresh> --headless` under a time-box.
- library_validation PRESENT; strays: java pid 54463 on `*:8080` (Kestra lab), node pid 23506 on
  `*:4400` (n8n lab).
- Model routes: 8771 and 8657 answered; Blackwell `192.168.68.90:8111` answered
  (`blackwell-qwen38-uncensored`, probe_endpoint ANSWERED_OK in 0.12 s) after timing out at 09:25.

## Observed 2026-09-28 09:25 MDT (references/probe-2026-09-28.json)

- Tools: uv 0.12.19, Python 3.12.13 and 3.13.12, node v22.22.3, pnpm 10.34.5, npx 10.9.8,
  n8n 2.33.3, all in `~/.local/bin` and none on the sandbox PATH; docker CLI 29.6.1 at
  `/usr/local/bin/docker`; PYTHONHOME exported into the sandbox. Corrected at 14:30: colima 0.10.3,
  lima 2.1.3, and temporal 1.7.2 are installed in `~/.homebrew/bin`, which this probe did not search yet.
- Docker: CLI points at `~/.colima/default/docker.sock`; daemon down (BLOCKED).
- Java: the macOS `java` stub said "Unable to locate a Java Runtime"; corrected at 14:30: JDK 17, 21,
  and 26 are installed keg-only in `~/.homebrew/opt` (JDK 26 at `~/.homebrew/opt/openjdk@26`).
- Model routes: PAIR `127.0.0.1:8771` answered (`qwen3.8-uncensored:27b`, 9 ms); Mac Studio
  tunnel `127.0.0.1:8657` answered (`MiMo-V2.6-Flash-RL-MLX-4bit-MTP`); `127.0.0.1:11435` and
  OmniRoute `127.0.0.1:20128` refused; Blackwell `192.168.68.90:8011` refused and `:8111` timed
  out from the sandbox (`UNREACHABLE_FROM_SANDBOX`, not proven down).
- PyInstaller single-file CLIs exit 1 here (AS-01): `~/.local/bin/yt-dlp --version` rc=1 with a
  semaphore warning, while the same tool installed with `uv pip` works.

## Rules

1. Probe at the start of every session; yesterday's probe is history, not state.
2. A tool is missing only when `present: false` after the extended-path search.
3. Daemons are started from an Orca terminal by Mike or a host-shell agent, then re-probed.
4. Cite `probe.json` by path and timestamp in every receipt that depends on it.
