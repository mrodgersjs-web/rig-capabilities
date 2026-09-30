---
name: client-delivery
description: "Deliver for a paying RIG client after the sale: kickoff and access, a starter pack, the scoped build or automation, handoff and training, proof of results, health checks and renewal. Use for a client kickoff, a starter pack, a build or CRM or site setup for a client, a handoff, a results report, or renewal prep."
---

# client-delivery

Full map of children with paths: `LAYERS.md` next to this file. Owner agent: clara-customer-success.

## Route

| Task | Skill |
|---|---|
| Run a client engagement stage by stage | `client-delivery-playbook` |
| Health score, churn risk, renewal readiness | `cs-health-score-audit` (with `cs-churn-risk-triage`, `cs-renewal-readiness-check`) |
| Go/no-go before a client launch | `gtm-launch-readiness-checklist` |
| Provision hosting, database, domain, email or payments for a client app | `golive` |
| The build itself | `app-studio` or `design-studio-os` metas |

## Rules

- Scope is written down before work starts: outcome, out-of-scope, and the number that proves success (`pmm-productized-service-offers` for packaging).
- Client data stays in that client's lane. Ideawake has its own meta, and the browser may be signed in as the client, not Mike.
- Every claimed result carries a ProofPacket (`rig-proof-packet-builder`).
- Anything sent to the client, deployed for them, or billed stops at Gate-D.

## Done-test

Each stage in `client-delivery-playbook` leaves its artifact in the client's folder before the next stage starts, and the results report cites a ProofPacket hash.
