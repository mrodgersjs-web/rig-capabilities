#!/usr/bin/env python3
# done_when: cmd:python3 scripts/hook_fires_misc.py redact_state.py
"""redact_state.py -- stdin -> stdout secret redaction.

Jev is a HOSTED classifier (api.typesafe.ai). Any state scored by a gate leaves the
machine. Sending unredacted dumps is a hard prohibition, so every hook path that
feeds a gate pipes through this first (jev-everywhere/references/decision-criteria.md,
"Hard prohibitions").

Deterministic stdlib only. Patterns are ordered: key blocks first, then bearer
tokens, then provider key shapes, then key = value pairs. A pattern that misses is
a leak, so this file carries a planted-secret test (run at wiring time): seed a fake
token, run the redactor, assert the seed appears zero times in the output.

Usage:  python3 redact_state.py < in > out
Exit 0 always (redaction is best-effort hygiene, never a verdict).
"""
import re
import sys

PATTERNS = [
    (re.compile(
        r"-----BEGIN[ A-Z]*PRIVATE KEY-----[\s\S]*?-----END[ A-Z]*PRIVATE KEY-----"),
     "[REDACTED-KEY-BLOCK]"),
    (re.compile(r"(?i)\bbearer\s+[a-z0-9._\-]{16,}"), "Bearer [REDACTED]"),
    (re.compile(r"\b(?:sk|pk|rk|ghp|gho|ghu|ghs|xoxb|xoxp|xoxa|AKIA|ASIA)"
                r"[A-Za-z0-9_\-]{16,}\b"), "[REDACTED-TOKEN]"),
    (re.compile(r"(?i)\b(api[_-]?key|secret|token|passwd|password)\b"
                r"(\s*[:=]\s*)(\S+)"), r"\1\2[REDACTED]"),
]


def redact(text: str) -> str:
    for pattern, replacement in PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def main() -> int:
    sys.stdout.write(redact(sys.stdin.read()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
