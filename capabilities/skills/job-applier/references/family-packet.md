# Ordered family packet

Reload the current Job Applier meta-skill and each exact leaf at the start of each new role. Cached chat instructions, a historical working packet, an installed filename, and a saved app stage do not prove execution. Existing routine enabled/disabled state stays unchanged. Installation does not refresh an already-running chat.

Use one packet directory per role/revision. The validator takes its `packet.json`; all artifact paths are relative to that directory, remain inside it, and carry actual SHA-256 hashes. Never fabricate a receipt to satisfy a gate. Store provider responses and human responses as evidence with appropriate local privacy controls. Tests use synthetic fixtures only.

## Packet shape

`target` has exact `company`, `role`, `id`, `url`. `artifacts` maps stable names to `{path, sha256}`. Required common names are `jd`, `inventory`, `persona`, `persona_review`; working adds `achievement_bank`, `alignment`, `red_docx`, `clean_docx`, `changes`; final adds `confirmations`, `images`, `quality`; submitted adds `approval`, `submission_receipt`. Additional named captured career/public-source artifacts are allowed. `public_source_ids` explicitly lists captured public research sources; persona citations may use only these or `jd`.

`stage` is `persona`, `working`, `final`, or `submitted`. These require respectively the first 2, 5, 7, or 8 ordered leaves. Future human confirmation/submission evidence is not required at the persona or working checkpoint. `tailoring_status` is `complete` for an actually tailored working draft; source-only recovery uses `source_only_recovery: true`, `tailoring_status: incomplete`, remains working, and never advances to final. Structural validity of a held recovery is not tailored completion.

Every `step_log` item contains `step`, `leaf` (exact `steps/<slug>/SKILL.md`), `artifact_hashes` and `execution_receipt: {path,sha256}`. Execution receipt JSON contains the matching `step`, actual `command_or_tool`, `started_at`, `completed_at`, matching `artifact_hashes`, and `response_artifact: {path,sha256}`. The retained structured response binds `step` and `artifact_hashes` and references the actual operator/tool output as appropriate. A self-authored wrapper preserves evidence bindings; it cannot authenticate that the underlying action happened. Keep original actual tool responses, not just summaries.

Every step binds JD and inventory; from the persona step onward it also binds persona. Bind its output names from `OUTPUTS` in [the validator](../scripts/validate_packet.py). A later persona edit invalidates the bank, alignment, review and execution bindings.

## Portfolio audit within evidence alignment

Every role records a `portfolio_audit` artifact under the existing evidence-alignment step. Follow [the GitHub portfolio evidence contract](github-portfolio-evidence.md). Bind the audit to target, JD hash, inventory timestamp, accessible account/repository coverage and the exact inspected commit/file sources. Record partial access honestly. Keep personal ownership/outcomes and test execution separate from source inspection. Include this artifact's hash in the alignment execution receipt. The existing standalone validator does not yet enforce this additional portfolio field; an agent must inspect the actual audit evidence and report that limitation rather than implying executable enforcement.

## Research schemas

`inventory.json` contains `target`, `jd_sha256`, and nonempty `requirements`. Each requirement has unique `id`, `kind` (`responsibility`, `minimum`, `preferred`, `constraint`) and an exact `jd_quote`. Split compound duties/qualifications. `coverage_review` contains ordered `requirement_ids` and a hashed `receipt` whose JSON binds the same IDs, `jd_sha256`, and actual coverage result `status: PASS`. A structural validator cannot infer omitted duties from prose; real full-JD coverage review remains required.

`persona.json` contains `kind: role_research_not_candidate_facts`, exact `target`, `jd_sha256`, and every ordered `requirement_id` in `requirement_ids`. Each section below is a nonempty array of `{text,basis,source_ids}`. Basis is `jd`, `public_source`, or `inference`; label inferred expectations in the text and cite their source basis. Never state private hiring-manager beliefs.

- `mandate`
- `decision_rights`
- `operating_environment`
- `industry_economics`
- `outcomes_90_days`
- `outcomes_year_one`
- `capability_depth`
- `leadership_behaviors`
- `ideal_career_proof_metrics`
- `hard_criteria`
- `tradeoffs_failure_modes`
- `hiring_questions`
- `adjacent_vs_direct_fit`

`persona_review.json` binds `status`, `decision_id`, `jd_sha256`, `persona_sha256`, `inventory_sha256`, and hashed `provider_response`. The saved typed provider response must match those fields. It must come from the actual configured Jev review route. Missing/unavailable/blocked semantic review holds advancement; arbitrary generic content cannot be approved merely because all field names exist.

`achievement_bank.json` binds target, JD and persona hashes and has `examples`. Each has unique `id`, `requirement_ids`, `result`, `personal_action`, `strategy`, and `status: hypothetical_not_candidate_fact`. All requirements must be covered, including qualifications and constraints. An illustrative ideal proof of a missing credential is a research example, not a claim that Mike has it. A shared example needs `shared_rationale`; duplicate boilerplate is rejected. Use explicit gap disposition when no truthful candidate match exists.

`alignment.json` binds target, JD, persona and `achievement_bank_sha256`. Its `claims` have unique `id`, `example_id`, matching `requirement_ids`, `status` (`confirmed`, `adjacent`, `unconfirmed`), actual `source_ids`, and known attribution. Confirmed claims require employer, role, period, personal_contribution and result. `origin: hypothetical` requires hashed factual `confirmation` evidence before confirmed status. Unconfirmed/adjacent rows can remain honest gaps in the useful working review copy.

## Word and review schemas

`red_docx` and `clean_docx` must be actual Word ZIP packages. Their existence/type is only a basic structural check. Follow [original Word fidelity](word-format-fidelity.md). Inspect actual `FF0000` run color in existing appropriate slots; bind explicit UNCONFIRMED status and tentative placement through Word comments or a separate linked worksheet to the exact draft hash/claim ID. Never insert process notes or labels as extra body paragraphs. Render original/output with the same renderer/settings and inspect every page; style hashes alone cannot pass. Preserve the selected source template. The clean version excludes unsupported examples and review labels. `changes` retains exact before/after wording and requirement/source pointers.

`confirmations.json` has `decisions` keyed by claim ID, each with `action` (`confirm`, `replace`, `omit`) and hashed `human_response`. Retaining an initially unconfirmed/adjacent claim requires actual employer, role, period, personal_contribution and result. `page_approval` binds `images_sha256`, `docx_sha256` and a hashed `human_response` for those exact pages. An affirmative boolean alone is not evidence.

`images.json` has `docx_sha256` and nonempty `pages` of hashed rendered images. `quality.json` has an actual `decision_id`, `status`, `criteria_ids` exactly 1–15, hashes for JD, persona, clean_docx, images, alignment and confirmations, and a hashed `jev_receipt`. Its typed contents must match these bindings. Bind the final quality review to current factual and page-approval evidence; obtain the review after these are current. Receipt authenticity and semantic truth remain outside the local validator.

`approval.json` and `submission_receipt.json` bind target, `docx_sha256` and hashed real `evidence`. The submission additionally requires `provider_receipt_id`. Stage `submitted` is allowed only after the actual scoped application and its real receipt. A pre-submission hold is reported outside the submitted checkpoint.

## Existing app compatibility

The app's `executive-resume` route keeps its native `ideal` envelope, priorities and source IDs. Its persona version is `job-applier.ideal-persona.v1`, uses the same 13 sections, and binds current source identity/hash. App source IDs such as `s###` belong to the app's captured source rows; the standalone family packet uses named local artifacts. Translate only verified source references when exporting a packet. Do not assume either schema is accepted by the other API verbatim.

This family and structural validator do not by themselves wire eight new executable app stages, fetch new research, register eight slash commands, or authenticate saved responses. Report the actual integration evidence separately. Load the nested leaves through the meta-skill's relative paths. Source-only/legacy app records cannot stand in for the mandatory full persona.

## Daily workflow evidence

For scheduled use, retain the additional durable workflow/Aside correlation and failure/replay evidence required by [the daily Temporal execution contract](temporal-daily-workflow.md). The standalone packet validator remains a structural artifact check; it does not test Temporal history replay, authenticated signals, actual ATS idempotency or a live daily schedule.
