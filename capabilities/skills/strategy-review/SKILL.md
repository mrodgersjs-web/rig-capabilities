---
name: strategy-review
description: "Pillar skill of business-strategy-os: the anti-average gate on any strategy artifact. Runs the deterministic lint (goal-as-strategy, virtue claims, missing only-statement, no trade-offs, missing sections) and the Jev strategy.output rubric (does the category match how customers shop, is there a disagreement a competitor would reject, do the only-claim, trade-offs, innovation and execution hold), and applies the forced verdict (Proceed / Narrow / Test manually / Park / Kill) so a review ends in a decision, not a compliment. Load whenever a strategy, positioning line, pricing rationale or pitch is graded, and before any outward use."
tags: [rig, doctrine, business-strategy, review, quality-gate]
metadata:
  source: "rules distilled from the Alex M H Smith corpus; the forced verdict follows the MIT-licensed paultaki/playing-to-win pack (see references/PROVENANCE.md)"
  extracted: "2026-09-26"
  parent: business-strategy-os
outcome: "strategy-review: every strategy artifact carries a lint report, a Jev strategy.output decision id, and one of five verdicts (Proceed / Narrow / Test manually / Park / Kill) with the gap that produced it"
activation: "Load whenever a strategy, only-statement, pricing rationale, positioning line or pitch is graded, before any client or public use, and when deciding whether a strategy conversation is finished."
instruction: "Lint first (code), then Jev (advisory verdict), then force one of five verdicts. A compliment is not a verdict. The only-statement must fail a fiercest-competitor reading or be rewritten. Lint and Jev never approve; the owner decides."
applies_when:
  env: "any strategy artifact: a document, a one-liner, a pricing rationale, a positioning statement"
  runtime: "python3 strategy_lint.py; ~/.rig/bin/rig-s1gate check strategy.output; Jev (hosted, advisory until calibrated)"
  deps: "strategy_lint.py; the strategy.output rubric; the corpus for evidence"
  params: "the business and category under review; the artifact file"
  budget: "seconds for lint; a fraction of a cent per Jev check"
  scale: "one artifact per run"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - "Run strategy_lint.py on the artifact; every high finding is a gap, not a style note."
  - "Run rig-s1gate check strategy.output --file <artifact> --subject strategy.output:<business> --json; record the decision id."
  - "If Jev is unavailable, DEFER the Jev half and say so; never guess the verdict locally."
  - "Force a verdict with strategy-forced-verdict: Proceed, Narrow, Test manually, Park, or Kill, naming the gap that produced it."
  - "On any high finding or ESCALATE, route back to the pillar that owns the gap (diagnose, new-value, innovation, document, stories, marketing) and re-lint."
done_when:
  - "grep:capabilities/skills/strategy-review/SKILL.md:## Verdicts"
  - "cmd:python3 capabilities/skills/strategy-review/scripts/strategy_lint.py --selftest"
  - "cmd:python3 capabilities/skills/business-strategy-os/scripts/claims_check.py capabilities/skills/strategy-review/SKILL.md"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/strategy-review/SKILL.md"
great_example: "examples/great/business-ops/great-strategy-document.md"
quality_floor: 0.8
out_of_scope:
  - "writing the strategy (route back to the owning pillar)"
  - "approving on the owner's behalf; Jev is advisory until calibrated"
---

# strategy-review

> **JEV FIRST.** This pillar is a task-start surface in its own right, not only through
> the meta-skill. Send every typed judgment it forces (whether the artifact is a strategy, whether the only-statement holds, and which verdict applies) to `rig-s1gate` BEFORE any
> frontier LLM call; a required noul passes only above 0.9. **When the fast classifier is
> unavailable: DEFER, never guess a verdict locally, and never let an unjudged stage
> advance.**



## What the lint catches (code, deterministic)

`python3 capabilities/skills/strategy-review/scripts/strategy_lint.py FILE [--mode statement|document]`
- **goal-as-strategy**: "grow revenue 20%", "become number one by 2030", "triple revenue" - a result, not a how CLAIM(rWcJOpdrbCY, Ikx1ECodt1M).
- **virtue-claim**: "best-in-class", "world-class", "leading provider", "customer-focused", "excellent service" without an innovation behind it CLAIM(ElaWyEeHS1w, FF46sruCVpY).
- **better-not-different**: "better than", "the best in the market" CLAIM(PpcQFN9euao, dt9wpjlT-zA).
- **no-only-statement**: no "we are the only X who Y, so Z" CLAIM(kIw__JxmbUo).
- **no-tradeoffs**: nothing is stopped, refused or changed CLAIM(y1-5nxulR68).
- **missing sections / execution not split** (document mode): the five sections and delivery-plus-communication CLAIM(y1-5nxulR68).
The linter ships two fixtures: a red boilerplate strategy (11 high findings) and a green corpus case (0 findings); `--selftest` proves the gate is not vacuous.

## What Jev catches (judgment, advisory)

`~/.rig/bin/rig-s1gate check strategy.output --file <artifact> --subject strategy.output:<business> --json`
Questions: category framed the way customers shop; a genuine disagreement a competitor would reject; the only-claim survives a fiercest competitor; trade-offs named; a concrete innovation, not a virtue; externally visible execution; a how, not a goal; specificity. A required noul passes only above 0.9; the rubric is advisory until calibrated and never approves.

## Verdicts

Every review ends in exactly one verdict and the gap behind it:
- **Proceed**: lint clean, Jev PASS or high scores, the only-claim is defensible. Execute the delivery and communication bullets.
- **Narrow**: the argument is sound but the scope is too wide. Cut to one audience, one problem, one channel, then re-lint.
- **Test manually**: the crux is unknown (pricing, the primary problem, whether a competitor would concede). Design a cheap manual test rather than arguing.
- **Park**: sound idea, wrong season or wrong moment (the channel is oversupplied, the market era is wrong). Name the trigger that brings it back.
- **Kill**: the only-claim fails the fiercest-competitor test, or the value is available elsewhere, or it is a goal. Kill it plainly; "nobody ever built a statue of a committee" applies to strategies too CLAIM(TjEwEUWtwbk).

## Traps

- Passing a review with a compliment instead of a verdict.
- Treating a Jev ESCALATE as a pass because lint was clean; the two gates answer different questions.
- Re-linting the same artifact without routing the gap back to the owning pillar.
