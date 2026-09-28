---
id: rig-hq-sub-j4-1-an-answer-has-no-source
version: 1
status: draft
tier: sub
department: Intelligence
agent: iris-sr-research
parent: rig-hq-prompt-iris-strategy
task: Interrupt sub-prompt (J4): an answer has no source — send it back for a cited retry
triggers: unsourced answer, no citation, claim without evidence
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J4 interrupt 1), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J4 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: an answer has no source

**Trigger.** An answer reaches review with claims that carry no resolvable source.

**Typed inputs.** `answer_path`, `uncited_claims`.

**Steps.**
1. Send it back — a hedge is not a citation. List each uncited claim.
2. Re-run as a cited retry: claim -> source (tier + weight + confidence) or the claim
   is cut.
3. Mark inferences explicitly; an inference dressed as a fact is the same defect.

**Output format.**
```
STATUS: RETURNED FOR CITATION | DONE (cited)
Uncited: <claims, one per line>
Retry: <path> — each claim -> <source, tier, weight>
Cut claims: <list or none>
```

**Expected output.** An answer a skeptic can trace end to end.

**Done test.** Every shipped claim resolves to a source that was actually read.

**Failure handling.** A claim with no findable source is cut or marked UNVERIFIED —
never re-worded into vagueness.

**Persistence.** Both the refused and cited versions are kept.

**Redaction.** No secrets in excerpts.

**Stop / escape hatch.** Contradicting sources -> show both with weights and ask.
