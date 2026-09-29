---
name: app-web-frontend
description: "App Studio sub-skill, stage 6 (web-frontend): build web front ends one route or component per slice, each ending in an executed check, with deny and empty states rendered, idempotent effects instead of a disabled StrictMode, and a click-through in the production build rather than only the dev server. Use for any Next.js, React, or Vite UI slice."
tags: [rig, app-studio, sub-skill, frontend, nextjs, react, web]
metadata:
  parent: app-studio
  tier: sub
  stage: web-frontend
  extends: "nextjs-app-router-patterns, next-best-practices, react-best-practices, vercel-react-best-practices, react-patterns, react-state-management, react-performance, shadcn-ui, frontend-patterns, responsive-design"
outcome: "Front-end slices each proven by an executed check (route 200 with expected content, test, or screenshot), deny and empty states visible, a production-build click-through recorded, and an app.stage-gate receipt per slice."
activation: "Load for any page, component, form, dashboard, or client-state slice in a web app."
instruction: "Build one route or component per slice, render its deny, empty, and error states, keep effects idempotent, click through the production build, and gate the slice with rig-s1gate app.stage-gate."
applies_when:
  env: "the project worktree under app-sandbox-survival rules"
  runtime: "Next.js App Router, React, Vite"
  deps: "spec.md acceptance rows; stack.md"
  params: "route list; breakpoints"
  budget: "one slice per route or component"
  scale: "one app"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
flow:
  - Take one route or component per slice with its acceptance row from the spec.
  - Render the deny, empty, loading, and error states the spec implies.
  - Keep effects idempotent rather than disabling StrictMode.
  - Click through the slice in the production build and curl its route.
  - Gate the slice record with rig-s1gate app.stage-gate.
done_when:
  - "grep:capabilities/skills/app-web-frontend/SKILL.md:StrictMode"
  - "grep:capabilities/skills/app-web-frontend/SKILL.md:LA-10"
  - "grep:capabilities/skills/app-web-frontend/SKILL.md:production build"
  - "cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py"
great_example: examples/great/code-engineering/great-tg-grok-bot-clone.md
out_of_scope:
  - mobile apps (app-mobile-build)
  - visual design decisions (app-ui-design)
  - deploys (app-ship-web, Gate-D)
---

# app-web-frontend

JEV FIRST, binding on every web-frontend step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call; this stage's verdicts go to `rig-s1gate check app.stage-gate` and `code.diff`. When the classifier is
unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9;
below that the stage does not advance, and an uncalibrated ESCALATE is a held transition.

## Load surface

Always loaded at the start of every web-frontend task: the `app-studio` meta-skill routes
stage 6 here and `app-studio-conductor` loads it from its routes table before the
stage's first action. It is a task-start surface, not a deep reference an agent
must already know about.

Sub-skill of `app-studio`, stage 6 of 11. Main skills it extends:
`nextjs-app-router-patterns`, `next-best-practices`, `react-best-practices`,
`vercel-react-best-practices`, `react-patterns`, `react-state-management`,
`react-performance`, `shadcn-ui`, `frontend-patterns`, `responsive-design`.
Main agents: `tg-web-builder`, `voltagent-nextjs-developer`, `voltagent-frontend-developer`.

## Procedure

1. **One slice, one check.** A slice is one route or component plus its acceptance row;
   it ends in an executed check (curl with expected content, a test that asserts, or a
   screenshot), never in "implemented".
2. **States are features.** Render signed-out, over-quota, empty, loading, and error
   states the spec implies. A visible credits or quota counter proves the gate (LA-08).
3. **StrictMode is a signal.** React runs effects twice in development; a duplicate write
   there means a non-idempotent effect (the TubeGuruji corpus shows this bug live,
   zlZ_7VTfxUs). Make the write idempotent; do not switch StrictMode off to hide it.
4. **Production build click-through.** Dev success is not production success: a
   production CSP killed WebAssembly that worked in dev (LA-10), and `next start` 404s
   public/ files added after the build (LA-09). Click through each slice in the production
   build on a fresh port and curl its route (LA-25).
5. **Responsive.** Check the slice at mobile, tablet, and desktop widths before handing it
   to `app-ui-design` for judging.
6. **Gate** the slice record with `app.stage-gate`.

## Lessons that fire here

LA-08, LA-09, LA-10, LA-23, LA-25. List them per task with `scripts/fire_lessons.py`.

## From the creators (candidate lessons)

Distilled from ten app-building YouTube channels (`youtube-<slug>` skills). LA-36..LA-51 are
status `candidate`: follow them now; they fire as gated checks only after promotion, which needs
an engine receipt for the lesson id. Source ids below are greppable in each channel's
`references/lessons.jsonl`.

- LA-36: fix a hydration mismatch at the diverging value (mounted gate, skipHydration, one
  formatter, client-only import), never by suppressing it (CH-CWA-01, CH-LMA-03,
  SSG-02-ssr-client-mismatch, JTC-02-hydration-source-fix).
- LA-37: one failed fetch never blanks the screen; check response.ok and render a section error
  state (CH-JSM-06, CH-LMA-09).
- LA-44: client hooks only in 'use client' files; check which surface a component comes from
  (CH-CWA-08, CH-CWA-09).
- DOM and React traps: no button inside a button (CH-LMA-01), a Link with several children wraps
  them in a fragment (CH-LMA-11), hooks return a cleanup function or nothing, never undefined by
  accident (CH-JSM-07), cart lines keyed by variant, not product id (CH-LMA-10).
- Shared code has no side effect that fires twice (TRV-01-code-runs-on-both-sides); realtime
  screens handle join and leave, tested with two clients (TRV-09-realtime-join-and-leave).
