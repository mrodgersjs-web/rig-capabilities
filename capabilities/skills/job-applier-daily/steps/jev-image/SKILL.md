---
name: job-daily-jev-image
description: Review real sanitized Word page pixels with the existing hosted JEV image adapter.
metadata:
  version: 1.4.0
---

# Hosted JEV image

## Inputs
Exact working or final DOCX, corresponding Markdown hash, source-template comparison, sanitized review-copy lineage, complete rendered-page manifest and authorized hosted review context.

## Actions
Follow [the adapter reference](../../references/jev-adapters.md). Render the actual Word document with bundled `tools/render_resume.py`; inspect every PNG locally before marking its redaction review. Call bundled `tools/resume_quality.py working_image` or `final_image` with that manifest. Keep every page and receipt. Compare original/output formatting locally as well as reviewing the hosted sanitized copy.

## Outputs
Original and sanitized artifact hashes, real PDF/PNG render files, complete manifest, renderer program paths, local visual-review evidence and actual hosted per-page defect probabilities.

## Gates
Lossless still PNG pixels only, each dimension 280–1568 pixels, at most 16 MiB per page. All pages must match recorded hashes and redaction review. The image adapter asks whether defects are present: probability at most 0.10 passes, at least 0.90 blocks, and the middle band requires human review. Preserve the fifteen-criterion workflow and source/artifact bindings. Text extraction, file existence, invented images and a model name are insufficient. A working `PROVISIONAL` status does not override its underlying hold.

## Recovery
Missing renderer, unsafe redaction, uncertain judgment, missing pages or changed artifacts holds the stage. Inspect the actual pages; repair a demonstrated defect before rerendering and renewing affected receipts/approvals. No unchanged repeated calls to obtain a favorable score. Final candidate page/fact approval and separate submission approval remain mandatory.

## Required skills and contracts
[Meta-skill](../../SKILL.md), [JEV decision](../jev-decision/SKILL.md), [document quality](../document-quality/SKILL.md) and [format comparison](../../subskills/format-comparison/SKILL.md).
