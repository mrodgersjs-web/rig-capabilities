---
name: app-observability
description: "App Studio sub-skill, stage 10 (ship-release): error monitoring and logging wired before release - API and client errors captured with request and session context, one induced error per side proven to arrive, sample rates set per environment, and a structured-log named fallback when no monitoring key exists."
tags: [rig, app-studio, sub-skill, observability, monitoring, logging, errors, release]
metadata:
  parent: app-studio
  tier: sub
  stage: ship-release
  extends: "rig-top100-monitoring-alerting, code-error-pattern-aggregator, rig-top100-incident-response"
outcome: "A release request whose monitoring claim is proven: one induced API error and one induced client error each arrive in the monitor (or the structured-log fallback) with request and session context, and no catch in the app swallows an error."
activation: "Load before any release or deploy request, when adding error monitoring or logging, or when a user reported an error before the team saw it."
instruction: "Wire monitoring for the API and the client before the first release, attach request and session context, set sample rates per environment, prove one induced error per side arrives, use a structured-log fallback when no key exists, and list the monitoring key for Gate-D."
applies_when:
  env: "local build with a monitoring test project or the structured-log fallback; production only after Gate-D"
  runtime: "Next.js server and client, Express or Hono APIs, Expo apps"
  deps: "a monitoring SDK (Sentry or similar) behind an env key, or structured logging"
  params: "sample and replay rates per environment; which context fields are captured"
  budget: "one slice: wire, induce, observe"
  scale: "single app"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - Wire error capture on the API and the client before feature work ships.
  - Attach request and session context to every captured error.
  - Set sample and replay rates per environment in config.
  - Induce one API error and one client error and observe both arrive.
  - List the monitoring key and dashboard in the release request for Gate-D.
done_when:
  - "grep:capabilities/skills/app-observability/SKILL.md:LA-38"
  - "grep:capabilities/skills/app-observability/SKILL.md:induced error"
  - "grep:capabilities/skills/app-observability/SKILL.md:named fallback"
  - "cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py"
out_of_scope:
  - logging secrets, tokens, or full request bodies that carry personal data
  - paid monitoring plans or production projects without Mike's approval (Gate-D)
  - paging people on alerts (operate phase, not this stage)
---

# app-observability

JEV FIRST, binding on every observability step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call; this stage's verdicts go to `rig-s1gate check app.stage-gate` and `app.ship`.
When the classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes
only above 0.9; below that the release request does not advance, and an uncalibrated ESCALATE is a
held transition.

## Load surface

Always loaded before any release or deploy request in stage 10: the `app-studio` meta-skill routes
it from the ship-release row, and `app-studio-conductor` loads it from its routes table alongside
`app-ship-web` and `app-ship-mobile`. It is a task-start surface, not a deep reference an agent
must already know about.

Sub-skill of `app-studio`, stage 10 of 11. Main skills it extends: `rig-top100-monitoring-alerting`,
`code-error-pattern-aggregator`, `rig-top100-incident-response`.

## Procedure

1. **Wire both ends before release.** Error capture on the API and on the client, in the first
   scaffold commit for mobile, never after launch (LA-38, GXD-01-error-monitoring-first).
2. **Context.** Each captured error carries the request (route, method, id) and the session
   (user id, device or browser) so a report can be replayed (TRV-11-error-carries-session-context).
   Never log secrets, tokens or personal request bodies.
3. **Rates per environment.** Development captures every session; production uses the sampled rate
   written in config (GXD-02-replay-rate-per-env).
4. **Named fallback.** With no monitoring key, write structured error logs (JSON lines with the same
   context) and say so in stack.md; the release request lists the monitoring key by env var name.
5. **Induced error.** Throw one API error and one client error on purpose and show each arriving
   with its context (TRV-03-error-both-ends). A dashboard that never received an error proves
   nothing.
6. **No swallowed errors.** Every catch fixes, rethrows, or logs with context (LA-37,
   TRV-08-no-suppressed-errors).
7. **Gate.** Send the record to `app.stage-gate` and `app.ship`. Creating a production monitoring
   project or a paid plan stops at Gate-D.

## Evidence

The induced-error commands with their exit codes, the captured events (monitor event ids or the
structured log lines) showing request and session context, the config lines for each
environment's sample rate, and a grep of the source for empty catch blocks with its count. A check
that could not run is BLOCKED with the missing piece named (LA-21).

## From the creators (candidate lessons)

Distilled from ten app-building YouTube channels (`youtube-<slug>` skills). LA-36..LA-51 are
status `candidate`: follow them now; they fire as gated checks only after promotion, which needs
an engine receipt for the lesson id. Source ids are greppable in each channel's
`references/lessons.jsonl`.

- LA-38: monitoring for API and client before the first release, proven with one induced error
  (CH-JSM-12, CH-CDS-01, GXD-01-error-monitoring-first, TRV-03-error-both-ends).
- LA-37: no catch swallows an error; one failed request never blanks a screen
  (TRV-08-no-suppressed-errors, CH-JSM-06).
- Per-environment replay and error rates (GXD-02-replay-rate-per-env); session context on every
  report (TRV-11-error-carries-session-context).
