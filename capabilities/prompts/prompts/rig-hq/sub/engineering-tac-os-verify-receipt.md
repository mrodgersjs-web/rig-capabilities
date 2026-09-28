---
id: rig-hq-sub-j2-verify-receipt
version: 1
status: draft
tier: sub
department: Engineering (TAC OS)
agent: george-application-engineering
parent: rig-hq-prompt-jordan-jr-ai-engineering
task: Recurring sub-prompt (J2): verify a claim of done independently and issue or refuse the receipt
triggers: verify done, prove it, is it done, independent verification
sources: ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md (J2), ~/.rig/jake/aos/maps/aside-links/jtbd.json
provenance: first-party RIG design | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Verify receipt (J2 recurring)

**Trigger.** A builder (or any agent) claims work is done.

**Typed inputs.** `claim` (the done-claim text), `artifact_paths`, `bar` (the checks
that must pass), `worktree`.

**Steps.**
1. Run the checks yourself from a clean state; never accept the builder's pasted
   output as your evidence.
2. Compare the claim against what the artifacts actually contain (counts, files,
   endpoints).
3. If the work involves renders or UI, look at real captures before agreeing.
4. Issue the receipt, or refuse it with the exact failing evidence.

**Output format.**
```
VERDICT: RECEIPT ISSUED | REFUSED | BLOCKED <missing piece>
Claim: <text>
Evidence: <command + your own pasted output>
Receipt: <path> (or the refusal reason)
```

**Expected output.** An independent verdict a human can trust without re-checking.

**Done test.** The verdict cites your own run of the bar's checks.

**Failure handling.** A check that cannot run is BLOCKED with the missing piece named
— never PASS. A refusal files a Windshield card (done-claim with no receipt).

**Persistence.** Verdict and receipt in the verification folder; refusals are never
deleted.

**Redaction.** No credential values in evidence.

**Stop / escape hatch.** If the claim is not decidable from the artifacts, refuse and
name what is missing — never grade on vibes.
