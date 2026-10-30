# Site acceptance repair

Mission: repair existing design routing distribution and reject fabricated website acceptance evidence. Codex is the only writer for canonical site capability paths. The production site repository remains owned by Aside mission QC6DdpCd7rfnfiru.

## Bug fix playbook

1. Reproduce it yourself on the matching surface via the control skill (Non-negotiables). Don't hand the repro to the user. A debug or instrumentation protocol that says to ask the user does not override this. You drive the instrumented runtime. Ask the user only with a stated, specific reason the control surface cannot reach the target, and only after driving it as far as it goes. Won't reproduce directly, force it: synthesize the trigger, tighten conditions, or instrument until it fires.
2. Binary-search the cause. Form the candidate hypotheses, then rule them out until one survives. Seed them with `how` over the affected subsystem and the **why** skill for regression history. Each pass, take the split that cuts the most remaining problem space, get runtime evidence, eliminate. When program state is unclear, add instrumentation or logging and read it as the code runs. Don't guess. Drive a long or stubborn hunt with Cursor's `/loop` command. Confirm the surviving *mechanism* with runtime evidence before the step-3 architect/interrogate fan-out.
3. Plan the fix. If it crosses a function boundary, `architect` first. Delegate implementation to a subagent using your configured bug-fix model (default `grok-4.6-fast-xhigh`) with a specific scope. Review the diff.
4. Verify on the same surface. The original repro now passes. "Inconclusive" or wrong-surface is not a pass. Flag it. Unit tests show branch behavior, not bug absence.
5. Stage the commits so the failing repro lands before the fix in git history. See the **pstack-tdd** skill for the failing-test-first cadence when the bug has a cheap local test path. Skip it when the test would be expensive, integration-heavy, or unclear.
6. Run **Opening a PR**.

Steps 2-3 use the supplied auditor's bounded findings and local source/behavior checks. This delegated worker retains its assigned implementation role; no recursive fleet launch or unrequested model switch. Step 5 history and step 6 PR are skipped because commits, branches, pushes and PR creation were not requested. Independent read-only review remains required.

## Done-test and design

- Existing exact canonical design router installed and byte-checked at Codex and Aside load paths; route must terminate without reciprocal redirects.
- Gate evidence is schema-versioned and bound to a trusted verifier public key supplied by the operator, outside builder-controlled site inputs. A signature binds build bytes, source artifacts, actual QA captures and observations. The builder cannot self-sign with a key in its site folder.
- Require a named actual client or explicitly user-named private project, client branding, source-located problem/solution evidence and visual Pinterest provenance. Public domain is optional for private projects such as TransformFit.
- Require ordered, per-offering Miro artifacts for all seven phases and three rendered divergence directions. Empty Markdown is never sufficient.
- Consume signed browser observations for reactive scroll, 3D, reduced motion and CTA interactions; read the actual Lighthouse JSON and decode bound PNGs.
- At least 30 adversarial/representative evidence-contract tests and a positive control; test fixtures never represent real client captures or a skill outcome evaluation.
- `python3 -m unittest tests.test_site_gate_evidence` and both capability done-tests must execute substantive assertions.
- No production propagation. Save the sync patch for the unregistered design owner; do not change repository registration.

## Current constraints

Meta-harness startup PASS, packet startup-c2e4cec9b41b4cc99e71522261258f61. Memory package sha256:219efe86dec142d0980bd129a1305553161334189fc98dc4cedce65000c3d2b6; returned legacy needle-haystack context is unrelated and is not applied. JevRouter live decision dec_47496d7b-a4d8-406d-8d44-8dff0bec4211 selected skill-upgrades. Repository guard ALLOW for rig-capabilities; BLOCK for rig-design-studio-os authoring paths. Zone guard reports pre-existing mixed spec/code changes. Those changes are preserved; no clean-zone or certified completion claim is possible from this tree. Applied pattern coding.agents.deterministic-core-bounded-agentic-edge matches fixed evidence checks and bounded reviewer judgments; dated pattern retrieval is reference only.
