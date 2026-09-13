# Mint-anchor decision — the four instruction-surface approvals (for Mike)

Nothing was regenerated, nothing was repointed, no approval was minted. This is the
decision, with the mechanism verified in the code that enforces it.

## What the anchor actually is

`rig_capabilities/surfaces_render.py:37` — `GATE_D_PROCESS = "build_standard_chain_v1"`.
The staged `mint_command` (`surfaces_render.py:185-188`) computes
`v = g.score_realized(g.AUTHORITY_REGISTRY, 'build_standard_chain_v1')` and binds
`inventory_sha256`, `classification_sha256`, and `realized_sha256 = _canonical_hash(v)`
into the signed row. The arm path (`surfaces_render.py:135`) calls
`arm_gate_d(GATE_D_PROCESS, action)`.

So the anchor is **the build-standard chain process**, named per-activity, matching the
estate's own naming (`build_standard_chain_v1`, `estate_automation_ledger_v1`).
`d85_register_selftest_v2` is a registrar selftest that already scores clean
(inventory `974f410925e936b6…`, classification `6e38918c281fc014…`); it has nothing to do
with writing `CLAUDE.md` / `SOUL.md` / `AGENTS.md`.

## Why mint is blocked today

`_estate_external_locks` (`d85_gates.py:909`) derives external-module locks
automatically from the registered sources' imports: `allowed_calls` come from the AST,
the artifact path and sha come from `_deterministic_module_origin`, and every entry is
validated through `d85._external_lock_entry`. Validation requires the callee to exist in
the module's AST surface, and `d85._surface_of_py` indexes only defs, classes, submodule
imports, and module-level `def`-shaped bindings. Two stdlib symbols are not there:

- `hashlib.sha256` — `hashlib.py:307` materializes it at import time via
  `globals()[__func_name] = __get_hash(__get_builtin(...))`.
- `os.environ.get` — `os.py:769` assigns `environ = _createenviron()`.

Hence `EXTERNAL_CALL_UNRESOLVED: hashlib.sha256: missing 'sha256'` and
`os.environ.get: opaque at 'environ'`, and no `.classification.json` for either process —
by design, because inventory refuses before a hash exists. The declarations were never the
gap: the registrar re-run is byte-identical. **This is an analyzer-resolution gap, not a
data gap** (the earlier D85-Score todo said otherwise; corrected).

## The three options

| | option | what it costs | what it means for the audit trail |
|---|--------|---------------|-----------------------------------|
| **a** | Teach `d85._surface_of_py` dynamic stdlib materialization: module-level `globals()[name] = factory(...)` and module-level `name = call(...)` count as surface members. | Smallest real change, but it edits the most load-bearing analyzer in the estate. Mandatory plant tests: a fixture module that materializes a symbol must accept the lock, and one that does **not** materialize it must still go RED — otherwise the escape probe is quietly weaker than it was. Needs the full suite, solo. | The approval binds the process that actually performs the action. Auditor sees the analyzer widened, with a test proving the widening has a floor. |
| **b** | Restructure the two registered processes so `hashlib` / `os.environ` never appear in their reachable sources (hashing behind a pinned external artifact rather than a stdlib import). | Real refactor of two estate processes to route around an analyzer limitation, and a *new* artifact to pin and trust. | Same honest binding, at the price of contorting the estate for the tool's benefit. |
| **c** | Repoint `GATE_D_PROCESS` at `d85_register_selftest_v2`, which scores today, and state the caveat on the face of each Gate-D request. | One constant in `surfaces_render.py`, plus regenerating the four staged `mint_command`s and diffs. | Four instruction-surface approvals get bound, in the append-only signed ledger, to a synthetic registrar selftest. An auditor reads: a selftest vouched for production writes to `CLAUDE.md`. **Recommend against** — that is gate theater with paperwork. |

**Recommendation: (a).** If you want surface writes before (a) or (b) lands, the honest
answer is that there is none available — the four surfaces stay dormant, which is their
current state (`surface check` exits 2).

## The mint→consume rule, stated correctly

The earlier phrasing ("mint and consume must share one interpreter context") was too
strong. The enforced rule, from `d85_gates.py:522-574`:

1. `gate_d()` **re-runs `score_realized`** at the effect moment.
2. Any approval row for that process whose `inventory_sha256`, `classification_sha256`,
   or `realized_sha256` differs from the recomputation → `BLOCK_GATE_D_MISMATCH`. It does
   not skip it — it blocks the whole call.
3. Expired → `BLOCK_GATE_D_EXPIRED`; lifetime capped at 24 h, default 1 h.
4. Consumption is one-time: an `O_CREAT|O_EXCL` marker per `(run_id, action_sha256)`.

So the real invariant is **no drift in the registered bytes between mint and arm**.
Same interpreter context is one sufficient way to get it, not the requirement itself.
Practical consequence: mint, get the typed approval, and arm within the hour, and do not
edit any file reachable from the registered process in between — otherwise the approval
mismatches and must be re-minted. `commit_gate.py:325-327` already encodes the related
rule: readiness checks replay Gate-D read-only and never consume; only `arm_gate_d` at
the effect consumes, and its `ARMED` verdict is the execution receipt.

## What is staged and untouched

`runs/agentic-stack-buildout/gate-d/surfaces/{claude_code,hermes,omp,prime_agent}/` —
candidates, diffs, exact action files, `PENDING_MIKE_TYPED_APPROVAL`. Zero bytes written
to any target; target sha and mtime unchanged. Policy bytes unchanged
(`8501a8c9…`), so whichever anchor wins, the staged diffs do not need rewriting — only
the `mint_command` line does, and only under (c).
