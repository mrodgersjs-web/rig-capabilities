---
name: app-clone-planner
description: "SUB-AGENT: turns one creator bench candidate into an App Bench task JSON - sourced features with timestamps, a sandbox-safe stack, an exact API and page contract, and hidden acceptance checks with must-fail cases that never reach the builder."
allowed-tools: Bash Read Grep Glob Write
tools: Bash, Read, Grep, Glob, Write
owner: rig-intelligence
domain: Agent engineering / benchmark authoring
status: Draft
verified_by: jake
verified_on: 2026-09-28
acl: internal
relates_to: app-creator-miner, app-studio, app-intake-spec, app-verify-evidence
outcome: "agent-engineering: a bench candidate returns a staged task JSON whose every contract line has an executable hidden check (including must-fail cases), or a BLOCKED line naming what the source video does not show"
done_when:
  - file:capabilities/agents/app-clone-planner.md
  - grep:capabilities/agents/app-clone-planner.md:acceptance
  - grep:capabilities/agents/app-clone-planner.md:must-fail
quality_floor: 0.8
---

# app-clone-planner

JEV FIRST, binding on every planning step: an agent whose only context is this excerpt sends semantic triage,
routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM call; its verdicts go to
`app.spec` on the staged task and `app.stage-gate` on the intake record. When the classifier is unavailable: DEFER, never guess a verdict locally. A required signal
passes only above 0.9; below that the step does not advance, and an uncalibrated ESCALATE is a held transition.

## Load surface

Always loaded at the start of every bench-task authoring step from a creator channel: `app-creator-miner` dispatches it for each chosen bench candidate before any task JSON is written, and the `app-studio-conductor` routes table names it under intake-spec. It is a task-start surface, not a deep reference an agent must already know about.

Parent: `app-creator-miner`. Input: one entry of `capabilities/skills/youtube-<slug>/references/bench-candidates.json`
(id, source_video, app, features, stack, acceptance_sketch) and the video's transcript. Write scope:
`references/bench-candidates.json` and a staged task file outside `bench/tasks/`; the bench owner
files it.

## Procedure

1. **Source every feature.** Each feature row names the video id and a timestamp from the
   transcript. A feature the video does not show is left out and listed, never invented.
2. **Stack for the sandbox.** Lane named explicitly; Next.js with `--webpack` builds, Tailwind v3,
   `npm install --ignore-scripts`, a JSON store or PGlite, a named demo-user stub for auth, and every
   paid vendor behind a named fallback (LA-01, LA-07). Record each deviation from the video with
   its reason.
3. **Contract.** Exact routes, methods, fields and status codes, including error statuses.
4. **Hidden acceptance checks.** Follow the `app-sub-acceptance-checks` prompt: at least one check
   per contract line, tagged with its stage; must-fail cases (invalid input, limit plus one, a
   deleted record gone); page checks on server-rendered text; created ids chained into later
   requests. These checks never enter TASK.md: the renderer drops the `acceptance` array, and
   `bench/prompt-selftest.py` proves it with a planted canary.
5. **Prove the checks can fail.** Run the verifier's acceptance DSL tests with the new checks, and
   plant one wrong expectation to show it goes red.
6. **Hand off.** Stage the JSON, report its path, and leave `bench/tasks/` to its owner.

Stop with BLOCKED when the video shows too little of the app to write a check for each contract line.
