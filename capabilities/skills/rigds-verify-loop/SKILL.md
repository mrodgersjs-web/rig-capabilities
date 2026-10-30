---
name: "rigds-verify-loop"
description: "JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict. Main skill of rig-design-studio for the verify loop: build green, serve, curl status+title, real captures at a stated viewport, sha256 evidence, executed checks only, honest D85 seal, ProofPacket. Use when verifying a design run or sealing any done-claim from it."
tier: main
parent: rig-design-studio
activation: "Load at the start of any verification task over a rig-design-studio run: smoke checks, captures, export checks, done-claims, D85 sealing."
owner: theo-design
status: Stable
acl: internal
outcome: "design-ux: verification evidence from the real served surface (status, title, captures with sha256), an export check result, an honest D85 seal or refusal chain, and a ProofPacket binding the done-claim to commands and exit codes"
done_when:
  - grep:capabilities/skills/rigds-verify-loop/SKILL.md:ProofPacket
  - grep:capabilities/skills/rigds-verify-loop/SKILL.md:rigds-capture-honesty
quality_floor: 0.6
great_example: corpus/examples/night-v2/artifacts/d85-coordinate.json
---

# Verify loop

Order matters; each rung observes the real thing:

1. **Build green** — the build tool's own exit code and output, not a summary of it.
2. **Serve + curl** — HTTP status and `<title>` of the served surface (local server or deployed URL).
3. **Capture** — screenshot/render of the real surface at a stated viewport, sha256 of the file
   (rigds-capture-honesty governs what counts as real).
4. **Export check** — rigds-export-check over the shipped export file.
5. **Done-claim + seal** — every claim lists the executed commands and exit codes; seal a ProofPacket
   binding claim -> commands -> artifact hashes. Independent verification outranks self-report: the
   builder never self-certifies.

## D85 honesty (carry-over, binding)

- v1 sealed **FAILED-not-certified** (BLOCK UNKNOWN_PROCESS / SUBMITTED_MALFORMED) and that stands. A
  failed or unknown build gate prevents a certification claim — it does not prevent fixing or continuing.
- Produce the classify artifact + score + coordinate record + fresh command evidence; if any gate is
  red or unknown, seal the refusal chain honestly. Never launder A2 through an A1 wrapper.
- Report each dimension separately: installed / configured / consented / loaded / exercised / enforced.

## Lessons from v1/v2 (binding)

- "Executed checks only": the v2 report listed only commands actually run with their real output —
  planned-but-skipped checks are named as skipped, never implied green.
- The deployed-URL curl (200 + expected title) is the cheapest end-to-end proof; do it on the canonical
  alias, not just the raw deployment URL.
- Supervisor "design-studio-serve failed exit 1" was a killed http.server — verify from the product
  surface, not from process noise.

Outward, paid or destructive steps stop at Gate-D: a verified local run is never send authorization.
