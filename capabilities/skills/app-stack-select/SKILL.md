---
name: app-stack-select
description: "App Studio sub-skill, stage 2 (architecture-stack): pick the stack for the app's lane from the default tables, apply the build-location matrix for the Aside sandbox, keep local and free-tier first, give every paid vendor a named fallback, and record deviations with reasons. Gated by JEV app.stack; DEFER when the classifier is down."
tags: [rig, app-studio, sub-skill, architecture, stack, web, mobile]
metadata:
  parent: app-studio
  tier: sub
  stage: architecture-stack
  extends: "tubeguruji-doctrine, advise-project-approach, fullstack-developer, tg-expo-mobile-ai, dart-flutter-patterns"
outcome: "A stack decision record (.app-studio/stack.md) naming the lane, the stack, where it builds, each paid vendor's fallback, and each deviation's reason, with a JEV app.stack receipt."
activation: "Load after the spec clears its gate and before any scaffold, or when a build fails for toolchain reasons and the stack needs revisiting."
instruction: "Name the lane, start from its default stack, apply the build-location matrix, env-gate every paid vendor with a named fallback, record deviations, gate with rig-s1gate app.stack, and write stack.md."
applies_when:
  env: "Aside sandbox, Orca terminals, or CI; Mike's LAN fleet for heavy builds"
  runtime: "web (Next.js, Vite), mobile (Expo, React Native, Flutter), voice agent, media pipeline"
  deps: "the approved spec from app-intake-spec"
  params: "lane; hosting target; which vendors are already paid for"
  budget: "minutes; zero cash until the product forces spend"
  scale: "single app, one team"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - Name the lane from the spec and load the default stack for that lane.
  - Apply the build-location matrix so every tool builds where the build will actually run.
  - Env-gate each paid vendor and write its named fallback.
  - Record every deviation from the default with its reason.
  - Gate the record with rig-s1gate app.stack and write .app-studio/stack.md.
done_when:
  - "file:capabilities/harnesses/s1gate/rubrics/app.stack.json"
  - "grep:capabilities/skills/app-stack-select/SKILL.md:LA-01"
  - "grep:capabilities/skills/app-stack-select/SKILL.md:Build-location matrix"
  - "cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py"
out_of_scope:
  - writing scaffold code (app-web-scaffold, app-mobile-build)
  - buying plans, seats, or credits (Gate-D purchase)
  - enterprise multi-tenant or compliance architecture
---

# app-stack-select

JEV FIRST, binding on every architecture-stack step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call; this stage's verdicts go to `rig-s1gate check app.stack`. When the classifier is
unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9;
below that the stage does not advance, and an uncalibrated ESCALATE is a held transition.

## Load surface

Always loaded at the start of every architecture-stack task: the `app-studio` meta-skill routes
stage 2 here and `app-studio-conductor` loads it from its routes table before the
stage's first action. It is a task-start surface, not a deep reference an agent
must already know about.

Sub-skill of `app-studio`, stage 2 of 11. Main skills it extends: `tubeguruji-doctrine`
(default web SaaS stack table), `advise-project-approach` (architecture and stack
research), `fullstack-developer`, `tg-expo-mobile-ai` (Expo lane), `dart-flutter-patterns`
and `flutter-production-build` (Flutter lane).

## Lane defaults

| Lane | Default | Source |
|---|---|---|
| Web SaaS | Next.js App Router + TS, Tailwind + shadcn/ui, Clerk, Neon + Drizzle, Inngest, Gemini or OpenAI, Stripe, Vercel | tubeguruji-doctrine default stack table |
| Marketing site | static or Next.js export on Vercel, content-hashed assets | memory/projects/rodgers-intelligence.md#L31 |
| Mobile (new) | Expo + Expo Router + EAS builds | tg-expo-mobile-ai |
| Mobile (existing Flutter) | stay on Flutter; drift + supabase_flutter as TransformFit does | memory/projects/transformfit-qa.md#L34 |
| Voice agent | the shared voice skeleton with Vapi or AssemblyAI | tg-voice-agent-stack |
| AI media pipeline | durable steps (Inngest step.run), Remotion render | tg-durable-ai-pipelines, tg-ai-media-pipeline |

## Build-location matrix

Measured in the Aside sandbox 2026-09-26 (memory/episodic/2026-09-26.md#L3, #L7) and
2026-09-27 (memory/episodic/2026-09-27.md#L1475):

| Tool | In the Aside sandbox | Use instead |
|---|---|---|
| Next.js SWC native binding, Turbopack | blocked (code signature not valid) | `next build --webpack`, `next dev --webpack` |
| Tailwind v4 (`@tailwindcss/oxide`, `lightningcss`) | blocked | Tailwind v3 (pure-JS PostCSS) |
| esbuild and other postinstall scripts | killed by allow-scripts policy | `npm i --ignore-scripts` |
| PGlite inside the Next bundler | throws on a URL path argument | PGlite as a standalone HTTP service |
| `ps`, `pgrep`, `pkill` | blocked | `lsof -t <file or port>` then `kill` |
| iOS Simulator (CoreSimulatorService) | unreachable | an Orca terminal running `xcrun simctl` |

If a tool must stay native, name where it builds instead (an Orca terminal, CI, a fleet
node) in the record. The `app.stack` rubric escalates a stack that builds nowhere.

## Procedure

1. Name the lane from the spec; load its default row.
2. Walk the build-location matrix for every tool in the stack (LA-01, LA-15).
3. Local and free tier first: a paid route appears only when the product forces it.
4. Every paid vendor is env-gated with a NAMED fallback so the app runs without its key
   (Composio static tool list, E2B mock viewer, mock LLM responder). List missing
   credentials exactly in a BLOCKED list rather than failing silently (LA-07).
5. Record each deviation from the default with its reason.
6. Gate: `rig-s1gate check app.stack --file .app-studio/stack.md --subject "app.stack:<mission> sha=<sha12>" --json`;
   rewrite until clean or ESCALATE.

## Lessons that fire here

- **LA-01** native binaries: webpack flag, Tailwind v3, ignore-scripts, PGlite service.
- **LA-07** named fallbacks for paid vendors.
- **LA-15** simulator work runs from an Orca terminal.

## Fixtures

`capabilities/harnesses/s1gate/fixtures/app.stack.md` passes (lane 0.96, local-first 0.97);
`app.stack.bad.md` (Turbopack, Tailwind v4, required paid APIs, "figure out builds later")
escalates (paid_without_fallback 0.91, lane 0.14). Measured 2026-09-27.

## From the creators (candidate lessons)

Distilled from ten app-building YouTube channels (`youtube-<slug>` skills). LA-36..LA-51 are
status `candidate`: follow them now; they fire as gated checks only after promotion, which needs
an engine receipt for the lesson id. Source ids below are greppable in each channel's
`references/lessons.jsonl`.

- stack.md names the lane on its first line (`Lane: web SaaS`, `mobile app`, ...); bench runs held
  architecture-stack when the lane was only implied.
- LA-51: one package manager per project, and any forced resolution recorded with the package that
  forced it (JTC-01-one-package-manager, CH-JSM-02).
- LA-48: pin the versions the code is written against; extend out-of-date vendor types locally
  instead of casting (JTC-07-dep-version-drift, SSG-10-vendor-types-out-of-date).
- LA-39: required config fails loud at start with its name; optional paid keys get a named
  fallback (CH-CDS-02, CH-JSM-03).
