---
name: agentic-selfhost-docker
description: "Agentic Systems Setup sub-skill: Colima + Docker Compose lifecycle for self-hosted agentic stacks (Dify, Kestra, Flowise, Langflow) on Mike's Mac - record state first, start/stop, CPU/RAM/disk, host ports 4500-4599, volumes kept under the lab dir, upgrade, teardown, backups, and the honest no-Docker fallback routes (pip/npm/standalone Java). Use whenever any agentic-systems-setup skill needs a container runtime, a compose stack must come up or go down, or Colima state must be proven. JEV-FIRST MANDATE."
when_to_use: "Docker, Colima, Docker Compose, container runtime, stack up or down, host ports, volumes, upgrade, teardown, backup. JEV-FIRST MANDATE: route typed judgments to rig-s1gate before any frontier model; DEFERRED when the classifier is down."
tags: [rig, agentic-systems-setup, sub-skill, docker, colima, compose, self-host]
metadata:
  parent: agentic-systems-setup
  tier: sub
  extends: "supersedes the now-archived Hermes skill docker-agentic-stack (archived 2026-09-28; agentic-selfhost-docker owns the Docker/Colima lifecycle role)"
outcome: "A compose stack that came up on recorded ports with volumes under the lab dir, a proof.json receipt for every command, and the runtime returned to the exact state it was found in (colima status before and after)."
activation: "JEV-FIRST MANDATE, findable at task start: route typed judgments to rig-s1gate before any frontier model; DEFERRED is the only answer when the classifier is down. Load before starting, stopping, upgrading or tearing down Docker for any agentic stack, before picking host ports or volume paths, and whenever a Docker error needs a verdict: BLOCKED (environment prevents it) versus FAILED (it ran and failed)."
instruction: "JEV FIRST, findable at start: run ./bin/rig-s1gate check doctrine.surface BEFORE any frontier model; PASS continues, ESCALATE rewrites, BLOCK stops, DEFERRED fails closed. Then: record colima status before touching anything, run stacks only from ~/.rig/agentic-lab/<slug>/ with ports 4500-4599, never start or stop Colima for another worker's stack, and return the runtime to its found state."
applies_when:
  env: "Mike's Mac; Aside sandbox bash (120s per call) driving the host Docker CLI at /usr/local/bin/docker"
  runtime: "Docker context 'colima' -> unix:///Users/rig128gb/.colima/default/docker.sock; Colima VM"
  deps: "colima, docker compose v2+; sibling skills agentic-setup-dify / -kestra / -flowise / -langflow"
  params: "colima start --cpu 4 --memory 8 --disk 60 unless the stack's docs demand more"
  budget: "one stack per lab dir; teardown before reporting done"
  scale: "single Mac, single-user, local-only; not a multi-host fleet"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - JEV FIRST, findable at task start: route every typed judgment to rig-s1gate (Jev) via ./bin/rig-s1gate check doctrine.surface BEFORE any frontier model call; DEFERRED when the classifier is down, fail closed.
  - Record colima status and docker context as receipts before any change.
  - Start Colima only if it is down and a stack needs it; log the exact start command.
  - Run compose stacks from the lab dir with volumes and .env under the lab dir.
  - Probe local model endpoints from inside a container, not just from the host.
  - Bring stacks down, then prove the runtime is back in its found state.
done_when:
  - "grep:capabilities/skills/agentic-selfhost-docker/SKILL.md:found state"
  - "grep:capabilities/skills/agentic-selfhost-docker/SKILL.md:BLOCKED [(]environment"
  - "grep:capabilities/skills/agentic-selfhost-docker/SKILL.md:lsof -t -i"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/agentic-selfhost-docker/SKILL.md"
out_of_scope:
  - starting or stopping Colima for stacks owned by other workers (worker A5 owns Docker)
  - Docker Hub sign-ins, paid registry plans, public tunnels (Gate-D)
  - installing anything system-wide with sudo
---

# agentic-selfhost-docker

JEV FIRST, binding on every runtime-lifecycle decision: an agent whose only context is this excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM call; receipts are judged with `rig-s1gate check doctrine.surface`. When the classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9; below that the gate does not advance.

## Load surface

Always loaded at the start of every agentic-systems-setup task: the agentic-systems-setup family routes here before the first install, start or teardown command. It is a task-start surface, not a deep reference an agent must already know about. Typed judgments it forces: is the daemon actually up; is this error BLOCKED (environment) or FAILED (it ran and failed); is this port free; did teardown really restore the found state.


## 1. When to choose it and when not

Choose this when a sibling framework skill (agentic-setup-dify, agentic-setup-kestra, agentic-setup-flowise, agentic-setup-langflow) needs Docker, Colima state, compose lifecycle, port/volume decisions, or a fallback-route decision. Do not choose it for workflow authoring itself (that is agentic-setup-kestra / agentic-setup-flowise) or for app building (agentic-setup-dify / agentic-setup-langflow). Nearest alternatives in the wider estate: **n8n** (hosted workflow automation that also runs under this same compose lifecycle) and **trigger-dev** (Node-native background jobs that need no container runtime at all - pick it when Docker is unavailable and the job is event-driven).

## 2. Current version and sources

Fetched/observed 2026-09-28:
- Docker CLI **29.6.1** (`/usr/local/bin/docker`, symlink to Docker.app resources) and **Docker Compose v5.3.0** - observed on this Mac via `docker context ls` and `docker compose version` (exit 0).
- Colima **0.10.3** at `~/.homebrew/bin/colima` (symlink -> ../Cellar/colima/0.10.3/bin/colima; `colima version` -> 0.10.3, git commit 00f6c297) and **lima 2.1.3** at `~/.homebrew/bin/lima` (-> `limactl version 2.1.3`), both verified 2026-09-28. Blind spot corrected twice over: Homebrew lives at `~/.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.3`); Colima's "lima not found" was a PATH artifact - the fix is PATH, never `brew install lima`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`. The fix is PATH, never an install. Also under ~/.homebrew: Temporal CLI 1.7.2, JDKs 17.0.20.1 / 21.0.12 / 26.0.2.
- Stack docs fetched today (the authority for each image tag and prerequisite): https://docs.dify.ai/getting-started/install-self-hosted/docker-compose, https://kestra.io/docs/installation and https://kestra.io/docs/installation/docker, https://docs.flowiseai.com/getting-started, https://docs.langflow.org/get-started-installation.

## 3. Environment route and prerequisites

- **Aside sandbox bash** for orchestration: each call times out at 120s, `ps`/`pgrep`/`pkill` are blocked, `timeout` is absent on macOS. Run long pulls with `nohup ... &` and poll; stop a non-Docker server with `lsof -t -i :PORT | xargs kill`.
- **Host shell / Docker CLI**: `PATH="$HOME/.local/bin:/usr/local/bin:$PATH"`; Docker context `colima` -> `unix:///Users/rig128gb/.colima/default/docker.sock`.
- Prerequisites from fetched docs: Dify 2 vCPU / 4 GiB min (Docker VM sized 2 vCPU / 8 GiB on macOS, Compose 2.24.0+); Kestra 2 vCPU / 4 GiB min; Langflow dual-core + 2 GB min (4 GB recommended); Flowise Node 18.15.0 or 20+ for the npm route.

## 4. Install / lifecycle commands

Colima 0.10.3 and lima 2.1.3 are both installed under `~/.homebrew/bin`; the only defect is PATH - without `~/.homebrew/bin` on PATH, Colima misreports `lima not found`. The fix is NOT an install. Start/stop happen in a **host shell (Orca terminal), never the Aside sandbox**: a VM started from a sandbox call cannot be stopped from later sandbox calls. Gate-D-free local step **Mike runs himself** (docs: INSTALL.md https://raw.githubusercontent.com/abiosoft/colima/main/docs/INSTALL.md pairs Lima+Colima; README https://raw.githubusercontent.com/abiosoft/colima/main/README.md "Colima means Containers on Lima"):

```bash
# ALL of these run in a host shell (Orca terminal), never the Aside sandbox:
PATH="$HOME/.homebrew/bin:$PATH" colima start --cpu 4 --memory 8   # README's sized-VM example; add --disk for storage
# ... compose stacks work here ...
PATH="$HOME/.homebrew/bin:$PATH" colima stop      # from the SAME host shell when done
# only if something is genuinely missing: ~/.homebrew/bin/brew install colima lima
```

```bash
# host shell (Orca terminal) throughout - never the sandbox: a VM started here cannot be stopped later
export PATH="$HOME/.homebrew/bin:$HOME/.local/bin:/usr/local/bin:$PATH"
colima status                       # receipt FIRST: record found state verbatim
colima start --cpu 4 --memory 8   # only if down and a stack needs it
docker context ls                   # prove the active context and socket
cd ~/.rig/agentic-lab/<slug>        # compose files live here, never in a repo
docker compose up -d
docker compose ps
# ... work ...
docker compose down                 # add -v only when the volume is disposable
colima stop                         # MUST return to the found state
```

Ownership rule: worker A5 owns Docker for the agentic-systems-setup effort. No other worker starts or stops Colima.

## 5. Local-first model wiring

Point every stack's OpenAI-compatible provider at Mike's local endpoints (from containers use the LAN IP directly, never `localhost`):

- `http://192.168.68.90:8011/v1` and `http://192.168.68.90:8111/v1` (Blackwell).
- Local OpenAI-compatible endpoints verified ANSWERING from this sandbox on 2026-09-28: `http://127.0.0.1:8771/v1` (model `qwen3.8-uncensored:27b`; disable thinking or the content comes back empty) and `http://127.0.0.1:8657/v1` (model `MiMo-V2.6-Flash-RL-MLX-4bit-MTP`). The Blackwell LAN endpoints `http://192.168.68.90:8011/v1` and `:8111/v1` refuse (curl exit 7, `Failed to connect ... Couldn't connect to server`).
- Probe first: `curl -s -m 5 <base>/models`. From inside containers use the host LAN address of the same servers (never `localhost`); no paid API may be substituted.

## 6. Secrets

Keychain items by name only (`com.rig.env.<NAME>`), never values. Compose `.env` files stay under the lab dir, are never committed, and only `.env.example` placeholders ship. Change every default password and secret key the compose file ships with before first start.

## 7. Hello-world

A minimal deterministic proof that the runtime works, with no model:

```bash
docker compose config >/dev/null && echo COMPOSE_VALID   # exit 0 = file parsed
docker run --rm hello-world                              # daemon proof (pull + run)
```

Today the second command is unavailable (daemon down) - see receipts.

## 8. Durable and production features

Named volumes under the lab dir or explicit volume names per stack, `restart: unless-stopped` only for stacks Mike wants persistent, healthchecks on db-backed stacks, and compose `depends_on` with conditions. Backups = `docker compose exec db pg_dump` style exports copied out of the volume before upgrade or teardown.

## 9. Observability

`docker compose logs -f --tail 100`, `docker compose ps`, and per-service health endpoints. Treat a healthy container as activity, not completion: require a request-level receipt (hello flow ran, API answered).

## 10. Testing

Deterministic test = `docker compose config` plus a no-model hello run. **Planted failure:** point `docker compose -f` at a copy with one image name typo'd (e.g. `postgres:15-alpne`); `docker compose config` may still pass, so the red must come from `docker compose up` failing to pull - if the check stays green, the check is theater; record the red and restore.

## 11. Deploy / self-host hardening and Gate-D

Bind ports to 127.0.0.1 where the stack allows, keep `EXPOSE_NGINX_PORT` off 80 for lab stacks, rotate every shipped default secret. **Gate-D (do not do without Mike's explicit approval):** Docker Hub or registry sign-in, any cloud login, deploy, push, paid plan, public URL, or tunnel (cloudflared/ngrok).

## 12. Teardown and upgrade

`docker compose down` (optionally `-v`), confirm with `docker compose ps -a`, then `colima stop` and re-run `colima status` to prove the found state is restored. Upgrade = read the release notes first (Dify requires per-release upgrade steps), diff `.env.example` against `.env` for new keys, pull pinned tags, never silently move to `:latest` in a lab receipt.

## 13. Gotchas

- **Search blind spot (corrected twice on 2026-09-28):** Homebrew is at `~/.homebrew`; probes of /opt/homebrew and /usr/local called Colima 'absent' while 0.10.3 + lima 2.1.3 were installed, and a PATH-less `colima status` falsely said `lima not found` - add ~/.homebrew/bin to PATH before declaring anything missing or installing anything. A socket file is not a running daemon either: the stale `~/.colima/default/docker.sock` coexists with `colima status` -> "colima is not running"; probe `docker info` for a Server section.
- macOS has no `timeout(1)`; `timeout 20 ...` fails with `command not found` (observed here).
- `ps`/`pgrep`/`pkill` blocked in the Aside sandbox; use `lsof -t -i :PORT | xargs kill` and `lsof -t <logfile>` to find a nohup'd pid (observed here).
- Parallel bash calls race each other: a boot call started before its dependency finished extracting died with `No such file or directory` (observed here). Sequence dependency-heavy steps.
- **Cross-call process control is impossible from this sandbox:** a process started in an earlier bash call cannot be killed (`kill: (54463) - Operation not permitted`, observed here). Start every server under `capabilities/skills/agentic-systems-setup/scripts/bounded_run.sh 110 <cmd> &` and poll inside the same call; the runner's perl parent sends SIGTERM at the bound and SIGKILL 5 s later (verified 2026-09-28 on a Go temporal dev server started in an earlier call). Do not use `perl -e 'alarm shift; exec @ARGV'`: Go programs ignore SIGALRM, which is how three Temporal dev servers outlived their proofs (AS-19). Strays left for Mike's terminal: Kestra pid 54463 still listens on *:8080 (all interfaces) - `kill 54463`; the n8n on :4400 is locked by the parent (owner set, password discarded; unauthenticated calls return 401) - leave it alone.
- The OMP client pid 18982 attached to :8080 is **alive** - the kill attempts never reached it (observed 2026-09-28); cross-call kills are not permitted, so do not report such a kill as done.

## 14. Proof receipts

| Command | Exit | Observed | Date | Proof |
|---|---|---|---|---|
| `~/.homebrew/bin/colima version` | 0 | 0.10.3 (git commit 00f6c297) | 2026-09-28 | L1 |
| `PATH=$HOME/.homebrew/bin:$PATH ~/.homebrew/bin/colima status` | 1 | `level=fatal msg="colima is not running"` (14:45; no lima error once PATH is set) | 2026-09-28 | L1 |
| `PATH=$HOME/.homebrew/bin:$PATH ~/.homebrew/bin/lima --version` | 0 | `limactl version 2.1.3` | 2026-09-28 | L1 |
| earlier PATH probe (3 paths) + `find /` | 127/0 | CORRECTED: missed ~/.homebrew/bin; Colima was installed all along | 2026-09-28 | L0 |
| `docker context ls` | 0 | context `colima` active; client 29.6.1 | 2026-09-28 | L1 |
| `docker compose version` | 0 | v5.3.0 | 2026-09-28 | L1 |
| `docker info` | n/a | no Server section (daemon down) | 2026-09-28 | L0 |
| `curl -s -m 5 http://192.168.68.90:8011/v1/models` | 7 | Couldn't connect to server | 2026-09-28 | L0 |
