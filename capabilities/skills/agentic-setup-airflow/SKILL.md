---
name: agentic-setup-airflow
description: "agentic-systems-setup sub-skill: set up Apache Airflow end to end on Mike's Mac - DAGs and tasks, the scheduler and webserver (airflow standalone), TaskFlow API, retries, schedules, pools and SLAs - with an LLM/agent step living inside a DAG task carrying retries, idempotent handlers and observability. Start here when: 'set up Airflow', 'Airflow DAG', 'airflow standalone', 'TaskFlow API', 'Airflow schedule or pool', or any agentic-systems-setup job whose orchestrator is Airflow. JEV-FIRST MANDATE."
tags: [rig, agentic-systems, sub-skill, airflow, orchestrator, dag, llm-tasks]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: airflow
  extends: "agentic-env-probe, provider-probe-first, app-data-layer"
outcome: "A runnable Airflow DAG whose agent step is a task with a fired retry and an idempotent handler, visible in the local airflow standalone UI - plus receipts and honest BLOCKED notes for native extensions."
activation: "Load before the first apache-airflow install on this machine, and again whenever a DAG, task, retry, schedule, pool, connection, or variable is added or the agent step's retry/idempotency is questioned."
instruction: "Probe first, install apache-airflow into a uv venv with PYTHONHOME unset under ~/.rig/agentic-lab/airflow with AIRFLOW_HOME set there, put the agent step in a TaskFlow task with retries= and an idempotent callable, prove the retry with a planted transient failure, and record every command and exit code in references/proof.json. Route typed judgments to rig-s1gate BEFORE any frontier LLM call; fail closed when the classifier is down."
applies_when:
  env: "Aside bash sandbox or an Orca terminal on Mike's Mac; lab dir ~/.rig/agentic-lab/airflow with AIRFLOW_HOME set there"
  runtime: "Python 3.10-3.12 uv venv (verified 3.12 here; Airflow does not support 3.13 yet); Airflow 2.x/3.x API and CLI"
  deps: "uv; apache-airflow from PyPI; optional openai client for a real local model task"
  params: "task retries/retry_delay; DAG schedule and catchup; pool/slot limits"
  budget: "one DAG per agent pipeline; airflow standalone on ports 4300-4399 (webserver) and 87xx (scheduler); no paid API"
  scale: "single Mac, LocalExecutor/SequentialExecutor; not Astronomer/Composer or a multi-node cluster"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - Probe the toolchain and the local model endpoints; record which answered.
  - Create the lab venv with PYTHONHOME unset and install apache-airflow with AIRFLOW_HOME set.
  - Write the agent step as a TaskFlow task with retries= and an idempotent callable.
  - Run the DAG with a deterministic fake model step and a planted transient failure to prove the retry fires.
  - Start airflow standalone on a 4300-4399 webserver port in a self-destructing call and poll its health endpoint.
  - Record commands, exit codes, versions, and proof level in references/proof.json.
done_when:
  - "cmd:env -u PYTHONHOME -u PYTHONPATH python3 -m rig_capabilities.skill_contract capabilities/skills/agentic-setup-airflow/SKILL.md"
  - "grep:capabilities/skills/agentic-setup-airflow/SKILL.md:Start here when"
  - "grep:capabilities/skills/agentic-setup-airflow/SKILL.md:rig-s1gate"
  - "file:capabilities/skills/agentic-setup-airflow/references/proof.json"
out_of_scope:
  - Astronomer, Google Cloud Composer, or any managed/cloud Airflow deploy (Gate-D)
  - paid API keys or paid model calls
  - editing repos or harness roots; installs stay in ~/.rig/agentic-lab/airflow
  - starting daemons owned by other workers (Docker/Colima)
---

# agentic-setup-airflow

Start here when: you are setting up Apache Airflow as an orchestrator on this Mac, or putting an
LLM/agent step inside an Airflow DAG task with retries, idempotent handlers and observability.

JEV FIRST, binding on every setup and judgment step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier
LLM call; setup receipts are judged with `rig-s1gate check agentic.setup`. When the classifier is
unavailable: DEFER, never guess a verdict locally. FAIL CLOSED: a required signal passes only above
0.9; below that the gate does not advance and the setup step is held, not assumed good.

## Load surface

Always loaded at the start of every Airflow setup task: the `agentic-systems-setup` meta-family
routes here and an agent picks this skill at task start from its `description` and `Start here when`
triggers. It is a task-start surface, not a deep reference an agent must already know about; load
`references/` detail on demand, not up front.

## 1. When to choose it and when not

Choose Airflow when you want the incumbent, battle-tested scheduler: DAGs with cron schedules,
rich task retries/SLAs, pools, a huge provider/operator ecosystem, and a central webserver that
many teams already know. The agent step is a task (TaskFlow `@task`) with `retries=` and an
idempotent callable.

The two nearest alternatives:
- **prefect** - choose Prefect instead when you want lighter, more Pythonic flow/task code with
  per-task caching and a faster local loop, and you do not need Airflow's operator library or its
  central-scheduler model.
- **kestra** - choose Kestra instead when you want declarative YAML DAGs with a modern UI and
  built-in backends, less Python boilerplate than Airflow, and event-driven triggers without
  running a Python scheduler.

Do not choose Airflow for durable execution with signals/queries and replay (see
`agentic-setup-temporal`) or for asset-lineage-first orchestration (see `agentic-setup-dagster`).

## 2. Current version and sources

- **apache-airflow 3.3.2** - verified today from the PyPI JSON API
  (`https://pypi.org/pypi/apache-airflow/json`). (Airflow 3.x is current; 2.11.x is the maintained
  legacy line. Confirm the version you install; the steps below are version-agnostic where noted.)
- Official docs fetched today: `https://airflow.apache.org/docs/apache-airflow/stable/install/index.html`,
  `https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html`,
  `https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html`,
  `https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html`,
  `https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/logging-monitoring/check-health.html`.
- PyPI: `https://pypi.org/project/apache-airflow/`.

## 3. Environment route and prerequisites

- **Route: Aside bash sandbox, uv venv** for install and DAG code. Airflow's scheduler/webserver
  are long-running processes - run them in a self-destructing call here, or use the host-shell route
  (Orca terminal) for a persistent instance.
- PATH prefix `PATH="$HOME/.local/bin:/usr/local/bin:$PATH"`.
- `env -u PYTHONHOME -u PYTHONPATH` for every Python call (Aside runtime leaks both).
- Prerequisites: `uv`, Python 3.12 (3.12.12 here). **Airflow does not support Python 3.13** - pin
  3.12 or lower in the venv.
- Set `AIRFLOW_HOME` to `~/.rig/agentic-lab/airflow/home` so the sqlite DB, logs, and
  `airflow.cfg` never land in a repo.
- Constraint files: Airflow strongly recommends installing with its matching constraints file
  (see docs); a bare `pip install apache-airflow` resolves a compatible set but pinning is safer.
- Run `capabilities/skills/agentic-env-probe/scripts/env_probe.py` first.

## 4. Install (exact commands)

```bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
mkdir -p ~/.rig/agentic-lab/airflow && cd ~/.rig/agentic-lab/airflow
env -u PYTHONHOME -u PYTHONPATH uv venv .venv --python 3.12
export AIRFLOW_HOME=$HOME/.rig/agentic-lab/airflow/home
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python "apache-airflow==3.3.2"
env -u PYTHONHOME -u PYTHONPATH AIRFLOW_HOME=$AIRFLOW_HOME .venv/bin/python -c "import airflow, importlib.metadata as m; print(m.version('apache-airflow'))"
env -u PYTHONHOME -u PYTHONPATH AIRFLOW_HOME=$AIRFLOW_HOME .venv/bin/airflow standalone   # or: airflow db init + airflow webserver/scheduler
```

Expected: `3.3.2`. If SQLAlchemy C extension import fails here (observed class of failure), try
`DISABLE_SQLALCHEMY_CEXT_RUNTIME=1`, then `xattr -cr .venv`, then one `codesign --force -s - <file.so>`;
if still blocked, record BLOCKED (sandbox library validation) with the exact error and use the
host-shell route. `airflow standalone` prints an admin URL + password to stdout - keep it local.

## 5. Local-first model wiring for the agent step

No paid keys. The agent TaskFlow task calls an OpenAI-compatible **local** base URL. Endpoints
verified answering here: `http://127.0.0.1:8771/v1` (qwen3.8-uncensored:27b) and
`http://127.0.0.1:8657/v1` (MiMo-V2.6-Flash-RL-MLX-4bit-MTP). Blackwell `192.168.68.90:8011/:8111`
do NOT answer from this sandbox. Put the base URL in an Airflow **Connection/Variable** (not code),
and use a placeholder key for local endpoints.

```python
from airflow.decorators import dag, task
from pendulum import datetime

@task(retries=2, retry_delay=timedelta(seconds=1))
def call_model(prompt: str) -> str:
    from openai import OpenAI
    c = OpenAI(base_url="http://127.0.0.1:8771/v1", api_key="not-needed-local")
    r = c.chat.completions.create(model="qwen3.8-uncensored:27b",
        messages=[{"role": "user", "content": prompt}],
        extra_body={"chat_template_kwargs": {"enable_thinking": False}})
    text = r.choices[0].message.content
    assert text, "empty content from local model"
    return text
```

qwen at `127.0.0.1:8771` returns 200 with EMPTY content when thinking is on - disable as above and
assert non-empty. Never call a paid API.

## 6. Secrets

Reference keychain item names, never values: `com.rig.env.<NAME>`. For Airflow, real values go in a
**Connection** (`airflow connections add`) or **Variable** (`airflow variables set`) backed by a
secret backend (Fernet-encrypted metadata DB, or an external secrets backend) - never hardcoded in
a DAG, never committed, never in `references/`. Local endpoints use a placeholder key
("not-needed-local"). `AIRFLOW_HOME/airflow.cfg` holds config, not secrets you paste into a repo.

## 7. Hello-world

`~/.rig/agentic-lab/airflow/hello_airflow.py` - a TaskFlow DAG where the agent step is a
`@task(retries=2, retry_delay=...)` with a deterministic fake model and a planted transient failure
on attempt 1:

```python
from datetime import timedelta
from airflow.decorators import dag, task
from pendulum import datetime

@task(retries=2, retry_delay=timedelta(seconds=1))
def call_model(prompt: str) -> str:
    if _ATTEMPTS["model_call"] == 1:
        raise RuntimeError("PLANTED_TRANSIENT: model endpoint 503 (simulated)")
    return f"fake-llm answer to: {prompt!r}"

@task
def postprocess(answer: str) -> str:
    return answer.upper()

@dag(start_date=datetime(2026, 9, 28), schedule=None, catchup=False, tags=["agentic"])
def agentic_hello():
    postprocess(call_model("hello from an agent step inside Airflow"))

agentic_hello()
```

Run the DAG (standalone running): `airflow dags test agentic_hello 2026-09-28` (a single local
run) or trigger it in the UI. Expected: the task retry appears in the task instance log (attempt 1
fails, attempt 2 succeeds) and the DAG run reaches success. Use the deterministic fake for
reproducible runs; swap the task body for the local model in section 5.

## 8. Durable and production features

- **Retries:** `@task(retries=N, retry_delay=..., retry_exponential_backoff=True)`. Retryability
  != idempotency; make the callable idempotent so a retry does not double-write/double-bill.
- **Idempotency / caching:** Airflow has no per-task result cache like Prefect; use an
  idempotent handler + `depends_on_past`/external sensors, or XCom + an idempotency key, to avoid
  duplicate side effects on retry.
- **Schedules:** DAG `schedule` (cron/timetable), `catchup`, and `max_active_runs`.
- **Concurrency:** `max_active_tasks`, `max_active_runs`, and **pools** (`airflow pools set`) with
  slot limits gate how many agent steps run at once.
- **SLAs / state:** task/DAG states (success, failed, up_for_retry), SLA misses, and clear/re-run
  semantics; `airflow tasks states-for-dag-run` shows state.
- **Human-in-the-loop:** deferrable operators/sensors, `airflow tasks run` with manual trigger, or
  an approval DAG; for durable signal-style interaction prefer Temporal (section 13).

## 9. Observability

- Local UI: `airflow standalone` (webserver + scheduler + auth) then open the printed
  `http://127.0.0.1:8080` by default - **use a 4300-4399 webserver port here** (`airflow webserver
  --port 43xx`) to avoid a stray service on 8080. The UI shows DAG runs, task attempts, retries,
  and logs.
- Logs: task instance logs under `AIRFLOW_HOME/logs`; `airflow tasks test <dag> <task> <date>` for
  a local log; health check `curl -s -m 5 http://127.0.0.1:43xx/health`.
- In-sandbox: start standalone in a self-destructing call and poll the webserver there (gotchas).

## 10. Testing

- **Deterministic fake LLM:** the task returns a fixed string, no network (section 7).
- **Unit test:** `airflow tasks test agentic_hello call_model 2026-09-28` or pytest with the
  TaskFlow callable; assert the retry fired and the output shape is correct.
- **One planted failure that goes red:** assert recovery from `PLANTED_TRANSIENT`; then set
  `retries=0` (or always-raise) and show the test FAILS (red); restore to green. Record the red run
  in `references/proof.json` - a green test that cannot go red is theater.
- `airflow dags test` runs one local execution with no scheduler dependency - good for CI.

## 11. Deploy / self-host and Gate-D

Self-host is default and NOT gated: `airflow standalone` (or webserver + scheduler + LocalExecutor)
runs entirely on this Mac with sqlite/local state. **Gate-D - do NOT do without Mike:** Astronomer,
Google Cloud Composer, or any managed Airflow deployment, `astro deploy`, cloud logins, paid plans,
or a public URL. This skill does none of them.

## 12. Teardown and upgrade

- Upgrade: `env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python -U apache-airflow`
  (respect the constraints file for the target version), run `airflow db upgrade` if the metadata
  schema moves, re-run section 7 and the tests, re-verify the version string.
- Teardown: stop standalone/webserver/scheduler (self-destructing call; `lsof -t -i :PORT | xargs
  kill` ONLY for a port you bound in the same call), then `rm -rf ~/.rig/agentic-lab/airflow`
  (drops `AIRFLOW_HOME`: config, sqlite DB, logs).

## 13. Gotchas

- **[observed here] PYTHONHOME/PYTHONPATH leakage** - always `env -u PYTHONHOME -u PYTHONPATH`.
- **[observed here] SQLAlchemy C extension library validation** - some `.so` files (SQLAlchemy C
  extensions, ormsgpack) fail macOS library validation in this sandbox while pydantic-core loads.
  Try `DISABLE_SQLALCHEMY_CEXT_RUNTIME=1`, then `xattr -cr <venv>`, then one
  `codesign --force -s - <file.so>`. If still blocked, record BLOCKED (sandbox library validation)
  with the exact error and run on the host-shell route (Orca terminal). Airflow is the most
  SQLAlchemy-heavy of the four orchestrators - budget time here.
- **[observed here] Python 3.13 unsupported by Airflow** - pin the venv to 3.12 or lower; the
  install will not resolve cleanly on 3.13.
- **[observed here] Blackwell LAN model endpoints unreachable** - `192.168.68.90:8011` exit 7,
  `:8111` exit 28; only `127.0.0.1:8771` and `127.0.0.1:8657` answer. Probe first.
- **[observed here] qwen thinking mode = 200 + empty content** at `127.0.0.1:8771`; disable via
  `chat_template_kwargs.enable_thinking=false` and assert non-empty.
- **[observed here] process control across bash calls** - a `airflow standalone` started in one call
  cannot be killed from a later call ("Operation not permitted"); wrap it in a self-destruct alarm
  in the same call and poll the webserver there. Never kill a port you did not bind in that call.
- **[observed here] don't declare a CLI/JVM absent from a bare PATH probe** - Homebrew lives at
  `~/.homebrew` (not on the default PATH); check there before concluding a tool is missing.
- **[docs] avoid port 8080** - a stray service (Kestra) may hold it; run the webserver on a
  4300-4399 port. Airflow also uses a scheduler log/port set - keep all of them clear of other
  workers' ports.
- **[docs: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html] retries
  are not idempotency** - a retried side-effecting task (an LLM call that writes) can double-run;
  give it an idempotency key or make the handler idempotent.

## 14. Proof receipts

| Step | Command | Exit code | Version | Date | Proof level |
|---|---|---|---|---|---|
| Install | `uv pip install --python .venv/bin/python apache-airflow==3.3.2` | 0 | apache-airflow 3.3.2 | 2026-09-28 | L1 |
| Version | `python -c "import airflow, importlib.metadata as m; m.version('apache-airflow')"` | 0 | 3.3.2 | 2026-09-28 | L1 |
| DAG build | `DISABLE_SQLALCHEMY_CEXT=1 .venv/bin/python hello_airflow.py` | 1 - `dlopen(_cffi_backend...so): library load disallowed by system policy` | 3.3.2 | 2026-09-28 | BLOCKED (cffi/cryptography, no pure-Python fallback) |
| Offline retry contract | `.venv/bin/python test_airflow_offline.py` | 0 - `RETRY_CONTRACT_OK attempts=2`, `PLANTED_FAILURE_RED_OK` | 3.3.2 | 2026-09-28 | L2-logic (not the engine) |
| Local UI/API | `airflow standalone` + curl /health | not run (DAG engine BLOCKED at import) | 3.3.2 | 2026-09-28 | BLOCKED |
| Real local model task | LLM endpoint probe | BLOCKED/answered - see references/proof.json | - | 2026-09-28 | L3 target |
| Deploy / Astronomer/Composer | Gate-D - not done | - | - | - | L5 not attempted |

Full machine-readable receipts: `capabilities/skills/agentic-setup-airflow/references/proof.json`.
