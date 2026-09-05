# RIG SkillOS — v0 specs for a v20 capability OS

Not a Tessl clone. Tessl packages markdown; this OS hires **jobs**.

| File | What |
|---|---|
| [00-PROVENANCE.md](00-PROVENANCE.md) | Clean-room. Do not fork `tesslio/cli`. |
| [01-TESSL-BENCHMARK.md](01-TESSL-BENCHMARK.md) | Public-docs/CLI/GitHub behavior map + 10 mechanisms + 10 gaps |
| [02-GOAL-CARD.md](02-GOAL-CARD.md) | Locked north star |
| [03-SPEC.md](03-SPEC.md) | Job, universe U, gates, three machines |
| [04-TOP-50-JTBD.md](04-TOP-50-JTBD.md) | J01–J50 doors; freeze test |
| [05-V20-FUTURE-BACK.md](05-V20-FUTURE-BACK.md) | v20→v0, ten layers each |
| [06-BUILD-OUT.md](06-BUILD-OUT.md) | DAG. Do not implement past v3 until "drain the DAG" |
| [07-CANONICAL-VS-TESSL.md](07-CANONICAL-VS-TESSL.md) | 140-id local review vs Tessl axes; 77 skips named |
| [canonical-test-2026-09-05.json](canonical-test-2026-09-05.json) | Per-asset `ran` / `unrunnable` matrix |
| [coverage-lane-assignment-DRAFT.json](coverage-lane-assignment-DRAFT.json) | Candidate lane routing only — not witnessed |

## Brief

Mike asked to reverse-engineer Tessl, design a RIG system 1000x better (future-back v0→v20), and collapse thousands of skills into a **top 50** without losing capability. Tessl CLI is proprietary (README+LICENSE only). RIG already has the local proof half. The missing product is the **door / splice / witness / orphan** layer.

## Converge (ADHD, then locked)

Wide set clustered as: compression-with-witness · runtime composition · trust/refusal · local-first · failure-first routing.

**Shortlist**

1. **Bidirectional executable witness + restorable warehouse** — conservation is a graph+blob/recipe, not a promise. ★ load-bearing for "don't lose capability"
2. **50 JTBD genes that splice skill exons at invocation** — menu stays 50 while the genome stays 4911
3. **Capability-orphan attack as the compression gate** — historical tail intents must still work or the release is red

Traps: Tessl-clone registry; combinatorial "skill markets"; ambient auto-run without Gate-D; path+hash receipts that cannot restore bytes; deleting files to tidy the menu.

## v0 numbers (2026-09-05)

4911 indexed · 2650 skills · 140 canonical · quality avg 98.2 · 10 canonical missing `great_example` · Tessl not logged in · not a Tessl project.

## Next

Specs for v1–v3 are in this folder. First build slice is v4–v5 in `06-BUILD-OUT.md`. Say **drain the DAG** to start.
