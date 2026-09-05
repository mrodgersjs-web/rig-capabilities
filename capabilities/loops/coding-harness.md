---
outcome: agent-engineering:
done_when:
  - file:capabilities/loops/coding-harness.md
  - cmd:python3 scripts/assert_loop_termination.py capabilities/loops/coding-harness.md
great_example: examples/great/agent-engineering/coding-harness.md.md
quality_floor: 0.6
---

# Coding Goal Harness — H_coding(GL-BI, GL-VQ)

Governs GL-BI (build/investigate) and GL-VQ (verify/quality) loops.
This is a runtime gate loop. Each gate must produce evidence before the session
may advance. No gate evidence, no progress.

## 0. Identity Lock

The session starts as Jake RIG Agent executing a coding task. Before any code
is written or reviewed, identity must be locked.

Gate 0.1 ❏ Session declared as GL-BI or GL-VQ in first 3 lines.
Gate 0.2 ❏ RIG procedures loaded — `~/.hermes/jake/rig-operating-procedures.md`
   read or cited by line range.
Gate 0.3 ❏ Coordinate stated: `L{level}-D{diamond}-A{mode}-{step}`.
Gate 0.4 ❏ Task scope bounded — explicit list of files/modules to touch.
   Proof: file path list or `git diff --stat` plan stated before editing.

## 1. Code Quality Gates

### 1.1 Type Safety
Gate T.1 ❏ All new/modified code has explicit type annotations (TypeScript,
   Python type hints, Go types, Rust types — whatever the project uses).
   Proof: grep for `: Type`, `-> Type`, `type X =`, or equivalent in diff.
   Exception: dynamically-typed projects where types are not idiomatic.
   State the exception explicitly.
Gate T.2 ❏ No `any`, `@ts-ignore`, `# type: ignore`, or equivalent escape
   hatches introduced without a `// TODO(reason)` comment explaining why.
   Proof: grep for escape hatches in diff; each must have a TODO.

### 1.2 Test Floor
Gate TF.1 ❏ Every new function/method has at least one test.
   Proof: test file exists, test function name matches or describes the
   new function. Show the test command and its output.
Gate TF.2 ❏ Test coverage does not decrease. Run coverage before and after.
   Proof: `coverage_before` vs `coverage_after` — delta must be >= 0.
   For projects without coverage tooling: at minimum, all tests pass.
Gate TF.3 ❏ No test is skipped, stubbed, or commented out without a tracking
   issue number. Proof: grep for `skip`, `xit`, `pending`, `# TODO` in tests.

### 1.3 Security Scan
Gate SC.1 ❏ No hardcoded secrets, API keys, passwords, or tokens in diff.
   Proof: run regex scan on diff for patterns:
   `(api[_-]?key|secret|password|token|bearer)\s*[:=]\s*['"][^'"]+['"]`
   Zero matches required.
Gate SC.2 ❏ No new dependencies introduced without a license check.
   Proof: if `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`
   modified, show `license-checker` output or manual license verification.
Gate SC.3 ❏ No SQL injection, path traversal, or command injection vectors
   in new code. Proof: if user input flows to SQL/filesystem/shell, show
   parameterized query / path sanitization / subprocess list form.

### 1.4 Build Verification
Gate BV.1 ❏ Project builds clean with zero new warnings.
   Proof: run `npm run build`, `cargo build`, `go build`, `python -m py_compile`,
   or project-specific build command. Show full output.
   Warnings that existed before this diff are acceptable if noted.
Gate BV.2 ❏ Linter passes with zero new violations.
   Proof: run `eslint`, `ruff check`, `golangci-lint run`, `clippy`, or
   project-specific linter. Show output.
Gate BV.3 ❏ If CI exists: CI pipeline green on the branch.
   Proof: `gh run list --branch <branch> --limit 1` or CI dashboard screenshot.

### 1.5 Code Review Discipline
Gate CR.1 ❏ Self-review performed before claiming done.
   Proof: read the full diff aloud (or show `git diff` output) and state
   "Reviewed — no issues" or list specific issues found and fixed.
Gate CR.2 ❏ If the change is > 200 lines: a second agent or human has reviewed.
   Proof: PR review comment, `gh pr review`, or explicit second-agent review
   with PASS verdict. For subagent work: the checker agent's report.

## 2. Independence Drill

### 2.1 No Premature Coupling
Gate ID.1 ❏ New code does not import/couple to modules it doesn't need.
   Proof: diff shows only necessary imports. No "just in case" imports.
Gate ID.2 ❏ New code works in isolation — can be tested without spinning up
   the entire system. Proof: unit test runs without external dependencies
   (or mocks are used for external deps).

### 2.2 No Assumed Context
Gate IC.1 ❏ No code assumes prior state from previous runs without
   initialization. Proof: if reading from DB/file/cache, show the
   initialization path or fallback behavior.
Gate IC.2 ❏ Error paths are handled, not just happy paths.
   Proof: every `catch`, `except`, `Result::Err` branch either handles
   the error or explicitly propagates it with context.

## 3. Gate-D Boundary

Gate D.1 ❏ No code deployed, pushed, or merged without typed APPROVE + run_id.
   Proof: `git push`, `gh pr merge`, `deploy` commands require explicit
   Mike approval or delegated Gate-D authority.
Gate D.2 ❏ Database migrations are reversible.
   Proof: if migration exists, show the rollback script or explain why
   irreversible migration is acceptable.
Gate D.3 ❏ No external API calls made in production without rate-limit
   awareness. Proof: if new API integration, show rate limit handling.

## 4. Proof Requirements

Every coding session produces a ProofPacket:

```json
{
  "schema_version": "rig.coding.v1",
  "run_id": "<uuid>",
  "loop": "GL-BI | GL-VQ",
  "files_changed": ["path1", "path2"],
  "diff_stats": "X insertions, Y deletions",
  "gates": {
    "identity_lock": {"pass": true, "evidence": "..."},
    "type_safety": {"pass": true, "evidence": "..."},
    "test_floor": {"pass": true, "coverage_before": 82, "coverage_after": 84},
    "security_scan": {"pass": true, "evidence": "no secrets found"},
    "build_verify": {"pass": true, "build_output": "..."},
    "code_review": {"pass": true, "reviewer": "self | agent | human"},
    "independence": {"pass": true, "evidence": "..."},
    "gate_d": {"pass": true, "evidence": "no deploy without approval"}
  },
  "verdict": "PASS | FAIL",
  "proof_hash": "sha256:..."
}
```

## 5. Definition of Done

A coding session is done when:
1. All applicable gates in §0–§3 passed (none skipped without stated reason).
2. Code builds, tests pass, linter clean.
3. ProofPacket written with evidence for every gate.
4. One improvement entry written to `~/.hermes/jake/improvements.log`.
5. Identity closure: final message states coordinate, verdict, files changed,
   next safe action.

## 6. What Happens When a Gate Fails

| Gate | On Failure |
|------|-----------|
| 0.1–0.4 (Identity) | HALT. No code written until identity established. |
| T.1–T.2 (Type Safety) | Block. Add types before proceeding. No merge without types. |
| TF.1–TF.3 (Test Floor) | Block. Write tests before proceeding. Coverage floor is sacred. |
| SC.1–SC.3 (Security) | HALT IMMEDIATELY. Secrets in diff = emergency. Rotate key, scrub diff. |
| BV.1–BV.3 (Build) | Block. Fix build before any other work. Build failure = no progress. |
| CR.1–CR.2 (Code Review) | Block until review completed. >200 lines without review = no merge. |
| ID.1–ID.2 (Independence) | Warn. Flag coupling but allow if architectural reason stated. |
| IC.1–IC.2 (No Assumed Context) | Block. Error handling is not optional. |
| D.1–D.3 (Gate-D) | HALT. No external action without approval. Immediate stop. |

## 7. Self-Improvement Loop

After each coding session, append to `~/.hermes/jake/improvements.log`:

```text
[YYYY-MM-DD HH:MM] coding session: GL-BI | GL-VQ
  gates passed: <count>/<total>
  gates failed/skipped: <which>
  files changed: <count>
  coverage delta: +/-X%
  capability gap: <what was missing>
  improvement: <what to add or change>
```

Every 5 entries: extract pattern. If same gate fails 3+ times, update this
harness with a new constraint or automated check.

## 8. Final Rule

```text
No gate evidence, no progress.
No test, no merge.
No build, no ship.
Every coding session leaves the codebase stronger than it found it.
```

---

*Companion to: hermes-conductor.md, doer-checker-validator.md*
*Governs: GL-BI (build/investigate), GL-VQ (verify/quality)*

## What Great Looks Like (WGLL)

Amazing coding output from this harness:

- **Every function has a docstring** with args, returns, raises, and a one-line summary
- **Type hints on all signatures** — no `Any` unless genuinely unavoidable
- **Tests written before or alongside code** — RED-GREEN-REFACTOR enforced
- **Error messages are actionable** — tell the user what went wrong AND what to do about it
- **No dead code left behind** — every import used, every function called, every branch reachable
- **Diff is minimal** — only the lines that need to change are changed; no cosmetic reformatting
- **Build passes clean** — type checker, linter, and test suite all green before commit

