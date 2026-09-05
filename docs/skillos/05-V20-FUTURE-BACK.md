# Future-back: v20 → v0 (ten layers each)

Read **v20 first**. Then walk down. Implementation order is the reverse (v0 → v20) in `06-BUILD-OUT.md`.

**Layers (stable across versions)**

| # | Layer | Question |
|---|---|---|
| L1 | Paradigm | What *is* a capability? |
| L2 | Operator surface | What does Mike type / pick? |
| L3 | Splice compiler | How does a job become a DAG? |
| L4 | Warehouse | Where do hidden exons live? |
| L5 | Proof / orphan | What can go red? |
| L6 | Authority | Who may act? |
| L7 | Routing / activation | How does an intent hit a door? |
| L8 | Distribution | How do harnesses see it? |
| L9 | Measurement | What number is allowed? |
| L10 | Evolution | What compounds next version? |

---

## v20 — Frozen SkillOS (destination)

Theme: 50 doors, full-universe executable witnesses, local-first, Tessl not on the path.

| L | State |
|---|---|
| L1 | Capability = a proven isoform of exons that satisfies a door contract. Files are inventory, not the product. |
| L2 | Exactly 50 doors. 51st = Goal Card scope change. |
| L3 | Compiler emits frozen hashed DAG per run; regulatory introns (never publish without Gate-D; prefer API over browser when both exist). Isoform registry caches winners. |
| L4 | Warehouse keyed `(kind,id)`. Blob if licence allows; else immutable git url+commit+path recipe. Restore drill must produce bytes matching sha. Path+hash alone is not a receipt. |
| L5 | `witness --strict` on **all of U**; orphan-replay corpus is CI; plant-failure fixtures committed. |
| L6 | Behavior BOM on every invocation. Blast-radius budget on the composition. Evidence leases expire stale exons to archive-but-reachable. |
| L7 | Intent-collision court: independent parsers must agree on door + effects before high-impact isoforms. |
| L8 | Harnesses load **doors**, not skill dumps. MCP: `skillos_open`, `skillos_splice`, `skillos_witness`. Offline resolve of warehoused exons. |
| L9 | Allowed: door done-tests, conservation rowcount, orphan pass rate, restore-drill pass. Banned: Tessl review %, "1000x", looks-like. |
| L10 | Splice rules evolve; door count does not. Rounds improve exons behind doors. |

Done-test: Goal Card four commands + plant-failure.

---

## v19 — Cross-family GEV on isoforms

| L | State |
|---|---|
| L1 | Maker of an isoform ≠ grader of its contract. |
| L2 | 50 doors unchanged. |
| L3 | Compiler (family A) proposes DAG; verifier (family B or deterministic) scores contract. |
| L4 | Warehouse unchanged. |
| L5 | Verifier plant-failure: accept a DAG that skips Gate-D → red. |
| L6 | Gate-D still human for outward. |
| L7 | Routing stays deterministic; GEV is on the compiled DAG, not on search. |
| L8 | No new harness copies. |
| L9 | Isoform score is contract-check, not LLM prose. |
| L10 | Failed isoforms feed splice-rule patches. |

---

## v18 — Epigenetic profiles

| L | State |
|---|---|
| L1 | Same gene, different eligibility by tenant/operator/risk. |
| L2 | 50 doors. Profiles do not add doors. |
| L3 | Overlays filter exons (e.g. no browser when API exists; no send skills in intern profile). |
| L4 | Profiles stored next to gene manifests, not as forks. |
| L5 | Profile plant-failure: intern profile must refuse J16 send-path. |
| L6 | Profiles cannot widen Gate-D. |
| L7 | Context fingerprint includes profile id. |
| L8 | Profile is an argument, not a per-harness fork. |
| L9 | Count of profile-blocked exons per run (honest, not a vanity score). |
| L10 | New profiles are data, not versions of doors. |

---

## v17 — Intent-collision court

| L | State |
|---|---|
| L1 | Ambiguous intent is a refusal, not a guess. |
| L2 | 50 doors. Collision ≠ new door. |
| L3 | Two independent door-parsers; disagreement → refuse with receipt. |
| L4 | Refusal receipts warehoused. |
| L5 | Plant: prompt that straddles J21 and J16 must refuse or ask, not send. |
| L6 | Refusal is versioned; names the dormant capability. |
| L7 | This *is* routing. |
| L8 | Receipts visible in MCP. |
| L9 | Collision-refuse count. Never "resolved by vibes". |
| L10 | Collisions that repeat become door-description patches, not extra doors. |

---

## v16 — Blast-radius budgets

| L | State |
|---|---|
| L1 | Harmless exons can compose into a forbidden act. |
| L2 | 50. |
| L3 | Isoform sums write/disclose/spend/egress; over envelope → refuse. |
| L4 | Envelope per door in gene manifest. |
| L5 | Plant: two read-only exons whose combo writes → red. |
| L6 | Envelope cannot exceed Gate-D class. |
| L7 | Budget checked after splice, before execute. |
| L8 | Unchanged. |
| L9 | Refused-by-budget count. |
| L10 | Envelopes tighten; doors stay. |

---

## v15 — Orphan-attack is a release gate

Milestone (not a layer): **kind=skill executable witnesses complete** for the 2650 snapshot ids.

| L | State |
|---|---|
| L1 | Compression that cannot replay the tail did not conserve. |
| L2 | 50 doors. No 51st for "misc tail". |
| L3 | Compiler must recover hidden-baseline fixtures from intent alone. |
| L4 | Baseline skill ids stored separately from the fixture prompt; names must not leak. |
| L5 | `orphan-replay` exit 1 blocks release. Planted leak-name fixture also red. |
| L6 | Unchanged Gate-D. Orphan runner cannot perform outward actions. |
| L7 | Router cannot cheat by embedding the old skill-id in the prompt. |
| L8 | CI only; no Tessl token. |
| L9 | Tail-coverage % published; critical regressions = 0. |
| L10 | Unresolved live intents mined into new fixtures. |

---

## v14 — Recoverability drills

| L | State |
|---|---|
| L1 | A receipt you cannot restore is a tombstone. |
| L2 | 50. |
| L3 | Unchanged. |
| L4 | Every release restores a sample: materialize blob or run recipe, hash must match. Plant: recipe that 404s is red. |
| L5 | Plant: corrupt one blob → drill red. |
| L6 | Restore is read-only of production roots. |
| L7 | Unchanged. |
| L8 | Drill runs local. |
| L9 | Restored/sampled counts. |
| L10 | Failed restores block exon retirement. |

---

## v13 — Isoform registry

| L | State |
|---|---|
| L1 | Recurrent successful DAGs become deterministic fast paths. |
| L2 | 50. |
| L3 | Cache by context fingerprint; still re-verify contract. |
| L4 | Cached DAGs are receipts, not new skills. |
| L5 | Stale cache (exon sha changed) must miss, not silently run. |
| L6 | Cached isoform still needs Gate-D if it has outward nodes. |
| L7 | Fast path after court. |
| L8 | Unchanged. |
| L9 | Cache hit rate is optional; correctness first. |
| L10 | Winners become default splice rules. |

---

## v12 — Regulatory introns (negative rules)

| L | State |
|---|---|
| L1 | Absence is first-class ("never include X"). |
| L2 | 50. |
| L3 | Intron set in gene manifests. |
| L4 | Unchanged. |
| L5 | Plant: intron-violating DAG must be refused. |
| L6 | Introns cannot be overridden by profiles except to *narrow*. |
| L7 | Unchanged. |
| L8 | Unchanged. |
| L9 | Intron-fire count. |
| L10 | New never-rules from incidents, not from taste. |

---

## v11 — Bidirectional executable witness graph

| L | State |
|---|---|
| L1 | Metadata links are candidates; only fixtures make edges. |
| L2 | 50 doors each have negative examples (cannot be a catch-all). |
| L3 | Compiler may only pick witnessed exons. |
| L4 | Unresolved nodes named, never skipped. |
| L5 | Mutation test: drop one known edge → compiler red. |
| L6 | Unchanged. |
| L7 | Doors publish supported intent classes. |
| L8 | Witness report in `capabilities_quality_report` sibling. |
| L9 | Orphan count must be 0 for canonical; skills in progress toward v15. |
| L10 | Freshness: payload/door/router/`done_when` change invalidates edge. |

---

## v10 — Top-50 surface live

| L | State |
|---|---|
| L1 | Operator no longer browses 2650 names as the default. |
| L2 | **Menu is 50 doors.** Search still exists as a debug exon, not the home screen. |
| L3 | Dry-run splice for ≥10 doors emits hashed DAGs. |
| L4 | Any id hidden from menu has a warehouse receipt. |
| L5 | Compression delta ledger: names that left the menu vs still reachable. |
| L6 | Unchanged. |
| L7 | `capabilities_route` prefers doors over raw skill ids. |
| L8 | Slash commands / Hermes ` /<door>` for the 50; skills remain loadable by id for debug. |
| L9 | Menu length == 50 (the freeze test in `04-TOP-50-JTBD.md`). |
| L10 | Door copy (descriptions) may improve; count frozen. |

---

## v9 — Splice compiler dry-run

| L | State |
|---|---|
| L1 | A job is a gene + splice sites, not a fixed workflow. |
| L2 | Manifests exist; menu not yet frozen in UX. |
| L3 | **Dry-run only**: resolve canonical ids → DAG, fail closed on port/gate mismatch. No execute. |
| L4 | Unchanged. |
| L5 | Adversarial exon mutation on 1 gene: remove required exon → red. |
| L6 | Dry-run cannot perform Gate-D actions. |
| L7 | Manual door pick. |
| L8 | CLI: `rig-capabilities skillos splice J01 --dry`. |
| L9 | DAG hash stability on identical inputs. |
| L10 | First splice-rule file. |

---

## v8 — 50 gene manifests

| L | State |
|---|---|
| L1 | Door = invariant outcome + ports + gates + splice sites. |
| L2 | 50 YAML/JSON genes under `docs/skillos/genes/Jxx.yaml`. |
| L3 | No compiler yet — schema only. |
| L4 | Canonical skills tagged `doors: [Jxx]`. |
| L5 | Schema plant: gene missing DONE-TEST fails validate. |
| L6 | Each gene lists Gate-D class (none / dormant / approve). |
| L7 | Unchanged. |
| L8 | Unchanged. |
| L9 | `genes/` count == 50. |
| L10 | Manifests are the evolution surface for v9+. |

---

## v7 — Conservation ledger (no deletes)

| L | State |
|---|---|
| L1 | Hide ≠ delete is enforced in code. |
| L2 | Still many names visible. |
| L3 | None. |
| L4 | Retirement/hide requires restorable store (blob or commit recipe), not path+sha. Keyed `(kind,id)`. |
| L5 | Plant: delete a snapshot id with no receipt → red. |
| L6 | Unchanged. |
| L7 | Unchanged. |
| L8 | Unchanged. |
| L9 | Receipt count; missing-receipt red. |
| L10 | Ledger is append-only. |

---

## v6 — Cluster U onto 50 doors

| L | State |
|---|---|
| L1 | Every snapshot id has a *candidate* door (J50 allowed). |
| L2 | Draft 50 published in `04-TOP-50-JTBD.md` (this already). |
| L3 | None. |
| L4 | universe.jsonl joined to door ids. |
| L5 | Plant: drop J50 assignment → remaining orphans red. |
| L6 | Unchanged. |
| L7 | Lane taxonomy remains the fallback. |
| L8 | Unchanged. |
| L9 | Orphan-candidate count → 0. |
| L10 | J50 shrinks by token promotions, not deletions. |

---

## v5 — First shippable slice

| L | State |
|---|---|
| L1 | Conservation is a snapshot + receipt, not a speech. |
| L2 | 50-door *manifest* exists (table). UX still old. |
| L3 | None required. |
| L4 | `universe.jsonl` = U keyed `(kind,id)` (N=4911 on 2026-09-05). Each row has sha + store (blob or recipe). Canonical assets blobbed (this repo). Externals: recipe until licence-checked blob. |
| L5 | Canonical skills executable witness; 1 orphan fixture red→green. Disappearance without receipt red. |
| L6 | Gate-D doctrine unchanged. |
| L7 | Unchanged. |
| L8 | Unchanged. |
| L9 | rowcount(universe)==N; canonical witness green. |
| L10 | Stop until these are green. |

---

## v4 — Index as warehouse substrate

| L | State |
|---|---|
| L1 | `.index.json` is inventory, not a menu. |
| L2 | 140 canonical + thousands of externals, as today. |
| L3 | None. |
| L4 | Index already has path+source; add sha to the snapshot format. |
| L5 | Existing certify/plant-failure stay green (do not break). |
| L6 | Unchanged. |
| L7 | `capabilities_route` / outcome lanes. |
| L8 | Existing MCP. |
| L9 | Quality report 98.2 canonical; 10 missing great_example (honest). |
| L10 | Do not round-upgrade via Tessl cloud. |

---

## v3 — Tessl gap register (this document set)

| L | State |
|---|---|
| L1 | Tessl = benchmark; SkillOS = different unit (job, not markdown package). |
| L2 | No menu change. Gap register is for designers, not operators. |
| L3 | Tessl eval/review pipelines described, not reimplemented. |
| L4 | No Tessl bytes warehoused. Public GitHub wrappers (setup-tessl, skill-eval) cited as behavior only. |
| L5 | `01-TESSL-BENCHMARK.md` exists. Ten mechanisms / ten gaps. Provenance file exists; no tesslio/cli source in tree. |
| L6 | No Tessl login in the critical path. |
| L7 | Discovery of Tessl is docs.tessl.io + CLI `--help` + public org repos. |
| L8 | Nothing from Tessl registry installed into RIG harnesses. |
| L9 | Cited Tessl facts have URLs. Unsourced claims dropped. |
| L10 | Specs beat code. v3 completes when this document set is in git. |

---

## v2 — Goal Card + SPEC lock

| L | State |
|---|---|
| L1 | A capability is whatever the Goal Card says Mike is hiring: 50 doors, conservation of U, orphan-replay. Not a SKILL.md listing. |
| L2 | Operator surface named: J01–J50 in `04-TOP-50-JTBD.md`. Menu is not live; the names exist so later versions cannot invent a 51st without a scope change. |
| L3 | No compiler. SPEC forbids mega-SKILL.md-per-door. Splice is specified as a future machine, not sketched in code. |
| L4 | Conserved universe U defined as every `.index.json` record keyed `(kind,id)`. Snapshot counts written (4911 / 2650). No warehouse yet. |
| L5 | Proof required in the card: four v20 commands + plant-failure. No runner yet. |
| L6 | Gate-D stays human. Tessl login, Tessl publish, and deleting skills to tidy the menu are OUT-OF-SCOPE. |
| L7 | Routing still outcome-lanes + BM25. Card says doors will replace that default. |
| L8 | Artifacts live in `docs/skillos/`. No harness menu change. |
| L9 | Allowed metrics named (door count, conservation, orphan). Banned: Tessl review %, "looks like Tessl", "1000x" as a score. |
| L10 | Effort budget: do not start v6–v20 until v5 done-tests are green. |

---

## v1 — Provenance / non-copy

| L | State |
|---|---|
| L1 | Tessl is a behavior benchmark. Capability OS code in this repo must be independently specified. |
| L2 | No operator menu work. Provenance is not a product surface. |
| L3 | No splice compiler. Do not copy Tessl review/eval pipelines. |
| L4 | Do not vendor `tesslio/cli`. Do not store Tessl rubric JSON or judge prompts. |
| L5 | `00-PROVENANCE.md` exists. A tree that contains tesslio/cli source is red. |
| L6 | No Tessl account in the critical path. No TESSL_TOKEN required to read RIG. |
| L7 | Discovery of Tessl facts is URL-cited docs/CLI help/public GitHub only. |
| L8 | Nothing installed into harnesses from Tessl registry. |
| L9 | Every Tessl claim in `01-TESSL-BENCHMARK.md` carries a URL. Unsourced claims dropped. |
| L10 | Clean-room constraint is permanent; later versions do not relax it to "just this once". |

---

## v0 — Sprawl (today, 2026-09-05)

| L | State |
|---|---|
| L1 | Capability ≈ a file the index can search. |
| L2 | ~2650 skills + 1258 agents + 900 commands as a menu. 15 JTBD packs exist but are not the default. |
| L3 | None. Humans/agents grep and hope. |
| L4 | External roots live in place; no receipts; reindex changes the denominator. |
| L5 | Plant-failure exists for *gates* and *rounds*, not for compression. |
| L6 | Gate-D exists. Tessl login does not. |
| L7 | Outcome lanes + BM25. `misc` = 416. |
| L8 | Five harness roots, install ledger, MCP. |
| L9 | Canonical quality 98.2; weakest 10 lack `great_example`. Tessl review unused (not logged in — and out of scope). |
| L10 | Adding skills is the default move (Limits to Growth). |

Honest: RIG already outruns Tessl on *local proof*. RIG loses on *operator menu*. v20 is the menu+conservation product, not a registry clone.

---

## Why not linear "Tessl features 1–20"

A Tessl clone would be: v1 lint, v2 review, v3 eval, v4 inventory, v5 registry, … That is parameter-level 1000x (Meadows 12–10). This ladder changes the **goal** (L2 doors) and the **paradigm** (L1 isoform) first, then installs proof so the compression cannot lie.
