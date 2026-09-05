---
name: capabilities-concepts-build
description: Build or extend the LLM concept overlay (.concepts.llm.json) that powers concept lookup — checkpointed, idempotent, resumable.
argument-hint: "[n]"
allowed-tools: Read, Bash
category: meta
outcome: "meta: concept coverage grows monotonically; every tagged asset carries a demonstrated red path for the untagged case"
done_when:
  - file:capabilities/commands/capabilities-concepts-build.md
  - file:examples/great/meta/capabilities-concepts-build.md
  - grep:capabilities/commands/capabilities-concepts-build.md:The overlay is derived data
great_example: examples/great/meta/capabilities-concepts-build.md
acl: public
quality_floor: 0.7
---

# capabilities-concepts-build

1. `./bin/rig-capabilities concepts-build --llm --n <n>` (default 300) — runs against the local ollama fleet, checkpoints per batch, safe to kill and rerun.
2. Progress is measured against total canonicals: report `tagged/total`, never a bare "done".
3. Verify with `./bin/rig-capabilities concepts <term>` on a term that previously returned nothing — the new coverage must answer.
4. Untagged assets stay untagged in the overlay; absence of a tag is honest, not an error to hide.

The overlay is derived data: it may always be rebuilt from the index. Never hand-edit it.
