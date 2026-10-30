---
name: "subagent-model-pinning"
description: "Pin the model explicitly on every subagent or worker spawn, and name its fallback chain in the prompt. Prompt-level model instructions are ignored. Use whenever spawning a subagent, background worker, parallel lane, or dispatching to a coding agent. Trigger on: 'spawn', 'subagent', 'run this in the background', 'delegate', 'dispatch'."
when_to_use: "At every spawn or dispatch call. The model is a parameter, not an instruction."
version: "1.0.0"
status: "active"
outcome: "agent-engineering: every spawn carries an explicit approved model and a named fallback chain; no worker lands on a Flash-class model"
done_when:
  - 'grep:capabilities/skills/subagent-model-pinning/SKILL.md:the model is a spawn parameter\. Text in the prompt is not a control'
great_example: "examples/great/agent-engineering/subagent-model-pinning.md"
quality_floor: "0.8"
---

# Subagent model pinning

**Rule: the model is a spawn parameter. Text in the prompt is not a control.**

## The check (every spawn, no exceptions)

1. Pass the model explicitly: `model: { provider, modelId }` - never rely on a default.
2. Put the fallback chain in the prompt, verbatim:

   > MODEL ROUTING: if your model errors or is unavailable, do NOT fall back to a Flash
   > model (no Blackwell Flash, MiMo Flash, Gemini Flash). Fall back in this order:
   > `mimo-plan/mimo-v2.6-pro`, then `xai-oauth/grok-4.7`, then `anthropic/claude-opus-5-5`.

3. Read the returned `model:` field back and confirm it is on the approved chain.
   If it is not, do not accept the output as-is. Respawn with the pin.
4. If a subagent cannot name its fallback, **do not spawn it.**

## Approved chain

`mimo-plan/mimo-v2.6-pro` → `xai-oauth/grok-4.7` → `anthropic/claude-opus-5-5`

Flash-class models (Blackwell Flash, MiMo Flash, Gemini Flash) are **never** a fallback,
and never a destination.

## Why this exists

2026-09-25 - a background subagent whose only instruction about models was prompt-level
text came back on `zai/glm-5.3-flash`. The instruction was present in the prompt and had
no effect whatsoever. Only the explicit `model` parameter controlled the outcome.

This matters beyond preference: a worker running on an unapproved model is doing work you
did not authorize and cannot vouch for, and its output enters the record as if it came
from the approved chain.
