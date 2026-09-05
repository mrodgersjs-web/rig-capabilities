---
name: great-jake-pushback-hook
lane: agent-engineering
exemplar_of: jake-pushback.sh
description: >-
  A machine-isolated pushback run proving non-mutating tools bypass the gate while a secret-path write is hard-blocked and logged without consuming a fabricated approval.
---

# jake-pushback.sh — layered write enforcement

## Input

Use a temporary HOME so the test neither reads live harness state nor writes the user's override ledger. Send one `Read` payload and one `Write` targeting `config/.env`; no approval-token file is created.

## Output

```console
$ tmp="$(mktemp -d)"; printf '%s' '{"tool_name":"Read","session_id":"demo","tool_input":{"path":"README.md"}}' | HOME="$tmp" bash capabilities/hooks/jake-pushback.sh; echo "rc=$?"
rc=0
$ tmp="$(mktemp -d)"; printf '%s' '{"tool_name":"Write","session_id":"demo","tool_input":{"file_path":"config/.env"}}' | HOME="$tmp" bash capabilities/hooks/jake-pushback.sh; echo "rc=$?"
🛑 JAKE HARD BLOCK — secret_file_guard (Juno/security council)
Target: config/.env
...
rc=1
```

The blocked fixture appends one `outcome: blocked` JSONL record under the temporary `~/.rig/state`; it never creates or consumes an approval token.

## Acceptance

- Non-mutating tools exit 0 without changing a counter.
- Secret-bearing paths exit 1, name the target, and produce one blocked ledger event.
- A one-time override is accepted only when the corresponding reason-coded token already exists; that separate path is not exercised by this no-approval fixture.
