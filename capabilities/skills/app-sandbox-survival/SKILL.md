---
name: app-sandbox-survival
description: "App Studio sub-skill, cross-cutting (scaffold-setup through verify-qa): build, run, and restart apps inside the Aside sandbox without losing a day to it - native binaries blocked, process listing blocked, ghost servers on old ports, competing builders, unregistered repos, unreachable simulators. Every rule here was paid for in the Grokbot and TransformFit builds and fires as a typed lesson with a mandated check."
tags: [rig, app-studio, sub-skill, sandbox, build, ports, processes]
metadata:
  parent: app-studio
  tier: sub
  stage: scaffold-setup
  extends: "fullstack-developer, tg-saas-skeleton, jake-lessons-ledger"
outcome: "Builds that finish, servers that serve the current build on a known port, exactly one builder per project, and a run record whose sandbox lessons carry receipts."
activation: "Load before the first install, build, dev server, or simulator run in any app project, and whenever a build hangs, a port lies, or a process will not die."
instruction: "Fire the sandbox lessons for the task, run long builds detached under a build lock and poll the log, find processes with lsof, serve on a fresh port, curl before claiming a surface is up, and record a receipt for each fired check."
applies_when:
  env: "the Aside bash sandbox (native .node blocked, ps and pkill blocked) or an Orca terminal"
  runtime: "Node 18+ toolchains, Next.js, Vite, Flutter, Xcode"
  deps: "lsof, curl, nohup, shasum"
  params: "project path; chosen port range"
  budget: "seconds per check; saves hours per build"
  scale: "one project, one builder at a time"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - Fire the sandbox lessons for the task text and note the checks the run owes.
  - Take the build lock and run the build detached while polling its log.
  - Find and stop processes with lsof and serve fresh builds on fresh ports.
  - Curl every surface before claiming it is up.
  - Record a receipt per fired check in .app-studio/run.jsonl.
done_when:
  - "cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/app-studio/references/lessons.jsonl --run capabilities/skills/app-studio/fixtures/run_web_build_green.jsonl"
  - "cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/app-studio/references/lessons.jsonl --run capabilities/skills/app-studio/fixtures/run_web_build_missing_receipt.jsonl; test $? -eq 2"
  - "grep:capabilities/skills/app-sandbox-survival/SKILL.md:build.lock"
  - "cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py"
out_of_scope:
  - changing Aside sandbox policy or code-signing settings
  - killing processes that belong to another agent's project
  - registering a repo with Mike's git hook (his call)
---

# app-sandbox-survival

JEV FIRST, binding on every scaffold-setup and every build step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call; this stage's verdicts go to `rig-s1gate check app.stage-gate`. When the classifier is
unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9;
below that the stage does not advance, and an uncalibrated ESCALATE is a held transition.

## Load surface

Always loaded at the start of every scaffold-setup and every build task: the `app-studio` meta-skill routes
stage 4 here and `app-studio-conductor` loads it from its routes table before the
stage's first action, and the `app-sandbox-build-verify` harness names it as doctrine. It is a task-start surface, not a deep reference an agent
must already know about.

Sub-skill of `app-studio`. It fires in every stage that installs, builds, serves, or
simulates. Evidence: memory/episodic/2026-09-26.md#L3, #L7, #L19, #L122, #L128 (Grokbot
build) and memory/episodic/2026-09-27.md#L1475, #L1557.

## The rules

1. **Native binaries are blocked (LA-01).** Every `.node` module fails with "code
   signature not valid for use in process". Use `next build --webpack` and
   `next dev --webpack`, Tailwind v3, `npm i --ignore-scripts`, and run PGlite as its own
   HTTP service. Turbopack fails outright.
2. **You cannot list or kill by name (LA-02).** `ps`, `pgrep`, `pkill` are blocked;
   `lsof -t <file the process holds>` or `lsof -t -i :<port>` yields PIDs and `kill` works.
   A ghost server on :3000 kept serving a stale build while invisible to lsof, so serve
   each fresh build on a fresh port and never trust :3000.
3. **Exactly one builder per project (LA-03).** Six competing builders (a watcher routine
   running `npm run build` on every wake plus the agent's own builds) produced
   `PageNotFoundError` and `ENOENT rename` in `.next`. Take the lock, build detached, poll:

   ```sh
   mkdir -p .app-studio
   if [ -e .app-studio/build.lock ]; then echo "build.lock held: wait or prove it stale"; exit 1; fi
   touch .app-studio/build.lock
   nohup sh -c 'npm run build > .app-studio/build.log 2>&1; echo "exit=$?" >> .app-studio/build.log; rm -f .app-studio/build.lock' >/dev/null 2>&1 &
   tail -5 .app-studio/build.log   # poll; the bash bridge may restart mid-build, the log survives
   ```

   The dormant hook `app-single-builder-guard.sh` enforces the same lock for agents once
   Mike wires it.
4. **Watchers read, never build (LA-26).** A heartbeat that watches a build reports
   green or red from the log. Delete it at mission close.
5. **Curl before you claim (LA-25).** `curl -s -o /dev/null -w '%{http_code}' <url>` plus a
   grep for expected content. The kanban server on :8913 was dead while its data layer
   and sync agent were alive; a keepalive supervisor is not liveness.
6. **Unregistered repos refuse commits (LA-04).** Mike's git hook returns
   `unregistered_repository` for a new project repo; registering is his decision.
7. **Simulators live outside the sandbox (LA-15).** CoreSimulatorService answers
   "connection invalid" here; run `xcrun simctl` work from an Orca terminal.

## Receipts

Before a build: `python3 capabilities/skills/app-studio/scripts/fire_lessons.py "<task>"`.
After performing each check, append its receipt row to `.app-studio/run.jsonl`; at close
`validate_lessons.py ... --run .app-studio/run.jsonl` must exit 0. The fixtures prove
the gate bites: the green run exits 0 and the same run without the single-builder
receipt exits 2.
