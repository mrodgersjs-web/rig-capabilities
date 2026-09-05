---
name: rig-known-expert-os
description: "Operator entry point for the RIG Known Expert OS — the 12-phase master prompt card for building a forward-deployed AI strategist & engineer, transcribed verbatim and made executable by rig_capabilities/expert_os.py and rig_capabilities/evidence_ledger.py. The card is truncated on disk: Phases 1-10 carry their verbatim gate criteria, Phase 11 keeps only its one-line objective, and Phase 12 is absent entirely, so GATES has keys 1..10 ONLY and a phase whose gate text is not on the card can never be reported as passed. Use to advance a phase against named deliverables, to validate the mandatory Evidence Ledger (rule 15), and to enforce rule 3 in code: never place an unverified claim on a résumé."
allowed-tools: Bash Read Grep Write
owner: rig-intelligence
domain: Agent engineering / career-strategy operating system
status: Stable
verified_by: jake
verified_on: 2026-09-01
outcome: "agent-engineering: Expertise construction advances phase-by-phase against the card's verbatim gates, every publishable claim sits in the Evidence Ledger at L3+ depth, and no truncated or absent phase can ever be declared passed"
done_when:
  - file:rig_capabilities/expert_os.py
  - grep:rig_capabilities/evidence_ledger.py:unverified_claim_on_resume
  - cmd:./bin/rig-capabilities expert-os phases --json | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['12']=='absent_at_source'"; test $? -eq 0
great_example: examples/great/agent-engineering/rig-known-expert-os.md
quality_floor: 0.6
---

# RIG Known Expert OS — Operator Entry

The source card ("RIG Known Expert OS — 12-Phase Master Prompt for a
Forward-Deployed AI Strategist & Engineer.md", 530 lines) exists **as a
truncated artifact**: it titles 12 phases but its text carries 11 headings;
Phase 11 keeps only its one-line objective ("Translate the validated expertise
into a bounded offer."), Phase 12 is absent, and only Gates 1–10 were written.
Every string in `rig_capabilities/expert_os.py` is transcribed verbatim from
that card. **Nothing was authored here, and nothing may ever be.** No Phase 11
body, no Phase 12, no Gate 11/12 substitute criterion.

## What is on disk (the honest phase table)

| # | Phase (verbatim title) | Status |
|---|------------------------|--------|
| 1 | Select the problem to own | gated |
| 2 | Reverse-engineer the market and target roles | gated |
| 3 | Mine scars, decisions, and proof | gated |
| 4 | Construct the category point of view | gated |
| 5 | Create signature intellectual property | gated |
| 6 | Build the guinea-pig reference implementation | gated |
| 7 | Convert positioning into résumé evidence | gated |
| 8 | Engineer the interview system | gated |
| 9 | Build the searchable expertise architecture | gated |
| 10 | Run the 90-day MAP deployment | gated |
| 11 | Turn the system into the RIG offering | `objective_only_truncated` |
| 12 | — (no heading exists on the card) | `absent_at_source` |

`PHASE_STATUS` marks 1–10 `gated`, 11 `objective_only_truncated`, 12
`absent_at_source`. `GATES` has keys 1..10 ONLY — `GATES[11]` and `GATES[12]`
raise `KeyError`. `advance(11, …)` returns `ok: false` with
`status: "objective_only_truncated"`; `advance(12, …)` returns `ok: false` with
`status: "absent_at_source"`. Neither is ever reportable as passed, by any
operator, in any report.

## Depth ladder

`L1_surface → L2_synthesis → L3_scar → L4_judgment → L5_procedure`. The card
prioritises L3–L5, so `MIN_PUBLISHABLE_DEPTH = "L3_scar"`: an L1/L2 claim is
work-in-progress, never publishable expertise.

## Commands

```bash
# The phase table, straight from the module:
./bin/rig-capabilities expert-os phases --json

# Advance one phase against its named deliverables (JSON: slug -> artifact):
./bin/rig-capabilities expert-os advance --phase 3 --evidence /tmp/phase3.json --json
# -> {"ok", "gate" (the verbatim Gate-N criterion), "missing" (named slugs),
#     "status", "title", "deliverables"}
# Unknown phase -> ValueError; phase 11/12 -> ok:false with the truncation
# status, never a gate verdict.

# Evidence Ledger (rule 15's table, mandatory columns exactly:
# id, claim, evidence, type, confidence, allowed_use):
./bin/rig-capabilities evidence validate               # default evidence_ledger.csv
./bin/rig-capabilities evidence validate --ledger tests/fixtures/fable2031/evidence-ledger-unverified-resume.csv
./bin/rig-capabilities evidence resume                 # only rule-3-clean rows (exit 1 if none)
```

## Rule 3 in code — the résumé gate

The card's rule 3: *"Never place an unverified claim on a résumé."* A ledger row
whose `allowed_use` includes `resume` must satisfy **all three**:

1. `type: direct` (not `inferred`, never `planned`),
2. `confidence >= 0.8` (`RESUME_MIN_CONFIDENCE`),
3. `evidence` names a path that resolves on disk.

Any miss collapses to the single reason `unverified_claim_on_resume` — a résumé
claim never gets a partial pass. A non-résumé row with an unresolvable path
reports `evidence_missing` instead. Full reason vocabulary:
`missing_field:<col>`, `unknown_claim_type:<v>`, `unknown_allowed_use:<v>`,
`confidence_not_numeric:<v>`, `confidence_out_of_range:<v>`,
`unverified_claim_on_resume`, `evidence_missing`.

Lanes are the declared ASCII set `(resume, interview, content, internal)`. The
card's own accented spelling is **not** an alias: a row written
`allowed_use: résumé` is rejected as unknown rather than slipping past rule 3.
The ledger fails closed, never open.

## Register linkage (this skill writes no register rows)

`register.py` owns the rows; this skill only states the mapping:

- Phase 1–10 deliverables become register rows with studio `Strategy` or `GTM`;
  subsystem `steering` for intake/offer work, `aero` for the public surface.
- The Phase-11 offering is a row of `type: offer` pinned at
  `maturity_M0_5: 0` for as long as its source section stays truncated.
- The card's lagging indicator "qualified conversations" maps onto the
  **existing** `booked_qualified_conversations` register row — it is never a
  second revenue KPI.

Honest current state at authoring: the Realign bookings artifact
(`data/fable2031/bookings-2026-W36.json`) carries **zero** qualified bookings
by evidence. No phase advance, ledger row, or report may imply a booking, a
revenue number, or a convergence improvement exists before the evidence does.

## Non-negotiables

1. **Never synthesise Phase 11 body text, Phase 12, or Gate 11/12** — in this
   repo, in a report, or in a prompt to a model. Recovery route if a fuller
   card surfaces: Recall or `~/.rig/bin/riglake-mount-ensure`; until then the
   truncation ledger (`docs/TRUNCATED-SOURCES.md`) is the truth.
2. **A gate is the card's verbatim text or it does not exist.** `advance()`
   checks deliverables against `GATES[phase]`; no substitute criterion may be
   authored for phases 11–12.
3. **The ledger is mandatory before the résumé.** Phase 7 output is exactly a
   ledger whose résumé rows pass rule 3 — not prose, not memory.
4. **L3_scar floor on anything published.** Surface synthesis (L1/L2) stays
   internal.

## Rationalizations to Reject

| Shortcut | Why It's Wrong |
|----------|----------------|
| "Phase 12 is obviously about X — write the gate" | The card ends at Sources after Phase 11's objective. Authored gate text makes a verdict on content that does not exist — the definition of fabrication this whole system exists to refuse. |
| "`advance(11)` is close enough, it has an objective" | `objective_only_truncated` is a terminal status, not a soft gate. ok:false carries the reason. |
| "Résumé row, confidence 0.7, it's basically direct" | `unverified_claim_on_resume` collapses all three requirements to one reason on purpose. No partial pass exists to negotiate with. |
| "`allowed_use: résumé` — the card spells it that way" | The lane set is ASCII-declared; the accented lane is rejected. Failing closed is the design, not a typo tolerance failure. |
| "One implied booking won't move the numbers" | Bookings are ZERO by evidence right now; every report reads `booked_qualified_conversations` from the register. An implied booking is a fabricated number with a story attached. |

## Success Criteria

- [ ] `expert-os phases --json` reports the eleven on-disk phases with 11 `objective_only_truncated` and 12 `absent_at_source`
- [ ] Any phase advance names every deliverable slug in `missing` and quotes the verbatim gate
- [ ] `evidence validate` is green on the live ledger, and the unverified-résumé fixture exits non-zero naming `unverified_claim_on_resume`
- [ ] Every published claim traces to a ledger row at L3+ whose `evidence` path resolves
- [ ] No artifact anywhere contains authored Phase 11 body, Phase 12 content, or Gate 11/12 text
