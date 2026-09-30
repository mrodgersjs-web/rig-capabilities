---
name: client-delivery-playbook
description: "Stage-by-stage checklist for one RIG client engagement: kickoff, starter pack, build, handoff, proof, health and renewal, each with the artifact that must exist before moving on. Use when starting, running or closing out a client engagement."
---

# client-delivery-playbook

Keep one folder per client. Each stage ends with its artifact in that folder.

1. **Kickoff.** Artifact: `kickoff.md` with the client's goal in their words, the one number that proves success and its baseline, owners on both sides, the access list (systems, accounts, who grants them), out-of-scope, and dates.
2. **Starter pack.** Artifact: what the client gets in week one, written so they can use it without us (the smallest useful workflow, a short guide, a contact path).
3. **Build.** One workflow at a time through `app-studio` or `design-studio-os`. Artifact per workflow: what changed, where it runs, how to switch it off.
4. **Handoff.** Artifact: `runbook.md` (how it works, what can break, who to call), a recorded or written training, and the access transfer checklist signed off by the client.
5. **Proof.** Artifact: before and after on the kickoff number, sealed as a ProofPacket (`rig-proof-packet-builder`). No number, no claim.
6. **Health and renewal.** Monthly `cs-health-score-audit`; 30 days before term end, `cs-renewal-readiness-check`.

## Gates

Messages to the client, deploys, invoices and anything public stop at Gate-D.

## Done-test

Before a stage is called done, its artifact exists in the client folder; the proof stage cites a ProofPacket hash that verifies.
