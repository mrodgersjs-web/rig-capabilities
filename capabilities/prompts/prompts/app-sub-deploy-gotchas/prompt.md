---
id: app-sub-deploy-gotchas
version: 2
status: draft
updated: 2026-09-28
task: App Studio sub-prompt: the after-approval deploy checklist distilled from shipped-broken deploys
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: deploy gotcha checklist
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | lessons LA-11 LA-13 LA-14 TG-13 TG-15 TG-19 TG-27 TG-28 LA-46 | uncalibrated
tier: sub
parent: app-studio-ship-release
stage: ship-release
audience: builder
lessons: LA-11 LA-13 LA-14 TG-13 TG-15 TG-19 TG-27 TG-28 LA-46
jev_gate: app.prompt
jev_decision: 121882
content_sha256: 939d1c266b197eee4340c04f2458d3d6983ac5ea5b469d7c5eebbc8a56ca4724
---

# Deploy-day gotcha checklist (App Studio sub prompt, v2)

Contract
- id: app-sub-deploy-gotchas | version: 2 | tier: sub | parent: app-studio-ship-release | stage: ship-release | audience: builder
- inputs: {{STACK}}
- output: a Post-approval checklist section in the release request, one line per applicable item
- lessons carried (each one is an instruction to follow):
  - LA-11: Confirm every changed bundled asset URL is content-hashed and that the served URL changed, because an immutable cache on an unhashed URL keeps returning visitors on the old file.
  - LA-13: Prove production identity by sha256 of the live page against candidate deployment URLs, not by deploy metadata or CDN cache headers.
  - LA-14: After any env change, redeploy without build cache and confirm the new value is in effect on the served build.
  - TG-13: After any env change, redeploy without the build cache and confirm the new value is live. (TubeGuruji videos: zrdbOx0eGtM, s28yOCBVgGw)
  - TG-15: Before real users: production OAuth origins and redirect URIs, the Clerk production instance, and both login and logout redirect URLs. (TubeGuruji videos: fh1s6UbzJ7k, hCSX5zSb3b4, saoW6BaNamc, zrdbOx0eGtM)
  - TG-19: Expect production data stores and job dashboards to start empty; swap dev deployment URLs and keys for production ones. (TubeGuruji videos: fh1s6UbzJ7k, UgLN9O930vE, b_4Z_QpEd2Q)
  - TG-27: Whitelist remote image hosts in next.config and restart the server; config does not hot-reload. (TubeGuruji videos: OTTZEwWN4l4)
  - TG-28: Webhooks never reach localhost: use a tunnel in development and seed demo credits directly. (TubeGuruji videos: O_f55bWzsik)
  - LA-46: Before a deploy request, add the single-page-app catch-all rewrite to index.html and make the cookie secure flag depend on the environment; prove one deep-link refresh and one login and logout on each environment.
- gates: library gate app.prompt on this text; output gate app.ship (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: each applicable item has the command or dashboard action that proves it, and each inapplicable one says why
- stop: stop and report BLOCKED: <item> when an item cannot be checked; the checklist runs only after Mike approves the release, and before that it stays text; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval

Include each item that applies:
1. Env changed: redeploy without build cache, then confirm the new value is served (LA-14, TG-13).
2. OAuth: production origins and redirect URIs; Clerk production instance; login and logout redirects (TG-15).
3. Data and jobs: production starts empty; swap dev URLs and keys; sync the job runner (TG-19).
4. Webhooks: register the production URL; dev used a tunnel (TG-28).
5. Remote images whitelisted in next.config (TG-27).
6. Asset URLs content-hashed (LA-11); production identity by sha256 of the live page (LA-13).
7. Single-page apps get the catch-all rewrite to index.html, and the cookie secure flag depends on the environment; prove one deep-link refresh and one login and logout per environment (LA-46; creators CH-JSM-05, CH-CWA-03).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
