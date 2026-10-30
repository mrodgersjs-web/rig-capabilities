---
name: "jev-ultrafast"
description: "Run an autonomous goal-driven browser agent (browser-use/jev-ultrafast) that picks each operation and target itself via TypeSafe Jev, for multi-step web tasks like 'search X, open the first result'. Use for end-to-end browser goals, the Jev ultrafast inspector, or when asked about jev / ultrafast / the TypeSafe browser agent. Not for reading one page or scripted scraping — use the native loop or browser-harness for those."
done_when:
  - grep:capabilities/skills/jev-ultrafast/SKILL.md:It never steals your tab
  - grep:capabilities/skills/jev-ultrafast/SKILL.md:Never quote a cold-start number
---

# jev-ultrafast

Autonomous browser agent: one URL + one natural-language goal, and it chooses each
action itself. `CLICK / TYPE_TEXT / SELECT / SCROLL / WAIT / DONE / BLOCKED` come
from one TypeSafe Jev request (operation head + target heads); a small LLM writes
text **only** for `TYPE_TEXT`. No screenshots in the loop, no site-specific scripts.

Install root: `/Users/rig128gb/Developer/jev-ultrafast` (vendor clone, pinned;
local additions are git-excluded so `git status` stays clean).

## Decide: this, the native loop, or browser-harness

| Situation | Use |
|---|---|
| One goal spanning several steps ("run the search and open the first result") | **this** |
| Read/inspect one page, or perform one known click | native `snapshot` loop |
| Scripted/deterministic automation, logged-in site work you must watch step by step | `browser-harness` skill |
| A page behind a login wall | native loop (this drives, this decides) |

## Commands

```bash
J=/Users/rig128gb/Developer/jev-ultrafast/bin/jev

$J run --url URL --goal 'A narrow, verifiable goal.'   # headless run
$J doctor                                              # harness/daemon state
$J                                                     # inspector UI (free port it picks)
$J pytest                                              # 31 offline gates
$J harness <<'PY' ... PY                               # raw browser-harness helpers
```

- Exit code is the contract. A run is only believable from its printed final
  `done` plus the final page URL, never from a traceback-free exit alone.
- `run` applies a **two-level helper ladder** declared in `.env` and enforces a
  retry. Any helper-shaped failure — `returned no valid field value`, or
  `Model connection failed` / `Model provider returned HTTP` / `Model
  unavailable` **from the `field_text` frame** — promotes
  `TEXT_MODEL_FALLBACK_BASE_URL`/`MODEL` for the next attempt and says
  `jev: helper route -> T1 fallback` on stderr. Retries stop at
  `JEV_RUN_RETRIES` (default 2), and `rc` is preserved across the pipeline
  (`tee` plus the `set -o pipefail` dance above, proven: killed-child test gave
  143). Any other non-zero exit propagates immediately, un-retried and
  un-promoted; `JEV_RUN_RETRIES=0` disables repeats but not a first promotion.
  Each attempt opens its own tab. **The environment wins over `.env`**, so
  `TEXT_MODEL_BASE_URL=https://openrouter.ai/api/v1 \
  TEXT_MODEL=inception/mercury-2.5 $J run ...` picks the paid helper for one
  run with no config edit (this did not work before 2026-09-26: `.env` was
  sourced over the caller's env). `JEV_HELPER_LADDER=off` disables promotion
  entirely and keeps a doomed run on T0. The `in field_text` condition is load-bearing:
  without it a Typesafe outage (same `post_json`) would be misread as a helper
  miss and point the retry at the wrong fix.
- The launcher **fails loud** (`BLOCKED:` + exit 3) if the TypeSafe key cannot be
  resolved. It never prints, writes, or passes a key on argv.
- `TYPESAFE_DEMO_PORT` defaults to a verified-free port: the vendor's 8766 is the
  local OpenAI-style gateway on this machine, and 8767 is occupied.

## Keys

Both come from the macOS keychain at launch (env var wins, then keychain):

- `TYPESAFE_API_KEY` ← `com.rig.env.TYPESAFE_API_KEY` (the decision layer:
  `jev_ultrafast/model.py` POSTs `https://api.typesafe.ai/v1/systemone` with it,
  model `TYPESAFE_MODEL=jev-latest`). This is the one key the engine needs.
- `TEXT_MODEL_API_KEY` ← `com.rig.env.OPENROUTER_API_KEY`, used only if you
  switch the helper to the T1 fallback below.

Non-secret config lives in `<repo>/.env`. Two lanes, local-first as set by Mike:

- **T0 active:** `TEXT_MODEL_BASE_URL=http://127.0.0.1:8655/v1`,
  `TEXT_MODEL=mimo-v2.6-flash` (loopback tunnel, his own box, $0).
- **T1 declared in the same file**, not commented out:
  `TEXT_MODEL_FALLBACK_BASE_URL=https://openrouter.ai/api/v1` +
  `TEXT_MODEL_FALLBACK_MODEL=inception/mercury-2.5`. The launcher promotes it
  automatically when T0 fails, so a tunnel that died on reboot costs one
  failed attempt rather than a stuck run. It is *not* probed up front, so if a
  run must never touch paid traffic, drop the two `FALLBACK_` lines. Model ids
  and IP↔lane bindings drift on this box: re-probe rather than trusting
  `.env` after a reboot (`~/.rig/bin/rig-model-probe.py --rank`).

## How it plugs into Aside's browser model

It attaches to the **same browser-harness CDP daemon** Aside already drives, so
it is an engine beside the native loop, not a second browser stack.

- **Zero-config is the default.** With no `BU_CDP_URL` exported at all,
  `env -u BU_CDP_URL $J run ...` attached to the daemon (doctor reported
  "active browser connections — 1") and finished `done` in 2749 ms.
  Proven 2026-09-26.
- **It never steals your tab.** `browser.py` opens its own
  `Target.createTarget(..., background=True)` and enables focus emulation so
  rendering keeps going in that owned tab *without activating the user's Chrome
  tab* (their comment, line 26), and `close()` closes only that target. The
  harness skill's "never clobber their work" rule holds for this engine too.
- **Paths, not `command -v`.** In an Aside bash call, `jev`,
  `~/.local/bin/jev` and `browser-harness` all report ABSENT while the binaries
  work at explicit paths. Always use the `J=` form below.

- **Chrome already running (preferred):** Way 1, one-time tick of "Allow remote
  debugging for this browser instance" at `chrome://inspect/#remote-debugging`,
  then click Allow on Chrome's popup. Keeps real profile/logins; no `BU_CDP_URL`.
- **Chrome not running:** Way 2, isolated profile, then export
  `BU_CDP_URL=http://127.0.0.1:<port>` for every `$J` call.

### Sandboxed runners (verified here on 2026-09-26)

GUI Chrome will not start: `sandbox initialization failed: Operation not
permitted`, then the GPU process dies. The working recipe is Playwright's
headless shell **plus `--no-sandbox`** — without `--no-sandbox`, `Target.*`
still answers while every renderer-side command hangs, which surfaces as
`_IPCResponseTimeout: Emulation.setDeviceMetricsOverride timed out` rather than
as a sandbox error:

```bash
HS="$HOME/Library/Caches/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-mac-arm64/chrome-headless-shell"
UD=/Users/rig128gb/Developer/jev-ultrafast/.chrome6
nohup "$HS" --remote-debugging-port=9270 --user-data-dir="$UD" --no-sandbox \
  --disable-gpu --in-process-gpu --disable-gpu-compositing --no-first-run about:blank &
export BU_CDP_URL=http://127.0.0.1:9270
```

In that sandbox `ps`/`pgrep` are `Operation not permitted`, so `jev doctor`'s
"chrome running" line cannot be judged — probe
`curl -s http://127.0.0.1:<port>/json/version` instead. If a run hangs on the
first session-scoped command, restart the daemon and drop stale state:

```bash
RD="$HOME/.config/browser-harness/runtime"
kill "$(cat $RD/bu-default.pid)" 2>/dev/null
rm -f "$RD/bu-default.pid" "$RD/bu-default.sock" "$RD/bu-default.spawnlock"
```

## Gates (proven 2026-09-26, commit 1231850)

- Offline: `pytest` 31 passed, `ruff check` clean, `node --check` clean on
  `snapshot.js` and `static/app.js`, `sh -n bin/jev` clean.
- Live with keychain keys: goal run finished `done` with final URL
  `…/wiki/Gödel%27s_incompleteness_theorems`; typing goal finished `done` in
  1.6 s, typed `godel` and landed on `…/wiki/Kurt_G%C3%B6del`.
- Inspector returned 200 on the port it picked (it carries a `demo-token` meta).
- Retry proved both ways: a planted code-fence response gave exactly 2 retry
  lines then exit 1 with `.env` restored byte-identical (same sha), and an
  unrelated usage error gave 0 retries and exit 3.
- Helper ladder proved all four ways on 2026-09-26 (`.env` restored
  byte-identical each time): healthy local T0 ran rc 0 with no promote and no
  retry; the local tunnel pointed at a dead port produced
  `jev: helper route -> T1 fallback (… / inception/mercury-2.5)` and finished
  `done` with the correct final URL; both routes dead under
  `JEV_RUN_RETRIES=1` exited rc 1 in 2383 ms; a usage error exited rc 3 with
  0 promotes and 0 retries. First version of the guard was caught red by that
  same plant — it grepped for `httpx` wording while vendor `post_json` reports
  `Model connection failed`.
- Integration proof: `env -u BU_CDP_URL $J run` with zero manual CDP wiring
  finished `done` in 2749 ms against the shared daemon, using its own
  background tab rather than activating yours.
- Helper route, **interleaved** on one goal (Wikipedia -> type "Kurt Godel" ->
  open it), 4 rounds, .env untouched:
  T0 local **5157 ms mean wall, 4/4 done** vs the same run with an inline T1
  override **3267 ms, 4/4 done**, so local-first costs **+1.9 s per run**, not
  the 7 s an earlier non-interleaved block implied. Native loop on the same
  goal, same window: **~2.0-2.5 s** tool floor, 2 reps here and 3 before.
  Per-step probe cost for the helper was ~3.0 s local vs ~0.6 s paid, which is
  a bigger gap than wall-clock shows because observe/decide/page-load dominate.
  **Absolute numbers drift hard:** the same config measured 9.7-14.4 s in an
  earlier block, so quote a same-block A/B, never a number from another hour.
- Speed split of a typical 2-action run: launcher python boot about 24 ms vs
  about 137 ms through `uv run`; first observation (page load) 280-1470 ms is
  the dominant term; helper text call median 607 ms with `.env`'s
  `TEXT_MODEL_REASONING=none` vs 1012 ms on the vendor default; each agent
  decision 110-420 ms. Interleaved A/B in the same minute with the same goal:
  `JEV_RUN_RETRIES=0` 6/7 succeeded at mean 2351 ms, retry-on 7/7 at mean
  3082 ms with zero retries firing, so the gap is page-load noise.

## Limits and honesty rules

- The MVP does not handle iframes, shadow roots, canvas, uploads, pop-up tabs or
  nested scrolling; a goal needing those reports `BLOCKED` instead of improvising.
- `DONE` requires independent outcome verification — re-read the final page URL or
  content before claiming success.
- The text helper's `ValueError: Text helper returned no valid field value;
  nothing typed.` is provider-side, not config, and has exactly two captured
  causes: (1) the model returns code-fenced JSON (a fenced `{"text": "..."}`)
  into vendor's strict `json.loads`; (2) OpenRouter upstream
  `504 Upstream idle timeout exceeded`, measured at 120,083 ms before it gives
  up. Vendor ships no retry, which is why `run` carries one. It clusters under
  rapid-fire consecutive runs: 4 models x 10 isolated calls were 40/40 valid,
  while a burst of agent runs failed about a third of the time. Both captured
  causes are T1/OpenRouter-side: on the local T0 route that same burst ran 6/6
  clean. Keep the retry anyway — it costs nothing while the helper is healthy,
  and it is the only protection the T1 fallback has.
- Cold browser bring-up is unmeasured here: `kill` on the CDP port's pids never
  took the browser down (lsof lists 4 pids, still answering 2 s later), so any
  cold-start figure from this sandbox is invalid.

## Accepted state (Mike, 2026-09-26)

He approved all three items that were left open, as they stand. Do not reopen
them as blockers, and do not change them unasked:

1. The helper ladder **may promote to the paid T1 route** on a helper failure,
   i.e. a dead local tunnel can cost one OpenRouter retry instead of probing
   up front. Not a defect. A lane that must never spend drops the two
   `FALLBACK_` lines.
2. Cold browser bring-up **stays unmeasured**. Never quote a cold-start number
   for this sandbox; the earlier attempt was invalid, not merely imprecise.
3. Integration **stops at the shared browser-harness daemon**. Putting jev on
   Aside's own live Playwright tab would mean exposing that browser on a CDP
   port, which is an Aside runtime change and is a separate decision.