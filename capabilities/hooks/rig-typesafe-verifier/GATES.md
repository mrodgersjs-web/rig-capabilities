# Gates: TypeSafe verifier

OWNS: src/** tests/** scripts/** skill/** build-context.json decision-trail.tsv package.json

Scope: Remediate and independently review an advisory TypeSafe verification layer for direct and Orca-launched OMP sessions. Reactivation and live API calls are out of scope.

- [x] G1: The verifier domain, wire, quota, and OMP lifecycle contracts pass.
  CHECK: bun test tests/extension.test.ts
  EXPECT: 18 pass, 0 fail
  EVIDENCE: 2026-09-18 — 18 pass, 0 fail, 55 assertions; evidence enriched with tool invocation details; quota lock retry added.

- [x] G2: The default and configured rollout mode perform no automatic outbound verification.
  CHECK: bun test tests/extension.test.ts --test-name-pattern "default mode is off"
  EXPECT: 1 pass, 0 fail
  EVIDENCE: 2026-09-16 — targeted test 1 pass; login-shell mode check equals off.

- [x] G3: Common cloud, source-control, chat, OAuth, URL-password, and private-key credentials are redacted.
  CHECK: bun test tests/extension.test.ts --test-name-pattern "redacts common"
  EXPECT: 1 pass, 0 fail
  EVIDENCE: 2026-09-16 — targeted quoted/unquoted provider, env, JSON, URL, and PEM fixture 1 pass.

- [x] G4: Two or more processes cannot exceed the shared quota, and stale locks are reclaimed only for dead owners.
  CHECK: bun test tests/extension.test.ts --test-name-pattern "concurrent quota|reclaims only stale"
  EXPECT: 2 pass, 0 fail
  EVIDENCE: 2026-09-16 — 2 targeted tests pass; five barriered rounds launch eight Bun processes each.

- [x] G5: Busy or corrupt quota state fails closed without invoking Jev.
  CHECK: bun test tests/extension.test.ts --test-name-pattern "busy and corrupt global quota|quota reclaim close errors|failed reclaim commit"
  EXPECT: 3 pass, 0 fail
  EVIDENCE: 2026-09-16 — no-call fixture covers busy lock, corrupt ledger, and unopenable database; injected close and COMMIT failures prove cleanup executes and no owned lock is orphaned.

- [x] G6: A planted unsupported claim produces review and a restored clean claim passes.
  CHECK: bun run scripts/adversarial-check.ts
  EXPECT: PLANT_RED and RESTORE_GREEN
  EVIDENCE: 2026-09-16 — PLANT_RED review; RESTORE_GREEN pass.

- [x] G7: The extension compiles for Bun.
  CHECK: bun build src/extension.ts --target bun --outdir /tmp/rig-typesafe-verifier-build
  EXPECT: exit 0
  EVIDENCE: 2026-09-16 — Bun bundled src/extension.ts to /tmp/rig-typesafe-verifier-build, exit 0.

- [x] G8: The gate manifest is structurally valid.
  CHECK: node /Users/rig128gb/.hermes/skills/unlazy/scripts/gate-lint.mjs GATES.md
  EXPECT: LINT OK
  EVIDENCE: 2026-09-16 — LINT OK.

- [x] G9: The installed OMP extension and universal skill resolve to this source tree while rollout mode remains off.
  CHECK: zsh -lc 'test "$RIG_TYPESAFE_MODE" = off && test "$(realpath /Users/rig128gb/.omp/agent/extensions/rig-typesafe-verifier.ts)" = /Users/rig128gb/.rig/typesafe-verifier/src/extension.ts && test "$(realpath /Users/rig128gb/.agents/skills/rig-typesafe-verifier)" = /Users/rig128gb/.rig/typesafe-verifier/skill'
  EXPECT: exit 0
  EVIDENCE: 2026-09-16 — extension realpath=src/extension.ts; skill realpath=skill; mode=off; exit 0.

- [x] G10: Direct OMP and an Orca-created OMP terminal load the installed extension without a network call.
  CHECK: Start each runtime with RIG_TYPESAFE_MODE=off and execute /typesafe-status.
  EXPECT: mode=off; surface=direct OMP AND mode=off; surface=Orca-launched OMP
  EVIDENCE: 2026-09-16 — direct and Orca /typesafe-status both reported mode=off, correct surface, 0/25 calls, and $0.001344 max estimate.

- [x] G11: An independent cross-family reviewer returns PASS after the quota and redaction remediation.
  CHECK: independent read-only review
  EXPECT: VERDICT: PASS
  EVIDENCE: 2026-09-16 — codex-family TypeSafeCloseGuardReview VERDICT: PASS on src 607087fd; codex quota then blocked a re-run, so a claude-opus-4-8 rebind PASS bound final bytes (src 607087fd, tests e633efdb incl. exact-cap race, worker 7ac2b27b, gates d6e400d8).

- [ ] G12: The durable A2 build is certified by the released D85 authority.
  CHECK: Released D85 chain: inventory rig-typesafe-verifier-v2; score rig-typesafe-verifier-v2; checklist build-context.json --process-id rig-typesafe-verifier-v2; verify-cert build-context.json <emitted-certificate>
  EXPECT: inventory eligible; all four realized ratios >= 0.85; checklist exit 0; verify-cert exit 0
  EVIDENCE: BLOCK — UNKNOWN_PROCESS; the released registrar accepts Python AST entrypoints and the released certifier supports A1 only, while this source-derived TypeScript build is A2.

- [x] G13: Shadow activation produces a persisted advisory receipt on both OMP surfaces after the hardening.
  CHECK: Resume each pre-hardening smoke session with RIG_TYPESAFE_MODE=shadow, attempt a turn, exit cleanly, and read the appended receipt plus the quota ledger delta.
  EXPECT: one new advisory_only receipt per surface; quota calls increase by exactly two at $0.001344 each; no raw payload text in receipts
  EVIDENCE: 2026-09-17 — session 01a0ac60 (direct) appended receipt 00:10:03.947Z verdict uncertain jev-1.13.0 756 tokens; session 01a0ac61 (Orca terminal term_588143b9) appended 00:10:36.901Z verdict uncertain; ledger day 2026-09-17 calls=2 reserved_cost_usd=0.002688 exactly matching the fixed reservation; receipts carry sha256 hashes and probabilities only. Fresh-turn probes additionally showed the null-skip path live: every exhausted-codex error-only transcript produced zero reservations.
