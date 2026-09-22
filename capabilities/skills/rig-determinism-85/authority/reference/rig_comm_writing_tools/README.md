# D85 A1 certification — `rig_comm_writing_tools` (v1, TERMINAL BLOCK)

Capability under certification: the `writing_tools` integration in
`capabilities/skills/rig-communications-core/rig_comm/integrations/writing_tools.py`
(awesome-writing-tools catalog + alex/write-good/markdownlint wrappers).

## Bindings
- Source snapshot (hash-bound): `authority/sources/rig_comm_writing_tools/writing_tools.py`
  - `sha256 = 62cf6ce30175fef6d2bb7466edf4748b40c746deed1d68ad3e235626e284e4bd`
- Adapter: `writing_tools_adapter.py` — entrypoint `analyze` via `execute`
- Process record: `authority/processes/rig_comm_writing_tools.process.json`
- Registry: `rig_comm_writing_tools` in `authority/registry.json`

## Lattice / BMS (grounded via rig-lattice-system)
- Cell: `L3-D2-A1-Q1` (primary coordinate `L3-D2-A1`)
- BMS: confidence `0.95`, mode `A1` (raw 0.88, altitude +0.12 at L3),
  criteria: failure_cost 0.15, reversibility 0.95, mechanism_clarity 0.85,
  past_failure_rate 0.1, data_volume 0.2

## Gate results (command + exit code)
- `rig-determinism-85 inventory rig_comm_writing_tools` → **BLOCK**,
  `SOURCE_UNSUPPORTED_GRAMMAR` (`writing_tools.py:35`, module-level `Assign`), **exit 2**
  → see `inventory.block.json`
- `classify` → NOT RUN (inventory blocked upstream)
- `score` → NOT RUN
- `checklist` / `verify-cert` → NOT RUN

## Verdict
**A1 certification BLOCKED — terminal for v1. Not certified, not promoted.**

Cause: the D85 A1 closed module grammar admits only straight-line builtin-call
function chains (cf. `authority/sources/julie_synthetic`). `writing_tools.py`
uses module-level constants (`__all__`, `_PINNED`, `TOOLS`), dataclasses, regex,
dict-based dynamic dispatch, and `subprocess` side effects — all outside the
closed grammar; external/opaque side-effect operations also earn zero
determinism credit by taxonomy, so A1 (four ratios ≥ 0.85, no opaque external in
the decision path) is structurally unreachable for a subprocess-orchestration
boundary.

## Remediation (new immutable process id/version only — never a retry of these bytes)
- (a) Certify only the pure deterministic core (catalog + parsers) as a separate
  process, leaving the subprocess wrappers as an explicit side-effect boundary; or
- (b) extend the released D85 closed grammar to admit real module constructs.

Neither is part of, nor was requested by, the "integrate awesome-writing-tools"
task. The integration itself is delivered and test-verified (pytest: 22 passed;
live alex/write-good/markdownlint runs) — that evidence is independent of this
A1 certification block.
