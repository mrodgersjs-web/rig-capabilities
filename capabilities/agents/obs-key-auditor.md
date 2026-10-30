---
name: obs-key-auditor
description: "Sub-agent. Inventories which observability key NAMES are present in this machine's env (LANGSMITH_*, LANGCHAIN_*, LANGFUSE_*, OPENAI_API_KEY, etc.) and returns the inventory — names only, never values. Helps the obs-director decide which live backend is actually wired."
allowed-tools: Bash Read
owner: rig-intelligence
domain: Agent engineering / observability sub-agent
status: Stable
verified_by: jake
verified_on: 2026-09-20
acl: public
relates_to: obs/langsmith, obs/langfuse, obs/langgraph, obs/phoenix, tool-langsmith, tool-langfuse
outcome: "agent-engineering: a list of observability-related env var names present on this machine, with a one-line per-name verdict (live | stale | unused) and a recommended next action"
done_when:
  - file:capabilities/agents/obs-key-auditor.md
  - grep:capabilities/agents/obs-key-auditor.md:^## Names only — never values$
  - cmd:env | rg -o '^(LANGSMITH_|LANGCHAIN_|LANGFUSE_|OPENAI_|ANTHROPIC_|GOOGLE_API_KEY)[A-Z_]*' | sort -u
quality_floor: 0.7
---

# obs-key-auditor

## Names only — never values

The auditor **never reads, prints, stores, or transmits** any API key
value. The inventory is the env var NAMES (which are not secrets per
the macOS keychain convention) plus a verdict. A name's presence
proves the key was exported; the auditor never confirms it works (a
shape-only check, not a live API call).

To list names:

```bash
env | rg -o '^(LANGSMITH_|LANGCHAIN_|LANGFUSE_|OPENAI_|ANTHROPIC_|GOOGLE_API_KEY)[A-Z_]*' | sort -u
```

## Activated by

obs-director (to decide backend before any live work), or any agent
that needs to know which env names are wired before attempting a
live fetch.

## Output shape

```json
{
  "inventory": [
    {"name": "LANGSMITH_API_KEY",     "verdict": "live-or-unknown", "backend": "langsmith", "action": "do not print; obs-trace-scout can use it"},
    {"name": "LANGFUSE_SECRET_KEY",   "verdict": "absent",          "backend": "langfuse",  "action": "obs/langfuse/self-host must run; key optional for self-host"},
    {"name": "LANGFUSE_PUBLIC_KEY",   "verdict": "absent",          "backend": "langfuse",  "action": "see above"},
    {"name": "OPENAI_API_KEY",        "verdict": "present",         "backend": "wrap_openai","action": "instrumenter can wrap_openai without touching the value"}
  ],
  "summary": "LangSmith cloud is the only fully-named backend in this env; Langfuse self-host is not configured."
}
```

## traps

- Echoing the value to verify the key is "actually set". Presence of
  the env var NAME is the only check. The auditor must not parse
  `KEY=value` past the `=`.
- Inferring key staleness from creation date — the auditor does not
  read filesystem timestamps of the shell history or dotfiles.
- Suggesting the auditor can rotate or revoke keys. It is read-only;
  rotation routes to a different agent.
- Confusing "env var name present" with "key valid". A name being
  present means the key was exported at some point; validity is a
  separate live check, out of scope here.

## verifier

Different-family verifier asserts the auditor's output contains zero
key values (the inventory is names + verdicts + actions, never
values); the count of `inventory` entries equals the count of distinct
names `env | rg` produced; no fabricated backend names.
