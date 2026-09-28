---
name: app-ship-web
description: "App Studio sub-skill, stage 10a (ship-release, web): turn a verified web app into a complete Gate-D release request - local production build cited, target env audited, content-hashed assets, preview treated as a render check only - then, after Mike approves, deploy and prove the real target changed by byte identity. A JEV PASS on the release record is never permission to ship."
tags: [rig, app-studio, sub-skill, ship, deploy, vercel, web, gate-d]
metadata:
  parent: app-studio
  tier: sub
  stage: ship-release
  extends: "vercel-deploy-doctrine, tg-deploy-gotchas, web-build-ship, setup-deploy, gstack-ship, golive, production-audit, github-actions-templates, gate-d-loop, git-push-safety-loop"
outcome: "A release record (.app-studio/release.md) with an app.ship receipt, a Gate-D request id held for Mike, and - only after approval - a post-release proof that the live bytes changed and key routes answer."
activation: "Load when a verified web app is ready to go public, when an env var changes on a deployed app, or when someone asks which build is live."
instruction: "Build for production locally, audit env, check asset hashing and cache headers, write the release record, gate it with rig-s1gate app.ship, stop at Gate-D, and after approval deploy and prove the live bytes changed."
applies_when:
  env: "Vercel (CLI at ~/.hermes/node/bin/vercel) or another host Mike already uses"
  runtime: "Next.js, Vite, or static builds"
  deps: "verify record from app-verify-evidence; gate-d-loop for the approval"
  params: "project, target domains (one deploy can alias two), env key list"
  budget: "free-tier hosting until traffic forces spend"
  scale: "one app, one release at a time"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
  - gate-d-required:deploy
  - gate-d-required:push
  - gate-d-required:publish
flow:
  - Run and cite a local production build.
  - Audit the target env and plan a no-cache redeploy for any env change.
  - Confirm changed asset URLs are content-hashed and read their cache headers.
  - Write the release record, gate it with app.ship, and stop at Gate-D.
  - After approval deploy and prove the live bytes changed with sha256 and route checks.
done_when:
  - "file:capabilities/harnesses/s1gate/rubrics/app.ship.json"
  - "grep:capabilities/skills/app-ship-web/SKILL.md:LA-11"
  - "grep:capabilities/skills/app-ship-web/SKILL.md:Gate-D"
  - "cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py"
out_of_scope:
  - any deploy, push, domain change, or purchase without Mike's recorded approval
  - DNS registrar changes
  - mobile store releases (app-ship-mobile)
---

# app-ship-web

JEV FIRST, binding on every ship-release (web) step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call; this stage's verdicts go to `rig-s1gate check app.ship`. When the classifier is
unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9;
below that the stage does not advance, and an uncalibrated ESCALATE is a held transition.

## Load surface

Always loaded at the start of every ship-release (web) task: the `app-studio` meta-skill routes
stage 10 here and `app-studio-conductor` loads it from its routes table before the
stage's first action, and the `app-web-release` harness names it as doctrine. It is a task-start surface, not a deep reference an agent
must already know about.

Sub-skill of `app-studio`, stage 10 of 11 (web half). Main skills it extends:
`vercel-deploy-doctrine`, `tg-deploy-gotchas`, `web-build-ship`, `setup-deploy`,
`gstack-ship`, `golive`, `production-audit`, `github-actions-templates`, `gate-d-loop`,
`git-push-safety-loop`. Sub-process: `app-web-release`.

## Procedure

1. **Local production build first.** Detached under the build lock; cite exit code and
   route count (tubeguruji-doctrine law 7).
2. **Env audit (LA-14).** List every key the target needs and check each is set. Any env
   change means a redeploy without build cache, then confirm the new value is live.
3. **Asset hashing (LA-11).** An `immutable` cache on an unhashed asset URL made a correct
   RIG deploy invisible to returning visitors for up to a year. Every changed bundled
   asset URL must be content-hashed; read `curl -sI <asset>` cache headers.
4. **Preview is a render check (LA-12).** Vercel previews sit behind SSO and hostname
   gates, so consent, attribution, and auth callbacks are proven only on the real domain,
   after the promote.
5. **Release record + gate.** Write `.app-studio/release.md` (build proof, env list,
   post-release checks, rollback) and run `rig-s1gate check app.ship`.
6. **STOP at Gate-D.** File the request (`gate_d_request` or `gate-d-loop`) naming the
   exact target. Record `held_at_gate`. Do not deploy, push, or attach a domain before
   Mike's typed approval.
7. **After approval, prove the target (LA-13).** sha256 the live page and one asset
   against the previous deployment; `vercel inspect` carries no git sha for CLI deploys,
   and CDN `x-vercel-cache` headers describe cache state, not provenance. The RIG project
   aliases `rodgersintelligence.com` and `www.mikerodgers.tech` from one deployment, so
   every promote hits both (memory/episodic/2026-09-24.md#L2320).
8. **Rollback** is named before the deploy: promote the previous production deployment.

## Evidence

memory/episodic/2026-09-17.md#L1845, #L1853; memory/episodic/2026-09-24.md#L2318;
memory/projects/rodgers-intelligence.md#L31.
