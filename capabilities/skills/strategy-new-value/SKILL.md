---
name: strategy-new-value
description: "Pillar skill of business-strategy-os: find the new value only this business can offer. Runs the 3 Ds - disagreement, difference, duplication - to generate it (CLAIM(ElaWyEeHS1w)), finds the unfair advantage already present rather than inventing one (CLAIM(fjQVEpeq3Lw)), breaks an invisible rule of the category (CLAIM(LJuNNotb6DQ)), enters a peaceful category and seeds a subculture (CLAIM(XOBXwCKI5WI)), and fights convergence with a human point of view (CLAIM(KBCFjK4ziUM)). Load when a business is the same as everyone, when an idea feels obvious, or when the ask is 'what should we do differently'. Returns a new-value statement plus the sacrifice it requires; it does not write the document."
tags: [rig, doctrine, business-strategy, differentiation, new-value]
metadata:
  source: "Alex M H Smith corpus; claims resolve in data/corpora/strategy/manifest.jsonl"
  extracted: "2026-09-26"
  parent: business-strategy-os
outcome: "strategy-new-value: a named form of value people want that they cannot get from this business's competitors, with the 3-D route that produced it, the unfair advantage mapped onto it, the category rule it breaks, and the sacrifice it costs"
activation: "Load when the business is interchangeable, an idea feels obvious or borrowed, differentiation is claimed but not real, or the question is 'what could we offer that nobody else does'."
instruction: "New value is the crux of the whole stack: innovations, customer story and company story all serve it, so get it first (CLAIM(ElaWyEeHS1w), CLAIM(OwF6JhsrkRo)). Work all three Ds, then map the unfair advantage already present onto it, then name the category convention you will break and the thing you will give up. Do not accept an idea until a competitor could not simply copy it tomorrow."
applies_when:
  env: "one business or offer with access to its customers' real comparison set and the founder's history"
  runtime: "python3 stdlib; corpus_search for prior art; rig-s1gate for Jev checks"
  deps: "corpus at data/corpora/strategy; no other network dependency"
  params: "the category as customers name it; the founder's effort-versus-return map; the category's unexamined conventions"
  budget: "one to two sessions; Jev checks a fraction of a cent each"
  scale: "one business or offer; not a portfolio of new ventures"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - "Run the 3 Ds in order: disagreement (what do you think is stupid in this category?), difference (what is already different, accidentally?), duplication (what does another industry do that you could copy?)."
  - "Map the unfair advantage: drop the vision, list every initiative scored for effort and for return, take the most skewed, then map that non-replicable fact onto the market."
  - "Name the invisible rule you will break and the sacrifice the idea requires; if nothing has to be given up, you have not found the idea yet."
  - "Choose the category conditions to enter or change (peaceful category, unsettled water) and how the early adopters will rationalize the purchase."
  - "Test for copyability and AI convergence: could a motivated competitor or an LLM produce this next quarter? If yes, de-converge the inputs or go harder."
done_when:
  - "grep:capabilities/skills/strategy-new-value/SKILL.md:## The 3 Ds"
  - "cmd:python3 capabilities/skills/business-strategy-os/scripts/claims_check.py capabilities/skills/strategy-new-value/SKILL.md"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/strategy-new-value/SKILL.md"
great_example: "examples/great/business-ops/great-strategy-document.md"
quality_floor: 0.75
out_of_scope:
  - "turning the value into a concrete innovation (strategy-innovation)"
  - "writing the argument, stories or execution (strategy-document, strategy-stories)"
---

# strategy-new-value

> **JEV FIRST.** This pillar is a task-start surface in its own right, not only through
> the meta-skill. Send every typed judgment it forces (whether this value is non-obvious, whether this advantage is non-replicable, and whether this idea is still copyable next quarter) to `rig-s1gate` BEFORE any
> frontier LLM call; a required noul passes only above 0.9. **When the fast classifier is
> unavailable: DEFER, never guess a verdict locally, and never let an unjudged stage
> advance.**



## The 3 Ds

New value is the crux: if you do not bring it, "the business shouldn't exist" because the world would be fine without you CLAIM(ElaWyEeHS1w). Most businesses fail because they double, triple and quadruple up on what is already done. There is no such thing as a "correct" new idea; what matters is that it is non-obvious, which means thinking the opposite way to everyone else and looking where competitors are not looking.

1. **Disagreement.** What in your industry do you, the founder, think is stupid, and what would you do instead? Any disagreement is a potential route to new value: ask how your alternative point of view creates value for the customer. Jobs disagreed that computers should be dull and technical; that disagreement produced accessibility CLAIM(ElaWyEeHS1w, xFlm6Qh8hUY). Peter Thiel's favorite interview question: "What is it that you believe that no one else believes?"
2. **Difference.** Look at ways your business is already different from competitors, especially accidental ones, then ask what customer value that difference could twist into. Airbnb's conference overflow became "belong anywhere"; Lush copied fresh-produce merchandising into cosmetics CLAIM(ElaWyEeHS1w). The unloved side project that performs on minimal effort is the signal: your true strategic advantage is where effort is low and reward is high CLAIM(fjQVEpeq3Lw, ca-K8zP1Y-c).
3. **Duplication.** Do not copy competitors; copy a company from outside your category. What form of value exists elsewhere that does not exist here, and what would it look like overlaid on your business? Lush lifted freshness; Peloton bundled existing hardware with existing software CLAIM(ElaWyEeHS1w, AnpT-o6cZZk).

## The unfair advantage already present

Everyone has one; most go unseen because they do not fit the picture of the planned business CLAIM(fjQVEpeq3Lw).
1. Drop the vision: notice what you have been filtering out because it does not match the plan.
2. List every initiative; score each for effort going in (0-10) and for how well it performs (0-10).
3. Take the most skewed ratio, low effort and high return, "including if it is the side project", and go there.
4. If nothing surfaces, force a list of non-replicable facts across ten categories of your life (family, career, school, geography, connections, recognition); do not stop at "I don't have anything".
5. Map each fact onto the market: a fact is not an advantage until it is combined with the thing you are trying to do. Sweden was not an advantage until Spotify mapped it onto securing music licenses CLAIM(fjQVEpeq3Lw, KVNB4ybqQvI).
Test: if only I had that, I would be in their shoes too, is the envy frame he rejects; the advantage is what only you can do.

## Invisible rules

A convention every company in a category follows blindly without asking whether it is necessary CLAIM(LJuNNotb6DQ, LInrWGuTn68). Hunt sacred cows: the pricing model everyone uses, the features everyone has, the customer everyone chases, the channel everything ships through, the billable hour. For each ask: is this essential to the product actually working, or is it just "thinking on rails"? Break one that is not essential and picture the broken version. Afterwards it looks obvious; it was not obvious before someone broke it (Method, Red Bull) CLAIM(LJuNNotb6DQ, XipA7Kl-t-g).

## Peaceful categories and the bedrock

- **Peaceful categories**: settled, boring, mature; new ideas almost never emerge, so weirdness is visible. In a churning category like soft drinks, standing out is nearly impossible CLAIM(XOBXwCKI5WI).
- **Plausible deniability**: attach a tiny germ of logic so buyers can rationalise a purchase they do not need; seed the niche subculture where the product is genuinely useful first (Yeti's bear clasps, Crocs' boating shoe) CLAIM(XOBXwCKI5WI).
- **Signaling**: if consumption is private, add a visible artifact so others see it (Yeti stickers) and lean into the statement once users make one CLAIM(XOBXwCKI5WI).
- **Conviction**: pull the same conviction through the line; do not hedge toward what the category already accepts CLAIM(XOBXwCKI5WI).

## Anti-convergence (the AI era)

AI does not give the best answer, it gives the most likely, therefore the average, answer; everyone slowly converges on the same ideas, look and sentence structures, and a tactic loses value the moment it becomes abundant CLAIM(KBCFjK4ziUM, JZVmL99ClfA).
- Stop using AI as the oracle for path choice; use it where there is a correct answer, as a researcher and as a maker. Knowing different things is as valuable as knowing more CLAIM(KBCFjK4ziUM, chkNrBQPyeY).
- Drink from a different trough than the average of the internet: your own strange lived experience is the dataset the machine and your competitors do not have.
- Compete to be the name your peers cannot stop talking about: the place people want to work and invest; that needs randomness and a human point of view, not correctness CLAIM(KBCFjK4ziUM, Cr0nyKZHa7w).
- When it matters, take the hard, expensive, slow option on purpose; point at something and say nobody else could do that CLAIM(KBCFjK4ziUM, JZVmL99ClfA).
- Hard and rare is the standing scarcity test: value is a function of scarcity, not goodness CLAIM(8q-zjm7mFGg, chkNrBQPyeY, JZVmL99ClfA).

## The sacrifice test

The non-obvious idea hides behind a sacrifice of what the category treats as sacred: Southwest gave up business travellers, the most lucrative customer, to create low-cost air travel CLAIM(dt9wpjlT-zA, XipA7Kl-t-g, q4W1KpJW8d0). "Only is better than best": a strategy that requires nothing to be given up is still a status quo. Name what you stop, refuse or change before handing off to strategy-innovation.

## Traps

- Answering "what customers want" and landing in the narrow band of obvious ideas: customers do not know what they want until they see it, and everyone is already doing what customers asked for CLAIM(ElaWyEeHS1w).
- Inventing a new advantage when one already exists: use is the point, not invention CLAIM(fjQVEpeq3Lw).
- Picking the cleverest idea rather than the interesting one: it is 2025, there is no scientifically correct unmet need, find an idea that makes people excited and think differently CLAIM(dt9wpjlT-zA).
- Treating "we are different because of our culture" as a value: culture is one of the nine innovation types only when it is a designed organisational change CLAIM(FF46sruCVpY).
