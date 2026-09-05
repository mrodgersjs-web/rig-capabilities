# Goal Card — RIG SkillOS (locked 2026-09-05)

## GOAL

Mike can hire the estate through **exactly 50 Jobs-To-Be-Done doors**. Every indexed capability remains reachable and recoverable. Tessl is a behavior benchmark, not a dependency. Destination is **v20**; we are **v0**.

## METRIC

- Operator menu size = **50** doors (not 2,650 skill names).
- **Conserved universe U**: every record in `.index.json` at snapshot time, keyed by `(kind,id)` (catalog shadows on that pair, not bare `id`). Frozen snapshot `docs/skillos/universe.jsonl` = **5004** rows at `984d60f`; identity digest = `sha256("\n".join(sorted(f"{kind}\t{id}\t{sha}")) + "\n")` over those triples — stable across `store`-only restock writes — `c3c5879fd6f3a23b64a2c2aa7295d00e2cba38ac66c5e7e0d10287ac037bb9af`. History measured from the committed files, not asserted: 4,919 (2026-09-04 live walk — non-authoritative observation, not commit-backed), 4,993 at `71af341`, 5,004 at `984d60f` — net +11 keys, with 188 triples retired / 199 introduced (91 exemplar renames, ~95 edited canonical assets, +11 new keys). Denominator = that file, never a live walk of drifting external roots, and it is never re-dumped to make a gate go green.
- **Conservation (v20)**: every `(kind,id)` in U has a bidirectional *executable* witness to ≥1 door, or the release is red.
- **Conservation (v5)**: U is frozen to `docs/skillos/universe.jsonl` (`kind,id,source,path,sha,store`). `store` is either a content-addressed blob under `docs/skillos/warehouse/<sha>` (only when the asset's licence allows local archive) or an immutable retrieval recipe (`git url + commit + path` or equivalent) whose restore command is tested. Path+hash alone is **not** a receipt. Witness compiler is red if any snapshot key disappears without a restorable receipt. Executable witnesses required for canonical skills at v5; all of U by v20. **v5 is not closed while `skillos check --stores` is red.**
- **Orphan-replay**: historical long-tail intents still produce the same observable outcome after compression, or the release is red.
- Store-gate evidence, per-source missing receipts, and the two lawful closing routes: `09-STORE-RESOLUTION-REGISTER.md`.
- Buyer/outcome terms only. Refused: "looks like Tessl", "award-tier", "1000x" as a score, LLM-judge review % as truth.

## DONE-TEST (v20)

```
./bin/rig-capabilities skillos doors --count   # prints 50
./bin/rig-capabilities skillos witness --strict && echo WITNESS_GREEN
./bin/rig-capabilities skillos orphan-replay --corpus docs/skillos/orphan/ && echo ORPHAN_GREEN
./bin/rig-capabilities skillos provenance --deny tesslio/cli && echo CLEAN_ROOM
./bin/rig-capabilities skillos check --stores && echo STORES_GREEN
```

All five green, plus plant-failure: drop one witness edge → `witness --strict` exits 1.
The fifth command is the store gate: success = exit 0 with every frozen-universe
row valid (`invalid_store_count: 0`). Line 12 named it as the v5 closure
condition; this block makes it executable, per the 2026-09-05 operator
instruction — a tightening, not a scope change.

## OUT-OF-SCOPE

- Logging into Tessl, publishing to Tessl registry, installing Tessl plugins into this repo
- Forking or vendoring `tesslio/cli`
- Deleting skills from disk to "clean up"
- Replacing Gate-D with policy-as-score
- Cloud-only eval as the ship gate

## ACTIVE-PROJECT

`/Users/rig128gb/Developer/rig-capabilities` — SkillOS specs under `docs/skillos/`. Substrate is the existing catalog/MCP/loop engine.

## EFFORT-BUDGET

v0→v5 (conservation + 50-door manifest + dry-run splice + 1 orphan fixture) is the first shippable slice. v5 done-tests are **not** green until every universe row has a restorable store. v6–v20 are named in `05-V20-FUTURE-BACK.md`.
