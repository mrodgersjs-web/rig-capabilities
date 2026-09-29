---
id: app-sub-real-screen-capture
version: 1
status: draft
updated: 2026-09-28
task: App Studio sub-prompt: capture real screens from the production build or a cold simulator for the UI judge
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: capture real screens
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | TubeGuruji doctrine + 11 tg-* skills (video ids inline), App Studio LA ledger, App Bench runs 2026-09-28 | uncalibrated
tier: sub
parent: app-studio-ui-judge
stage: design-ux
audience: ui-judge
lessons: LA-15 LA-16 LA-17 LA-23
jev_gate: app.prompt
jev_decision: 119545
content_sha256: 673e3e4d2d576a4f12098f6838f52dde208c5f762903574cd4f1ac151a60e37f
---

# Real screen capture (App Studio sub prompt, v1)

Contract
- id: app-sub-real-screen-capture | version: 1 | tier: sub | parent: app-studio-ui-judge | stage: design-ux | audience: ui-judge
- inputs: {{SCREENS_DIR}}, the done-screen routes
- output: one PNG per done-screen in {{SCREENS_DIR}}, named <screen>-<viewport>.png, with the URL and build id beside it
- lessons carried (each one is an instruction to follow):
  - LA-15: Run simulator work from an Orca terminal (CoreSimulatorService is unreachable from the Aside sandbox) and cold shutdown, boot and uninstall before each capture run.
  - LA-16: Use screenshots of the real app on a device or simulator and have a person or vision judge actually look; golden-test renders and pixel metrics are not visual QA.
  - LA-17: Tap Not now or Skip on permission screens during automated runs and clear leftover system alerts with a cold simulator restart.
  - LA-23: Confirm a UI defect on the rendered screen and find the enclosing conditional before reporting it; source proves code exists, not that it renders.
- gates: library gate app.prompt on this text; output gate ui.design (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: each done-screen has a capture file from the production build (web) or a cold-booted simulator (mobile)
- stop: report BLOCKED: capture tool missing; renders and pixel metrics never substitute (LA-16); deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval

1. Web: start the production build, open each route at desktop and mobile widths, wait for data, capture.
2. Mobile: from an Orca terminal, cold shutdown, boot and uninstall, then install and capture (LA-15); dismiss permission dialogs (LA-17).
3. Record URL, viewport and build id per file.
4. Confirm a suspected defect on the capture before reporting it (LA-23).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
