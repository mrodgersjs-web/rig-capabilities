---
name: cursor-review
description: "Review code changes with the Bugbot or Security Review subagent."
disable-model-invocation: true
source: grok.com/dashboard/plugins (Managed by Cursor, manual only), pulled 2026-10-26
---

# Review

Ask the user which review to run with the AskQuestion tool. If the AskQuestion tool is not available, ask the user directly. Provide exactly one single-select question with two options:

- `bugbot`: Bugbot (`/review-bugbot`)
- `security`: Security Review (`/review-security`)

After the user chooses, run the matching review once:

- Bugbot: follow the `/review-bugbot` instructions.
- Security Review: follow the `/review-security` instructions.
