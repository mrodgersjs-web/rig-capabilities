---
name: strategy-leadership
description: "Pillar skill of business-strategy-os: the leadership habits that make a strategy real. Conversations are destiny: what the leadership team repeats predicts whether the business thrives, dominates or disappears in five years (CLAIM(Cr0nyKZHa7w)); the five front-foot questions (3x in 18 months, the industry in five years, what we will fix, what peers think, what cannot be copied) run on the calendar as a walk, coffee or beer, not a deck. Covers the founder's stance (serve yourself, the customer, the industry) and grower versus harvester (CLAIM(99wUqymnvSc), CLAIM(kCGh6NObzC0)). Load when a strategy exists but the team is not moving."
tags: [rig, doctrine, business-strategy, leadership, meetings]
metadata:
  source: "Alex M H Smith corpus (CLAIM(Cr0nyKZHa7w), CLAIM(99wUqymnvSc), CLAIM(kCGh6NObzC0), CLAIM(Ege5JDlGpy8))"
  extracted: "2026-09-26"
  parent: business-strategy-os
outcome: "strategy-leadership: a leadership team running the five front-foot conversations on the calendar as a habit, with the founder's stance named (self, customer, or industry) and the grower-versus-harvester choice made deliberately"
activation: "Load when a strategy document exists but the team is not executing, when the leadership team's conversations have drifted to defence and detail, or when the founder's motives need naming."
instruction: "Block an hour a week as if it were your most important client, pick one of the five questions, and have it on a walk, over coffee or a beer with the co-founder or team; no deck, no spreadsheet, no consultant, and do not let people hedge, because an honest no is the issue. Set the founder's stance deliberately."
applies_when:
  env: "a business with a leadership team of two or more; the strategy already written"
  runtime: "python3 stdlib; calendar and notes only"
  deps: "corpus at data/corpora/strategy; no other network dependency"
  params: "one hour a week; one of five questions per session; the founder's current stance"
  budget: "an hour a week; no tooling cost"
  scale: "one leadership team; not an org-wide change programme"
permissions:
  - fs.read
  - fs.write
flow:
  - "Name the founder's stance: serving yourself (poison), serving the customer (mediocrity), serving the industry (iconic); decide which one you are on and what it demands."
  - "Decide grower or harvester: growers create value, harvesters collect it; most leaders are harvesters and either drain an un-grown crop or pick the brand to nothing; each has a season."
  - "Block an hour a week on the calendar, pick one of the five questions, and hold it without a deck; do not let hedged answers pass."
  - "Close each session by naming the one proactive move the answer implies; strategy work is never urgent, so it is scheduled anyway."
done_when:
  - "grep:capabilities/skills/strategy-leadership/SKILL.md:## The five front-foot conversations"
  - "cmd:python3 capabilities/skills/business-strategy-os/scripts/claims_check.py capabilities/skills/strategy-leadership/SKILL.md"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/strategy-leadership/SKILL.md"
great_example: "examples/great/business-ops/great-strategy-document.md"
quality_floor: 0.75
out_of_scope:
  - "hiring, structure and compensation (route to the relevant ops skills)"
---

# strategy-leadership

> **JEV FIRST.** This pillar is a task-start surface in its own right, not only through
> the meta-skill. Send every typed judgment it forces (whether the founder's stance is named, whether the grower/harvester choice is made, and whether the conversations are real) to `rig-s1gate` BEFORE any
> frontier LLM call; a required noul passes only above 0.9. **When the fast classifier is
> unavailable: DEFER, never guess a verdict locally, and never let an unjudged stage
> advance.**



## Conversations are destiny

What the team talks about over and over predicts whether the business is thriving, dominating or disappearing in five years. After the unavoidable admin, the thin sliver of discretionary attention is where outcome variability lives, and left alone it drifts down, toward defence and detail, not up CLAIM(Cr0nyKZHa7w). Strategy is optional; these conversations are not, and in 2026 the only form of defence is attack.

## The five front-foot conversations

One hour a week, on a walk, over coffee or a beer, with the co-founder or leadership team; no agenda, no slides, no output; do not let people hedge, because an honest no is the finding CLAIM(Cr0nyKZHa7w).
1. What is the chance we grow 3x in the next 18 months? A goal too aggressive to hit by tinkering; most should aim at something like 3x revenue or profit, not a literal Coca-Cola target.
2. Where will our industry be in five years, with or without us? Put two or three genuinely different futures on the table, including one that seems crazy, and ask how you would adapt; do not bet the company on one forecast.
3. What needs to be fixed about our industry, and will we fix it? Name what is broken, lazy, dishonest or stupid, and ask whether this room can fix it at a scale others must respond to; make the weather rather than suffer it.
4. What do our peers actually think of us? What is the sentence that follows our name at a drink; when a journalist writes about our sector, are we the ones they call; when talent moves in our space, are we the name they want on their resume.
5. What are we doing that cannot be copied? Create and own an offer or department that would not exist without us, or admit we own nothing.

## The founder's stance

Three stages, each one's downstream: serving yourself (absolute poison, the market does not care about your freedom, rewards or wish to be rich), serving the customer (mediocrity, the customer is just as selfish as you are), serving the industry (iconic, you change the industry or the market has no reason for you) CLAIM(99wUqymnvSc, Ege5JDlGpy8, D0W0RTAh7nc). The switch is not moral, it is strategic: an industry-serving founder is making the weather CLAIM(Cr0nyKZHa7w).

## Grower and harvester

There are only two kinds of leader: the grower, who wants to create value, and the harvester, who collects it. Each has a place and a season, and most leaders are harvesters at heart, so they either extract from a crop that was never grown or keep picking until the brand is gone. Apple is the parable: Jobs the grower, Cook the harvester CLAIM(kCGh6NObzC0).

## Traps

- Running the questions as a meeting with a deck; they are conversations, and the format is the point CLAIM(Cr0nyKZHa7w).
- Letting "we're doing fine" pass as an answer; the honest no is the issue CLAIM(Cr0nyKZHa7w).
- Treating strategy as something that will become urgent on its own; it never will, so it goes on the calendar CLAIM(dt9wpjlT-zA).
