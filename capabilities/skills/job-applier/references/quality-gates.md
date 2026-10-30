# Quality gates

Run the typed Jev review at each transition: `posting`, `ideal_profile`, `working_draft`, `working_image`, `evidence_review`, `final_content`, `final_image`, and `application_ready`. The adapter is implemented in the Aside Work app's `work/resume_quality.py`. Save the actual request/response receipt and artifact/source hashes. A configured model name is not proof that Jev reviewed this packet.

Working-draft request version `2026-10-28.4` retains the full posting, draft, working text, gaps and questions, plus all historical rows referenced by draft `source_evidence_id` values. It omits unused historical catalog rows without truncating referenced evidence. The receipt still binds the full local source packet. A technically accepted request may still return a semantic BLOCK; keep that hold. Renderer discovery checks PATH then existing supported macOS and current-user Codex-runtime locations, records the exact programs used, and never installs missing dependencies.

The fifteen criteria are:

1. Active posting identity.
2. Complete JD and duties.
3. Qualification gaps visible.
4. Requirement-to-example coverage.
5. Employer, title, and date attribution.
6. Result, personal contribution, and strategy.
7. Defensible metrics, units, period, and attribution.
8. Specific questions for missing evidence.
9. Executive summary fitted to the role.
10. Concise, natural, honest language.
11. ATS-readable structure and natural keywords.
12. Alignment and whitespace.
13. Font and heading consistency.
14. Pagination without clipping or stranded content.
15. Artifact, source, and review binding, complete process, and human approval.

The typed states are `PASS`, `BLOCK`, `DEFER`, `NEEDS_HUMAN_REVIEW`, and `PROVISIONAL`. Missing credentials, unavailable Jev, malformed output, or a missing receipt never becomes PASS. An uncertain image judgment returns `NEEDS_HUMAN_REVIEW` and cannot advance; it is not proof that the layout is bad. Working image output can remain `PROVISIONAL`, with that hold in its underlying receipt. Keep the step pending and state what needs inspection or repair. Jev may return focused evidence questions; Mike supplies the facts after receiving the working draft. Do not fabricate answers or repeat unchanged requests until a score passes.

For `working_image`, render the actual working DOCX and review its sanitized PNG pages before asking Mike to confirm claims. Bind this manifest to the exact working Markdown hash. Unknown/bracketed patterns belong in the linked worksheet; keep process notes out of the resume body. Explicit UNCONFIRMED status may use Word comments or the exact-hash/claim-bound worksheet.

For `final_image`, render the actual final DOCX into page images and send the sanitized still PNG page pixels through the image-aware adapter. Images must meet the adapter's 280–1568 pixel bounds. A text extraction, filename, generated design description, or DOCX existence check is not a visual review. The current image API is experimental. A stage PASS is advisory evidence, and overall readiness still requires Mike's approval of the exact pages and facts. The working draft and working image stages use `PROVISIONAL` while their underlying receipt decides whether advancement is allowed. Do not claim calibrated visual accuracy or an ATS/hiring guarantee.

Keep personal contact fields and unnecessary private identifiers out of external quality requests. Use the recipient's own provider credentials when distributing the workflow; never package a key. If safe redaction or image processing is unavailable, fail closed rather than sending private content or inventing a visual verdict.

## Template and tailoring acceptance

Criteria 4 and 9 require applied, evidence-backed job-specific content, not just a target-title replacement or a requirement map. Inspect the exact before/after wording for the summary, capabilities emphasis, and relevant experience against each substantive requirement; document supported retention and unresolved gaps. Never turn missing facts into fabricated achievements or numbers.

Criteria 12–15 include fidelity to the selected source Word template. Retain the immutable master path/hash, output hash, comparisons of styles, numbering and section/page properties (including margins), and rendered source/output page inspection. Preserve original formatting and section structure while replacing content in a separate copy; a readable generic DOCX still fails template fidelity. Pagination may change with content, but clipping, lost structure, or silent font/margin changes remain defects.

A source-only fallback is **TAILORING INCOMPLETE**. It cannot pass role-tailoring acceptance or final readiness solely because the file exists, the source facts are valid, a model call succeeded, or the review checkpoint was persisted. Unknown template/tailoring evidence remains a hold. These are acceptance requirements, not a claim that a new executable gate has been implemented or passed.

For criteria 12–15, apply [original Word fidelity](word-format-fidelity.md): paragraph/run properties, tabs, dates, bullets, spacing and section order plus same-renderer comparison of every original/output page. Matching style/numbering/theme/section hashes alone cannot pass. Added resume-body banners, inline editorial holds, requirement checklists and questionnaires are defects; move them to the linked review worksheet. Preserve source history and original font/margin geometry. These checks and actual visual approval remain required even when structural tests pass.
