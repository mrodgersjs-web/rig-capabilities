# PROVENANCE — rig-lattice-system

Vendored 2026-09-02. Four sources fused into one installable bundle, two
sources evaluated and rejected, one source lost and rebuilt from its spec.

Everything below is what was actually on disk at copy time, not what a prior
plan expected to find. Where the two disagreed, the disk won and the
discrepancy is recorded.

---

## 1. rig-deviator — the 40 engines, auditor, DES², enterprise layer

| field | value |
|---|---|
| path | `~/Developer/rig-deviate-engines/sources/rig-deviator` (nested git repo) |
| nested repo HEAD | `665f298ae134a19debb09f76249c0fd2730f058a` |
| nested repo branch | `main` |
| outer repo | `~/Developer/rig-deviate-engines` @ `c5c3971c9f2b8b554dbf2233d6e20eec60a409b0` |
| working tree | **dirty** at copy time: ` M criteria/hawking_horizon.yaml`, ` M criteria/quantum_tunnel.yaml` |
| upstream | https://github.com/rodgemd1-lgtm/rig-deviator |
| license | MIT |

**Plan discrepancy, recorded:** the approved plan named commit `c5c3971` on
branch `copilot/rig-v10-git-agent-cli-readiness-design` as the rig-deviator
source. On disk `c5c3971` is the HEAD of the **outer** `rig-deviate-engines`
repo; the nested `sources/rig-deviator` repo is at `665f298` on `main`. The
copy was taken from the working tree as-is — the state the 272-plus vendored
tests were last observed against — including the two modified criteria files.

**Taken:** `core/`, `adapters/`, `engines/`, `criteria/` (44 packs),
`calibration.yaml`, `enterprise/` (verbatim, incl. `integrations/`,
`runbooks/`), `system/`, `dashboard/`, `config/`, `examples/`, `bin/*.sh`,
`REPO_GUARD.md`, `DOCTRINE.md`, `FINAL_REPORT.md`,
`docs/archetypes/README.md` → `docs/ARCHETYPES.md`, and the flat deviator
modules (`auditor.py`, `dv.py`, `modes.py`, `patch_overlays.py`,
`fix_suggestions.py`, `result_packet.py`, `des_squared.py`,
`des2_innerloop.py`, `render_strict_audit.py`, `cli.py`) plus `pipeline/`,
`hooks/`, `reports/` into `rig_lattice/deviator/`. All 9 test suites ported.

**Excluded, with reasons:**

| excluded | reason |
|---|---|
| `.git/`, `__pycache__/`, `*.pyc` | build/VCS noise |
| `.github/` | CI belongs to the rig-capabilities repo that hosts this skill, not to the skill payload. The two tests asserting its presence (`test_github_workflows_exist`, `test_github_meta_files_exist`) were **deleted**, not softened |
| `deploy/launchd/*.plist` | hardcodes the original author's `~/Desktop/rig-deviator` as the working directory — meaningless in a skill installed into five harness roots. `test_daemon_launchd_plist_present` deleted for the same reason; the daemon shell scripts ARE vendored and remain under test |
| `audits/*` contents | runtime output; replaced by `runs/` |
| `explainer/` | 5.8 MB of PNG/SVG diagrams, no runtime role |
| `templates/`, `migrations/` | unused by any vendored call site |
| `slash-commands/` | superseded by `capabilities/commands/rig-lattice-system.md` |
| `baselines/_last_recal.txt` | regenerated artifact |
| `run_audit.py` | **deleted after vendoring.** Every path in it reads `../rig_engines_v2/hed_seed.md` and sibling HED artifacts that do not exist here; there was no non-comparison branch to keep. Its role — "audit a path" — is the CLI's `audit` subcommand |
| `__main__.py` (repo root) | replaced by `rig_lattice/__main__.py` |
| `cli/manifest.json` | superseded by the command asset |

---

## 2. rig-monorepo — the 588-cell data, archetypes, geometry doctrine

| field | value |
|---|---|
| path | `~/Library/Mobile Documents/com~apple~CloudDocs/Desktop/_ACTIVE/rig-studio/RIG-One/rig-monorepo/platform` |
| discovered via | `mdfind` — the plan's `…/RIG-One/rig-monorepo/platform` path did not resolve directly |
| license | none present (internal RIG source) |

**Taken:** `lattice/constants.py` (the corrected geometry doctrine — Z-axis is
BMS, IQRSQPI is the in-cell process), `lattice/bms.py`, `lattice/resolver.py`,
`lattice/generator.py`, and `archetypes/{a1_python_only,a2_hybrid,
a3_agent_bounded,a4_llm_agent_free}/` (25 files, incl. `_types.py`,
`contract.py`).

### The 588 cell contracts are GENERATED, not copied — and proven equivalent

The plan's stated contingency was invoked. iCloud file-provider hydration
delivered ~20 cell files per 180 s (≈9 s/file), which projects to ~79 minutes
for 588 files and crossed the plan's ~10 minute stall threshold. Two copy
attempts were killed by timeout after 63 files.

Rather than vendor a partial set, the 588 contracts were **generated** by the
vendored `lattice/generator.py` — which is itself a copy of the monorepo
generator that produced the originals — and then checked against the files
that had genuinely hydrated:

```
61 of 61 fully-copied originals are byte-identical to the generated output
 2 of 63 "differences" were zero-byte files truncated by the killed copy
588 of 588 shipped contracts are byte-identical to a fresh regeneration
```

The equivalence check is reproducible: `python3 rig_lattice/lattice/generator.py
<tmpdir>` then `cmp` against `rig_lattice/lattice/cells/`. The generator's
byte-for-byte fidelity survived the `DIAMOND_DIGIT` refactor in Step 3 (the
canonical `Diamond` enum now serializes as `D1` while cell filenames keep the
monorepo's bare-digit form), which is re-verified by
`tests/test_bundle_integrity.py::TestCells`.

**Filenames are NOT renamed.** Contracts keep the bare-digit dialect
(`L1-1-A1-I1.yaml`); `generator.load_cell` maps a canonical id onto the
filename.

---

## 3. strategy-studio-pro — BMS formula, validator, build cards, idea bridge

| field | value |
|---|---|
| path | `~/Developer/strategy-studio-pro/strategy_studio` |
| repo HEAD | `e3dc1f7b4707a94cb7654902b54fa979a1b78c7d` (branch `main`) |
| license | `LICENSE` present at repo root |

**Taken:** `lattice/_types_reexport.py` → `lattice/schema.py`,
`lattice/validator.py`, `lattice_wire.py` → `lattice/wire.py`,
`studios/creative_booster.py` → `idea/bridge.py`,
`studios/innovation_ingestion.py` → `idea/innovation.py`. The BMS scoring
formula, `BMSMode.from_score`, `CELL_ID_PATTERN_STRICT`,
`IQRSQPIStep.sequence()` and the altitude-bonus table were fused into
`lattice/constants.py` and `lattice/bms.py`.

**Dropped from `lattice_wire.py`, with reasons:**

| dropped | reason |
|---|---|
| `Diamond.D1_STRATEGY` / `D2_INTELLIGENCE` / `D3_OPERATIONS` | second Y-axis dialect, contradicts the doctrine. Survives only as `constants.LEGACY_DIAMOND_LABELS`, a docstringed lookup, never an enum. The `route_company` keyword sets that encoded it were rebuilt from `DIAMOND_OWNS` |
| `wire_cell_to_engine`, `_execute_a1`..`_execute_a4`, `LatticeOrchestrator` | the B-engine bridge imports `strategy_studio.engines` and `strategy_studio.core.types`, neither of which is vendored — every path would have been an ImportError dressed as a fallback. The orchestration role is filled by `rig_lattice.system.orchestrator.run_system` (7 levels, BMS-routed). Replaced by `archetype_runner(mode)`, which returns the real A1/A2 archetypes and **raises** for A3 |
| the A3 → A1 ImportError fallback | a silent downgrade that reports an A3 result produced by A1 code is exactly the green-that-cannot-go-red this bundle refuses. `archetype_runner("A3")` raises `NotImplementedError("A3 requires an agent runtime; escalate to A4 human gate")` |
| `generate_lattice_map` | Excalidraw diagram emitter, no runtime role |
| `strategy_studio/rig_lattice.py` | back-compat shim mixing both diamond dialects; its only unique symbol `ArchetypeExecutor` is a lazy alias to a LangGraph executor not vendored |
| pydantic `BaseModel` on `LatticeCoordinate`, `BuildCard`, `ProofPacket`, `BMSCriteria`, `BMSScore`, `RouteResult`, `Option` | converted to frozen dataclasses with explicit `to_dict()`; range validation moved into `__post_init__` raising `ValueError`. A1 must be pure stdlib |
| `strategy_studio.core.types.Option` import | replaced by a local `Option` dataclass in `rig_lattice/idea/__init__.py` carrying only the fields the bridge touches |
| `_STUB_WEIGHTS`, `_STUB_ACCEPT_THRESHOLD`, `score_creative_brief` | a second set of accept thresholds that disagreed with the build card's gates. A bundle with two thresholds cannot tell you whether an idea passed |

**Test suites not ported file-for-file.** `tests/test_lattice.py`,
`test_lattice_sio.py` and `test_geometry_sio.py` import
`strategy_studio.hermes.*`, `strategy_studio.session` and
`strategy_studio.core.types` (not vendored) and assert on the dropped diamond
dialect 28 times. Their surviving assertions — 147 legacy-shape cells, 588
cells, 84 primaries, 28 archetypes, BMS selection/adjustment/clamping, both
cell-id formats — were rewritten against the unified API as
`tests/test_lattice_math.py`.

---

## 4. Creative Booster V3.1 — spec for a lost implementation

| field | value |
|---|---|
| build card | `/Users/rig128gb/scratch/recall_import/RIG Architecture/Creative Booster Scoring Gates — RIG Build Card for Deterministic + Probabilistic Idea Evaluation (V3.1).md` |
| implementation | **lost** — the private `rig-creative-booster` repo 404s under both `rodgemd1-lgtm` and `RIGIntelligence` |
| last known metadata | pushed 2026-06-09, 269 tests, 95% coverage |

`rig_lattice/idea/booster.py` is a deterministic rebuild of the card's
Master Creativity Function and its four gates. The optional package import
path is preserved in `idea/bridge.py`: if a clone ever surfaces it wins
automatically and `booster_available()` reports `"package"` instead of
`"builtin"`. The rebuilt core is not deleted in that case — it is the offline
default and the source of the gate fixtures.

**Two declared proxies.** Two of the card's fifteen sub-formulas specify
machinery unavailable offline. Each carries a module-level comment naming what
it approximates and what would replace it, and every score reports them in a
`proxies` field:

| term | card specifies | shipped proxy |
|---|---|---|
| `N_vendi` | `exp(H(eigenvalues(K)))` over an embedding similarity matrix (Vendi Score) | normalized max n-gram distance to the supplied corpus |
| `S_bayesian` | `D_KL(P_post ‖ P_prior)` | count of claims contradicting the corpus's modal claim, normalized |
| `G` third term | inverse cliché embedding distance | folded into the n-gram overlap term |

**One documented extension to the gates.** The card's §3.2 trigger pair is
`Usefulness > 0.70 and DeviationScore < 0.40`. Its §1 defines the failure mode
that gate guards more broadly — "practical but median, boring, copyable, and
indistinguishable from competitor output" — where the distinguishing property
is median-ness, not usefulness. A buzzword artifact with no receipts scores
`usefulness = 0` and so escapes the literal pair while being the purest
instance of the failure. The gate therefore carries a second, explicitly
documented arm: `deviation < 0.40 and generic_penalty >= 0.85 and
proof_density <= 0.2` → **reject** (not revise: "revise" presumes a mechanism
worth keeping). Both arms are covered by
`tests/test_idea_gates.py::TestGateThresholds`.

---

## 5. Rejected sources

| source | reason |
|---|---|
| `~/Developer/rigforge-deterministic-platform` | local checkout contains zero lattice code; its upstream (renamed `rodgemd1-lgtm/rigforge`) carries a fifth, untested keyword-table lattice implementation |
| `~/Developer/RIG-AI-Engineering-pro` | the `LATTICE` dict at `python/rig/prompt_engine.py:39-44` is unrelated, mislabelled data |
| `~/Developer/rig-linkedin-studio-luca/alfred/deviation_pipeline.py` | a *consumer* of engine codenames (COLLIDER/SURPRISE/BREAKER/…), not an engine implementation. It stays in the GTM repo; this bundle ships only the codename→engine-id alias table it needs (`rig_lattice/engine_aliases.py`) |

---

## 6. Known upstream data conflict, preserved

Engine `e15` is `hermeneutic_density` / `SourcePerClaim` — per-claim source
weighting, which is the **WITNESS** engine (cf. the `rig-witness` skill:
"Per-claim source weight; method transparency"). Its criteria pack
(`criteria/hermeneutic_density.yaml`) is labelled `codename: WELLSPRING`,
which is a different concept entirely (Hedonic Adaptation Resistance, cf. the
`rig-wellspring` skill).

Both codenames resolve to `e15` in `engine_aliases.py` rather than silently
dropping one, so either caller works. The mislabel is upstream and is recorded
here rather than "fixed" by guessing which artifact is wrong.

---

## 7. Behavioral changes made during vendoring

Every change below altered observable behavior and is deliberate. Everything
else was carried verbatim.

| change | reason |
|---|---|
| `system/persistence.py`: `from core.registry import REGISTRY` inside a bare `except Exception` → `from rig_lattice.core.registry import ENGINE_REGISTRY as REGISTRY`, error propagating | the exported name is `ENGINE_REGISTRY`; the old import always failed and silently zeroed `slug_to_id`, so every `engine_score` row fell back to a positional index. Letting it propagate immediately exposed a second latent bug: the field is `EngineSpec.id`, not `.engine_id` — also fixed |
| `adapters/llm.py`: `OFFLINE_MODE` constant → `offline_mode()` live read | the constant was evaluated at import time, so any process setting `RIG_DV_OFFLINE` after the first import was ignored — the documented env switch did not work. `OFFLINE_MODE` remains as a back-compat snapshot |
| `enterprise/integrations/litellm.py`: check `offline_mode()` **before** reaching for litellm | `RIG_DV_OFFLINE=1` means "make no outbound model call"; the vendored order called the network first and only degraded on the resulting exception |
| `pipeline/approval_client.py`: `RIG_DV_AUTO_APPROVE` default `"1"` → `"0"`; new `request_approval()` returning `(False, "approval_required_no_client")` | shipping an auto-approving approval gate into five coding agents is a Gate-D bypass. The `"1"` path stays for tests that opt in explicitly |
| `deviator/auditor.py` + `adapters/criteria_runner.py`: YAML load → `_load_criteria()` preferring compiled JSON | rig-capabilities is stdlib-only; PyYAML is now a compile-time dependency of `scripts/compile_criteria.py` only. A missing pack raises `FileNotFoundError`; a stale compile with no PyYAML raises `RuntimeError` naming the fix |
| `render_strict_audit.py`: legacy Desktop path (`~` + `Desktop` + `HED-v2.5-Strict-Audit.html`, de-literalised per host-hygiene rule) → `runs/<timestamp>-strict-audit.html`, `--out` flag | a skill installed into five harness roots has no business writing to a user's Desktop |
| all runtime writes: `<ROOT>/audits/…` → `runs/` via `rig_lattice/_paths.AUDITS_DIR` | one writable directory per install, overridable with `RIG_LATTICE_RUNS_DIR` |
| `auditor.py`, `dv.py`, `adapters/llm.py`: hardcoded QNAP-tailnet URL (`http://<redacted-tailnet-ip>:11434`; literal removed per host-hygiene rule — the value is the author's own tailnet host and must not ship) → `RIG_LATTICE_LLM_URL` env with a `127.0.0.1` default | the QNAP tailnet host is not reachable from an arbitrary install. `RIG_DV_LLM_URL` is kept as a deprecated alias, read first |
| `enterprise/iqrsqpi.py`: local `BMSMode`, `BMS_THRESHOLDS`, `route_bms`, `Dimension`, `TOTAL_CELLS`, `LatticeCell`, `all_cells` → re-exports from the canonical modules | five implementations of one doctrine is how the four repos diverged. `route_bms` stays as a thin wrapper because `tests/test_enterprise.py` calls it by name |
| `docs/DOCTRINE.md` §1.2 | the "1,680 evaluation cells" block (40 engines × 6 audience tiers × 7 steps) is wrong and was replaced with the 588 geometry plus a sentence naming the superseded number, so the change is auditable |
| A4 prose | "free-form multi-agent Opus crews" replaced with "A4 LLM_AGENT_FREE — adversarial, model-free decision path, mandatory human approval" wherever it appeared |
| `sys.path.insert` (22 sites) deleted; all intra-tree imports rewritten to `rig_lattice.*` | top-level names `core`, `engines`, `cli`, `auditor`, `dv`, `system` are collision-prone and must never enter `sys.path` |

## 8. Deliberate deviation from the plan

**`archetypes/a1_python_only/_types.py` keeps its pydantic-optional path.** The
plan's Step 2.4 listed it among the files to de-pydantic. On inspection it
already carries a stdlib dataclass fallback with the same field surface and a
`.model_dump()`, and it imports cleanly with pydantic blocked
(`PYDANTIC_AVAILABLE = False`). Rewriting it would delete working validation
when pydantic *is* present, for no gain to the determinism contract it already
satisfies. Instead the property is now proven by
`tests/test_bundle_integrity.py::TestStdlibOnly::test_archetype_contract_types_import_without_pydantic`,
which blocks the import and asserts the module still loads — a stronger claim
than the rewrite would have produced. The `lattice/` modules named in the same
step WERE de-pydantic'd, and a test asserts no module under `lattice/` imports
pydantic.
