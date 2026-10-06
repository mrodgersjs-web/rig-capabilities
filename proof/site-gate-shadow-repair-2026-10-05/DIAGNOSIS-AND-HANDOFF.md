# Candidate shadow-output collision and admission stop

Status: incident mechanism reproduced; implementation blocked. This is a read-only operational diagnosis plus disposable-fixture reproduction, not a candidate upgrade or production adoption.

## Observed collision

The owner-authored receipt was read at its supplied SHA-256 `5e2d56e4cdf586a3572699e1156940e8ca0458aa8b6821caacab4c6ff35c30f9`. The owner is Aside conductor `QC6DdpCd7rfnfiru`; its `_gate/SHADOW-V2.md` reports a shadow invocation of canonical gate SHA-256 `9279221095b97582c5a0ec02434ff92c6d58508f1870d2c6cb803c37cb287407` without `--verifier-key` or `--airtable-record` at 11:01Z. Exact historical shell argv/runner were not recovered from the bounded accessible source. Searching the named `_tools` and `_gate` directories found the shadow document, not a runner. No blocked Aside history was used.

Fifteen archived v2 outputs actually exist under the owner's `_gate/shadow-v2/`, dated 11:01:11–11:01:12Z. All have FAIL, 0/1, C00 `operator-trusted --verifier-key required`. Their fifteen corresponding live gate outputs now have PASS 27/27. This observes current replacement/regeneration, not restoration of the original bytes or full client acceptance. The document's table contains sixteen rows, but only fifteen archived outputs were found; TransformFit has no archive in this snapshot.

`graft grep 'gate-result.json'` locates the canonical writes at gate.py lines54,65,152. `graft callers main --in capabilities/skills/jev-site-gate/ --depth all` shows its module entrypoint. The CLI has no dry-run/output-path options. It creates the site's evidence directory and replaces `evidence/gate-result.json` with RUNNING before checking trust, then replaces that same path with C00 FAIL. Omitting an Airtable record suppresses Airtable updates, not local writes.

The actual command in `reproduction.json` ran the unchanged candidate against a disposable fixture. It replaced the fixture's active-v1 PASS marker with C00 FAIL and exited1. No production gate was executed. This proves the collision mechanism without reconstructing an unavailable historical command.

## Exact admission blocker

Two ordinary startup checks reported DEGRADED, `hard_stop:false`, with `live:jake_founder_heartbeat` FAIL despite `blocking:false`. Mike's standing live-Jake-gate rule and the coordinator's explicit instruction preserve the implementation stop; neither metadata flag waives it.

The latest observed heartbeat was generated at11:24:33Z. At11:33:22Z its age was529.340914s, below the1800s health threshold. The loaded launch agent has StartInterval900s and RunAtLoad=true. Actual launchctl print returned exit0, runs151, last exit code0, and not running between scheduled invocations. Payload status and report/Markdown hashes pass. This is not a missing, unloaded or stale heartbeat observation.

The heartbeat's attached proof generated at11:24:58Z has FAIL. Its only non-PASS proof gate is `jake_route_eval:freshness`, DEGRADED, referencing a route evaluation generated on2026-10-02 at11:21:46Z, age259368s at its check. The evaluation payload itself is PASS with47 cases; its default allowed age is21600s. The proof builder explicitly requires that freshness gate to be PASS. Thus successful execution/fresh heartbeat and failing qualification proof are separate facts.

A normal scheduled refresh was subsequently observed at11:39:58Z (05:39:58 Mountain), without starting a job here. Its payload is again PASS, with a new attached proof at11:40:24Z still FAIL. The final incident receipt records that proof's actual non-PASS gates and current report/hash checks. A fresh successful payload is not qualification recovery.

Owning source confirms the distinction: `rig_meta_harness/cli.py` lines876–884 attach workflow proof but return the payload's status; lines1242–1247 require route-evaluation freshness and lines1288–1293 fail a proof without those required PASS gates. `rig_meta_harness/live.py` lines1462–1512 requires the attached proof status to be PASS or pending. `rig_meta_harness/agency_catalog.py` line974 sets the21600s age limit. Its graph is stale, so these claims use the named current source spans, not stale graph edges. No graph rebuild or unrelated routine repair was performed.

## Narrow repair pending admission

The repair scope, once the prerequisite genuinely recovers, is the existing canonical gate's output side effects only. Preserve website source, claims, provider/trust state, v1 results and all unlanded edits. Do not install/adopt/promote this candidate.

Two possible shapes were considered: stdout-only dry-run results, or an explicit dry-run with a dedicated external result destination. Prefer an explicit dry-run that never writes into its input workspace, rejects provider-write flags before any effect, and emits diagnostic JSON either to stdout or a caller-owned new output path outside the input tree. Reject existing destinations and symlink/hardlink aliases rather than permitting a nominally different path to overwrite active state. This is a proposal, not implemented behavior or a safe command to run today.

Required behavior regressions include failed-trust and successful synthetic dry runs preserving all input bytes/directories, meaningful external result contents, refusal of Airtable-write combinations and output aliases, and portfolio child-mode propagation if supported. Legacy authorized result-writing behavior must remain tested. Run the original disposable-fixture reproduction after repair and obtain independent source-hash-bound review. Do not rerun the unchanged82-test suite merely to imply progress.

Pstack Bug fix steps remain the governing plan:
1. Reproduce it yourself on the matching surface via the control skill (Non-negotiables). Don't hand the repro to the user. A debug or instrumentation protocol that says to ask the user does not override this. You drive the instrumented runtime. Ask the user only with a stated, specific reason the control surface cannot reach the target, and only after driving it as far as it goes. Won't reproduce directly, force it: synthesize the trigger, tighten conditions, or instrument until it fires.
2. Binary-search the cause. Form the candidate hypotheses, then rule them out until one survives. Seed them with `how` over the affected subsystem and the **why** skill for regression history. Each pass, take the split that cuts the most remaining problem space, get runtime evidence, eliminate. When program state is unclear, add instrumentation or logging and read it as the code runs. Don't guess. Drive a long or stubborn hunt with Cursor's `/loop` command. Confirm the surviving *mechanism* with runtime evidence before the step-3 architect/interrogate fan-out.
3. Plan the fix. If it crosses a function boundary, `architect` first. Delegate implementation to a subagent using your configured bug-fix model (default `grok-4.6-fast-xhigh`) with a specific scope. Review the diff.
4. Verify on the same surface. The original repro now passes. "Inconclusive" or wrong-surface is not a pass. Flag it. Unit tests show branch behavior, not bug absence.
5. Stage the commits so the failing repro lands before the fix in git history. See the **pstack-tdd** skill for the failing-test-first cadence when the bug has a cheap local test path. Skip it when the test would be expensive, integration-heavy, or unclear.
6. Run **Opening a PR**.

Steps1–2 produced direct evidence. Step3's proposal is bounded; implementation and further workflow steps stop at admission. No recursive fleet/implementation delegation was launched. Commits, PRs and promotion are not authorized. The read Separate Before Serializing Shared State principle changes the proposal from a shared result file to an independent shadow destination. Test Behavior, Not Implementation requires asserting real CLI output and input-byte preservation, not mocked write-call absence alone.

## Remaining production-adoption gates

An actually passing live prerequisite, valid source ownership, targeted OpenSpec/BDD/zone admission, independent repair verification, held-out skill outcomes, existing approved website-QA trust, actual client/source/Miro/browser/Lighthouse QA, different-family GEV and applicable D85 remain required. The82-test gate is still a candidate; production acceptance is not established. No source fix, trust change, install, deploy, publishing, provider write, destructive cleanup, merge, commit or push occurred in this investigation.
