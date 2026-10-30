---
name: traject-proof
description: "Traject OS sub-skill, cross-cutting (proof): the claims ledger that decides what Mike may say where — VERIFIED-BY-ARTIFACT / OWNER-ONLY / BANNED-UNSUPPORTED. Publishing any claim is Gate-D. Fix a claim on every surface. Gated by JEV atomic.claim and mission.completion. DEFER when the classifier is down."
tags: [rig, traject-os, sub-skill, proof, claims, evidence]
metadata:
  parent: traject-os
  tier: sub
  stage: cross-cutting
  extends: "aside-job-learning, resume-screening-stack"
outcome: "A claims ledger (claims-ledger.jsonl) classifying every public claim as VERIFIED-BY-ARTIFACT, OWNER-ONLY, or BANNED-UNSUPPORTED, with publishing held at Gate-D and a claim fixed on every surface at once."
activation: "Load whenever a number or claim is about to enter a résumé, room, message, or the public site, and whenever a claim is corrected."
instruction: "Classify each claim into the ledger: VERIFIED-BY-ARTIFACT (public-safe, cites the artifact), OWNER-ONLY (verify before public), BANNED-UNSUPPORTED (never publish). Publishing is Gate-D. When a claim is corrected, fix it on every surface (résumé, headline, room, template) in the same pass or the fix is cosmetic. Gate with atomic.claim."
applies_when:
  env: "<project>/.traject/claims-ledger.jsonl; résumé, rooms, outreach, the public site"
  runtime: "the claims ledger; rodgersintelligence.com proof pages"
  deps: "the proof inventory (VERIFIED / OWNER-ONLY / BANNED); atomic.claim rubric"
  params: "claim text, surfaces it appears on, evidence"
  budget: "per claim; one classification pass over a document"
  scale: "one ledger row per claim"
permissions:
  - fs.read
  - fs.write
  - bash
  - gate-d-required:publish
flow:
  - Classify each claim (VERIFIED-BY-ARTIFACT / OWNER-ONLY / BANNED-UNSUPPORTED).
  - Record the claim and its evidence in claims-ledger.jsonl.
  - Hold any publishing at Gate-D; verify OWNER-ONLY before it goes public.
  - When correcting, fix every surface at once.
done_when:
  - "cmd:python3 capabilities/skills/traject-os/scripts/validate_hierarchy.py"
  - "file:capabilities/harnesses/s1gate/rubrics/atomic.claim.json"
out_of_scope:
  - publishing a claim to the public site (Gate-D)
  - inventing a claim or upgrading an OWNER-ONLY claim without verification
  - the Ideawake client lane and Jacob's minor lane (separate claim rules)
---

# traject-proof

JEV FIRST: a claim's admissibility goes to `rig-s1gate check atomic.claim` BEFORE any
frontier call. Classifier down: DEFER, never guess. Required signals above 0.9.

Cross-cutting sub-skill of `traject-os`. Main skills: `aside-job-learning`,
`resume-screening-stack`. Agent: `traject-proof-curator` (with `traject-claim-verifier`).
Harness: `traject-proof-publish-session`.

## Claims ledger statuses

- **VERIFIED-BY-ARTIFACT** — public-safe; cites a real artifact (e.g. Teletriage $10M+ opex,
  Agentblazer Champion, proof-studio 252 tests, RIG founder 01/2025-, Oracle/Cerner Sr Director
  07/2021-03/2026, the $32B merger, InvestMKE $10M). May appear everywhere, with the artifact.
- **OWNER-ONLY** — verify before public (e.g. Aurora ~$16M downstream revenue, Actuant −20%,
  BD $500K, GWU award, 40-under-40, GPA 3.63, Army Sergeant). Stays in private prep until Mike
  confirms the source; never surfaces as fact from memory.
- **BANNED-UNSUPPORTED** — never publish (e.g. $35M for teletriage, 100+/130+ agents,
  $500K avoided headcount, IntOps 5-layer, Salesforce/Looker/Tableau expertise, owning an SE
  org, PMP, $10M venture fund, the 3h→15min contested claim).

## Rules

- **Publishing is Gate-D.** No claim reaches the public site, a résumé to an employer, or a
  message without Mike's approval where it is outward.
- **Fix a claim on every surface (TL-07).** A number corrected in the résumé is corrected in the
  headline, the room, and the standing template in the same pass, or the fix is cosmetic.
- **Truth beats tactics (TL-10).** A contested number is classified, not softened; the agent may
  not silently weaken a claim only the owner can settle — it is named and put on the open list.

## Lessons that fire here

- **TL-07** fix a claim on every surface at once.
- **TL-10** contested/unsupported claims are classified BANNED or OWNER-ONLY, never published.
