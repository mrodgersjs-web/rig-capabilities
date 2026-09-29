---
name: app-verify-evidence
description: "App Studio sub-skill, stage 9 (verify-qa): verification that can fail - assertion-bearing tests, BLOCKED kept distinct from FAILED, planted failures with byte-movement proof, route and deny-path proofs, real-screen UI judging, bundle flags proven, and an independent verifier who is not the builder. Use before any stage is called done and before any release record is written."
tags: [rig, app-studio, sub-skill, verify, qa, testing, evidence]
metadata:
  parent: app-studio
  tier: sub
  stage: verify-qa
  extends: "tdd, matt-pocock-tdd, e2e-testing, react-testing, testsprite-engineering, gstack-qa, jake-qa, design-mobile-responsive-tester, code-test-coverage-analyzer, screen-reader-testing, adversarial-verification-loop"
outcome: "A verify record (.app-studio/verify.md) with a PASS, FAIL, or BLOCKED verdict and proof per spec row, at least one planted failure proven RED then GREEN, UI verdicts from a real-screen judge, and an independent verifier's signature."
activation: "Load before calling any slice or stage done, when a report claims all tests pass, or when a QA campaign or screenshot set needs to be trusted."
instruction: "Re-run each spec acceptance check, count assertion verbs behind any PASS report, keep BLOCKED distinct, plant one failure with checksum proof, judge real screens, prove bundle flags, and hand verification to an agent that did not build."
applies_when:
  env: "the project worktree plus the Aside browser for screens"
  runtime: "any test runner (Jest, Vitest, Playwright, flutter test, pytest)"
  deps: "spec.md acceptance table; advisor-plus judge-image; rig-s1gate ui.design"
  params: "breakpoints and devices for screens; which suite owns each spec row"
  budget: "one verify pass per stage; more after any FAIL"
  scale: "one app"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
flow:
  - Re-run every spec acceptance check and record PASS, FAIL, or BLOCKED with proof.
  - Count assertion verbs behind any PASS report before quoting it.
  - Plant one failure with checksum proof and watch it go RED then GREEN.
  - Judge real screens with the image judge and ui.design.
  - Hand the record to an independent verifier and gate it with app.stage-gate.
done_when:
  - "grep:capabilities/skills/app-verify-evidence/SKILL.md:LA-20"
  - "grep:capabilities/skills/app-verify-evidence/SKILL.md:LA-27"
  - "grep:capabilities/skills/app-verify-evidence/SKILL.md:BLOCKED"
  - "cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py"
out_of_scope:
  - fixing the defects found when another session owns fixes (file them instead)
  - certifying your own build as the only verifier
  - reporting pixel metrics as visual quality
---

# app-verify-evidence

JEV FIRST, binding on every verify-qa step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call; this stage's verdicts go to `rig-s1gate check app.stage-gate` and `ui.design`. When the classifier is
unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9;
below that the stage does not advance, and an uncalibrated ESCALATE is a held transition.

## Load surface

Always loaded at the start of every verify-qa task: the `app-studio` meta-skill routes
stage 9 here and `app-studio-conductor` loads it from its routes table before the
stage's first action. It is a task-start surface, not a deep reference an agent
must already know about.

Sub-skill of `app-studio`, stage 9 of 11. Main skills it extends: `tdd`, `matt-pocock-tdd`,
`e2e-testing`, `react-testing`, `testsprite-engineering`, `gstack-qa`, `jake-qa`,
`design-mobile-responsive-tester`, `code-test-coverage-analyzer`, `screen-reader-testing`,
`adversarial-verification-loop`. Agents: `tg-ship-verifier`, `app-ui-judge`.

## Procedure

1. **Re-run the spec.** Every acceptance row gets PASS, FAIL, or BLOCKED with its proof
   line (command and output, route and status, or screenshot path). Include deny paths.
2. **Tests must be able to fail (LA-20).** Before quoting a PASS count, grep its runner:
   `rg -c 'expect\(|assert' <runner>`. A TransformFit report showed 300 PASS / 0 FAIL from a
   runner with zero `expect(` calls, hardcoded `full_scenario_executed: false`, and about
   15 real flows repeated under 20 persona labels. That is a checkpoint, not a test.
3. **BLOCKED is not FAILED (LA-21).** A suite that dies on a missing tool (`deno` absent)
   proves nothing is checking. Name the missing piece; never report it as a failure of
   the code or as a pass.
4. **Plant one failure (LA-27).** `shasum` the target, plant the defect, `shasum` again and
   refuse the plant if the bytes did not move, run the check and require RED, restore,
   require GREEN. A red-green harness once ran `sed -i` with no file operand and "planted"
   nothing five times in a row.
5. **Real screens, judged (LA-16).** Screens from the real app on the target viewport or
   simulator. Run `advisor-plus judge-image --image <png> --brief "<spec screen>"` and
   `rig-s1gate check ui.design` on the screen record.
6. **Bundle flags (LA-19)** and **source versus render (LA-23)** before filing a defect.
7. **Independent verifier.** The builder does not certify its own work: `tg-ship-verifier`
   or `app-ui-judge` re-runs the checks and signs the record.
8. **Gate** the verify record with `app.stage-gate`.
9. **Seconds mean stub (LA-34).** Compare a run's duration and evidence with the work it
   claims. The rig-app-studio engine reported 20 phases complete in 7 seconds and recorded
   "pnpm install succeeds" and "pnpm dev boots" with exit 0 from hashes of placeholder
   strings; neither command ran. That evidence is now either executed or recorded NOT RUN.
10. **Run acceptance through rig-testlab.** `pnpm studio:mission verify` calls
   `rig-testlab app run` (`~/Developer/ai-user-testing-mcp`): the reviewed `app-acceptance`
   adapter runs the hidden checks in a testlab sandbox, seals receipts and an AppRunProof, and
   `rig-testlab app verify` re-checks that proof before its hash lands in
   `.rig/runs/<id>/testlab.json`. A run is `verified` only with that proof verified. Testlab
   missing or unparseable marks every check BLOCKED with the reason, never a pass.
11. **Four verdicts, never merged.** `pass`, `fail`, `flaky` (failed, then passed on a retry;
   only GET/HEAD are retried, at most twice), `blocked` (a check with zero assertion verbs, or
   a suite with zero checks). Flaky is not pass (Google: about 1.5% of runs flaky, 84% of
   pass-to-fail transitions involved a flaky test).
12. **Judge page text on the rendered DOM.** Playwright's Chromium launches in the Aside
   sandbox (headless Chromium 148, 920 ms, proved 2026-09-28), so page text checks are
   judged on what a user sees (source casing, captured variables substituted), with the raw
   result kept beside it; tg-doctor-booking D11 passed raw only because the word sat inside a
   `<script>` payload. playwright-core is rig-app-studio's own pinned devDependency. No launchable browser means
   `render BLOCKED: <reason>`. Before filing a page defect, compare raw and rendered text: the
   first case (expense tracker P1) was an over-specific hidden check (case-sensitive
   "Expense" against "Add expense"), not an app defect. Use `text_includes_ci` for intent.
13. **Prove the suite catches defects.** `pnpm studio:mission prove <task> --app <dir>` clones
   the app, plants one defect per class (API handler, validation, computed value), refuses a
   plant whose sha256 did not move, requires the original GREEN and each mutant RED, and names
   survivors. tg-ai-form-builder v0: 2/3 killed (0.667); a disabled JSON-object guard in
   `lib/http.ts` survived. Bench v0.1 added check G11 (null body -> 400) and the gate killed 3/3.
   A survivor is a missing check: add it, record why in the task changelog, re-run the gate.
14. **Intake evidence comes from the builder.** intake-spec and architecture-stack read the
   builder's `.app-studio/spec.md` and `stack.md`; an absent doc is a named blocker, never
   re-derived from task.json. Feature traceability is advisory, so an uncalibrated heuristic
   never holds a stage.

## Evidence

memory/projects/transformfit-qa.md#L18, #L20, #L22, #L24; memory/MEMORY.md#L11;
memory/episodic/2026-09-27.md#L1467; `~/Developer/ai-user-testing-mcp/docs/app-studio-merge.md`
(sources: playwright.dev/docs/test-agents, stryker-mutator.io/docs, arxiv.org/abs/2501.12862,
testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html,
openai.com/index/introducing-swe-bench-verified).

## From the creators (candidate lessons)

Distilled from ten app-building YouTube channels (`youtube-<slug>` skills). LA-36..LA-51 are
status `candidate`: follow them now; they fire as gated checks only after promotion, which needs
an engine receipt for the lesson id. Source ids below are greppable in each channel's
`references/lessons.jsonl`.

- LA-41: drive one real request in a browser with the network tab open (a device or the store
  sandbox for mobile) and record request, response and rendered result; code reading is not
  evidence (SSG-12-verify-in-real-browser, PYG-02-drive-one-real-request,
  JTC-06-submit-fires-request).
- LA-40: a build or console with warnings is not clean (TRV-04-lint-warning-is-not-clean,
  SSG-09-no-ignored-console-errors).
- LA-37: no swallowed errors: every catch fixes, rethrows or logs with context
  (TRV-08-no-suppressed-errors).
- Failed signups return one identical error shape so the endpoint does not reveal which emails exist
  (CH-JSM-10).
