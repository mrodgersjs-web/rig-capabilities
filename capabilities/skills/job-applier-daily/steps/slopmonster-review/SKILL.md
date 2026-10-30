---
name: job-daily-slopmonster-review
description: Apply SlopMonster prose guidance without changing factual scope.
metadata:
  version: 1.3.0
---

# Slopmonster review

## Inputs
Draft resume/letter text, claim ledger, source hashes and intended executive voice.

## Actions
Read the bundled SlopMonster skill. Remove stock AI phrasing, empty adjectives, repetition and unsupported certainty. Preserve exact metrics, negation, employer/date attribution and personal/team distinctions. Compare every changed claim against evidence.

## Outputs
Edited text, factual-diff review and actual SlopMonster execution record.

## Gates
Style approval cannot clear factual/JEV/page holds. No detector-evasion or hiring-outcome guarantee.

## Recovery
If dependency unavailable, retain drafts and mark writing review pending. Changed text returns to rendering and affected approvals.

## Required skills and contracts
[Meta-skill](../../SKILL.md) and [execution contract](../../references/execution-contract.md).
[SlopMonster](../../../slopmonster/SKILL.md) and [document quality](../document-quality/SKILL.md).
