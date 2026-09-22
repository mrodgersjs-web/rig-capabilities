# Red-Team Register (v19.5) — attacks already run, with their command

Every row is a planted failure that PROVED the gate goes red, then was restored.
No row is aspirational.

| # | attack | expected | result |
|---|---|---|---|
| R1 | banned word in draft (`Unlock seamless…Game changer!`) | voice_v2 RED | ✅ exit 2, `can_ship:false`, 4 named blocks |
| R2 | plant-failure suite per gate (agf, rig_comm_v10, voice_v2, wound×2, fabrication, rubric) | each RED-capable | ✅ `tests/test_gate_stack.py` exit 0 (proves RED paths fire) |
| R3 | private lane scored without `--human` | exit 3 PRIVACY_LOCK | ✅ CLI + MCP both refuse; no draft produced |
| R4 | 4th correction on one artifact | exit 5 refuse + escalate + error trace | ✅ proven 1-3 pass, 4th refuses |
| R5 | tamper installed SKILL.md (codex copy) | doctor drift exit 2 | ✅ drift:true exit 2; restore exit 0 |
| R6 | predictions with <10 resolutions | UNMEASURED, no fake Brier | ✅ deficit named; ≥10 → scored (0.16 HOLD) |
| R7 | ship with red gate | refuse, exit propagated | ✅ `cmd_ship` re-runs gate fresh; no packet written |
| R8 | fabricated number in public lane | fabrication gate RED | ✅ regex fires; bare years excluded (context, not claim) |
| R9 | MCP packet for love-notes without human:true | JSON-RPC error -32001 | ✅ PRIVACY_LOCK |

## Next attacks (queued, not claimed)
- mirror leak probe: regenerate from a dirty canonical tree → manifest sha must change
- ledger torn-line injection → readers must skip+log, never crash
- persona-file symlink → must refuse non-regular files outside `~/.rig/comms/personas-private`

Kill switches: `~/.rig/comms/KILL_{corpus,recall,monitor}` (cron specs); the
monitor itself is killable. Freeze discipline: paused state is the state — no
bulk-resume without an inventory first.
