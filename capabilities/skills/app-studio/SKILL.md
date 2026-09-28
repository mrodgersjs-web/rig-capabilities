---
name: app-studio
description: "META skill for building web and mobile apps at RIG (the App Studio): routes every app build through eleven stages, each with a RIG sub-skill, the estate's main skills (161, JEV-classified from 1,404 candidates), and agents, harnesses, loops, hooks, and JEV criteria at meta, main, and sub tiers, plus 30 typed lessons that fire as gates. Use to build, clone, rebuild, verify, or ship a web app, site, SaaS, internal tool, or iOS or Android app. Fail-closed: transitions defer when JEV is down; anything public stops at Gate-D."
tags: [rig, meta-skill, app-studio, web, mobile, fullstack, build]
metadata:
  tier: meta
  purpose: meta-skill
  category: code-engineering
  family: app-studio
  built: "2026-09-27"
outcome: "An app mission run stage by stage: gated spec and stack, slices ending in executed checks, app.stage-gate receipts on every transition, judged real screens, independent verification, anything public held at Gate-D, and lessons that reach the ledger and their sub-skills."
activation: "Load first for any request to build, clone, rebuild, extend, verify, or ship a web or mobile application, and whenever when-shipping-code or when-designing-interfaces routes an app build here."
instruction: "Name the stage, fire the lessons for the task, load exactly that stage's sub-skill, use the main skills it names, gate the stage transition with rig-s1gate app.stage-gate, and hand orchestration to app-studio-conductor under the app-studio-session harness. Never scaffold on an ungated spec; never ship past Gate-D."
applies_when:
  env: "a project Mike named; the Aside sandbox for web builds, Orca terminals for Xcode and simulators"
  runtime: "Next.js, React, Vite web apps; Expo, React Native, Flutter mobile apps"
  deps: "rig-capabilities checked out; rig-s1gate with the app.* rubrics; experience-lesson-records validator"
  params: "mission name, source (request, video, document, existing app), lane, target (web host or store)"
  budget: "stage by stage; three fix attempts per slice before escalating"
  scale: "one app per mission; not multi-tenant enterprise architecture"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
  - net.api-calls
  - gate-d-required:deploy
  - gate-d-required:push
  - gate-d-required:publish
  - gate-d-required:purchase
flow:
  - Name the stage the task is in and fire the App Studio lessons for its text.
  - Load exactly one stage sub-skill and the main skills it names.
  - Build in slices that each end in an executed check.
  - Gate every stage transition with rig-s1gate app.stage-gate and the stage rubric.
  - Hold anything public at Gate-D and close through app-close-and-learn.
done_when:
  - "cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py"
  - "cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py --plant bad_path; test $? -eq 2"
  - "cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py --plant unwired_sub; test $? -eq 2"
  - "cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/app-studio/references/lessons.jsonl"
  - "cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/app-studio/references/lessons.jsonl --run capabilities/skills/app-studio/fixtures/run_web_build_missing_receipt.jsonl; test $? -eq 2"
  - "file:capabilities/skills/app-studio/references/inventory.md"
great_example: examples/great/code-engineering/great-app-studio-mission.md
out_of_scope:
  - deploys, pushes, domains, purchases, or app store submissions without Mike's recorded approval
  - projects Mike did not name (First Mate home rule)
  - marketing copy, social posts, and brand imagery owned by other lanes (Eden)
  - enterprise multi-tenant, compliance, or SOC2 architecture
---

# App Studio

JEV FIRST, and it binds every app build under this skill: an agent whose only context is
this excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path
BEFORE any frontier LLM call. Spec verdicts, stack verdicts, stage transitions, screen
verdicts, and release readiness are typed judgments, not vibes. When the fast classifier is
unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9;
below that the stage does not advance, and an uncalibrated ESCALATE is a held transition.

## Load surface

This meta-skill is an always-loaded task-start surface for app building: the
`app-studio-session` harness names it as its parent doctrine, `app-studio-conductor` loads
it before its first action, and `when-shipping-code` routes app builds here. It is the
front door for the family, not a deep reference an agent must already know about.
Every path and command in this family is relative to the canonical repo
`~/Developer/rig-capabilities`; installed copies in other harness roots run from there.

## Decision routing (binding)

Route each typed decision first match wins: CODE (preflight tables, exit codes, the lesson
ledger, the stack defaults) -> JEV (`app.stage-gate`, `app.spec`, `app.stack`, `app.ship`,
`app.inventory-fit`, plus reused `plan.readiness`, `ui.design`, `code.diff`, `mission.completion`)
-> SYSTEM 2 (writing features) -> HUMAN (Gate-D for deploy, push, domain, purchase, store
submission). Full map: `references/jev-decisions.md`.

## Org chart (meta, main, sub across six kinds)

| Kind | Meta (one) | Main | Sub |
|---|---|---|---|
| Skills | `app-studio` (this) | 161 estate skills: 144 JEV-included by `app.inventory-fit` plus 17 reused ones the subs extend (full list: `hierarchy.json`, `references/inventory.md`) | 13 RIG sub-skills, one or more per stage (router below) |
| Agents | `app-studio-conductor` | tg-web-builder, tg-mobile-builder, tg-ship-verifier, voltagent-nextjs-developer, voltagent-frontend-developer, voltagent-fullstack-developer, voltagent-mobile-app-developer, ae-frontend-engineer | tg-corpus-miner, tg-integration-fitter, tg-deploy-check-runner, app-sandbox-preflight, app-ui-judge, app-lesson-filer |
| Harnesses | `app-studio-session` | tg-app-studio-session (video-clone lane), hA-03 test writing, hA-04 debug, hA-06 perf audit, hA-09 API design, hA-10 schema design, hA-12 CI/CD, hA-13 security audit, hC-02 UI design, hC-06 accessibility, hC-07 mobile design | app-sandbox-build-verify, app-web-release, app-mobile-release, tg-corpus-mining, tg-skeleton-implementation, tg-ship-verify, tg-auth-schema-wiring, tg-background-jobs, tg-deploy-checklist |
| Loops | `app-studio-mission-loop` | iqrsqpi-v20, phase-discipline-loop, proof-loop, adversarial-verification-loop, gate-d-loop, git-push-safety-loop, coding-harness, doer-checker-validator | app-slice-loop, app-ui-judge-loop, app-lesson-promotion-loop, iqrsqpi-v20-slice |
| Hooks | `app-studio-hook` (dispatcher, dormant until wired) | guard-secret-write, guard-dangerous-commands, s1gate-stage-gate, rig-loop-hook, tac-plan-gate | app-native-binary-preflight, app-single-builder-guard, app-env-commit-guard |
| JEV criteria | `app.stage-gate` | plan.readiness, code.diff, code.review, api.backend, ui.design, website.buyer, mission.completion, atomic.claim, doctrine.surface | app.spec, app.stack, app.ship, app.inventory-fit |

Machine-readable copy: `hierarchy.json` (generated by `scripts/build_hierarchy.py`;
edit the script, not the JSON). `scripts/validate_hierarchy.py` proves every path resolves,
every sub reaches its meta, every sub is named by its parent's file, and every stage is
covered.

## Stage router

| # | Stage | Sub-skill | Main skills to reach for | Agent | Harness | JEV |
|---|---|---|---|---|---|---|
| 1 | intake-spec | `app-intake-spec` | tubeguruji-doctrine, iqrsqpi-v20, ultraplan, grill-with-ui | tg-corpus-miner (video clones) | tg-app-studio-session | app.spec, plan.readiness |
| 2 | architecture-stack | `app-stack-select` | tubeguruji-doctrine, advise-project-approach, fullstack-developer | conductor | app-studio-session A2 | app.stack |
| 3 | design-ux | `app-ui-design` | when-designing-interfaces, impeccable, baseline-ui, fixing-accessibility | app-ui-judge | hC-02, hC-06 | ui.design |
| 4 | scaffold-setup | `app-sandbox-survival`, `app-web-scaffold` | tg-saas-skeleton, dotenv, turborepo-caching | app-sandbox-preflight, tg-web-builder | app-sandbox-build-verify, tg-skeleton-implementation | app.stage-gate |
| 5 | backend-data | `app-data-layer` | tg-auth-wiring, auth-implementation-patterns, database-migrations, prisma-patterns, supabase-postgres-best-practices, stripe-integration | tg-web-builder, tg-integration-fitter | hA-09, hA-10, tg-auth-schema-wiring, tg-background-jobs | api.backend |
| 6 | web-frontend | `app-web-frontend` | nextjs-app-router-patterns, next-best-practices, react-best-practices, shadcn-ui | tg-web-builder, voltagent-nextjs-developer | app-sandbox-build-verify | code.diff |
| 7 | mobile | `app-mobile-build` | tg-expo-mobile-ai, react-native-architecture, dart-flutter-patterns, flutter-production-build | tg-mobile-builder, voltagent-mobile-app-developer | hC-07 | app.stage-gate, ui.design |
| 8 | ai-features | `app-ai-features` | tg-durable-ai-pipelines, tg-ai-media-pipeline, tg-voice-agent-stack, typesafe-ai | tg-integration-fitter | tg-background-jobs | code.diff |
| 9 | verify-qa | `app-verify-evidence` | tdd, e2e-testing, react-testing, testsprite-engineering, gstack-qa | tg-ship-verifier, app-ui-judge | hA-03, hA-04, hA-13, tg-ship-verify | code.review |
| 10 | ship-release | `app-ship-web`, `app-ship-mobile` | vercel-deploy-doctrine, tg-deploy-gotchas, web-build-ship, app-store-ship, flutter-store-deployment | tg-deploy-check-runner | app-web-release, app-mobile-release, hA-12 | app.ship + Gate-D |
| 11 | operate-learn | `app-close-and-learn` | experience-lesson-records, jake-lessons-ledger, canary | app-lesson-filer | app-lesson-promotion-loop | mission.completion, atomic.claim |

Routing contract: load exactly one stage sub-skill per task step; load a main skill only
when that sub-skill names it or the task needs it; if nothing fits, fall back to
`when-shipping-code`. A missing route is reported, never improvised.

## Laws (each earned by a lesson in `references/lessons.jsonl`)

1. **Spec before scaffold.** Every feature row has a source and an executable acceptance
   check, with a limit+1 check on every gate (LA-08).
2. **Build where it can build.** The Aside sandbox blocks native .node binaries and the
   iOS simulator: webpack, Tailwind v3, ignore-scripts, PGlite service, Orca for Xcode (LA-01, LA-15).
3. **One builder, one lock, fresh ports, curl before claiming** (LA-02, LA-03, LA-25, LA-26).
4. **Every paid vendor has a named fallback**; local and free tier first (LA-07).
5. **Evidence or it did not happen.** Slices end in executed checks; tests must be able to
   fail; BLOCKED is not FAILED; plants must move bytes (LA-20, LA-21, LA-27).
6. **Real screens, judged by someone who did not build them** (LA-16, LA-17, LA-23).
7. **Production is proven on the real target by bytes**: hashed assets, preview is render
   only, sha256 identity, no-cache redeploy after env changes (LA-11 to LA-14).
8. **Anything public waits at Gate-D**; store policy is proven on the release build (LA-22).
9. **Lessons land in the ledger and the owning sub-skill in the same session** (LA-28).

## Mission record layout

```
<project>/.app-studio/
  spec.md          stage 1, app.spec receipt
  stack.md         stage 2, app.stack receipt
  stages/          one stage-close record per stage, app.stage-gate receipts
  verify.md        stage 9, verdict and proof per spec row
  release.md       stage 10, app.ship receipt and the Gate-D request id
  run.jsonl        task row, a receipt per fired lesson, close row
  build.lock       single-builder protocol (build.log beside it)
```

The `.app-studio/` folder is also the switch for the hook tier: the native-binary and
single-builder hooks act only inside a project that has one.

## How to run a mission

1. `python3 capabilities/skills/app-studio/scripts/fire_lessons.py "<the task>"` lists the
   checks this run owes.
2. Hand orchestration to `app-studio-conductor` with harness
   `capabilities/harnesses/app-studio-session.yaml` and loop
   `capabilities/loops/app-studio-mission-loop.md`.
3. Follow each stage's sub-skill; gate each transition; keep receipts in `run.jsonl`.
4. Close with `app-close-and-learn`; the run must validate against the ledger.

## Inventory (what the estate already had)

`scripts/build_inventory.py` scanned 3,739 skills, agents, harnesses, loops, and hooks, sent
1,404 candidates through JEV `app.inventory-fit`, and recorded every decision id:
144 skills, 11 agents, and 4 harnesses included above 0.9; 335 skills and 186 agents
in a named review bucket between 0.4 and 0.9; the rest excluded. Hooks and loops are
generic governance, so their main tiers are chosen reuses. Refresh with
`python3 capabilities/skills/app-studio/scripts/build_inventory.py`; re-render without
new JEV calls with `--render-from references/inventory.json`.

## Verify this family

```
python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py
python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py --plant unwired_sub   # must exit 2
python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/app-studio/references/lessons.jsonl
python3 capabilities/skills/app-studio/scripts/hook_cases.py app-studio-hook.sh
```
