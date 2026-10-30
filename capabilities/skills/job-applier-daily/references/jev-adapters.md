# Existing hosted JEV adapters — 1.4.0

Reuse the portable sibling Job Applier core's `tools/resume_quality.py` and `tools/render_resume.py`. Do not invent a generic JEV CLI, chat endpoint or second implementation. The inspected adapter uses `https://api.typesafe.ai/v1/systemone`, model `jev-latest`, `noul` questions, and the recipient's own `TYPESAFE_API_KEY` environment credential. It uses Python's standard library. The distribution builder copies this implementation into the core package; verify its manifest hash before use.

For non-resume workflow checkpoints, the included [step wrapper](../scripts/jev_step.py) reuses that exact pinned transport and the chosen meta-skill's declared entry/exit requirements. It is a new local wrapper, not a provider-supplied CLI. Run it from `skills/job-applier-daily` with `python3 scripts/jev_step.py --context step-context.json --output new-step-receipt.json`. Context requires an actual catalog `meta_id`, exact packet `binding`, captured `evidence`, observed `report`, reviewed `redactions`, and truthful `hosted_authorized`/`redaction_reviewed` flags. It emits the actual request/response pair, local receipt/request IDs labeled as locally minted, and a live-provider flag. Both typed judgments must be at least 0.90; missing or malformed results defer. It never authorizes submission. Preserve this raw file alongside any normalized audit record. The wrapper cannot turn an account flag, self-authored approval or worker summary into authenticated evidence.

No credential is bundled. Obtain it through the destination's approved secret facility without printing it. Hosted review also requires `quality_context.hosted_authorized: true` and `quality_context.redaction_reviewed: true` from actual scoped authorization and redaction inspection. Setting flags does not create authorization. Keep personal contacts, unnecessary identifiers, secrets and private source code out of hosted state. Unavailable redaction or permission is a hold.

## Commands and order

Run these from the installed `skills/job-applier` directory. Values such as `CONTEXT` and `OUTPUT` are absolute paths to actual task files; use a new output filename for every receipt.

```sh
python3 tools/resume_quality.py --help
python3 tools/resume_quality.py posting --context "$CONTEXT" --output "$OUTPUT"
python3 tools/resume_quality.py ideal_profile --context "$CONTEXT" --output "$OUTPUT"
python3 tools/resume_quality.py working_draft --context "$CONTEXT" --output "$OUTPUT"
python3 tools/resume_quality.py working_image --context "$CONTEXT" --manifest "$MANIFEST" --output "$OUTPUT"
python3 tools/resume_quality.py evidence_review --context "$CONTEXT" --output "$OUTPUT"
python3 tools/resume_quality.py final_content --context "$CONTEXT" --output "$OUTPUT"
python3 tools/resume_quality.py final_image --context "$CONTEXT" --manifest "$MANIFEST" --output "$OUTPUT"
python3 tools/resume_quality.py application_ready --context "$CONTEXT" --manifest "$MANIFEST" --receipts "$PRIOR_RECEIPTS" --output "$OUTPUT"
```

These are individual transition templates, not a shell script to run consecutively against one unchanged file. Choose a fresh `OUTPUT` each time. Construct context from the actual posting, full ideal persona, source evidence, draft and authenticated review records as applicable; use the installed core's `references/quality-api.md` schema. `PRIOR_RECEIPTS` is a JSON array of individual receipt objects extracted from prior result files' `receipts` arrays, not an array of whole results. Keep the original result files intact.

CLI exit 0 means `can_advance` is true; exit 2 means hold. The result includes `status`, `can_advance`, `blocking_questions`, `receipts`, `criteria`, and `submission_authorized: false`. Working stages can report outer `PROVISIONAL` even when the underlying receipt is PASS or held. Always inspect both `can_advance` and `receipts[].decision`.

## All fifteen criteria

| ID | Criterion | Stages |
|---|---|---|
| c01 | Active posting identity | posting, ideal_profile, final_content |
| c02 | Complete JD and duties | posting, ideal_profile, final_content |
| c03 | Qualification gaps visible | ideal_profile, working_draft, evidence_review, final_content |
| c04 | Requirement-to-example coverage | working_draft, evidence_review, final_content |
| c05 | Employer, title and date attribution | working_draft, evidence_review, final_content |
| c06 | Result, personal contribution and strategy | working_draft, evidence_review, final_content |
| c07 | Defensible metrics and attribution | working_draft, evidence_review, final_content |
| c08 | Specific missing-evidence questions | working_draft, evidence_review, final_content |
| c09 | Role-fit executive summary | ideal_profile, working_draft, final_content |
| c10 | Concise natural honest language | working_draft, final_content |
| c11 | ATS-readable structure and keywords | working_draft, final_content |
| c12 | Alignment and whitespace | working_image, final_image |
| c13 | Font and hierarchy consistency | working_image, final_image |
| c14 | Pagination without clipping or orphans | working_image, final_image |
| c15 | Artifact/source/process binding and human approval | application_ready |

Content support must be at least 0.90 for every applicable criterion; c01 uses the minimum of its identity/activity/no-closed subchecks. This is policy over advisory model judgments, not calibrated accuracy. Missing, malformed, nonfinite or out-of-range answers fail closed. Do not require fifteen IDs inside every stage receipt: all fifteen are covered across the required stages.

## Real PNG image path

Prepare a sanitized review copy preserving the original Word layout, and record the exact original-to-sanitized artifact lineage. Inspect the original locally too. Render through the existing helper:

```sh
python3 tools/render_resume.py "$SANITIZED_DOCX" \
  --source-sha256 "$MARKDOWN_SHA256" --output "$NEW_RENDER_DIR"
```

The output directory must not already exist. Installed `soffice`, `pdfinfo` and `pdftoppm` are required; discovery never installs them. Output includes the actual PDF, PNG pages and `render-evidence.json`. `MARKDOWN_SHA256` binds the actual working Markdown for `working_image`, or reviewed final Markdown for `final_image`.

Inspect every rendered pixel page for contacts/secrets before marking each manifest page `redaction_reviewed: true`. The adapter checks still lossless PNG data, hashes, each dimension 280–1568 pixels, maximum 16 MiB per page, complete page count and artifact/source bindings. It sends actual base64 PNG assets using header `TypeSafe-Danger-Zone-Images: true`; maximum request size is 30 MiB and the provider request timeout is 35 seconds. The image API is experimental. Never replace pixels with text, filenames, a design description or a simulated page.

Image questions ask for probability that each visible defect is present. Each criterion uses its maximum defect probability across pages: at most 0.10 is PASS, at least 0.90 is BLOCK, otherwise `NEEDS_HUMAN_REVIEW`. Deterministic artifact problems still BLOCK. Human review in the middle band is not proof of a defect and does not permit forcing the receipt to PASS. Retain the hold until resolved with actual evidence.

## Receipts, boundaries and readiness

Preserve unmodified result files and full returned request/response receipts privately. Image receipts omit base64 assets while retaining asset hashes; keep actual PNGs and the complete manifest alongside them. Record source, draft, final, context, manifest, request and receipt hashes, receipt ID, endpoint/model, rubric/request versions and `provider_live`. A simulated `transport` run is test evidence and must not stand in for a live receipt. Hashes prove integrity only, not provider authenticity or human identity.

`application_ready` checks current matching live PASS receipts for all preceding stages plus exact final facts/pages approval. It always returns `submission_authorized: false`; the caller separately enforces approval for the exact employer, role, destination, answers and attachment hashes. Each of the first five resumes gets its own factual/page review. Neither a high JEV probability nor wording approval confirms personal contribution. Proposed accomplishments remain red UNCONFIRMED in the review copy until explicit contribution confirmation and inclusion decisions exist; unsupported content stays out of the clean final file.

Provider errors, missing keys, stale hashes, rendering failures, malformed responses and uncertain image judgments stay named holds. Never rescore unchanged inputs until a favorable draw. Change or clarify the failing evidence, then create a new receipt and renew dependent approvals. Packaging and help checks do not prove hosted access or image execution on the destination.
