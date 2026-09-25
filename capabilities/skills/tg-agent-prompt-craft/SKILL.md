---
name: tg-agent-prompt-craft
description: >
  Sub-skill of tg-agentic-build-workflow: the prompting craft the TubeGuruji
  corpus demonstrates for coding agents — one-feature tasks, named vendors,
  docs-in-prompt integration, consistent-data instructions, component-level edit
  requests, and incremental verification ("expected result at each point").
tags: [rig, doctrine, prompting, agentic-coding, tubeguruji]
metadata:
  source: "corpus — kxM_oEMn3IM (plan mode + named services), 31-Qfr2Pc5Q (plan review), 5VK8rc3GXdc (error paste-back), tJmN2XduBVk (component-level edits, real data not random), sxn2GPQjJgc (step-by-step expected results), -h1O73T0jmo (Arcjet docs prompt integration), WmWJNSxCiZc (persistent memory)"
  extracted: "2026-09-25"
  parent: tg-agentic-build-workflow
outcome: "Agent tasks that land in one or two iterations because each brief names the feature, the vendors, the verification point, and the failure path."
activation: "Load when writing prompts/tasks for a coding agent on a skeleton build, or when agent output keeps missing intent."
instruction: >
  One feature per task; name vendors explicitly; paste the relevant vendor docs or
  a docs prompt into the task; state the expected result at each point so the agent
  can self-verify; on failure, feed the exact error back instead of rephrasing
  hopes.
applies_when:
  env: "any coding-agent session on a web/mobile build"
  runtime: "agent CLI/IDE"
  deps: "none beyond the agent"
  params: "task size = one feature; one named verification point per task"
  budget: "prompting minutes; iterations are the cost to minimize"
  scale: "single agent, single repo"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - Scope one feature per task; sequence tasks along the skeleton stages.
  - Name the vendor and model in the task ("state which model/service to use in the prompt", kxM_oEMn3IM).
  - Paste docs into the task when integrating a service — the corpus integrates Arcjet by giving the agent Arcjet's own docs prompt including the quota to enforce (2/day self-resetting, -h1O73T0jmo).
  - State the expected result at each point: "you have to go step by step and make sure that you are getting expected result at each of the point" (sxn2GPQjJgc).
  - For AI-generated surfaces, instruct consistency: "this is not just a random data it's putting in. It's putting a real data" (tJmN2XduBVk) — real, coherent content across regenerated screens.
  - Request component-level edits, not page regeneration: "make the changes to a specific component instead of regenerating the complete page" (tJmN2XduBVk).
  - On failure, paste the exact runtime error into a follow-up task for the same session (5VK8rc3GXdc).
done_when:
  - "grep:capabilities/skills/tg-agent-prompt-craft/SKILL.md:one feature per task"
  - "grep:capabilities/skills/tg-agent-prompt-craft/SKILL.md:docs prompt"
  - "grep:data/corpora/how-to/manifest.jsonl:sxn2GPQjJgc"
out_of_scope:
  - fleet orchestration, multi-agent message protocols
  - evaluating model quality/benchmarks
  - RIG prompt-intelligence scoring (rig-ai-engineering owns that)
quality_floor: "A task brief without a named verification point is RED — it produces 'the agent said done' claims instead of checkable results."
---

# Agent Prompt Craft (corpus patterns)

## Task shape

One feature per task, sequenced along the skeleton. The brief names:
the feature, the vendors (never "pick something"), the files involved, and the
expected observable result. The corpus' own rule: "whenever you develop something
you have to go step by step and make sure that you are getting expected result at
each of the point" (sxn2GPQjJgc).

## Docs-in-prompt integration

The cleanest corpus example: Arcjet protection is added by pasting Arcjet's own
integration docs prompt into the agent, WITH the product quota appended ("enforce
two uploads per day, self-resetting") so the agent implements security and business
logic in one pass (-h1O73T0jmo). Same shape for any SDK: give the agent the docs
snippet plus your product parameters.

## Consistency instructions for generated surfaces

Agent-generated screens drift into lorem-ipsum mush unless told otherwise. The
corpus instruction: the agent "is not just putting random data in. It's putting
real data" — coherent names, prices, and content across regenerated screens
(tJmN2XduBVk). Add it to every surface-generation brief.

## Edit requests: smallest scope that works

Ask for the component, not the page: changing a heading color or padding is a
component-level edit; regenerating the page risks new drift (tJmN2XduBVk shows
per-component AI editing as the product feature itself).

## Failure handling

Paste the exact error text into a follow-up task in the same session
(5VK8rc3GXdc). Rephrasing the goal ("make it work") instead of feeding the failure
("TypeError: X is not a function at line N") is how agent loops thrash.

## What the corpus models for review discipline

Plans are accepted only after reading ("proposed changes… feel good to me",
O_f55bWzsik) and diffs get an automated review pass (CodeRabbit after each feature,
WmWJNSxCiZc). Adopt both: no unreviewed plan becomes implementation, no merged
feature skips the diff review.
