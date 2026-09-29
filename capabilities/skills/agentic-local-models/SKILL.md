---
name: agentic-local-models
description: "agentic-systems-setup sub-skill, gates E3 and E5: wire every agentic framework to a local-first model route with a named, probed fallback - list and prove OpenAI-compatible local endpoints, run L2 hellos on a deterministic fake model server, avoid the reasoning-model empty-content trap, and keep paid models as probed fallbacks only. JEV-FIRST MANDATE."
tags: [rig, agentic-systems, sub-skill, local-models, openai-compatible, fake-model]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: install-models
  stages: [install-models, hello-proof]
  extends: "provider-probe-first, typesafe-jev"
outcome: "A framework that talks to a proven local route (probe_endpoint.py ANSWERED_OK), passes its L2 hello on fake_openai_server.py, and names a fallback route that was probed with one real completion before it is relied on."
activation: "Load when a framework needs a model: at install (E3), before any hello proof (E5), whenever a model call returns empty or errors, and before adding any paid key to a setup."
instruction: "Probe the local route with probe_endpoint.py, point the framework at its base URL, run L2 on fake_openai_server.py, run L3 on the local route with thinking disabled and content asserted, and add a paid fallback only after a one-token probe and a keychain item name."
applies_when:
  env: "Aside sandbox or Orca terminal; loopback model routes on Mike's Mac"
  runtime: "any framework that accepts an OpenAI-compatible base URL"
  deps: "scripts/probe_endpoint.py, scripts/fake_openai_server.py (stdlib)"
  params: "base URL, model id, optional keychain item name for keyed routes"
  budget: "one probe per route per session; seconds each"
  scale: "one framework's model wiring at a time"
permissions:
  - fs.read
  - bash
  - net.api-calls
  - gate-d-required:paid-api
flow:
  - Probe candidate routes and keep the first ANSWERED_OK loopback route.
  - Start fake_openai_server.py and run the framework's L2 hello against it.
  - Point the framework at the local route and run L3 with content asserted.
  - Name a fallback and probe it with one completion before relying on it.
done_when:
  - "cmd:env -u PYTHONHOME -u PYTHONPATH python3 capabilities/skills/agentic-local-models/scripts/fake_openai_server.py --selftest"
  - "grep:capabilities/skills/agentic-local-models/SKILL.md:enable_thinking"
  - "grep:capabilities/skills/agentic-local-models/SKILL.md:finish_reason"
out_of_scope:
  - paid model calls without a Gate-D approval id
  - changing router configuration (OmniRoute, PAIR, Aside provider settings)
  - switching any interactive session onto a Flash model
---

# agentic-local-models

JEV FIRST, binding on every model-wiring step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call; hello receipts are judged with `rig-s1gate check agentic.setup`. When the
classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only
above 0.9; below that the level does not count.

## Load surface

Always loaded at the start of every agentic setup task that touches a model: the
`agentic-systems-setup` meta-skill routes gates E3 and E5 here, `agentic-setup-conductor` loads
it from its routes table, `agentic-proof-runner` executes it, and the `agentic-setup-session`
harness names it as doctrine. It is a task-start surface, not a deep reference.

## Policy (Mike, standing)

Local-first: dependable local routes carry the work; a paid route is allowed only as a named
fallback, probed with one real completion first (paid accounts have been found silently dead
at the billing layer), and used only under Gate-D.

## Prove a route (L3 precondition)

```sh
S=capabilities/skills/agentic-local-models/scripts
env -u PYTHONHOME -u PYTHONPATH python3 $S/probe_endpoint.py --base-url http://127.0.0.1:8771/v1
# ANSWERED_OK exit 0 | ANSWERED_EMPTY exit 2 | UNREACHABLE/TIMEOUT exit 3 | KEYED/HTTP_ERROR exit 4
```

Observed 2026-09-28: `127.0.0.1:8771` (PAIR, `qwen3.8-uncensored:27b`) ANSWERED_OK in 0.33 s;
`127.0.0.1:8657` (Mac Studio tunnel, `MiMo-V2.6-Flash-RL-MLX-4bit-MTP`) ANSWERED_OK in 2.87 s;
OmniRoute `127.0.0.1:20128` UNREACHABLE (connection refused).

## The empty-content trap (AS-07)

A reasoning model answered HTTP 200 with `content: ""` and `finish_reason: "length"`: all 8
tokens went to `reasoning_content`. The same call with
`"chat_template_kwargs": {"enable_thinking": false}` returned `"ready"`, `finish_reason: "stop"`,
in 0.97 s. Every hello asserts non-empty content AND `finish_reason == "stop"`; disable thinking
or budget `max_tokens` for reasoning routes.

## L2: a deterministic fake for any framework

```sh
env -u PYTHONHOME -u PYTHONPATH python3 $S/fake_openai_server.py --port 18999 --log <run>/fake-calls.jsonl &
# point the framework at http://127.0.0.1:18999/v1 with model "fake:scripted" and any non-secret key string
```

Scripted replies (`--reply`, default `ready`; "2 plus 3" answers `5`), SSE streaming supported,
every call logged so the test can assert the framework actually called the model. Self-test and
a probe against it passed on 2026-09-28. Start it under a time-box, for example
`capabilities/skills/agentic-systems-setup/scripts/bounded_run.sh 600 env -u PYTHONHOME -u PYTHONPATH python3 $S/fake_openai_server.py --port 18999 &`,
because a later bash call cannot kill it in this sandbox (Operation not permitted). The runner
keeps a perl parent that sends SIGTERM at the bound; the older `perl -e 'alarm shift; exec @ARGV'`
form does not stop Go programs, which ignore SIGALRM (AS-19).
Framework-native fakes (LangChain `GenericFakeChatModel`, Pydantic AI `TestModel`, LlamaIndex
`MockLLM`) are equally valid for L2; the framework skill confirms their import path at L0.

## Wiring pattern

Most frameworks take an OpenAI-compatible base URL plus a model id: set it in the framework's
client constructor or its `OPENAI_BASE_URL`-style variable, with a placeholder key string such
as `local` for keyless routes. The exact class and parameter per framework are owned by the
`agentic-setup-<slug>` skill and confirmed against today's docs (L0), not written from memory.

## Fallback

Name it in the receipt (`fallback: openrouter via com.rig.env.OPENROUTER_API_KEY`), probe it
with `probe_endpoint.py --key-item <item>` only when Gate-D allows a paid call, and never make
it the default route.
