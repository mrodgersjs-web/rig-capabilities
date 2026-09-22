# Voice Fingerprint v2 (locked)

v1 sources merged: rig-voice-engineering (7-axis scorecard),
content-voice-fingerprint-extractor (quantification procedure), voice-builder
(interview schema). Deterministic enforcement lives in
`rig-communications-core/rig_comms/voice.py` — this file is the human-readable
mirror; the code is canonical.

## Axis 1 — hard-banned words (any hit = BLOCK)
`unlock`, `empower`, `seamless`, `game-changer`, `game changer`, `disruptive`, `determination`, `get started`, `learn more`, `thought leader`, `AI strategist`, `delve`, `unlocking`, `in today's fast-paced`, `revolutionize`, `harness the power`

## Axis 2 — signature vocab, per 1,000 words (min, target, max)
| word | min | target | max |
|---|---|---|---|
| median | 0 | 3–5 | 12 |
| deviation | 0 | 2–4 | 8 |
| production | 0 | 2–3 | 6 |
| operator | 0 | 3–5 | 10 |

Above max anywhere = over-stuffed (reads forced). Zero is legal off-topic.

## Axis 3 — sentence-length distribution bands
- short_1_7: 15–25%
- medium_8_18: 40–50%
- long_19_28: 25–35%
- architectural_29_plus: 5–10%

## Axis 4 — paragraphs
Max 4 sentences per paragraph — hard FAIL. Average 2–3 short-form, 2–4 long-form.

## Axis 5 — hook (heuristic in code; agent confirms)
Specific signal (number, quote, named concrete noun — not a generic label) in the
first 8 words; disqualifies the wrong audience; earns the click without bait;
operator-coded, not academic.

## Axes 6–7 — agent judgement, never machine PASS
Manifesto beats: median is the enemy; creativity is the gap; deviation is the answer; production is the proof. Cadence: read-aloud rhythm,
earned transitions, hard close (never "subscribe for more").

## Wound authenticity (hard)
Allowed: W3, W4, W5, W6, W8. FORBIDDEN (manufactured pain = red): W1, W2, W7.
Library and provenance: rig-communications-wounds.
