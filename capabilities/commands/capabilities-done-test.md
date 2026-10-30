---
name: capabilities-done-test
description: Run one asset's executable done_when contract (cmd/file/grep forms) and report pass/fail with the exact failing check — then stamp WHO ran it (model + version, harness + config hash) and refuse the record if the verifier is not external (no adjective, and no unpinned or self-graded green).
argument-hint: "<asset-id>"
allowed-tools: Read, Bash
category: meta
outcome: "meta: done means every runnable check exited 0, quoted, BY A NAMED MODEL IN A FINGERPRINTED HARNESS, JUDGED OUTSIDE THAT CONTEXT — unrunnable is stated, unpinned is refused, self-graded is refused, never counted as green"
done_when:
  - file:capabilities/commands/capabilities-done-test.md
  - file:examples/great/meta/capabilities-done-test.md
  - file:rig_capabilities/acceptance_identity.py
  - grep:rig_capabilities/acceptance_identity.py:identity_unavailable:
  - cmd:T="${TMPDIR:-/tmp}/aid-green-$$"; mkdir -p "$T"; printf '{"asset_id":"capabilities-done-test","verdict":"pass","executed_by":{"model":"claude-opus-4-1","model_version":"2026-08-01","process_id":"p-producer"},"harness_ref":{"harness_id":"rig-capabilities","config_hash":"sha256:2b1e0f6a9c4d8e7f5a3b1c9d7e5f3a1b9c8d7e6f"},"verifier":{"model":"gpt-5-codex","process_id":"p-verifier","harness_id":"cross-family-checker"}}' > "$T/rec.json"; python3 rig_capabilities/acceptance_identity.py "$T/rec.json" --stamp "$T/stamp.json" >/dev/null; rc=$?; if grep -q '"externality_basis"' "$T/stamp.json"; then g=0; else g=1; fi; rm -rf "$T"; test $rc -eq 0 && test $g -eq 0
  - cmd:T="${TMPDIR:-/tmp}/aid-red-model-$$"; mkdir -p "$T"; printf '{"asset_id":"x","verdict":"pass","executed_by":{"model_version":"2026-08-01","process_id":"p-producer"},"harness_ref":{"harness_id":"rig-capabilities","config_hash":"sha256:2b1e0f6a9c4d8e7f5a3b1c9d7e5f3a1b9c8d7e6f"},"verifier":{"model":"gpt-5-codex","process_id":"p-verifier","harness_id":"cross-family-checker"}}' > "$T/rec.json"; python3 rig_capabilities/acceptance_identity.py "$T/rec.json" --stamp "$T/stamp.json" 2>"$T/err.txt"; rc=$?; if grep -q identity_unavailable:executed_by.model "$T/err.txt"; then g=0; else g=1; fi; s=absent; test -e "$T/stamp.json" && s=present; rm -rf "$T"; test $rc -eq 1 && test $g -eq 0 && test $s = absent
  - cmd:T="${TMPDIR:-/tmp}/aid-red-self-$$"; mkdir -p "$T"; printf '{"asset_id":"x","verdict":"pass","executed_by":{"model":"claude-opus-4-1","model_version":"2026-08-01","process_id":"p-1"},"harness_ref":{"harness_id":"rig-capabilities","config_hash":"sha256:2b1e0f6a9c4d8e7f5a3b1c9d7e5f3a1b9c8d7e6f"},"verifier":{"model":"claude-sonnet-5","process_id":"p-2","harness_id":"rig-capabilities"}}' > "$T/rec.json"; python3 rig_capabilities/acceptance_identity.py "$T/rec.json" --stamp "$T/stamp.json" 2>"$T/err.txt"; rc=$?; if grep -q self_verification "$T/err.txt"; then g=0; else g=1; fi; s=absent; test -e "$T/stamp.json" && s=present; rm -rf "$T"; test $rc -eq 1 && test $g -eq 0 && test $s = absent
  - cmd:T="${TMPDIR:-/tmp}/aid-red-none-$$"; mkdir -p "$T"; printf '{}' > "$T/rec.json"; env RIG_MODEL_ID=decoy-model HARNESS_ID=decoy-harness python3 rig_capabilities/acceptance_identity.py "$T/rec.json" --stamp "$T/stamp.json" 2>"$T/err.txt"; rc=$?; n=$(grep -c identity_unavailable "$T/err.txt"); s=absent; test -e "$T/stamp.json" && s=present; rm -rf "$T"; test $rc -eq 1 && test $n -eq 8 && test $s = absent
great_example: examples/great/meta/capabilities-done-test.md
acl: public
quality_floor: 0.7
---

# capabilities-done-test

1. Resolve `<asset-id>` via the index (canonical wins; note the source actually run).
2. Run `./bin/rig-capabilities test <asset-id>` — every cmd/file/grep check executes; mcp: entries are reported as contract lines, marked unrunnable unless an executor is wired.
3. Report per-check: form, ok, detail. A pass claim without the per-check table did not happen.
4. If done_when is missing entirely, the asset is `uncontracted` — that is a gap to round-fix, not a pass.
5. **Stamp the acceptance.** The run's verdict alone is half a record: pipe the done-test result (identity fields grafted on) through `rig_capabilities/acceptance_identity.py <record.json> --stamp <out.json>`. Exit 0 writes the identity stamp and the PASS is joinable by variant; exit 1 is a named refusal and the run is recorded as refused, not green.

The grep target must live OUTSIDE the asset's own frontmatter — a done_when that greps for its own text is tautology (found by plant-failure, V22). The grep check below this line is now aimed at `rig_capabilities/acceptance_identity.py`: it verifies the refusal vocabulary lives in the code, not in this file's prose.

## The acceptance identity stamp

The unit being evaluated is the coupled (model, harness) state — "the real
agent configuration is a combined interlink state" (5S9NemR7Fwo,
arXiv:2608.13951). A PASS earned by model A inside harness variant X says
nothing about model B or variant Y, so an acceptance record that does not pin
all of it cannot be joined, compared, or trusted. Every acceptance record must
carry:

| field | pins |
|---|---|
| `executed_by.model` + `executed_by.model_version` | which model ran the done_when |
| `executed_by.process_id` | which run — and the anchor for the externality check |
| `harness_ref.harness_id` + `harness_ref.config_hash` | which harness variant, fingerprinted ([sha256:]hex 16–64; free text like `main` pins nothing) |
| `verifier.model` + `verifier.process_id` + `verifier.harness_id` | who judged it |

**Never fabricate an identity.** There is no environment, config, or heuristic
fallback anywhere in `acceptance_identity.py`: a field the record does not
carry is emitted as `identity_unavailable:<field>` with exit 1, not guessed.
The honest output of a run whose environment exposed no identity is a named
refusal — the module's own refusal string when the record is empty:

```
identity_unavailable:executed_by.model (executed_by missing or not an object)
identity_unavailable:executed_by.model_version (executed_by missing or not an object)
identity_unavailable:executed_by.process_id (executed_by missing or not an object)
identity_unavailable:harness_ref.harness_id (harness_ref missing or not an object)
identity_unavailable:harness_ref.config_hash (harness_ref missing or not an object)
identity_unavailable:verifier.model (verifier missing or not an object)
identity_unavailable:verifier.process_id (verifier missing or not an object)
identity_unavailable:verifier.harness_id (verifier missing or not an object)
```

## The verifier must be EXTERNAL at the acceptance moment

The failure signature from arXiv:2608.11888: "The skill performs the internal
validation" (TA5QzGTQU_U) — a skill whose own validation section certifies
correctness while an external evaluation judges the output wrong. RIG already
believes the doctrine (`loops/doer-checker-validator.md` maker-never-grades,
`commands/capabilities-certify.md` "No LLM participates in certification",
`commands/capabilities-dispatch-verify.md` cross-family verifier) but
`capabilities_test` runs the asset's OWN done_when, which is self-validation by
construction. The stamp closes that hole at the record level:

- **same process** (`verifier.process_id == executed_by.process_id`) → refused:
  `self_verification:producer_and_verifier_are_one_process(<id>)`.
- **same model family AND same harness id** — the asset's checklist graded by
  the same brain in the same harness, a different invocation notwithstanding
  → refused: `self_verification:same_model_family_and_harness(<family>+<harness>)`.
- external iff a DIFFERENT process AND at least one axis differs — different
  model family (the ideal, cross-family verifier) or a different harness
  process — the stamp records which in `externality_basis`.

Model family is derived deterministically from the model id (last `/`-segment,
first `[-:@_]` token: `openrouter/anthropic/claude-opus-4` → `claude`), with an
optional explicit `model_family` override. That is a normalization of a field
that exists, never an invention of one that does not.

## Commands

```bash
# stamp an acceptance record (exit 0, writes ONLY the stamp file, echoes it):
python3 rig_capabilities/acceptance_identity.py record.json --stamp stamp.json

# refusal exercises (exit 1, one line per defect on stderr, nothing written):
printf '{}' | python3 rig_capabilities/acceptance_identity.py - --stamp s.json
#   identity_unavailable:<field> x8 — no identity in the environment is refused, not guessed
# verifier sharing the producer's family+harness:
#   self_verification:same_model_family_and_harness(claude+rig-capabilities)
```

Exit codes: `0` stamped · `1` refused · `2` usage. The four `cmd:` done_when
checks above are the permanent fixtures: complete identity GREEN, missing
producer model RED, self-verification RED, no-identity-at-all RED (exit code +
refusal string + proof that no stamp was written).

## RIG delta

- `capabilities_test` / `capabilities_quality_report` scored a done_when with
  the executing model unpinned — the same asset could report PASS under two
  models with no record of which ran it.
- ProofPacket sealing binds commands, exit codes, artifact hashes — but not
  harness variant or model, so packets were not joinable by variant
  (arXiv:2608.13951 C5/C6).
- Nothing in the estate applied maker-never-grades to the done-test record
  itself; the stamp is where that doctrine finally bites.

## Ceiling (stated, not smoothed)

The module validates the SHAPE of the config hash and the self-consistency of
the identities it is given; it cannot cryptographically prove a record's
claims — a record fabricated wholesale by the producer passes the stamp. Its
teeth are structural: a run that does not name who judged it, or names the
producer as judge, gets no acceptance stamp at all. Cryptographic writer
identity belongs to the seal layer (same ceiling as the wm-commit-gate).
