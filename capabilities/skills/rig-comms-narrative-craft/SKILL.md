---
name: rig-comms-narrative-craft
description: Screenplay craft translated into message engineering — dramatic question, stakes clarity, environmental exposition, arc sequencing, expectation play. Distilled from 25 full-transcript episodes (Lessons from the Screenplay, StudioBinder). Use when drafting or critiquing any consequential business message (email, LinkedIn, proposal, announcement).
outcome: messages structured the way audiences process stories — one open question, concrete stakes, embedded exposition, theme-held variation — instead of feature-list prose
done_when:
  - file:capabilities/skills/rig-comms-narrative-craft/SKILL.md
  - grep:capabilities/skills/rig-comms-narrative-craft/SKILL.md:dramatic question
  - grep:capabilities/skills/rig-comms-narrative-craft/SKILL.md:9f0_Liz5_XM
  - cmd:python3 -c "import json; m=[json.loads(l) for l in open('data/corpora/writing-craft/manifest.jsonl')]; assert len(m)==25; ids={r['video_id'] for r in m}; body=open('capabilities/skills/rig-comms-narrative-craft/SKILL.md').read(); cited={i for i in ids if i in body}; assert len(cited)>=8, cited; print('OK', len(cited))"
quality_floor: 0.65
great_example: capabilities/skills/rig-comms-narrative-craft/SKILL.md
metadata:
  source_corpus: data/corpora/writing-craft (25 transcripts, sha256-verified manifest)
---

# rig-comms-narrative-craft

Nine patterns, each present in ≥2 transcripts of the wave-1 corpus (video_ids cited; the
manifest in `data/corpora/writing-craft/manifest.jsonl` hashes every transcript).

## P1 — The dramatic question IS the hook
McKee via LFTS: "Hunger for the answer to the Major Dramatic Question grips the audience's
interest, holding it to the last act's climax... the dramatic question is the hook, the engine"
(9f0_Liz5_XM). In The Dark Knight "all three story threads in the crosscut sequence directly
relate to this question: will the Joker win the battle for Gotham's soul?" (Xaw9f1ujDnA).
**Comms translation:** one message = one open question stated in the first two lines. Every
paragraph must visibly relate to that question; delete anything that doesn't. Before sending,
name the question the recipient now holds; if you can't, the message has no engine.

## P2 — Stakes must be pinned per thread
"To keep the audience invested in the trial's outcome, A Few Good Men must first establish
crystal-clear and compelling stakes" (MoCQPEh3MyI); Inception crosscutting "creates suspense
because the audience understands what's at stake in each line of action... the stakes are
absolutely clear: if he takes control of that ship, we're dead" (Xaw9f1ujDnA). Where "the
stakes are trickier to pin down" (Murph's thread) the tension measurably drops (Xaw9f1ujDnA).
**Comms translation:** every ask names its concrete loss/gain ("if this slips past Friday we
lose the December board slot"), never a category ("important", "urgent"). If a number exists,
use it.

## P3 — Exposition goes into the environment, not the lecture
"Minority Report weaves in exposition about Precrime in several environmental ways, from
showing advertisements being broadcast in the city" plus the clueless-character device:
"introducing a character who is as clueless about the story world as the audience"
(QbMPjas_rRU).
**Comms translation:** background arrives as artifact — a 30-second case clip, a screenshot,
a dated result — not as a paragraph of context. When you must explain, route it through a
persona asking the reader's naive question.

## P4 — Arc: flaw → inciting opportunity → midpoint reversal → completion
The arc engine: flawed character introduced "resistant to change," forced "into extreme and
opposite positions at the midpoint," arc completed by demonstrated change (3p_H2FxuOWs);
"the inciting incident of the film makes his want even more specific — the chance to play
with jazz legend Dorothea Williams" (SM3IQFgP-d8).
**Comms translation:** multi-touch sequences are arcs, not reminders. Touch 1 names the gap
(their flaw), touch 2 arrives with a dated specific opportunity (the inciting incident),
mid-sequence touch flips the frame (new evidence, named-peer result), final touch shows
completion state. Each touch's CTA = who they become, not what you sell.

## P5 — Thesis / antithesis / synthesis argument shape
"Act One: Thesis. Act Two: Antithesis. Act Three: Synthesis... Act One establishes a flawed
character, Act Two confronts them with their opposite" (3p_H2FxuOWs, quoting Yorke).
**Comms translation:** long-form = state their current model (thesis), confront its strongest
counter-fact (antithesis), deliver the reframe as resolution (synthesis). Never argue with
someone whose position you haven't stated in their words first.

## P6 — Hold theme, play expectation on treatment
"They want you to surprise their expectations but what they're really coming back for is
they love the theme of that story" and Cameron on Aliens: a response "totally opposite from
what we got the first time... you've got to do that, especially in a sequel" (-LDXBGgs1QI,
4x9mplwN3Lo).
**Comms translation:** recurring series keep the theme constant and invert the angle every
installment (last email warned loss, this one shows gain). The follow-up that repeats the
treatment trains delete.

## P7 — Earn investment before spectacle
Act One of the Infinity Saga is "all about exposition — we get to know our characters" BEFORE
the spectacle pays off (3p_H2FxuOWs); trial suspense works only "because we
understand what's at stake for all the characters involved, and the values each side is
fighting for" (MoCQPEh3MyI).
**Comms translation:** demo, pricing deck, and feature list come only after the reader is
invested (question open + stakes pinned). Leading with spectacle on a cold reader is Act
Three first.

## P8 — Specific subtext beats stated intent
Mad Men's pitch room "presents the specific subtext he envisions for this campaign" as the
tool — the ad's meaning lives under the line (uQ1Rbdi189w); characters whose "personality
causes her to clash with people's expectations" carry theme without stating it (LlVLOtD6Mv8).
**Comms translation:** let one concrete detail carry the claim (the client's before/after
number) and keep the literal ask plain. Adjectives assert; specifics subtext.

## P9 — Economy: every element is load-bearing
The dramatic question "keeps Before Sunset engaging" scene to scene — nothing exists that
doesn't feed it (9f0_Liz5_XM); crosscut threads exist only because each "directly relates to
this question" (Xaw9f1ujDnA).
**Comms translation:** the edit test: delete any sentence that neither opens the question,
pins a stake, nor advances the ask. Length is not a virtue; latency to the first
stake-relevant word is the metric.

# Anti-patterns (named in the corpus)
- **Formula cosplay** — "you save the cat and they think that's all I need... these books are fine for beginners but they have very few practical story techniques" (-LDXBGgs1QI). Beat-sheet compliance is not craft; a message passing a template but opening no question is dead.
- **Chasing the hot genre** — "you cannot predict the market... don't ever write genres because you think they're the hot genre" (-LDXBGgs1QI). Don't angle a message to the trending format; angle it to the recipient's question.
- **On-the-nose** — dialogue/claims that state their own meaning ("so on the nose") register as propaganda; specifics + plain ask instead (l9jUcTFN3Ww, uQ1Rbdi189w).
- **Unpinned stakes** — threads where "the stakes are trickier to pin down" lose tension (Xaw9f1ujDnA). Vague urgency reads as noise.
- **Unearned setup** — hero "set up by some guy you don't know or even care about for reasons that aren't at all clear" (QbMPjas_rRU). A CTA whose mechanics depend on unexplained machinery gets deleted, not clarified.
