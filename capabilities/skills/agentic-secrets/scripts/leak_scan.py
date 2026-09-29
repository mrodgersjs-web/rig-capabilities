#!/usr/bin/env python3
"""Fail closed when a credential VALUE sits in a setup's files, logs, or receipts (gate E4).

Scans the given files/directories for token-shaped strings (OpenAI, Anthropic, OpenRouter,
LangSmith, Langfuse, Trigger.dev, Prefect, GitHub, Slack, AWS, private keys) and for
`KEY=value` assignments of well-known secret variable names with a literal value. It prints
file, line, and the pattern NAME with the value masked, never the value itself.

Keychain item NAMES (com.rig.env.*) are the allowed way to reference a secret and never match.

Usage: leak_scan.py PATH [PATH ...] [--plant]
  --plant scans an in-memory planted token instead of the paths; exit 2 means the scanner
  catches it, 0 means it is blind (use as a done_when with `; test $? -eq 2`).
Exit: 0 clean, 2 leak found (or plant caught), 1 usage. Stdlib only, read-only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PATTERNS = {
    "openai": r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}",
    "anthropic": r"\bsk-ant-[A-Za-z0-9_-]{20,}",
    "openrouter": r"\bsk-or-v1-[A-Za-z0-9]{20,}",
    "langsmith": r"\blsv2_(?:pt|sk)_[A-Za-z0-9_]{20,}",
    "langfuse": r"\b(?:sk|pk)-lf-[A-Za-z0-9-]{16,}",
    "trigger_dev": r"\btr_(?:dev|prod|stg|pat)_[A-Za-z0-9]{16,}",
    "prefect": r"\bpnu_[A-Za-z0-9]{20,}",
    "github": r"\b(?:ghp|gho|ghs|ghu)_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{40,}",
    "slack": r"\bxox[abprs]-[A-Za-z0-9-]{20,}",
    "aws_access_key": r"\bAKIA[0-9A-Z]{16}\b",
    "private_key": r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----",
    "assigned_secret": r"\b(?:OPENAI|ANTHROPIC|OPENROUTER|LANGSMITH|LANGCHAIN|LANGFUSE_SECRET|TRIGGER_SECRET|PREFECT_API|DIFY|GEMINI|GOOGLE)_(?:API_)?KEY\s*[=:]\s*['\"]?(?!\$|<|\{|\"\$|com\.rig\.env\.)[A-Za-z0-9_\-]{16,}",
}
RX = {k: re.compile(v) for k, v in PATTERNS.items()}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".next", "dist"}


def scan_text(name: str, text: str) -> list[str]:
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        for kind, rx in RX.items():
            m = rx.search(line)
            if m:
                v = m.group(0)
                hits.append(f"LEAK {name}:{i} {kind} {v[:4]}...{'*' * 6} (len {len(v)})")
    return hits


def files(paths: list[str]):
    for p in map(Path, paths):
        if p.is_file():
            yield p
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and not (set(f.parts) & SKIP_DIRS) and f.stat().st_size < 5_000_000:
                    yield f


def main(argv: list[str]) -> int:
    if "--plant" in argv:
        planted = "OPENAI_API_KEY=" + "sk-proj-" + "PLANTEDFIXTURE" * 3
        hits = scan_text("<plant>", planted) + scan_text("<clean>", "key via keychain item com.rig.env.OPENAI_API_KEY")
        caught = any(h.startswith("LEAK <plant>") for h in hits)
        false_pos = any(h.startswith("LEAK <clean>") for h in hits)
        print(f"PLANT leak_scan: {'CAUGHT' if caught else 'ESCAPED'}; keychain-name false positive: {false_pos}")
        return 2 if caught and not false_pos else 0
    if not argv:
        print(__doc__.splitlines()[0], file=sys.stderr)
        return 1
    hits, n = [], 0
    for f in files(argv):
        n += 1
        try:
            hits += scan_text(str(f), f.read_text(errors="ignore"))
        except OSError:
            continue
    for h in hits:
        print(h)
    print(f"leak_scan: {len(hits)} finding(s) across {n} file(s)")
    return 2 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
