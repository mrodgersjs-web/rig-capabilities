---
name: great-guard-dangerous-commands-hook
lane: agent-engineering
exemplar_of: guard-dangerous-commands.sh
description: >-
  A paired allow-and-deny fixture proving that ordinary inspection passes while an unmanaged worktree creation payload is rejected before any shell command executes.
---

# guard-dangerous-commands.sh — deterministic command denial

## Input

Feed the PreToolUse JSON payload itself to the hook; do not run the command contained in the payload. One case is read-only, and one is the exact unmanaged-worktree-add shape governed by Law L2.

## Output

```console
$ printf '%s' '{"tool_input":{"command":"git worktree list"}}' | sh capabilities/hooks/guard-dangerous-commands.sh; echo "rc=$?"
rc=0
$ printf '%s' '{"tool_input":{"command":"git -C /work/repo worktree add /tmp/reviewer HEAD"}}' | sh capabilities/hooks/guard-dangerous-commands.sh; echo "rc=$?"
rig-guard: blocked — git worktree add is blocked (unmanaged-worktree-add); materialise verifier trees with git archive | tar. Refine the command or run it manually.
rc=2
```

The second command is inert test data. The hook extracts `tool_input.command`, matches the canonical global-option form, and emits the reason on stderr.

## Acceptance

- The allow fixture exits 0 with no block text.
- The denial fixture exits 2 and names `unmanaged-worktree-add`.
- `python3 scripts/hook_fires.py guard-dangerous-commands.sh` exits 0, covering the hook's registered trigger fixture.
