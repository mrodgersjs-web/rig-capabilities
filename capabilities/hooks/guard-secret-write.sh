#!/bin/sh
# outcome: security-review:
# done_when: file:capabilities/hooks/guard-secret-write.sh || cmd:python3 scripts/hook_fires.py guard-secret-write.sh
# great_example: examples/great/security-review/guard-secret-write.sh.md
# quality_floor: 0.6
# rig guard-secret-write — PreToolUse guard for file-write tool calls.
# Canonical source: rig-capabilities repo.
#
# Blocks writes whose content contains unambiguous private credentials:
# AWS access key ids, PEM private key headers, GitHub tokens (classic+GH
# prefix), Slack tokens, Stripe live keys. Deterministic prefixes only —
# no heuristics, no false-positive sweep. Fail open on internal error.
set -u
payload=$(cat 2>/dev/null || true)
[ -n "$payload" ] || exit 0

printf '%s' "$payload" | /usr/bin/python3 -c '
import json, re, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
ti = d.get("tool_input") or {}
text = " ".join(str(ti.get(k) or "") for k in ("content", "new_string", "command", "text"))
pats = [
    r"AKIA[0-9A-Z]{16}",
    r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY( BLOCK)?-----",
    r"gh[pursr]_[A-Za-z0-9]{36,255}",
    r"xox[baprs]-[0-9A-Za-z-]{10,}",
    r"sk-(live|proj)-[A-Za-z0-9]{24,}",
    r"AIza[0-9A-Za-z_-]{35}",
]
sys.exit(1 if any(re.search(p, text) for p in pats) else 0)
' || { echo "rig-guard: blocked write — content contains a credential pattern (AWS key / PEM private key / GitHub token / Slack token / Stripe key / Google API key). Use the secret store or an env reference instead." >&2; exit 2; }
exit 0
