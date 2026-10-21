---
name: "ns-ai-career-and-content"
description: "Keep value rooted in business judgment as AI absorbs execution, and run content as a governed authority engine. Nick Saraev method. Use for: what should I learn; is this model release worth testing; content pipeline; repurpose this video; should I post or do outreach."
tier: main
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Keep value rooted in business judgment as AI absorbs execution, and run content as a governed authority engine."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: nick-saraev-os
  stage_doctrine: references/doctrine.md
---

# ns-ai-career-and-content

Keep value rooted in business judgment as AI absorbs execution, and run content as a governed authority engine.

**Use when:** what should I learn; is this model release worth testing; content pipeline; repurpose this video; should I post or do outreach.

## Laws
- Content builds a long-term brand; early cash comes from outreach. CLAIM(FdJuDZ6OVOY@1m) CLAIM(yR9enwhUkp8@2m)
- The edge has moved from knowing tools to business judgment, because agents can research tools now. CLAIM(S3kdxriOESk@13m) CLAIM(npCSNPN3F1o@18m)
- If you cannot name the business formula a system moves (profit, growth or value), do not build it. CLAIM(Ozp3k4qzmHo@13m)
- Skip minor model bumps; test new classes of capability. CLAIM(x55Fj_syFcI@0m) CLAIM(x55Fj_syFcI@3m)
- Learn a task by hand before handing it to AI, or the skill fades. CLAIM(iqfA2vfbKUY@3m)
- Match the message to the buyer's awareness stage. CLAIM(nmal1JTOrWI@0m)
- A human reviews before anything is published. CLAIM(jBF48jNWPJE@18m) CLAIM(XlYQa0GgfaU@32m)

## Procedure: Governed content pipeline
1. Pull source text, using existing subtitles before paying for transcription. CLAIM(G3LuGcAeiOU@26m) CLAIM(DNfp1XKC15k@9m)
2. Run a role prompt that must return JSON. CLAIM(G3LuGcAeiOU@9m) CLAIM(DNfp1XKC15k@20m)
3. Parse it safely (escaped newlines). CLAIM(jp_GEYNC7jo@19m) CLAIM(DNfp1XKC15k@51m)
4. Map to each platform behind a human review gate. CLAIM(jp_GEYNC7jo@41m) CLAIM(G3LuGcAeiOU@30m)
5. Write a posted-on timestamp back so nothing posts twice. CLAIM(DNfp1XKC15k@82m)

## Sub-skills (load one at a time)
- `ns-content-engine`: Source to draft to review gate to publish to write-back, tagged by awareness stage.
- `ns-career-positioning`: Triage model releases, apply the business-formula test, and check skills are learned by hand before automating them.

## Done-test (fails if any is true)
- Anything published without a logged human review.
- A duplicate post.
- A piece cannot be traced to an awareness stage and a business formula.
- A model release was tested without first logging it as a minor bump or a new class.

## Does not fit RIG
- YouTube thumbnail recipes as laws (single-source production craft).
- Build craft (Tailwind, curl import) that belongs in ns-automation-builds.
- Any auto-publish path: Mike's lanes keep their own Jev/Clef gates and approval rules.

## Deeper doctrine
`references/doctrine.md` holds the full stage doctrine: core laws marked consensus or single-source, procedures, decision rules, failure modes and changed views, all cited. Malformed tags from distillation were removed by the tag validator.

## Where this sits
Layer 2 under `nick-saraev-os`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
