# Voice drift detector (v5.10)

`rig_comms.voice.drift(text, baseline)` diffs a draft's deterministic axes
(1 banned, 2 signature, 3 distribution, 4 paragraphs) against a stored baseline
scorecard: any axis that worsens PASS->WARN/FAIL is reported as drift.

- Baseline = the scorecard of the last APPROVED artifact per surface, persisted
  by the loop ledger under `data/comms/` (one JSON per artifact).
- Shipped in the gate stack: voice_v2 gate blocks only on hard fails; drift
  deltas are surfaced for agent judgement, not silent passes.
- Recurring same-axis failures across drafts = voice-drift-alert (v1 pattern):
  correction goes to the fingerprint (via corrections-to-memory), not chat.
