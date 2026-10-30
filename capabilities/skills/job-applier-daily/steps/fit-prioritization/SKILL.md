---
name: job-daily-fit-prioritization
description: Qualify and prioritize current jobs without changing candidate constraints to fill a quota.
metadata:
  version: 1.4.0
  origin: newly-composed-source-grounded-step
---

# Fit prioritization

## Inputs
Complete current postings, profile constraints and full-table duplicate results.

## Actions
Apply deterministic exclusions for explicit hard constraints first. Preserve unknown salary/credential/location evidence instead of guessing. Build bounded sanitized fit questions for JEV using the actual available rubric; record its policy version and current input hashes. Rank only admitted eligible roles by returned typed evidence under documented current criteria. Distinguish eligible, rejected and held.

## Outputs
Fit table with job key, constraint result, cited JD evidence, actual JEV receipt and ranking rationale.

## Gates
No silent compensation/location relaxation. No guessed fit verdict on unavailable/malformed JEV. A strong semantic score cannot override a failed hard constraint or prior application.

## Recovery
Store hold reasons and original receipts. Retry only transient read failures under existing caps; new evidence may justify a new review, not unchanged repeated calls seeking PASS.

## Required skills and contracts
- [profile-evidence](../../steps/profile-evidence/SKILL.md).
- [jev-decision](../../steps/jev-decision/SKILL.md).
- [duplicate-identity](../../subskills/duplicate-identity/SKILL.md).

Follow the [daily execution contract](../../references/execution-contract.md). Source IDs target-qualify, jev-everywhere identify the inspected antecedents in [the provenance catalog](../../references/meta-catalog.md). This is a newly composed portable adaptation; it does not import those sources' historical private paths, grants, compensation defaults or alternative ledgers. Real receipts and current approvals remain required.
