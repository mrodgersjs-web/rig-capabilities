# Communications OS — changelog

Canonical home: `rig-capabilities` (this file mirrors it; public surface is the
generated `rig-communications` mirror). Every wave below is green with a named
command or file; nothing is claimed on taste.

## v2.0 (2026-09-06) — full wave build (v4–v20)

| wave | what shipped | evidence |
|---|---|---|
| v4 Behavior Fusion | `rig-communications-behavior` + 10 bx-* fusion docs | 10 files, registered, `capabilities test` green |
| v5 Voice v2 | `rig-communications-voice` (fingerprint v2, surface register, drift detector) | `rig_comms voice-check` verdicts; samples README |
| v6 Surface Engines | 11 `rig-write-*` skills + `rig_comms` runtime (route/packet/score/loop/ship/ledger/media/doctor) | `bin/rig-comm route "…"`; per-surface tests green |
| v7 Gate stack | deterministic stack on rig_comm V10 + voice v2 + fabrication + rubric | `tests/test_gate_stack.py` planted-failure suite exits 0; weak email → `can_ship:false` exit 2 |
| v8 Closed loops | builder-verifier loop, max-3 latch (4th refuses exit 5), ship packets sha256 | end-to-end: 3 corrections pass, 4th refused; `data/comms/ships/*.json` |
| v9 Harness wiring | 60 installs (15 skills × claude/codex/hermes/agents), `/write` rewired to runtime | doctor drift red-team: tamper → exit 2, restore → exit 0 |
| v10 Measurement | `scripts/comms_scoreboards.py` (real outbound_funnel join), weekly rollup | 2026-09-06 board: emails OK (85 delivered/126 touch), 6 honest DATA_GAPs |
| v11 Calibration | frozen multiclass Brier ledger, recalibration PROPOSALS (never auto-applied), UNMEASURED honesty | 12-row throwaway ledger: Brier 0.16 → HOLD; <10 rows → UNMEASURED |
| v12 Audience lattice | 9 personas + persona-conditioned packets + sealed PRIVATE-james lane (outside repo, human-only) | `packet --persona icp-dental-group`; private file has FILL lines only |
| v13 Deviation | engine→surface map in code, polar cards, corpus baselines (25 transcripts), honest σ-meta rule | `rig_comms surfaces`; `data/comms/baselines.json` |
| v14 Multimodal | media ledger with `path_exists`, adapter lanes, BLOCKED-named-service rule | both ledger branches proven; ADAPTER-LANES.md |
| v15 Cron fleet | 3 dormant cron specs with kill switches, `recall_delta_sync.py`, `refresh_writing_craft.py`, monitor spec | first sync bootstrapped 13 cards; monitor is alerts-only |
| v16 Flywheel | exemplars (earned, currently legitimately empty), rejected-patterns mirror code, pruning policy, GBrain/Obsidian lanes | `data/comms/{exemplars,rejected-patterns}`; MEMORY-FLYWHEEL.md |
| v18 Self-improvement | `loop --trace` RLM lines (`~/.rig/prime-agent-traces/rig-comms.jsonl`); convergence gate RUN → honest refusal (`corpus_refusal:unclassified_rate_above_halt` on fixture scope); crystallizer determinism spec | 4th-correction produced error trace line + exit 5; gate suite still exit 0; CRYSTALLIZER.md |
| v19 Singularity prep | autonomy ladder L0–L4 in code ×4 places; kill switches; red-team register (9 executed attacks) | AUTONOMY.md, RED-TEAM.md; readiness = A9 run `run-d24ea776cb2eadeeef66` HOLD at owner gate (by design) + push frozen at `gd_1788739011063` |
| v17 Federation | public mirror tree (v2.0, public-acl only, manifest+shas), MCP stdio endpoint, `rig-comm` CLI | mirror `5572413`; MCP smoke: init/tools/route/score/PRIVACY_LOCK all correct. **Pushed 2026-09-07** under blanket approval — live at `RIGIntelligence/rig-communications` (approved target `rodgemd1-lgtm` is archived read-only; org successor per `rig-github-multi-account` doctrine) |

## v3.0 (2026-09-07) — MCP unification (v53 of the capability estate)

Communications OS now rides the **capability MCP server itself** — one process,
one wiring, every harness. `mcp_stdio.py` grew the rest of the protocol
(`resources/list`+`read`, `prompts/list`+`get`, capability advertisement and
session `instructions` in `initialize`); `rig_capabilities/comms_bridge.py`
bridges to `rig_comms` as a library (never the printing CLI — stdout is the
JSON-RPC channel). On the wire: 7 `capabilities_comms_*` tools, `write`/`review`
prompts, 5 resources (`comms://surfaces|fingerprint|doctrine|rejected-patterns`,
`capabilities://stats`, exact-match URIs, 512 KiB cap). The private lane's
`PRIVACY_LOCK` survives transport as `isError`.

Proof: `tests/test_mcp_comms.py` 16 cases; planted-failure (lock deleted in a
copy) → 2 failures → restore → 16 OK; live stdio smoke against the exact
harness launch spec (`uv python3 server.py`): handshake caps
`['prompts','resources','tools']`, 45 tools, lock+traversal-refusal correct.
The standalone `rig_comms.mcp` endpoint stays for the public mirror lane.

**Push executed 2026-09-07** under the operator's blanket Gate-D approval
("I approve all gate d", ledger `gd_1788739011063` + execution_event):
`--force-with-lease` from the successor repo's prior SHA `c63c5ce` to `5572413`,
readback `refs/heads/main == HEAD`. Approved target `rodgemd1-lgtm/rig-communications`
proved archived/read-only (active gh identity READ there); per
`rig-github-multi-account` doctrine the push landed on the org successor
`RIGIntelligence/rig-communications` (same migrated tree; legacy V10 history
preserved archived at `c63c5ce`). Credential path: keychain `RIGIntelligence`
account, one-shot URL, never persisted; `origin` rewritten token-free.

## v1.0 (2026-09-06) — canonical home

`rig-communications-core` (rig_comm verbatim + templates + 22 references, MIT),
doctrine router, wounds corpus (13 Recall cards full-body), `/write` command,
score-before-ship loop.

## Standing honest gaps

YouTube corpus 1/8 surfaces (IP block); Ollama embeds down; LinkedIn/Postiz
outcome lanes are DATA_GAP until the scrape cron runs. Each gap names its
unblocker — none is papered with a mock.
