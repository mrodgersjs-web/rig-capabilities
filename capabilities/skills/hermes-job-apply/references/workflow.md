# Operating workflow

## 1. Resume and answer bank

Read the complete selected source file. For DOCX, extract paragraphs and tables in document order using a local parser; verify that employment headings and dates survived extraction. PDF extraction must be available and readable; do not substitute a placeholder or smoke-test resume. Keep the file path and SHA-256 in the run manifest. If the master changes, re-extract and reconcile affected answers before resuming.

Build an evidence table of employer, explicit alias, title, dates, and source section. A client mentioned in a project does not enter this table. Use exact normalized names (case/whitespace only) plus explicitly sourced aliases. No fuzzy matching. Distinguish current employment from ever-employed questions; year-only dates cannot settle a question requiring a precise current date or month.

The private answer bank starts from `assets/answer-bank.template.json`. Entries record the exact question meaning, answer, source reference, verification date, and scope. A user correction supersedes a conflicting saved answer for its stated scope. If it changes employment history, save the correction and mark the resume binding for reconciliation; never claim the file was updated unless it actually was.

Keep unknown answers null. Ask a concise grouped question only for facts needed now. Save the reply once and reuse it for equivalent questions; re-check wording, time frame, and company scope each time. Do not transform a No to “need sponsorship now” into a No to “need sponsorship now or in future.” Do not round overlapping experience upward or invent missing months.

The typed unresolved-answer outcome is `NEEDS_MIKE`; keep the answer value null. Legacy `needs_evidence` is an input alias for `NEEDS_MIKE`, not permission to guess. A sourced user selection changes the resume binding to `selected_by_user` with `selection_reference`, path, and hash. The current registry's original candidate remains unselected until that occurs.

## 2. Job intake and duplicate protection

Start with supplied URLs or the existing cockpit queue. If asked to find jobs, use current employer career pages and available search tools, verify each role is still open, and record the source and checked time. If the job description cannot be read, hold fit-dependent drafting instead of inventing requirements from the title.

Use employer + ATS requisition ID as the application key. Fall back to the canonical application URL after removing tracking parameters while preserving requisition identifiers. Same title with a different requisition can be a different job.

Before filling, check the existing tracker, this workflow's checkpoints, and the logged-in ATS application history where available. Preserve legacy applied/submitted statuses. If history cannot be checked, record `history_unverified`; investigate before final submission. Never overwrite the cockpit's schema or invoke an old pipeline that deploys a website as a side effect.

Evidence handling is explicit: a matching ATS confirmation/receipt establishes `already_applied` and skips filling/submission. A tracker-only Applied/Submitted row establishes `duplicate_held`, also skipping submission while evidence is reconciled; it does not create a receipt or become `submitted`. If tracker, checkpoint, and ATS disagree, retain all evidence and use `duplicate_held`. Absence from a current ATS list does not invalidate a prior receipt. Resolve the exact account/requisition and, if still inconclusive, ask Mike before a new application attempt.

## 3. Tailor the packet

Produce the requested resume variant and, when useful or required, a cover letter under 300 words. Use employer-specific requirements and resume-supported examples. Keep the source master untouched. Omit unsupported claims even when a legacy template says every bullet needs a number.

Save: job description snapshot/source URL, requirement-to-evidence map, tailored documents, complete answer sheet, unresolved questions, and resume hash. Keep identity/contact details in private per-job files, never in capability source or shared examples. Do not include RIG client/private pipeline data in a personal job application.

## 4. Fill and read back

Use the available browser's documented tools, the user's authenticated session when authorized, and fresh element references after every navigation. Do not reset a profile or close unrelated tabs. Read complete labels, helper text, option values, and time qualifiers; ignore preselected answers until verified.

Record each question's exact text, selected answer, evidence, and verification state in the per-job answer sheet. After filling, read back visible values. Upload only the correct job-specific file and verify the filename/attachment preview. If the connected browser lacks an upload tool, request the human upload that file, then continue; do not invent an upload command or claim it happened.

If login, OTP, CAPTCHA, or an access restriction appears, preserve state and request the required human step. Do not switch tools to evade a restriction. Missing optional fields may remain blank; missing required facts block that job, not the rest of a batch.

## 5. Submission and evidence

Prepare a compact review: employer, role, requisition, resume variant, cover letter, material answers, unresolved items, and target URL. Check existing scoped authorization and any active harness Gate-D requirement. Do not send recruiter messages or enroll in unrelated marketing as part of applying.

Persist `submitting` with the intended target and timestamp immediately before the final action. Submit once. Confirm the resulting application ID, ATS status, confirmation page, or employer acknowledgement. Save `submitted` only with that evidence. A draft/save confirmation is not a submission receipt.

On ambiguity, save `submission_unknown` and perform read-only receipt/history reconciliation. If no conclusive evidence exists, ask Mike before another submission attempt. Do not label an application failed simply because the browser disconnected after the click.

## 6. State and resuming

Private state directory: `/Users/rig128gb/Documents/JakeStudio/Personal/Job Applications/`. Use `applications/<stable-key>/checkpoint.json`, `answers.json`, and job-specific documents. `assets/application.template.json` gives the checkpoint fields. This is a documented state contract executed by Hermes, not an installed transaction engine.

Use one writer for applications. Create directories with owner-only permissions and files with mode 0600. Save JSON through a temporary file in the same directory followed by atomic replacement; preserve the last valid version before migration. No tokens, cookies, passwords, full browser profiles, or credential-bearing URLs in state or receipts.

Legal transitions:

`discovered → preparing → ready_for_review → submitting → submitted`

`preparing/ready_for_review → blocked → preparing` after resolving the named blocker.

`submitting → submission_unknown → submitted` only after reconciliation; a new submit needs explicit retry authorization after failed reconciliation.

Any pre-submission state may become `already_applied` on matching prior receipt or `duplicate_held` on a tracker-only claim/conflict. `duplicate_held → already_applied` requires reconciliation evidence; `duplicate_held → preparing` requires a documented resolution showing no duplicate or Mike's explicit instruction to proceed despite the unresolved history. `already_applied` is terminal here and remains distinct from applications submitted by this run.

`submitted` is terminal for this workflow. A request to withdraw is a separate scoped action. Resume by reading the checkpoint, verifying the source hash and live page, and reconciling any uncertain submission first. Never assume the last browser position persisted.

Operational limit: two attempts for the same transient navigation/read failure, one final-submit attempt, then checkpoint and explain the blocker. End at the requested batch size or when Mike says stop. There is no background auto-apply schedule in this package.
