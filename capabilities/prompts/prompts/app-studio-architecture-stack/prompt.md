---
id: app-studio-architecture-stack
version: 2
status: draft
updated: 2026-09-28
task: App Studio architecture-stack stage prompt: record the stack the task names, what builds in the sandbox, and a named fallback per paid vendor
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: app stack decision write stack.md
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | lessons LA-01 LA-07 LA-32 TG-03 TG-29 BENCH-05 LA-48 LA-51 | uncalibrated
tier: main
parent: app-studio-meta
stage: architecture-stack
audience: builder
lessons: LA-01 LA-07 LA-32 TG-03 TG-29 BENCH-05 LA-48 LA-51
jev_gate: app.prompt
jev_decision: 121870
content_sha256: 71600a136266d8f63d3f9e1559017036dffbc0e5533f6cec31f6e8cf14d9c9ad
---

# Stage 2: architecture-stack (App Studio main prompt, v2)

Contract
- id: app-studio-architecture-stack | version: 2 | tier: main (stage) | parent: app-studio-meta | stage: architecture-stack | audience: builder
- inputs: {{STACK}}, {{SERVE}}, {{OUT_OF_SCOPE}}
- output: .app-studio/stack.md in the app-sub-stack-md format and the record .app-studio/stages/architecture-stack.md
- lessons carried (each one is an instruction to follow):
  - LA-01: Confirm the toolchain avoids native .node binaries in the Aside sandbox: next --webpack, Tailwind v3, npm i --ignore-scripts, PGlite as a standalone service.
  - LA-07: Env-gate each paid vendor with a NAMED fallback so the app runs without the key, and list missing credentials exactly in a BLOCKED list.
  - LA-32: Do not rely on an agent's own sandbox inside the Aside sandbox: run it in its configured mode with secrets scrubbed from its env, one folder in scope, and a hard time cap.
  - TG-03: Choose each vendor by its free tier first and name the paid upgrade; pay only when the product forces it. (TubeGuruji videos: ciXiibK7Gds, cxto0P5DSYU)
  - TG-29: The corpus skips tests and security (keys in source lUMIj6I9fR8, RLS disabled bpP7PKuEjgI): add tests with assertions and keep keys and access rules on. (TubeGuruji videos: lUMIj6I9fR8, bpP7PKuEjgI)
  - BENCH-05: Name the lane on stack.md's first line (Lane: web SaaS, mobile app, ...) and say why the stack fits it. (evidence: bench stage gates held architecture-stack with app.stack lane_named at 0.26-0.28 when the lane was only implied (Fork T measurement, 2026-09-28))
  - LA-48: Record the dependency versions the code was written against; run a docs or tutorial snippet as written and diff it against the installed versions before adopting it; extend an out-of-date vendor type locally with a note instead of casting it away.
  - LA-51: Use one package manager per project, prove install and build with it, and record any forced resolution (legacy-peer-deps or an override) with the package that forced it instead of hand-editing versions.
- gates: library gate app.prompt on this text; output gate app.stage-gate plus app.stack on stack.md (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: `head -1 .app-studio/stack.md` prints the lane line, `test -s .app-studio/stack.md` exits 0, and stack.md shows each layer from the task, its sandbox constraint, and for each paid vendor the env var name and its named fallback
- stop: stop and report BLOCKED: <layer> when a layer the task names cannot build in this sandbox and the task gives no alternative; never swap the named stack silently; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval
- sub-prompts owned: app-sub-stack-md, app-sub-named-fallbacks

Question this stage answers: which stack fits this lane, and where will it actually build?

1. Name the lane on stack.md's first line (BENCH-05). Use the stack the task names; a substitution needs a written reason in stack.md, never a silent swap.
2. Check each layer against the sandbox before choosing versions: no native .node binaries, so next --webpack, Tailwind v3, and npm install --ignore-scripts (LA-01).
3. Pick free tiers first and name the paid upgrade (TG-03).
4. Give every paid vendor an env var name and a named fallback so the app runs without the key (LA-07, app-sub-named-fallbacks).
5. Tests with assertions and keys kept out of source are RIG additions the corpus skips; plan both here (TG-29).
6. Write stack.md (app-sub-stack-md).
7. Record the versions the code is written against and use one package manager; any forced resolution is written down with the package that forced it (LA-48, LA-51).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
