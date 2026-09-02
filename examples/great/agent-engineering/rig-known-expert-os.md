---
name: great-rig-known-expert-os
lane: agent-engineering
source: canonical-curated
exemplar_of: rig-known-expert-os
description: Reference exemplar — the Known Expert OS operator surface refusing to bless what the truncated card does not contain (Phases 11/12) and rejecting unverified résumé claims by name, on real command output
---

# rig-known-expert-os — reference

Canonical asset `rig-known-expert-os` (skill). Path:
`capabilities/skills/rig-known-expert-os`.

> The 12-phase master prompt card, transcribed verbatim and made executable:
> Phases 1–10 advance only against their verbatim gates, Phase 11 is
> `objective_only_truncated`, Phase 12 is `absent_at_source`, and every résumé
> claim must pass rule 3 in code — direct, confidence ≥ 0.8, evidence path that
> resolves — or it is `unverified_claim_on_resume`.

All transcripts below are real command output from this repo, 2026-09-01.

## The truncation is the point — straight from the module

```console
$ ./bin/rig-capabilities expert-os phases --json
{
    "1": "gated",  ...  "10": "gated",
    "11": "objective_only_truncated",
    "12": "absent_at_source"
}
```

Asking to advance past the truncation returns a refusal, never a gate verdict:

```console
$ python3 -c "from rig_capabilities.expert_os import advance; print(advance(11, {})); print(advance(12, {}))"
{'ok': False, 'gate': '', 'missing': [], 'status': 'objective_only_truncated'}
{'ok': False, 'gate': '', 'missing': [], 'status': 'absent_at_source'}
```

`GATES[11]` and `GATES[12]` raise `KeyError` — the card never wrote them, so no
operator, report, or model may invent them. A gated phase is equally unforgiving
from the other side; Phase 1 with no deliverables names every slug and quotes
the verbatim criterion:

```console
$ ./bin/rig-capabilities expert-os advance --phase 1 --json
{
 "ok": false,
 "gate": "Advance only with an identifiable economic buyer, costly status quo,
          observable transformed state, credible evidence alignment, and a path
          to demonstration.",
 "missing": ["primary_and_secondary_problems", "one_rejected_broad_position",
             "one_sentence_problem_statement", "market_narrative", ...]
}
```

## Rule 3 firing on the planted fixture (the résumé gate)

Ten ledger rows, nine defects, one reason vocabulary, zero partial passes:

```console
$ ./bin/rig-capabilities evidence validate --ledger tests/fixtures/fable2031/evidence-ledger-unverified-resume.csv; echo $?
{
 "ledger": "tests/fixtures/fable2031/evidence-ledger-unverified-resume.csv",
 "rows": 10,
 "invalid": [
  {"id": "E-201", "errors": ["unverified_claim_on_resume"]},
  {"id": "E-202", "errors": ["unverified_claim_on_resume"]},
  {"id": "E-204", "errors": ["unverified_claim_on_resume"]},
  {"id": "E-205", "errors": ["evidence_missing"]},
  {"id": "E-206", "errors": ["unknown_claim_type:asserted"]},
  {"id": "E-207", "errors": ["unknown_allowed_use:investor"]},
  {"id": "E-208", "errors": ["confidence_out_of_range:1.4"]},
  {"id": "E-209", "errors": ["confidence_not_numeric:high"]},
  {"id": "E-210", "errors": ["missing_field:evidence"]}
 ],
 "ok": false
}
1
```

Meanwhile the live ledger validates clean (`"ok": true`, exit 0). The gate is
selective, not decorative.

## Honest state, stated boringly

At authoring the Realign bookings artifact
(`data/fable2031/bookings-2026-W36.json`) counts **zero** qualified bookings,
and the Phase-11 offering row stays pinned at `maturity_M0_5: 0` while its
source section stays truncated. No expertise claim in this system outruns its
evidence — same law as the résumé gate, applied to the register.

**Why this is the exemplar:** every claim the skill makes is either a verbatim
transcription of the card or a command with output above; the two failure
modes the card exists to prevent (inventing the missing phases, and résumé
claims without evidence) are shown being refused mechanically, with non-zero
exits.
