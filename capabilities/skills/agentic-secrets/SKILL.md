---
name: agentic-secrets
description: "agentic-systems-setup sub-skill, gate E4: handle every framework credential by macOS keychain item NAME only - list names without values, inject a value into one child process, keep .env files out of git, and fail closed with leak_scan.py when a value lands in code, logs, or receipts. JEV-FIRST MANDATE."
tags: [rig, agentic-systems, sub-skill, secrets, keychain, leak-scan]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: secrets
  extends: "sec-secret-leak-sweep, guard-secret-write"
outcome: "Every credential a setup uses is named by its com.rig.env.* item, injected only into the process that needs it, absent from files, logs, and receipts (leak_scan.py exit 0), and any new credential is held at Gate-D."
activation: "Load at the start of every agentic setup session (gate E4 runs in every session), before a framework reads an API key, before writing any .env or config file, and whenever a quickstart asks you to paste a key."
instruction: "Reference secrets by keychain item name, check presence without reading the value, inject the value into one child process, keep env files ignored by git, run leak_scan.py over the project and run folder, and hold creation of any new key at Gate-D."
applies_when:
  env: "Mike's Mac login keychain; Aside sandbox or Orca terminal"
  runtime: "any framework or platform that reads API keys from env, files, or its own secret store"
  deps: "security (macOS), scripts/leak_scan.py (stdlib)"
  params: "keychain item names; project and run directories to scan"
  budget: "seconds per scan"
  scale: "one project per scan"
permissions:
  - fs.read
  - bash
  - gate-d-required:credential-create
flow:
  - List the com.rig.env item names the setup needs; check presence without values.
  - Inject each value into exactly one child process at run time.
  - Keep env files git-ignored and outside receipts.
  - Run leak_scan.py over the project, logs, and receipts before closing E4.
done_when:
  - "cmd:env -u PYTHONHOME -u PYTHONPATH python3 capabilities/skills/agentic-secrets/scripts/leak_scan.py --plant; test $? -eq 2"
  - "cmd:env -u PYTHONHOME -u PYTHONPATH python3 capabilities/skills/agentic-secrets/scripts/leak_scan.py capabilities/skills/agentic-systems-setup capabilities/skills/agentic-proof-ladder"
  - "grep:capabilities/skills/agentic-secrets/SKILL.md:find-generic-password"
out_of_scope:
  - printing, pasting, or storing a credential value, even when Mike asks
  - creating, rotating, or deleting keys without Gate-D
  - reading credential files to work around a denied tool
---

# agentic-secrets

JEV FIRST, binding on every credential step: an agent whose only context is this excerpt sends
semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier
LLM call; receipts are judged with `rig-s1gate check agentic.setup`, whose `secret_exposure`
signal blocks a leaked value. When the classifier is unavailable: DEFER, never guess a verdict
locally. A required signal passes only above 0.9.

## Load surface

Always loaded at the start of every agentic setup task, before the first install command:
every framework setup reads at least one key or env file, so the `agentic-systems-setup`
meta-skill routes gate E4 here in every session, `agentic-setup-conductor` loads it from its
routes table before the stage's first action, `agentic-proof-runner` runs its leak scan, and
the `agentic-setup-session` harness names it as doctrine. It is a task-start surface, not a
deep reference an agent must already know about.

## Names, never values

```sh
# names only (no -d, no -w): what exists
security dump-keychain 2>/dev/null | grep -o '"svce"<blob>="com\.rig\.env\.[A-Z0-9_]*' | sed 's/.*="//' | sort -u
# presence of one item without reading it
security find-generic-password -s com.rig.env.OPENROUTER_API_KEY >/dev/null 2>&1 && echo present || echo absent
# inject into ONE child process; never echo, never set -x, never write it down
OPENROUTER_API_KEY="$(security find-generic-password -s com.rig.env.OPENROUTER_API_KEY -w)" uv run python app.py
# Docker: pass through by name from the caller env; no value on the command line
docker run -e OPENROUTER_API_KEY ...
```

Observed 2026-09-28 (names only): `com.rig.env.OPENAI_API_KEY`, `ANTHROPIC_API_KEY`,
`OPENROUTER_API_KEY`, `LANGFUSE_SECRET_KEY`, `AZURE_OPENAI_API_KEY` exist. No item exists for
LangSmith, Trigger.dev, Prefect Cloud, Dify, or CrewAI AMP; creating one is a Gate-D action.

## Files that frameworks want

Quickstarts write `.env` (Trigger.dev, Dify, Flowise, Langflow, n8n) or store secrets in their
own backend (Prefect Secret blocks, Kestra secrets, n8n credentials). Rules: the file is
ignored by git (`git check-ignore <file>` prints it), lives outside the run folder that holds
receipts, and holds placeholders when committed as an example (`.env.example`).

## Fail closed

```sh
env -u PYTHONHOME -u PYTHONPATH python3 capabilities/skills/agentic-secrets/scripts/leak_scan.py <project> <run>
# exit 0 clean; exit 2 prints file:line and pattern NAME with the value masked
```

Patterns: OpenAI, Anthropic, OpenRouter, LangSmith, Langfuse, Trigger.dev, Prefect, GitHub,
Slack, AWS, private keys, and `NAME_KEY=literal` assignments. Keychain item names never match.
`--plant` proves the scanner catches a planted token (exit 2) with no false positive on an item
name; it did on 2026-09-28. The `guard-secret-write` hook covers writes made by agents.
