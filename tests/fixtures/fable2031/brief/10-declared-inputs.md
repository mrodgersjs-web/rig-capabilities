## 1. DECLARED INPUTS

These are the only inputs you may rely on. Every one is a real path on disk, verified present by the
orchestrator at brief-freeze time (bytes and sha256 of each card match the manifest exactly). If a
path will not open, say so in S1 — do not substitute memory, inference, or a plausible reconstruction.

### 1.1 The nine source cards (`data/fable2031/source_inventory.json` is the manifest of record)

| # | id | title (frontmatter `title:`, verbatim) | bytes | status |
|---|---|---|---|---|
| 1 | `prompt-pack-2031-chain` | PROMPT PACK — Full-Corpus Scrape → Grok Extraction → Fable 5.1 Capability Map (2031 Design Chain) | 991 | **truncated_at_source** |
| 2 | `claude-fable-5-1-fleet-install` | Claude Fable 5.1 — RIG Fleet Install, Routing Policy & Breaking-Change Audit (shipped Sept 1, 2026) | 6287 | complete |
| 3 | `rig-realign-loop-v1` | BUILD CARD — RIG Realign Loop v1: Weekly Strategy → Research → Design → Execution → Learnings with Convergence Scoring | 6113 | complete |
| 4 | `rig-capability-criteria-2031` | RIG CAPABILITY CRITERIA & 2031 ROADMAP — The M0–M5 Ladder, Register Schema, Weight Tiers & Phase Gates (v1) | 7103 | complete |
| 5 | `rig-1000x-car-v2` | RIG 1000x CAR v2 — The Forward-Deployed Chassis: Every Subsystem Turned Outward + Scrutineering as the Commercial Object | 7693 | complete |
| 6 | `rig-gap-register-v1` | RIG GAP REGISTER v1 — Every Missing Capability, Ranked by Blast Radius × Revenue Proximity (Worst-Harness-First Fix Order) | 1505 | **truncated_at_source** |
| 7 | `grok-dispatcher-system-prompt-v1` | PROMPT — Grok Dispatcher System Prompt (Anti-Fabrication, Worktree-Leased, Canary-Gated) v1 | 7105 | complete |
| 8 | `rig-anti-fabrication-harness-v1` | RIG ANTI-FABRICATION HARNESS — Grok Dispatcher Protocol: Worktree Leases, Canary Lie-Detection & Reproducibility-as-Truth (v1) | 7039 | complete |
| 9 | `rig-known-expert-os-v1` | RIG Known Expert OS — 12-Phase Master Prompt for a Forward-Deployed AI Strategist & Engineer | 20559 | **truncated_at_source** |

Exact paths (all in `/Users/rig128gb/Downloads/`; read them, do not paraphrase them from memory):

1. `/Users/rig128gb/Downloads/PROMPT PACK — Full-Corpus Scrape → Grok Extraction → Fable 5.1 Capability Map (2031 Design Chain).md`
2. `/Users/rig128gb/Downloads/Claude Fable 5.1 — RIG Fleet Install, Routing Policy & Breaking-Change Audit (shipped Sept 1, 2026).md`
3. `/Users/rig128gb/Downloads/BUILD CARD — RIG Realign Loop v1 Weekly Strategy → Research → Design → Execution → Learnings with Convergence Scoring.md`
4. `/Users/rig128gb/Downloads/RIG CAPABILITY CRITERIA & 2031 ROADMAP — The M0–M5 Ladder, Register Schema, Weight Tiers & Phase Gates (v1).md`
5. `/Users/rig128gb/Downloads/RIG 1000x CAR v2 — The Forward-Deployed Chassis Every Subsystem Turned Outward + Scrutineering as the Commercial Object.md`
6. `/Users/rig128gb/Downloads/RIG GAP REGISTER v1 — Every Missing Capability, Ranked by Blast Radius × Revenue Proximity (Worst-Harness-First Fix Order).md`
7. `/Users/rig128gb/Downloads/PROMPT — Grok Dispatcher System Prompt (Anti-Fabrication, Worktree-Leased, Canary-Gated) v1.md`
8. `/Users/rig128gb/Downloads/RIG ANTI-FABRICATION HARNESS — Grok Dispatcher Protocol Worktree Leases, Canary Lie-Detection & Reproducibility-as-Truth (v1).md`
9. `/Users/rig128gb/Downloads/RIG Known Expert OS — 12-Phase Master Prompt for a Forward-Deployed AI Strategist & Engineer.md`

The manifest itself: `/Users/rig128gb/Developer/rig-capabilities/data/fable2031/source_inventory.json`
(nine entries, `cards:` begins at line 6; each entry carries `id`, `path`, `sha256`, `bytes`,
`status`, `end_anchor`).

### 1.2 The three truncation anchors — named explicitly, and final

`rig_capabilities.corpus.detect_truncation()` returns exactly these, and the manifest agrees:

- **Card 1 — anchor `| QNA |`.** The card dies at line 24 of 27, mid table. Lines 21–24 are
  `## Source systems to sweep`, `| System | Content |`, `| --- | --- |`, `| QNA |`. The table has no
  further rows. **`QNA` is a fragment of an unknown name.** See §2.3.
- **Card 6 — anchor `No capability register.` immediately followed by a bare `Z`.** The last content
  line of the card is line 19, verbatim `**3. No capability register.**Z`. Gaps 1 and 2 survive
  (line 15 `**1. No steering column — no client intake service.**…`, line 17
  `**2. No public surface — no website, no ads.**…`). **Gaps 4 and beyond do not exist on disk.**
- **Card 9 — anchor `## Sources`.** The card ends at 530 lines: line 522 `# Phase 11 — Turn the
  system into the RIG offering`, line 524 `## Objective`, line 525 the one-line objective
  `Translate the validated expertise into a bounded offer.`, then line 529 `## Sources` and line 530
  a single `- [website](https://www.youtube.com/watch?v=vl6GDCbMi4I)` bullet. **Phase 11 has no body,
  no deliverables, and no gate. Phase 12 is absent entirely — no heading, no objective, no gate.**
  Gates 1–10 exist (`### Gate 1` :165, `### Gate 2` :207, `### Gate 3` :255, `### Gate 4` :299,
  `### Gate 5` :342, `### Gate 6` :377, `### Gate 7` :416, `### Gate 8` :449, `### Gate 9` :488,
  `### Gate 10` :514). **There is no Gate 11 and no Gate 12 anywhere on disk.**

### 1.3 The Known Expert OS phase / gate table (transcribed in `rig_capabilities/expert_os.py`)

Phases 1–10 are **gated**. Phase 11 is **objective_only_truncated**. Phase 12 is
**absent_at_source**. (`PHASES` :31, `PHASE_STATUS` :53, `PHASE_11_OBJECTIVE` :69, `GATES` :72 — the
`GATES` mapping has keys 1..10 ONLY, and `GATES[11]`/`GATES[12]` raise `KeyError` by design.)

| Phase | Title (verbatim) | Status | Gate on disk? |
|---|---|---|---|
| 1 | Select the problem to own | gated | Gate 1 |
| 2 | Reverse-engineer the market and target roles | gated | Gate 2 |
| 3 | Mine scars, decisions, and proof | gated | Gate 3 |
| 4 | Construct the category point of view | gated | Gate 4 |
| 5 | Create signature intellectual property | gated | Gate 5 |
| 6 | Build the guinea-pig reference implementation | gated | Gate 6 |
| 7 | Convert positioning into résumé evidence | gated | Gate 7 |
| 8 | Engineer the interview system | gated | Gate 8 |
| 9 | Build the searchable expertise architecture | gated | Gate 9 |
| 10 | Run the 90-day MAP deployment | gated | Gate 10 |
| 11 | Turn the system into the RIG offering | **objective_only_truncated** | **none** |
| 12 | *(no title exists — the phase is absent)* | **absent_at_source** | **none** |

Depth ladder (`rig_capabilities/expert_os.py:139`, `:147`): `L1_surface`, `L2_synthesis`,
`L3_scar`, `L4_judgment`, `L5_procedure`, with `MIN_PUBLISHABLE_DEPTH = "L3_scar"`.

### 1.4 The register schema — all 22 columns, read from `capability_register.csv`

Header of `/Users/rig128gb/Developer/rig-capabilities/capability_register.csv` (line 1), **22
columns, in this exact order**; the file currently holds **21 data rows**:

```
id, name, subsystem, studio, type, maturity_M0_5, automation_band, weight_w,
evidence_paths, harness_signed, verifier_named, proof_status, target_M_2031,
target_band_2031, blocking_deps, enables_product_classes, duplicate_of,
contradicts, last_touched, owner, source_document_ids, contradiction_group
```

Columns 1–20 are the criteria-card fields (card 4, `## Register schema`, lines 60–84).
`source_document_ids` and `contradiction_group` are the two additive reconciliation cells.
Authoritative enums and validation live in `rig_capabilities/register.py` (`REGISTER_FIELDS` :25,
`SUBSYSTEMS` :50, `STUDIOS` :55, `TYPES` :58, `BANDS`/`TARGET_BANDS` :62/:64, `PROOF_STATUS` :65,
`validate_row` :213):

- `subsystem` ∈ chassis | powertrain | transmission | turbo | tires | seatbelts | fuel | spark |
  navigation | sound | shocks | steering | aero | scrutineering
- `studio` ∈ Design | App | GTM | LinkedIn | Strategy | CompanyOSFactory
- `type` ∈ workflow | harness | doctrine | tool | repo | dataset | asset | offer
- `maturity_M0_5` 0–5 · `weight_w` 1–5 · `target_M_2031` 0–5
- `automation_band` ∈ A1 | A2 | A3 | A4 | manual; `target_band_2031` ∈ A1 | A2 | A3 | A4 (no `manual`)
- `proof_status` ∈ none | golden_run | proofpacket_sealed | replay_passing
- `evidence_paths` **must be non-empty** ("no path, no row"); `enables_product_classes` **must be
  non-empty** (the mandatory mesh edge); `harness_signed` boolean; `last_touched` ISO date; `owner`
  required; `maturity_M0_5 >= 4` with no `verifier_named` → row rejected and the owner flagged.
- **`booked_qualified_conversations` is mandatory at `weight_w = 5`** (`BOOKED_ID`/`BOOKED_WEIGHT`
  :69/:70). It already exists as row 3 of the CSV. Do not create a second revenue row.

### 1.5 The `E_stage` contract (`rig_capabilities/estage.py`)

- Promotion-gate string pinned on the route and on all six golden manifests:
  `DORMANT_PER_STUDIO_UNTIL_E_STAGE_LOWER_THAN_OPUS5` (`rig_capabilities/model_route.py:37`).
  All six Studios (`capabilities/golden/{Design,App,GTM,LinkedIn,Strategy,CompanyOSFactory}/missions.json`)
  are `status: DORMANT`, `recorded_under: null`, `baseline_recorded: false`, 3 missions each,
  `verifier_family: opus`, `candidate_family: fable`. **No baseline replay has been recorded anywhere.**
- `E_STAGE_WEIGHTS = {"fail": 0.6, "cost": 0.25, "turns": 0.15}` (`estage.py:37`). Lower is better.
  `fail_loss` = 1.0 if any blocking gate missed, else the mean of (1 − score) over scored gates,
  else 0.0 (`:131`). `cost_loss` = clamp(`cost_usd` / declared `cost_budget_usd`); `turns_loss` =
  clamp(`turns` / declared `turn_budget`) (`:152`). Budgets are **declared ceilings**, never
  measurements; a missing/zero ceiling raises `GoldenSetInvalid` rather than contributing a free term.
- `compare(baseline_runs, candidate_runs)` (`:228`) pairs by `mission_id`; a missing or extra
  mission id raises `GoldenSetInvalid`.
- `promotion_verdict(studio, cmp, spend)` (`:276`) returns `promote: True` only with an empty
  reasons list — i.e. strictly lower E_stage on **every** mission of that Studio, mean improvement,
  no blocking-gate regression, `candidate_family != verifier_family` (else
  `same_family_collusion`), matching `manifest_signature`/`replay_signature`, and no
  `forced_tool_choice_harness`.
- `AUTO_FALLBACK_TO_EARLIER_FAMILY = False` (`:40`) — pinned. Earlier families cannot read Fable 5.1
  thinking blocks, so a failed Fable mission terminates FAIL/BLOCKED; any later Opus attempt is a
  NEW mission with its own `mission_id` and its own E_stage.
- Kill criteria / revocation (`:44`–`:46`, `revocation_check` :352): spend growth > 30 % across a
  two-week window with no C_t movement ⇒ `revoked: True`, remedy `revert to Opus 5`; fewer than
  three weekly observations ⇒ `insufficient_history`, never an invented baseline.
  `rebaseline_required` (`:386`): a baseline not recorded under the candidate family (or with
  unknown provenance) must be re-baselined.

### 1.6 Honest current state — quote this, never contradict it

- **Bookings are ZERO by evidence.** `data/fable2031/bookings-2026-W36.json` has `"records": []`
  (line 3) and a note stating no booked qualified conversation has qualification evidence on disk as
  of 2026-09-01. Zero is the evidenced count, not an omission.
- The weekly gate (`rig_capabilities/convergence.py`, `weekly_gate`) PASSes only when ΔC_t > 0 AND
  ΔA_t ≥ 0 AND unclassified_rate ≤ 10 % AND booked qualified conversations > 0 AND no unresolved
  ≥5σ flag. With zero bookings it cannot PASS today. With no prior sealed week, the honest answer is
  `BASELINE_ONLY`.
- `capability_register.csv` = 21 rows, 20 of them at `maturity_M0_5` = 2;
  `booked_qualified_conversations` is M0, `manual`, `weight_w = 5`, `proof_status: none`.
- Fable 5.1 is **dormant** in all three route registries pending Gate-D; the `E_stage` baseline does
  not exist yet.

### 1.7 Supporting repo artifacts you may read (all under the repo root)

`docs/DONE-CONTRACT-2031.md`, `docs/ASSUMPTIONS.md`, `docs/CONFLICT-RESOLUTIONS.md`,
`docs/TRUNCATED-SOURCES.md`, `docs/ROADMAP.md`, `evidence_ledger.csv` (6 rows; E-005 `planned` and
E-006 `inferred` are `internal` only), `data/fable2031/classify_rules.json`,
`rig_capabilities/{corpus,register,convergence,realign,expert_os,evidence_ledger,estage,model_route,lease,canary,dispatcher,iqrsqpi_v10,afproof,certify,proofchain}.py`,
`capabilities/golden/*/missions.json`.

---

