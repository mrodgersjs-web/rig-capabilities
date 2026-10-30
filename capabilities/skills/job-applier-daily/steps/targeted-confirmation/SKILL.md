---
name: job-daily-targeted-confirmation
description: Resolve factual participation and separate inclusion choices for current draft claims.
metadata:
  version: 1.3.0
---

# Targeted confirmation

## Inputs
Full useful review packet, initiative question queue, claim IDs and exact document hashes.

## Actions
Execute inherited targeted-confirmation. Ask what Mike personally did and the supported outcome. Separately ask whether to include the confirmed contribution and in which document. Record confirm/replace/omit without treating prose approval as factual evidence.

## Outputs
Authenticated response references, updated claim and inclusion records, explicit unresolved questions.

## Gates
Pending/denied participation or pending/omitted inclusion bars that claim from clean final files. Silence is no response.

## Recovery
Keep durable human waits. Revised claims return through writing and visual checks; renew affected approvals.

## Required skills and contracts
[Meta-skill](../../SKILL.md) and [execution contract](../../references/execution-contract.md).
[Inherited targeted-confirmation](../../../job-applier/steps/targeted-confirmation/SKILL.md).
[Contribution questions](../../subskills/contribution-questions/SKILL.md).
