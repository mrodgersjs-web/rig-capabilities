# Run the complete process in Aside

## Set up your own inputs

Select your own resume, career evidence, and official target job URL. Use an application-specific local folder. Do not paste credentials or unrestricted personal transcripts into it. Keep the master resume unchanged.

Use Aside's existing browser and document capabilities to read the live posting and prepare Markdown/DOCX. If your Aside installation cannot create a DOCX, stop the document step and configure a trusted document tool. This bundle does not install Python document libraries or change your model settings.

The required record consists of the full JD and source hash, active-posting evidence, duplicate-check result, selected source-resume hash, requirement profile, working resume, claim ledger, exact before/after changes, saved human reviews, final Markdown/DOCX, rendered pages, Jev transition receipts, and proposed application answers. Keep these together in your application folder or existing ledger.

Before provisional drafting, require the full captured JD, current activity evidence, correct target identity, passing deterministic source checks, and a valid live provider receipt passing active identity (`c01`). Once those pass, keep downstream pre-draft semantic findings visible and supply them as input to the working draft. Failed or unknown results remain holds; preserve every original receipt and its `can_advance` value. Output schema, source-ID, and candidate-fact validation still apply. The portable quality helper does not override or clear any hold. Any failed or unknown gate blocks finalization and submission until corrected evidence and fresh reviews pass. Inactive, stale, unreadable, or mismatched sources and missing or failed live identity verification cannot use this draft-first route.

## Review facts after the full draft exists

For each claim, preserve an ID and the candidate's decision: confirm, replace, or omit. Confirmation must cover the actual factual proposition. Record the actual employer, title, dates, outcome and units, personal action, mechanism, and scope where relevant. Do not interpret "sounds good" as confirmation of an invented event.

The review record must include the exact draft SHA-256 and a direct human-response reference. If the candidate supplies new facts or changes wording, produce the new draft and renew the affected review. Keep source-confirmed, candidate-reported, and independently verified status separate.

Write the final resume only from confirmed or safely narrowed claims. Create the final DOCX with the same text. Render and inspect it before the application review. The quality helper does not write or improve the resume for you; Aside and the candidate perform those steps.

## Stop before submission

Show the official destination, employer, exact role, requisition ID, full form answers, exact resume attachment and hash, other attachments, and employer attestations. Obtain a separate specific submission approval after factual resume review and human rendered-page approval.

No tool in this package submits applications or sends messages. An existing application operator may submit only after the candidate gives the necessary specific approval. Capture the real employer/ATS confirmation and reconcile ambiguous outcomes before another attempt.

## Count the pilot from receipts

Run the installed helper with your ledger:

```sh
python3 tools/pilot_receipts.py /absolute/path/to/pilot-ledger.json
```

Run this command from the installed `job-applier` skill directory. An empty ledger is `{"applications": []}` and reports 0/5. Each application record uses this shape. The file paths can be relative to the ledger directory:

```json
{
  "applications": [{
    "employer": "Verified employer",
    "requisition_id": "Official requisition ID",
    "destination": "Official application URL",
    "draft": {"path": "working.md", "sha256": "actual hash"},
    "final_resume": {"path": "final.docx", "sha256": "actual hash"},
    "answers": {"path": "answers.json", "sha256": "actual hash"},
    "evidence_review": {"path": "evidence-review.json", "sha256": "actual hash"},
    "submission_approval": {"path": "submission-approval.json", "sha256": "actual hash"},
    "submission_receipt": {"path": "submission-receipt.json", "sha256": "actual hash"}
  }]
}
```

The referenced review JSON requires `status: factually_confirmed`, matching `draft_sha256` and `final_resume_sha256`, `human_response_reference`, and `human_page_approval_reference`. The approval JSON requires `action: submit_this_application`, `human_response_reference`, matching `employer`, `requisition_id`, `destination`, `final_resume_sha256`, and `answers_sha256`. The receipt JSON requires matching identity, `status: submitted`, `provider_receipt_id`, and `provider_evidence: {path, sha256}` pointing to the saved actual employer/ATS confirmation. Record timezone-aware ISO timestamps as `reviewed_at`, `approved_at`, and `submitted_at`; the helper rejects a chain whose timestamps are out of that order.

These are schema examples, not fabricated receipts to fill in automatically. The helper checks bindings, local evidence files, and duplicates. It cannot prove that a human response or provider confirmation is authentic. The operator must inspect the original evidence before counting it. Without a real chain, progress stays unchanged.
