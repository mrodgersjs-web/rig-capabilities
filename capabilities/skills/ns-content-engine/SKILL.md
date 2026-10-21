---
name: "ns-content-engine"
description: "Source to draft to review gate to publish to write-back, tagged by awareness stage. Sub-skill of ns-ai-career-and-content (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Source to draft to review gate to publish to write-back, tagged by awareness stage."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-ai-career-and-content
---

# ns-content-engine

Source to draft to review gate to publish to write-back, tagged by awareness stage.

## Steps
1. Pull the source transcript or card.
2. Draft through a JSON-returning prompt.
3. Tag the awareness stage.
4. Human review, then publish and write back the timestamp.

## Laws
- Reuse existing subtitles before paying for transcription. CLAIM(G3LuGcAeiOU@26m)
- Require structured JSON from the model. CLAIM(DNfp1XKC15k@20m)
- Never publish without review. CLAIM(jBF48jNWPJE@18m) CLAIM(XlYQa0GgfaU@32m)

## Done-test (fails if any is true)
- A post has no awareness tag.
- A post has no review record.

## Where this sits
Layer 3 under `ns-ai-career-and-content`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
