---
name: app-web-scaffold
description: "App Studio sub-skill, stage 4 (scaffold-setup, web): stand up a Next.js App Router project that actually builds and serves inside the Aside sandbox, with env-gated vendors and named fallbacks, a committed .env.example, and slice 0 proven by a green production build, one served route, and a screenshot. Use for every new web app or web clone."
tags: [rig, app-studio, sub-skill, scaffold, nextjs, web]
metadata:
  parent: app-studio
  tier: sub
  stage: scaffold-setup
  extends: "tg-saas-skeleton, nextjs-app-router-patterns, next-best-practices, dotenv, fullstack-developer"
outcome: "A project whose slice 0 is proven: production build exit 0, one route returning 200 on a fresh port, a screenshot, .env.example listing every key with its fallback, and an app.stage-gate receipt."
activation: "Load when a web app's spec and stack are gated and no project exists yet, or when an existing scaffold will not build in the sandbox."
instruction: "Scaffold with the sandbox-safe toolchain, wire env-gated vendor modules with named fallbacks, prove slice 0 with a detached production build, a served route, and a screenshot, then gate the slice record."
applies_when:
  env: "a project folder Mike named under ~/Desktop/Projects or an Orca worktree"
  runtime: "Node 18+, Next.js App Router, TypeScript"
  deps: "approved spec.md and stack.md; npm"
  params: "project name, fresh port, vendor list with fallbacks"
  budget: "under an hour to slice 0"
  scale: "one app"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
flow:
  - Scaffold the Next.js App Router project and switch its scripts to webpack.
  - Install with ignore-scripts and pin Tailwind v3.
  - Write env-gated vendor modules with named fallbacks and a committed .env.example.
  - Prove slice 0 with a detached production build, a served route, and a screenshot.
  - Gate the slice-0 record with rig-s1gate app.stage-gate.
done_when:
  - "grep:capabilities/skills/app-web-scaffold/SKILL.md:--webpack"
  - "grep:capabilities/skills/app-web-scaffold/SKILL.md:LA-09"
  - "file:capabilities/harnesses/s1gate/rubrics/app.stage-gate.json"
  - "cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py"
great_example: examples/great/code-engineering/great-tg-grok-bot-clone.md
out_of_scope:
  - projects Mike did not name (First Mate home rule)
  - mobile apps (app-mobile-build)
  - deploys and domains (app-ship-web, Gate-D)
---

# app-web-scaffold

JEV FIRST, binding on every scaffold-setup step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call; this stage's verdicts go to `rig-s1gate check app.stage-gate`. When the classifier is
unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9;
below that the stage does not advance, and an uncalibrated ESCALATE is a held transition.

## Load surface

Always loaded at the start of every scaffold-setup task: the `app-studio` meta-skill routes
stage 4 here and `app-studio-conductor` loads it from its routes table before the
stage's first action, and the `app-sandbox-build-verify` harness names it as doctrine. It is a task-start surface, not a deep reference an agent
must already know about.

Sub-skill of `app-studio`, stage 4 of 11. Main skills it extends: `tg-saas-skeleton`,
`nextjs-app-router-patterns`, `next-best-practices`, `dotenv`, `fullstack-developer`.
Runs under `app-sandbox-survival` rules the whole time.

## Procedure

1. **Only in a project Mike named.** First Mate home rule: no edits to a project worktree
   he did not name in the request.
2. **Scaffold** with create-next-app (TypeScript, App Router). Then set
   `"dev": "next dev --webpack"`, `"build": "next build --webpack"` in package.json
   (LA-01). Install with `npm i --ignore-scripts`; pin `tailwindcss@3` with postcss and
   autoprefixer.
3. **Env layout.** Commit `.env.example` listing every key, each with a comment naming its
   fallback. Keep `.env.local` out of git (the dormant hook `app-env-commit-guard.sh`
   blocks staging it). One module per vendor (`lib/openai.ts`, `lib/composio.ts`) that
   returns the real client when its key exists and a named fallback otherwise (LA-07).
4. **Data.** If the stack uses PGlite locally, start it as its own service with its own
   `PGLITE_DATA` directory per instance (two instances cannot share a data dir).
5. **Prove slice 0.** Detached build under the build lock (app-sandbox-survival rule 3),
   `next start -p <fresh port>`, `curl` the route for 200 plus expected content, take a
   screenshot in the Aside browser.
6. **Production-serve rules.** `next start` serves only public/ files that existed at
   build time: after adding one, rebuild and restart or fold it into an existing built
   file (LA-09). A production CSP without `wasm-unsafe-eval` kills WebAssembly; scope the
   exception to its path and click through it in the production build (LA-10).
7. **Commit** only after the repo-registration question is settled (LA-04).
8. **Gate** the slice-0 record with `app.stage-gate`.

## Lessons that fire here

LA-01, LA-03, LA-04, LA-07, LA-09, LA-10, LA-25. List them for the exact task with
`scripts/fire_lessons.py`.
