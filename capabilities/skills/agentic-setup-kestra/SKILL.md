---
name: agentic-setup-kestra
description: "Agentic Systems Setup: Kestra on Mike's Mac - declarative YAML flows with typed tasks, namespaces, inputs/outputs, schedule and event triggers, secrets, plugin tasks (scripts, HTTP, JDBC, AI/agent plugins from Maven Central), run via the standalone Java distribution or Docker. Use when Mike wants scheduled or event-driven batch/ops orchestration with git-friendly YAML, not a visual app builder. JEV-FIRST MANDATE."
when_to_use: "Kestra, YAML flow, orchestration, scheduler, namespace, Kestra API, Kestra plugin. JEV-FIRST MANDATE: route typed judgments to rig-s1gate before any frontier model; DEFERRED when the classifier is down."
tags: [rig, agentic-systems-setup, kestra, yaml, orchestration, scheduling, java]
metadata:
  family: agentic-systems-setup
  tier: framework
  siblings: "agentic-setup-dify, agentic-setup-flowise, agentic-setup-langflow, agentic-selfhost-docker"
outcome: "A Kestra server running from the lab dir whose hello_world flow (a Log task, no model) executes through the REST API and returns a SUCCESS execution receipt, with secrets and defaults rotated."
activation: "JEV-FIRST MANDATE, findable at task start: route typed judgments to rig-s1gate before any frontier model; DEFERRED is the only answer when the classifier is down. Load for any request to author, run, schedule or operate Kestra flows, namespaces, triggers, secrets or plugins, or to run its standalone Java or Docker distribution."
instruction: "JEV FIRST, findable at start: run ./bin/rig-s1gate check doctrine.surface BEFORE any frontier model; PASS continues, ESCALATE rewrites, BLOCK stops, DEFERRED fails closed. Then: verify the Java major version the release actually needs before booting; keep flows in references/ as YAML and prove them by execution receipts, not by file writes."
applies_when:
  env: "Mike's Mac, local-only; Aside sandbox bash or host shell"
  runtime: "Standalone Java distribution (Temurin JRE in the lab dir) or Docker via agentic-selfhost-docker"
  deps: "A JRE matching the release's class-file level (2.0.3 needs Java 25); 2 vCPU / 4 GiB minimum (docs)"
  params: "host port 4530 (lab range 4500-4599); H2/local storage under ~/.rig/agentic-lab/kestra"
  budget: "one instance; teardown after proof"
  scale: "single-node local server; not the distributed/K8s topology"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - JEV FIRST, findable at task start: route every typed judgment to rig-s1gate (Jev) via ./bin/rig-s1gate check doctrine.surface BEFORE any frontier model call; DEFERRED when the classifier is down, fail closed.
  - Verify the release tag and the Java major its bytecode requires; download JRE and binary with checksums into the lab dir.
  - Boot the server (server local for embedded lab use) on a lab port and probe its API.
  - Create the hello_world flow via POST /api/v1/flows with application/x-yaml.
  - Execute it, read the execution back, and record the state transition as the receipt.
  - Rotate default credentials, then stop the server and tear down the lab dir state.
done_when:
  - "grep:capabilities/skills/agentic-setup-kestra/SKILL.md:io.kestra.plugin.core.log.Log"
  - "grep:capabilities/skills/agentic-setup-kestra/SKILL.md:application/x-yaml"
  - "grep:capabilities/skills/agentic-setup-kestra/SKILL.md:Gate-D"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/agentic-setup-kestra/SKILL.md"
out_of_scope:
  - Kestra Cloud signup, Enterprise API tokens, paid plans (Gate-D)
  - paid model APIs inside flows (local endpoints only)
  - production/Kubernetes deploys, public URLs, tunnels (Gate-D)
---

# agentic-setup-kestra

JEV FIRST, binding on every Kestra-setup decision: an agent whose only context is this excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM call; receipts are judged with `rig-s1gate check doctrine.surface`. When the classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9; below that the gate does not advance.

## Load surface

Always loaded at the start of every agentic-systems-setup task: the agentic-systems-setup family routes here before the first install, start or teardown command. It is a task-start surface, not a deep reference an agent must already know about. Typed judgments it forces: is this flow valid; did the execution really reach SUCCESS (not just queue); is this error BLOCKED (environment) or FAILED (it ran and failed).


## 1. When to choose it and when not

Choose Kestra when the deliverable is **declarative, git-friendly, scheduled or event-driven orchestration**: cron/webhook triggers, typed inputs/outputs, namespaces, retries, and task plugins (shell/Python scripts, HTTP, JDBC, and AI/agent plugins from Maven Central). Do not choose it when the deliverable is a visual LLM app or chatbot - the two nearest alternatives are **dify** (app platform with RAG knowledge bases and per-app APIs) and **langflow** (visual Python flows with custom components). Pick Kestra over those when the unit of work is a pipeline with a schedule, not an app.

## 2. Current version and sources

Verified 2026-09-28:
- **Kestra v2.0.3** (GitHub latest release, published 2026-09-22; `https://api.github.com/repos/kestra-io/kestra/releases/tags/v2.0.3`).
- Release assets verified: `kestra-2.0.3` (130,371,660 bytes, sha256 `b4b4518a617f93965dcf98c9673beda3dad2b6d9d1780ad8b9a945e437975ab4`, matches the release's `checksums_sha256.txt` - `shasum -c` returned OK) and `checksums_sha256.txt`.
- Docs fetched today: https://kestra.io/docs/installation (min 2 vCPU / 4 GiB) and https://kestra.io/docs/installation/docker (commands `kestra/kestra:latest[-slim] server standalone|server local`, port 8080, `repository.type: postgres`, `queue.type: postgres`, `storage.type: local`, `kestra.server.basic-auth` example `admin@kestra.io` / `kestra`).
- Flow schema + API verified today from kestra.io pages: https://kestra.io/docs/tutorial/fundamentals (flow = `id`, `namespace`, `tasks`), https://kestra.io/plugins/core/log/io.kestra.plugin.core.log.log (`io.kestra.plugin.core.log.Log`), https://kestra.io/docs/how-to-guides/api (POST flows with `Content-Type: application/x-yaml`, POST `/api/v1/executions/{namespace}/{id}`, optional Basic Auth `-u 'admin@kestra.io:kestra'`).

## 3. Environment route and prerequisites

- **Standalone Java route (primary here):** a Temurin JRE untarred into `~/.rig/agentic-lab/kestra/` (no sudo, nothing system-wide) plus the release binary `kestra-2.0.3` run with `java -jar kestra-2.0.3 server local`.
- **Docker route:** `kestra/kestra:latest server standalone` with the config file from the docker docs, via agentic-selfhost-docker (BLOCKED here 2026-09-28: Colima 0.10.3 in ~/.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.3`); Colima's "lima not found" was a PATH artifact - the fix is PATH, never `brew install lima`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`.
- Prerequisites (docs): 2 vCPU, 4 GiB RAM minimum. **Java level is release-specific - verify, do not assume:** 2.0.3's bytecode is class-file version 69 = **Java 25** (observed: Temurin 21 rejected it with `UnsupportedClassVersionError ... up to 65.0`).
- The bare `kestra-2.0.3` binary delegates to `java` on PATH and dies with macOS's `Unable to locate a Java Runtime` stub when none is installed (observed here).
- **Java 25+ options (both verified 2026-09-28):** the downloaded lab JRE (Temurin 25.0.4.1+1, section 4) OR Homebrew's JDK 26 - `~/.homebrew/opt/openjdk@26/bin/java -version` -> `openjdk version "26.0.2"` (Homebrew lives at ~/.homebrew). Homebrew's openjdk@21 (21.0.12) and openjdk@17 (17.0.20.1) are too old for 2.0.3's class-file 69.

## 4. Install (exact, pinned)

```bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
mkdir -p ~/.rig/agentic-lab/kestra && cd ~/.rig/agentic-lab/kestra
curl -fsSL -o kestra-2.0.3 https://github.com/kestra-io/kestra/releases/download/v2.0.3/kestra-2.0.3
curl -fsSL -o checksums_sha256.txt https://github.com/kestra-io/kestra/releases/download/v2.0.3/checksums_sha256.txt
shasum -a 256 -c checksums_sha256.txt                       # must print "kestra-2.0.3: OK"
curl -fsSL -o temurin-jre25.tar.gz "https://api.adoptium.net/v3/binary/latest/25/ga/mac/aarch64/jre/hotspot/normal/eclipse"
tar -xzf temurin-jre25.tar.gz                                # -> jdk-25.x.y-jre/
./jdk-25*/Contents/Home/bin/java -jar kestra-2.0.3 server local
```

Pins verified this session: binary v2.0.3 with the sha256 above; Temurin JRE 25.0.4.1+1 (sha256 `5b02bcc908da092e7e00b9772d4f9bbb87f44a60b7c90f7cf5a91a1d98f37e1b`). Note `server local` (embedded, quickstart) versus `server standalone` (needs the repository/queue/storage config from the docs).

## 5. Local-first model wiring

For AI/agent task plugins, point the plugin's model config at a local OpenAI-compatible endpoint (`http://192.168.68.90:8011/v1` - use the LAN IP, and probe with `curl -s -m 5 <base>/models` first). On 2026-09-28 Local OpenAI-compatible endpoints verified ANSWERING from this sandbox on 2026-09-28: http://127.0.0.1:8771/v1 (model qwen3.8-uncensored:27b; disable thinking or the content comes back empty) and http://127.0.0.1:8657/v1 (model MiMo-V2.6-Flash-RL-MLX-4bit-MTP). The Blackwell LAN endpoints http://192.168.68.90:8011/v1 and :8111/v1 refuse (curl exit 7). Probe first: `curl -s -m 5 <base>/models`. From containers use the host LAN address of these same servers; never a paid key. Plugin coordinates install with `kestra plugins install <group>:<artifact>:<version>` (pattern verified in the fetched docker docs Dockerfile: `io.kestra.plugin:plugin-aws:LATEST`); look up the exact AI-plugin artifact on https://kestra.io/plugins at use time rather than trusting a remembered id.

## 6. Secrets

Reference secrets in flows as `{{ secret('NAME') }}` (verified pattern, kestra.io blueprint page) and store them in Kestra's namespace secret store (UI/API) - never in YAML. Keychain names for the machine side: `com.rig.env.KESTRA_BASIC_AUTH_PW`, `com.rig.env.OPENAI_API_KEY_LOCAL`. **Change every default:** the docs' config example ships `kestra.server.basic-auth` with `username: admin@kestra.io`, `password: kestra` (observed in fetched docs) - rotate before any non-loopback exposure.

## 7. Hello-world

references/hello_world.yaml (also the official README's first flow, verified today):

```yaml
id: hello_world
namespace: dev
tasks:
  - id: say_hello
    type: io.kestra.plugin.core.log.Log
    message: "Hello, World!"
```

Create + execute via API (no model, deterministic):

```bash
curl -X POST http://127.0.0.1:4530/api/v1/flows -H "Content-Type: application/x-yaml" --data-binary @references/hello_world.yaml
curl -X POST http://127.0.0.1:4530/api/v1/executions/dev/hello_world
# then GET /api/v1/executions/<id> -> state.current == SUCCESS
```

Expected output: a JSON execution object, then `{"state": {"current": "SUCCESS"}}` with the log line `Hello, World!` in the task logs.

## 8. Durable and production features

Namespaces (project/env isolation), typed `inputs` with defaults, task outputs passed between tasks, `labels`, `triggers:` (`io.kestra.plugin.core.trigger.Schedule` with `cron`), retries, `pluginDefaults`, quotas, and namespace files (upload via `POST /api/v1/namespaces/{ns}/files`, verified in the API guide). Back up the H2/repository db and `storage` dir before upgrades.

## 9. Observability

Execution Gantt/log views in the UI at :8080, `GET /api/v1/executions/{id}` state transitions and durations, per-task logs. An execution object returned by POST is queued, not done - wait for `state.current: SUCCESS` before claiming anything.

## 10. Testing

Deterministic test = execute `hello_world` and assert `state.current == SUCCESS` and the log message is present. **Planted failure:** create a copy of the flow with a typo'd task type (`io.kestra.plugin.core.log.Logg`); flow creation/validation must go red with a task-type validation error. If it stays green, the check is theater. Restore, and record both receipts in references/proof.json.

## 11. Deploy / self-host hardening and Gate-D

Bind to 127.0.0.1, enable `kestra.server.basic-auth` with a rotated password, keep `server local` storage under the lab dir, and do not mount `/var/run/docker.sock` unless a flow truly needs Docker-in-Docker (the docs' docker run does mount it - that is root-equivalent on the host). **Gate-D (do not without Mike's explicit approval):** Kestra Cloud signup, Enterprise API tokens, plugin installs that download externally at run time in production, deploys (K8s/VM), pushes, paid plans, public URLs or tunnels.

## 12. Teardown and upgrade

Stop the server with `lsof -t -i :4530 | xargs kill`; confirm port closed (curl exit 7). Upgrade = download the new release binary + checksums, re-verify the Java major it needs (it changed between lines before), back up `~/.../kestra` storage/db, re-apply config changes onto the new release's example. Delete the lab dir when the proof is archived.

## 13. Gotchas

- **Java level is per-release and undocumented in the binary name:** 2.0.3 needs Java 25 (class-file 69); Java 21 fails with `UnsupportedClassVersionError` (observed here 2026-09-28). Download the JRE the release needs, not the one a plan assumed.
- `server standalone` refuses to boot without explicit `kestra.repository.type`, `kestra.queue.type`, `kestra.storage.type` - observed error: `Incomplete server configuration - missing required properties`. The quickstart's embedded route is `server local` (fetched docs, 2026-09-28).
- The docs' docker command mounts `/var/run/docker.sock` and runs `--user=root` (fetched docs) - that is host-root-equivalent; do not copy it into a hardened setup.
- macOS has no `timeout(1)` and the sandbox blocks `ps/pgrep` (observed here) - use `nohup ... &` polling and `lsof -t -i :PORT | xargs kill` (which only works inside the same bash call).
- **Cross-call kills are impossible here:** a Kestra started in one bash call cannot be killed from a later one (`kill: (54463) - Operation not permitted`, observed). Start it under the bounded runner, e.g. `capabilities/skills/agentic-systems-setup/scripts/bounded_run.sh 110 ../jdk-25*/Contents/Home/bin/java -jar ../kestra-2.0.3 server local &`, and poll within that call (the runner sends SIGTERM at the bound; the older alarm-and-exec form is unreliable for non-Python servers, AS-19). Stray instance: the Kestra started during authoring (pid 54463) still holds :8080 - Mike stops it from a normal terminal with `kill 54463`.

## 14. Proof receipts

| Command | Exit | Observed | Date | Proof |
|---|---|---|---|---|
| `curl .../releases/tags/v2.0.3` | 0 | tag v2.0.3, assets `kestra-2.0.3` + checksums | 2026-09-28 | L0 |
| `shasum -a 256 -c checksums_sha256.txt` | 0 | `kestra-2.0.3: OK` (b4b4518a...) | 2026-09-28 | L1 |
| `java -jar kestra-2.0.3 server standalone` (Temurin 21) | 1 | `UnsupportedClassVersionError ... class file version 69.0 ... up to 65.0` | 2026-09-28 | L1 |
| `java -jar kestra-2.0.3 server standalone` (Temurin 25) | 1 | `Incomplete server configuration - missing required properties` | 2026-09-28 | L1 |
| `java -jar kestra-2.0.3 server local` (Temurin 25) | see proof.json | boot + hello flow receipts recorded there | 2026-09-28 | up to L2 |
