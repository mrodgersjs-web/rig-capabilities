# Comms Self-Healing Monitor (v15.9) — alerts-only watchdog

Cycle pattern follows jake-self-healing-monitor (M1-M5), scoped to Comms OS.
**Dormant by default. Alerts only. No auto-restart. No bulk-resume of frozen lanes.**

- **M1 stall**: corpus/delta jobs — last proof entry older than 2× cadence → ALERT (stale), never re-run.
- **M2 drift**: `rig_comms doctor` drift=true (SKILL.md sha mismatch across harnesses) → ALERT with skill+harness names.
- **M3 blocklist/privacy**: any score/ship run that touched love-notes without `--human` (should be impossible — exit 3) → CRITICAL, page Mike.
- **M4 proof writers**: data/comms/scoreboards/ has no file for today while a job claims OK → ALERT.
- **M5 north-star**: weekly rollup missing or drafted_vs_shipped all-zero while ships ledger non-empty → ALERT.

Cadence-aware thresholds: threshold = cadence_min * 2 (fixed 90min thresholds regressed before).
Freeze discipline: when crons are paused, the pause IS the state; the monitor reports the
inventory and waits. `~/.rig/comms/KILL_monitor` stops the monitor itself.
