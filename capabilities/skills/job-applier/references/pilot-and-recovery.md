# First-five pilot and recovery

## Pilot count

The first five applications are hand-held. The order for each one is mandatory:

1. Verify the active full JD and application ledger.
2. Produce the complete working resume with clearly marked unknown facts.
3. Mike confirms, replaces, or omits the facts in the exact hashed draft.
4. Produce and visually review the final resume.
5. Mike reviews the exact application and separately approves that specific submission.
6. An authorized application operator submits once and records the employer/ATS receipt.
7. Count that distinct receipt only after it is linked to the preceding review and approval.

Compute progress from actual evidence. For a counted application, all of these must agree: employer/requisition/destination, reviewed draft hash, final resume hash, approved form-answer/attachment version, approval reference, and submission receipt. Deduplicate by the stable application identity and receipt. An old receipt without the required review/approval chain is historical application evidence, not pilot completion.

Keep the pilot at `0/5` if no qualifying receipts exist. Never initialize the count from model runs, generated DOCX files, queued applications, approvals, synthetic tests, or guessed prior activity. A timeout after clicking Submit is `submission_unknown` until reconciled; it does not increase the count.

The fifth qualifying receipt ends the hand-held pilot count. It does **not** activate background submissions or grant batch authority. Subsequent applications still need the permissions and review required by the current task.

## Approval boundaries

Resume factual review and submission approval serve different purposes. Preserve both records. A useful request after review is: “Review this final resume and the exact answers for <employer>, <role>, <requisition ID>, at <destination>. Approve this specific submission only when these versions are correct.”

An approval must identify the job and exact reviewed content. If the attachment, answer, role, destination, or material employer attestation changes, present the new content and renew the affected approval. A resume review never authorizes a submit, outreach message, profile edit, paid action, or another job.

Do not treat “apply to five” as a substitute for the pilot's five individual resume reviews and five specific submit approvals. Help Mike reach each concrete approval point; do not ask for an empty advance approval before the packet exists.

## Failure and recovery

| Observation | Required action |
| --- | --- |
| Official posting closed, removed, truncated, or unreadable | Hold this job. Save the source status. Request or locate a complete active official posting; do not manufacture requirements. |
| Full JD text supplied but current listing not independently checked | Preserve the text as supplied evidence; hold active-status verification before an application-ready handoff. |
| Existing ledger says submitted | Show the actual receipt; do not prepare a duplicate submission. |
| Ledger/checkpoint suggests a previous submit without confirmation | Mark submission unknown, inspect employer history or receipt evidence, and reconcile before retrying. |
| Resume source missing, stale, or conflicts with another source | Preserve conflicting pointers. Draft ideal patterns with visible unknowns where useful, but hold unsupported final claims and source-dependent steps. |
| Unknown employer, period, mechanism, result, or metric | Keep a bracketed working field. Mike may confirm a fact, supply a different real example, or omit it. Never silently invent the missing value. |
| Mike approves wording but provides no factual confirmation | Keep the affected claims pending. Ask only the specific factual confirmation needed after showing the useful draft. |
| Stale draft hash or source changed after review | Reject the stale review and show the changed exact draft for renewed evidence review. |
| Generated output empty, malformed, or incomplete | Preserve the failure. Use the app's bounded recovery path; do not label the run complete or manufacture a passing status. |
| Final text still contains brackets or unsupported claims | Hold finalization. Confirm, replace, omit, or truthfully narrow; recheck the summary as well as bullets. |
| DOCX missing, text differs, or layout is clipped | Hold the application packet. Regenerate from the reviewed final content and inspect the rendered artifact. |
| Missing screening fact, consent, or employer attestation | Show the exact question. Use a sourced answer or ask Mike; no general Yes/No default. |
| App or model unavailable | Retain artifacts and report the exact error. Do not restart infrastructure or switch to a submission path. |
| CAPTCHA, sign-in, or unsupported upload | Hand control to Mike and retain the checkpoint; never bypass access controls. |
| Submit timed out or returned ambiguous success | Record submission unknown. Reconcile through the employer/ATS account or confirmation before retrying; no blind second click. |
| Inactive routine references an older application flow | Update its preparation route when authorized; preserve its inactive state. Never reactivate it as part of installation. |

After two identical no-progress failures, stop retrying that step and report the saved state and exact blocker. Continue independent preparation only when it cannot duplicate or change an unresolved application.

## Status report

Use observed counts and artifact links: working drafts awaiting evidence review; final packets awaiting application review; specific approved submissions awaiting execution; submitted with receipts; submission unknown; blocked. Display the pilot receipt count separately. A skill install, successful model call, or form fill proves none of the submission states.
