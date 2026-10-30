# Jev/OpenJev/LAYA promotion dataset contract

This is a schema for collecting **real** coding-agent routing and completion
cases. It is not a trained model, a labelled dataset, or a production gate.

One record per request/claim in `cases.jsonl` (do not commit private case
bodies). Required fields:

```json
{
  "case_id": "opaque-id",
  "surface": "mission_route | agent_choice | skill_choice | prompt_choice | tool_choice | completion_claim | visual_claim",
  "input_ref": "Memory OS reference, not raw private text",
  "input_sha256": "sha256 of exact input bytes",
  "candidate_ids": ["version-pinned permitted candidate"],
  "gold_label": "one candidate, no_match, supported, unsupported, or review",
  "labeler": "independent reviewer identity",
  "label_provenance": "artifact or behavioral observation reference",
  "project_group": "split whole projects/tasks to prevent leakage",
  "sensitivity": "public | internal | restricted",
  "modality": "text | image | text_image",
  "image_ref": null
}
```

The collector must preserve a separate held-out split, genuine positives and
hard negatives, and current artifact/test receipts. Never fabricate labels
from model answers or simply copy the agent's completion statement. Screen
training eligibility through Memory OS/privacy policy before exporting any
retrieved content. Record each evaluated checkpoint and preprocessing hash.

Compare deterministic-only, served local OpenJev, RIG-trained OpenJev, LAYA
released head, and LAYA fine-tuned head where the input modality is supported.
Do not submit images to installed LAYA: its current API has no image parameter.
For visual claims, use actual screenshots and verify UI behavior separately.

Required report: n by split/class/modality; confusion matrix; false PASS and
false BLOCK; abstention; accuracy; Brier score; ECE; p50/p95 wall time; memory
and cost; malformed/timeout/unavailable behavior; and baseline deltas with
confidence intervals. The quality target and maximum false-PASS rate must be
declared **before** evaluating held-out cases. A replacement requires a
version-pinned rollback path and independent promotion review. Until then
`mission.route` is shadow-only and `mission.completion` is never-auto.
