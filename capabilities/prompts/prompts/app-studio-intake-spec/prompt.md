---
id: app-studio-intake-spec
version: 2
status: draft
updated: 2026-09-28
task: App Studio intake-spec stage prompt: pin what the app is, its source, its done-screens and its contract in spec.md
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: app intake spec write the app spec
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | lessons TG-01 TG-02 LA-16 LA-35 BENCH-01 BENCH-04 | uncalibrated
tier: main
parent: app-studio-meta
stage: intake-spec
audience: builder
lessons: TG-01 TG-02 LA-16 LA-35 BENCH-01 BENCH-04
jev_gate: app.prompt
jev_decision: 121869
content_sha256: 6a6da61fe488f80d563853d50fb034aed7ec698f1aed2787c5ef6bb17242025d
---

# Stage 1: intake-spec (App Studio main prompt, v2)

Contract
- id: app-studio-intake-spec | version: 2 | tier: main (stage) | parent: app-studio-meta | stage: intake-spec | audience: builder
- inputs: {{OUTCOME}}, {{SOURCE}}, {{FEATURES}}, {{CONTRACT}}, {{OUT_OF_SCOPE}}
- output: .app-studio/spec.md in the app-sub-spec-md format and the record .app-studio/stages/intake-spec.md
- lessons carried (each one is an instruction to follow):
  - TG-01: Write the finished app down as a click-through (every screen, its one action, the observable result) before the first file. (TubeGuruji videos: zcYM_Gqoph4, Dsw0pMnblWg, zrdbOx0eGtM)
  - TG-02: Build the repeatable skeleton (landing, auth gate, sidebar dashboard, input form with quota, generation with progress, artifact view/share, credits gate); vendors are swaps behind it. (TubeGuruji videos: zcYM_Gqoph4, zjwj21wzs4U)
  - LA-16: Use screenshots of the real app on a device or simulator and have a person or vision judge actually look; golden-test renders and pixel metrics are not visual QA.
  - LA-35: Search ~/Desktop/Projects and the Memory OS studio map as well as the capability index before building, because the capability index does not cover project folders.
  - BENCH-01: Write .app-studio/spec.md and .app-studio/stack.md before the first source file. (evidence: both builders skipped them on 2026-09-28 and intake-spec and architecture-stack did not advance (runs 6415a483, 9cfde8ad))
  - BENCH-04: Give every feature id in spec.md a Done looks like line: the screen or route, the one action, and the observable result. (evidence: bench stage gates held intake-spec with app.spec done_looks_like at 0.29 when spec.md lacked it (Fork T measurement, 2026-09-28))
- gates: library gate app.prompt on this text; output gate app.stage-gate plus app.spec on spec.md (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: `test -s .app-studio/spec.md` exits 0, and spec.md names the app, lists every feature with its source, gives each feature id a Done looks like line, and copies every contract line verbatim, with those commands in the intake-spec record
- stop: stop and report BLOCKED: spec source missing when the source video, transcript or feature list cannot be read; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval
- sub-prompts owned: app-sub-spec-md, app-sub-acceptance-checks

Question this stage answers: what are we building, from what source, and how will we know it is done?

1. Before any scaffold, write the finished app as a click-through: every screen, the one action on it, and the observable result (TG-01).
2. Map the features onto the skeleton (landing, auth, dashboard, form, generation, artifact, credits) and mark which parts apply (TG-02).
3. When the app rebuilds an existing product, its done-screens come from the real app, never from renders (LA-16).
4. The conductor searches ~/Desktop/Projects and the Memory OS studio map for an existing build before starting a new one (LA-35).
5. Write spec.md (app-sub-spec-md) with a Done looks like line per feature id. Builders that skipped it, or wrote it without those lines, left this stage un-advanced (BENCH-01, BENCH-04).
6. Conductor only: executable acceptance checks are authored here (app-sub-acceptance-checks) and kept out of every builder prompt.

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
