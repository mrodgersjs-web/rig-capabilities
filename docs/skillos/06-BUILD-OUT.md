# Build-out plan (motion). Specs are state.

Specs in this folder declare what should be true. This file is the DAG. **Finishing this file is not consent to implement v4+.** Trigger phrase to execute: "drain the DAG".

Status now: **v4 done. v5 BLOCKED** on all-stores-restorable (4779 unresolved). Do not call v5 drained. Goal Card not re-locked. v6+ proceeds only after `--stores` is green.

## Anti-patterns (build-out)

| Code | Design fix |
|---|---|
| AP-REALITY-GAP | `universe.jsonl` rowcount from a real index dump, not an estimated 4911 |
| AP-PARTIAL-COMPLETE | v5 checklist all-or-nothing |
| AP-CONNECTION-BLIND | restore recipe must fetch bytes, not print a path |
| AP-NO-WALK-AWAY | witness CLI exits 1 in CI without a human watching |

GEV: universe dump script ≠ witness compiler ≠ orphan runner.

## DAG

```
p-v1-provenance
p-v2-goal-card
p-v3-benchmark     } done (docs/skillos 00–05)
        ↓
p-v4-index-sha
        ↓
p-v5-universe  →  p-v5-canonical-witness  →  p-v5-orphan-one
        ↓
p-v6-cluster-doors
        ↓
p-v7-receipts
        ↓
p-v8-genes
        ↓
p-v9-splice-dry
        ↓
p-v10-menu-freeze
        ↓
p-v11-executable-graph → p-v12-introns → p-v13-isoforms
        ↓
p-v14-restore-drill
        ↓
p-v15-orphan-gate
        ↓
p-v16-budgets → p-v17-court → p-v18-profiles → p-v19-gev
        ↓
p-v20-freeze
```

## Plan records

| slug | status | depends | implements | validation (must go red when planted) |
|---|---|---|---|---|
| p-v1-provenance | done | — | 00-PROVENANCE | tree must not contain tesslio/cli source |
| p-v2-goal-card | done | p-v1 | 02-GOAL-CARD, 03-SPEC, 04-TOP-50 | 50 J-ids; freeze test in 04 |
| p-v3-benchmark | done | p-v1 | 01-TESSL-BENCHMARK, 05-V20 | Tessl facts cited; no fork |
| p-v4-index-sha | done | p-v3 | v4 | `skillos dump` n from live index (4919) |
| p-v5-universe | **blocked** | p-v4 | v5 L4 | keys green; `--stores` must go green without invented recipes |
| p-v5-canonical-witness | done (held behind blocked v5) | p-v5-universe | v5 L5 | 29/29 `witness --strict` |
| p-v5-orphan-one | done (held behind blocked v5) | p-v5-canonical-witness | v5 L5 | orphan green; `--plant-leak` exit 1 |
| p-v6-cluster-doors | planned | p-v5-universe | v6 | every universe key has a door (J50 ok); plant: unassign J50 → orphans > 0 |
| p-v7-receipts | planned | p-v6 | v7 | hide/retire requires blob or git-commit recipe; restore produces matching sha |
| p-v8-genes | planned | p-v6 | v8 | 50 files `docs/skillos/genes/Jxx.yaml`; each has DONE-TEST + Gate-D class |
| p-v9-splice-dry | planned | p-v8 | v9 | `skillos splice J01 --dry` hashes a DAG; remove required exon → red |
| p-v10-menu-freeze | planned | p-v9, p-v7 | v10 | operator default list length 50; delta ledger for hidden names |
| p-v11-executable-graph | planned | p-v10 | v11 | metadata edges not enough; mutation-drop-edge red |
| p-v12-introns | planned | p-v11 | v12 | never-publish-without-Gate-D intron fires |
| p-v13-isoforms | planned | p-v12 | v13 | cache miss when exon sha changes |
| p-v14-restore-drill | planned | p-v7 | v14 | sample restore; 404 recipe red |
| p-v15-orphan-gate | planned | p-v11, p-v5-orphan-one | v15 | kind=skill witnesses complete; corpus blocks release |
| p-v16-budgets | planned | p-v15 | v16 | two read exons that write together → red |
| p-v17-court | planned | p-v16 | v17 | J21/J16 straddle refuses |
| p-v18-profiles | planned | p-v17 | v18 | intern profile cannot take J16 send path |
| p-v19-gev | planned | p-v18 | v19 | compiler ≠ contract verifier |
| p-v20-freeze | planned | p-v19, p-v14, p-v15 | v20 Goal Card | four commands green + plant-failure |

## v5 closeout checklist (first ship)

**Verdict: NOT CLOSED.** AP-PARTIAL-COMPLETE. `--stores` red.

- [x] `universe.jsonl` generated from live `.index.json` (n=4919 printed, not guessed)
- [x] store: canonical=blob (140); others=`unresolved_bundle`/`unresolved` — **not** invented recipes
- [x] plant: `--plant-drop skill/iqrsqpi-v10` exit 1
- [x] restore: adversarial-verification-loop blob → catalog sha match
- [x] canonical skill witnesses 29/29 green
- [x] orphan fixture green; name-leak plant red
- [x] provenance deny tesslio/cli hits=[]; standalone Tessl CLI authenticated for explicitly requested reviews (no CLI source vendored)
- [ ] all stores restorable

## Out of this DAG

- Tessl onboarding / reviews on the estate are a separate, explicitly authorized task; they do not satisfy the SkillOS store gate or authorize vendoring Tessl source.
- Deleting ~/.claude or ~/.hermes skills
- Publishing a public registry

## Drain rule

v4 closed. v5 open until `--stores` is green. v6+ starts after that, not before.
