"""V31: Gate-D evaluate() as a stdlib library.

HEADLESS.md step 3: promote the demo callback's decision table into a
shared importable module so every headless runner shares one rule set
with the house hooks. This module has ZERO SDK dependency — `evaluate`
is the source of truth; the SDK wrapper stays in examples/.
"""
from __future__ import annotations

import json
import re
from typing import Any

# Mirrors capabilities/hooks/guard-dangerous-commands.sh
DANGEROUS_COMMAND_RULES: list[tuple[str, str, str | None]] = [
    (
        "rm-rf-root-or-home",
        r"\brm\s+(-[a-zA-Z]*\s+)*-[a-zA-Z]*r[a-zA-Z]*f|\brm\s+(-[a-zA-Z]*\s+)*-[a-zA-Z]*f[a-zA-Z]*r",
        r"(?<![\w/])/(?=\s|$|\*)|(?<![\w])~(?![A-Za-z0-9_-])|(?<![\w])~/|\$HOME(?![A-Za-z0-9_])|\b(usr|etc|sys|boot|var|Library)\b",
    ),
    ("mkfs", r"\bmkfs(\.\w+)?\b", None),
    ("dd-to-device", r"\bdd\b[^\n]*\bof=/dev/(disk|rdisk|nvme|sd|hd)", None),
    ("redirect-to-device", r">\s*/dev/(disk|rdisk|nvme\d|sd[a-z]|hd[a-z])", None),
    ("force-push-main", r"\bgit\s+push\b[^\n]*(--force(?!-with-lease)|-f)\b[^\n]*\b(main|master)\b", None),
    ("force-push-main-2", r"\bgit\s+push\b[^\n]*\bmain\b[^\n]*(--force(?!-with-lease)|-f)\b", None),
    ("destructive-git", r"\bgit\s+reset\b[^\n]*--hard[^\n]*\s~/|\bgit\s+clean\b[^\n]*-[a-zA-Z]*f[a-zA-Z]*x", None),
    ("chmod-r-777-root", r"\bchmod\s+-[a-zA-Z]*R[a-zA-Z]*\s+7{3,4}\s+/(?:\s|$)", None),
    ("fork-bomb", r":\(\)\s*\{.*\|.*&\s*\};\s*:", None),
]

# Mirrors capabilities/hooks/guard-secret-write.sh
SECRET_RULES: list[tuple[str, str]] = [
    ("aws-access-key-id", r"AKIA[0-9A-Z]{16}"),
    ("pem-private-key", r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY( BLOCK)?-----"),
    ("github-token", r"gh[pursr]_[A-Za-z0-9]{36,255}"),
    ("slack-token", r"xox[baprs]-[0-9A-Za-z-]{10,}"),
    ("stripe-live-key", r"sk-(live|proj)-[A-Za-z0-9]{24,}"),
    ("google-api-key", r"AIza[0-9A-Za-z_-]{35}"),
]

SHELL_TOOLS = {"Bash"}

CASES: list[tuple[str, dict[str, Any], str]] = [
    ("Bash", {"command": "rm -rf / --no-preserve-root"}, "deny"),
    ("Bash", {"command": "mkdir out && rm -rf $HOME/Documents"}, "deny"),
    ("Write", {"file_path": "notes/aws.md", "content": "key: AKIAIOSFODNN7EXAMPLE\n"}, "deny"),
    ("Write", {"file_path": "id.pem", "content": "-----BEGIN RSA PRIVATE KEY-----\nMIIE...\n"}, "deny"),
    ("Bash", {"command": "rm -rf ./build && npm run build"}, "allow"),
    ("Edit", {"file_path": "README.md", "new_string": "Shipped 2026-08-30."}, "allow"),
]


def _strings(value: Any) -> list[str]:
    out: list[str] = []
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, dict):
        for v in value.values():
            out.extend(_strings(v))
    elif isinstance(value, (list, tuple)):
        for v in value:
            out.extend(_strings(v))
    return out


def evaluate(tool_name: str, input_data: dict[str, Any]) -> tuple[str, str]:
    """Return (allow|deny, rule_id). Mirrors the two house hooks."""
    if tool_name in SHELL_TOOLS:
        cmd = str(input_data.get("command") or input_data.get("cmd") or "")
        if cmd:
            if re.search(r"\bsudo\b.*\brm\b", cmd):
                return "deny", "sudo-rm"
            for rule_id, sweep, target in DANGEROUS_COMMAND_RULES:
                if re.search(sweep, cmd) and (target is None or re.search(target, cmd)):
                    return "deny", rule_id
    for rule_id, pat in SECRET_RULES:
        for s in _strings(input_data):
            if re.search(pat, s):
                return "deny", rule_id
    return "allow", "no-rule-match"


def sanitize(payload: dict[str, Any]) -> dict[str, Any]:
    blob = json.dumps(payload)
    for _, pat in SECRET_RULES:
        blob = re.sub(pat, "[REDACTED-CREDENTIAL]", blob)
    return json.loads(blob)
