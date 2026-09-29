---
name: agentic-setup-prefect
description: "agentic-systems-setup sub-skill: set up Prefect 3 end to end on Mike's Mac - flows, tasks, local server, work pools, deployments, schedules - with an LLM/agent step living inside the flow carrying retries, caching/idempotency and observability. Start here when: 'set up Prefect', 'Prefect flow', 'Prefect work pool or deployment or schedule', 'run an LLM call as a Prefect task', 'agent step inside Prefect', or any agentic-systems-setup job whose orchestrator is Prefect. JEV-FIRST MANDATE."
tags: [rig, agentic-systems, sub-skill, prefect, orchestrator, workflows, llm-tasks]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: prefect
  extends: "agentic-env-probe, provider-probe-first, app-data-layer, tool-temporal"
outcome: "A runnable Prefect flow whose agent step is a task with a fired retry, a cache policy, and a run visible in the local API/UI - plus receipts naming exactly what ran and what was BLOCKED."
activation: "Load before the first prefect install command on this machine, and again whenever a flow, work pool, deployment, schedule, or an LLM/agent task is added or its retry/caching is questioned."
instruction: "Probe the environment and model routes first, install into a uv venv with PYTHONHOME unset under ~/.rig/agentic-lab/prefect, wrap the agent step in a @task with an explicit retry policy and cache policy, prove the retry with a planted transient failure, and record every command and exit code in references/proof.json. Route typed judgments to rig-s1gate BEFORE any frontier LLM call; fail closed when the classifier is down."
applies_when:
  env: "Aside bash sandbox or an Orca terminal on Mike's Mac; lab dir ~/.rig/agentic-lab/prefect with PREFECT_HOME set there"
  runtime: "Python 3.10-3.13 uv venv (verified 3.12 here), Prefect 3.x API and CLI"
  deps: "uv; prefect from PyPI; optional openai client for a real local model step"
  params: "retries and retry_delay_seconds per task; cache_key_fn policy; work pool and deployment names"
  budget: "one flow per agent pipeline; local server on ports 4300-4399; no paid API"
  scale: "single Mac, local server and local worker; not a multi-tenant Prefect Cloud estate"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - Probe the toolchain and the local model endpoints; record which answered.
  - Create the lab venv with PYTHONHOME and PYTHONPATH unset and install prefect.
  - Write the flow with the agent step as a @task carrying retries and a cache policy.
  - Run the flow with a deterministic fake model step and a planted transient failure to prove the retry fires.
  - Start the local server on a 4300-4399 port in a self-destructing call and poll its health URL.
  - Record commands, exit codes, versions, and proof level in references/proof.json.
done_when:
  - "cmd:env -u PYTHONHOME -u PYTHONPATH python3 -m rig_capabilities.skill_contract capabilities/skills/agentic-setup-prefect/SKILL.md"
  - "grep:capabilities/skills/agentic-setup-prefect/SKILL.md:Start here when"
  - "grep:capabilities/skills/agentic-setup-prefect/SKILL.md:rig-s1gate"
  - "file:capabilities/skills/agentic-setup-prefect/references/proof.json"
out_of_scope:
  - Prefect Cloud signup, login, or any cloud workspace (Gate-D: never without Mike)
  - paid API keys or paid model calls
  - editing repos or harness roots; installs stay in ~/.rig/agentic-lab/prefect
  - starting daemons owned by other workers (Docker/Colima)
---

# agentic-setup-prefect

Start here when: you are setting up Prefect 3 as an orchestrator on this Mac, or putting an
LLM/agent step inside a Prefect flow with retries, caching and observability.

JEV FIRST, binding on every setup and judgment step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier
LLM call; setup receipts are judged with `rig-s1gate check agentic.setup`. When the classifier is
unavailable: DEFER, never guess a verdict locally. FAIL CLOSED: a required signal passes only above
0.9; below that the gate does not advance and the setup step is held, not assumed good.

## Load surface

Always loaded at the start of every Prefect setup task: the `agentic-systems-setup` meta-family
routes here and an agent picks this skill at task start from its `description` and `Start here when`
triggers. It is a task-start surface, not a deep reference an agent must already know about; load
`references/` detail on demand, not up front.

## 1. When to choose it and when not

Choose Prefect when you want Python-native flows and tasks with per-task retries, caching,
scheduling and a local UI, and the unit of work is data/agent steps rather than a long-lived
durable state machine. The agent step is just a `@task`, so an LLM call with its own retry policy
drops straight in.

The two nearest alternatives:
- **dagster** - choose Dagster instead when the primary mental model is *assets and lineage*
  (software-defined assets, partitions, materializations) rather than imperative flow code. Prefect
  is flow/task-first; Dagster is asset-first.
- **airflow** - choose Airflow instead when you need the incumbent scheduler/executor ecosystem,
  many provider hooks, and DAGs scheduled by a central scheduler with heavy operator libraries.
  Prefect is lighter and more Pythonic; Airflow is more entrenched for pure scheduled batch.

Do not choose Prefect when you need Temporal-grade durable execution with signals/queries and
replay across months of wall time (see `agentic-setup-temporal`), or when you want a
browser-native low-code builder (n8n, flowise, langflow).

## 2. Current version and sources

- **prefect 3.8.7** - verified today from the PyPI JSON API (`https://pypi.org/pypi/prefect/json`)
  and identical to the version installed in this lab venv.
- Official docs fetched today: `https://docs.prefect.io/v3/get-started/index`,
  `https://docs.prefect.io/v3/tutorial/flows`, `https://docs.prefect.io/v3/concepts/flows`,
  `https://docs.prefect.io/v3/concepts/tasks`, `https://docs.prefect.io/v3/concepts/schedules`,
  `https://docs.prefect.io/v3/concepts/work-pools`.
- PyPI project: `https://pypi.org/project/prefect/`.

## 3. Environment route and prerequisites

- **Route: Aside bash sandbox, uv venv** (verified working here). Host shell (Orca terminal) is
  the fallback if a native extension fails library validation.
- Bash PATH lacks `~/.local/bin` and `/usr/local/bin`: prefix
  `PATH="$HOME/.local/bin:/usr/local/bin:$PATH"` before every call.
- The Aside runtime exports `PYTHONHOME` and `PYTHONPATH`; unset them for any other Python:
  `env -u PYTHONHOME -u PYTHONPATH uv venv .venv --python 3.12` then
  `env -u PYTHONHOME -u PYTHONPATH .venv/bin/python ...`.
- Prerequisites: `uv` (0.12.19 here), Python 3.12 (3.12.12 here). Native Python wheels import fine
  in a uv venv here (pydantic-core verified).
- Set `PREFECT_HOME` to `~/.rig/agentic-lab/prefect/home` so no state lands in a repo or `~/.prefect`.
- Run the environment probe first: `capabilities/skills/agentic-env-probe/scripts/env_probe.py`.

## 4. Install (exact commands)

```bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
mkdir -p ~/.rig/agentic-lab/prefect && cd ~/.rig/agentic-lab/prefect
env -u PYTHONHOME -u PYTHONPATH uv venv .venv --python 3.12
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python prefect
env -u PYTHONHOME -u PYTHONPATH .venv/bin/python -c "import prefect; print(prefect.__version__)"
```

Observed here: `prefect 3.8.7`. Do not `pip install` into a system Python and never into a repo.

## 5. Local-first model wiring for the agent step

No paid keys. The agent step points at an OpenAI-compatible **local** base URL. Endpoints verified
answering from this sandbox: `http://127.0.0.1:8771/v1` (qwen3.8-uncensored:27b) and
`http://127.0.0.1:8657/v1` (MiMo-V2.6-Flash-RL-MLX-4bit-MTP). The Blackwell LAN endpoints
`http://192.168.68.90:8011/v1` and `:8111/v1` do NOT answer from this sandbox (observed:
8011 exit 7 connection refused; 8111 exit 28 timeout).

```python
import os
from openai import OpenAI
client = OpenAI(base_url=os.environ.get("MODEL_BASE_URL", "http://127.0.0.1:8771/v1"),
                api_key=os.environ.get("MODEL_API_KEY", "not-needed-local"))
```

For qwen3.8-uncensored at `127.0.0.1:8771`, thinking mode returns HTTP 200 with EMPTY content -
disable it: `extra_body={"chat_template_kwargs": {"enable_thinking": false}}`, and assert the
returned content is non-empty. Never call a paid API from this skill.

## 6. Secrets

Reference macOS keychain item names, never values: `com.rig.env.<NAME>`. For a local endpoint the
API key is a placeholder ("not-needed-local"); if a real secret is ever needed it lives in the
keychain and is exported at runtime, never committed. Prefect's own block/variable store
(`prefect block`, `prefect variable`, work-pool base job template `job_configuration`) is where
orchestrator-side config goes - real values never enter a repo, a flow file, or `references/`.

## 7. Hello-world

`~/.rig/agentic-lab/prefect/hello_prefect.py` (written and run here) - a flow with the agent step
as a `@task(retries=2, retry_delay_seconds=1, cache_key_fn=TASK_SOURCE)` that raises a planted
transient failure on attempt 1 and returns a deterministic fake answer on the retry:

```python
from prefect import flow, task, get_run_logger
from prefect.cache_policies import TASK_SOURCE

@task(retries=2, retry_delay_seconds=1, cache_key_fn=TASK_SOURCE)
def call_model(prompt: str) -> str:
    if _ATTEMPTS["model_call"] == 1:
        raise RuntimeError("PLANTED_TRANSIENT: model endpoint 503 (simulated)")
    return f"fake-llm answer to: {prompt!r}"

@flow(name="agentic-hello")
def agentic_hello(prompt: str = "hello") -> dict:
    return {"answer": call_model(prompt)}
```

Command: `env -u PYTHONHOME -u PYTHONPATH PREFECT_HOME=$HOME/.rig/agentic-lab/prefect/home .venv/bin/python hello_prefect.py`
Expected output: a task retry log (attempt 1 fails, attempt 2 succeeds) then `RESULT: {...}` and
`HELLO_PREFECT_OK attempts=2`. Use the deterministic fake for reproducible runs; swap the task body
for the local OpenAI client in section 5 for a real LLM step.

## 8. Durable and production features

- **Retries:** `@task(retries=N, retry_delay_seconds=...)` or a `RetryPolicy` on the flow call.
  Retryability and idempotency are separate; a retried side effect needs its own idempotency key.
- **Caching / idempotency:** `cache_key_fn` (e.g. `TASK_SOURCE`, `INPUTS`) + `cache_expiration`
  make a re-run skip the agent step; this is the idempotency lever for expensive LLM calls.
- **Schedules:** `Deployment`/`RunnerDeployment` with a cron or interval schedule; `prefect deploy`.
- **Concurrency:** work pools and per-work-pool concurrency limits; global concurrency limits
  gate how many agent steps run at once.
- **State:** every task/flow run has a state (Completed, Failed, Crashed, Retrying) queryable via
  the API/`prefect flow-run ls`.
- **Human-in-the-loop:** `pause_flow_run` / `suspend_flow_run` and infrastructure overrides; for
  signal-style durable interaction prefer Temporal (section 13 gotcha).

## 9. Observability

- Local UI/API: `prefect server start --host 127.0.0.1 --port 43xx` then open
  `http://127.0.0.1:43xx` (default UI 4200; use 4300-4399 here). `prefect config view` shows
  `PREFECT_API_URL`.
- Logs: `log_prints=True` on the flow, `get_run_logger()` in tasks; run history and task
  retries are visible per run in the UI and via `GET /api/flow_runs/` on the local API.
- Health probe: `curl -s -m 5 http://127.0.0.1:43xx/api/health`.

## 10. Testing

- **Deterministic fake LLM:** the `call_model` body returns a fixed string and touches no network,
  so unit tests are reproducible (section 7).
- **Unit test:** assert the retry fired (`attempts == 2`) and the result shape is correct.
- **One planted failure that goes red:** remove the retry (`retries=0`) or make the task always
  raise; the test asserting recovery must FAIL (red), then restore and see it pass (green). A green
  test that cannot go red is theater. Record the red run in `references/proof.json`.
- **Planted transient inside the flow:** attempt 1 raises `PLANTED_TRANSIENT`, attempt 2 succeeds -
  this is the L4-style proof the retry policy executes rather than being declared.

## 11. Deploy / self-host and Gate-D

Self-host is the default and is NOT gated: `prefect server start` and a local worker
(`prefect worker start --pool <pool>`) run entirely on this Mac. The following are **Gate-D** and
must NOT be done without Mike's explicit approval: Prefect Cloud signup or login, `prefect cloud
login`, any cloud workspace, `prefect deploy` to a remote/Cloud work pool, pushing flow code to a
remote, paid plans, and any public URL. This skill does none of them.

## 12. Teardown and upgrade

- Upgrade: `env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python -U prefect`
  then re-run section 7 to confirm nothing broke; re-verify the version string.
- Teardown: stop any worker/server you started (a self-destructing call, or
  `lsof -t -i :PORT | xargs kill` **only** for a port you bound in the same call), then remove the
  lab dir: `rm -rf ~/.rig/agentic-lab/prefect`. Deleting `PREFECT_HOME` drops local run state.

## 13. Gotchas

- **[observed here] PYTHONHOME/PYTHONPATH leakage** - the Aside runtime exports them and a venv
  python misbehaves; always `env -u PYTHONHOME -u PYTHONPATH`.
- **[observed here] Blackwell LAN model endpoints unreachable from the sandbox** - `192.168.68.90:8011`
  returns exit 7 (connection refused) and `:8111` returns exit 28 (timeout); only `127.0.0.1:8771`
  and `127.0.0.1:8657` answer. Probe before naming a route.
- **[observed here] qwen thinking mode returns 200 with empty content** at `127.0.0.1:8771` -
  disable thinking via `chat_template_kwargs.enable_thinking=false` and assert non-empty content.
- **[observed here] process control** - a server started in one bash call cannot be killed from a
  later call ("Operation not permitted"); start servers with a self-destruct alarm in the same call
  and never kill a port you did not bind in that call.
- **[docs] SQLAlchemy C extension library validation** - some `.so` files fail macOS library
  validation in this sandbox (seen: SQLAlchemy C extensions, ormsgpack). If prefect import fails on
  it, try `DISABLE_SQLALCHEMY_CEXT_RUNTIME=1`, then `xattr -cr <venv>`, then one
  `codesign --force -s - <file.so>`; if still blocked record BLOCKED (sandbox library validation)
  and use the host-shell route.
- **[observed here] don't declare a CLI/JVM absent from a bare PATH probe** - Homebrew lives at
  `~/.homebrew` (not on the default PATH); check there before concluding a tool is missing.
- **[own guidance, not a docs quote] retries are not idempotency** - a retried side-effecting
  task (an LLM call that writes, a charge, an insert) can run again and double-write. Give that
  task its own idempotency key or a cache policy. Do not cite
  `https://docs.prefect.io/v3/concepts/tasks` for this; that page does not say it.
  The caching page does say caching exists to "ensure that your pipelines are idempotent when
  retrying them due to unexpected failure" (`https://docs.prefect.io/v3/concepts/caching`, fetched
  2026-09-28). That sentence is about caching, not a claim that the tasks page defines retries.

## 14. Proof receipts

| Step | Command | Exit code | Version | Date | Proof level |
|---|---|---|---|---|---|
| Install | `uv pip install --python .venv/bin/python prefect` | 0 | prefect 3.8.7 | 2026-09-28 | L1 |
| Version | `.venv/bin/python -c "import prefect; print(prefect.__version__)"` | 0 | 3.8.7 | 2026-09-28 | L1 |
| Hello flow (fake LLM, retry fired) | `.venv/bin/python hello_prefect.py` (vs live server) | 0 - `HELLO_PREFECT_OK attempts=2`, retry fired | 3.8.7 | 2026-09-28 | L2 |
| asyncpg `.so` import (before stub) | `.venv/bin/python hello_prefect.py` | 1 - `dlopen(asyncpg/protocol/protocol...so): library load disallowed by system policy` | 3.8.7 | 2026-09-28 | BLOCKED (mitigated by stub) |
| Local API/UI | `prefect server start --host 127.0.0.1 --port 4310` + `curl /api/health` | 0 - health `200` body `true` | 3.8.7 | 2026-09-28 | L4 |
| Real local model endpoint | `curl http://127.0.0.1:8657/v1/chat/completions` | 0 - `content='PONG'` non-empty | - | 2026-09-28 | L3 (endpoint verified; seeded hello used the fake) |
| Deploy | Gate-D - not done | - | - | - | L5 not attempted |

Full machine-readable receipts: `capabilities/skills/agentic-setup-prefect/references/proof.json`.
