---
name: great-what-great-looks-like
lane: agent-engineering
source: canonical-curated
exemplar_of: what-great-looks-like
description: "Reference exemplar for applying the 36-hour sprint quality contract cycle by cycle, with one declared upgrade, inspectable proof, and fail-closed issue handling."
---

# What great looks like: lead-engine cycle four

## Input

Read the prior lead-engine state, select cycle four's single upgrade—reply-history feedback in ICP weights—and run the lead batch without changing another lane. Stage at least 50 real leads with `predicted_p_reply`, keep every packet dormant, and test the blocked-prospect list before reporting.

```console
$ python3 scripts/assert_loop_termination.py capabilities/loops/what-great-looks-like.md
```

## Output

The loop contract validates. The cycle writes its artifact, proof hash, counters, applied-upgrade name, and next-upgrade note before scoring against the WGLL-A checklist. The report states real lead and blocklist counts and can be checked from paths in under 30 seconds. Missing proof skips advancement; a near-miss is quarantined; a blocked touch, fabricated public claim, unauthorized send, or unapproved spend stops the mission instead of being auto-healed.

## Acceptance

- The command exits 0.
- At least 50 leads are staged, every lead has an ICP score and `predicted_p_reply`, and blocklist hits are zero.
- Exactly one cycle-map upgrade is applied and named in the proof packet.
- GREAT, GOOD, and BAD are assigned from recorded checklist evidence, never tone; no outcome is called complete without an inspectable artifact and proof.
