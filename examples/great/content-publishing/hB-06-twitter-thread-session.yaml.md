---
name: great-hB-06-twitter-thread-session-yaml
lane: content-publishing
exemplar_of: hB-06-twitter-thread-session.yaml
description: Reference exemplar for an atomic X thread whose opening contract, payoff, link placement, media, and repetition checks are machine-verifiable.
---

# hB-06-twitter-thread-session.yaml — great example

## Input

Draft an eight-post data-drop thread. `arc.yaml` declares the arc, payoff, and tweet count. The first post promises the result without “A thread” filler or a link; the penultimate post delivers the payoff; the last post recaps and offers one follow/reply prompt.

## Output

Every numbered block contains one standalone idea and stays at or below 280 characters. A sourced number appears in the evidence post. Links are absent from posts 1–7 and may appear only in post 8 or a declared reply. Any image meets the permitted dimensions and has paired alt text.

```console
$ python3 scripts/t1_check.py "$SESS/thread.md"
# expected: tweet 1 is <=280 characters, contains tension/payoff, and has no filler or link

$ python3 scripts/thread_atom.py "$SESS/thread.md"
# expected: every block passes length, numbering, atomicity, and anaphora checks

$ python3 scripts/payoff_check.py "$SESS/arc.yaml" "$SESS/thread.md"
# expected: the declared payoff appears by the penultimate tweet
```

## Acceptance

- Thread count is between five and twelve and matches `arc.yaml`.
- No link appears before the final tweet; evidence is concrete for the data arc.
- Banned-token and repeated-opener checks pass; attached media size, dimensions, and alt-text count agree.
- Thread, arc, and asset hashes verify, and tweet 1 is logged in the anti-repeat ledger.
