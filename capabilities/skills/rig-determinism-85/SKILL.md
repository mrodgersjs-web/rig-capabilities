---
name: rig-determinism-85
description: Enforces the deterministic-admission chain — source-derived operation inventory, authority classification, four-ratio D85 scoring, exact-action Gate-D, and agent-surface wiring. Use when registering, classifying, scoring, or arming a process, or verifying surface wiring.
---

<objective>
Build the reachable Python operation graph from a fixed authority registry, classify every extracted operation from a separate authority file, require all four determinism ratios at or above 0.85, authorize one exact outward action through signed one-time Gate-D approval, and verify that all four coding-agent surfaces carry the same doctrine marker. Every gate fails closed with exit 2 and a BLOCK JSON verdict.
</objective>

<current_boundary>
This capability owns the realized admission chain: inventory, classification, scoring, Gate-D arming, and surface-wiring verification. It does not execute effects, dispatch outward actions, register live agent hooks, or seal proofs. An `ARMED` Gate-D verdict authorizes exactly one action envelope; the effect itself stays with the calling tool.
</current_boundary>

<process>
1. Add a process record under `authority/processes/` plus its registry entry in `authority/registry.json`.
2. Bind the record to an absolute source root, exact file SHA-256 values, source entrypoints, adapter operations, optional locked single-file external modules, and a `classification_path`.
3. Run `bin/rig-determinism-85 inventory PROCESS_ID` and `compare PROCESS_ID INVENTORY_FILE` when an inventory is submitted for equality checking.
4. Author `classification_path` with one record per extracted operation ID: runtime kind, taxonomy, and remapped graph edges. Declare a typed necessity record for every MODEL operation.
5. Run `bin/rig-determinism-85 classify PROCESS_ID` — mints final operation identities from provisional IDs plus classification bindings.
6. Run `bin/rig-determinism-85 score PROCESS_ID` — requires `REALIZED_PASS` on all four ratios.
7. For an outward or irreversible action: mint a signed approval with `d85_gates.mint_approval` (authority operator), then run `bin/rig-determinism-85 gate-d PROCESS_ID --action ACTION_FILE`. The action file is the exact pre-tool envelope; one arm consumes one approval.
8. Run `bin/rig-determinism-85 wiring` to verify all four surfaces carry the doctrine marker recorded in `authority/surfaces.json`.
9. Stop on exit 2. Create a new immutable process authority version before retrying.
</process>

<rules>
- The production command reads only `authority/registry.json`. It accepts no environment or command-line authority-root override. Gate-D additionally rejects the `RIG_LOOP_STATE` override in production.
- Process records name entrypoints and hashes. Python AST traversal derives reachable symbols, spans, local edges, and external call-site stages. The admitted grammar is closed and linear; unrecognized statements, dynamic builtins (including `breakpoint`, `input`, `open`), callable escapes, and external callables used as values return `BLOCK`.
- Classification is authority-owned and lives in a separate file. Its ID set must equal the extracted inventory exactly; missing, unknown, duplicate, or stale-bound IDs return `BLOCK`. Edges must be mirrored, acyclic, self-edge-free, and reachable from roots. Final operation identities are minted from provisional ID + runtime kind + taxonomy + remapped bindings.
- Critical controls (`control plane`, `side effect` taxonomies) must be CODE. Every MODEL operation needs a typed necessity record: falsifiable claim, deterministic alternative, `expected_improvement` in (0,1], non-empty typed input/output schemas, positive attempt/tool/token ceilings, positive time/cost ceilings, and reachable CODE validator, fallback, and failure-state operations.
- Scoring requires aggregate unweighted, aggregate weighted, minimum-path unweighted, and minimum-path weighted CODE ratios ≥ 0.85. HUMAN operations are excluded from both numerator and denominator. Only CODE earns credit.
- `INVENTORY_PASS` and classification admission never authorize effects. Gate-D is a separate exact-action gate: HMAC-SHA256-signed append-only approvals bound to process, inventory, classification, realized, and action hashes; issue+expiry ≤ 24h; atomic O_EXCL one-time consumption; distinct BLOCK reasons for missing, corrupt, unapproved, expired, mismatched, consumed, and root-override.
- D85 eligibility never authorizes an effect. A passing internal process terminates without Gate-D.
- Surface wiring requires exactly `claude_code`, `hermes`, `omp`, and `prime_agent` in `authority/surfaces.json`, each file carrying the marker `rig-determinism-85@<doctrine_sha256>`. Missing or divergent surfaces return `BLOCK`.
- A local imported module under the source root requires a file hash. An omitted local module returns `UNHASHED_REACHABLE_FILE`.
- The adapter operation is the execution root. Its source-derived call graph must reach the bound process entrypoint.
</rules>

<verification>
Run:

```bash
python3 -m unittest tests.test_determinism_85 tests.test_d85_gates -v
```

The inventory suite proves the matching path, exact snapshot parsing, exact nested and sequential order, adapter reachability, locked external-module resolution, and the planted padding, split-node, hidden-symbol, omitted-module, source-drift, root-escape, alias, loader-state, sentinel-iter, breakpoint, external-value-escape, and unsupported-grammar failures. The gates suite proves classification pass/stale/missing/unknown/duplicate, critical-control CODE enforcement, necessity field and reachability validation, graph asymmetry/cycle/self-edge, all four ratio blocks including minimum-path-only and HUMAN exclusion, Gate-D arm/replay/unapproved/expired/mismatch/corrupt/root-override, and wiring pass/divergent/missing.
</verification>

<success_criteria>
- The source-derived inventory includes every reachable local symbol admitted by the closed grammar, with every builtin and locked external call-site stage in exact execution order at `credit_eligible: false`.
- Classification covers exactly the extracted IDs, mints stable final operation identities, and proves every MODEL operation's necessity with reachable CODE support.
- `REALIZED_PASS` requires all four ratios at or above 0.85 with HUMAN operations excluded.
- Gate-D arms at most once per signed approval bound to the exact action envelope; every failure mode is a distinct terminal BLOCK.
- All four agent surfaces carry the same doctrine marker; any divergence blocks wiring.
- No gate in this skill executes an outward effect.
</success_criteria>
