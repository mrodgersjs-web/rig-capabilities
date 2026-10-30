---
name: job-daily-company-due-diligence
description: Build a dated source-backed employer dossier for role understanding and interview questions.
metadata:
  version: 1.4.0
  origin: newly-composed-source-grounded-step
---

# Company due diligence

## Inputs
Verified employer/role identity, current JD and public research access.

## Actions
Resolve employer versus parent, subsidiary or similarly named company. Read dated first-party pages, annual reports and relevant announcements where available. Capture business model, products, customers, operating environment, role priorities, relevant initiatives and sourced changes. Separate event date from retrieval date and historical announcement from current status. Label inference and unresolved contradictions.

## Outputs
Dossier with source URL/artifact/hash, date, employer identity, fact or inference label, requirement relevance and gaps.

## Gates
Never invent hiring-manager beliefs, layoffs, growth, funding, interviewer identity or candidate participation. Source statements remain attributable claims rather than independent proof of every reported outcome.

## Recovery
If access is blocked, record the precise gap and use supported alternative public sources. Do not bypass sign-in restrictions or turn a snippet into a full source. Refresh stale facts before employer-facing use.

## Required skills and contracts
- [employer-initiative-research](../../steps/employer-initiative-research/SKILL.md).
- [ideal-candidate-persona](../../steps/ideal-candidate-persona/SKILL.md).
- [jev-decision](../../steps/jev-decision/SKILL.md).

Follow the [daily execution contract](../../references/execution-contract.md). Source IDs company-researcher, traject-os identify the inspected antecedents in [the provenance catalog](../../references/meta-catalog.md). This is a newly composed portable adaptation; it does not import those sources' historical private paths, grants, compensation defaults or alternative ledgers. Real receipts and current approvals remain required.
