---
name: great-tac-plan-gate-hook
lane: agent-engineering
exemplar_of: tac-plan-gate.sh
description: >-
  An opt-in plan boundary proving ordinary sessions remain untouched while enforced Write/Edit sessions fail closed when the TAC plan gate is unavailable or red.
---

# tac-plan-gate.sh — opt-in edit admission

## Input

Run two empty PreToolUse payloads. The first leaves enforcement disabled. The second enables `RIG_TAC_ENFORCE` under an empty temporary HOME, guaranteeing that the expected `~/.rig/tac/bin/tac plan-gate` executable is unavailable.

## Output

```console
$ printf '{}' | RIG_TAC_ENFORCE=0 bash capabilities/hooks/tac-plan-gate.sh; echo "rc=$?"
rc=0
$ tmp="$(mktemp -d)"; printf '{}' | HOME="$tmp" RIG_TAC_ENFORCE=1 bash capabilities/hooks/tac-plan-gate.sh; echo "rc=$?"
[TAC plan-gate] BLOCKED Write/Edit: no valid plan. Run /tac-plan or: tac init-plan && tac plan-gate
python3: can't open file '.../.rig/tac/bin/tac': ...
rc=2
```

The disabled case performs no plan lookup. The enforced case reports the recovery command and rejects the edit instead of treating missing gate machinery as green.

## Acceptance

- `RIG_TAC_ENFORCE=0` exits 0.
- With enforcement enabled, a missing or red `python3 "$HOME/.rig/tac/bin/tac" plan-gate` exits 2 and prints `BLOCKED Write/Edit`.
- A real TAC executable returning 0 admits the edit without warning.
