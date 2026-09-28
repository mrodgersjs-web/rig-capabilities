---
name: lv-strategy
description: >-
  Positioning, pillars, lanes and voice for Mike Rodgers' LinkedIn estate: the golden question,
  content-market fit, which game the account plays, pillar design with numeric kill criteria,
  voice fingerprinting, Taki hot-button rules applied to RIG, and the 2026 doctrine every other
  lv-* stage obeys. Use when asked "what should I be known for", "what should I post about",
  "which game are we playing", "design my pillars", "does this topic earn a slot", or "whose voice
  is this". JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage (topic
  admission, pillar retirement, voice drift, hot-button fit, lane assignment) goes to rig-s1gate
  (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down.
  Child of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, positioning, pillars, voice]
outcome: "content-publishing: every lane has one named buyer, a golden question it answers, 3-5 pillars with receipts and kill criteria, and a locked voice profile"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-strategy
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  absorbed: "10"
---

# lv-strategy: positioning, pillars, lanes, voice

## JEV-first mandate (read first)

Every typed judgment this stage forces goes to Jev through rig-s1gate BEFORE any frontier LLM call:
topic admission (does a topic pass content-market fit), pillar retirement, a voice-drift call,
hot-button fit of a proposed hook angle, and which lane a strategy request belongs to.
Command: `rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`.
Stored rubrics: `post.linkedin` (Lane B), `post.viral`, `post.eden`, `comment.linkedin`, `doctrine.surface`.
Strategy artifacts usually have no stored rubric that fits; the verdict is then DEFERRED to Mike.
Fail closed: classifier down, erroring, or rubric missing means DEFERRED, never a pass and never a
local guess. An advisory PASS is not permission to publish, send or spend; Gate-D still applies.
Any claim that "Jev judged X" cites the decision id from `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use when setting or revisiting positioning, choosing the game, designing pillars, deciding whether a
topic earns a calendar slot, extracting or refreshing a voice profile, or applying Taki's hot-button
rules to a RIG topic. Also use when two lanes look alike and the voice boundary must be drawn.

Do not use to plan a week or a calendar (that is lv-plan), write or rank hooks (lv-hooks), draft
copy (lv-draft), or score a finished post (lv-gate). Strategy answers "what are we known for and
who is it for"; it never produces a dated slate.

## Procedure

1. Fix the lane first, exactly as `~/Developer/rig-capabilities/capabilities/skills/linkedin-viral/SKILL.md`
   Step 0 does. One lane, one voice. Never blend.
2. Write the golden question as one sentence: why should one named member of the ICP follow this
   account? It carries a buyer, an outcome, and the receipt that proves Mike can deliver it.
3. Run the content-market fit gate on every candidate topic: the buyer cares, the topic sits next to
   what the lane sells, and the lane holds credibility on it. No receipt, no slot.
4. Choose the game (leads, recruiting, fundraising, awareness) and weight the pillars accordingly.
   Mike's three goals compete for one profile; surface that trade-off and let Mike pick the owner
   before anything is planned.
5. Build the pillar system with references/pillars-and-lanes.md: inventory receipts first, cluster
   against the buyer's jobs, then 3-5 pillars each carrying thesis, formats, cadence share, proof
   source, numeric kill criteria, and the weekly slot map that lv-plan fills.
6. Build or refresh the voice fingerprint per references/voice-fingerprint.md: 5+ samples of real
   writing, quantified rhythm and vocabulary, absence signals, then lock it and map each lane's
   register. Drift-check before anything ships.
7. Draw the Hot Button Map for the topic per references/hot-buttons-taki.md (60 seconds, four
   quadrants); the hook comes from the immediate column and declares the frustration instead of
   asking about it.
8. Hand the 2026 governing rules in references/doctrine-2026.md to every downstream stage. Anything
   that contradicts them is a conflict to name, not a variant to try quietly.

## Quality bar

- Golden question names one buyer and one receipt, not a demographic.
- Every pillar has all six fields and a kill criterion that is numeric.
- Voice fingerprint has rhythm stats, signature vocabulary with frequencies, and absence signals
  backed by the samples; nothing is invented to fill a section.
- Topic list passes content-market fit in writing; anything without a receipt is cut.
- The lane is stated at the top of the artifact and no other lane's voice appears in it.
- Every number is labelled by evidence class or is dropped.

## Lanes

- **Lane A (personal brand, Eden, Ted Lasso register):** pop-culture openings welcome, Birch
  Tuesday-only, The Coach only from behind or in silhouette. Strategy owns the pillars and voice;
  the themed-day rhythm itself belongs to lv-plan.
- **Lane B (RIG B2B):** evidence-led, named receipts, no mascots, no em dashes, no banned words,
  AntiGenericForce target at or above 85 on finished copy. The proprietary cast never appears.
- **Ideawake client lane:** Coby's account and Coby's voice. Never borrow Mike's voice. Nothing
  fires without Mike's explicit client approval.
- **Job-search lane:** positioning serves recruiters; profile changes are shown as exact
  before/after values and applied only after Mike approves.
- **Lane C (athletic, about a minor):** out of scope here. STOP and route to the minor-lane skill.

## Tools and runners

| name | kind | path | when to call |
|---|---|---|---|
| rig-communications-voice | tool | `~/Developer/rig-capabilities/capabilities/skills/rig-communications-voice/SKILL.md` | to score a draft against the locked fingerprint v2 or run the drift detector |
| rig-communications-doctrine | tool | `~/Developer/rig-capabilities/capabilities/skills/rig-communications-doctrine/SKILL.md` | to resolve which doctrine doc governs a writing surface before drafting |
| rig-linkedin-studio-engine-builder | tool | `~/Developer/rig-skills/studios/rig-linkedin-studio-engine-builder/SKILL.md` | only when building a new LinkedIn Studio engine on the A1A3A4 layers |

This stage has no runner rows. Runners live in lv-plan and call this stage for positioning and voice.

## Sub-skills

| file | covers |
|---|---|
| `references/positioning-golden-question.md` | golden question, content-market fit, which game, the strategy document skeleton |
| `references/pillars-and-lanes.md` | pillar procedure, six pillar fields, kill criteria, lane map |
| `references/voice-fingerprint.md` | quantified fingerprint, absence signals, register map, drift check |
| `references/hot-buttons-taki.md` | Taki Hot Button Map for RIG, four-leg anatomy, anti-patterns |
| `references/doctrine-2026.md` | the 2026 rule set every lv-* stage inherits, tactic tiers, lane law |

## Hard rules carried forward

- Eden is the publisher of record; Postiz is retired and must never be instructed or recommended [li-growth, linkedin-viral].
- Nothing outward fires without the lane's explicit approval state; drafts stop at the hand-off [li-growth].
- The three lanes never borrow each other's voice; Lane C is never auto-scheduled and is out of scope here [li-growth].
- Comments on other people's posts are positive-only: validate, add one insight, then optionally link own work as a complement [li-growth, rig-linkedin-taki].
- Never AI-written comments of any kind [li-tactic-corpus, clark-content-system].
- Caps are hard: at most 3 link-bearing comments per sweep, at most one carrying a site link, 14-day author dedupe, at most 12 comments per sweep, follow batches at most 40/day and 90/week [li-growth].
- No tactic is a winner before roughly 10 posts of data; the hook library stays empty rather than estimated [li-growth].
- Corpus numbers are creator reports and never appear in public copy; a number that cannot survive "who measured it and what did they look at" stays in the ledger and out of the post [li-growth, claim-ledger].
- RESTRICT tactics are permanent prohibitions: pods, like or comment rings, third-party auto-commenters, template comments that paraphrase the host [li-tactic-corpus].
- Tier 1 corpus claims (3+ videos) are law; tier 2 stays behind a flag until measured; tier 3 is a pre-registered experiment only [li-tactic-corpus].
- Never invent numbers, quotes, clients, results, posts, creators or links; cite only what a tool returned this run [linkedin-viral, personal-brand-strategist].
- No engagement bait and no keyword-comment CTAs; the platform detects and demotes them [linkedin-operating-doctrine].
- No external links in the post body; a PS-line link is allowed only on a post that may be boosted [linkedin-operating-doctrine, clark-evolution].
- The hook carries a specific claim and comes from the immediate column of the Hot Button Map; state the frustration, never ask it [rig-linkedin-taki].
- One payoff line per post, one invitation (CTA or CTE, never both); remove the invitation and the post must still be useful [rig-linkedin-taki].
- Buyer is the hero; Mike is the guide who names the map [rig-linkedin-taki].
- No em dashes anywhere and none of the banned words: unlock, empower, synergy, leverage, disrupt, hustle, utilize, iterate, optimize [rig-linkedin-taki, personal-brand-strategist].
- Never take a post from nothing to a draft with AI; AI researches, edits, stress-tests and repurposes only [clark-content-system].
- Every voice-profile section must be backed by what the samples show or clearly avoid; never invent a pattern to fill a section [voice-builder].
- A personal-brand strategy never invents a creator or a number, never discards a misfit interest, and keeps the low point as trust rather than spectacle [personal-brand-strategist].
- Defend 1-3 contrarian beliefs and repeat the same core ideas for years; audiences remember less than the author assumes [clark-positioning].
- No receipt, no post [clark-positioning].

## Done-test

`python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-strategy`
is GREEN only when the frontmatter name matches the folder and carries the JEV-FIRST MANDATE, the
body opens with the JEV-first mandate section, references/ holds at least three sub-skills of 400+
bytes plus a ledger.md whose table has an action-bearing row for every stage-map row assigned to
this stage, every backticked disk path resolves, and no sub-skill shares a 12-word run with a
third-party merge source.
