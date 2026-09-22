---
name: rig-comms-conversation-craft
description: Conversation craft translated into message engineering — promise-confirming hooks, need-ladder questions, reflective follow-ups, objection reframes, proof beats, dialogue rhythm, and agency-preserving closes. Distilled from 20 full transcripts across all 11 populated channels in the 250-transcript comms-craft corpus. Use when drafting or critiquing interviews, sales calls, emails, posts, presentations, or any consequential human exchange.
outcome: conversations that earn attention fast, turn surface claims into real motives, resolve resistance without pressure, and end in an explicit next move
done_when:
  - file:capabilities/skills/rig-comms-conversation-craft/SKILL.md
  - grep:capabilities/skills/rig-comms-conversation-craft/SKILL.md:need ladder
  - grep:capabilities/skills/rig-comms-conversation-craft/SKILL.md:dOZkAqR_2lA
  - cmd:python3 -c "import json; m=[json.loads(l) for l in open('data/corpora/how-to/manifest.jsonl') if json.loads(l)['surface']=='comms-craft']; assert len(m)==250; ids={r['video_id'] for r in m}; body=open('capabilities/skills/rig-comms-conversation-craft/SKILL.md').read(); cited={i for i in ids if i in body}; assert len(cited)>=12, cited; print('OK', len(cited))"
quality_floor: 0.65
great_example: capabilities/skills/rig-comms-conversation-craft/SKILL.md
metadata:
  source_corpus: data/corpora/how-to/comms-craft (250 transcripts; sha256-verified parent manifest)
---

# rig-comms-conversation-craft

Ten patterns distilled from 20 full transcripts across all 10 populated channels in the
200-transcript comms-craft corpus. Quotes retain transcript wording; every parenthetical is a
verbatim `video_id` from `data/corpora/how-to/manifest.jsonl`.

## P1 — Confirm the promise, then collapse time-to-value
The opening contract is simple: prove this is the exchange the person expected, then make the
first useful move. The Futur calls this "confirm your click in your first five seconds" and warns
that "the longer the time to value, the more people are going to drop off" (j8yGn1v8OgU).
Thomas Frank promises a complete task manager from a blank page, then says, "and this build
starts right now over in screen share mode" (H2IFv_GBdUQ).

**Mechanism:** attention begins as a verification problem. Until the listener sees the promised
subject and a credible path to value, every sentence is exit friction. Context can be drip-fed
when it becomes necessary; it cannot invoice the opening.

**Draft check:** the first line names the promised subject, the first beat delivers progress, and
biography waits. If the first useful sentence survives after deleting the introduction, delete the
introduction.

## P2 — Open one tension, not a topic
A topic tells people what is present; tension gives them a reason to stay. Ali Abdaal opens with a
named person and a hard transformation: "He made $98 in his first 6 months and then a few years
later, last year, he made $835,000" (LLjpnubsOWc). Noah Kagan couples spectacular proof with a
moral reversal: the businesses made millions, yet the founder found them "extremely unfulfilling"
and said, "I felt like a snake oil salesman" (o2YgHTAHYbs). GaryVee uses the blunt version:
"I've really bad news. It's going to go away. away. away. Let me explain" (rweBX3sO_8c).

**Mechanism:** contrast creates a missing explanation. Concrete stakes stop the gap from feeling
like clickbait; the audience knows what changed, what may be lost, or what does not add up.

**Draft check:** write the unanswered question produced by the opening. It must be singular and
answerable. "This is about sales" is a label. "Why did $12 million feel like failure?" is an
attention engine.

## P3 — Run the need ladder: fact → constraint → motive
The first answer is usually a description, not the decision driver. Alex Hormozi moves from the
business, to what blocks scale, to: "Why do you even want to grow the business to begin with?
Like, you're already making money, right?" (zzleYxkf39k). Charisma on Command compresses the
same move: "Then the question is what's what's the need behind that want?" and then asks for the
need behind the need to relax (yei-LUJ0Uvo). The Futur tests commitment with two successive
questions — "What would need to happen for you to be 100%?" and "What would you need to believe
in order to be 100%?" (dOZkAqR_2lA).

**Mechanism:** people defend methods but reveal motives. Each rung separates the stated tactic
from the outcome it is meant to produce. Once the real need is named, the conversation can invent
more than one route to it.

**Draft check:** after any want, objection, or urgency claim, ask one level down: What blocks it?
Why does removing that block matter? Stop when the answer becomes a human consequence, not a
business category.

## P4 — Reflect once; sharpen once
A follow-up should prove the answer landed and expose the next unresolved edge. Ali Abdaal turns
a long answer into: "So, it's like diversifying your identity away from putting all your eggs in
the I work at Google basket" (LLjpnubsOWc). GaryVee listens for the identity stake and sharpens it:
"It's when your entire self-worth is attached to your career, what do you do when that career goes
away?" (qh3_JJFxDmQ). Roberto Nickson uses a lighter cadence: validate one concrete point, then
bridge to the next bounded question (8HrzoEvLWH0).

**Mechanism:** reflection gives the speaker a proposition to confirm, reject, or complicate.
Sharpening converts the proposition into forward motion. Reflection without a new edge is parroting;
a new question without reflection feels like an interrogation.

**Draft check:** between answer and question, allow one sentence that begins in substance with
"what I hear is..." Then ask about the contradiction, consequence, choice, or missing detail that
sentence exposes. Do not summarize the whole answer.

## P5 — Treat an objection as a mismatched goal or method
Do not defend the recommendation until the real optimization target is visible. GaryVee separates
the goal from the assumed vehicle: "You don't have to be a teacher to be in the trenches" and
"You can replicate it in a different way. You understand?" (rweBX3sO_8c). In a polarized exchange,
he first unbundles the premise: "I think things are blended. And things are easy for me to decouple.
Both things can be true" (qh3_JJFxDmQ). Ali Abdaal's interview splits a vague compliance objection
into professional and compliance questions before naming the right decision-maker (LLjpnubsOWc).

**Mechanism:** resistance often protects an outcome, not a position. Separating goal from method
turns "yes/no" into "which route?" Separating bundled truths lets you validate the legitimate
concern without conceding its attached conclusion.

**Draft check:** write the objection as "I need [outcome], and I currently believe [method] is the
only safe route." Preserve the outcome. Offer an alternative method, its tradeoff, and the boundary
where the objection would be correct.

## P6 — Replace defense with inspectable proof
When a claim can be shown, another paragraph is a tax. Marketing Examples observes, "we don't want
to be told we want to be shown"; the seller peels a potato, then a carrot, then lets the customer
try ( _OMrvqU4Blk). Ali Abdaal voices the built-in-dictation objection, answers it briefly, and says,
"So, we're going to test this live. I'm going to say the same thing into my phone and also [music]
into Whisper Flow" (Ig2zcKJQWig). GaryVee turns an algorithm dispute into a next-morning experiment:
"stop the podcast, go to Instagram, go to search, type in rainbows, enter, like three posts"
(qh3_JJFxDmQ).

**Mechanism:** demonstration changes the listener from judge to witness. Participation goes one
step further: the person generates the evidence, so the proof no longer depends on the speaker's
status.

**Draft check:** circle every sentence shaped like "trust me, this works." Replace it with an
artifact, side-by-side test, live example, or reversible micro-experiment. State what result would
falsify the claim.

## P7 — Hold rhythm with promise → progress → payoff → new question
Long exchanges fail when they become an undifferentiated stream. The Futur names the atomic unit:
"A story cycle is just a promise, a progress, and a payoff"; after the payoff, open the next cycle
(j8yGn1v8OgU). Roberto Nickson moves from AI to devices with an explicit bridge: "but speaking of
Hardware it's been 10 years now since the Oculus acquisition 10 years of reality Labs"
(8HrzoEvLWH0). Thomas Frank refreshes location and importance — "the next thing we're going to do
is really the most useful part of this build" — before the next technical section (H2IFv_GBdUQ).
Hormozi likewise maps offer, price, sales motion, and demand before moving through them
(mRlSb0O5QNU).

**Mechanism:** progress rewards the attention already spent; a new question recruits the next
unit. Bridges preserve continuity across topic changes. Signposts reduce working-memory load
without repeating the content.

**Draft check:** every section must answer one promised question and open exactly one next question.
At each transition, name the connective word: "because," "but," "so," or "speaking of." If none
fits, the section is probably a detour.

## P8 — Use one person's symptom language
Composite audiences produce dialogue no human would say. The Futur's correction is explicit:
"I would like for you to err more on how they would say it" and "swap services, services, services,
websites, marketing, branding, etc., for symptoms" (dOZkAqR_2lA). Hormozi reports the payoff when
the opening names one narrow avatar and recurring pain: prospects say, "Oh my gosh, it's like you
knew me" (mRlSb0O5QNU). Marketing Examples adds the mechanical check: direct language, personal
pronouns, short words, short sentences (_OMrvqU4Blk).

**Mechanism:** symptom language enters a conversation already running in the person's head. Service
labels require translation and trigger vendor comparison. A real person's words carry scene,
friction, and consequence at once.

**Draft check:** stage the exact moment: who is present, what just went wrong, and what the person
says next. Use that line. Reject any sentence that sounds like the seller's capability map wearing
a buyer costume.

## P9 — Close on a specific, agency-preserving move
A close is not pressure; it is removal of ambiguity. The Futur turns "I'll share it" into: "Thanks
so much for offering to share it. What would be the best way to share this?" then specifies channel,
message, and contribution (dOZkAqR_2lA). Hormozi puts one micro-commitment in the pre-call video:
"hey by the way text me your head count" (mRlSb0O5QNU). Marketing Examples shows a seller who places
the product and money where the action is obvious while preserving the principle that "people are
happy to buy but they hate being sold to" (_OMrvqU4Blk). Roberto Nickson closes with a callback —
"the eight months have gone by like this interview did as well" — rather than a generic sign-off
(8HrzoEvLWH0).

**Mechanism:** specificity converts goodwill into behavior. A small voluntary action proves
attention and creates momentum; a callback repays attention with closure. Pressure is unnecessary
when the next move is visible and proportionate.

**Draft check:** name who does what, through which channel, and when. The other person must retain a
clean no. If the close depends on urgency theater, hidden expectations, or a vague "circle back,"
the conversation is not closed.

## P10 — Regulate before you redirect
A tense exchange is shaped by the speaker's state before it is shaped by the speaker's words.
Hostage negotiator George Kohlrieser calls staying calm the "number one lesson" and replaces
self-defense with: "Don't defend. Ask the question" (AxA1SvOmp1Y). In a conversation about
co-regulation, Sarah Baldwin says that if the practitioner is not regulated, "you should stop the
session"; from a steadier state, language becomes slower and attunement precedes advice
(rcdTQgPyzlg).

**Mechanism:** pace, turn-taking, and vocal tension signal safety before the argument is processed.
An activated speaker is more likely to defend, control, or ramble; a deliberate pause restores
enough choice to reflect, ask one bounded question, and hear the answer.

**Draft check:** before a consequential reply, inspect breath, pace, and the urge to rebut. If any
are accelerating, pause and lengthen the exhale before speaking. Then reflect one fact and ask one
question. If you cannot do that honestly, defer the exchange rather than perform calm.

# Anti-patterns (named in the corpus)
- **Context invoice** — front-loading biography, setup, or credentials before value. "Do not list your resume in your intro" (j8yGn1v8OgU). Drip-feed only the context required for the current decision.
- **Softball theater** — questions designed to cue prepared promotion. Ali Abdaal describes "teeing up softball questions that they knew the answers to rather than having an interesting conversation" (Ig2zcKJQWig). Ask for a contradiction, artifact, cost, or failed case.
- **Commodity surrender** — letting price remain the only comparison variable. "Customers will always go to price if you don't give them any other variables to consider" (zzleYxkf39k). Surface a consequential preference or risk before defending price.
- **Emotional verdict** — telling someone what they feel, or using emotion to force compliance. Charisma on Command notes that labeling fear triggers "no, I'm not" and replaces it with a question about what might happen (yei-LUJ0Uvo). Name the observed behavior; ask about the feared outcome; state the boundary.
- **Vague assent** — accepting "I'll share," "I'll try," or "we should" as movement. The Futur shows that the agreeable conversation ends and "nothing really happens" when channel, words, owner, and timing remain unnamed (dOZkAqR_2lA).
- **Polished hindsight** — showing only the answer after uncertainty has been removed. Nathan Barry's stronger version shares while "I'm in the situation" and the story is still happening (6Kzf2kWh5gI). Keep the stuck point, failed attempt, and decision that changed the route.

# Provenance
- `zzleYxkf39k` — demonstrated fact-to-constraint-to-motive discovery and preference-led price handling.
- `mRlSb0O5QNU` — demonstrated pre-call micro-commitments, stage-specific objection handling, and live proposal dialogue.
- `Ig2zcKJQWig` — demonstrated reflective interviewing, reciprocal vulnerability, first-person disagreement, and live proof.
- `LLjpnubsOWc` — demonstrated transformation hooks, reflective reframes, artifact probes, and objection decomposition.
- `yei-LUJ0Uvo` — demonstrated need-ladder questioning, outcome-focused fear questions, recognition, and firm boundaries.
- `qh3_JJFxDmQ` — demonstrated familiar analogies, both-things-can-be-true reframes, scoped uncertainty, and audience-run tests.
- `rweBX3sO_8c` — demonstrated consequence-first openings, diagnosis before prescription, and goal/method separation.
- `_OMrvqU4Blk` — demonstrated short-line rhythm, feature-to-benefit translation, escalating proof, and low-pressure action cues.
- `6Kzf2kWh5gI` — demonstrated teaching through unresolved struggle, visible progression, and direct consequential asks.
- `o2YgHTAHYbs` — demonstrated proof-plus-tension openings, concrete follow-ups, candid objections, and thematic callbacks.
- `8HrzoEvLWH0` — demonstrated bounded questions, explicit topic bridges, brief validation, and callback closure.
- `dOZkAqR_2lA` — demonstrated customer symptom language, belief-level objections, partner-centered value, and explicit agreements.
- `j8yGn1v8OgU` — demonstrated click confirmation, time-to-value, curiosity gaps, and promise-progress-payoff cycles.
- `H2IFv_GBdUQ` — demonstrated immediate starts, progress signposts, anticipated confusion, and parallel access paths.
- `lghSjBl9yGM` — demonstrated unresolved-question openings, scene-level specificity, variable story pace, personal warmth, and takeaway landings.
- `649HhiSv0K0` — demonstrated learned-not-taught revelation, emotional range, sparse slides, concrete examples, and rehearsal discipline.
- `AxA1SvOmp1Y` — demonstrated calm-first negotiation, bonding through names, pain-point questions, bounded choices, and loss-aware change communication.
- `hU_28Q3avoQ` — demonstrated direct-to-substance openings, concrete failure probes, candid self-disclosure, practical follow-ups, and present-moment attention.
- `ygsJWeOnF1I` — demonstrated scene-first interviewing, sensory clarification, personal reflection, embodied demonstrations, and thematic callback closure.
- `rcdTQgPyzlg` — demonstrated surprising reframe openings, metaphor extension, lived-scenario probes, regulated attunement, and concept-to-practice questioning.
