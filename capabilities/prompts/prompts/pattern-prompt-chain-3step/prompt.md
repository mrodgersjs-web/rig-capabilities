---
id: pattern-prompt-chain-3step
version: 1
status: draft
updated: 2026-09-24
task: Chain three single-purpose prompts: summarize, extract insights, create action items
category: prompt-craft
domain: prompt-craft
model_target: unspecified
score: null
license: pattern-with-attribution
source: https://github.com/tysoncung/awesome-prompt-engineering
triggers: prompt chaining break it into steps summarize then insights action items from chain of prompts one shot failing
compose: 
provenance: https://github.com/tysoncung/awesome-prompt-engineering | paraphrased pattern with attribution; canonical 3-line example quoted
content_sha256: 76c9a24cdc783dbd60eebb940e6ce34ead0e48326fa4c4ca98a56b7123161717
---

Break a heavy one-shot job into a chain of three simpler prompts, each consuming the previous output:

1. "Summarize this article: <ARTICLE>"
2. "Extract key insights from: <SUMMARY>"
3. "Create action items based on: <INSIGHTS>"

Use a chain when the one-shot version leaks format errors, drops constraints, or buries the ask. Keep each step single-purpose and state the output shape of each step explicitly. The chain is also the audit trail: each step can be checked on its own.

Pattern paraphrased from the prompt-chaining section of tysoncung/awesome-prompt-engineering. Not copied text beyond the canonical three-line example.
