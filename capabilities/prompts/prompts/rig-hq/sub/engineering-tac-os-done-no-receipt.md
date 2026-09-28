---
id: rig-hq-sub-j2-2-a-claim-of-done-has-no-receipt
version: 1
status: draft
tier: sub
department: Engineering (TAC OS)
agent: george-application-engineering
parent: rig-hq-prompt-jordan-jr-ai-engineering
task: Interrupt sub-prompt (J2): a claim of done has no receipt — refuse it and file a Windshield card
triggers: done claim no receipt, unevidenced done, badge not work
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J2 interrupt 2), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J2 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: a claim of done has no receipt

**Trigger.** An agent reports done without an artifact: no report file, no commit sha,
no pasted check output.

**Typed inputs.** `claim` (text), `claimant`, `expected_artifacts`.

**Steps.**
1. Refuse the claim. A completion record, badge or job status is not work.
2. Re-verify by reading the target artifact directly (file exists? counts match?).
3. File a Windshield card: who claimed, what was missing, what evidence would settle
   it.

**Output format.**
```
VERDICT: REFUSED — no receipt
Claim: "<text>" — <claimant>
Reality: <artifact check results>
Windshield card: <path>
What would settle it: <named artifacts>
```

**Expected output.** An honest refusal that cannot be talked past.

**Done test.** The refusal cites the artifact check you ran yourself.

**Failure handling.** If the artifact later appears, a new verification runs — the
refusal record is never edited away.

**Persistence.** Refusal + card saved; this is regression evidence.

**Redaction.** No secrets in excerpts.

**Stop / escape hatch.** "Two runs ended without a receipt" is a defect report, not
an inconvenience.
