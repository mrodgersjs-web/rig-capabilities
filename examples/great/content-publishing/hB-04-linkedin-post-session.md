---
name: great-hB-04-linkedin-post-session-yaml
lane: content-publishing
exemplar_of: hB-04-linkedin-post-session.yaml
description: Reference exemplar for a receipt-led LinkedIn post with a bounded hook, concrete evidence, voice checks, and an anti-repeat seal.
---

# hB-04-linkedin-post-session.yaml — great example

## Input

Draft one text-only receipt post. `angle.yaml` locks pillar `receipt`, a one-sentence angle, and mode before writing. The post cites a dated tool version and measured result, uses the author's voice profile, contains no body link, and ends with one short conversation prompt rather than engagement bait.

## Output

The final post is 900–1,300 characters with line breaks every one or two sentences. Its first two lines total at most 210 characters and provide tension plus a concrete number. Hashtags are limited to registered lowercase terms; the exact hook is appended to the anti-repeat ledger.

```console
$ python3 scripts/hook_check.py "$SESS/post.md" --log ~/.rig/logs/linkedin_hooks.jsonl
# expected: exit 0; hook is strong and not a repeat of the recent pattern

$ python3 scripts/voice_fp.py "$SESS/post.md"
# expected: signature vocabulary is in band and banned-token scan is clean

$ sha256sum -c "$SESS/proof/packet.sha256"
# expected: post and angle hashes verify; hook-ledger append is present
```

## Acceptance

- Pillar and angle parse, and the receipt has at least one metric, date, or named version.
- The post contains no “comment YES,” repost bait, generic creator phrasing, or body URL.
- The final line is a single prompt at most 80 characters; hashtags number zero to three and resolve in the registry.
- The packet is sealed and the post remains a draft until a separate approved publish action.
