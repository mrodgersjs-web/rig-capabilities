---
id: app-studio-ship-release
version: 2
status: draft
updated: 2026-09-28
task: App Studio ship-release stage prompt: prepare a complete release request and hold it at Gate-D
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: ship the app release request held at gate-d
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | lessons LA-11 LA-12 LA-13 LA-14 TG-12 TG-13 TG-15 TG-23 LA-38 | uncalibrated
tier: main
parent: app-studio-meta
stage: ship-release
audience: builder
lessons: LA-11 LA-12 LA-13 LA-14 TG-12 TG-13 TG-15 TG-23 LA-38
jev_gate: app.prompt
jev_decision: 121936
content_sha256: de029e6041a3c6c417d2e2ffff70bd14eec344f3e9127396fd85921fd43cd67a
---

# Stage 10: ship-release (App Studio main prompt, v2)

Contract
- id: app-studio-ship-release | version: 2 | tier: main (stage) | parent: app-studio-meta | stage: ship-release | audience: builder
- inputs: {{STACK}}, the verified build, env var names
- output: .app-studio/stages/ship-release.md with status HELD and a release request in the app-sub-gate-d-hold format
- lessons carried (each one is an instruction to follow):
  - LA-11: Confirm every changed bundled asset URL is content-hashed and that the served URL changed, because an immutable cache on an unhashed URL keeps returning visitors on the old file.
  - LA-12: Report a green preview as a render check only; functional proof that depends on the real domain waits for the Gate-D promote.
  - LA-13: Prove production identity by sha256 of the live page against candidate deployment URLs, not by deploy metadata or CDN cache headers.
  - LA-14: After any env change, redeploy without build cache and confirm the new value is in effect on the served build.
  - TG-12: Run the production build locally and fix it from the build log before any deploy request. (TubeGuruji videos: -AVtkiG0laE)
  - TG-13: After any env change, redeploy without the build cache and confirm the new value is live. (TubeGuruji videos: zrdbOx0eGtM, s28yOCBVgGw)
  - TG-15: Before real users: production OAuth origins and redirect URIs, the Clerk production instance, and both login and logout redirect URLs. (TubeGuruji videos: fh1s6UbzJ7k, hCSX5zSb3b4, saoW6BaNamc, zrdbOx0eGtM)
  - TG-23: A rendered page is not a working deploy: sign in, create one artifact, fire one webhook and run one job on the production URL. (TubeGuruji videos: zrdbOx0eGtM, zjwj21wzs4U)
  - LA-38: Wire error monitoring for the API and the client before the first release and prove one induced error reaches it with request and session context; with no monitoring key, log structured errors with the same context as the named fallback and list the monitoring key in the release request.
- gates: library gate app.prompt on this text; output gate app.stage-gate plus app.ship (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: the release request lists target, exact commands, env var names (never values), rollback, and the post-approval checks, and the stage status reads HELD at Gate-D
- stop: stop at status HELD and report `HELD at Gate-D: <target>`; report BLOCKED: <item> when the local build fails or a release input is missing; never deploy, push, attach a domain or submit to a store from this stage; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval
- sub-prompts owned: app-sub-gate-d-hold, app-sub-deploy-gotchas, app-sub-observability

Question this stage answers: is the release request complete and held at Gate-D?

1. The local production build exits 0 first (TG-12).
2. Write the release request (app-sub-gate-d-hold). HELD at Gate-D is the correct end state for this stage.
3. Attach the post-approval checklist (app-sub-deploy-gotchas): env changes redeploy without cache (LA-14, TG-13), production OAuth settings (TG-15), and the production-URL bar (TG-23).
4. A green preview is a render check only (LA-12). Production identity is proven by sha256 of the live page (LA-13), and asset URLs stay content-hashed (LA-11).
5. Error capture for the API and the client is wired before the release request and proven with one induced error (app-sub-observability, LA-38).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
