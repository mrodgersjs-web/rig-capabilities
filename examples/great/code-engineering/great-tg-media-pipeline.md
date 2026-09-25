---
name: great-tg-media-pipeline
lane: code-engineering
exemplar_of: tg-durable-ai-pipeline
description: >-
  The media-generation reference run: an AI motion-graphic video generator built
  by a coding agent (Factory.ai) on Next.js + Inngest + Gemini (chosen for free
  daily credits) + Remotion on free AWS render + Arcjet quotas - free-tier
  engineering as the visible design constraint.
---

# Media pipeline - what done looks like

## Corpus match

- `ciXiibK7Gds` - "Build Full Stack AI Motion Graphic Video Generator using NextJs, React, Factory.ai, Arcjet, Remotion"
- thumbnail: `data/corpora/how-to/build-craft/tubeguruji-images/ciXiibK7Gds.jpg`

## Spec rows (cited)

| Feature | Evidence |
|---|---|
| Built "without writing any code" via Factory.ai coding agent | title + intro walkthrough |
| Inngest background jobs with a progress bar per step | pipeline chapters |
| Gemini API chosen explicitly for free daily credits (AI Studio key) | stack-selection chapter |
| Remotion renders on the free AWS tier | render chapter |
| Arcjet token-bucket rate limiting as product quota (refill 86400s = 2/day) | quota chapter |
| Live theme color changes; chat-based modification | demo chapters |
| Vercel + Inngest app sync on deploy | deploy chapter |

## Done means

1. Generation runs as a step chain with per-step progress - no in-request media work.
2. Prompt/config edits re-render without re-calling the model where the corpus
   pattern allows (config-first, c9qA-uhysIY two-stage).
3. Quota denies attempt #3 with the upgrade toast; the deny path was exercised.
4. Free tiers carry the whole demo; the only paid line item is named.
5. The build itself was agent-driven with plan-review gates - the agentic
   workflow is part of the deliverable, not a side note.
