---
name: great-guard-secret-write-hook
lane: security-review
exemplar_of: guard-secret-write.sh
description: >-
  A paired content fixture showing that environment references remain writable while a syntactically valid fake credential is blocked with the PreToolUse exit contract.
---

# guard-secret-write.sh — secret content boundary

## Input

Exercise the write-content fields the hook actually reads. The first payload contains only an environment lookup. The second contains the reserved fake AWS shape `AKIAABCDEFGHIJKLMNOP`; it is test data, not a credential.

## Output

```console
$ printf '%s' '{"tool_input":{"content":"API_KEY=${API_KEY}"}}' | sh capabilities/hooks/guard-secret-write.sh; echo "rc=$?"
rc=0
$ printf '%s' '{"tool_input":{"content":"AWS_KEY=AKIAABCDEFGHIJKLMNOP"}}' | sh capabilities/hooks/guard-secret-write.sh; echo "rc=$?"
rig-guard: blocked write — content contains a credential pattern (AWS key / PEM private key / GitHub token / Slack token / Stripe key / Google API key). Use the secret store or an env reference instead.
rc=2
```

Malformed JSON and empty input fail open so the hook cannot brick file tooling; deterministic credential prefixes fail closed.

## Acceptance

- The environment-reference fixture exits 0.
- The fake credential fixture exits 2 and emits `blocked write` on stderr.
- `python3 scripts/hook_fires.py guard-secret-write.sh` exits 0 against the repository fixture set.
