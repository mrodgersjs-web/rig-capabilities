# Wound Classifier — Behavior Spec (v3; executable in v6)

Spec only. The executable classifier ships in v6 (rig_comm engine integration);
until then an agent follows this procedure literally.

## Input

An audience description (persona, vertical, segment) OR an inbound message
(email, DM, comment) to classify before replying.

## Output

1. **Ranked wound ids** with scores, drawn from the wounds defined in
   `../wounds/core-wounds.md`: currently exported: **W3 "I'm Going to Be
   Abandoned", W4 "I'm Invisible", W5 "I'm Stupid / I Don't Know Enough",
   W6 (attachment-anxiety fragment), W8 root ("I will die and nothing I do
   might matter" — Terror Management section, flipped by E7 "I Matter")**.
   W1/W2/W7 are NOT in the exported corpus — never emit them (see SKILL.md
   export honesty).
2. **Depth layer** — one of Layers 1–3 (Rational → Behavioral Triggers →
   Identity Architecture; Layers 4–5 are named in the source card but its body
   truncates at Layer 3, so classify to Layer 3 maximum and say so when the
   evidence points deeper). Buyer-depth calibration uses the 0σ→10σ ladder in
   `../wounds/depth-layers.md` (Deviation Scale Doctrine).
3. **Recommended reply strategy** — one of: mirror-first (oxytocin/E1),
   selectivity-reversal (E2), legacy-flip (E7 from W8), safety-first (E6), or
   straight WMAQO sequence (`../sequences/wmaqo.md`) for cold outbound.
4. **One-paragraph justification** — REQUIRED; names the textual/behavioral
   evidence for the wound ranking and the layer.

## Method (ordered)

1. **bx-need-architect need-hierarchy first.** Build the need stack for the
   input: functional need → emotional need → social need; identify which need
   is unmet and whose absence the input is compensating for (the card's Five
   Whys chain is the worked template).
2. **Wound match second.** Map the unmet need onto the exported wounds by the
   wound's documented Origin/How-it-shows-up fields (e.g. posting-constantly +
   engagement-desperation → W4; reassurance-seeking + fear of being dropped →
   W3; over-researching + fear of looking dumb → W5; status-signalling → W8-adjacent).
   Rank, do not pick-one: emit up to 3 with scores.
3. **Layer assignment.** Rational-only language → Layer 1 (rarely actionable);
   trigger-reactive language ("everyone says", comparisons) → Layer 2;
   identity claims ("I'm the kind of person who…") → Layer 3.
4. **Strategy selection.** The top wound's documented flip (W→E) sets the
   reply strategy; email inbound additionally scores the draft against
   `../gates/email-reply-scoring.md` before sending (Gate-D applies).
5. **Refusal case.** If the input is purely Layer 1 with no emotional trace,
   the classifier must return "no wound claim — write at mechanism level"
   rather than manufacturing pathos.

## Done-test (for the v6 executable)

Classify the 5 seed cases (one per exported wound + one Layer-1-only): correct
wound ranking on 4/5, Layer-1-only case returns the refusal, every output
carries a non-empty justification paragraph. A run that emits W1/W2/W7 is auto-RED.
