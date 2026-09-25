---
name: jev-system1-cascade
description: "Use Jev (TypeSafe System-1) for every semantic triage/routing/classification decision before any frontier LLM. Use when bulk-classifying notes or files, building a judgment/routing pipeline, triaging the Obsidian Inbox, or when a decision could be a typed choice/probability instead of generated prose. Full doctrine: ~/.rig/agent-doctrine/JEV_SYSTEM1_CASCADE_DOCTRINE.md"
---

# Jev System-1 Cascade

1. Check for an existing rubric: `/Users/rig128gb/Developer/rig-capabilities/bin/rig-s1gate list`. Run one: `echo STATE | rig-s1gate check <rubric> --stdin --json` (exit 0 PASS / 1 BLOCK / 2 ESCALATE / 3 config). ~100-200 ms, typed answers, decision logged.
2. Vault intake is automatic: files dropped in JakeStudio `Inbox/` are triaged every 15 min by `~/.rig/bin/jev-vault-triage` (files/escalates/quarantines + one `memory.record_event` each). Frontier work drains `~/.rig/state/jev-triage/escalations.jsonl` — never re-classify the bulk yourself.
3. New judgment: add a rubric JSON under `rig-capabilities/capabilities/harnesses/s1gate/rubrics/` and commit. One narrow judgment per question; independent questions share one call. Policy (routes, budgets, locks) stays in code; Jev only answers questions.
4. Redact secrets before any state leaves the machine. Fail closed when the provider is down (defer, don't guess). Respect `TYPESAFE_DAILY_MAX_CALLS` in `~/.rig-secrets/typesafe.env`.
5. Label right decisions (`rig-s1gate label <id> good|bad`); calibrate when ~20+ labels exist — calibration is what turns advisory gates into enforcing ones.
6. D85: a model in the deployed decision path is A2 by rule; never launder it through an A1 wrapper. Ship, prove live, seal with `d85_certified` honestly FAILED and the refusal chain preserved.
7. Session layer (how an agent applies this after it knows its mission) + per-situation good/bad criteria + per-surface embedding (coding agents, programs, Aside): skill `jev-everywhere` (same repo).
