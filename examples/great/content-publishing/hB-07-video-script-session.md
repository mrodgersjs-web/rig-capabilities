---
name: great-hB-07-video-script-session-yaml
lane: content-publishing
exemplar_of: hB-07-video-script-session.yaml
description: Reference exemplar for a runtime-bounded video script with a cold open, beat-map bijection, rehooks, visuals, source binding, and CTA placement.
---

# hB-07-video-script-session.yaml — great example

## Input

Write an eight-minute tutorial script using a declared 150 words per minute. `format.yaml` locks the format, runtime, and rate; `beats.yaml` names the hook, four teaching beats, their viewer questions, and payoff before prose begins. Research entries support every statistic and dated claim.

## Output

The script opens directly on payoff/tension within its first 60 spoken words, maps every section to exactly one beat, stays within ten percent of target runtime, and includes a rehook every 60–90 seconds. Visual notes cover each beat and on-screen demo action; one CTA appears in the final ten percent.

```console
$ python3 scripts/cold_open.py "$SESS/script.md"
# expected: exit 0 and no welcome-back, channel-meta, or subscription opener

$ python3 scripts/beat_map.py "$SESS/beats.yaml" "$SESS/script.md"
# expected: one-to-one beat/section mapping with no missing viewer question

$ python3 scripts/runtime_math.py "$SESS/script.md" "$SESS/format.yaml" --tol 0.10
# expected: exit 0 and proof/runtime.json records estimated duration
```

## Acceptance

- Cold open, beat-map bijection, and runtime math pass by command.
- Rehook intervals are 60–90 seconds and each relevant spoken claim has a `[VISUAL:]` note.
- Speakability limits sentences to 25 words, and all statistics resolve in `research.yaml`.
- Script, beats, runtime proof, and research pass `sha256sum -c $SESS/proof/packet.sha256`.
