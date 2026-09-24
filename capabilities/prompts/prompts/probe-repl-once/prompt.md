---
id: probe-repl-once
version: 1
status: draft
updated: 2026-09-24
task: Connection test exercising exactly one repl call and reporting one observed value
category: verification-probe
domain: verification-probe
model_target: unspecified
score: null
license: first-party
source: aside: sessions/2026-09-17_21metlYHPFlNBcaD/messages.jsonl (fired 35x)
triggers: connection test repl exactly once report the page title one tool call fresh observation
compose: agent/prompt-injection-and-probes.md
provenance: aside: sessions/2026-09-17_21metlYHPFlNBcaD/messages.jsonl (fired 35x) | observe-an-external-value probe shape
content_sha256: 6d7545b1229c649af183bd39ff657e35891c2b14332a1c4fa52e2085dabcfd03
---

Connection test. Use repl exactly once with this code: <REPL_SNIPPET> Then report the returned <VALUE_DESCRIPTION>. Do not read memory, files, other tabs, or settings. Do not use other tools.
