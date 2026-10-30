---
name: lv-draft
description: >-
  Body writing and formats for LinkedIn: post architecture, body craft, the format catalog, CTA and
  threads, with the RIG write engine and writer agents called as tools and Eden as the copy
  generator fed by a real story, transcript or receipt. USE WHEN a brief must become a draft, a body
  needs rewriting, a format or CTA must be chosen, or a long idea becomes a series. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage (format
  choice, whether the body pays the hook, CTA fit, draft quality screen, thread structure call) goes to rig-s1gate (Jev)
  BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of
  linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, drafting, formats, cta, threads]
outcome: "content-publishing: every draft is written from real source material in the right format, pays its hook's promise, and hands a gated brief to Eden with nothing left to invent"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-draft
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  absorbed: "9"
---

# lv-draft: body writing and formats

This stage owns everything after the hook is chosen and before a draft is gated and scheduled: the
intake, the source material, the body, the format, the CTA, and threads. Nine merge sources were
reconciled here. The write engine and the writer agents are tools to call, not content to copy.

## JEV-first mandate (read first)

The typed judgments this stage forces: which format a draft should take, whether the body actually
pays the hook's promise, whether a CTA fits the reader's intent stage, whether a draft is good enough
to leave this stage, and whether a thread structure earns each next click. Each goes to Jev BEFORE
any frontier LLM call.

- Command: `rig-s1gate check post.linkedin --file <draft> --subject "draft <id> sha256:<hash>" --json`. Use rubric `post.viral` for viral-shaped posts, `post.eden` for Eden-generated copy under review.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring, or rubric missing means DEFERRED. Report it, keep the draft a draft, and do not substitute a frontier model's opinion.
- An advisory PASS is not permission to publish. Eden is the publisher of record and Gate-D governs every live item.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use when: a plan slot or brief must become a draft, a body reads like a lecture or a chopped-up blog
post, a format must be chosen for real material, a CTA is weak or mis-staged, an essay becomes a
series, or a flopped post needs a rewritten body.

Do not use for: hooks (lv-hooks), visuals (lv-visuals), the final gate (lv-gate), scheduling or
publishing (lv-launch), comments and DMs (lv-engage, lv-outreach), profile sections (lv-profile), or
anything about a minor (Lane C: stop and hand back to Mike).

## Procedure

1. **Intake before anything else.** Fill four fields, none vague: belief_from (the specific belief the ideal reader holds now), belief_to (the falsifiable belief after reading), ideal_reader (title, context, moment in their day), and platform_moment (how they are consuming the feed). Missing or vague input is a stop, not a prompt to improvise.
2. **Classify the reader.** One sentence: "This post is for <named person> struggling with <specific thing>." A category instead of a describable person is a stop.
3. **Source material rule (Eden).** The brief comes from a real story, a content interview or voice notes, a transcript, a receipt, or calendar mining of the week's meetings. Never a bare topic, and never a blank-to-draft AI run. Agents assemble the brief and the receipts; Eden generates the copy and the brand assets; Mike edits for voice. That satisfies both the no-blank-draft rule and the Eden-as-generator rule.
4. **Proof table before prose.** Find two to three citable, specific evidence items ("a study showed" is not proof). Name the strongest counter-argument as the deliberate valley. Flag any unsourced factual claim: unsourced means blocked.
5. **Choose the format from the catalog** (`references/formats-and-cta.md`) that fits the material and the funnel stage. One idea per post. If the material is long-form and multi-post, structure it as a series instead of stretching one post.
6. **Build the arc** (`references/post-architecture.md`): hook, rupture (the valley), reframe, proof rising weakest to strongest, CTA. Do not skip the valley; a post without one goes from hook to answer and reads as a lecture.
7. **Write the body** by `references/body-craft.md`: one idea per post, one point per line, real whitespace, written the way Mike talks, read aloud before it leaves.
8. **Design the CTA and the first comment now, not after publishing.** One primary ask matched to the reader's intent stage and friction budget; the first comment engineers the one conversation the post wants. No external link in the body and no link-drop workaround in the comment either.
9. **Mechanical filters:** no link in body, 2-3 hashtags maximum, no engagement bait, no em dashes, no CTA unless this is the week's one ask-bearing post, one post per day maximum per account.
10. **Generate candidates, then pick.** For consequential posts, draft three complete candidates with different hook styles and proof orderings, score each honestly (credibility, engagement probability, proof density, audience fit), and state which won and why. A single post with no comparison is an unverifiable claim of best.
11. **Gate through Jev** (command above), then run the hook validator prompts held by lv-hooks (`~/.hermes/archived/linkedin-studio/prompts/hook-validation-prompts.md`). Fix or kill anything that blocks.
12. **Hand to Eden as a brief, never as finished brand copy.** The draft goes to critique first; a draft failing the bar returns here with the named failing criteria. Nothing from this stage is published.

## Quality bar

- Four intake fields filled and falsifiable; classification sentence names one person.
- Every factual claim carries a named source; the proof sequence rises weakest to strongest.
- The body pays exactly what the hook promises; the brand find-and-replace test fails (at least one detail only Mike could write).
- At least one falsifiable claim; no zero-substance post that sounds smart and says nothing.
- CTA is one ask at the right intent stage with friction counted; the first comment names the conversation it engineers.
- Filters pass: no link, 2-3 hashtags, no engagement bait, no em dashes, no banned words.
- Jev verdict recorded with a decision id or explicitly DEFERRED.

## Lanes

- **Lane A (personal brand, Eden, Ted Lasso register):** warm register, pop-culture material allowed; Birch is Tuesday only, The Coach only from behind or in silhouette. Themed days run by the weekly rhythm and stay while they beat baseline.
- **Lane B (RIG B2B):** evidence-led, named receipts, no mascots, no pop-culture frame, operator register (we install, build, operate) not advisor register. The moonshot slot of the week is where RIG's governed-build receipts and original data belong.
- **Ideawake client lane:** drafts only, on Coby's account; assert the signed-in handle before any action, never borrow Mike's voice, nothing fires without Mike's explicit client approval.
- **Job-search lane:** every claim must survive the resume check; profile edits and outward activity stay behind Mike's approval.

## Tools and runners

| name | kind | path | when to call |
|---|---|---|---|
| rig-write-linkedin | engine (tool) | `~/Developer/rig-capabilities/capabilities/skills/rig-write-linkedin/SKILL.md` | Lane B drafting: assemble the write packet (voice, wounds, corpus, persona) and gate-score the artifact |
| rig-communications-core references | engine (tool) | `~/Developer/rig-capabilities/capabilities/skills/rig-communications-core/references/SKILL.md` | when the draft needs the full comms protocol or scoring formulas |
| vertical-domain-li-agents | agents (tool) | `~/.hermes/skills/vertical-domain-li-agents/SKILL.md` | when a draft or conference comment needs vertical expertise (dental, law, CPA, PE) |
| agency-linkedin-content-creator | agent (tool) | `~/.claude/agents/agency-linkedin-content-creator.md` | when an Agency-spec content creator should run the drafting work |
| rc-linkedin-writer | agent (tool) | `~/.omp/agent/agents/rc-linkedin-writer.md` | when a feed-rhythm writer should draft posts or series copy |
| linkedin-guru | agent (tool) | `~/Developer/rig-gtm-studio-v2/agents/linkedin-guru.md` | when a post brief should be turned into finished copy by the writer/craft/vocabulary trio |
| dream-weaver | agent (tool) | `~/Developer/rig-gtm-studio-v2/agents/dream-weaver.md` | when a draft needs a deliberated treatment before the scoring loop |
| step-3-draft | agent (tool) | `~/.aside/u/0/skill-library/linkedin-growth-os/agents/step-3-draft.md` | when the growth-os drafting step should run with its own gates |
| draft-body | agent (tool) | `~/.aside/u/0/skill-library/linkedin-growth-os/agents/sub/draft-body.md` | when the body sub-agent should write against a plan slot and its source claims |
| gtm-draft-only | Eden skill (tool) | `eden://settings/skills/gtm-draft-only` | prospecting lane: stage connection and comment drafts only; sending needs exact Gate-D approval |
| rig-comms-drafting-loop | runner | `~/Developer/rig-capabilities/capabilities/loops/rig-comms-drafting-loop.md` | routines load it at run time; call this stage at GENERATE, respect the max-3 REVISE latch, and let the verifier certify at VERIFY |

## Sub-skills

| file | covers |
|---|---|
| `references/post-architecture.md` | the arc with its valley, the named body structures, line mechanics, retention tricks |
| `references/body-craft.md` | dwell and saves, whitespace, readability floor, filler cutting, voice pass and banned words |
| `references/formats-and-cta.md` | the format catalog, length bands, week shape, CTA design, threads and series |
| `references/draft-workflow.md` | intake fields, source-material rules, proof tables, candidates, gates, the Eden brief |
| `references/creator-playbook.md` | cross-creator consensus, conflicts and gaps for this stage (11 doctrines) |

## Hard rules carried forward

- Never draft from a bare topic. The brief carries a real story, transcript, receipt or meeting moment. [clark:content-system, li-hooks]
- Eden generates the copy and the brand assets; agents brief, gate and measure, never hand-author brand copy. [li-hooks]
- Every factual claim carries a named source. Unsourced claims are blocked, not softened. [/rig-ae-linkedin-run, hook-selection]
- No external link in the body, and the first-comment link workaround is penalised too: put a saveable asset in the reference comment instead. [body-craft]
- 2-3 hashtags maximum, no engagement bait, no em dashes, one post per day per account. [li-hooks, hook-lab]
- One idea per post, one point per line; a wall of text is a defect. [body-craft]
- Give four, take one: no CTA in every post, and no CTA at all unless this is the week's one ask-bearing post. [post-architecture, lg-draft]
- Never publish a creator-reported number as ours, and never invent a metric to fill a hook. [lg-draft]
- A case study without proof artifacts is a claim, not a case study. [post-architecture]
- AI may research, edit, stress-test and repurpose real material, but it may not take a post from nothing to a draft, and AI-written comments are forbidden entirely. [clark:content-system]
- One approver. Mike is the final filter on every post; committees make corporate mush. [clark:content-system]
- Never publish, schedule or send from this stage. Eden is the publisher of record and Gate-D governs live items. [viral-core]

## Lessons from measured outcomes (added 2026-10-01)

These four rules come from this account's own analytics read on 2026-10-01, not from a corpus.
Provenance tag `[measured:eden-analytics-2026-10-01]` marks an observation on Mike's accounts;
`[ext:...]` marks an outside finding. Do not blur the two.

- **No closing device repeats within 14 days.** The same thesis close ("the floor drops... what is
  left on top is judgment") shipped in three posts in two days, and a "PS: What did you...?" close
  sat on nearly every post in the queue. Recognisable repetition is the AI tell this stage exists to
  prevent. Check the last 14 days of shipped posts before drafting a close. [measured:eden-analytics-2026-10-01]
- **Put the receipt in the body, not in a footnote.** Bare thesis lines scored `unverified_claim`
  0.70-0.81 and did not move across 5 rewrites and 4 line-ablations; the same copy with a named
  outlet and a date inline dropped to 0.34 and passed. Rewriting does not move that flag, adding the
  source does. Every draft carries one named number and one named person or outlet in the body.
  [measured:eden-analytics-2026-10-01]
- **A poll is a format, and it is the only vehicle that has broken out on this account.** The one
  post to pass 10K in three weeks closed on a four-option poll and drew 58 comments against 44-116
  impressions for every non-poll post in the same window. Treat a poll as a first-class option in
  the format catalog, not an afterthought. [measured:eden-analytics-2026-10-01]
- **Machine output needs a fail-closed lint gate before it is a draft.** A voice-law audit found 20
  posts carrying 42 em dashes and 22 posts burying the hook past the ~210-character fold, and every
  one of them was Lane B, Lane C or unclassified machine output, while 26 hand-written Lane A posts
  returned zero of both. The doctrine was never the problem; the missing executable check on the
  producer was. [measured:eden-analytics-2026-10-01]
- Format evidence from outside our own corpus, recorded as a conflict rather than a silent change:
  this stage's house default is 6-9 slides, while getcreator's 8,400-post carousel benchmark puts
  the engagement sweet spot at **9-12 slides** (5.4% engagement, 68-76% swipe-through) and Buffer's
  45-52M post sample puts carousels at 21.77% median engagement, +278% vs video. The house default
  has not been tested against this account's own baseline, so the two disagree until measured.
  [ext:getcreator.io/stats/linkedin-carousel-benchmarks, ext:buffer.com/resources/state-of-social-media-engagement-2026]

- `references/poll-vehicle.md` — polls as a vehicle: construction, cadence conflict, and the private
  lead read-out. Distilled from three how-to transcripts 2026-10-01, every law cited. Load when the
  format decision is a poll or when a poll has closed and needs its results post.

## Done-test

`check_ledger.py` verifies the JEV-FIRST MANDATE in the frontmatter and the mandate section opening
the body, three sub-skills of 400 bytes or more plus a ledger with a row for every stage-map asset of
this stage, every backticked path resolving on disk, and no twelve-word run shared with a third-party
merge source. GREEN on exit 0, RED on exit 2.
