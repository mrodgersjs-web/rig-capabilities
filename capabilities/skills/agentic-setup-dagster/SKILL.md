---
name: agentic-setup-dagster
description: "agentic-systems-setup sub-skill: set up Dagster end to end on Mike's Mac - software-defined assets and ops/jobs, resources, schedules, sensors, partitions, and the local dagster dev web UI - with an LLM/agent step living inside an asset or op carrying retries, idempotent materialization and observability. Start here when: 'set up Dagster', 'Dagster asset or job', 'dagster dev', 'software-defined asset', 'Dagster schedule or sensor', or any agentic-systems-setup job whose orchestrator is Dagster. JEV-FIRST MANDATE."
tags: [rig, agentic-systems, sub-skill, dagster, orchestrator, assets, llm-ops]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: dagster
  extends: "agentic-env-probe, provider-probe-first, app-data-layer"
outcome: "A runnable Dagster job/asset whose agent step is an op/asset with a fired retry and an idempotent materialization, visible in the local dagster dev UI - plus receipts and honest BLOCKED notes for native extensions."
activation: "Load before the first dagster install on this machine, and again whenever an asset, op, job, resource, schedule, sensor, or partition is added or the agent step's retry/idempotency is questioned."
instruction: "Probe first, install dagster into a uv venv with PYTHONHOME unset under ~/.rig/agentic-lab/dagster, put the agent step in an op/asset with an explicit retry policy and an idempotent compute, prove the retry with a planted transient failure, and record every command and exit code in references/proof.json. Route typed judgments to rig-s1gate BEFORE any frontier LLM call; fail closed when the classifier is down."
applies_when:
  env: "Aside bash sandbox or an Orca terminal on Mike's Mac; lab dir ~/.rig/agentic-lab/dagster with DAGSTER_HOME set there"
  runtime: "Python 3.10-3.13 uv venv (verified 3.12 here); Dagster 1.x API and dagster dev CLI"
  deps: "uv; dagster, dagster-webserver from PyPI; optional openai client for a real local model op"
  params: "op/asset retry_policy; job and run config; schedule cron; partition key"
  budget: "one job per agent pipeline; dagster dev on ports 4300-4399; no paid API"
  scale: "single Mac, local Dagster instance; not Dagster+ or a multi-user deployment"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - Probe the toolchain and the local model endpoints; record which answered.
  - Create the lab venv with PYTHONHOME unset and install dagster + dagster-webserver.
  - Write the agent step as an op/asset with an explicit retry policy and idempotent compute.
  - Run the job with a deterministic fake model step and a planted transient failure to prove the retry fires.
  - Start dagster dev on a 4300-4399 port in a self-destructing call and poll its web server.
  - Record commands, exit codes, versions, and proof level in references/proof.json.
done_when:
  - "cmd:env -u PYTHONHOME -u PYTHONPATH python3 -m rig_capabilities.skill_contract capabilities/skills/agentic-setup-dagster/SKILL.md"
  - "grep:capabilities/skills/agentic-setup-dagster/SKILL.md:Start here when"
  - "grep:capabilities/skills/agentic-setup-dagster/SKILL.md:rig-s1gate"
  - "file:capabilities/skills/agentic-setup-dagster/references/proof.json"
out_of_scope:
  - Dagster+ signup, login, or any cloud deployment (Gate-D)
  - paid API keys or paid model calls
  - editing repos or harness roots; installs stay in ~/.rig/agentic-lab/dagster
  - starting daemons owned by other workers (Docker/Colima)
---

# agentic-setup-dagster

Start here when: you are setting up Dagster as an orchestrator on this Mac, or putting an
LLM/agent step inside a Dagster asset or op with retries, idempotent materialization and observability.

JEV FIRST, binding on every setup and judgment step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier
LLM call; setup receipts are judged with `rig-s1gate check agentic.setup`. When the classifier is
unavailable: DEFER, never guess a verdict locally. FAIL CLOSED: a required signal passes only above
0.9; below that the gate does not advance and the setup step is held, not assumed good.

## Load surface

Always loaded at the start of every Dagster setup task: the `agentic-systems-setup` meta-family
routes here and an agent picks this skill at task start from its `description` and `Start here when`
triggers. It is a task-start surface, not a deep reference an agent must already know about; load
`references/` detail on demand, not up front.

## 1. When to choose it and when not

Choose Dagster when the mental model is **assets and lineage**: typed software-defined assets,
partitioned materializations, an asset dependency graph, and a local dev UI that shows what is
materialized and when. The agent step becomes an asset (or op inside a job) whose retry and
idempotent compute are declared, and re-materialization is the cache/lineage mechanism.

The two nearest alternatives:
- **prefect** - choose Prefect instead when you want imperative flow/task code with per-task
  caching and a lighter footprint, rather than an asset graph with lineage and partitions.
- **airflow** - choose Airflow instead when you need the incumbent scheduler, a huge operator
  library, and centrally scheduled DAGs; Dagster gives stronger asset lineage and dev UX but a
  smaller legacy operator ecosystem.

Do not choose Dagster for long-lived durable execution with signals and replay (see
`agentic-setup-temporal`) or browser-native low-code (n8n, flowise, langflow).

## 2. Current version and sources

- **dagster 1.13.24** - verified today from the PyPI JSON API (`https://pypi.org/pypi/dagster/json`).
- Official docs fetched today: `https://docs.dagster.io/getting-started`,
  `https://docs.dagster.io/guides/build/assets`, `https://docs.dagster.io/guides/build/jobs`,
  `https://docs.dagster.io/guides/automate/schedules`, `https://docs.dagster.io/guides/operate/io-managers`,
  `https://docs.dagster.io/dagster-cloud`.
- PyPI: `https://pypi.org/project/dagster/`.
- Companion packages: `dagster-webserver` (the local UI), `dagster-postgres` (state DB, optional).

## 3. Environment route and prerequisites

- **Route: Aside bash sandbox, uv venv** (verified for install/import). Host shell (Orca terminal)
  is the fallback if a native extension fails library validation.
- PATH prefix `PATH="$HOME/.local/bin:/usr/local/bin:$PATH"`.
- `env -u PYTHONHOME -u PYTHONPATH` for every Python call (Aside runtime leaks both).
- Prerequisites: `uv`, Python 3.12 (3.12.12 here).
- Set `DAGSTER_HOME` to `~/.rig/agentic-lab/dagster/home` so run/event state never lands in a repo.
- Run `capabilities/skills/agentic-env-probe/scripts/env_probe.py` first.

## 4. Install (exact commands)

```bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
mkdir -p ~/.rig/agentic-lab/dagster && cd ~/.rig/agentic-lab/dagster
env -u PYTHONHOME -u PYTHONPATH uv venv .venv --python 3.12
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python dagster dagster-webserver
env -u PYTHONHOME -u PYTHONPATH .venv/bin/python -c "import dagster, importlib.metadata as m; print(m.version('dagster'))"
```

Expected: `1.13.24`. If SQLAlchemy C extension import fails here (observed class of failure), try
`DISABLE_SQLALCHEMY_CEXT_RUNTIME=1`, then `xattr -cr .venv`, then one `codesign --force -s - <file.so>`;
if still blocked, record BLOCKED (sandbox library validation) and use the host-shell route.

## 5. Local-first model wiring for the agent step

No paid keys. The agent op/asset calls an OpenAI-compatible **local** base URL. Endpoints verified
answering here: `http://127.0.0.1:8771/v1` (qwen3.8-uncensored:27b) and
`http://127.0.0.1:8657/v1` (MiMo-V2.6-Flash-RL-MLX-4bit-MTP). Blackwell `192.168.68.90:8011/:8111`
do NOT answer from this sandbox. Inject the base URL via a Dagster **resource** (configurable) so
tests can swap in a fake.

```python
from dagster import ConfigurableResource
class LocalModel(ConfigurableResource):
    base_url: str = "http://127.0.0.1:8771/v1"
    model: str = "qwen3.8-uncensored:27b"
    def complete(self, prompt: str) -> str:
        from openai import OpenAI
        c = OpenAI(base_url=self.base_url, api_key="not-needed-local")
        r = c.chat.completions.create(model=self.model,
            messages=[{"role": "user", "content": prompt}],
            extra_body={"chat_template_kwargs": {"enable_thinking": False}})
        text = r.choices[0].message.content
        assert text, "empty content from local model"
        return text
```

qwen at `127.0.0.1:8771` returns 200 with EMPTY content when thinking is on - disable as above and
assert non-empty. Never call a paid API.

## 6. Secrets

Reference keychain item names, never values: `com.rig.env.<NAME>`. Local endpoints use a placeholder
key ("not-needed-local"); a real secret is injected through a Dagster **resource** or Dagster's
configured value store / env mapping at runtime, never hardcoded in an asset, never committed, and
never in `references/`. `DAGSTER_HOME` holds run/event state and dagster.yaml, not secret values in
plaintext you paste into a repo.

## 7. Hello-world

`~/.rig/agentic-lab/dagster/hello_dagster.py` - a `@job` of ops where the agent step is an
`@op(retry_policy=RetryPolicy(...))` with a deterministic fake model and a planted transient
failure on attempt 1:

```python
from dagster import job, op, OpExecutionContext, RetryPolicy, RetryRequested, Definitions

@op(retry_policy=RetryPolicy(max_retries=2, delay=1))
def call_model(context: OpExecutionContext) -> str:
    prompt = "hello from an agent step inside Dagster"   # or from op_config; not a literal arg
    n = _ATTEMPTS["model_call"] = _ATTEMPTS.get("model_call", 0) + 1   # module counter for the planted run
    if n == 1:
        raise RuntimeError("PLANTED_TRANSIENT: model endpoint 503 (simulated)")
    return f"fake-llm answer to: {prompt!r}"

@op
def postprocess(answer: str) -> str:
    return answer.upper()

@job
def agentic_hello():
    postprocess(call_model())   # note: @job composition cannot take literal args
```

Run: `env -u PYTHONHOME -u PYTHONPATH DAGSTER_HOME=$HOME/.rig/agentic-lab/dagster/home .venv/bin/python hello_dagster.py`
(or `dagster job execute -f hello_dagster.py -j agentic_hello`). Expected: a retry in the event log
(attempt 1 fails, attempt 2 succeeds) and the job succeeds. Use the deterministic fake for
reproducible runs; swap the op body for the local model resource in section 5.

## 8. Durable and production features

- **Retries:** `RetryPolicy(max_retries, delay, backoff)` on an op/asset, or raise
  `RetryRequested` for dynamic control. Retryability != idempotency; make the compute idempotent.
- **Idempotent materialization / caching:** assets are re-materializable and keyed by partition +
  version; an IOManager persists outputs so re-runs skip unchanged work - the cache/lineage lever
  for expensive LLM steps.
- **Schedules and sensors:** `@schedule` (cron) and `@sensor` (event/partition-driven) launch runs.
- **Concurrency:** `max_concurrent_runs`, op-level concurrency limits, and run queues gate how many
  agent steps run at once.
- **Partitions / state:** `@asset(partitions_def=...)` for time- or key-partitioned materializations;
  run status and asset materialization events are the state record.
- **Human-in-the-loop:** sensors + run config / `dagster job launch --config` for approval-driven
  runs; for durable signal-style interaction prefer Temporal (section 13).

## 9. Observability

- Local UI: `dagster dev -h 127.0.0.1 -p 43xx` then open `http://127.0.0.1:43xx` (webserver on the
  given port; Dagit/dagster-webserver shows the asset graph, run logs, and per-op retries).
- Logs: `context.log` in ops; run stdout/stderr captured per step in the run log. Health:
  `curl -s -m 5 http://127.0.0.1:43xx/server_info` (or the webserver root).
- In-sandbox: start `dagster dev` in a self-destructing call and poll the port there (gotchas).

## 10. Testing

- **Deterministic fake LLM:** the op returns a fixed string and touches no network (section 7).
- **Unit test:** `dagster.materialize` / `job.execute_in_process()` and assert the retry fired and
  the output shape is correct.
- **One planted failure that goes red:** assert recovery from `PLANTED_TRANSIENT`; then set
  `max_retries=0` (or always-raise) and show the test FAILS (red); restore to green. Record the red
  run in `references/proof.json` - a green test that cannot go red is theater.
- Resource swapping: pass a `FakeModel` resource in tests so no network is used.

## 11. Deploy / self-host and Gate-D

Self-host is default and NOT gated: `dagster dev` runs entirely on this Mac with local state in
`DAGSTER_HOME`. **Gate-D - do NOT do without Mike:** Dagster+ signup/login, deploying to Dagster+,
any cloud/agent deployment, paid plans, or a public URL. This skill does none of them.

## 12. Teardown and upgrade

- Upgrade: `env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python -U dagster dagster-webserver`,
  re-run section 7 and the tests, re-verify the version string.
- Teardown: stop `dagster dev` (self-destructing call; `lsof -t -i :PORT | xargs kill` ONLY for a
  port you bound in the same call), then `rm -rf ~/.rig/agentic-lab/dagster` (drops `DAGSTER_HOME` state).

## 13. Gotchas

- **[observed here] PYTHONHOME/PYTHONPATH leakage** - always `env -u PYTHONHOME -u PYTHONPATH`.
- **[observed here] SQLAlchemy C extension library validation** - some `.so` files (SQLAlchemy C
  extensions, ormsgpack) fail macOS library validation in this sandbox while pydantic-core loads.
  Try `DISABLE_SQLALCHEMY_CEXT_RUNTIME=1`, then `xattr -cr <venv>`, then one
  `codesign --force -s - <file.so>`. If still blocked, record BLOCKED (sandbox library validation)
  with the exact error and run on the host-shell route (Orca terminal).
- **[observed here] Blackwell LAN model endpoints unreachable** - `192.168.68.90:8011` exit 7,
  `:8111` exit 28; only `127.0.0.1:8771` and `127.0.0.1:8657` answer. Probe first.
- **[observed here] qwen thinking mode = 200 + empty content** at `127.0.0.1:8771`; disable via
  `chat_template_kwargs.enable_thinking=false` and assert non-empty.
- **[observed here] process control across bash calls** - a `dagster dev` started in one call cannot
  be killed from a later call ("Operation not permitted"); wrap it in a self-destruct alarm in the
  same call and poll the webserver there. Never kill a port you did not bind in that call.
- **[observed here] don't declare a CLI/JVM absent from a bare PATH probe** - Homebrew lives at
  `~/.homebrew` (not on the default PATH); check there before concluding a tool is missing.
- **[docs: https://docs.dagster.io/guides/build/jobs] ops should be idempotent** - a retried
  side-effecting op (an LLM call that writes) can double-run; give it an idempotency key or an
  IOManager-keyed output so retries do not duplicate work.

## 14. Proof receipts

| Step | Command | Exit code | Version | Date | Proof level |
|---|---|---|---|---|---|
| Install | `uv pip install --python .venv/bin/python dagster dagster-webserver` | 0 | dagster 1.13.24 | 2026-09-28 | L1 |
| Version | `python -c "import dagster, importlib.metadata as m; m.version('dagster')"` | 0 | 1.13.24 | 2026-09-28 | L1 |
| Hello job (fake LLM, retry fired) | `DISABLE_SQLALCHEMY_CEXT=1 .venv/bin/python hello_dagster.py` | 0 - `EXEC_SUCCESS: True`, `STEP_RESTARTED attempt # 2`, `HELLO_DAGSTER_OK attempts=2` | 1.13.24 | 2026-09-28 | L2 + L4 (retry after planted failure) |
| SQLAlchemy Cython `.so` (before fix) | `python hello_dagster.py` | 1 - `dlopen(_collections_cy...so): library load disallowed by system policy` | 1.13.24 | 2026-09-28 | BLOCKED (mitigated: move `.so` aside) |
| Local UI/API | `dagster dev` + curl webserver | not run (in-process engine used) | 1.13.24 | 2026-09-28 | partial |
| Real local model op | LLM endpoint probe | BLOCKED/answered - see references/proof.json | - | 2026-09-28 | L3 target |
| Deploy / Dagster+ | Gate-D - not done | - | - | - | L5 not attempted |

Full machine-readable receipts: `capabilities/skills/agentic-setup-dagster/references/proof.json`.
