---
name: agentic-setup-temporal
description: "agentic-systems-setup sub-skill: set up Temporal for durable agent loops on Mike's Mac - Python SDK first, workflows and activities, local dev server via the temporal CLI, retries, signals/queries, schedules, and time-skipping tests - with the LLM/agent call inside a retryable activity. Start here when: 'set up Temporal', 'durable agent loop', 'Temporal workflow or activity', 'temporal server start-dev', 'time-skipping test', or any agentic-systems-setup job whose orchestrator is Temporal. JEV-FIRST MANDATE."
tags: [rig, agentic-systems, sub-skill, temporal, orchestrator, durable-execution, agent-loops]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: temporal
  extends: "agentic-env-probe, tool-temporal, tg-durable-ai-pipelines, provider-probe-first"
outcome: "A runnable Temporal workflow whose agent call lives in a retryable activity, proven with a fired retry and a live dev-server run, plus receipts. CLI is ~/.homebrew/bin/temporal 1.7.2; JDKs are ~/.homebrew/opt/openjdk@17, @21, and @26."
activation: "Load before the first temporalio install on this machine, and again whenever a workflow, activity, retry policy, signal, schedule, or time-skipping test is added or a durable agent loop is questioned."
instruction: "Probe first, install temporalio into a uv venv with PYTHONHOME unset under ~/.rig/agentic-lab/temporal, keep all I/O (LLM calls, files, network, clock) in activities with explicit RetryPolicy, prove determinism with WorkflowEnvironment.start_time_skipping(), and record every command and exit code in references/proof.json. Route typed judgments to rig-s1gate BEFORE any frontier LLM call; fail closed when the classifier is down."
applies_when:
  env: "Aside bash sandbox or an Orca terminal on Mike's Mac; lab dir ~/.rig/agentic-lab/temporal"
  runtime: "Python 3.10-3.13 uv venv (verified 3.12 here); temporalio Python SDK; temporal CLI 1.7.2 at ~/.homebrew/bin/temporal (Go binary, runs in-sandbox) for the dev server; JDKs 17/21/26 under ~/.homebrew/opt"
  deps: "uv; temporalio from PyPI; optional openai client for a real local model activity"
  params: "RetryPolicy(initial_interval, maximum_attempts); task queue name; workflow id"
  budget: "one workflow per agent loop; local dev server on ports 4300-4399; no paid API"
  scale: "single Mac, temporal server start-dev; not Temporal Cloud or a multi-node cluster"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - Probe the toolchain, the temporal CLI binary, and the local model endpoints.
  - Create the lab venv with PYTHONHOME unset and install temporalio.
  - Write the workflow as deterministic orchestration with all I/O in activities.
  - Give the agent activity an explicit RetryPolicy and prove it with a planted transient failure.
  - Run a time-skipping test to prove long-running timing without wall-clock waits.
  - Record commands, exit codes, versions, and proof level in references/proof.json.
done_when:
  - "cmd:env -u PYTHONHOME -u PYTHONPATH python3 -m rig_capabilities.skill_contract capabilities/skills/agentic-setup-temporal/SKILL.md"
  - "grep:capabilities/skills/agentic-setup-temporal/SKILL.md:Start here when"
  - "grep:capabilities/skills/agentic-setup-temporal/SKILL.md:rig-s1gate"
  - "file:capabilities/skills/agentic-setup-temporal/references/proof.json"
out_of_scope:
  - Temporal Cloud signup, login, namespace creation, or any cloud deploy (Gate-D)
  - paid API keys or paid model calls
  - editing repos or harness roots; installs stay in ~/.rig/agentic-lab/temporal
  - starting daemons owned by other workers (Docker/Colima)
---

# agentic-setup-temporal

Start here when: you are setting up Temporal as a durable orchestrator on this Mac, or putting an
LLM/agent call inside a durable workflow as a retryable activity.

JEV FIRST, binding on every setup and judgment step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier
LLM call; setup receipts are judged with `rig-s1gate check agentic.setup`. When the classifier is
unavailable: DEFER, never guess a verdict locally. FAIL CLOSED: a required signal passes only above
0.9; below that the gate does not advance and the setup step is held, not assumed good.

## Load surface

Always loaded at the start of every Temporal setup task: the `agentic-systems-setup` meta-family
routes here and an agent picks this skill at task start from its `description` and `Start here when`
triggers. It is a task-start surface, not a deep reference an agent must already know about; load
`references/` detail on demand, not up front.

## 1. When to choose it and when not

Choose Temporal when the agent loop must be *durable execution*: survive worker/process failure,
resume exactly where it left off, wait minutes-to-months (timers), and take external input via
signals/queries, with deterministic replay as the correctness guarantee. The LLM/agent call is an
**activity** with its own `RetryPolicy`; the workflow is pure deterministic orchestration.

The two nearest alternatives:
- **prefect** - choose Prefect instead when you want lighter Python flows/tasks with caching and a
  data-orchestration feel, and you do not need Temporal's durable timers, signals, or replay
  semantics. Faster to stand up; weaker at long-lived durable state machines.
- **trigger-dev** - choose Trigger.dev instead when you want durable step functions for AI jobs in
  a TypeScript-first, serverless-oriented runtime with per-step progress. Temporal is
  language-agnostic and self-hosted with a stronger execution model; Trigger.dev is DX-first.

Do not choose Temporal for simple scheduled batch DAGs (airflow, dagster) or browser-native
low-code (n8n, flowise). Existing design-harness doctrine lives in `capabilities/skills/tool-temporal`;
this skill is the general agentic-systems-setup route and defers to it for Design-Harness specifics.

## 2. Current version and sources

- **temporalio 1.33.0** - verified today from the PyPI JSON API
  (`https://pypi.org/pypi/temporalio/json`).
- Official docs fetched today: `https://docs.temporal.io/develop/python`,
  `https://docs.temporal.io/develop/python/core-application`, `https://docs.temporal.io/activities`,
  `https://docs.temporal.io/workflows`, `https://docs.temporal.io/testing/python`,
  `https://docs.temporal.io/self-hosted-guide`, `https://docs.temporal.io/cli`.
- PyPI: `https://pypi.org/project/temporalio/`.
- Reference skill: `capabilities/skills/tool-temporal` (temporalio 1.33.0 pinned for Design Harness).

## 3. Environment route and prerequisites

- **Route: Aside bash sandbox, uv venv** for the SDK and workflow code, plus the **temporal CLI dev
  server**, which RUNS in-sandbox. Homebrew lives at `~/.homebrew` (NOT on the default PATH): the CLI
  is `~/.homebrew/bin/temporal` (1.7.2, Go binary - runs here, verified) and JDKs 17/21/26 are under
  `~/.homebrew/opt/openjdk@{17,21,26}`. Verified 2026-09-28: `~/.homebrew/bin/temporal` is 1.7.2; `openjdk@17/bin/java` is 17.0.20.1;
  `openjdk@21/bin/java` is 21.0.12; `openjdk@26/bin/java` is 26.0.2. They are installed. A bare
  PATH probe misses them. That is a PATH miss, not an absent install.
- PATH prefix `PATH="$HOME/.homebrew/bin:$HOME/.local/bin:/usr/local/bin:$PATH"`.
- `env -u PYTHONHOME -u PYTHONPATH` for every Python invocation (the Aside runtime leaks both).
- Prerequisites: `uv`, Python 3.12 (3.12.12 here). temporalio installs pure-Python + wheels; import
  verified in a uv venv here.
- Lab dir `~/.rig/agentic-lab/temporal`; keep any state/config there, never in a repo.
- Run `capabilities/skills/agentic-env-probe/scripts/env_probe.py` first; it reports whether the
  `temporal` CLI is present and runnable.

## 4. Install (exact commands)

```bash
export PATH="$HOME/.homebrew/bin:$HOME/.local/bin:/usr/local/bin:$PATH"
mkdir -p ~/.rig/agentic-lab/temporal && cd ~/.rig/agentic-lab/temporal
env -u PYTHONHOME -u PYTHONPATH uv venv .venv --python 3.12
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python temporalio
env -u PYTHONHOME -u PYTHONPATH .venv/bin/python -c "import temporalio; import importlib.metadata as m; print(m.version('temporalio'))"
```

Expected: `1.33.0`. The Temporal CLI is ALREADY installed here at `~/.homebrew/bin/temporal`
(`temporal version 1.7.2`, Server 1.31.1, UI 2.49.1) and runs in-sandbox - no `brew install` needed.
Start your OWN dev server on a free port in 4300-4399. Do not reuse a port another process
already holds (4350/4351 and 7233 were already taken here). Example that ran:
`~/.homebrew/bin/temporal server start-dev --port 4360 --ui-port 4361 --ip 127.0.0.1 --db-filename ~/.rig/agentic-lab/temporal/dev-a3b.db --namespace default`.
Do NOT touch Mike's server (pid 7353 on 127.0.0.1:7233). Point the worker at the port you bound.

## 5. Local-first model wiring for the agent step

No paid keys. The agent **activity** calls an OpenAI-compatible **local** base URL. Endpoints
verified answering here: `http://127.0.0.1:8771/v1` (qwen3.8-uncensored:27b) and
`http://127.0.0.1:8657/v1` (MiMo-V2.6-Flash-RL-MLX-4bit-MTP). Blackwell `192.168.68.90:8011/:8111`
do NOT answer from this sandbox. All I/O - including the LLM call and any clock read - belongs in
the activity, never in the workflow body.

```python
@activity.defn
async def call_model(prompt: str) -> str:
    client = OpenAI(base_url="http://127.0.0.1:8771/v1", api_key="not-needed-local")
    r = client.chat.completions.create(
        model="qwen3.8-uncensored:27b",
        messages=[{"role": "user", "content": prompt}],
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )
    text = r.choices[0].message.content
    assert text, "empty content from local model"
    return text
```

qwen at `127.0.0.1:8771` returns HTTP 200 with EMPTY content when thinking is on - disable it as
above and assert non-empty. Never call a paid API.

## 6. Secrets

Reference keychain item names, never values: `com.rig.env.<NAME>`. Local endpoints use a
placeholder key ("not-needed-local"); any real secret is exported from the keychain at worker
startup, never in workflow/activity source and never committed. Temporal's own config is
`temporal` CLI flags / env (e.g. namespace, address); a real secret goes in worker env or a secret
store, never into a repo or `references/`.

## 7. Hello-world

`~/.rig/agentic-lab/temporal/hello_temporal.py` - a deterministic `@workflow.defn` that calls a
retryable `@activity.defn` agent step (deterministic fake model, planted transient failure on
attempt 1):

```python
from temporalio import workflow, activity
from temporalio.common import RetryPolicy
with workflow.unsafe.imports_passed_through():
    from datetime import timedelta

@activity.defn
async def call_model(prompt: str) -> str:
    if _ATTEMPTS["model_call"] == 1:
        raise RuntimeError("PLANTED_TRANSIENT: model endpoint 503 (simulated)")
    return f"fake-llm answer to: {prompt!r}"

@workflow.defn
class AgenticHelloWorkflow:
    @workflow.run
    async def run(self, prompt: str) -> str:
        return await workflow.execute_activity(
            call_model, prompt,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=1), maximum_attempts=3),
        )
```

Run against a dev server (worker + starter) or run the offline unit test below. Expected: the
retry fires (attempt 1 fails, attempt 2 succeeds) and the workflow returns the fake answer.

## 8. Durable and production features

- **Retries:** `RetryPolicy(initial_interval, backoff, maximum_attempts)` on the activity call.
  Retryability and idempotency are separate - a retried side effect needs its own idempotency key.
- **Durable timers / long waits:** `workflow.sleep(timedelta(...))` - a workflow can wait months
  and resume; this is what Prefect/Trigger.dev do not give you at the same strength.
- **Signals / queries (human-in-the-loop):** `@workflow.signal` to inject approval mid-run,
  `@workflow.query` to read state - the durable equivalent of a human gate.
- **Schedules:** `temporal schedule create` or the SDK ScheduleClient; cron + interval + jitter.
- **Concurrency / state:** task queues, worker slots, workflow state via queries; replay-safe
  determinism is the state guarantee.
- **Continue-As-New / child workflows** for very long agent loops.

## 9. Observability

- Temporal Web UI ships with the dev server: `temporal server start-dev` then
  `http://127.0.0.1:8233` (dev default) or a 4300-4399 port via `--ui-port`. Event histories,
  activity attempts, and retries are visible per workflow execution.
- Logs: `activity.logger` / workflow logger; run `temporal workflow show <workflow-id>` for the
  event history. Health: `curl -s -m 5 http://127.0.0.1:<port>/` (UI) or the gRPC endpoint.
- In-sandbox: start the dev server in a self-destructing call and poll its UI port (see gotchas).

## 10. Testing

- **Deterministic fake LLM:** the activity returns a fixed string, no network (section 7).
- **Unit test with time-skipping:** `WorkflowEnvironment.start_time_skipping()` proves a
  month-long `workflow.sleep` completes instantly and deterministically - the canonical Temporal
  test (`https://docs.temporal.io/testing/python`).
- **One planted failure that goes red:** assert the retry recovers from `PLANTED_TRANSIENT`; then
  set `maximum_attempts=1` (or always-raise) and show the test FAILS (red); restore to green.
  A green test that cannot go red is theater - record the red run in `references/proof.json`.
- Replay test: `WorkflowWorker.replayer` over a saved history to prove determinism.

## 11. Deploy / self-host and Gate-D

Self-host is default and NOT gated: `temporal server start-dev` runs entirely on this Mac with a
local worker. **Gate-D - do NOT do without Mike:** Temporal Cloud signup/login, namespace creation
on a cloud account, deploying a worker to Temporal Cloud, paid plans, or any public URL. This
skill does none of them.

## 12. Teardown and upgrade

- Upgrade: `env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python -U temporalio`,
  re-run section 7 and the time-skipping test, re-verify the version. Pin a compatible CLI if the
  server is version-sensitive.
- Teardown: stop the dev server/worker you started (self-destructing call; `lsof -t -i :PORT |
  xargs kill` ONLY for a port you bound in the same call), then `rm -rf ~/.rig/agentic-lab/temporal`.

## 13. Gotchas

- **[observed here] PYTHONHOME/PYTHONPATH leakage** - always `env -u PYTHONHOME -u PYTHONPATH`.
- **[observed here] process control across bash calls** - a server started in one call cannot be
  killed from a later call ("Operation not permitted"). `perl -e 'alarm shift; exec @ARGV'` does
  not reap the Go dev server after exec: Go catches and ignores SIGALRM (observed: pids 35550,
  68400 and 25385 still listened after their alarms). Start the dev server under
  `capabilities/skills/agentic-systems-setup/scripts/bounded_run.sh 110 temporal server start-dev --port 4350 --ui-port 4351 &` instead: its perl parent sends
  SIGTERM at the bound, and a dev server started that way in one call was gone (port closed) when a
  later call checked, twice on 2026-09-28. Same-call kill also works (4380 closed, exit 0).
- **[observed here] Blackwell LAN model endpoints unreachable** - `192.168.68.90:8011` exit 7,
  `:8111` exit 28; only `127.0.0.1:8771` and `127.0.0.1:8657` answer. Probe first.
- **[observed here] qwen thinking mode = 200 + empty content** at `127.0.0.1:8771`; disable via
  `chat_template_kwargs.enable_thinking=false` and assert non-empty.
- **[docs: https://docs.temporal.io/workflows] workflow code must be deterministic** - no system
  time, randomness, file/network I/O, or subprocess in the workflow body; put it all in activities,
  or replay breaks. Use `workflow.now()`/`workflow.sleep()` for time and
  `workflow.unsafe.imports_passed_through()` for module imports of I/O libs.
- **[observed here] the temporal CLI RUNS in-sandbox** - `~/.homebrew/bin/temporal` (1.7.2) is a Go
  binary that executes fine here (unlike PyInstaller single-file binaries, which fail with semaphore
  errno 1). Homebrew is at `~/.homebrew`, NOT on the default PATH - a bare `which temporal` or `java -version` misses them because they are not on the default PATH.
  Installed paths: `~/.homebrew/bin/temporal` (1.7.2); `~/.homebrew/opt/openjdk@17/bin/java`
  (17.0.20.1); `openjdk@21/bin/java` (21.0.12); `openjdk@26/bin/java` (26.0.2). No
  `~/.homebrew/bin/java` symlink. Do not report the CLI or these JDKs as absent.
- **[observed here] `WorkflowEnvironment.start_time_skipping()` still needs its own test server**
  (a Java jar) and can time out (`Failed starting test server ... did not start within 5s`). Run the
  LIVE path against your own `temporal server start-dev` instead (section 4) - that proved L2/L3/L4 here.
- **[observed here] L3 model route is 127.0.0.1:8657** - model id `MiMo-V2.6-Flash-RL-MLX-4bit-MTP`.
  A 2026-09-28 activity call returned `content='PONG'` (non-empty). `192.168.68.90:8111` did not
  answer from this sandbox. Assert non-empty content; do not cite the LAN box as the working route.

## 14. Proof receipts

| Step | Command | Exit code | Version | Date | Proof level |
|---|---|---|---|---|---|
| Install | `uv pip install --python .venv/bin/python temporalio` | 0 | temporalio 1.33.0 | 2026-09-28 | L1 |
| Version | `python -c "import importlib.metadata as m; m.version('temporalio')"` | 0 | 1.33.0 | 2026-09-28 | L1 |
| Own dev server (CLI 1.7.2) | `~/.homebrew/bin/temporal server start-dev --port 4360 --ui-port 4361 --ip 127.0.0.1 --db-filename ~/.rig/agentic-lab/temporal/dev-a3b.db` + `temporal operator cluster health --address 127.0.0.1:4360` | 0 - UI up in 2s, cluster `SERVING` | Server 1.31.1 | 2026-09-28 | L1 |
| L3 real local model activity | `env -u PYTHONHOME -u PYTHONPATH .venv/bin/python run_a3b_live.py l3` against `http://127.0.0.1:8657/v1` model `MiMo-V2.6-Flash-RL-MLX-4bit-MTP` | 0 - `L3_RESULT: 'PONG'`, `TEMPORAL_L3_OK` | 1.33.0 | 2026-09-28 | L3 |
| L4 planted retry then success | `run_a3b_live.py l4` | 0 - `L4_ATTEMPTS: 2`, `L4_RESULT: 'PONG'`, `TEMPORAL_L4_OK` | 1.33.0 | 2026-09-28 | L4 |
| Planted failure meant to be RED | `run_a3b_live.py red` (`maximum_attempts=1`) | 1 - `PLANTED_FAILURE_RED_OK`, `RED_ATTEMPTS: 1` | 1.33.0 | 2026-09-28 | L4 red |
| Offline retry contract | `.venv/bin/python test_temporal_offline.py` | 0 - `RETRY_CONTRACT_OK attempts=2`, `PLANTED_FAILURE_RED_OK` | 1.33.0 | 2026-09-28 | L2-logic |
| `start_time_skipping()` test env | `hello_temporal.py` | 1 - `Failed starting test server ... did not start within 5s` | 1.33.0 | 2026-09-28 | blocked (needs its Java test server; use the live path above) |
| Deploy / Cloud | Gate-D - not done | - | - | - | L5 not attempted |

Full machine-readable receipts: `capabilities/skills/agentic-setup-temporal/references/proof.json`.
