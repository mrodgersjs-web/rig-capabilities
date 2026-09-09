---
name: rig-determinism-85
description: Enforces the deterministic-admission chain — source-derived operation inventory, authority classification, four-ratio D85 scoring, tool-selection and durable-build certification with consumer-side verification, exact-action Gate-D, and agent-surface wiring. Use when registering, classifying, scoring, certifying, or arming a process, selecting a framework, verifying a certificate, or verifying surface wiring.
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
8b. Tool selection and durable-build certification (standard v1.4.0): `bin/rig-determinism-85 select EVIDENCE_FILE` derives one framework from closed-schema evidence records (absent claim = FALSE, contradicted claim BLOCKs). `checklist BUILD_FILE --process-id ID` certifies the build: it declares `process_id` and the `inventory_sha256` snapshot it was generated against; certification recomputes the live inventory and binds only on exact equality — unbound, mismatched, or stale BLOCKs. `verify-cert BUILD_FILE CERT_FILE` is the consumer boundary: it recomputes the canonical build digest, rejects non-exact certificate schemas and tampered payloads, and blocks post-cert mutation replays. The worked example is `authority/reference/julie_synthetic/` — copy that shape, never hand-edit outputs, and rerun `verify-cert` before trusting an archived certificate.
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
- Surface wiring requires exactly `claude_code`, `hermes`, `omp`, and `prime_agent` in `authority/surfaces.json`; each file must carry the exact marker line `rig-determinism-85@<doctrine_sha256>` followed by the canonical `authority/doctrine.md` body bytes (marker substring alone is not wiring). Missing, unreadable, or divergent surfaces return `BLOCK`.
- A local imported module under the source root requires a file hash. An omitted local module returns `UNHASHED_REACHABLE_FILE`.
- The adapter operation is the execution root. Its source-derived call graph must reach the bound process entrypoint.
</rules>

<verification>
Run:

```bash
python3 -m unittest tests.test_determinism_85 tests.test_d85_gates -v
```

The inventory suite proves the matching path, exact snapshot parsing, exact nested and sequential order, adapter reachability, locked external-module resolution, and the planted padding, split-node, hidden-symbol, omitted-module, source-drift, root-escape, alias, loader-state, sentinel-iter, breakpoint, external-value-escape, and unsupported-grammar failures. The gates suite proves classification pass/stale/missing/unknown/duplicate, critical-control CODE enforcement, necessity field and reachability validation, graph asymmetry/cycle/self-edge, all four ratio blocks including minimum-path-only and HUMAN exclusion, Gate-D arm/replay/unapproved/expired/mismatch/corrupt/root-override, and wiring pass/divergent/missing.
The tool-selection suites (`tests.test_tool_selection`, `tests.test_tool_selection_cli`, `tests.test_evasion_battery`) prove the closed evidence grammar, typed blocks, claim-and-verify inventory binding, root containment, seven planted evasion attacks, and the verifier's honest-replay/mutated-build/tampered-certificate/stale-inventory exits.
</verification>

<success_criteria>
- The source-derived inventory includes every reachable local symbol admitted by the closed grammar, with every builtin and locked external call-site stage in exact execution order at `credit_eligible: false`.
- Classification covers exactly the extracted IDs, mints stable final operation identities, and proves every MODEL operation's necessity with reachable CODE support.
- `REALIZED_PASS` requires all four ratios at or above 0.85 with HUMAN operations excluded.
- Gate-D arms at most once per signed approval bound to the exact action envelope; every failure mode is a distinct terminal BLOCK.
- All four agent surfaces carry the exact doctrine marker plus the canonical doctrine body; any divergence blocks wiring.
- No gate in this skill executes an outward effect.
</success_criteria>

## Universal Enforcement (v1.5)

The central gate is `rig-loop dispatch_hook`, above loop-specific logic and
active even when no loop run exists. Claude, Codex, Hermes, OMP, and Prime Agent
must route mutation-class pre-tool calls through it. Protected roots come only
from `~/.rig/d85/enforcement.json`; a `write`, `edit`, `bash`/`shell`,
`apply_patch`, or equivalent mutation touching an exact path beneath one of
those roots requires a current signed admission for that path and session.

### Admission ceremony

```bash
rig-determinism-85 admit-request <build.json> \
  --path <exact-absolute-target> \
  --session-key <sid-or-cwd-key>
# Mike types in chat: APPROVE d85adm_<hex12>
rig-determinism-85 admit-approve
```

`process_id` defaults from `build.json`. `admit-request` first requires a bound
`CHECKLIST_PASS`; an unbound pass is not an enforcement verdict.
`admit-approve` reads the exact phrase from an interactive TTY; `--phrase` is
test-only. Approval appends an HMAC-signed record to
`~/.rig/d85/admissions/approvals.jsonl`, binding exact absolute paths, build
SHA-256, process, session, and a finite positive TTL of at most 24 hours. Each mutation
revalidates signature, TTL, exact-path coverage, session, and unchanged build
bytes.

The Python approval boundary itself opens `/dev/tty` and requires a TTY before
minting a production record; the CLI delegates to it. Supplied phrases or
clocks require `RIG_D85_TEST_PHRASE=1` plus an explicit temporary D85 home,
non-escaping ledger/key paths, and temporary builds/outputs/launchers.
The test path refuses the production home and records `how=test-phrase`, not
`typed-approve`. Same-account signing-key compromise remains outside this
application boundary. Tests never mint production admissions.

An admission needs at least one `--path` OR `--launcher`. A launcher-only
request has no writable outputs. `--launcher <script>` binds execution
identity and content digest; `--path <output>` grants only that exact writable
literal. Neither the launcher nor its parent becomes writable implicitly.

### Scheduled automation launcher

Scripts that live under, or can touch, protected roots must be scheduled through:

```bash
rig-determinism-85 d85-run <script> [args...]
```

With active protected roots, `d85-run` requires an admission for EVERY script,
regardless of where it lives. It checks the signed launcher digest, unchanged
approved build digest, and live `verify-cert` before executing under
`sandbox-exec`. The profile allows default operations, denies writes under
canonical protected roots, then permits only explicitly admitted output
literals. Resolve roots before emitting SBPL so aliases such as `/var` and
`/private/var` cannot escape the boundary. A directory literal does not grant
its descendants. The sandbox is the execution-time boundary, not shell parsing.

### Estate migration

`estate-validate` requires a declared existing launcher at or after
`launcher_epoch`, including numeric Unix epochs interpreted in UTC. The
builder derives `modified_at` from the source file's mtime and emits
`modified_at_source` with path, field, and raw value. For a shared Hermes store,
this conservatively marks every enabled job as modified when that store changes.
Known pre-epoch jobs remain the visible `grandfathered_launcher_missing`
retrofit backlog. Missing/invalid dates do not grandfather newly discovered jobs.
A launcher path check alone is not proof of scheduler wiring or signed admission.

Verify Hermes locations from the installed scheduler, not an old runbook.
On this host, `.hermes/hermes-agent/cron/jobs.py` defines
`get_hermes_home()/cron/jobs.json`: the root store and
`~/.hermes/profiles/*/cron/jobs.json`. The previously documented no-`cron/`
paths are absent. The builder records each scanned path and scopes IDs by profile.

### Fail-closed matrix

| Condition | Verdict |
| --- | --- |
| Protected target with no exact current-session admission | DENY |
| Missing, unreadable, or malformed config, payload, key, ledger, or signature | DENY |
| Expired approval, changed build bytes, missing build, or non-bound checklist result | DENY |
| Unknown shell verb referencing a protected path, or unproven verb with cwd under a protected root | DENY |
| Missing or failing live certificate, unavailable sandbox, or unsafe sandbox path literal | DENY |
| Arbitrary-code tool (`eval`, Python/REPL aliases) while protected roots are active | DENY, even with a path admission |
| Hook engine absent, failed, empty, malformed, or missing a boolean verdict | DENY mutations; retain read-only recovery |
| Proven read-only call or mutation with no target under configured roots | PASS without admission |

### Partial shell ceiling

Shell classification recognizes mutation verbs, redirections, and a closed set
of read-only verbs. It cannot prove that interpreter or build tools such as
Python, `make`, or `npm` will not write paths they never name. The cwd-under-root
rule narrows that gap, but does not close it. `d85-run` plus `sandbox-exec` is
the execution boundary for scheduled automation; universal harness-shell
sandboxing remains open work. Any unclassifiable or internally failed check
against a protected surface denies.

### Emergency recovery

Only Mike's explicitly authorized break-glass process may repair a broken live
gate. Verify `RIG_D85_DISABLE=1` in the process that will perform the write.
Do not set it from a tool or use an alternate alias after a denial. A persistent
execution worker can differ from the shell; a fresh standalone child may be
used only when explicitly authorized, with normal inheritance and no override.
Require one complete-line match, compile the candidate in memory, retain a
backup and original permissions, then atomically replace and recompile.
Remove the override from every isolated enforcement-test subprocess and inspect
the actual pi JSON `block` values: read false, protected write true, eval true.
Ordinary eval denial is intentional, not an outage.

### Wiring proof

`rig-loop wire` is a dry-run proposal unless `--apply` is supplied.
`rig-loop doctor --json` compares installed managed JSON registrations and
adapter bytes with canonical sources. Markers alone do not establish parity.
Matching files do not prove invocation in an already-running harness, and Hermes
gateway hooks cannot block. Obtain approval before changing live security wiring.
