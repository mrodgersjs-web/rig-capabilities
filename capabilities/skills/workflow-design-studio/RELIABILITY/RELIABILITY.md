# RELIABILITY LAYER — the studio also fixes the surfaces it embeds into

Jordan Jr, 2026-10-26. Scope: Mike v2 mandate ("make this 1000x better than described": the studio
must fix its surfaces). Everything here is EVIDENCE + DRAFT PATCH ONLY. Nothing applied: the
single writer for `~/.rig/bin/prime-chat-mcp` and `~/.rig/runtimes/aside-watchdog/aside_watchdog.py`
applies after owner sign-off.

## Measured metrics (metrics/measure_reliability.py -> metrics/reliability.json)

| metric | measured value | source |
|---|---|---|
| stuck-relays (distinct job ids ever flagged) | **19** (18 real + 1 planted test `planted000001`) | watchdog-log.jsonl, 17 sweeps |
| stuck-relays red sweeps | **11 / 17** | watchdog-log.jsonl |
| stuck-relays current at last sweep | **0** | watchdog-log.jsonl (after supersede/backfill logic) |
| watchdog false-RED (jake-alive) | **5**, and **5/5 = 100%** of jake-alive reds were the /tmp probe ENOENT | watchdog-log.jsonl |
| relay round-trip seconds | n=56 polled: **median 41.5s, mean 82.4s, max 375s** (17 more replies backfilled, untimeable) | ledger.jsonl prime_say -> prime_reply by job |

## Defect 1 — relay pairing flaw (duplicate re-sends mint new job ids)

**Mechanism (read from code, not assumed):** `~/.rig/bin/prime-chat-mcp` `t_say()` mints
`jid = uuid.uuid4().hex[:12]` on EVERY call, including a duplicate re-send of identical text.
Pairing (`_reply`) is per-job by msg_id/snippet after `n0`, so a re-send of an answered text
leaves the FIRST job unpaired forever. The watchdog's supersede skip (newer answered same-text)
mitigates reporting but silently drops the pair, so the job can re-surface as stuck whenever the
newer twin is absent from the candidate window.

**Proposed fix (drafts in RELIABILITY/patches/):**
- `01-bridge-t-say-dedup.patch` — bridge-level: a same-text job within 30 min re-joins the family
  (no new job id, retry noted in meta, `prime_say_dup` ledger row). Genuinely later repeats mint fresh jobs.
- `02-watchdog-supersede-mark-dupof.patch` — watchdog-level: superseding now writes a
  `prime_reply_backfill` row with `source: superseded-by:<newer>` (mark dup-of) instead of `continue`.

**Apply rule:** single writer, owner sign-off first; run `prime-chat-mcp --self-test` and one
planted dup re-send after applying.

## Defect 2 — watchdog TMPDIR mismatch (false-RED on jake-alive)

**Mechanism:** launchd gives the watchdog no `$TMPDIR`; the old probe hit
`/tmp/prime-agent-rust-501/daemon.sock` (ENOENT) while the live daemon socket is
`/var/folders/.../T/prime-agent-rust-501/daemon.sock`. Measured: all 5 jake-alive reds are this
one signature. The 23:00 sweep onward is green.

**State now (verified on disk today):**
- `~/.rig/runtimes/aside-watchdog/aside_watchdog.py` `_daemon_socket()` is already TMPDIR-aware
  (globs `/var/folders/*/*/T/...` first, then `/tmp` fallback). Owner of the probe fix: session
  01a175d3's worker (the file itself is the owner record).
- Compat symlink bridge is IN PLACE: `/tmp/prime-agent-rust-501/daemon.sock -> /var/folders/5h/.../T/prime-agent-rust-501/daemon.sock` (created 2026-10-25 23:00).

**Permanent fix (proposed, needs an owner):** (a) export `PRIME_AGENT_DAEMON_SOCKET` from the
daemon-start/keeper path so every CLI consumer resolves the socket without the /tmp convention;
(b) until then the symlink is a NAMED contract (comment in both the daemon starter and
aside_watchdog.py) — never delete it silently; (c) grep audit found no other hardcoded
`/tmp/prime-agent-rust-501` probe in `~/.rig/bin` (checked prime-jake-keeper: none); the residual
consumer is the prime-agent CLI's own /tmp default for any caller launched without the env var.
Owner to find for (a): whoever owns the prime-agent daemon startup (com.rig.prime-jake-keeper /
prime-agent-rust). That is the one open OWNER question in this document.

## Defect 3 — reliability metrics wired into the studio's before/after table

Done: `metrics/measure_reliability.py` (re-runnable, read-only) feeds the table in
`metrics/BEFORE-AFTER.md` and SPEC.md. After-state targets for the two patches (proposed, NOT
claimed): stuck-relays 0 persistent (duplicates become `prime_say_dup`/superseded rows),
false-RED 0 on jake-alive (probe fixed + symlink contract), round-trip unchanged (measurement,
not a defect) — the studio reports these numbers on every drift-doctor run instead of nobody
measuring them.

## A1 note
All three fixes are code and config; no model sits in any decision path. The compiler and the
metrics scripts stay PYTHON_ONLY (cell L4-D3-A1-I1, BMS 0.89).
