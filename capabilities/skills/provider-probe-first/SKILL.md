---
name: "provider-probe-first"
description: "Probe the model provider with a real completion BEFORE diagnosing any gate, routine, tool, or code failure. A provider outage manufactures fake gate verdicts that look like real ones. Use whenever a gate returns BLOCK or ESCALATE unexpectedly, a routine emits empty output, a model call errors, or before writing any root cause into memory. Trigger on: 'gate failing', 'why did this block', 'the model is broken', 'diagnose this', 'routine did nothing'."
when_to_use: "The FIRST action of any failure diagnosis. Before blaming rubrics, code, prompts, config, or data."
version: "1.0.0"
status: "active"
outcome: "infra-ops: no failure diagnosis is written without a provider-health receipt; outages are named as outages, not as verdicts"
done_when:
  - "cmd:python3 -c \"import urllib.request,sys;print(urllib.request.urlopen('http://192.168.68.53:4000/health/liveliness',timeout=5).status)\""
great_example: "examples/great/infra-ops/provider-probe-first.md"
quality_floor: "0.8"
---

# Provider probe first

**Rule: you cannot diagnose a verdict you did not prove was produced.**

A gate, a routine, and a model call all report failure the same way. Only one of those
three is a real verdict. Prove which one you are looking at before you write a cause down.

## The check (run this before any diagnosis)

1. Hit the provider's health or models endpoint and record the HTTP code:

   ```bash
   curl -sS -m 5 -o /dev/null -w '%{http_code}\n' "$ENDPOINT/v1/models"
   ```

2. Then make ONE real completion and require **non-empty content**.
   `/models` answering 200 proves nothing. A credit-exhausted key still serves `/models`.

3. Record the receipt in the diagnosis: endpoint, HTTP code, timestamp, and whether
   the completion returned content.

Interpret the codes the same way every time:

| Observed | Means | Fix |
|---|---|---|
| `rc=7` connection refused | host up, that service down | restart the service, not the node |
| `rc=28` timeout | off-LAN or port filtered | check the node, not the service |
| `401` | up, needs auth | fix the key |
| `402` / "credit balance is too low" | **out of credits** | this is billing, not logic |
| `429` / "account is not active" | account state | billing or account, not logic |
| `200` + empty content | budget too small or reasoning tokens | raise the token budget before concluding it is broken |

## Why this exists

2026-09-25 14:30 - TypeSafe returned `HTTP 402 · no available TypeSafe API credits`.
Every Jev lane reported a **gate failure**: Wax On batch 5 showed 0 comments, the s14
slice returned no verdict, jobhunt returned BLOCK. The rubrics were fine. Nothing was
wrong with any code. The failure was money.

The same class of false diagnosis had already been written into five memory pages and a
routine's own memory earlier that week, when the real answer was also a credit error and
was already recorded in memory from the day before.

## Hard rules

- A diagnosis without a probe receipt is **not a diagnosis**. Say "BLOCKED: provider
  unprobed" instead of guessing.
- Never report a verdict as meaningful when the provider call did not succeed.
- Re-probe before repeating an old diagnosis. Provider state changes hourly.
- `200` from a health endpoint is not proof. Non-empty completion content is proof.
