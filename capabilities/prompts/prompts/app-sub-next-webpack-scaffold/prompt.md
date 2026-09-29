---
id: app-sub-next-webpack-scaffold
version: 1
status: draft
updated: 2026-09-28
task: App Studio sub-prompt: scaffold Next.js App Router with webpack builds and Tailwind v3 so it builds in the Aside sandbox
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: next.js webpack scaffold
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | TubeGuruji doctrine + 11 tg-* skills (video ids inline), App Studio LA ledger, App Bench runs 2026-09-28 | uncalibrated
tier: sub
parent: app-studio-scaffold-setup
stage: scaffold-setup
audience: builder
lessons: LA-01 TG-12
jev_gate: app.prompt
jev_decision: 119541
content_sha256: d207a4d61bb677f66887ef3da04fca30a139f4bbc76c8ed9d999bbc621ea420f
---

# Next.js scaffold on webpack (App Studio sub prompt, v1)

Contract
- id: app-sub-next-webpack-scaffold | version: 1 | tier: sub | parent: app-studio-scaffold-setup | stage: scaffold-setup | audience: builder
- inputs: {{STACK}}, {{PORT_LO}}
- output: package.json, next.config, tailwind.config, postcss.config, tsconfig.json and app/layout.tsx that build with webpack
- lessons carried (each one is an instruction to follow):
  - LA-01: Confirm the toolchain avoids native .node binaries in the Aside sandbox: next --webpack, Tailwind v3, npm i --ignore-scripts, PGlite as a standalone service.
  - TG-12: Run the production build locally and fix it from the build log before any deploy request. (TubeGuruji videos: -AVtkiG0laE)
- gates: library gate app.prompt on this text; output gate app.stage-gate on the scaffold-setup record (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: `npm run build` exits 0 with webpack, and `npm run start -- -p {{PORT_LO}}` serves / with a 200
- stop: report BLOCKED: <error> after 3 build failures on the same exact error; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval

1. package.json scripts: dev = next dev --webpack, build = next build --webpack, start = next start. No Turbopack anywhere (LA-01).
2. Tailwind v3 with postcss and autoprefixer; content globs cover app/ and components/.
3. Install with npm install --ignore-scripts.
4. TypeScript strict; path alias @/* to the project root.
5. Build, then fix from the build log before adding features (TG-12).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
