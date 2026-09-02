---
name: rig-capabilities-register
description: Operate the M0–M5 capability register — validate rows, diff a week, name flagged owners, recompute C_t/A_t, and run the weekly Realign gate, which is dry by default.
argument-hint: "[validate|diff|flags|converge|realign]"
allowed-tools: Read, Bash
category: meta
outcome: "meta: a week moves only when every number in it resolves to a file on disk — zero bookings is a verdict, never a gap to fill in"
done_when:
  - file:capabilities/commands/rig-capabilities-register.md
  - grep:capabilities/commands/rig-capabilities-register.md:zero by evidence
  - cmd:test 1 -eq $(python3 -c 'from rig_capabilities.register import gate_register as G; print(1 if G(".")[0] else 0)')
  - cmd:test 0 -eq $(python3 -c 'from rig_capabilities.register import load_bookings as L; print(L("data/fable2031/bookings-2026-W36.json")["count"])')
  - cmd:python3 -m unittest tests.fable2031_register
great_example: capabilities/commands/rig-capabilities-register.md
acl: public
quality_floor: 0.7
---

# rig-capabilities-register

The store is `capability_register.csv` at the repo root: 21 committed rows, the criteria card's
field order (`id, name, subsystem, studio, type, maturity_M0_5, automation_band, weight_w,
evidence_paths, harness_signed, verifier_named, proof_status, target_M_2031, target_band_2031,
blocking_deps, enables_product_classes, duplicate_of, contradicts, last_touched, owner`) plus the
two reconciliation cells (`source_document_ids`, `contradiction_group`). It is data a verifier can
re-read, not a number quoted in a conversation.

Verb surface: `register validate|diff|flags`, `converge`, `realign` are the operator verbs; the
`done_when` checks below call the module entry points directly, so they verify the same code the
verbs wrap and pass whether or not a given checkout has the verbs wired. Quote the run, never the
intention: a missing verb answers `invalid choice` from argparse, which is a gap to report, not a
result to describe as green.

1. **Validate** (`register validate`; module `gate_register('.')` → `(ok, detail)`). On the
   committed store today the detail is
   `register_ok rows=21 booked_qualified_conversations=weighted`; a failure names every bad row id
   via `row_errors(rows)`. A row is unsound when a vocabulary cell
   falls outside `SUBSYSTEMS × STUDIOS × TYPES × BANDS × PROOF_STATUS` (`target_band_2031` has no
   `manual`: a 2031 target is always an automation band), when `maturity_M0_5` / `weight_w` /
   `target_M_2031` are not integers in `0..5` / `1..5` / `0..5`, when `evidence_paths` or
   `enables_product_classes` is empty, when `last_touched` is not an ISO date, when `duplicate_of`
   names the row itself, or when an `M4+` row names no Verifier. `gate_register` is the function
   that knows a repo root, so it is also where evidence paths must resolve.
2. **Diff** (`register diff`; module `diff_register(prev, cur)`). Week-over-week delta keyed by
   `id`: added, removed, changed, unchanged. A changed row lists the cells that moved — that list,
   not a prose summary, is what the weekly report quotes.
3. **Flags** (`register flags`; module `flagged_owners(rows)`). Names the owners of `M4+` rows with
   no named Verifier. The law is reject-and-flag: M4 means an independent Verifier holds
   termination, and an unowned maturity claim is a claim about the future wearing a number.
4. **Converge** (`converge`; module `convergence.score_week(repo, roots, week=…, previous=…)`).
   Recomputes `E_cap(t)`, `C_t`, `A_t` in Decimal — never float, because this score gets quoted.
   `C_t = 1 − E_cap(t)/Σw_i`; `A_t` is the weight share sitting in bands `A1`/`A2`; a row with
   `target_M_2031 == 0` contributes nothing and is listed under `degenerate_targets` rather than
   dividing by zero. A delta compares against a prior state (`previous=` / `diff_register`); with
   no prior **sealed** week `gate["verdict"]` is `BASELINE_ONLY`, because a first number is a
   coordinate, not progress.
5. **Realign** (`realign`; module `realign.run_week(repo, week, apply=False, roots=None)`).
   **Dry by default** — it scores and returns, writing nothing (`wrote: false`, `would_write: […]`).
   `apply=True` writes the five artifacts under `.context/realign/<ISO-week>/`:
   `register-diff.json`, `convergence_report.md`, `proof/*.json`,
   `doctrine-update-phrase.md`, `operators-weekly.md`. An unsealed run reports `sealed: false` with
   the driver's own `seal_reason`; `apply=True, seal=True` hashes the week, lands a real `proof_hash`
   through `afproof`, and writes the `proof/sealing.json` receipt (CLI: `--apply --seal`). No run
   invents a hash it has not computed. Scan roots matter for timing: bare
   walks the live roots (~61 s here, ending in a `TimeoutError` on `~/mnt/RIGLake`), while
   `roots=["tests/fixtures/fable2031/corpus"]` (verb: `--root`) is repo-only and sub-second — keep
   it inside any 15 s `cmd:` budget.

## The weekly gate: five conditions, all of them or no PASS

1. `ΔC_t > 0` against the previous **sealed** week;
2. `ΔA_t ≥ 0` — automation may hold or rise, never slip;
3. `unclassified_rate ≤ 0.10` and *reported* — an unreported rate never PASSes, and past the halt
   the corpus refuses the week outright (`CorpusRefusal`), so nothing is scored on cards the
   classifier cannot place;
4. booked qualified conversations `> 0`;
5. no unresolved `≥ 5σ` RobustMADZ flag.

Escalations are separate from the verdict, not adjectives on it: three consecutive FAILs →
`LOOP_REBUILD_REQUIRED`; three `C_t` rises with zero bookings → `WEIGHTS_INVALID` (the register is
measuring something nobody buys). `require_booked_row` pins the row `booked_qualified_conversations`
at `weight_w: 5`, studio `GTM`; a missing or underweighted row is
`booked_qualified_conversations_missing_or_underweighted`, because the KPI that pays for the
register must be inside the register.

## Honest state as of 2026-09-01 (quote this, not optimism)

- **Bookings are zero by evidence.** The artifact is
  `data/fable2031/bookings-2026-W36.json`; its `records` array is empty, and a record counts only
  when its `qualification_evidence_path` resolves to a file that exists. `load_bookings` on it
  returns `count: 0`. The `booked_qualified_conversations` register row exists at
  `maturity_M0_5: 0`, `proof_status: none` — a weighted placeholder for a KPI, not evidence of a
  conversation. No booked call and no revenue number exists on this disk; nothing here may be
  written as though one did.
- **The first sealed week exists; a second does not.** `.context/realign/2026-W36/` is on disk, so
  `convergence.sealed_series('.')` returns one entry (`c_t 0.4442528735632183908045977011494253`,
  `verdict BASELINE_ONLY`, `bookings 0`) and a later week has a baseline to move from.
- Therefore `realign` for `2026-W36` reported `verdict: BASELINE_ONLY`, `ok: false`, `bookings: 0`,
  and causes that depended on which roots it scanned. Bare
  (`run_week('.', '2026-W36')`) it reported
  `causes: [unclassified_rate_unreported, booked_qualified_conversations]`; pointed at the
  repo-only corpus (`--root tests/fixtures/fable2031/corpus`) the rate is reported at `0.05` and
  the single remaining cause is `booked_qualified_conversations`. Neither form PASSes, and neither
  is retried into a green: `unclassified_rate_unreported` is the honest recording of a live-root
  scan that did not complete (see `rig-capabilities-corpus`) — an unknown rate is carried as
  unknown, which blocks PASS, rather than being read as zero.
- `convergence.metrics(load_register('.'))` prints `c_t 0.4442528735632183908045977011494253`,
  `a_t 0.5689655172413793103448275862068966`, `rows_scored 21`, `weight_scored 58`. Those are a
  restatement of distance to 2031 with nothing to compare against — **no convergence improvement
  may be claimed from them**, and a week whose only news is that a number appeared is a baseline,
  not a gain.

A zero-booking week is a complete, honest FAIL once a baseline exists — never a retry loop, and
never a register edited until it clears. If the gate will not go green, the register stays as it
is and the report says why.
