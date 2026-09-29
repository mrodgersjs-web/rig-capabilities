---
id: app-studio-web-frontend
version: 3
status: draft
updated: 2026-09-28
task: App Studio web-frontend stage prompt: every contract page returns real server-rendered content from the production build
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: web frontend pages server rendered pages for the app
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | lessons LA-09 LA-10 LA-11 LA-23 LA-25 TG-14 TG-27 BENCH-02 LA-36 LA-37 | uncalibrated
tier: main
parent: app-studio-meta
stage: web-frontend
audience: builder
lessons: LA-09 LA-10 LA-11 LA-23 LA-25 TG-14 TG-27 BENCH-02 LA-36 LA-37
jev_gate: app.prompt
jev_decision: 121885
content_sha256: 59593e6881983413b29717571dfe4f0275dda3f9cf2f886d5f1ea708b89e44bc
---

# Stage 6: web-frontend (App Studio main prompt, v3)

Contract
- id: app-studio-web-frontend | version: 3 | tier: main (stage) | parent: app-studio-meta | stage: web-frontend | audience: builder
- inputs: {{CONTRACT}} page lines, spec.md screen map
- output: pages that return 200 with the app's name and primary content in the server HTML, recorded in .app-studio/stages/web-frontend.md
- lessons carried (each one is an instruction to follow):
  - LA-09: After a fresh production build and next start, fetch every file under public/ and require HTTP 200 (next start serves only files present at build time), and compare the NEXT_PUBLIC_* names used in source with the built client bundle (a name still read as process.env.NEXT_PUBLIC_* in .next/static was not inlined at build time).
  - LA-10: Click through the wasm feature in the production build and scope wasm-unsafe-eval to its path instead of weakening the global CSP.
  - LA-11: Confirm every changed bundled asset URL is content-hashed and that the served URL changed, because an immutable cache on an unhashed URL keeps returning visitors on the old file.
  - LA-23: Confirm a UI defect on the rendered screen and find the enclosing conditional before reporting it; source proves code exists, not that it renders.
  - LA-25: Curl the exact local URL for a 200 and the expected content before claiming a local surface is up; a keepalive supervisor does not prove liveness.
  - TG-14: Keep / (and every public page) in the auth middleware's public-route list; a deployed landing page that demands sign-in is a shipped bug. (TubeGuruji videos: zjwj21wzs4U)
  - TG-27: Whitelist remote image hosts in next.config and restart the server; config does not hot-reload. (TubeGuruji videos: OTTZEwWN4l4)
  - BENCH-02: Server-render the app name and primary content of every contract page so a raw GET without JavaScript proves the page. (evidence: a working app failed its home-page check on 2026-09-28 because the raw HTML lacked the expected text (run 6415a483, P1))
  - LA-36: Reproduce a hydration mismatch on first load and after client navigation, then fix the diverging value at its source (a mounted gate, skipHydration with an explicit rehydrate, one shared formatter, or a client-only import); suppressHydrationWarning is allowed only on the one element whose value the server cannot know (the theme attribute), never to hide a data mismatch.
  - LA-37: One failed request never blanks a screen or replaces the app with a raw error popup: check response.ok on every fetch, render an in-page error state for the failed section only, and make every catch fix, rethrow or log with context; prove it by forcing one request to fail and capturing the rest of the screen still rendered.
- gates: library gate app.prompt on this text; output gate app.stage-gate plus website.buyer (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: for every page in the contract, `curl -s http://127.0.0.1:<port><path>` against the production server returns 200 and HTML containing the app name, with the command and a grep count in the Evidence block
- stop: stop and report BLOCKED: <route> when a page cannot render without a missing credential and no named fallback exists; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval
- sub-prompts owned: app-sub-ssr-first-paint, app-sub-next-build-time, app-sub-error-states

Question this stage answers: does each route or component pass its check in the production build?

1. Server-render each page's name and primary content (app-sub-ssr-first-paint). On 2026-09-28 a working app failed its home-page check because the raw HTML lacked the app's name (BENCH-02).
2. Keep / and every public page outside any auth wall (TG-14).
3. Files under public/ and NEXT_PUBLIC_ values are fixed at build time: rebuild and restart after changing them (app-sub-next-build-time, LA-09).
4. Forms call the real API and show the API's error message on failure.
5. Remote image hosts go in next.config, then restart (TG-27). WASM features are clicked through in the production build (LA-10); bundled asset URLs stay content-hashed (LA-11).
6. Confirm any UI defect on the rendered page before reporting it (LA-23).
7. Fix hydration mismatches at the source (app-sub-ssr-first-paint, LA-36), and never let one failed request blank a screen (app-sub-error-states, LA-37).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
