# Voice: fingerprint, register map, drift

Sub-skill of lv-strategy. A voice profile is a measurable artifact, not a vibe. Two outputs: a
quantified fingerprint the gates can score against, and a short human-readable profile other skills
(idea generation, matrix building) can read. Confidence in "sounds right" is not evidence; the
calibration sentences are.

## Build procedure

1. Collect 5 or more real writing samples, at least 2,000 words in total. Published posts, emails,
   essays, newsletter issues. Minimum 3 samples to detect anything; below that, ask for more.
2. Run a short interview alongside the samples: name and role, who the reader is, the 3-5 topics to
   be known for, the contrarian belief, the one thought to own in the reader's head, and one topic
   never to write about. Short blunt answers are fine. One follow-up round at most.
3. Compute the fingerprint (below) from the samples only.
4. Write the profile pair: a short about file (who the writer is, audience, pillars, point of view,
   brand promise, off-limits topics; under 300 words) and one integrated voice file covering how the
   voice writes and what it avoids. Keep the voice file under 500 words.
5. Score 5 freshly generated sentences against the fingerprint as the calibration test. If the
   generated sentences cannot be told apart from generic prose, the fingerprint is not doing work.
6. Map registers per lane and lock the fingerprint. Later drafts are drift-checked against it.

## Fingerprint contents (quantified)

| axis | measure |
|---|---|
| sentence rhythm | mean, standard deviation, and the short-to-long sentence ratio |
| signature vocabulary | words at 3x or more of baseline frequency, stopwords excluded, each with its count |
| banned words | words common in the genre that never appear in the samples |
| punctuation habits | em dashes, colons, fragments, question marks per 100 sentences |
| structure | paragraph length, list usage, question usage, opening patterns, closing patterns |
| hooks | the 3-5 opening types the samples actually use, each with one real example |

## Absence signals (the part people skip)

Every "never does" claim must be an observed gap across the whole sample set: zero em dashes in five
samples, no rhetorical questions anywhere, no tricolons, no motivational closing. Name the count.
A prohibition with no sample evidence is a preference, and belongs in the interview answers instead.

## Register map (one fingerprint, many surfaces)

- Lane A: warm, story-first, pop-culture opening allowed; the cast rules travel with it.
- Lane B: evidence-first, mechanism-level, receipts named; no mascots, no banned words.
- Ideawake client lane: Coby's voice, trained from Coby's samples; Mike's fingerprint never applies.
- Job lane: plain credential-forward register; humor only when the samples show it.

## Drift check

Before anything ships, score the draft against the locked fingerprint and against the last approved
draft. A drift finding is an action, not a dashboard: rewrite the offending sentences or escalate.
Deterministic scoring and drift detection run through the tool listed in the parent SKILL.md.

## Brand-voice outcome contract

The brand must be recognizable everywhere: a voice model with style guidelines, tone matching, and
quality scoring is the target state; inconsistent voice is the baseline being fixed. Finished copy
should fail a blind test of "which brand wrote this" when the fingerprint is not applied, and pass it
when it is.

## Checks before a voice profile ships

- Rhythm stats and at least 10 signature words with frequencies are present.
- Every absence claim names what the samples never do.
- The 5-sentence calibration is scored, not asserted.
- Per-lane registers are separate; no lane inherits another's voice.
- Nothing in the profile was invented to fill a section.

Absorbed from: content-voice-fingerprint-extractor, voice-builder, rig-top100-brand-voice, rig-communications-voice.
