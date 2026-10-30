---
name: ss-strategy
description: >-
  Positioning for a Substack publication: who it is for, the one-line promise, 1-3 pillars, the publication name and the About page as the offer. USE WHEN starting or re-positioning a publication, when readers read but do not subscribe, or when Mike asks what the Substack should be about. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of ss-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [substack, ss-growth-os, strategy]
outcome: "content-publishing: the publication leaves this stage with a named reader, a one-line promise, 1-3 pillars and an About page that sells the promise"
done_when:
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-strategy/SKILL.md
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/check_family.py ss-strategy
quality_floor: 0.6
metadata:
  parent: "ss-growth-os"
  laws: "14"
  corpus: "data/corpora/substack (914 transcripts, 27 channels)"
---

# ss-strategy: positioning, promise and pillars

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `ss-growth-os`, which `when-growing-social-accounts` routes every Substack job through. An agent meets it before any stage work.

Typed judgments this stage forces: does a topic fit a pillar, is the promise specific enough, which positioning option wins. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check idea.solid --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `idea.solid` is advisory until calibrated. Substack-specific rubrics `substack.issue` and `substack.note` exist since 2026-09-28 (planted-fixture separation proven, decisions 125944-125948); stages without a Substack rubric use the nearest existing one.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, send, restack, recommend or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use before post 10, before any growth push, and whenever the Growth page shows visitors who do not subscribe. Not for single-post packaging (ss-package) or pricing (ss-convert).

## Procedure

1. **Name the reader** in one sentence (role, company size, the problem they carry). For RIG: an owner or ops lead at a small or mid-size company who has bought AI tools that are not running anything.
2. **Write the promise** in the corpus form `I help <reader> get <outcome> without <pain>` and test it against three unrelated LinkedIn visitors: can they say in 10 seconds what the email gives them?
3. **Pick 1-3 pillars** and brainstorm 10 post ideas per pillar. A pillar that cannot yield 10 ideas is cut (the corpus test).
4. **Rewrite the About page as the offer**: promise, what arrives and how often, who it is for, who it is not for, one proof receipt, the next step. Biography goes last.
5. **Name check**: the publication name should say the category, not the owner. "Mike's Substack" says nothing; propose 2-3 names to Mike (Gate-D: the rename is his call).
6. **Jev**: run the promise and each pillar through `idea.solid`; keep only PASS or record DEFERRED.
7. Hand the positioning card to ss-plan.

## Hands the next stage

`positioning-card.md`: reader, promise, pillars with 10 ideas each, About-page draft, name options. ss-plan builds the calendar from the pillars; ss-publish installs the About page after Mike approves it.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/substack/notes/ss-strategy.md` (local corpus, not republished).

- L1. Do not hunt for a niche topic: document what you are building and let the journey itself be the niche. CLAIM(G3kol7GZ70w, sGV4NbLJezU, mHRJfOWzdJQ) | channels: 2 | status: consensus
- L2. Name your ideal reader and a clear promise for them before you write anything. CLAIM(I98IOJwSR14, C_R4O_y87qM, QmqN1Zl4X8U) | channels: 2 | status: consensus
- L3. Define a niche as a target audience plus a value proposition; a topic word like "fitness" is not a niche. CLAIM(jxzhM0iYQqI) | channels: 1 | status: single-source
- L4. Before committing to a niche or pillar, test it by brainstorming a run of post ideas; if you cannot, it is the wrong niche. CLAIM(4vjWhvZ6T9Q, U0IWoCaBw_o) | channels: 2 | status: consensus
- L5. Pick one to three content pillars and make every post tie back to them so a new reader can tell what the publication is about. CLAIM(4vjWhvZ6T9Q, ABx5xv7O7o4, 2TVwm93Vcow) | channels: 3 | status: consensus
- L6. Treat the About page as your offer and put your strongest case there, because it decides whether a visitor subscribes. CLAIM(9NnU6KogWu0, W4rXKY5h6Fk, AdLLOjrToC4) | channels: 2 | status: consensus
- L7. If people read your work but do not subscribe, the problem is positioning clarity, not content quality. CLAIM(QmqN1Zl4X8U) | channels: 1 | status: single-source
- L8. Build the niche around the reader's problem and outcome, not around what you feel like writing. CLAIM(GAwbbH64cQY) | channels: 1 | status: single-source
- L9. Aim to be known for a category you own, not just to be known. CLAIM(xy2ELDsdSVY) | channels: 1 | status: single-source
- L10. Differentiate the label you use for yourself, because the label decides which bucket buyers file you in. CLAIM(TOMbKs4NJBU) | channels: 1 | status: single-source
- L11. Write a one-liner in the form [quote in corpus notes] and use it everywhere. CLAIM(AdLLOjrToC4) | channels: 1 | status: single-source
- L12. Do not stall your launch on branding; publish now and let the brand evolve on top of the old one. CLAIM(HIUDuIzERis, GSGOISFfmt0, U0IWoCaBw_o) | channels: 2 | status: consensus
- L13. Treat expertise as what you can pay forward to the next person, not as a title, a credential, or a follower count. CLAIM(8IMwkO0d6Dg) | channels: 1 | status: single-source
- L14. Do not chase originality: find what already works for writers in your niche and run your own version of it. CLAIM(C_R4O_y87qM, Y3G8NrvlcE8) | channels: 2 | status: consensus

## Where the creators disagree

How far to niche down. @nicolascole77 argues any "niche too small" story is wrong and specialization compounds:
@TheCoachsAlchemist argues niches can be narrowed past the point of a viable audience, and that people follow a person they like across topics:

Single-niche focus versus a generalist personal brand. @mattgiaro says mixed topics confuse followers:
@substackgrowth runs and defends a deliberate generalist position:

How much to invest in branding early. @sutoscience says good branding pays for itself and top publications have it:
@creativelyconsciousUK says most rebranding effort is displacement activity and the foundation does not change:

## Creator result claims (UNVERIFIED, never repeat as fact)

- [quote in corpus notes] (mxWcx2Pc5wY, @nicolascole77) CLAIM(mxWcx2Pc5wY) UNVERIFIED.
- [quote in corpus notes] (0f89F3a4iqE, @soloshannonhq) CLAIM(0f89F3a4iqE) UNVERIFIED.
- [quote in corpus notes] (2kSHYM7YAf4, @TheCoachsAlchemist) CLAIM(2kSHYM7YAf4) UNVERIFIED.
- [quote in corpus notes] (CpQLOLB-0po, @creativelyconsciousUK) CLAIM(CpQLOLB-0po) UNVERIFIED (stated goal, not a result).
- [quote in corpus notes] (8BWt4IMNazM, @sutoscience) CLAIM(8BWt4IMNazM) UNVERIFIED (creator cites another creator).

## Platform mechanics (Substack's own channel)

- The About page is where credibility and voice are established: [quote in corpus notes] (4eboPeVL8R8). CLAIM(4eboPeVL8R8).
- About page copy job: [quote in corpus notes] (bTdUaD3dZ9E). CLAIM(bTdUaD3dZ9E).
- Recording studio branding: [quote in corpus notes] (6nT6G_do-6c). CLAIM(6nT6G_do-6c).
- Discovery settings: [quote in corpus notes] (Zneuro_NdVw). CLAIM(Zneuro_NdVw).

## RIG application (RIG synthesis, not corpus claims)

(RIG synthesis, not corpus claims.)
- Position RIG's Substack as "you are the niche": write the build log of installing governed AI operations in small companies, so the journey content does the niching (laws L1, L14).
- Fix the promise before post 10: one line of the form [quote in corpus notes], and make the About page sell that offer rather than Mike's biography (L6, L11).
- Choose 1-3 pillars now (governed AI ops teardowns, agent-estate lessons, Denver small-business AI) and reject topics outside them, since 9 posts is early enough to lock the pillar set (L5).
- Skip the branding project. rigoperator.substack.com needs a clean About page and a clear name, not a visual identity pass (L12).
- Convert the ~5,400 LinkedIn followers by making every LinkedIn post carry the Substack promise; the positioning test is whether a LinkedIn visitor can tell in 10 seconds what the email gives them (L2, L7).

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/promise-and-pillars.md` | writing the one-line promise and testing pillars with the 10-ideas rule |
| `references/about-page-as-offer.md` | rebuilding the About page so it sells the promise |

## Hard rules

- The About page and publication name are public: drafted here, changed only after Mike's explicit yes.
- A claim on the About page needs a receipt (a dated number or a named, permissioned client). No invented results.
- Never position around the minor (Jacob) or reuse Lane A mascots (Birch, Unit 7, The Coach) on the RIG publication.
- Single-source laws are hypotheses: say so when one drives a recommendation.

## Done-test

`python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-strategy/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ss-strategy` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
