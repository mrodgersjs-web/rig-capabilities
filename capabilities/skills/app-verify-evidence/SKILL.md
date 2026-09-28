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

## Evidence

memory/projects/transformfit-qa.md#L18, #L20, #L22, #L24; memory/MEMORY.md#L11;
memory/episodic/2026-09-27.md#L1467.
