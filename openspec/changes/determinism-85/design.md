# Determinism 85 design

## Goals

- Derive the realized operation set from source rather than the submitted manifest.
- Require at least 85 percent deterministic work on aggregate and minimum paths.
- Require CODE for every critical control.
- Keep D85 admission separate from one-action Gate-D authorization.
- Make every failure terminal for the current immutable attempt.

## Decisions

The fixed authority registry names process entrypoints, file hashes, source roots, adapter bindings, and locked external single-file modules. Python AST traversal derives reachable symbols and expands builtin and locked-module call sites into an exact linear provisional sequence. The parser uses the same file snapshots it hashes and rejects canonical-path or inode aliases.

Structural symbols and provisional stages receive no deterministic credit. A later authority stage must prove distinct realized work, classify every stage, and mint final operation identities. Only CODE earns deterministic credit. HUMAN is excluded. MODEL, MODEL_AGENT, and MIXED receive no credit.

The scorer must compute weighted and unweighted aggregate ratios and the minimum reachable root-to-terminal ratios. All four values must be at least 0.85. Critical controls must be CODE.

Gate-D requires a separate authenticated append-only signed approval record and atomic one-use consumption. D85 never authorizes an effect.

## Risks

Static Python analysis cannot safely infer every construct. The inventory admits a closed linear synchronous grammar and blocks every other construct. Locked external modules require exact resolver candidate, source hash, and top-level symbol evidence without import execution. The inventory records that isolated runtime-loader proof is still missing. Other languages, packages, compiled extensions, async execution, keyword calls, higher-order callbacks, and branching graphs remain blocked until a closed adapter extracts equivalent evidence.

## Migration

Register one process at a time. Generate its inventory, classify every extracted identity, plant a failure, and bind the passing proof before enabling a hook. Keep the four global surfaces unchanged until the shared compiler and authenticated approval substrate pass.

## Rollback

Remove the unopened process authority record and the new inventory files. No production hook or scheduler consumes this slice, so rollback requires no state migration.
