---
name: great-goal-loop-startup-hook
lane: agent-engineering
exemplar_of: goal-loop-startup.sh
description: >-
  A session-start fixture that renders the goal-loop chooser even when the optional local specification tree is absent, while keeping boot-pack work best-effort and asynchronous.
---

# goal-loop-startup.sh — fail-soft session injection

## Input

Start the hook under an empty temporary HOME. This deliberately removes `~/.hermes/skills/goal-loop/yaml-specs` and the optional `bin/rig-boot-pack`, isolating the banner contract from machine state.

## Output

```console
$ tmp="$(mktemp -d)"; HOME="$tmp" bash capabilities/hooks/goal-loop-startup.sh
╔══════════════════════════════════════════════════════════╗
║  GOAL LOOP ACTIVE — ? loops loaded                     ║
...
║  /goal-loop         → Run any of 73 loops                ║
║  /fix-this          → Fix something broken                ║
...
```

The missing YAML tree resolves the count to `?` through the hook's fallback; it does not suppress the usable loop menu or fail the session. If `~/Developer/rig-capabilities/bin/rig-boot-pack` is executable, the hook launches it silently with a five-second cap where `timeout` exists.

## Acceptance

```console
$ python3 scripts/hook_fires.py goal-loop-startup.sh
```

The fixture exits 0, stdout contains `GOAL LOOP ACTIVE`, `/goal-loop`, and `/command-registry`, and a missing optional boot pack produces no error on stderr.
