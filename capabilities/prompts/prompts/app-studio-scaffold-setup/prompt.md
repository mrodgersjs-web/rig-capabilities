---
id: app-studio-scaffold-setup
version: 1
status: draft
updated: 2026-09-28
task: App Studio scaffold-setup stage prompt: get a first slice to build, serve and answer curl inside the Aside sandbox
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: scaffold the app first slice builds and serves
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | TubeGuruji doctrine + 11 tg-* skills (video ids inline), App Studio LA ledger, App Bench runs 2026-09-28 | uncalibrated
tier: main
parent: app-studio-meta
stage: scaffold-setup
audience: builder
lessons: LA-01 LA-02 LA-03 LA-25 LA-33 TG-12
jev_gate: app.prompt
jev_decision: 119518
content_sha256: 781c40d5f075e2bc6870dd0558f1323f9d70f785b78c89e7d233fd6dc26d152c
---

# Stage 4: scaffold-setup (App Studio main prompt, v1)

Contract
- id: app-studio-scaffold-setup | version: 1 | tier: main (stage) | parent: app-studio-meta | stage: scaffold-setup | audience: builder
- inputs: {{STACK}}, {{PORT_LO}}, {{PORT_HI}}
- output: a scaffold whose production build exits 0 and serves / with a 200, recorded in .app-studio/stages/scaffold-setup.md
- lessons carried (each one is an instruction to follow):
  - LA-01: Confirm the toolchain avoids native .node binaries in the Aside sandbox: next --webpack, Tailwind v3, npm i --ignore-scripts, PGlite as a standalone service.
  - LA-02: Find PIDs with lsof -t on a file or port the process holds (ps, pgrep and pkill are blocked) and serve a fresh build on a fresh port instead of trusting :3000.
  - LA-03: Confirm exactly one builder runs for this project (no watcher routine or second agent building) and run long builds detached with nohup while polling the log.
  - LA-25: Curl the exact local URL for a 200 and the expected content before claiming a local surface is up; a keepalive supervisor does not prove liveness.
  - LA-33: Unset PYTHONHOME and PYTHONPATH before a child process starts a different Python, because the Aside runtime exports its own and the system python then dies with No module named encodings.
  - TG-12: Run the production build locally and fix it from the build log before any deploy request. (TubeGuruji videos: -AVtkiG0laE)
- gates: library gate app.prompt on this text; output gate app.stage-gate (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: `npm run build` exits 0, `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:{{PORT_LO}}/` prints 200 from the production server, and the server is stopped afterwards
- stop: stop and report BLOCKED: <package> when a dependency needs a native binary the sandbox blocks and no pure-JS alternative exists; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval
- sub-prompts owned: app-sub-sandbox-rules, app-sub-next-webpack-scaffold

Question this stage answers: does a first slice build, serve and answer in this sandbox?

1. Follow the sandbox rules (app-sub-sandbox-rules) before installing anything.
2. Scaffold (app-sub-next-webpack-scaffold for Next.js tasks).
3. Run the production build and fix it from the build log (TG-12).
4. Start the production server on a port in {{PORT_LO}}-{{PORT_HI}} and curl the exact URL (LA-25).
5. Stop it with kill $(lsof -t -i :PORT) (LA-02), and never run two builds at once (LA-03).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
