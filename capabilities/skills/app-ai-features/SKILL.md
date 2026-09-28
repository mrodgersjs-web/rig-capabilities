---
name: app-ai-features
description: "App Studio sub-skill, stage 8 (ai-features): ship LLM, agent, RAG, voice, and media features inside web and mobile apps with a deterministic backbone, typed judgments on a System One model instead of prompt-and-parse, schema-validated outputs, env-gated vendors with named fallbacks, durable jobs for long generation, and consent before user data leaves the device."
tags: [rig, app-studio, sub-skill, ai, llm, agents, rag, voice, media]
metadata:
  parent: app-studio
  tier: sub
  stage: ai-features
  extends: "tg-durable-ai-pipelines, tg-ai-media-pipeline, tg-voice-agent-stack, typesafe-ai, zazen-rag-microservice"
outcome: "An AI feature that runs without paid keys through named fallbacks, validates every model output against a schema, routes typed decisions to code or a System One model, runs long work as durable steps with progress, and carries an app.stage-gate receipt."
activation: "Load for any chat, agent, RAG, classification, voice, image, video, or generation feature inside an app."
instruction: "Put policy and classification in code or a System One model first, let the LLM own narrative only, validate outputs against a schema, env-gate each vendor with a named fallback, move long generation into durable steps, and gate the slice."
applies_when:
  env: "local development with mock responders; production keys only behind env gates"
  runtime: "Next.js server routes, Inngest or Trigger.dev steps, Flutter or React Native clients"
  deps: "Zod or equivalent schema library; TypeSafe Jev for typed judgments; vendor SDKs behind env gates"
  params: "model per call; quota per user; consent flag for remote AI"
  budget: "cost capped by quota gates; free daily credits first"
  scale: "single app"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - Separate deterministic policy from generated narrative before any model call.
  - Route typed judgments to code or a System One model instead of a frontier prompt.
  - Validate every model output against a schema and handle the failure branch.
  - Env-gate each vendor with a named fallback and move long work into durable steps.
  - Gate the feature slice with rig-s1gate app.stage-gate and code.diff.
done_when:
  - "grep:capabilities/skills/app-ai-features/SKILL.md:LA-07"
  - "grep:capabilities/skills/app-ai-features/SKILL.md:deterministic backbone"
  - "grep:capabilities/skills/app-ai-features/SKILL.md:typesafe-ai"
  - "cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py"
great_example: examples/great/code-engineering/great-tg-voice-agent-saas.md
out_of_scope:
  - model training or fine-tuning
  - paid model routes without a fallback (Mike's local-first policy)
  - quoting vendor speed or cost claims as measured facts
---

# app-ai-features

JEV FIRST, binding on every ai-features step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call; this stage's verdicts go to `rig-s1gate check app.stage-gate` and `code.diff`. When the classifier is
unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9;
below that the stage does not advance, and an uncalibrated ESCALATE is a held transition.

## Load surface

Always loaded at the start of every ai-features task: the `app-studio` meta-skill routes
stage 8 here and `app-studio-conductor` loads it from its routes table before the
stage's first action. It is a task-start surface, not a deep reference an agent
must already know about.

Sub-skill of `app-studio`, stage 8 of 11. Main skills it extends: `tg-durable-ai-pipelines`,
`tg-ai-media-pipeline`, `tg-voice-agent-stack`, `typesafe-ai`, `zazen-rag-microservice`.

## Procedure

1. **Deterministic backbone, LLM for narrative.** TransformFit's live coach is the
   pattern: policy and safety classification run before any remote call, a blocked call
   returns a deterministic route, and the LLM owns narrative only with a flagged
   deterministic fallback (memory/projects/transformfit-qa.md#L34).
2. **Typed judgments are not prompts.** Classification, routing, verification, and
   ranking inside the app are System One calls with a fixed answer set consumed by code
   (`typesafe-ai`), not a frontier prompt whose text gets parsed.
3. **Schema-validated outputs.** Every model response parses against a schema before use:
   the Grok Bot clone validates `answer, steps, toolCalls, usedDesktop, summary` with Zod
   in `agent-response-schema.ts`. Handle the parse-failure branch visibly.
4. **Named fallbacks (LA-07).** Each vendor module returns the real client when its key
   exists and a named fallback otherwise (mock responder, static tool list, mock desktop
   viewer), so every route runs with zero paid keys and the BLOCKED list names what is
   missing.
5. **Long generation is durable.** Multi-step generation (script, voice, captions, images,
   render) runs as durable steps with per-step progress, never inside a request handler
   (tubeguruji-doctrine law 5).
6. **Consent before data leaves the device.** Remote AI stays off by default behind an
   explicit named-destination consent where user data would leave the device, as
   TransformFit's `remote_ai_consent` does.
7. **Cost is a gate.** Quotas and credits cap spend and are proven at limit+1 (LA-08).
8. **Gate** with `app.stage-gate` on the slice record and `code.diff` on the diff.
