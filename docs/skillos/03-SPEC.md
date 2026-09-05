# SPEC — RIG SkillOS

SPEC.md is the build contract (rig-jtbd-packs). Outcome criteria lock at Gate 04; non-goals lock at Gate 06.

## Job statement

When Mike (or Jake) needs the estate to **do a job**, the system presents **50 stable doors**, compiles the smallest proven capability DAG for this context, executes under Gate-D, and leaves a ProofPacket — without requiring anyone to know 2,650 skill names, and without deleting any skillset.

## Barrier

Today the estate is an index of files. Outcome lanes help search; they are not a menu. Tessl-class products add more files, scores, and copies. Activation falls as count rises (Limits to Growth). Compression-by-deletion would amputate long-tail jobs. Compression-by-promise ("it's still in the index") is theater unless a witness *and* an orphan-replay can go red.

## Conserved universe

U = every asset in `.index.json`, keyed by `(kind,id)`. External roots drift; **U is the snapshot**. v5 writes `docs/skillos/universe.jsonl` with `kind,id,source,path,sha,store`. `store` is a licence-aware content blob *or* an immutable upstream retrieval recipe; a row of path+sha with neither cannot retire or hide an asset. Disappearance without a **restorable** receipt is red. Restore drill (v14) must materialize bytes and match `sha`. Executable witness coverage: canonical ⊂ U at v5; kind=skill at v15; all of U at v20.

## Outcome criteria (time-bounded)

| When | Criterion |
|---|---|
| v5 | 50-door manifest exists; `universe.jsonl` rowcount = snapshot N; disappearance without receipt is red; every *canonical* skill has an executable witness edge; 1 orphan fixture planted red→green |
| v10 | Operator-facing list is 50 doors; splice dry-run emits hashed DAG for 10 doors; warehouse receipts for any renamed/hidden id |
| v15 | Orphan-replay corpus is a release gate; compression delta ledger published per round; kind=skill executable-witness coverage complete |
| v20 | All four Goal Card commands green on **all of U**; plant-failure on witness; local-first resolve/execute of warehoused exons; Tessl CLI not on the critical path |

## Non-goals

- A public skill marketplace competing with tessl.io/registry
- LLM-judge "review %" as a ship gate
- One mega-SKILL.md per door
- Moving harness roots (~/.claude, ~/.hermes, …) in v0–v5
- Auto-send / auto-publish

## Constraints

- Clean-room vs Tessl (`00-PROVENANCE.md`)
- ANCHOR law: no source, no Tessl claim
- GEV: splice compiler ≠ witness compiler ≠ orphan runner
- Gate-D on outward/irreversible
- Destructive inventory changes are one commit *after* replacement verifies
- MIT/Apache may be forked; Tessl CLI may not

## Gate list (minimum + blocking)

1. **Provenance** — no tesslio/cli bytes in tree
2. **Conservation** — witness graph bidirectional, executable edges only
3. **Orphan-replay** — hidden-baseline fixtures; no skill-name leakage
4. **Splice closed** — isoform fails if ports/permissions/Gate-D/quality_floor mismatch
5. **Plant-failure** — each of 2–4 goes red on a known-bad fixture
6. **Menu freeze** — adding a 51st door is a named scope change, not a drive-by

## Principles (decisive)

- **Job over file.** When a new SKILL.md appears, it is an exon. It does not get a menu slot.
- **Hide ≠ delete.** Names may leave the operator surface only with a warehouse receipt + witness edge.
- **Green that cannot go red is theater.** Witness and orphan gates must have planted failures.
- **Local proof beats cloud delta.** `done_when` / `rig-capabilities test` is the ship signal; hosted evals are optional later.
- **Compile, don't copy.** A run gets a frozen isoform, not another installed clone in a dotfile.

## Architecture (three machines)

1. **Splicing** — 50 gene manifests + compiler → hashed DAG (isoform)
2. **Witness** — bipartite graph skill↔door with executable fixtures
3. **Orphan-attack** — historical intents whose only solution lived in the tail; compression cannot ship if they fail

GEV: three different code paths; none grades itself.
