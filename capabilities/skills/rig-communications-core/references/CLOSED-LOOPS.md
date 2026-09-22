# Closed loops (v8) — builder/verifier discipline for writing

The engine separates BUILDER (drafts) from VERIFIER (scores + ships). Same
agent may play both roles in sequence, but never in the same breath: the
verifier acts on the artifact via commands, not on the builder's narration.

## Loop protocol (per artifact)

```bash
cd capabilities/skills/rig-communications-core
PYTHONPATH=. python3 -m rig_comms loop start --surface <s> --artifact <f>
# ... draft, re-draft ...
PYTHONPATH=. python3 -m rig_comms loop correction --surface <s> --artifact <f>   # each re-draft
PYTHONPATH=. python3 -m rig_comms ship --surface <s> --artifact <f>
```

- **Max-3 latch (v8.3, enforced in code):** the 4th `correction` on the same
  artifact is REFUSED (exit 5) and an `escalate` event is auto-logged. A loop
  that needs a 4th pass is a spec problem for Mike, not a 4th try for the agent.
- **Ship gate (v8.4/8.9):** `ship` RE-RUNS the gate stack fresh — a past green
  is not a ship permit. Green → artifact packet (sha256 + full gate JSON) under
  `data/comms/ships/`. Red → refused, exit 2. Red = nothing ships.
- **Real-path verification (v8.8):** every ship packet carries
  `real_path_status: PENDING`. It flips to `VERIFIED` only when the published
  artifact is fetched logged-out (published URL/email event observed). The
  weekly `ledger report` surfaces PENDING debt.
- **ProofPacket:** the ship packet is the artifact-level proof; when the change
  is code- or deploy-backed, additionally seal via the standard ProofPacket
  tooling (`proofpacket_seal`) and store `proof_hash` into the packet.

## Long projects (v8.5 — SWS stage machine)

Novel chapters / feature scripts: one `loop start` per stage
(`detail: {"stage":"outline|draft|revise|lock"}`), never start the next stage
while the current stage's checks are red. Commit per stage.

## Voice-critical pieces (v8.6 — stochastic coverage)

N≥2 drafts from genuinely different frames (different persona, different
deviation engine rung), then read the convergence: agreement = confidence,
divergence = the hidden constraint. Tournament-select the survivor; the
`loop ship` packet names the loser artifacts in `detail`.

## Review gate + Gate-D (v8.7)

Review before publish is the packet's ship-gate line; public lanes additionally
require Gate-D typed approval (`gate_d_required: true` in every green envelope
on linkedin/substack). No approval, no publish.

## Telemetry (v8.10)

`loop_report` gives red rates, correction counts, corrections-per-ship per
surface; drafted-vs-shipped shows what the gates actually filter. Costs stay
out of this lane (see cost-tracking capability).
