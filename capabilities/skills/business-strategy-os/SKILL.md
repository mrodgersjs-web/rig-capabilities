---
name: business-strategy-os
description: "Meta-skill and router for business strategy, distilled from Alex M H Smith's full YouTube corpus (51 videos) plus 10 Jev-selected peer channels (1,679 transcripts, 9.0M words) and 4 license-verified open-source packs. Use when a business, offer or team needs a real strategy (a unique how, not a goal), when growth stalls, when differentiation, category, competitive set, pricing power, wasted marketing or AI sameness is the problem, or when a strategy artifact must be reviewed. Routes to 8 strategy-* pillars and the strategy-director agent. JEV FIRST: typed judgments go to rig-s1gate before any frontier LLM call; if Jev is down, DEFER."
tags: [rig, doctrine, business-strategy, differentiation, positioning, meta-skill]
outcome: "business-strategy: a business leaves with one real strategy - a unique, risky how stated as 'we are the only X who Y, so customers get Z' - in a five-section document with named trade-offs and delivery-plus-communication execution, screened by strategy_lint.py and the Jev strategy.output rubric, every doctrine claim traceable to a corpus videoId"
activation: "Load when a business, product, offer, team or client needs a strategy, when a stated strategy may really be a goal or a 'be better' wish, when growth plateaus, price is compared, marketing spend does not convert, messaging will not land, or AI sameness is eroding an edge; also when reviewing anyone's strategy."
instruction: "Treat the strategy stack (new value, key innovation, customer story, company story) as the spine and leverage (high demand, low supply) as the test. Route to the one strategy-* pillar that matches before improvising. Run strategy_lint.py and the Jev strategy.output check on every artifact. Cite CLAIM(videoId); label creator results claims unverified."
applies_when:
  env: "any RIG workspace; corpus at data/corpora/strategy; pillars under capabilities/skills/strategy-*"
  runtime: "python3 stdlib for the three scripts; ~/.rig/bin/rig-s1gate for Jev"
  deps: "rig-s1gate (hosted, advisory until calibrated); no other network dependency"
  params: "one business unit per run; category named as a customer shops for it; one decision-maker"
  budget: "one session per draft; Jev a fraction of a cent; corpus search about 2 s"
  scale: "one business, offer or client engagement; not a portfolio or market-sizing study"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
  - gate-d-required:publish
  - gate-d-required:send
flow:
  - "Classify against the router and name the one pillar."
  - "Run strategy-diagnose first unless a diagnosis exists."
  - "Build through the pillars in stack order: new value, innovation, document, stories."
  - "Gate: strategy_lint.py then rig-s1gate strategy.output; a failure loops back to the owning pillar."
  - "Outward material goes to Gate-D; this family drafts, never sends."
done_when:
  - "file:capabilities/skills/business-strategy-os/SKILL.md"
  - "grep:capabilities/skills/business-strategy-os/SKILL.md:## Router"
  - "cmd:python3 capabilities/skills/business-strategy-os/scripts/claims_check.py"
  - "cmd:python3 capabilities/skills/business-strategy-os/scripts/claims_check.py --plant"
  - "cmd:python3 capabilities/skills/strategy-review/scripts/strategy_lint.py --selftest"
  - "cmd:test $(wc -l < data/corpora/strategy/manifest.jsonl | tr -d ' ') -ge 1679"
great_example: "examples/great/business-ops/great-strategy-document.md"
quality_floor: 0.8
out_of_scope:
  - "financial modelling, valuation, fundraising terms, M&A diligence"
  - "sending, publishing, pitching or posting (Gate-D owns every outward action)"
  - "presenting a creator's revenue, client-count or results claims as verified"
  - "inventing frameworks or quotes the corpus does not contain"
  - "content about a minor (Lane C) - route to jacob-x-growth"
---

# Business Strategy OS

JEV FIRST, and it binds every run of this family: an agent whose only context is
this excerpt sends semantic triage, routing, classification and verdicts (is this a
goal or a strategy, would a competitor concede the only-claim, is this category framed
the way customers shop) to the rig-s1gate Jev path BEFORE any frontier LLM call. When
the fast classifier is unavailable: DEFER, never guess a verdict locally. A required
noul passes only above 0.9.

## Load surface

This file is the always-loaded task-start surface for strategy work: the
strategy-director meta-agent, every strategy-* lane agent and every strategy-* pillar
skill load it before their first action. It is not a deep reference an agent must
already know about.

## Decision routing (binding)

Route each decision, first match wins: CODE (strategy_lint.py, claims_check.py,
corpus_search.py, counts and section checks) -> JEV (`rig-s1gate check
strategy.output --file <artifact> --subject strategy.output:<business> --json`;
`corpus.source` for source selection) -> SYSTEM 2 (generating options, drafting the
argument and stories) -> HUMAN (Gate-D: anything sent, published or presented to a
client, and the final choice of strategy, which belongs to the business owner).

<objective>
Give Jake and every RIG harness a governed way to produce strategies that are not
average: find value people want that they can only get from this business, make the
move that delivers it, write it so a team can execute it, and prove it is not a goal,
a plan or a "be better" wish before anyone acts on it.
</objective>

## The corpus in one paragraph

Seed: Alex M H Smith, strategy consultant and author of *No Bullsh\*t Strategy*
(captions render the bleeped title as "No Strategy"), full channel 2025-05 to 2026-09.
Peers (closest available, selected by Jev, see `data/corpora/strategy/TARGETS.md`):
StoryBrand (Donald Miller), Win Without Pitching (Blair Enns), Alex Hormozi,
Outthinker (Kaihan Krippendorff's guests, e.g. Richard Rumelt), Rory Sutherland's
MADMasters, ben at hiredthought (Wardley mapping), Ryan Deiss, Jeremy Haynes,
orenmeetsworld, The Invisible Game. Jev found no true twin of the seed (no candidate
cleared same_domain > 0.9 and practitioner_voice > 0.9), so the seed's doctrine is the
spine and peers extend it where they add a method; where they disagree, both views are
named. Open-source packs (MIT/Apache-2.0, provenance in `references/PROVENANCE.md`)
supply scorers and verdict gates the corpus lacks.

## The worldview in one sentence

A business wins by offering something people want that they can only get from it -
high demand, low supply, "leverage" CLAIM(u-jQ74wAqvo, udkwqWaBjnw) - and a strategy is
the unique, usually risky move that makes that true, written down and executed until
an outsider can see it CLAIM(y1-5nxulR68, Ikx1ECodt1M).

## Metadata

- **Source**: YouTube @AlexMHSmith full channel (33 long-form + 18 Shorts, 2025-05 to 2026-09) plus 10 peer channels chosen by the `corpus.source` Jev rubric. Corpus at `data/corpora/strategy/` (manifest.jsonl, COVERAGE.md, TARGETS.md, errors.jsonl).
- **Extracted**: 2026-09-26.
- **Method**: full-channel enumeration (yt-dlp) -> caption transcripts via two independent methods (fidelity re-fetch bigram precision >= 0.998) -> per-video notes (every quote machine-checked against its own transcript) -> synthesis with CLAIM(videoId) citations resolved by `scripts/claims_check.py`.
- **Evidence**: every doctrine claim in this family cites a videoId that resolves in `data/corpora/strategy/manifest.jsonl`.
- **Provenance and licences**: `references/PROVENANCE.md`.

## The laws

1. **Only is better than best.** "Better" is a synonym for "the same": chasing it means
   matching the competitor and ends in commodification CLAIM(PpcQFN9euao, dt9wpjlT-zA,
   q4W1KpJW8d0). Wrinkle: where quality has collapsed, not being terrible is itself
   the exception worth owning CLAIM(C7j8SqfHKBo).
2. **A goal is not a strategy.** "Number one by 2030", "triple revenue", "provider of
   choice" are results; a strategy never leaves you asking how, only when to start
   CLAIM(Ikx1ECodt1M, STExF7xbKzU, rWcJOpdrbCY).
3. **Leverage decides, execution adjusts.** High demand plus low supply lets mediocre
   execution work; without it world-class execution still struggles
   CLAIM(u-jQ74wAqvo, udkwqWaBjnw). Every business has a natural size set by what it is;
   to grow past it, change the beast, not the effort CLAIM(eQOEvgloI1s, c_AwFCghnBU).
4. **Saying you are different requires doing something different.** A claimed virtue
   ("excellent service") without an observable innovation is not differentiation; there
   are nine types of innovation to choose from CLAIM(FF46sruCVpY, ElaWyEeHS1w).
5. **The category is what the customer is shopping for,** not the shape of your product;
   your true competitive set sets your leverage CLAIM(y1-5nxulR68, XPhxUrUPO-A,
   LInrWGuTn68).
6. **New value comes from disagreement, difference or duplication,** and it hides behind
   a sacrifice of something the category treats as sacred CLAIM(ElaWyEeHS1w,
   dt9wpjlT-zA, q4W1KpJW8d0).
7. **The only-statement must survive your fiercest competitor.** "We are the only X who
   do Y, so customers get Z" is true only if that competitor would concede it in good
   faith CLAIM(kIw__JxmbUo, y1-5nxulR68).
8. **Marketing presents value; it cannot create demand.** Ask whether the offer is
   marketable before paying for good marketing CLAIM(qxdY2kdKz9g); in saturated channels,
   what still works is hard, rare and uncopyable CLAIM(JZVmL99ClfA, 8q-zjm7mFGg).
9. **AI converges everyone on the average answer.** Do not use it as the oracle for
   strategic choices; de-converge your inputs and take the hard option on purpose
   CLAIM(KBCFjK4ziUM, chkNrBQPyeY).
10. **Overserved markets reward changing the conditions, not playing well inside them.**
    Focus moves from company, to customer, to category CLAIM(r-B79h2GUPk, XipA7Kl-t-g,
    3h178lirdcw).
11. **One point of view, told as a story.** Strategy is a narrative with the business as
    hero, owned by one decision-maker, not a committee compromise; it is tested on
    someone who does not care CLAIM(y1-5nxulR68, TjEwEUWtwbk, LeBAj6jRyk4).
12. **A strategy that changes nothing is validation.** If you cannot list what you will
    stop doing, you do not have one CLAIM(y1-5nxulR68).

## Router

| Situation | Pillar skill | First sub-skill | Agent |
|---|---|---|---|
| "Is this even a strategy?", stalled growth, price pressure, messaging that will not land | strategy-diagnose | strategy-goal-or-strategy | strategy-diagnostician |
| Who do we really compete with, what market era are we in, moats and maps | strategy-diagnose | strategy-competitive-set / strategy-market-era / strategy-moat-map | strategy-diagnostician |
| We are the same as everyone; find what only we can offer | strategy-new-value | strategy-three-ds / strategy-invisible-rules / strategy-unfair-advantage | strategy-value-architect |
| AI is flattening our edge; everything is copyable | strategy-new-value | strategy-anti-convergence | strategy-value-architect |
| Turn the idea into a concrete move; write the only-statement | strategy-innovation | strategy-nine-innovations / strategy-only-statement | strategy-value-architect |
| Write the strategy document | strategy-document | strategy-argument / strategy-execution-plan | strategy-writer |
| Tell it to customers, team, investors | strategy-stories | strategy-customer-story / strategy-company-story | strategy-writer |
| Marketing is not working; pricing power | strategy-marketing | strategy-make-marketing-hard / strategy-value-pricing | strategy-marketing-realist |
| Leadership habits: what the team talks about, founder stance | strategy-leadership | strategy-front-foot-conversations | strategy-board-reviewer |
| Review or grade any strategy artifact | strategy-review | strategy-bs-lint / strategy-forced-verdict | strategy-board-reviewer + strategy-gate |

Service pricing and packaging for RIG's own offers: route to `pmm-productized-service-offers`
(existing skill; do not duplicate). Systems mapping of recurring problems: `systems-thinking-studio`.

## Contracts (every child inherits these)

- **Claim hygiene.** Doctrine claims carry `CLAIM(videoId)`; `scripts/claims_check.py`
  fails the family if any id does not resolve in the corpus manifest. Creator claims
  about their own results, revenue or clients are **unverified** and never become client
  promises (Hormozi figures, Alex's "hundreds of businesses", agency case numbers).
- **Quotes are verbatim or absent.** A paraphrase never sits inside quote marks.
- **Commercial disclosure.** Books, templates, courses, communities and workshops the
  creators sell (No Bullsh\*t Strategy, The Hidden Path, StoryBrand workshops, Win Without
  Pitching programs, Acquisition.com) are labelled COMMERCIAL wherever they appear.
- **Owner decides.** The family proposes and grades; the business owner chooses the
  strategy. Jev verdicts are advisory until calibrated and are never permission to send.
- **Evidence over eloquence.** A strategy that passes lint and Jev but rests on an
  unverified fact about the business (price, share, capability) is flagged, not shipped.

## Verification

```bash
cd ~/Developer/rig-capabilities
python3 capabilities/skills/business-strategy-os/scripts/claims_check.py          # every CLAIM resolves
python3 capabilities/skills/business-strategy-os/scripts/claims_check.py --plant  # proves the gate goes red
python3 capabilities/skills/strategy-review/scripts/strategy_lint.py --selftest   # red fixture trips, green stays clean
~/.rig/bin/rig-s1gate check strategy.output --file <artifact> --subject strategy.output:<business> --json
python3 capabilities/skills/business-strategy-os/scripts/corpus_search.py "invisible rules" -k 5   # evidence lookup
```

## Traps

- Answering "what should our strategy be" with a goal, a plan or a list of tactics.
- Letting a workshop or committee average the point of view back to the status quo CLAIM(TjEwEUWtwbk).
- Asking an LLM for the strategy itself: it returns the most likely, therefore average, answer CLAIM(KBCFjK4ziUM).
- Fixing a symptom (messaging, price, leads) with a copywriter or a bigger ad budget CLAIM(c_AwFCghnBU, qxdY2kdKz9g).
- Treating a peer's tactic (an ad formula, a funnel) as strategy; tactics sit downstream of the stack.
