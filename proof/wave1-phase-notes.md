# Communications OS — Wave 1 phase notes (2026-09-06)

## Phase A (v1 Canonical Home)
- A1: `rodgemd1-lgtm/rig-communications` cloned @ /tmp/rig-comm-v10, MIT (c) 2026 RIG / Mike Rodgers.
- A2-A3: `rig-communications-core` seeded (rig_comm pkg verbatim; templates 7; references = 17 docs + 5 cards; tests 2) and registered (`registered`, sha in index).
- A3 note: `add <id> --kind command` indexes commands under the file id (`write.md`), matching every existing canonical command; `test write.md` is the correct handle.
- A4: PROVENANCE.md with verbatim MIT; `acl: public` (repo convention: `acl: public` marks publishable; acl_policy.json maps agents→scopes only).
- A5: `rig-communications-doctrine` router skill with surface→doc table; done_when asserts all 21 reference docs exist.
- A6: `/write` command (`capabilities/commands/write.md`), 12 surfaces, v1 router + score-before-ship.
- A7: `bin/rig-capabilities test` green ×3 (import, gates.py, CLI score). Behavioral proof: weak email gated `can_ship:false` with 3 named blocks, exit 2.
- A8: installed to claude harness; `~/.claude/skills/rig-communications-core/SKILL.md` present; `.install.json` ledger entry present.
- A9: `rig-strategy-studio lattice summary` → OK (588 cells). Baseline run on `examples/case-rig-business.json` completed: run-d24ea776cb2eadeeef66, HOLD at owner.explicit_disposition (by design; owner gate). **BLOCKED (informational): master-plan-as-candidate** — case schema fully discovered (25 top-level keys incl. mission/goal_graph/options/economics/evidence_edges/judgments/scenarios/falsification); authoring a faithful Communications-OS-V20 candidate case is a standalone artifact beyond A9's 15-minute timebox. Gate declared non-load-bearing for B/C by plan.
- A10: concept tags `[writing,communications,voice,wounds,gates,scoring]` (+doctrine) resolve in `.concepts.json`; tags written without post-comma spaces because `_tags()` does not strip them (existing quirk, shared parser untouched).

## Open follow-ups
- Consensus.app API key (B1 skip condition) — key acquisition deferred.
- Weekly Recall delta-sync cron → v15.
- Fleet-wide install (codex/hermes/agents) → v9.
- `gbrain embed --stale --source writing-craft` once ollama serves; rerun scraper when the YouTube IP block lifts (7/8 surfaces still at 0 transcripts).


## Phase B (v2 Writing-Craft Corpus) — executed inline (subagent backend `usage_limit_reached`)
- B1: exa API validated all 6 open surfaces; TARGETS.md rewritten with 25 URL-bearing picks. Consensus.app skipped (no key).
- B2/B3: `scripts/scrape_writing_craft.py` (stdlib + yt-dlp; youtube_transcript_api v1 `fetch` API, yt-dlp VTT fallback through vendored cleaner) + `scripts/clean_auto_subs.py` (provenance header).
- B4: two passes (initial + plan-mandated rerun after 15-min pause). YouTube IP-blocked both transcript lanes after 25 fetches: 25 transcripts / 60,360 words (screenwriting-film only), 746 error rows (700×429, 46 resolve). Partial accepted per contingency; resume = rerun idempotent scraper. **V4 literal criterion (≥100) NOT met** — documented in COVERAGE.md.
- B5: substrate.json (rig-substrate-v1) in both populated channel dirs.
- B6: GBrain isolated source `writing-craft` via git mirror `~/.rig/sources/writing-craft` (sync: 25 pages/158 chunks); embeddings deferred — local ollama down, `gbrain embed --stale` pending. Obsidian: index note `90_Generated/writing-craft-corpus/`.
- V5 idempotence: rerun showed fetched=0, manifest 25→25 unchanged. ✓

## Phase C (v3 Wounds) — executed inline
- C1: all 13 cards exported at full body via `~/.jake/abilities/recall/jake_recall` (MCP wrapper truncates at 12k — used the CLI directly). core-wounds.md flagged TRUNCATED (source card itself ends mid-sentence).
- Delta vs plan assumption: the exported corpus carries W3–W6 + W8-flip, not literal W1/W2/W7; depth-layers.md is the 0→10σ Deviation Scale Doctrine, buyer Layers 1–3 live in core-wounds.md. Documented in SKILL.md "Export honesty"; classifier spec refuses emitting W1/W2/W7. Verification grep therefore uses W3.
- C2–C4: SKILL.md (file map + routing), behavior/wound-classifier.md (bx-need-architect-first spec, done-test for v6), weekly delta-sync procedure. Registered + `test rig-communications-wounds` → pass.
## v2 closure (2026-09-06)

Full wave build v4–v20 accepted at `proof/communications-os-endstate.md`
(layer table, dirty-tree report, named unblockers). Push executed 2026-09-07
under blanket approval → `RIGIntelligence/rig-communications` (legacy archived
target disclosed in the ledger's `execution_event`).

## 2026-09-07 v20 closeout (this session)

- v20 engine + 14-tool MCP + 5 assets + install: sealed `~/.rig/proof/jake-pai-mcp/eafa001c-6011-4e79-ba9b-aaaa344ad314.json` (`sha256:367aade0…5073`), verdict done=FALSE by design: push (gd_1788812712326) + how-to corpus (timedtext IP-throttle; recovery pid 8636) open.
- Suite green: 628 passed / 1 skipped after fixing 4 pre-existing reds (missing agentforge workflow asset, applypilot dangling exemplar, canary fixture collection, harness compile shape for the new card) + the BLUF value-carrier fix.
- Mirror `RIGIntelligence/rig-communications` regenerated: local `36c0ed6`, remote still `1daf68a` — push is the ONLY remaining mechanical step, one typed approval away.
- Push EXECUTED under `APPROVE gd_1788812712326 and gd_1788805491811` (Mike typed, Main session): `1daf68a..36c0ed6 main -> main`, readback `refs/heads/main == HEAD == 36c0ed6` (Gate-P X by command); secret sweep clean (scanning API 404 = not enabled; local diff sweep 0 credential hits); grant audit row `gd_1788812712326 -> 36c0ed6` in `~/.rig/github-steward/public-push-grants.json`. gd_1788805491811 verified already-satisfied (remote at 2f14653c ⊇ approved head 3a564507) — no-op recorded, zero push under that approval.
