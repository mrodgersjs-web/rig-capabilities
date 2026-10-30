---
name: model-probe
outcome: "fleet health: no child or paid run is admitted on a model whose credential was not probed; dead credentials are named with the provider's own error, not a silent exit"
done_when:
  - "cmd:python3 capabilities/skills/model-probe/tests/test_model_probe.py"
  - "file:capabilities/skills/model-probe/src/model_probe/__init__.py"
great_example: "examples/great/infra-ops/provider-probe-first.md"
quality_floor: "0.8"
compatibility: "Python-backed. The kernel import and CLI need the skill installed into the agent kernel venv (Prime Agent does this at startup: uv pip install -e <skill-dir> --python ~/.prime/agent/kernel-venv/bin/python). Other harnesses can read the recipe, tests, and CLI source from the canonical copy."
description: Probe a model for a live credential and a real completion BEFORE spawning a child agent, a paid run, or a fleet fan-out. Use whenever choosing a model= for rlm.spawn or a worker, when a child exited fast with zero tokens or stopReason error, when a run reports 'No API key for provider', when AGENTS.md model routes look stale, or before any spend on a hosted provider. Verdicts are alive / dead / unproven with the provider error surfaced verbatim.
---

# Model probe (pre-spawn credential gate)

**Rule: no child and no paid run starts on an unprobed model.** A dead credential costs
~45s, zero tokens, and a stopReason buried in a child transcript. A probe costs 0.1s to
~20s and names the failure.

```python
import model_probe

v = model_probe.probe("blackwell-flash-next/qwen3.8-flash-next-uncensored")
v["verdict"], v["stage"], v["reason"]          # 'alive', 'completion', 'completion-returned-content'

model_probe.run("xai/grok-4.5")                # the same verdict as one line
model_probe.search_models("grok")              # real selectors only (models.json + shipped catalogue)
```

## Spawning children through the gate

`spawn()` probes, then hands off to `rlm.spawn` and returns the child handle plus the probe
verdict it was admitted on. It raises `ModelProbeError` (with every candidate's reason)
instead of admitting a child that cannot answer.

```python
res = await model_probe.spawn("Load the darius-gtm skill and draft this week's outbound.",
                              name="darius",
                              prefer=["blackwell-flash-next/qwen3.8-flash-next-uncensored",
                                      "rig-96gb/qwen3-coder:30b"])
handle = res["handle"]

try:
    res = await model_probe.spawn("...", name="ralph", model="xai/grok-4.5")
except model_probe.ModelProbeError as exc:
    print(exc)            # lists each candidate: dead (credential/credential-rejected) HTTP 400 ...
```

`pick(prefer=[...])` returns the first alive verdict, so a fleet plan can carry a fallback
chain instead of one hopeful model id.

## Verdicts (fail closed)

| verdict | means | next move |
|---|---|---|
| `alive` | a real completion returned non-empty content | spawn freely |
| `dead` | no credential, credential rejected, unreachable, HTTP >= 400, or empty completion | surface `error` + `fix`; do not spawn |
| `unproven` | credential accepted but no completion was run (metered provider, rate limit, budget too small) | treat as not-alive; re-probe with `paid=True` once spend is authorised |

The verdict dict carries `schema`, `provider`, `base_url`, `api`, `cost_per_mtok`, `paid`,
`credential` (kind/source/expiry, never the value), `stage`, `reason`, `check` (HTTP codes,
latency_ms, content_len, finish_reason, usage) and `ts`. `suggestions` appear on an unknown
selector.

## Cost and Gate-D

Local and LAN providers cost 0 in their own config, so the probe runs a real completion for
free. Hosted providers cost real money, so by default the probe only makes the **free**
authenticated `GET /models` call and reports `unproven / paid-probe-skipped`. One bounded
completion (128 tokens) on a hosted provider needs the explicit flag:

```python
model_probe.probe("anthropic/claude-opus-4-7", paid=True)   # spends a few tokens - authorised only
```

## Why a completion, not just /models

`200` from a health or models endpoint is not proof - a credit-exhausted key still serves
them (see the `provider-probe-first` doctrine). Non-empty content is the proof. The 128-token
floor is measured, not guessed: at 16 tokens `qwen3.8-flash-next-uncensored` returned empty
content with `reasoning_tokens: 19`, which reads as dead and is not.

## Known limits (measured, not assumed)

- Completion probing covers `openai-completions`, `openai-responses` and `anthropic-messages`
  request shapes. Anything else (bedrock-converse-stream, vertex, ...) resolves and gets the
  credential check, then a `chat/completions` POST that may 400 for shape reasons — read such a
  DEAD as "unknown to this probe", not "provider down".
- Credentials the agent keeps in its own stores (a Copilot device/PAT, for example) are invisible
  here, so they surface as `dead / no-credential`. Trust the fix line, then check that store.
- A live completion on a reasoning model measured 19-37s on the LAN. `pick()` over a long chain
  pays that per candidate; keep chains short or probe the fallback once and cache the verdict.
- The probe never prints a secret value: it reports kind, source, expiry, and whether the stored
  `!command` resolved.

## Verify

```bash
python3 tests/test_model_probe.py                     # offline, 50 checks, exit 0 = pass
model_probe --selector qwen3.8-flash-next-uncensored  # LAN probe, no spend (bare id resolves too)
model_probe --selector xai/grok-4.5                 # expects dead + the provider error verbatim
```

The CLI mirrors the kernel call — `model_probe --selector xai/grok-4.5 [--paid]
[--timeout 90] [--json-out]` (tyro turns every `run()` parameter into a flag). A typo in a
selector comes back `DEAD [resolve/unknown-model]` with close matches, which is how stale
doctrine model ids get caught.

## Receipts

Every build that uses this gate keeps its probe output under its own proof directory,
alongside the command that produced it. `~/.rig/live/builder-friday/proof/` holds the
original build's receipts.
