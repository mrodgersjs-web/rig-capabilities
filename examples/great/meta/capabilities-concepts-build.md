# Great example — capabilities-concepts-build

Run: `concepts-build --llm --n 300`

Good run shape:

- Checkpointed batches (50/batch), ~1s per asset against local qwen3:8b; kill-safe — rerun resumes at 62, not 0.
- Reported `62/4687 canonicals tagged` — a small honest number, not "overlay building nicely".
- Proof step: `concepts zero-trust` returned nothing before the run and a ranked asset list after. That before/after IS the done-test.

The failure mode this example guards: claiming coverage from a run that only re-tagged assets BM25 already found.
