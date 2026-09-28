---
name: lv-gate
description: >-
  The single pre-publish gate for LinkedIn content: Jev rubrics first, then the executable post gate,
  the harness gates, an independent critic, the anti-slop pass and the Eden voice-law check, ending in
  one verdict with evidence. Use before a draft is shown to Mike as ready, before anything goes to Eden
  for scheduling, and before any publish decision. JEV-FIRST MANDATE, findable at task start: every
  typed judgment in this stage (post gate, comment gate, lane call, voice-law check, doctrine surface
  check) goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when
  the classifier is down. Child of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, gate, quality, jev, anti-slop]
outcome: "content-publishing: nothing leaves this stage without one verdict (PASS / ESCALATE / BLOCK) bound to evidence, and no verdict can authorize a publish on its own"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-gate
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  absorbed: "3"
---

# LV Gate: the single pre-publish gate

## JEV-first mandate (read first)

Typed judgments this stage forces: does a post pass, does a comment pass, which lane a draft belongs
to, does the voice law hold, and does a doctrine surface pass. Each goes to Jev before any frontier LLM
call: `rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json` with
rubric `post.linkedin` (Lane B), `post.viral`, `post.eden`, `comment.linkedin` or `doctrine.surface`.
A pass needs every required noul and confidence above 0.9; exactly 0.90 does not pass.
Fail closed: classifier down, CLI or `jev-mcp` missing, or a rubric absent from the criteria file means
DEFERRED, never a guessed verdict and never a frontier model's substitute. Report DEFERRED and keep the
item a draft. Where no stored rubric fits, the verdict is DEFERRED to Mike.
An advisory PASS is not permission to publish, send, boost or spend. Gate-D and Mike still decide.

## When to use / when not to

Use on every draft before it is called ready, before it reaches Eden, and before any publish or boost
decision; use on comments before they are posted on other people's threads; use when a rewrite loop
needs an authoritative stop. Do not use to write the draft (lv-draft), to make visuals (lv-visuals), to
schedule (lv-launch) or to interpret analytics (lv-measure). The minor lane (Lane C) is never gated
toward publication here because it is never auto-published at all.

## Procedure (one pass, in this order)

1. **Freeze the artifact.** Record the file and its sha256; that hash is the gate subject. The author
   may not grade its own homework: the critic step runs in a different session and, where a choice
   exists, a different model family from the drafter. If they share a session, refuse to score and
   report `blocked`, not a number [lg-critique].
2. **Jev first.** Run the rubric per the mandate. Any claim that "Jev judged X" cites the decision id
   from `~/.rig/s1gate/decisions.db`.
3. **Executable post gate.** Run `li_post_gate.py <draft> --selftest` and require SELFTEST PASS before
   trusting any verdict of it; then run it on the draft (with `--crowding N` for near-identical takes in
   the last day) and rewrite-until-clean on the named ACTION. Exit 0 is pass, 1 blocked, 2 usage error.
   Every finding carries a verb: a gate that only reports a score is a dashboard [li-post-gate].
4. **Harness gates.** Execute the applicable hB-04 capability gates in order. A proof command that
   cannot run is reported SKIPPED, never PASS. A self-test failure means the gate itself is broken: say
   so, do not publish on its verdict, and do not treat a missing gate as a pass [hB-04].
5. **Independent critic.** Load the scorecard, read only the draft, hooks, lane and classifier line (not
   the drafter's rationale), score 8 criteria, list named failing criteria, apply the hard blocks, and
   return ship / rewrite / kill. Max 2 rewrite iterations, then ESCALATE to Mike rather than grinding
   [lg-critique, scorecard].
6. **Data-backed check (when history exists).** Score against the account's own top-decile post history
   rather than generic advice, per `references/scorecard-and-critic.md`.
7. **Voice and slop.** Run the anti-slop loop (lint AI tells, rewrite, cleanse with a rival model, lint
   again), then the Eden-resident `voice-law-checker` audit (banned words, sign-off day rules, cast
   assignment, pop-culture hook position). Both must clear.
8. **Publish gate.** `rig-revenue-publish-gate` runs claim hygiene, disclosure labels, risk register,
   professional review where YMYL, ramp fit and evidence. Its verdict vocabulary is closed:
   REQUEST-APPROVAL or BLOCK. It never approves; the human's typed approval is a separate act
   [rig-revenue-publish-gate].
9. **Emit exactly one verdict**: PASS / ESCALATE / BLOCK, each with evidence (Jev decision id, gate exit
   codes, named failures). DEFERRED replaces the verdict when any step above could not run.
10. **Stop at the boundary.** Even a full PASS is advisory: publishing, scheduling, boosting and spend
    are Gate-D items with Mike's explicit yes for that item.

## Quality bar

- Gate subject recorded: artifact path + sha256
- Jev verdict with decision id, or an explicit DEFERRED
- `li_post_gate.py` selftest passed and its run exit code recorded
- hB-04 gates each recorded PASS / FAIL / SKIPPED (an unrun gate is SKIPPED)
- Critic score with named failing criteria and the hard-block list applied
- Anti-slop and voice-law-checker both cleared (or named as blocking)
- Publish-gate record with its six checklist cells
- One verdict, and every number or claim in the output traceable to a source
- An advisory PASS labeled as advisory; no publish instruction anywhere in the output

## Lanes

- **A (personal brand, Eden):** use rubric `post.eden`; run the voice-law-checker's day rules (Tuesday
  closes with the Birch sign-off; Wednesday to Saturday Coach posts close warm and never with the Birch
  sign-off); cast assignment must match the day.
- **B (RIG B2B):** use rubric `post.linkedin`; no proprietary cast; every figure carries a named
  receipt; the executable gate's buyer-vocabulary and promo-CTA checks apply.
- **Client (Ideawake, Coby's account):** gate drafts only. Nothing fires on Coby's account without
  Mike's explicit client approval, and Mike's personal voice rules never leak into the client lane.
- **Job search:** profile and activity material is shown as exact before/after values; applied only
  after Mike approves.

## Tools and runners

| name | kind | path | when to call |
|---|---|---|---|
| li-post-gate | harness | `~/Developer/rig-capabilities/capabilities/harnesses/linkedin-post-gates/li_post_gate.py` | every post draft: selftest first, then the run with crowding count; rewrite on its named ACTION |
| hB-04-linkedin-post-session | harness | `~/Developer/rig-capabilities/capabilities/harnesses/hB-04-linkedin-post-session.yaml` | session contract for any linkedin-post-session; read before drafting and execute its gates in order |
| harness-hb-04-linkedin-post | skill | `~/.aside/u/0/skills/user/harness-hb-04-linkedin-post/SKILL.md` | when the hB-04 contract is needed as an installed skill entry point |
| rig-revenue-publish-gate | agent | `~/Developer/rig-capabilities/capabilities/agents/rig-revenue-publish-gate.md` | final pre-publish record on one artifact; returns REQUEST-APPROVAL or BLOCK and never self-approves |
| anti-slop | skill | `~/.aside/u/0/skills/user/anti-slop/SKILL.md` | voice cleanup on any AI-assisted draft (lint, rewrite, cleanse, lint) |
| slopmonster | skill | `~/.aside/u/0/skills/user/slopmonster/SKILL.md` | same engine as anti-slop; call only when that name is the one installed on the surface |
| voice-law-checker | tool | `voice-law-checker` (Eden-resident skill, cite by name) | every Lane A draft audit and any pre-schedule review |
| step-4-critique | agent | `~/.aside/u/0/skills/user/linkedin-growth-os/agents/step-4-critique.md` | growth-os pipeline step that runs the critique stage |
| critic-panel | agent | `~/.aside/u/0/skills/user/linkedin-growth-os/agents/sub/critic-panel.md` | multi-voice second opinion; a 2+ point disagreement is escalated, never averaged |
| draft-antislop | agent | `~/.aside/u/0/skills/user/linkedin-growth-os/agents/sub/draft-antislop.md` | the de-slop agent step inside the growth-os tree |
| icp-scorer | agent | `~/.aside/u/0/skills/user/linkedin-growth-os/agents/sub/icp-scorer.md` | buyer-fit screening of a draft before it reaches the critic |

## Sub-skills

| file | covers |
|---|---|
| `references/gate-stack.md` | the ordered gate stack, fail-closed rules, verdict vocabulary |
| `references/scorecard-and-critic.md` | the 8-criterion scorecard, critic discipline, data-backed scoring |
| `references/voice-law-and-slop.md` | anti-slop loop, banned words, day sign-offs, cast map, hook position |
| `references/claim-hygiene-and-hard-blocks.md` | claim/disclosure/risk rules, measured corrections, hard-block list |
| `references/creator-playbook.md` | cross-creator consensus, conflicts and gaps for this stage (11 doctrines) |

## Hard rules carried forward

- The author may not grade its own homework: a critic sharing a session or model family with the
  drafter refuses to score and reports blocked [lg-critique].
- A claim without an evidence class is a failing criterion even if the prose is excellent; never soften
  a claim only Mike can settle, flag it for him [lg-critique].
- Disagreement of more than 2 points between critic and a second opinion is escalated, not averaged;
  max 2 rewrite iterations, then escalate to Mike [lg-critique].
- Score floor to ship is 8/10; any hard block is a fail regardless of score [scorecard].
- Never score above the top-decile match bar when no history supports it; a generous scorer is useless
  [post-scorer].
- If the Jev classifier errors, the rubric is absent, or the CLI is missing: DEFER. Never guess a
  verdict, never invent a JEV model, never publish on a verdict you could not obtain [hB-04].
- An unrun proof gate is SKIPPED, never PASS; a gate whose green cannot go red is theatre [hB-04].
- A broken selftest means the gate is broken: do not trust or publish on its verdict [hB-04].
- An advisory PASS is not permission to send, publish, push, deploy or spend; outward action needs
  Gate-D [hB-04].
- `rig-revenue-publish-gate` never self-approves; its output space is REQUEST-APPROVAL or BLOCK only
  [rig-revenue-publish-gate].
- Every figure carries a source; no ranking guarantees; no invented metrics, clients or quotes
  [rig-revenue-publish-gate, viral-core].
- Positive-only comments on other people's posts, human-written; never AI-written comments
  [viral-core].
- Eden is the publisher of record; Postiz is retired and never routed to [viral-core].
- Engagement bait is refused outright, not softened [scorecard].

## Done-test

`python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-gate`
verifies the frontmatter name and JEV-FIRST MANDATE description, that the body opens with the
JEV-first mandate, that references/ holds at least three sub-skills of 400+ bytes plus a ledger with a
named action for every stage-map row of this stage, that every backticked path resolves on disk, and
that no sub-skill shares a 12-word run with a third-party merge source. GREEN means all of it holds.
