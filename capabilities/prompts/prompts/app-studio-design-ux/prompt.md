---
id: app-studio-design-ux
version: 1
status: draft
updated: 2026-09-28
task: App Studio design-ux stage prompt: map the screens onto the SaaS skeleton with real data and plan real captures for judging
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: app screen map design the app screens
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | TubeGuruji doctrine + 11 tg-* skills (video ids inline), App Studio LA ledger, App Bench runs 2026-09-28 | uncalibrated
tier: main
parent: app-studio-meta
stage: design-ux
audience: builder
lessons: TG-02 TG-10 TG-11 TG-30 LA-16 LA-23
jev_gate: app.prompt
jev_decision: 119515
content_sha256: 643bafc06d63dcee212aeb6adae4d647ec0583b2f5dad6281e6a88f494322806
---

# Stage 3: design-ux (App Studio main prompt, v1)

Contract
- id: app-studio-design-ux | version: 1 | tier: main (stage) | parent: app-studio-meta | stage: design-ux | audience: builder
- inputs: spec.md done-screens, {{FEATURES}}, {{CONTRACT}}
- output: a screen map in .app-studio/stages/design-ux.md: route, purpose, components, data shown, empty state, and the capture file each screen will have
- lessons carried (each one is an instruction to follow):
  - TG-02: Build the repeatable skeleton (landing, auth gate, sidebar dashboard, input form with quota, generation with progress, artifact view/share, credits gate); vendors are swaps behind it. (TubeGuruji videos: zcYM_Gqoph4, zjwj21wzs4U)
  - TG-10: Seed and render coherent real data (names, amounts, dates), never lorem ipsum, on every generated surface. (TubeGuruji videos: tJmN2XduBVk)
  - TG-11: Change the smallest component that fixes the issue; do not regenerate the page. (TubeGuruji videos: tJmN2XduBVk, c9qA-uhysIY)
  - TG-30: Every mutation gives visible feedback (toast), every list has an empty state and a skeleton loader, and render guards wait for data. (TubeGuruji videos: zlZ_7VTfxUs, YwcyE1XlUZU)
  - LA-16: Use screenshots of the real app on a device or simulator and have a person or vision judge actually look; golden-test renders and pixel metrics are not visual QA.
  - LA-23: Confirm a UI defect on the rendered screen and find the enclosing conditional before reporting it; source proves code exists, not that it renders.
- gates: library gate app.prompt on this text; output gate app.stage-gate plus ui.design on real captures (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: every done-screen in spec.md has a row in the screen map, and every captured screen has a file path; screens without a capture tool are listed as BLOCKED for visual QA
- stop: report BLOCKED: no capture tool when no screenshot path exists; do not grade your own screens; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval
- sub-prompts owned: app-sub-saas-skeleton

Question this stage answers: what do the screens look like, and do real captures pass the judge?

1. Build the screen map from spec.md along the skeleton (app-sub-saas-skeleton, TG-02).
2. Seed coherent real data: names, amounts and dates that belong to this app, never lorem ipsum (TG-10).
3. Each list gets an empty state and a loader; each mutation gets visible feedback (TG-30).
4. Fix the smallest component that is wrong; never regenerate a whole page (TG-11).
5. You do not grade your own screens. Visual verdicts come from real captures judged by a person or the vision judge (LA-16); a defect is confirmed on the rendered screen before it is reported (LA-23).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
