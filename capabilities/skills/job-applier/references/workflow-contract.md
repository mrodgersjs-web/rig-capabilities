# Job Applier workflow contract

## Local surface and dependencies

The local app lives at `/Users/rig128gb/Developer/aside-work` and is served at `http://127.0.0.1:4912`. Its displayed workflow is **Job Applier**. The persisted skill ID remains `executive-resume` for compatibility with existing runs.

The installed skill lives at `/Users/rig128gb/.aside/u/0/skills/user/job-applier/SKILL.md`. Its canonical source is `/Users/rig128gb/Developer/rig-capabilities/capabilities/skills/job-applier/`. The four existing Lucy packages remain separate dependencies. On this workstation the intact full source pack is `/Users/rig128gb/.omp/agent/skills/lucy-skills/`; the loaded sibling router names the correct resume leaf.

Start from an Aside chat: **“Use Job Applier for this role: <official posting URL>. Prepare the full working resume, then walk me through the evidence review. Stop before submission.”** The Aside agent captures the full source and its identity/activity evidence, calls the structured local API below, and opens the resulting review board. Pasting a bare URL into the board is not a supported launch path and does not supply the required source evidence.

Use the existing app at `http://127.0.0.1:4912`, selected canvas, and configured model. Do not launch a second server, create an automation, change provider configuration, or replace the source resume registry just to run this workflow.

## Local start request

The app accepts `POST /api/runs` with this structure:

```json
{
  "canvas": "<existing selected canvas ID>",
  "skill": "executive-resume",
  "objective": "Prepare the Job Applier working resume for <employer and exact role>; stop for Mike's evidence review.",
  "model": "<model ID selected from the app's current supported models>",
  "resume_input": {
    "posting_url": "<official active employer or ATS URL>",
    "posting_text": "<complete JD text; preserve source and retrieval evidence>",
    "target": {"company": "<employer>", "role": "<exact role>", "id": "<official identifier>", "url": "<canonical official URL>"},
    "activity_evidence": {
      "checked_at": "<actual ISO timestamp>",
      "http_status": 200,
      "application_form_present": true,
      "response_fields": {"<actual captured ATS field>": "<actual captured value>"}
    },
    "capture_provenance": {
      "jd_sha256": "<SHA256 of trimmed posting_text>",
      "source_jd_file_sha256": "<optional full captured file hash>",
      "source_capture_sha256": "<optional raw capture hash>",
      "checked_at": "<actual UTC ISO capture timestamp>",
      "source_path": "<capture provenance path>"
    },
    "qualification_gaps": []
  }
}
```

Angle-bracket values above are request-template fields, never literal production inputs. Record actual activity evidence; do not set the success status or form flag merely because the template contains them. `response_fields` must contain actual captured ATS identity and application-entrypoint fields. Activity must be within 24 hours, with no more than five minutes of forward clock allowance. Use actual qualification gaps, not an empty array when unresolved gaps exist. Omit optional provenance fields when unavailable rather than inventing their values. Historical sources are already server-configured; do not place private career files in `posting_text`.

The `model` field is optional; omitting it retains the configured existing model. If supplied, select a currently supported model ID. The current implementation accepts the `glm-5.3-flash-uncensored` route, but availability must be checked from the app rather than assumed from this document. Do not run a model request during installation or discovery verification.

Input limits: `posting_text` is 300–60,000 characters; target and activity objects are each at most 20,000 JSON characters; provenance strings are at most 2,500 characters; qualification gaps contain at most 20 strings of at most 2,000 characters each.

Current generation sequence: analyze the target executive requirements, then compose the full working resume. The run pauses at durable `awaiting_evidence`. Read the app's returned record and artifacts; do not claim that a successful request alone proves usable content or a completed review.

The draft-first boundary requires a full captured JD, current activity evidence, correct target identity, passing deterministic source checks, and a valid live provider receipt passing active identity (`c01`). Once those pass, downstream pre-draft semantic findings are recorded, displayed, and supplied to the provisional draft generation. Preserve the original receipts and every failed or unknown result; none becomes PASS. `draft_permission` remains `PROVISIONAL`, and visible quality holds explain what needs attention. Output schema, source-ID, and candidate-fact validation still apply. Missing or invalid live identity evidence, stale or closed roles, mismatched identity, or a deterministic source failure cannot use this route. Every failed or unknown gate blocks evidence-to-final advancement, final downloads, application readiness, and submission. Recheck after meaningful corrections; do not repeatedly send unchanged inputs merely to obtain PASS.

## Continue an eligible failed run

Recovery uses the same `POST /api/runs` endpoint and schema, adding **`resume_input.continue_source_run`** with the prior failed run ID. Use the same canvas. Copy the exact `posting_url`, `posting_text`, `target`, `activity_evidence`, `capture_provenance`, and unchanged known `qualification_gaps` from that run's server-returned `resume_packet`. Serialize the actual captured values; do not send invented timestamps, client-authored receipts, or `can_advance` flags.

The server checks exact source SHA, URL, target, activity and provenance equality; original receipt integrity and context; current rubric and deterministic admission; and a valid live c01 source pass. Retained ideal output must still pass schema and source-ID validation. Eligible original source/ideal receipts are reused without rescoring.

The deterministic source-only fallback specifically requires an earlier run with `status=error`, packet `stage=generating`, retained `ideal_markdown`, and no draft. An initial failure does not automatically invoke it. An eligible explicit continuation uses literal source-only draft content without another generation call, records the failed run/hash/error, and keeps the final hold. Other continuations may perform missing normal generation. Normal generation calls retain their existing 600-second wall-clock and 6,000-token limits; do not change shared model settings to recover a run.

If the capture is stale or has changed, recapture the actual source and start a new revision without `continue_source_run`. Never edit old timestamps or receipts to make recovery appear eligible. There is no recovery button; the Aside agent performs this supported API continuation.

After start or continuation, poll `GET /api/state?canvas=<id>` for the returned `run.id`. Once the packet reaches `awaiting_evidence`, open the returned working node at `http://127.0.0.1:4912/?focus=<working_node>#<canvas>` and its `review_node`. Use actual returned node IDs. Request success alone does not prove that a working draft or review checkpoint exists.

## Word fidelity and job-specific content acceptance

The selected master DOCX is the immutable template for working, review, and final Word artifacts. Current workstation source: `/Users/rig128gb/.applypilot/resumes/masters/Mike-Rodgers-Resume-FINAL-v3-2026-10-06.docx`. Record the actual selected path and SHA-256; use a separate output copy. Preserve styles, fonts, paragraph/run properties, numbering, margins, page setup, headers/footers, and section structure/settings. A fresh Markdown-to-DOCX document is not template preservation. If this cannot be done, expose the limitation and hold the Word deliverable rather than passing a generic export.

Retain evidence of meaningful role-specific summary, capabilities, and experience edits with a requirement-by-requirement before/after map. Each row binds the JD requirement to the actual employer/source, original text, proposed text, and factual limits. Retained already-relevant text needs a rationale. Title substitution, copying source prose, or producing a map without applying supported edits is insufficient. Ask Mike about missing facts; do not infer new facts or metrics from the JD.

Before review, verify the master hash is unchanged, compare template styles/numbering/section properties, and inspect rendered original/output pages for layout fidelity and readable pagination. Record changed content separately from formatting evidence. Content growth may change page count; formatting changes need explicit review rather than silent margin/font substitutions.

Source-only continuation remains **SOURCE-ONLY RECOVERY — TAILORING INCOMPLETE**, even if its document renders or a durable `awaiting_evidence` checkpoint exists. Display that label in the review surface/receipt, not the employer-facing resume body. Preserve existing holds and return to substantive job-specific rewriting and before/after review. Neither continuation success nor literal source fidelity satisfies tailored-resume completion or final readiness.

## Review and finalization

Use the app's evidence review controls. They call `POST /api/resume/review` and bind confirm/replace/omit decisions to the recorded working draft hash. The request is:

```json
{
  "canvas": "<existing canvas ID>",
  "run": "<run ID>",
  "draft_sha256": "<resume_packet.draft_sha256>",
  "decisions": [
    {"claim_id": "c01", "action": "confirm"},
    {"claim_id": "c02", "action": "replace", "text": "<Mike's factually supported replacement>"},
    {"claim_id": "c03", "action": "omit"}
  ],
  "claim_evidence": [
    {"claim_id": "c02", "employer": "<actual employer>", "title": "<actual title>", "period": "<actual period>", "personal_contribution": "<confirmed contribution>", "result": "<confirmed result>", "strategy": "<actual strategy>"}
  ]
}
```

Include every actual claim item once when completing review. The example claim IDs do not imply every draft has three claims. `text` is required for replace. Proposed or unplaced examples retained in the final draft need the actual candidate-confirmed `claim_evidence` fields. Save partial choices with the same shape to `/api/resume/progress`. Never forge Mike's review event.

`GET /api/state?canvas=<id>` returns `runs[].resume_packet`. Retrieve artifacts with `GET /api/resume/artifact?canvas=<id>&run=<runid>&kind=<kind>`, selecting an actual kind such as `ideal`, `working`, `working-docx`, `review`, `review-docx`, `working-page-1`, `page-1`, `final`, or `final-docx`. Final artifacts are denied until the required quality receipts and exact-page human approval exist. Durable records live at `/Users/rig128gb/.rig/live/aside-work/<canvas>.json`, with the append-only `.json.journal` beside them.

After factual review and the evidence/content quality checks, the app produces the review document and pauses at `awaiting_document_review`. Changed sources or a changed draft require refreshed review. Resolve every final claim: confirm from evidence, replace with an actual supported example, omit, or narrow without inventing a fact. A blanket assertion of experience does not fill missing dates, employers, metrics, or mechanisms.

## Render and review the exact document

Use `POST /api/resume/document` through the app controls. Every action includes `canvas`, `run`, and `action`:

- `working_render` and `working_check` include the exact `draft_sha256`.
- `render`, `check`, and `approve` include the exact `final_sha256`.
- `check` and `approve` include the returned `manifest_sha256`.
- Image checks include `redaction_reviewed: true` only after actual pixel review confirms safe external content.
- `approve` includes `approved: true` only after Mike explicitly approves those exact facts and pages.

Manifests are generated by the server from actual rendered documents. Do not invent a manifest, review receipt, redaction confirmation, or approval event. Inspect the returned stage and blockers. The `application_review` state is reached only after the required live stage receipts and the exact-page human approval pass. These are local experimental gates, not production certification or submission authority.

The application review state is the handoff to Mike. This app has no submit step. If Mike later authorizes a specific submission, use the established application operator within that exact scope and return its real receipt to the same application record. Do not call a submission tool as part of this package's local generation or review route.

## Record to retain

Keep these facts with the existing run/application record, using its native schema rather than maintaining a competing second ledger:

- Application identity: employer, role, requisition ID, canonical destination, duplicate-check result and pointer.
- Posting: full JD, active-status evidence, retrieval time, source path and SHA-256.
- Career inputs: selected resume path/hash, claim source IDs, exact supported employer/title/date fields and limits.
- Working output: complete resume, requirement matrix, claim ledger, before/after changes, exact draft SHA-256.
- Evidence review: Mike's authenticated or direct response reference, time, draft hash, per-claim confirm/replace/omit decision and factual content.
- Final output: Markdown and DOCX paths/hashes, content check, rendered layout check, remaining fit gaps, proposed screening answers.
- Application review: exact destination and content to be submitted; hold until separate specific approval.
- If a later approved submission occurs: approval reference, matching final content hashes, actual employer/ATS receipt, submission time, and reconciliation status.

Do not write passwords, session cookies, access tokens, or unrestricted private transcripts into these records. Save the minimum evidence needed to review the claims and reconcile the application.

## Morning use

Mike starts in Aside chat with **“Use Job Applier for this role: <official posting URL>.”** The agent captures the full source, target identity, activity and provenance, calls the structured start or eligible continuation API, then opens the actual working draft and review board. A bare board paste is insufficient. Read the complete draft and walk Mike through confirm/replace/omit decisions. Show the final resume and exact proposed application only after the required reviews pass, then stop for separate submission approval. For the pilot, finish one reviewed application before moving to the next submission decision.

A second role can be researched while one waits for review, but never apply the first role's approval to the second. If Mike pauses, preserve the current record and resume from its last observed state.

## Original-format review boundary

Follow [original Word fidelity](word-format-fidelity.md). Use the source DOCX package and existing paragraph/run slots. Keep banners, process notes, questions and requirement maps in a separate linked review worksheet. Red proposed edits retain original layout; UNCONFIRMED status is explicit in comments or the exact-draft/claim-bound worksheet. Verify paragraph/run formatting and every rendered original/output page using the same renderer/settings. Style-hash parity alone cannot establish visual fidelity. Never delete source history or shrink formatting to make space.
