#!/bin/sh
# outcome: agent-engineering:
# done_when: cmd:python3 scripts/hook_fires.py guard-dangerous-commands.sh
# great_example: examples/great/agent-engineering/guard-dangerous-commands.md
# quality_floor: 0.6
# rig guard-dangerous-commands — PreToolUse guard for shell tool calls.
# Canonical source: rig-capabilities repo. Installed copies are wired via hook config.
#
# Contract (Claude Code / Codex / Hermes PreToolUse): JSON payload on stdin.
# Exit 2 + stderr message = block the call. Exit 0 = allow. Internal errors
# FAIL OPEN (never brick the fleet); blocks are deterministic pattern matches only.
#
# Blocks: irreversible recursive/system deletes, raw device writes, filesystem
# destruction, forced pushes to default branches, destructive git resets with
# clean, and unmanaged `git worktree add` (Law L2: verifier trees are
# materialised with `git archive <sha> | tar -x`, never agent-created
# checkouts). Read-only worktree inspection (list/remove/prune/status) passes.
# Everything else passes.
#
# Parity: rig_capabilities/gate_d.py is the source of truth; every regex below
# mirrors DANGEROUS_COMMAND_RULES (plus its sudo-rm special case) verbatim,
# and tests.fable2031_dispatch.WorktreeDenialParityTests re-executes this hook
# against gate_d's verdicts.
set -u
payload=$(cat 2>/dev/null || true)
[ -n "$payload" ] || exit 0

# One embedded pass: extract the shell command from the payload, then apply the
# deterministic deny patterns. Any internal error exits 0 (fail open).
printf '%s' "$payload" | /usr/bin/python3 -c '
import json, re, sys

GENERIC = "command matches a deterministic irreversible-destruction pattern"
checks = [
    (r"\bsudo\b.*\brm\b", None, "sudo rm is not permitted from agent tool calls"),
    (r"\brm\s+(-[a-zA-Z]*\s+)*-[a-zA-Z]*r[a-zA-Z]*f|\brm\s+(-[a-zA-Z]*\s+)*-[a-zA-Z]*f[a-zA-Z]*r", r"(?<![\w/])/(?=\s|$|\*)|(?<![\w])~(?![A-Za-z0-9_-])|(?<![\w])~/|\$HOME(?![A-Za-z0-9_])|\b(usr|etc|sys|boot|var|Library)\b", GENERIC),  # rm -rf with root/home/system target
    (r"\bmkfs(\.\w+)?\b", None, GENERIC),
    (r"\bdd\b[^\n]*\bof=/dev/(disk|rdisk|nvme|sd|hd)", None, GENERIC),
    (r">\s*/dev/(disk|rdisk|nvme\d|sd[a-z]|hd[a-z])", None, GENERIC),
    (r"\bgit\s+push\b[^\n]*(--force(?!-with-lease)|-f)\b[^\n]*\b(main|master)\b", None, GENERIC),
    (r"\bgit\s+push\b[^\n]*\bmain\b[^\n]*(--force(?!-with-lease)|-f)\b", None, GENERIC),
    (r"\bgit\s+reset\b[^\n]*--hard[^\n]*\s~/|\bgit\s+clean\b[^\n]*-[a-zA-Z]*f[a-zA-Z]*x", None, GENERIC),
    (r"\bchmod\s+-[a-zA-Z]*R[a-zA-Z]*\s+7{3,4}\s+/(?:\s|$)", None, GENERIC),
    (r":\(\)\s*\{.*\|.*&\s*\};\s*:", None, GENERIC),  # fork bomb
    # unmanaged-worktree-add (Law L2, deny-only): catches `git worktree add`
    # with the real global-option prefixes (-C, -c, --git-dir, --exec-path,
    # --work-tree, --namespace, --no-optional-locks); no `wt` alias exists in
    # any git config surface, so none is matched.
    (r"\bgit\b(?:\s+(?:-C\s+\S+|-c\s+\S+|--git-dir[=\s]\S+|--exec-path[=\s]\S+|--work-tree[=\s]\S+|--namespace[=\s]\S+|--no-optional-locks))*\s+worktree\s+add\b", None, "git worktree add is blocked (unmanaged-worktree-add); materialise verifier trees with git archive | tar"),
]
try:
    d = json.loads(sys.stdin.read() or "{}")
    ti = d.get("tool_input") or {}
    c = ti.get("command") or ti.get("cmd") or ""
    if not c:
        sys.exit(0)
    for sweep, target, why in checks:
        if re.search(sweep, c) and (target is None or re.search(target, c)):
            sys.stderr.write("rig-guard: blocked — " + why + ". Refine the command or run it manually.\n")
            sys.exit(2)
except SystemExit:
    raise
except Exception:
    sys.exit(0)
sys.exit(0)
'
exit $?
