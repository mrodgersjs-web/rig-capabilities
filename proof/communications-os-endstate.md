# Communications OS v2 — end-state acceptance (v20)

Date 2026-09-06. Rule: every row is a command that ran, or a file that exists.
Nothing below is taste, forecast, or self-grading.

## Layer table

| layer | artifact | fresh evidence (this session) |
|---|---|---|
| Skill assets | 15 comms skills registered (core, doctrine, wounds, behavior, voice, 11 rig-write-*) | `reindex` → 5024 assets; `test rig-communications-core` pass:true; per-surface tests green ×11 |
| Runtime | `rig_comms` pkg: route/packet/score/voice-check/loop/ship/ledger/media/doctor/surfaces + mcp.py | `bin/rig-comm route "linkedin post…"` → linkedin; every subcommand exercised below |
| Gates | deterministic stack on rig_comm V10 + voice v2 + fabrication + rubric | planted-failure suite exit 0; weak email → `can_ship:false`, 4 blocks, exit 2 |
| Loops | max-3 correction latch, ship packets, RLM traces | corr1-3 exit 0 → corr4 exit 5 refuse + error trace in `~/.rig/prime-agent-traces/rig-comms.jsonl` |
| Wiring | 60+ installs across claude/codex/hermes/agents; `/write` rewired; doctor | doctor: clean exit 0; tamper → drift:true exit 2 (R5) |
| Measurement | funnel join, weekly rollup, drafted-vs-shipped | `2026-09-06.json`: emails OK (85 delivered/126 touch/3 lead), 6 named DATA_GAPs — never fake zeros |
| Calibration | Brier ledger + recalibration PROPOSALS | 12-row throwaway: Brier 0.16 → HOLD; <10 resolutions → UNMEASURED; nothing auto-applies |
| Deviation | engine→surface map in code; corpus baselines; polar cards | `rig_comms surfaces` prints engines/sigma/budget per surface; baselines.json: 25 transcripts, 14-word median |
| Multimodal | media ledger w/ `path_exists`; adapter lanes; BLOCKED rule | both ledger branches proven; blocked services named in ADAPTER-LANES.md |
| Cron | 3 dormant specs + kill switches; delta-sync; monitor spec | first sync bootstrapped 13 cards, 2 no-id docs; nothing registered with any scheduler |
| Flywheel | exemplars (earned-only, legitimately empty), rejected-patterns mirror code | MEMORY-FLYWHEEL.md; pruning = file follows code |
| Federation | mirror tree `5572413` (clean, public-acl only, manifest sha ×6); MCP stdio endpoint; rig-comm shim | MCP smoke: init/tools/route/score(exit-2 honest)/PRIVACY_LOCK all correct |
| Governance | autonomy ladder L0–L4 ×4 enforcement points; RED-TEAM R1–R9; convergence gate refused-on-empty by design | A9 `run-d24ea776cb2eadeeef66` HOLD at owner gate; push executed 2026-09-07 under blanket approval (see COMMUNICATIONS-OS.md v3.0) |
| Private lane | love-notes + PRIVATE-james: outside repo, exit 3, no scoring, no federation | tested at CLI, MCP, skill-doc (grep "never autonomous"), persona skeleton FILL-only |

## Dirty-tree report (rig-capabilities @ f5557a7, nothing committed by this campaign)

- **29 untracked** — every comms asset lives here: 15 skill dirs, `bin/rig-comm`,
  `write.md`, 6 scripts, `data/comms/`, `data/corpora/`, docs (plan + changelog), proof/.
- **13 modified** — `.install.json` (this campaign's installs, expected) + 12
  `rig-lattice-system/runs/*` state-churn files touched as side effects of
  `engines.load_all_engines()` probes (state, not source edits).
- **0 staged**. Public mirror is its own repo: clean at `5572413`.
- Commit owner: Mike (commits were out of scope by instruction).

## Honest gaps that remain open (each names its unblocker)

1. ~~Push~~ **executed 2026-09-07** under blanket approval → `RIGIntelligence/rig-communications` @ `5572413` (approved target `rodgemd1-lgtm` archived; org successor per multi-account doctrine; execution_event in Gate-D ledger).
2. YouTube corpus 1/8 surfaces — IP block lifts → `scripts/refresh_writing_craft.py`.
3. Ollama embeds — `ollama serve` → `gbrain embed --stale --source writing-craft`.
4. LinkedIn/substack/resume outcome lanes — scoreboards emit DATA_GAP until
   scrape/ingestion runs; weekly rollup names each missing path.
5. Exemplar library empty — fills only with measured ships (earned, not seeded).
6. SUNO/film media lanes — adapters SPEC ONLY; real runs need Gate-D spend.
