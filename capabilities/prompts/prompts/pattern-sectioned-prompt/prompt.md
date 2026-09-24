---
id: pattern-sectioned-prompt
version: 1
status: draft
updated: 2026-09-24
task: Structure any task prompt into delimited sections: background, instructions, tool guidance, output description
category: prompt-craft
domain: prompt-craft
model_target: unspecified
score: null
license: pattern-with-attribution
source: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
triggers: section the prompt structure the prompt xml tagged prompt background information instructions output description prompt layout
compose: 
provenance: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | paraphrased pattern with attribution, not copied text
content_sha256: cedca8abff06eb060e34e3a15f16cb24f725630c3d458b90f7ce48dae258e287
---

Structure a task prompt as explicitly delimited sections, using XML tags or Markdown headers, in this order:

<background_information>
Only the facts, state, and prior decisions needed for THIS task. Cut anything the model can retrieve on demand.
</background_information>

<instructions>
The job, stated as verbs and constraints. One instruction per line. Name what NOT to do as explicitly as what to do.
</instructions>

## Tool guidance
When to use each tool, and which one to prefer when two overlap.

## Output description
The exact shape of the answer: fields, order, length limit, and what to do when a fact is unknown (say "unknown", never guess).

Rule: do not hardcode brittle if-else behavior into prose. Put decisions in code or in the tool; keep the prompt about the job. The middle of the spectrum is the target: specific without being fragile, general without falsely assuming shared context.

Pattern paraphrased from Anthropic, "Effective context engineering for AI agents" (2025-09-29). Not copied text.
