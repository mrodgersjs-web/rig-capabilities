# Databricks × RIG Lattice — Mission Spec

Standard: **D85 deterministic admission.** No process in this workstream is durable
until all four determinism ratios score ≥ 0.85 via
`rig-determinism-85 score <process_id>` (weights 5/5/3/2/1/1).

## Non-negotiables (written in, per doctrine)
1. **CODE owns the control plane.** Every critical control and side-effect
   operation (SQL submission, job trigger, credential use, resource provisioning)
   is deterministic code with closed-schema inputs. The model may choose
   parameters only within a deterministic envelope; it never free-forms SQL
   writes, DDL, or API mutations.
2. **D85 admission ≠ Gate-D.** A process passing the four-ratio score is
   ELIGIBLE; every outward or irreversible effect (query cost spend, cluster
   start, data write, share/ACL change) additionally needs a typed Gate-D
   approval for the exact action. No inherited approvals.
3. **Tool selection is deterministic.** Verdicts come from
   `rig-determinism-85 select <evidence-file>` over closed-schema evidence
   records: absent claims FALSE, contradicted BLOCK.
4. **Builds bind to inventory snapshots.** `checklist <build-file>
   --process-id <id>` recomputes live inventory; unbound/stale/mismatch → BLOCK.
5. **Bounded model use** only where deterministically necessary (drafting read
   queries for review, summarizing results). Every model artifact lands as a
   proposal for code-side validation, never as an executed effect.
6. **Plant-failure verification** on every gate trusted here: prove the gate
   goes RED on a planted defect, restore, keep as regression.
7. **ProofPackets seal** each claimed outcome: command, exit code, artifact
   hash. No seal → no claim.

## Target architecture (initial)
- `databricks-connection` (registered process): PAT/OAuth token in env/secret
  store, never in repo; workspace URL in `build.json`.
- `rig-lattice run databricks_<playbook_id>`: deterministic runner that
  executes registered playbooks (read queries, metrics refresh, data QA) via
  Databricks SQL Statement Execution API; all writes behind per-action Gate-D.

## Gate state (2026-09-10, verified)
- Startup gate PASS in this cwd (`hard_stop: false`; only non-blocking `live:cognee` DEGRADED).
- Live score red-path proven: `score databricks_lattice` →
  `{"reason":"UNKNOWN_PROCESS","verdict":"BLOCK"}` exit 2 (canonical CLI,
  /Users/rig128gb/Developer/rig-capabilities). Nothing registered; canonical
  authority untouched.
- Registration blocker found while probing grammar: the extractor admits ONLY
  local modules + `__future__`; every stdlib import (urllib, json, os) needs a
  closed `external_modules` lock with pinned artifact sha256 — a real closure
  must be built against the ACTUAL worker source, not guessed. Registration
  resumes when the real source exists.
- No Databricks workspace URL or auth mode exists anywhere on this host
  (no ~/.databrickscfg; no substrate references).

## Required from Mike (exact)
1. Workspace URL + auth mode (PAT / OAuth / SSO browser session).
2. First surface: SQL warehouse vs Jobs vs Unity Catalog scope.
3. Typed Gate-D approval per effect once the action packet is real; and the
   open commit-route decision gating the frozen break-glass install.

## Browser note
OMP browser is eval-routed; `eval` is DENIED in-session by live D85 (table row:
"Arbitrary-code tool while protected roots active → DENY, even with a path
admission"). The earlier cua-driver failure was an ended MCP session, not D85 —
browser automation becomes available after authorization via its own consent
path, or the connection runs API-side through the registered process.

## Verified schemas (read from implementation, 2026-09-10 — do not re-derive)
Sources: `rig-determinism-85/{d85.py,d85_gates.py,tool_selection.py}` +
`authority/reference/julie_synthetic/` in the canonical checkout.
- Registry (production read, ONLY): `authority/registry.json`
  `rig.d85.authority-registry.v1` = `{schema, processes:{id: rel-path}}`.
  ~/.rig/d85/processes/*.process.json are DRAFT cards, never registration.
- Process record `rig.d85.process-authority.v1` — 6 required keys: `schema,
  process_id, source_root, file_hashes, external_modules, entrypoints`, plus
  optional `classification_path` (read by d85_gates). entrypoint =
  `{source_path, symbol, adapter_path, adapter_operation}`. `source_root` is
  an absolute path and MAY point at this project's `sources/` — no product
  copy under `authority/sources/`.
- Imports: only local modules + `__future__` admitted; EVERY other import
  needs an `external_modules` lock `{module, artifact_path, artifact_sha256,
  allowed_calls}` — single plain .py artifact, exact-hash pinned.
- Classification `rig.d85.classification.v1` — exact 5 keys: `schema,
  process_id, inventory_sha256, operations, model_necessity`. Operation =
  `{inventory_id, runtime_kind, taxonomy, predecessors, successors}`;
  runtime_kind ∈ CODE|MODEL|MODEL_AGENT|MIXED|HUMAN; taxonomy weights
  control plane 5 / side effect 5 / decision 3 / transformation 2 /
  retrieval 1 / presentation 1; threshold 0.85.
- Build record (input; no `schema` field) — exact 10 keys: `process_id,
  inventory_sha256, framework, properties, durable_system, pydantic_models,
  model_necessity_claims, archify_diagram_path, d85_realized_pass,
  orchestration_is_code` (see julie_synthetic/build.json). The checklist
  verdict/certificate it emits uses schema `rig.d85.build-checklist.v1`.
- Sequence: register (registry edit = authority/Gate-D event, immutable
  version) → `inventory` → classification bound to inventory_sha256 →
  `classify` → `score` → `checklist build.json --root R --process-id ID`
  (bound CHECKLIST_PASS only) → `verify-cert` → `gate-d ID --action file`.
- Scope note: `enforcement.json` roots do NOT include
  ~/Developer/rig-capabilities — exact-path admission (d85adm) and Gate-D
  authority approval are different events; registry mutation needs the latter
  regardless of the former.

## Companion documents (same directory)
- `PARTNER_ANALYSIS.md` — dated, source-URL-per-row target matrix with
  A-verified / B-lead / C-hypothesis tiers. Partner claims in any downstream
  artifact MUST cite its rows; no relationship may be presented without a
  Tier-A row or an explicit hypothesis label. Pending validation: live partner-
  directory crawl (browser path currently D85-gated).
- `VIDEO_BRIEF.md` — marketing-cut and demo-cut acceptance sets (distinct),
  Higgsfield scoped to B-roll/transitions only after real product capture exists.

## Publication dependency (corrected 2026-09-10)
- Publishing THIS spec is bound to a **registered deterministic git-publication
  process** (score ≥0.85 + `gate-d <pub-process> --action <push-action-file>` +
  typed approval). No such process is registered → that is the authority gap;
  `databricks_lattice` runtime work is NOT its precondition.
- Jake gate-d ledger request `gd_1789072285353` alone is insufficient; commit
  `f6535c3` stays local until the publication process passes. Repo is PRIVATE
  (origin `mrodgersjs-web/rig-capabilities`, fable-2031 ahead 1) — visibility does
  not waive the gate.
