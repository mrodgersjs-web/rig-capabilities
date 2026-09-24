---
id: probe-connectivity-ack
version: 2
status: draft
updated: 2026-09-24
task: One-shot connectivity check that echoes an exact ack literal and touches nothing
category: verification-probe
domain: verification-probe
model_target: unspecified
score: null
license: first-party
source: aside: sessions/2026-09-23_3jhQ1roc47aXmyPn/messages.jsonl (fired 38x)
triggers: connectivity check reply with exactly echo echo back is this alive alive is it up still responding liveness ping the agent ack literal just have it echo
compose: agent/prompt-injection-and-probes.md
provenance: aside: sessions/2026-09-23_3jhQ1roc47aXmyPn/messages.jsonl (fired 38x) | v2: triggers widened after selftest regression (echo vs echoes token gap); body unchanged
content_sha256: d9dcba3089cd5bfdead1c7e9bcb3fb21e2f17b831aad1354be8e08e9d1770af6
---

Connectivity check only. Do not use tools, browse, read files, or write anything. Reply with exactly <ACK_LITERAL>.
