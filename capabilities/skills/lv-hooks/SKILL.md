---
name: lv-hooks
description: >-
  The one hook system for LinkedIn: levers, families, three-variant drafting, the cold-reader rule,
  selection and ranking through Jev before any model opinion, A/B testing, hook validation, and the
  lane differences. USE WHEN a post needs an opening, a first line is weak, Mike says "write me
  hooks" or "which hook", or a hook set must be ranked or tested. JEV-FIRST MANDATE, findable at
  task start: every typed judgment in this stage (hook ranking and winner choice, hook family
  choice, specificity and receipts gate verdicts, A/B variant priority, hook quality screen) goes to
  rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier
  is down. Child of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, hooks, ranking, ab-testing]
outcome: "content-publishing: every post leaves this stage with one ranked, receipt-backed hook, a rehook, and a written brief Eden can draft against"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-hooks
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  absorbed: "7"
---

# lv-hooks: the one hook system

Four competing hook generators were merged into this one procedure: the corpus taxonomy and gates
from li-hooks, the generation spec from the hook lab, the family-and-scoring spread from the
cross-platform generators, and the variant-pair test design. The formula-hook generator is raw
material only (see the hard rules).

## JEV-first mandate (read first)

The typed judgments this stage forces: which hook wins, which family a post should open in, whether
a hook clears the specificity and receipts gates, which A/B pair to run first, and whether a hook
set is good enough to leave the stage. Each goes to Jev BEFORE any frontier LLM call.

- Command: `rig-s1gate check post.viral --file <hook-set-file> --subject "hook <id> sha256:<hash>" --json`. Use rubric `post.linkedin` for Lane B drafts and `post.viral` for hooks and viral openers.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring, or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess; keep the hooks as drafts and report DEFERRED.
- An advisory PASS is not permission to publish. Gate-D still governs any live post or boost.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use when: a post needs its opening, a first line is weak or generic, hooks must be generated for a
plan slot or for Eden, a hook family must be chosen from the evidence on the desk, variants must be
ranked or paired for a test, or a flopped post is getting a rewritten opening.

Do not use for: the body itself (lv-draft), visuals (lv-visuals), scoring a finished post (lv-gate),
publishing (lv-launch), comments or DMs (lv-engage, lv-outreach), headlines that are profile
sections (lv-profile), or anything about a minor (Lane C: stop and hand back to Mike).

## Procedure

1. **Classification sentence first.** Write: "This post is for <named person> struggling with <specific thing>." No category words. Unclassifiable means stop and fix the brief before touching hooks.
2. **Inventory the evidence on the desk.** List each claim with its source: a receipt, a transcript, a named published figure, or our own measured scoreboard. Take numbers from a fresh read; a published post is an editable source and its figure can be superseded mid-session. No receipt, no number-bearing hook.
3. **Pick the moat before the hook:** one of a real story, proprietary data, or physical proof. The hook must be the strongest honest opening of that material.
4. **Draft three variants** (Clark treats this as non-negotiable [TH63A9m1VNA, 2XeAckxuAKM]). Each variant stacks two or three levers, four at most, from `references/hook-families.md`. Give the three variants different shapes: a number or scene, a narrative, and a contrast or negative. Never three synonyms of one line.
5. **Cold-reader rule.** Write for a stranger who has never heard of Mike. Callbacks and inside references go in the body. The opening answers, fast, what this is about and what the reader gets for continuing.
6. **Invisible levers.** Keep the machinery under a conversational voice. Recognisable formula openings now read as machine output [SL8yfxUVFKE]. A fuller opening that uses the visible lines beats choppy fragments [sDuWUBoHsRI].
7. **Generate the wider lab only when a spread is needed.** The ten-type lab (one variant per named type) is for plan slots where the downstream critic and floor gate need a spread. Ship the count the consumer's gate enforces and say so; never pad with uncited variants.
8. **Rank through Jev before any model opinion.** Run the gate command above on the variant set. A model's aesthetic ranking comes after the classifier, never instead of it.
9. **Run the selection gates in order** (`references/hook-selection.md`): classification, specificity floor, receipts, lane check, clarity and length. A hook that fails any gate is out regardless of family preference.
10. **Tie-break, then pick.** Higher honest specificity, then the ease-of-use modifier if true, then family diversity across the week, then the recorded library scores for the five scored tracks only, then positioning honesty, then trust over virality.
11. **Write the hook brief** (`references/hook-lanes-and-ab.md` template) and hand it to Eden. Eden generates the final copy and brand assets. The brief is the contract, not the copy.
12. **A/B only with a hypothesis.** Pair variants that differ in exactly one named variable, each pair with its hypothesis and the metric that resolves it. Rank pairs by expected information value, not by which line sounds best.
13. **Validate before the draft moves on.** Run the hook validator prompts in the tool table before the post goes to drafting, before any image or video asset is generated, and before any pop-culture reference post. Any BLOCK is logged and the hook is fixed or killed.

## Quality bar

- Three variants minimum, different shapes, each with two or three named levers.
- Every number in a hook traces to a named source, or the hook is re-angled without the number.
- Specificity scored 0-10; floor is 6, target 8.
- One hook line plus one rehook. Three lines on mobile is too much.
- The promise matches what the body can pay. No clickbait the body cannot cash.
- The hook survives a brand find-and-replace unchanged: fail. At least one detail only Mike could write.
- Ranked through Jev with a decision id, or explicitly DEFERRED. Never a guessed verdict.

## Lanes

- **Lane A (personal brand, Eden):** a pop-culture opening is allowed and proven; Mike's best-performing post used one, which is the borrowed-credibility lever in practice. Keep the proprietary cast rules: Birch is Tuesday only, The Coach appears only from behind or in silhouette, and no cast member appears on any other lane.
- **Lane B (RIG B2B):** every number is a named receipt from Mike's work. No mascot, no pop-culture frame. Strongest shapes: results-first with a real number, contrarian with a receipt, an admission about a killed project. Authority-shaped hooks without earned receipts burn trust; run student-shaped families (transformation, confession) when the wins are not in hand.
- **Ideawake client lane:** hooks are drafted only and land on Coby Skonord's account; nothing fires without Mike's explicit client approval, and Mike's voice never travels to it.
- **Job-search lane:** a hook may not claim anything the resume cannot evidence.

## Tools and runners

| name | kind | path | when to call |
|---|---|---|---|
| hook-validation-prompts | prompt library (tool) | `~/.hermes/archived/linkedin-studio/prompts/hook-validation-prompts.md` | before the post moves to drafting, before any visual asset, before any pop-culture reference post; any BLOCK stops the pipeline |
| draft-hooks | sub-agent (tool) | `~/.aside/u/0/skill-library/linkedin-growth-os/agents/sub/draft-hooks.md` | when a plan slot needs the full ten-variant spread with claim refs for the downstream gates |

## Sub-skills

| file | covers |
|---|---|
| `references/hook-families.md` | the lever table, the merged family taxonomy, skeleton shapes, the kill list |
| `references/hook-drafting.md` | three-variant drafting, the cold-reader rule, the ten-type lab, formula-hooke handling |
| `references/hook-selection.md` | the five gates in order, tie-breakers, the receipts rule, Jev ranking, A/B design |
| `references/hook-lanes-and-ab.md` | lane hook rules, the hook brief template, A/B pair design and the validation sequence |
| `references/creator-playbook.md` | cross-creator consensus, conflicts and gaps for this stage (11 doctrines) |

## Hard rules carried forward

- Three variants of every hook, then merge the best parts; never ship one uninspected line. [hook-drafting, Clark TH63A9m1VNA]
- Every number in a hook traces to a named source. No receipt, no number-bearing hook, ever. [hook-selection]
- Never publish a skeleton with a placeholder number or an invented client. [clark:hooks-and-media]
- Formula-style opening lines are raw material only: recognisable formula phrasing reads as AI output. [hook-generator superseded by Clark SL8yfxUVFKE]
- One hook line plus one rehook; if it runs to three lines on mobile, cut it. [hook-selection, hook-lab]
- Never invent a library score. Only five tracks are scored and none is proven on this account yet. [hook-families]
- Lane B carries no mascot and no pop-culture frame; the proprietary cast is Lane A Tuesday only. [draft-hooks, hook-selection]
- Engagement bait ("comment X and I'll DM") is on the kill list; LinkedIn has said it filters it. [hook-families]
- No hashtags in line one, no question-only hook with no stake, no em dashes. [hook-lab]
- Hook ranking is DEFERRED when the classifier is down. Never guess a verdict, never substitute a model's opinion. [hook-selection, clark:hooks-and-media]
- Eden generates the final copy and the brand assets. This stage writes briefs and never hand-authors post copy or visuals. [li-hooks]
- Never publish, schedule, boost or send from this stage. Live posts need Mike's explicit yes per item. [li-hooks, viral-core]

## Lessons from measured outcomes (added 2026-10-01)

Provenance tag `[measured:eden-analytics-2026-10-01]` marks an observation on Mike's accounts;
`[ext:...]` marks an outside finding.

- **Rank the vehicle before the idea. This is the single most important lesson the account has
  produced.** On 2026-09-17 a Ted Lasso post drew 10,000 views / 6,400 reach / 96 likes / 58
  comments / 5 shares. Between 2026-09-25 and 09-30, five posts carrying the *same thesis* ("the
  scarce skill is judgment") drew 44, 81 and 116 impressions. The idea was identical. What differed
  was the vehicle: a named receipt ("I've audited 400+", the FastAPI creator), an arrow listicle
  that reads on mobile, and a four-option poll close. When a post is under consideration, ask which
  vehicle it is in before asking whether the idea is good. [measured:eden-analytics-2026-10-01]
- **The poll family is untested and is the highest-value gap in this stage.** No hook or format rule
  anywhere in this family covers polls, and the only post to clear 10K in three weeks was one. Until
  there are 10 posts of data, generate a poll vehicle as one of the three variants whenever the
  topic is a genuine either/or the audience has an opinion on. [measured:eden-analytics-2026-10-01]
- **Curiosity-gap and contrarian openings outperform personal-story openings**, measured at 6.8% and
  6.2% engagement versus 5.4%, roughly 2.3x the field over a 1,000+ post sample. Contrarian shape:
  "Most [audience] think [belief] is the key to [result]. They're wrong." Single-vendor dataset,
  treat the direction as solid and the exact multiplier as unproven on this account.
  [ext:connectsafely.ai/articles/linkedin-hooks-engagement-guide-2026]
- **Non-round numbers read as documented; round numbers read as invented.** "10,737 reviews" lands
  where "about 10K reviews" does not. This account's own best-written copy (the TransformFit post)
  already does this and it is the clearest voice in the queue.
  [ext:github.com/jakeolschewski/viral-hook-formulas]
- **The hook must fit the ~140-character mobile cutoff and own its own line above the fold.** 22
  shipped posts currently bury it. A hook that is not visible before "see more" is not a hook.
  [ext:postory.io/blog/hook-formulas-social-media]

## Done-test

`check_ledger.py` verifies that this SKILL.md carries the JEV-FIRST MANDATE and opens with the
mandate section, that references/ holds at least three sub-skills of 400 bytes or more plus a
ledger with a row for every stage-map asset of this stage (merge, tool, runner), that every backticked
path resolves on disk, and that no sub-skill shares a twelve-word run with a third-party merge
source. GREEN on exit 0, RED on exit 2.
