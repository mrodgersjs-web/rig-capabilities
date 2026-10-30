---
name: strategy-diagnose
description: "Pillar skill of business-strategy-os: decide whether a business has a strategy at all, and which disease it has. Distinguishes goal / plan / 'better' wish from a real strategy (CLAIM(rWcJOpdrbCY), CLAIM(Ikx1ECodt1M)), separates symptoms from the strategic disease (CLAIM(c_AwFCghnBU)), classifies the market era (underserved / served / overserved, CLAIM(r-B79h2GUPk)), finds the true competitive set (CLAIM(XPhxUrUPO-A), CLAIM(LInrWGuTn68)), and maps moats and the landscape (Wardley, CLAIM(lhDcrVWFU40)). Load when a business is stuck, growing slowly, price-compared, or told it needs a strategy. Returns a named diagnosis with the next pillar named; it never writes the strategy itself."
tags: [rig, doctrine, business-strategy, diagnosis, positioning]
metadata:
  source: "Alex M H Smith corpus (CLAIM ids resolve in data/corpora/strategy/manifest.jsonl); peer: Outthinker/Rumelt CLAIM(Ggl_O1vhk_c), hiredthought Wardley chapters"
  extracted: "2026-09-26"
  parent: business-strategy-os
outcome: "strategy-diagnosis: a business leaves with one named disease (goal-not-strategy, no-leverage, wrong-competitive-set, overserved-market, commodity-cluster, copyable-edge) and the single next pillar named - never a symptom fix list"
activation: "Load when a business is stuck, growing below plan, compared on price, told it needs a strategy, or has a written strategy that produces no change."
instruction: "Diagnose before any remedy. Name the disease in one sentence, cite the corpus rule that identifies it, and route to exactly one next pillar. If the stated strategy is a goal, a plan, or a 'be better' wish, say so plainly and go to strategy-new-value, not to tactics."
applies_when:
  env: "one business, product or client offer with access to prices, competitors and a decision-maker"
  runtime: "python3 stdlib; rig-s1gate for the strategy.output / corpus.source Jev checks"
  deps: "corpus at data/corpora/strategy (manifest.jsonl, TARGETS.md); no network beyond Jev"
  params: "the category as a customer shopping would name it; the current stated strategy in one sentence; the top 3 named competitors or substitutes"
  budget: "one session to diagnose; Jev checks a fraction of a cent each"
  scale: "single business unit; not a portfolio or market-sizing exercise"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - "Run strategy-goal-or-strategy: put the stated strategy through the how-not-how test and the fiercest-competitor test."
  - "Classify the market era (underserved, served, overserved) and the K-shape: is supply exploding while demand is flat?"
  - "Find the true competitive set (what customers compare you to) and score leverage: high demand, low supply?"
  - "Screen the five red flags / rare questions for the disease behind the symptom; map moats and the landscape with strategy-moat-map."
  - "Name one disease in a sentence, cite the CLAIM rule, and hand off to exactly one pillar."
done_when:
  - "grep:capabilities/skills/strategy-diagnose/SKILL.md:## The six diseases"
  - "cmd:python3 capabilities/skills/business-strategy-os/scripts/claims_check.py capabilities/skills/strategy-diagnose/SKILL.md"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/strategy-diagnose/SKILL.md"
great_example: "examples/great/business-ops/great-strategy-document.md"
quality_floor: 0.75
out_of_scope:
  - writing the strategy, the only-statement, the stories or the execution (other pillars own them)"
  - pricing changes for RIG's own offers (pmm-productized-service-offers)"
  - declaring a disease without evidence the category is what the customer shops for"
---

# strategy-diagnose

> **JEV FIRST.** This pillar is a task-start surface in its own right, not only through the
> meta-skill. Send every typed judgment it forces (whether the stated strategy is a strategy
> at all, whether the named disease is real, whether the category is framed the way customers
> shop) to `rig-s1gate` BEFORE any frontier LLM call; a required noul passes only above 0.9.
> **When the fast classifier is unavailable: DEFER, never guess a verdict locally, and never
> let an unjudged stage advance.**


## The six diseases

1. **Goal-not-strategy.** "Number one by 2030", "triple revenue", "provider of choice", "grow 3x" - a result, not a how. "The number one most cliched, most predictable reason" companies have no strategy is mistaking a goal for one CLAIM(rWcJOpdrbCY); a true strategy never leaves you asking how, only when to start CLAIM(Ikx1ECodt1M, STExF7xbKzU). A plan (a budget, a calendar) is also not a strategy; plans assume the goal is right.
2. **No leverage.** High demand, low supply is what makes messaging, marketing and product work; with mediocre execution CLAIM(u-jQ74wAqvo, udkwqWaBjnw). "Better" is a synonym for "the same", so trying to out-execute lands you in the commodifying dogfight CLAIM(PpcQFN9euao, dt9wpjlT-zA, q4W1KpJW8d0). The desert-water test: are you the only seller of something people badly want?
3. **Wrong competitive set.** The category is not what you think; it is what the customer is shopping for CLAIM(y1-5nxulR68). Leverage is set by the options the buyer actually compares you against - move the offer into the set where you have power (Eat Natural: candy-bar shelf, not health aisle) CLAIM(XPhxUrUPO-A, LInrWGuTn68).
4. **Overserved market.** Supply exploding while demand is flat (his K-shape) means the playbook of answering needs, positioning and niching is cooked; the win is changing the conditions - company focus to customer focus to category focus CLAIM(r-B79h2GUPk, XipA7Kl-t-g, 3h178liredcw). Natural size: every business has a ceiling set by what it is; change the beast, not the effort CLAIM(eQOEvgloI1s, c_AwFCghnBU).
5. **Commodity cluster.** Businesses competing to beat each other match innovations and prices until they are interchangeable and stacked; trying to be better accelerates the clustering CLAIM(XipA7Kl-t-g). Even a good edge disappears when AI makes the same answer available to everyone CLAIM(KBCFjK4ziUM, chkNrBQPyeY).
6. **Copyable edge.** You are different only in ways a motivated competitor or an LLM can copy: writing, ideas, volume, a nice aesthetic. What still holds is hard and rare CLAIM(JZVmL99ClfA, 8q-zjm7mFGg). A reputation monopoly lets quality slip because buyers have no alternative; software doing the junior work removes headcount as a moat CLAIM(ohCAPyqlJpo, P7G80jGOr9w).

## Symptom vs disease

Headaches, tiredness, bloating have treatments that do not cure the disease; billions are wasted on symptom treatments while the strategic issue goes untouched CLAIM(c_AwFCghnBU). The five pains map to diseases, not fixes:

| Pain | Disease | Directional fix (not a tactic) |
|---|---|---|
| Plateau / growth stalled | natural size, overserved market | change what the business is (Amazon: books to general retail) |
| Price pressure | no mini-monopoly | make the offer the only one of its kind so comparison is impossible |
| Messaging will not land | nothing interesting to say | change the strategy until there is an interesting gambit; do not start with a copywriter |
| Thin profit | in the comparison set | own the purchase so you are not compared at the moment of buying |
| Leads dry | wrong aisle | insert the offer into a category people already shop and understand |

## The how-not-how test

1. Ask "how?" until you cannot. If the answer is a goal, it is not a strategy.
2. Ask "would our fiercest competitor agree this is true?" If yes, the only-claim is empty CLAIM(kIw__JxmbUo, y1-5nxulR68).
3. Ask "what are we stopping?" If nothing, the document validates the status quo CLAIM(y1-5nxulR68).
4. Ask the Rumelt test: a strategy is a hypothesis about the single crux, the most important challenge we can actually handle, not a list of goals CLAIM(Ggl_O1vhk_c).

## The five rare questions

Use when the ordinary questions (more leads, stand out, 2x) are exhausted CLAIM(LInrWGuTn68):
1. Who are we really competing against?
2. Are we following any invisible rules?
3. Where do we suck? (what does each weakness enable that a "fixed" version could not?)
4. How do we help our competitors? (what would balance their offer?)
5. How can we sell to people who don't want our stuff? (sell oat milk to non-oat-milk drinkers)

## Market era

- **Underserved** (demand > supply): win by supplying - Ford's assembly line, early Nike.
- **Served** (everyone can get it): win by positioning, then by niching on unmet problems - Ries and Trout, referenced by CLAIM(r-B79h2GUPk).
- **Overserved** (now, most categories): gaps are gone, the customer is satisfied; win by changing the conditions of the market, by making the weather rather than suffering it CLAIM(r-B79h2GUPk, Cr0nyKZHa7w).

## Moats and the landscape

- Five advantages, all continuums, ranked for a business to choose from: Sticky, Expensive (gross margin), Expansion (growing market), Air (low ops complexity), Unique (moat); if you can have only one, pick retention CLAIM(3fsJFUvA6Ts). (Hormozi figures in his videos are his own claims, unverified.)
- Wardley mapping (hiredthought): landscape before purpose; value chain of needs (visible) by evolution (genesis, custom-built, product, commodity); seven climatic patterns you cannot stop but can anticipate; build maps in small loops - "pockets of coherence" - not all-or-nothing CLAIM(DgxdYuIt9-o, jdN2qR9QYbY, uJbPZJYiCSY, GC3uNLaOyrk). Wardley's book is CC-BY-SA: reference, never copy the text.

## Traps

- Diagnosing on titles or vibes: the true competitive set is what buyers compare, which is often an adjacent set.
- "Be better" as a diagnosis - it names a fight you cannot win.
- Fixing messaging, price or leads directly before naming the disease.
- Treating a plan or budget as a strategy.
