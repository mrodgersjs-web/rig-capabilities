# Daily durable Job Applier execution contract

Status: required design and acceptance contract, not a deployed Temporal workflow. Aside owns runtime implementation and execution. Codex maintains these skills only. No worker, server, daemon, schedule or routine is installed, restarted or enabled by this document.

## Observed activation blocker

The 2026-10-29 owner probe reported Temporal serving at `127.0.0.1:7233`, but startup failed `live:temporal_owner` with `owner_inventory_incomplete`: unresolved `oxygen-watch-helper` script and invalid `rig-dashboard` plist. The dependent Temporal gate also failed. The schedule inventory showed `aside-chat-loop-watchdog`, not a Job Applier schedule. This is a time-bound observation from the coordinating run, not a permanent health assertion. Activation remains blocked until the owning Aside lane resolves ownership and passes a fresh check. The approved local skill/workflow exception permits these document updates only; it does not approve service changes or schedule activation.

## Daily coordinator and identity

The proposed daily coordinator targets 30 applications per local calendar day. This is a target, not a guarantee and never permission to skip evidence, reviews or approval. Report distinct discovered, drafted, awaiting facts, awaiting page review, awaiting submission approval, submitted-with-receipt, blocked and unknown counts. Only real receipts count as applications submitted.

Default schedule is daily 18:00 in `America/Denver`, following the user's 6 p.m. preference; make timezone, time, daily target and concurrency explicit configurable values. Preserve daylight-saving behavior of that named timezone. Use overlap policy SKIP. Limit missed-run catchup to the most recent scheduled run within a configured 24-hour window; do not replay a backlog of daily quotas. A skipped or missed day does not authorize extra submissions tomorrow.

Before configuring a schedule, inventory current schedule/routine ownership and the existing worker/server health. Reuse the established healthy Temporal service and owned worker. Do not launch parallel daemons or reactivate old Aside routines. One owner dispatches the daily coordinator. Existing routines may route to its idempotent entry only after explicit integration; no duplicate trigger can create another application for the same job. Health failure is a visible hold for the owning Aside lane, not authority to restart or replace infrastructure.

Keep each daily coordinator bounded to ten minutes of discovery, admission and reconciliation by default; do not wait for human-reviewing jobs to finish. Application children survive coordinator closure through an explicit `ParentClosePolicy.ABANDON` when implemented as children, or durable independent application workflows with equivalent tracked ownership. Their own step children and waits stay attached to the application workflow. Record the chosen lifecycle policy and prove it with restart/parent-close tests. Do not silently cancel or orphan waiting applications. Thus a human wait does not leave the daily coordinator open forever and cause tomorrow's SKIP policy to suppress discovery.

Default discovery selection budget is 30 new unique job admissions per Denver day, with a global cap of 30 active/pending application lineages. Both are explicit configurable limits. Count admissions atomically across scheduled, manual and retry coordinator invocations; retrying or attaching an existing job does not consume a new admission. When the pending cap is reached, reconcile or surface the backlog and admit no new jobs. A missed target is reported honestly; do not accumulate an unlimited backlog or issue catchup quotas. Count submitted applications by their actual verified receipt timestamp converted to America/Denver, not by discovery date, workflow start or retry time. Global receipt deduplication applies before daily totals and first-five totals are incremented.

Maintain a global application ledger across all dates, routines and coordinators. A stable job key combines candidate identity, canonical employer identity, ATS/requisition identifier and canonical posting URL. Normalize aliases before creating it. If the employer supplies no requisition, use a deterministic canonical-URL identity; never generate a fresh random key per discovery. An ambiguous possible duplicate stays on reconciliation hold. Workflow identities are per employer/requisition and candidate, not per day. A source revision changes artifact/version bindings within the same application lineage; it does not make a second application.

## Eight durable child workflows

Every job application workflow invokes the existing eight leaf skills in order, with a durable child workflow for each step. Each step identity binds the stable job key, step name and explicit revision. A retry resumes that identity rather than inventing another. The daily coordinator discovers or attaches to existing application lineages; human-waiting children remain durable across daily coordinator completion.

| Child step | Required checkpoint output |
|---|---|
| posting-inventory | Verified target, captured JD/hash/activity, atomic inventory, global-ledger duplicate decision. |
| ideal-candidate-persona | All 13 persona sections, current JD/inventory bindings and actual Jev review receipt. |
| ideal-achievement-bank | Result/action/strategy examples covering every requirement, with hypothetical status and explicit gaps. |
| evidence-alignment | Authenticated multi-account GitHub audit, exact source SHAs, private-evidence treatment, source-backed claims and attribution gaps. |
| word-review-copy | Immutable-template proof, complete tailored red UNCONFIRMED Word copy, separate clean copy and before/after map. |
| targeted-confirmation | Actual authenticated per-claim confirm/replace/omit responses bound to current job and draft. |
| document-quality | Current content/format checks, all 15 criteria, actual page images, Jev receipts and exact-page approval. |
| application-approval | Exact application manifest, separate submission authorization and real receipt or reconciliation hold. |

A durable checkpoint records workflow/run/child IDs, step/revision, target and JD hash, input/output artifact paths and hashes, Aside session/task IDs, dispatch operation ID, activity receipt IDs, last observed state, unresolved holds, approval references and receipt identity. Store sensitive artifacts in the governed local evidence store; workflow history carries minimal references/hashes and sanitized metadata rather than raw private career/code material. No boolean can substitute for a step's actual execution response.

## Aside activities and retry rules

Workflow orchestration must remain replay-safe. Browser/ATS operations, model/Jev calls, filesystem/document work, GitHub reads, ledger writes, clock-dependent source capture and other I/O occur only through Aside-owned activities. Persist the Aside session/task correlation before waiting for completion. Pass the leaf path/version, stable job/step/revision key, input hashes and bounded purpose to each activity. Resume the same Aside task when possible; never mistake a lost poll response for a failed dispatch.

Use a durable dispatch intent and idempotency key before invoking Aside. Aside must enforce that key so a crash between remote acceptance and local acknowledgement can be recovered by lookup. Before any retried dispatch, query the existing operation/task by key and reconcile its state. Poll/retrieve an accepted task rather than dispatch another. If the interface lacks that recovery path, hold for reconciliation instead of pretending exactly-once execution.

Set finite activity start-to-close and schedule-to-close timeouts plus a capped retry policy. Default safe read/poll attempts are at most three with backoff within a ten-minute overall window; long document/model operations need their own explicit bounded timeout and heartbeat settings. Retry only classified transient transport failures. Semantic BLOCK/DEFER, invalid input, absent source, authentication failure, human waits and ambiguous external effects are not retry-until-PASS cases. Exhaustion persists an actionable checkpoint. Human waits use durable signals, not an open activity or a tight polling loop.

## Human review and approval signals

Only the authenticated user interface can deliver accepted review signals. Validate actor/scope on the ingress service and persist its authentication evidence. A caller-supplied name, a model-written `approved: true` or an arbitrary JSON receipt is not authenticated approval. Deduplicate each signal by signal/event ID.

Use distinct signal types for factual claim review, exact rendered-page approval, and specific application submission approval. Each binds the candidate/job key, requisition/destination, workflow revision, relevant draft or clean DOCX hash, and human response reference. Page approval additionally binds the rendered manifest/page hashes. Submission approval additionally binds the complete application manifest: resume, form answers, attachments, destination and attestations. No approval transfers between roles, dates, revisions or materially changed form answers.

A changed JD, source fact, claim, draft, final DOCX, rendered page manifest or application payload invalidates every dependent approval and receipt. Recompute dependency hashes and return to the earliest affected checkpoint; preserve old decisions as superseded evidence. Never erase audit history to make an approval appear current. Send no application while facts/pages/quality or specific approval remain unresolved.

## Submission uncertainty and first five

Before attempting submission, atomically reserve the application action in the global ledger using its job key, manifest hash and specific approval ID. Check existing submitted, in-flight and unknown records. At most one authorized attempt may own that reservation. Record actual destination and attachment hashes.

Disable automatic retries of the external ATS submit action. A timeout, browser crash, missing acknowledgement or ambiguous success becomes `submission_unknown`. Reconcile using the employer/ATS receipt, application history or confirmation evidence; never click submit again merely because the worker restarted. A confirmed no-submission outcome may permit a new explicitly tracked attempt under still-valid scope, but only after reconciliation. Missing proof remains held.

The first-five counter is global and advances only for unique real employer/ATS receipts linked to matching factual/page review and specific submission approval. Replayed events, duplicate receipts, tests, drafts and approval-only records do not increment it. Five completed applications never unlock blanket autonomous submission. The daily target cannot override these boundaries.

## Planned quality requirements

Preserve the [fifteen criteria](quality-gates.md): active identity; complete JD; visible qualification gaps; requirement/example coverage; employer/title/date attribution; result/contribution/strategy; defensible metrics; focused factual questions; fitted summary; concise honest language; ATS-readable structure; alignment/whitespace; font/headings; unclipped pagination; and exact artifact/source/review binding with human approval.

Each relevant child stores the actual typed Jev decision ID and original receipt. Missing/unavailable/uncertain review remains a hold. Inspect actual sanitized rendered page pixels, not filenames or text previews. Private GitHub source remains local; only sanitized supported capability descriptions enter hosted review payloads. Revalidate all image/content and approval bindings after changes. These are planned runtime acceptance requirements, not proof that the current app/Temporal worker implements them.

## Required failure and replay proof before claiming live

Aside must implement and run reproducible tests that establish all of the following:

1. Worker restart after each step restores the exact checkpoint, Aside task ID and current artifacts without redoing completed side effects.
2. Crash after dispatch acceptance but before acknowledgement recovers by idempotency key with no second Aside task.
3. Temporal history replay produces no new browser/model/filesystem/GitHub side effect and preserves deterministic workflow decisions.
4. Overlapping triggers and bounded catchup attach to the same global job lineage and never duplicate an application.
5. Duplicate, stale, wrong-actor and cross-job signals are rejected; valid distinct factual/page/submission signals resume only their matching waits.
6. Changed JD/draft/pages/form answers invalidate dependent approval; old approvals cannot submit the new content.
7. Jev outage, invalid response, semantic hold, missing image and unsanitized private evidence fail closed at the affected transition.
8. Uncertain ATS submission after restart stays unknown without retry; reconciliation and duplicate receipt events leave the counter correct.
9. Global first-five count survives restart/day rollover and requires receipt-linked approvals; the 30/day target never bypasses holds.
10. Exhausted bounded retries, source closure and cancellation preserve evidence and expose the next safe action without orphaning work.

Retain commands, failing-control cases, actual Temporal workflow/run/history references, Aside task receipts, artifact hashes, source revision, owner/health evidence and verifier results in the runtime proof packet. Skill installation, passing standalone packet tests and a healthy Temporal endpoint do not establish these behaviors. Until that evidence exists report **skills installed; durable daily runtime not verified**. This document does not activate the schedule.

## Aside session bounds

Every step activity follows [bounded step execution](bounded-step-execution.md). Persist checkpoints and complete originals; pass only bounded source projections to one leaf session. Context-limit/failed-compaction errors do not retry the old session. Reconcile its existing operation, then recover the same logical step from pointers/hashes in a fresh session, preserving attempt counters, approval bindings and submission uncertainty. These are required runtime behaviors, not a claim of current enforcement.
