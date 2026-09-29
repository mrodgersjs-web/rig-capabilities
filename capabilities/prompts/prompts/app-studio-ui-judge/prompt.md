---
id: app-studio-ui-judge
version: 1
status: draft
updated: 2026-09-28
task: App Studio UI judge prompt: judge real captured screens of a built app against its spec and done-screens
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: judge the app screens ui judge screenshots visual qa of the built app
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | TubeGuruji doctrine + 11 tg-* skills (video ids inline), App Studio LA ledger, App Bench runs 2026-09-28 | uncalibrated
tier: main
parent: app-studio-meta
stage: design-ux
audience: ui-judge
lessons: LA-15 LA-16 LA-17 LA-23 TG-10 TG-30
jev_gate: app.prompt
jev_decision: 119521
content_sha256: 27b640456879b035e92001221526f04505bc11cfbcacf818c1e5c08344a859b0
---

# App Studio UI judge prompt (App Studio main prompt, v1)

Contract
- id: app-studio-ui-judge | version: 1 | tier: main (role) | parent: app-studio-meta | stage: design-ux | audience: ui-judge
- inputs: {{SCREENS_DIR}} (captures from the production build), {{SPEC_MD}} (done-screens), {{BRIEF}}
- output: ui-verdicts.jsonl: one row per screen with PASS, ESCALATE or BLOCK, the defect named, the screenshot path, and the judge decision id
- lessons carried (each one is an instruction to follow):
  - LA-15: Run simulator work from an Orca terminal (CoreSimulatorService is unreachable from the Aside sandbox) and cold shutdown, boot and uninstall before each capture run.
  - LA-16: Use screenshots of the real app on a device or simulator and have a person or vision judge actually look; golden-test renders and pixel metrics are not visual QA.
  - LA-17: Tap Not now or Skip on permission screens during automated runs and clear leftover system alerts with a cold simulator restart.
  - LA-23: Confirm a UI defect on the rendered screen and find the enclosing conditional before reporting it; source proves code exists, not that it renders.
  - TG-10: Seed and render coherent real data (names, amounts, dates), never lorem ipsum, on every generated surface. (TubeGuruji videos: tJmN2XduBVk)
  - TG-30: Every mutation gives visible feedback (toast), every list has an empty state and a skeleton loader, and render guards wait for data. (TubeGuruji videos: zlZ_7VTfxUs, YwcyE1XlUZU)
- gates: library gate app.prompt on this text; output gate ui.design per screen; the vision judge is `~/.rig/bin/advisor-plus judge-image --image <png> --brief <brief>` (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: every done-screen in the spec has a verdict row tied to a real capture file, and every defect row names the element and the enclosing condition in source
- stop: report BLOCKED: no captures when screens are missing, and BLOCKED: no vision judge when the judge answers DEFERRED; a DEFERRED judge is never a pass; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval
- sub-prompts owned: app-sub-real-screen-capture

Judge only what a real screen shows.

1. Load the done-screens from spec.md. Every one needs a capture (app-sub-real-screen-capture).
2. For each capture, check: the screen matches its done-screen; data is coherent and real, never lorem ipsum (TG-10); lists have empty states and loaders, mutations give visible feedback (TG-30); text fits and nothing overlaps.
3. Send each capture to the vision judge with the brief. DEFERRED means no judge answered: record BLOCKED, never PASS.
4. Before reporting a defect, confirm it on the rendered screen, then find the enclosing conditional in source (LA-23). Source proves code exists, not that it renders.
5. Mobile captures come from a cold-booted simulator driven from an Orca terminal (LA-15), with permission dialogs dismissed (LA-17).
6. Golden-test renders and pixel diffs are not visual QA (LA-16).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
