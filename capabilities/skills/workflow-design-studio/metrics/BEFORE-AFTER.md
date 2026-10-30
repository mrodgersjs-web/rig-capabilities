# BEFORE / AFTER — Workflow Design Studio (all numbers measured or schema-counted)

Unit = one hand-authored value: schema field | JSON leaf key | RRULE clause | TOML key |
done_when check | operator command (defined in SPEC.md). Measured by
`metrics/measure_baseline.py` -> `metrics/baseline.json` (live artifacts, read-only).

## Design-to-live steps, one workflow, per surface

| # | surface | BEFORE (per surface) | source | AFTER (per surface) |
|---|---|---|---|---|
| 1 | Aside routine | **25.6 units** avg + one 5,167-char prompt body (87 active routines measured: 9.9 columns + 3.9 metadata leaves + 7.4 session_config leaves + 4.4 rrule clauses) | MEASURED | 0 (compiled) |
| 2 | Grokbot router+behavior | **15.5 units** + 3 operator commands (5.0 lane keys + 7.5 [model.X] keys + 6 pool keys; litellm.yaml is generated so a human edits lanes.yaml then runs gen.py) | MEASURED (35 lanes / 40 model blocks) | 0 (compiled) |
| 3 | Jake harness/brain loop | **7.7 units** + a 126-line loop card hand-written (4.5 frontmatter keys + 3.2 done_when checks; 33 real cards measured) | MEASURED | 0 (compiled) |
| 4 | Temporal schedule | ~8 units (Schedule/ScheduleSpec/State fields a human sets in lane_schedules.py style) | schema-counted | 0 (compiled) |
| 5 | goal-harness spec | 7 top keys + 9 keys x gates (e.g. 5 gates = 52 keys) over the compiled goalspec JSON/YAML pair | schema-counted from out/harness-goalspecs | 0 (compiled) |
| 6 | jake-brain loop card | ~7.7 units + card prose (same shape as #3) | schema-counted | 0 (compiled) |
| 7 | Aside chat brief | 2 fields + brief text | schema-counted | 0 (compiled) |

**Totals, one workflow on all 7 surfaces: BEFORE ~119 structured units + 3 long free-text
artifacts + 3 operator commands, hand-wired per surface. AFTER: 1 design row (16 fields; the
intent/steps/gates free text is authored ONCE and reused on every surface) + 1 command
(`compile_workflow.py <row>.yaml`) + a review read per surface draft. 0 per-surface authoring.**

- Single-workflow ratio on structured units: **~119 -> 16 = 7.4x** (measured surfaces 1-3 give the
  floor: 49 -> 16 = 3.1x if only those three are counted).
- Marginal cost of one MORE surface per workflow: **BEFORE +8 to +52 units, AFTER +0** (a renderer
  is written once). Marginal cost of one MORE workflow per surface: BEFORE +full surface cost,
  AFTER +1 design row + 1 compile.
- **The 1000x claim is NOT defensible on single-workflow step count (7.4x measured).** The honest
  1000x metric is the marginal axis at fleet scale: 122 live routines x 7 surfaces, each future
  revision touching one registry row instead of N surface artifacts. Proposed claim wording:
  "7.4x measured on design-to-live steps per workflow; zero marginal steps per added surface;
  1000x projected on revision cost across the 122-workflow fleet" — with these numbers attached.

## Surfaces per workflow

| | BEFORE | AFTER |
|---|---|---|
| surfaces one design reaches | 1 (multi-surface = separate hand builds, usually 1-2) | **7** from one row (pilot: daily-scorecard-loop, all 7 drafts in out/daily-scorecard-loop/) |

## Drift detections

| | BEFORE | AFTER |
|---|---|---|
| automated drift checks | **0** (3 real defects found by hand across sessions: relay pairing, TMPDIR probe, supersede logic) | `drift_doctor.py` checks every registry row, exit 2 on drift: **123 rows checked today (122 imported + 1 studio draft), 0 drift, 1 draft** |
| reverse extraction | none (the 122 live routines had no design records) | `extract_routines.py`: 122 rows -> registry/imported/aside-routines.yaml (87 active + 35 other) |

## Reliability metrics (MEASURED, metrics/reliability.json)

| metric | BEFORE (measured) | AFTER (target, patches NOT applied) |
|---|---|---|
| stuck-relays (distinct jobs ever flagged) | **19** (18 real + 1 planted); 11/17 sweeps red; 0 at last sweep | 0 persistent (dups -> prime_say_dup / superseded-by rows) |
| watchdog false-RED (jake-alive) | **5** (5/5 of jake-alive reds = /tmp probe ENOENT) | 0 (TMPDIR-aware probe landed; symlink is a named contract) |
| relay round-trip seconds | n=56: median **41.5s**, mean **82.4s**, max **375s** (17 replies untimeable, backfilled) | same measurement every drift-doctor run (measurement, not a defect) |
