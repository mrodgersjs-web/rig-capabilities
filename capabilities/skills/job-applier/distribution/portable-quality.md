# Run the quality checks

Run the installed `tools/resume_quality.py` CLI for each transition. Read [the adapter reference](quality-api.md) for the exact arguments, JSON fields, typed criteria, and receipt format. The adapter uses only Python's standard library and the recipient's own `TYPESAFE_API_KEY`. It sends the supplied sanitized review state to TypeSafe. It does not generate a resume, choose facts, or grant approval.

Required transition order: `posting`, `ideal_profile`, `working_draft`, `working_image`, `evidence_review`, `final_content`, `final_image`, `application_ready`. Save each actual result with the source and artifact hashes. Failed, missing, timed-out, malformed, or unconfigured calls never count as PASS.

The fifteen criteria cover active posting identity; complete JD and duties; visible qualification gaps; requirement-to-example coverage; employer/title/date attribution; result and personal contribution and strategy; defensible metrics and periods; focused missing-evidence questions; role-specific executive summary; concise honest language; ATS structure and natural keywords; alignment and whitespace; font and hierarchy; pagination without clipping; and artifact/source/review binding with human approval.

The working-draft request includes the full posting, full draft, working text, qualification gaps, excluded claims, missing-evidence questions, and every historical row referenced by a draft item's `source_evidence_id`. It omits unused history from this hosted stage and records included/available counts, while the context hash still binds the complete local packet. No referenced row is truncated. Oversized, invalid or unavailable provider replies remain holds; preserve any recorded typed error code. Request acceptance alone is not a passing quality judgment.

## Prepare actual page images

Remove personal contact details and unnecessary identifiers from a review copy while preserving the final layout. Record the relation between the final DOCX hash and the sanitized review copy hash. Render that copy. Also inspect the original final DOCX pages locally before approving the application.

From the installed Job Applier skill directory:

```sh
python3 tools/render_resume.py /absolute/path/to/sanitized-final.docx --source-sha256 ACTUAL_MARKDOWN_SHA256 --output /absolute/path/to/new-render-folder
```

The output folder must not exist yet. The helper locates installed `soffice`, `pdfinfo`, and `pdftoppm` through PATH and the supported existing macOS/Codex-runtime locations documented in the API reference. It saves the PDF and real PNG pages, and writes `render-evidence.json` with the exact `renderer_programs` used. It neither installs software nor calls a provider. Missing executables remain an explicit error. Review the pages locally and ensure no private content remains before setting each page's `redaction_reviewed` to true and supplying the manifest to the image gate. Never set that flag without actual pixel review.

The adapter requires actual sanitized still PNG pixels within its 280–1568 pixel bounds. A text extraction, DOCX filename, visual description, or mock page is not image evidence. The renderer scales the longest dimension to 1568; the adapter checks the actual accepted dimensions.

Use the same render procedure for the working DOCX before evidence review. For `working_image`, set the manifest's `source_sha256` to the exact working Markdown hash. For `final_image`, use the exact reviewed final Markdown hash. The CLI accepts `--source-sha256` for this binding.

The experimental image API provides advisory visual evidence. A `final_image` PASS means those criteria met the configured policy. An uncertain image judgment returns `NEEDS_HUMAN_REVIEW`, which cannot advance and does not prove that the formatting is bad. Inspect the actual pages and resolve the question or defect before a justified new check; do not repeat unchanged requests until one passes.

Overall readiness remains blocked until the candidate explicitly approves the exact pages and facts. The working draft and working image stages report `PROVISIONAL`; check the underlying receipt and `can_advance`, not the display status alone. An underlying `NEEDS_HUMAN_REVIEW` remains a hold. If Jev or rendering is unavailable, report the specific missing dependency. Do not silently replace the visual gate with a text score or manufacture a passing receipt.

## Protect evidence and approvals

Keep question-specific factual gaps visible after a draft exists. Let the candidate supply evidence, replace the pattern, or omit it. Re-run the affected transition after a content change and bind the new receipt to that exact version.

The current workflow never submits or sends. After all required quality evidence exists, show the complete application and request separate approval for that specific destination and content. No score substitutes for the candidate's review. Do not write credential values or full private transcripts into receipts.
