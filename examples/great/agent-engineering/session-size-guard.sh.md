---
name: great-session-size-guard-hook
lane: agent-engineering
exemplar_of: session-size-guard.sh
description: >-
  A transcript-size boundary fixture that emits one structured 2 MiB checkpoint warning, then proves the same tier is throttled for the same session path.
---

# session-size-guard.sh — grounded size tiers

## Input

Create a 2 MiB transcript in a temporary directory and provide its absolute path in the PostToolUse payload. Reuse the same transcript and `TMPDIR` for the second invocation so the per-session marker is observable.

## Output

```console
$ tmp="$(mktemp -d)"; truncate -s 2097152 "$tmp/demo.jsonl"; printf '{"transcript_path":"%s"}' "$tmp/demo.jsonl" | TMPDIR="$tmp" bash capabilities/hooks/session-size-guard.sh
{"systemMessage":"🟠 Session transcript 2MB (>2MB). Checkpoint soon and plan a fresh session before it snowballs (mega-sessions were the coach audit's top finding).","suppressOutput":true}
$ printf '{"transcript_path":"%s"}' "$tmp/demo.jsonl" | TMPDIR="$tmp" bash capabilities/hooks/session-size-guard.sh
```

The second invocation is intentionally silent: tier `2` is already stored in `claude-sessguard-demo.jsonl.tier`.

## Acceptance

- A transcript below 2 MiB emits nothing and exits 0.
- The first 2 MiB crossing emits valid JSON with `suppressOutput: true`; a repeat at that tier emits nothing.
- Growing the same transcript to 5 MiB emits the red fresh-session message exactly once.
