---
name: great-hB-13-email-sequence-session-yaml
lane: revenue-gtm
exemplar_of: hB-13-email-sequence-session.yaml
description: Reference exemplar for a trigger-bound email sequence with justified cadence, honest escalation, suppression, compliance, clean fallbacks, and sealed evidence.
---

# hB-13-email-sequence-session.yaml — great example

## Input

Create a five-email nurture sequence entered by a lead-magnet download and exited by conversion or suppression. `sequence.yaml` locks trigger, exit conditions, goal, delays, and unique roles: deliver, teach, story, proof, offer. Customers and active opportunities must be suppressed before any automation is staged.

## Output

Each email is 75–200 words with one CTA, two subject candidates, a justified 1–7 day delay, tagged reachable links, compliance footer, and a plain-text twin. Every merge tag has a fallback. `suppression.yaml` maps lists and the early-exit field to actual ESP fields.

```console
$ python3 scripts/ladder_check.py "$SESS/sequence.yaml" --min 4 --max 7
# expected: five emails, non-repeating roles except proof, and a declared goal

$ python3 scripts/email_format.py "$SESS/emails/" --min-words 75 --max-words 200 --max-ctas 1
# expected: every email remains inside the format band

$ python3 scripts/merge_fallback.py "$SESS/emails/" --render-empty
# expected: empty contact data leaves zero raw merge tokens
```

## Acceptance

- Cadence validation passes or any out-of-band delay has a written reason.
- Subjects have no fake `re:`/`fwd:` prefixes or spam tokens; links resolve and carry the sequence UTM campaign.
- Every message includes unsubscribe and sender address, with a corresponding `.txt` file.
- Suppression/early exit map cleanly, the packet checksum passes, and the sequence remains unsent.
