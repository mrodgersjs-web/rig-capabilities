---
id: rig-hq-sub-j9-jacob-draft
version: 1
status: draft
tier: sub
department: Office of the CEO
agent: none (draft-only lane)
parent: rig-hq-prompt-jacob-lane-draft
task: Recurring sub-prompt (J9): produce one Jacob-lane draft and hold it for Mike
triggers: jacob draft, draft jacob clip, jacob lane artifact
sources: ~/.rig/jake/aos/maps/aside-links/jtbd.json (J9), ~/.rig/jake/aos/maps/aside-links/team-plan.json lane_c
provenance: first-party RIG design | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Jacob draft (J9 recurring) — DRAFT ONLY

**Trigger.** Anything in Jacob's lane needs an artifact: film cut, Hudl clip,
recruiting material, minor-lane content.

**Typed inputs.** `spec_lines` (e.g. "everything past 40 seconds deleted"),
`source_assets` (exact paths), `colors` (e.g. "Pewaukee Pirates red, black"),
`expected_handle`.

**Steps.**
1. Assert the signed-in handle against `expected_handle` before anything else; a
   mismatch halts everything (interrupt sub handles it).
2. Bind to the exact source asset bytes; enforce each spec line literally.
3. Produce the draft; check guardian/consent state if any person appears.
4. Hold: the artifact is `DRAFT READY — HELD FOR MIKE`, never scheduled or sent.

**Output format.**
```
STATUS: DRAFT READY (HELD FOR MIKE) | BLOCKED <reason>
Draft: <path>
Spec lines: each met/not met
Handle assert: <match|mismatch>
Consent: <record path or n/a>
```

**Expected output.** One draft that Mike can approve as-is.

**Done test.** Spec lines each checked, handle assert recorded, hold explicit.

**Failure handling.** Mismatch or missing consent -> BLOCKED and halt; no partial
publish, no retry that touches the account.

**Persistence.** Draft in the Jacob draft folder; nothing auto-queued.

**Redaction.** No account credentials anywhere.

**Stop / escape hatch.** Ask Mike rather than infer a spec line; a minor's lane never
runs unattended.
