---
name: app-intake-spec
description: "App Studio sub-skill, stage 1 (intake-spec): turn a request, a video, a document, or a voice note into a build spec where every feature row cites its source, every acceptance criterion is an executable check, done-screens are shown, and out-of-scope is named. Use before any scaffold exists. Gated by JEV app.spec and plan.readiness; DEFER when the classifier is down, never scaffold on an ungated spec."
tags: [rig, app-studio, sub-skill, intake, spec, web, mobile]
metadata:
  parent: app-studio
  tier: sub
  stage: intake-spec
  extends: "tubeguruji-doctrine, iqrsqpi-v20, ultraplan, grill-with-ui"
outcome: "A spec the builder can be graded against: sourced feature rows, executable acceptance checks including deny paths, done-screens, out-of-scope, and a JEV app.spec receipt with its decision id."
activation: "Load at the start of any app build, clone, or rebuild before a scaffold exists, or whenever a builder asks what done looks like."
instruction: "Write the spec as a table of sourced rows with executable acceptance checks, gate it through rig-s1gate app.spec and plan.readiness, rewrite until clean or defer, and hand the spec path plus decision ids to the conductor. Never scaffold on an ungated spec."
applies_when:
  env: "local project folder Mike named; optional TubeGuruji corpus at data/corpora/how-to/build-craft/tubeguruji"
  runtime: "any web or mobile app lane (Next.js, Vite, Expo, Flutter)"
  deps: "rig-s1gate on PATH or ./bin/rig-s1gate; rg for registry lookups"
  params: "source type (video clone, rebuild, document, voice note, reference site); mission name"
  budget: "minutes; one to three rewrite passes"
  scale: "one app per spec"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
flow:
  - Name the source type and resolve the source record before writing any feature.
  - Write the spec table with a source and an executable acceptance check per row.
  - Add done-screens, deny paths, a limit+1 check for every gate, and the out-of-scope list.
  - Gate the spec with rig-s1gate app.spec and plan.readiness and rewrite until clean or defer.
  - Hand the spec path and JEV decision ids to app-studio-conductor.
done_when:
  - "file:capabilities/harnesses/s1gate/rubrics/app.spec.json"
  - "file:capabilities/harnesses/s1gate/fixtures/app.spec.bad.md"
  - "grep:capabilities/skills/app-intake-spec/SKILL.md:LA-08"
  - "cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py"
great_example: examples/great/code-engineering/great-tg-grok-bot-clone.md
out_of_scope:
  - choosing the stack (app-stack-select)
  - writing any application code or scaffolding
  - inventing features, numbers, or integrations the source does not show
  - deploy, domain, or store decisions (Gate-D, owned by the ship sub-skills)
---

# app-intake-spec

JEV FIRST, binding on every intake-spec step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call; this stage's verdicts go to `rig-s1gate check app.spec` and `plan.readiness`. When the classifier is
unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9;
below that the stage does not advance, and an uncalibrated ESCALATE is a held transition.

## Load surface

Always loaded at the start of every intake-spec task: the `app-studio` meta-skill routes
stage 1 here and `app-studio-conductor` loads it from its routes table before the
stage's first action. It is a task-start surface, not a deep reference an agent
must already know about.

Sub-skill of `app-studio`, stage 1 of 11. Main skills it extends: `tubeguruji-doctrine`
(clone-from-video lane), `iqrsqpi-v20` (Intent stage with executable done-tests),
`ultraplan` (large planning missions), `grill-with-ui` (when the requester must answer
questions first). Agent: `app-studio-conductor` dispatches `tg-corpus-miner` for video sources.

## Procedure

1. **Name the source type**: video clone, rebuild of an existing app, document or PRD,
   voice note or chat request, or a reference site. Mike's dictation mangles names
   (Kobe = Coby, Ideal Wake = Ideawake); test for a homophone before treating a name as unknown.
2. **Resolve the source record first.** Video clone:
   `rg '"<videoId>"' data/corpora/how-to/build-craft/tubeguruji-registry.jsonl` returns the
   transcript path, sha256, and thumbnail. No row means say no-match; do not paraphrase a
   video you have not read. Rebuild: capture the current app's real screens (LA-16).
3. **Write the spec table**: `# | feature | source | acceptance check`. The source is a
   videoId@timestamp, a document section, a verbatim requester quote, or a screen. A feature
   with no source moves to a "speculative" section or is dropped.
4. **Acceptance is executable**: a command with expected output, a route with expected
   status and body, or a UI step with the expected screen. Include deny paths (signed out,
   wrong role, over quota) and a limit+1 check for every quota or credits gate (LA-08).
5. **Done looks like**: list the screens and routes and attach reference images.
   TubeGuruji thumbnails are screenshots of the finished app
   (`data/corpora/how-to/build-craft/tubeguruji-images/<id>.jpg`).
6. **Out of scope**: name what the source skipped (the Grok Bot video skipped Stripe and
   email, so a faithful clone ships them as named stubs) and every outward step (deploy,
   domain, store submission stay at Gate-D). List each paid vendor with its fallback (LA-07).
7. **Gate**: `rig-s1gate check app.spec --file .app-studio/spec.md --subject "app.spec:<mission> sha=<sha12>" --json`,
   then the same with `plan.readiness`. Rewrite until no rule trips and every positive
   signal clears 0.9. After three rewrites still short: ESCALATE to Mike with the failing
   signals named. Uncalibrated rubrics downgrade BLOCK to ESCALATE; treat that as a hold.
8. **Hand off** `.app-studio/spec.md` plus the decision ids to the conductor.

## Lessons that fire here

- **LA-07** name each paid vendor's fallback in the spec.
- **LA-08** a limit+1 deny check for every quota or credits feature.
- **LA-16** done-screens for a rebuild come from the real app, never from renders.
- **LA-35** before building a studio, platform, or app, search `~/Desktop/Projects` and
  the Memory OS studio map, not only the capability index: the index misses project
  folders, which is how `rig-app-studio` went unseen while its skill family was built.

Run `python3 capabilities/skills/app-studio/scripts/fire_lessons.py "<task text>"` to list
the checks this run owes.

## Fixtures

`capabilities/harnesses/s1gate/fixtures/app.spec.md` passes; `app.spec.bad.md` (adjectives,
invented 99.9% uptime, 50+ integrations) must never pass. Measured 2026-09-27:
good PASS (acceptance 0.95, invented 0.23), bad ESCALATE (invented 0.91, sources 0.05).

## From the creators (candidate lessons)

Distilled from ten app-building YouTube channels (`youtube-<slug>` skills). LA-36..LA-51 are
status `candidate`: follow them now; they fire as gated checks only after promotion, which needs
an engine receipt for the lesson id. Source ids below are greppable in each channel's
`references/lessons.jsonl`.

- Clone sources beyond TubeGuruji: each `youtube-<slug>/references/bench-candidates.json` lists
  apps with feature lists and acceptance sketches. `app-clone-planner` turns one into a task JSON
  whose acceptance checks stay hidden from the builder; `app-creator-miner` adds a new channel.
- LA-48: record the versions the source video used before copying its steps
  (GXD-05-docs-snippets-drift, JTC-07-dep-version-drift).
- spec.md carries a "Done looks like" line per feature id: the screen or route, the one action, and
  the observable result (bench runs held intake-spec when it was missing).
