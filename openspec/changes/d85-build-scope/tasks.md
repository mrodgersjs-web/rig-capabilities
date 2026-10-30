# Work plan

## pstack bug-fix playbook

1. Reproduce it yourself on the matching surface via the control skill (Non-negotiables). Don't hand the repro to the user. A debug or instrumentation protocol that says to ask the user does not override this. You drive the instrumented runtime. Ask the user only with a stated, specific reason the control surface cannot reach the target, and only after driving it as far as it goes. Won't reproduce directly, force it: synthesize the trigger, tighten conditions, or instrument until it fires.
2. Binary-search the cause. Form the candidate hypotheses, then rule them out until one survives. Seed them with `how` over the affected subsystem and the **why** skill for regression history. Each pass, take the split that cuts the most remaining problem space, get runtime evidence, eliminate. When program state is unclear, add instrumentation or logging and read it as the code runs. Don't guess. Drive a long or stubborn hunt with Cursor's `/loop` command. Confirm the surviving *mechanism* with runtime evidence before the step-3 architect/interrogate fan-out.
3. Plan the fix. If it crosses a function boundary, `architect` first. Delegate implementation to a subagent using your configured bug-fix model (default `claude-fable-5-1-thinking-max`) with a specific scope. Review the diff.
4. Verify on the same surface. The original repro now passes. "Inconclusive" or wrong-surface is not a pass. Flag it. Unit tests show branch behavior, not bug absence.
5. Stage the commits so the failing repro lands before the fix in git history. See the **pstack-tdd** skill for the failing-test-first cadence when the bug has a cheap local test path. Skip it when the test would be expensive, integration-heavy, or unclear.
6. Run **Opening a PR**.

Steps 5 and 6: skip commits and PR creation for this local policy repair; preserve unrelated dirty work. Retain failing-before/passing-after test evidence locally.

## Task checklist

- [x] Reproduce actual startup and guard denials; trace dispatch_hook and hook_check.
- [x] Read RIG Lattice skill and record canonical cell plus BMS evidence.
- [x] Compare boundary separation against policy-mode switching and command exceptions.
- [x] Implement ordinary-tool scope correction and live certification checks.
- [x] Update policy and installed instruction surfaces.
- [x] Run relevant regression suites, original live commands, and Lattice audit.
- [x] Obtain independent review and seal ProofPacket.
- [x] Save durable correction to JakeStudio.

Local repair verified. Independent reviewer accepted bounded scope. Full Lattice prose audit and whole-tree zone check remain blocked as documented; no build/estate certification or clean-tree promotion claimed. Memory written; vault auto-commit encountered an existing index lock.
