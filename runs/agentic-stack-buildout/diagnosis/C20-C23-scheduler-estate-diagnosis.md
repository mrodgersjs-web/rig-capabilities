# C20-C23 — Scheduler/runtime/process estate diagnosis (2026-09-12)

Cites: inventory/C17-C19-estate-schedulers.md (EstateSchedulers-2), inventory/C18-runtime-inventory.md (RuntimeInventory-2), inventory/C20-process-surfaces.md (ProcessSurfaces-2). All states quoted are installed/configured/enabled/running as separately reported there; UNRESOLVED stays UNRESOLVED.

## D1 — No scheduler of record; cadence claims are unowned

Six scheduling planes coexist: launchd (305 user plists, owns resident services), Hermes cron (232 registered jobs, 2 enabled), Kestra (healthy Docker pair), Temporal (launchd-running, namespace reads FAILING), Prefect (workers running with restart churn; only tunneled :14200 health responds), local PostgreSQL (pg_cron UNVERIFIED). None is authoritative for a new commit-gate cadence, and two cannot even serve today (Temporal namespace, Prefect tunnel-only). Consequence for the plan: the durable ≥24h re-run evidence cannot be attached to any scheduler in this pass; the durable-evidence schedule stays a documented decision (Temporal > launchd > cron; research.md) pending a separately Gate-D-scoped enable. Scheduler-selection claims that cite "installed" as "available" are rejected against these inventories.

## D2 — Runtime claims must be live-probed, never cached

Ollama 0.33.3 installed but daemon UNRESOLVED and model count 0, while `com.rig.local-ollama-desktop-guard` runs under launchd; oMLX 0.6.3rc2 is a separate server (`~/bin/omlx`). Any fleet-routing claim ("model X served") is only admissible with a fresh probe receipt (C18 shows install≠serve). Corollary: cross-family verifier selection (Q-gate) must resolve family from a live invocation receipt, not from config files.

## D3 — Resident listeners are owned; the commit-gate must be a foreground client

Executor daemon :4789 and desktop-commander-router :18001 have exactly one owner each (C20). A gate flow that spawns its own listener would collide (launchd KeepAlive patterns already relaunch crashed residents — a second owner duplicates listeners). Design locked from this diagnosis: commit-gate is a one-shot foreground process that CALLS :4789/:18001 and exits; launchd (if used) supervises the one-shot, never a daemon. Kestra host-port documentation conflicts (C17) reinforce: port claims need live socket receipts.

## D4 — Documentation-vs-reality contradictions to reconcile (feeds C34-C37)

1. Hermes registry: doctrine skills cite `~/.hermes/jobs.json` as root; live root has NO such file — live registries are `~/.hermes/cron/jobs.json` + `profiles/seoresearch/cron/jobs.json`. Doctrine text is stale, not the system.
2. Temporal: documented "running" estate component vs failing namespace reads — the label exists, the service is unusable for new workflows right now.
3. tool_selection.v1 langgraph rule targets a package that is not importable (C18) — rule fires on absent infrastructure.
Resolution rule applied here: inventories (live command receipts) outrank doctrine prose; doctrine corrections are candidates, not unilateral edits.

## Ledger-gate evidence (uncopied — ledgers intentionally left unmutated, D-T3b)

Wave checker 2026-09-12: `wave inventories ok` in all-three and single-file modes (satisfies leaf gates R1/E1/S1 CHECK lines). Estate inventory states read-only 70× with per-row command receipts (E2 substance); UNRESOLVED used 15× (estate), 14× (runtime), 8× (process). Secret-pattern scan across all three files: zero matches (S2 substance). R2 substance partial: mtime receipts on 9 C18 lines; per-line audit open. The .unlazy leaf ledgers were deliberately NOT mutated in slice s3 (scope fence; advisor blockers 1–2); a future properly-scoped pass may check the boxes citing this section.
