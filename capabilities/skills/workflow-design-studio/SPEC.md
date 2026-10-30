# SPEC — Workflow Design Studio v3

**Mission (Mike, via Jake):** Mike designs an agentic workflow in plain language; it compiles into
every runtime surface as draft artifacts, with the REGISTRY as single source of truth, reverse
extraction of what already runs, a drift doctor, and a dry-run before any embed.

Jordan Jr (AI Engineering) under Jake's conductor, 2026-10-26.
Build record: `lattice/RECORDED-CELL.md` — **L4-D3-A1-I1, BMS 0.89 = A1 PYTHON_ONLY**, recorded
before the first file. The compiler has no model in its decision path; unknown values are refused
(exit 2), never guessed.

## 1. The pipeline: DESIGN -> REGISTRY -> COMPILE -> DRY-RUN -> EMBED

1. **DESIGN (plain language).** Mike writes the workflow as a design card: one intent sentence,
   plain-language steps, plain-language stop conditions, outputs, schedule in words ("weekdays
   7:03am Denver"), and who owns it. The card IS `registry/<id>.yaml` — plain language in,
   frozen vocabulary only where a machine must decide (freq, days, timezone, model, permissions).
2. **REGISTRY (SSOT).** The design row is the single source of truth. One row per live workflow:
   `id, name, surface[], schedule, owner, done-test, last-drift-check, embed_state, routes`.
   Compiled outputs, imports, and drift verdicts all key back to the row.
3. **COMPILE (A1, deterministic).** `python3 compiler/compile_workflow.py registry/<id>.yaml`
   emits DRAFT artifacts for SEVEN surfaces under `out/<id>/` + `MANIFEST.json` (sha256 per
   artifact). Byte-identical outputs for identical inputs (verified: two runs, equal MANIFEST).
4. **DRY-RUN.** `--dry-run` prints the embed plan and writes nothing. `--check` validates the row
   (frozen vocab, schedule grammar, route allowlists against the live grokbot catalog + litellm
   model_list) without writing. Fail-closed: bad time, bad day, outward without Gate-D, unknown
   model -> `COMPILE REFUSED`, exit 2.
5. **EMBED (human, one surface at a time).** `out/<id>/EMBED.md` is the runbook. Every embed is a
   human action; anything outward, recurring, or paid is Gate-D. The studio writes NOTHING into
   live surfaces, `app/jake_brain/**`, `app/jake_brain_nightly/**`, or Clients.ai.

## 2. Registry schema (design row)

```yaml
id: daily-scorecard-loop          # lowercase slug, 3-49 chars
name: Daily Scorecard Loop
owner: jake                       # who answers for the workflow
intent: <one plain sentence>      # what it does and for whom
schedule:
  freq: WEEKLY                    # frozen: DAILY | WEEKLY
  days: [MO, TU, WE, TH, FR]      # frozen day codes, WEEKLY only
  time: "07:03"                   # HH:MM
  timezone: America/Denver        # Area/Location
  start_date: "2026-10-27"        # YYYY-MM-DD
model:
  aside_provider: mimo-plan       # must exist in grokbot catalog/aside-models.json
  aside_model: mimo-v2.6-pro
  thinking: medium                # frozen: minimal|low|medium|high|xhigh
  grokbot_lane: rig-scorecard-daily
  grokbot_route_model: rig-local-first   # must exist in live litellm.yaml model_list
permissions: read-only            # frozen: read-only | full-access
steps: [...]                      # plain-language bullets (compiled to prompt + card body)
gates: [...]                      # plain-language stop conditions (compiled to done-when)
outputs: [...]                    # artifacts the run must produce
outward: false                    # true requires gate_d_required: true or compile refuses
gate_d_required: true
```

Machine rows add: `surface[], done-test, last-drift-check, embed_state, routes, prompt_sha256`
(see `out/<id>/registry/row.yaml` and `registry/imported/aside-routines.yaml`).

## 3. The seven embed surfaces (all DRAFT artifacts in `out/<id>/`)

| # | surface | draft artifacts | real target schema (verified on disk) | embed action (human) |
|---|---|---|---|---|
| 1 | Aside routines | `aside/routine.json` | `~/.aside/u/0/state.db` routines: 18 cols, DTSTART;TZID+RRULE, metadata{}, session_config{} | insert with minted id, status active, memoryPath created |
| 2 | Grokbot router+behavior | `grokbot/lanes.fragment.yaml`, `grokbot/config-model-block.toml` | grokbot-allmodels `lanes.yaml` (gen.py input, append-only) + `~/.grok/config.toml` [model.X] | merge fragment -> run gen.py -> review candidate -> place TOML block |
| 3 | Jake harness/brain loop | `jake/loop-card.md`, `jake/heartbeat.json` | rig loop-card frontmatter (outcome/done_when/state/gate_d_required/cadence/quality_floor) + prime-agent heartbeat | stage card or arm heartbeat; DORMANT until armed (Gate-D) |
| 4 | Temporal always-on schedule | `temporal/schedule-spec.py`, `temporal/schedule.json` | `~/.rig/runtimes/temporal-runners/lane_schedules.py` Schedule+ScheduleSpec+ScheduleState | register paused=True; unpause is Gate-D |
| 5 | goal-harness specs | `goalspec/harness-goalspec.draft.json` | `out/harness-goalspecs/*.json` shape: goals[0].gates[] with 9 keys/gate | promote via the goalspec owner's compile flow |
| 6 | jake-brain loop cards | `jake-brain/loop-card.md`, `jake-brain/COORD.md` | jake-brain loop-card store (app/jake_brain owner) | owner places the card; this studio NEVER writes app/jake_brain/** — COORD.md is the handoff |
| 7 | Aside chat briefs | `aside-chat/brief.md`, `aside-chat/brief.json` | aside_chat_new brief (the `aside-chats` driver / prime-aside-driver) | Mike or the driver opens the chat; quiet-hours bind |

The prompt body is compiled ONCE from intent/steps/gates/outputs and reused verbatim on surfaces
1, 3, 6 (single source, no divergence).

## 4. Registry as SSOT + reverse extraction + drift doctor

- `registry/imported/aside-routines.yaml` — **122 live Aside routines reverse-extracted**
  (`compiler/extract_routines.py`, read-only sqlite URI): id, name, schedule (rrule), owner,
  model, prompt_sha256, embed_state. 87 active + 35 other. Their done-test is honestly
  `none-recorded (imported; design predates the studio)`.
- `compiler/drift_doctor.py` (modeled on `tac3 surfaces check`) — compares every design row to
  its live surface. Verdicts: OK / DRAFT / DRIFT / UNCHECKED (no deterministic probe yet —
  surfaces 4, 5, 7 report UNCHECKED rather than guess). **Exit 2 on any DRIFT.**
  Today's run: `rows=123 ok=122 draft=1 drift=0` -> exit 0.
- `last-drift-check` in every row is refreshed by the doctor; `never` is a visible gap, not silence.

## 5. Pilot vertical slice — `daily-scorecard-loop`

Designed in plain language in `registry/daily-scorecard-loop.yaml`; compiled to **all 7 surfaces**
under `out/daily-scorecard-loop/` (15 files incl. MANIFEST + registry row). Weekdays 07:03
Denver, read-only scorecard, `outward: false`, `gate_d_required: true`, state DORMANT everywhere.
Everything is a draft; nothing installed.

## 6. Reliability layer (the studio fixes its surfaces)

`RELIABILITY/RELIABILITY.md` + `RELIABILITY/patches/*.patch` (DRAFT, single-writer apply after
owner sign-off): (1) relay pairing flaw — t_say mints a fresh job id per re-send; patch dedupes
by text+window at the bridge and marks superseded jobs `superseded-by:<job>` at the watchdog;
(2) watchdog TMPDIR mismatch — probe fix already landed in `aside_watchdog._daemon_socket()`, the
/tmp compat symlink is now a named contract, one owner question open (daemon-start env export);
(3) reliability metrics (`metrics/measure_reliability.py`, re-runnable) sit in the before/after
table: stuck-relays 19 ever flagged, watchdog false-RED 5 (=100% of jake-alive reds), relay
round-trip median 41.5s / mean 82.4s / max 375s over 56 polled samples.

## 7. Before/after and the 1000x claim

`metrics/BEFORE-AFTER.md` carries the full measured table. Headline numbers:
**~119 structured units + 3 free-text artifacts + 3 commands (7 surfaces, before) -> 16-field
design row + 1 command (after); 7.4x measured on design-to-live steps; 0 marginal steps per
added surface.** The 1000x claim is honest only on the marginal/revision axis across the
122-workflow fleet — the table says so out loud.

## 8. Constraints honored

A1-first (no model in the decision path; A2-A4 not claimed) · lattice cell recorded before build ·
nothing outward, everything DRAFT · no writes into `app/jake_brain/**` or
`app/jake_brain_nightly/**` (COORD.md handoff instead) · no Clients.ai changes · reuse-first:
surface schemas taken from live artifacts (state.db DDL, lanes.yaml, config.toml, loop-card
corpus, lane_schedules.py, harness-goalspecs), not reinvented.
