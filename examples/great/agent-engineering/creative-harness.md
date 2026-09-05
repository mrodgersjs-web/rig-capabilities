---
name: great-creative-harness
lane: agent-engineering
source: canonical-curated
exemplar_of: creative-harness
description: "Reference exemplar for a channel-correct creative artifact that survives brand, voice, originality, licensing, accessibility, and public-release gates."
---

# Creative loop: dormant LinkedIn image post

## Input

Produce a 16:9 LinkedIn draft from a locked brief using the declared RIG palette, typography, and Mike voice profile. Use an original or generated visual with recorded provenance, no text baked into the image, and no public release.

```console
$ python3 scripts/assert_loop_termination.py capabilities/loops/creative-harness.md
```

## Output

The loop contract validates. The artifact is recognizable without a logo, contains a specific operator-level angle, and uses no banned AI phrasing. Its scorecard reports anti-generic score 89, zero AI-isms, correct channel dimensions, readable mobile composition, accessibility basics, and a provenance entry for every visual. The proof packet names brief, format, channel, word count, per-gate evidence, verdict, and hash. Gate-D evidence says `gated artifact, not published`.

## Acceptance

- The command exits 0.
- Anti-generic score is at least 85, voice audit has zero AI-isms, and one non-commodity insight is explicit.
- Visual assets are real and licensed, generated, or attributed; no placeholder description stands in for an image.
- Nothing is published, and any use of Mike's image remains blocked pending approval for that exact use.
