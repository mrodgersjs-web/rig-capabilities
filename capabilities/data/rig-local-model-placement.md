# RIG local model placement — Splash + Switchyard + abliterated lane
Established 2026-09-20. Splash 1.0.1, switchyard-server 0.2.0, nemo-switchyard 0.3.0.

## Hard constraint that drives every choice
Splash only serves **Splash packages** (`incoai/*-Splash`); plain GGUF/MLX checkpoints are
rejected, and no abliterated Splash package exists. So the fleet runs two lanes:

| Lane | Engine | Models | Why |
| --- | --- | --- | --- |
| Fast/clean coding | Splash | `incoai/Qwen3.6-35B-A3B-Splash`, `incoai/Qwen3.8-27B-Splash` | 2× decode, 7× cached TTFT vs next engine |
| Uncensored | ollama | huihui/abliterated GGUF | the only lane that can load abliterated weights |

Splash floor: **Apple M3+, macOS 26.4+, 36 GB unified**. The 24 GB node is permanently
out of scope for Splash.

## Placement

### 128 GB — M5 Max, macOS 26.5.1 (this box) — heavy node
- Splash `incoai/Qwen3.6-35B-A3B-Splash` on `127.0.0.1:8000` — running, 883 ms TTFT
- `qwen3.6-35b-a3b-abliterated` (Q4_K_M, 21 GB) — MoE, 3B active — verified 92 tok/s
- `qwen3.8-27b-abliterated` (UD-DW-Q4_K_M, 16.6 GB) — dense, highest-fidelity uncensored
- ollama here is `tech.rig.livecoach-ollama` on **:11436** (0.32.9). Nothing listens on
  :11434 any more — the desktop app that held it is guard-forbidden and now quit.
- Optional later: `bartowski/Llama-3.3-70B-Instruct-abliterated` Q4_K_M (~42 GB). Only
  this node has the headroom.

### 36 GB — M4 Max, macOS 26.6 — LAN code node
Only ONE big model fits at a time (Splash 27B plans a 27.7 GB budget; ollama's
`qwen3-coder:30b` holds 21 GB with a 24h keep-alive and gets re-pinned by fleet traffic).
- ollama `qwen3-coder:30b` stays primary (wired into firstmate `scripts/model-routing.json`)
- `huihui_ai/Qwen3.8-abliterated:27b-q4_K_M` (17 GB) — verified; use `num_ctx` 8192
- `huihui_ai/gemma-4-abliterated:12b-q4_K` (7.6 GB) — verified; coexists with anything
- Server is the **desktop Ollama.app**, upgraded 0.32.5 → **0.34.2** this session (0.32.5
  answered `unknown renderer "qwen3.8"`). The brew formula there is a stale 0.23.1 client;
  `brew upgrade ollama` does not touch the server.
- Splash installed + verified (`SPLASH36 OK` through the tunnel); LaunchAgent parked at
  `~/Library/LaunchAgents/tech.rig.splash.plist.disabled`. To switch to the fast lane:
  `ollama stop qwen3-coder:30b && launchctl bootstrap gui/$(id -u) <plist>`

### 24 GB — M4 Pro, macOS 26.4 (labelled "28GB", actually 24) — small-model node
No Splash (below the 36 GB floor). All three installed and refusal-tested; none refused:
- `huihui_ai/gemma-4-abliterated:12b-q4_K` (7.6 GB) — primary
- `thomboe/dolphin3.0-llama3.1-8b-abliterated` (4.9 GB)
- `klassiqgrafikz/qwen3.5-uncensored` (2.7 GB) — always-hot
Server is Ollama.app 0.33.0 on :11434; CLI symlinked `~/bin/ollama` →
`/Applications/Ollama.app/Contents/Resources/ollama`. No python3 on this box.

### 48 GB — MacBook Pro — OFFLINE (tailscale last seen 23 h ago); nothing installed
When it returns it is the best Splash host after the 128:
```sh
brew install incoai/tap/splash
splash serve --model incoai/Qwen3.6-35B-A3B-Splash      # 20.9 GB, 210 tok/s
ollama pull huihui_ai/Qwen3.8-abliterated:27b-q4_K_M    # 17 GB uncensored
ollama pull huihui_ai/gemma-4-abliterated:12b-q4_K      # 7.6 GB small
```

## Switchyard
Config `~/.rig/switchyard/routes.toml`, proxy on `127.0.0.1:4100`, model id `rig-local`.
- efficient → 36 GB `qwen3-coder:30b` (ssh tunnel `8037 → rig-36gb:11434`)
- capable  → 128 GB Splash `Qwen3.6-35B-A3B` (`:8000`)
- routing decisions logged to `~/.rig/switchyard/routing.jsonl`
Python library (Path 2) in `~/.rig/switchyard/.venv` (`nemo-switchyard==0.3.0`).
Tunnels are per-session: `ssh -f -N -L 8037:127.0.0.1:11434 rig-36gb`

## Traps found the hard way
1. **ollama version gates renderers.** 0.32.5 answers `unknown renderer "qwen3.8"`. Need ≥0.33.
2. **Two ollama servers = dead downloads.** Ollama.app and RIG's LaunchAgents fight over a
   port; `com.rig.local-ollama-desktop-guard` boots the desktop one every 15 s and every
   in-flight pull dies with `unexpected EOF`. The desktop app must stay quit on the 128.
3. **`tech.rig.livecoach-ollama` (:11436) flaps** — ~27 restarts/hour, every ~2.2 min,
   5958 lifetime. Each instance exits **cleanly** (code 0, no signal, no jetsam kill)
   having served zero requests. Never pull or run anything long through it. Provision
   with `~/.rig/switchyard/pull-models.sh`: `hf download` + `ollama create`, no daemon
   in the download path, resumable, driven by launchd agent `tech.rig.model-pull`.
   Ruled out by measurement, do not re-test: the binary (same binary + same plist env +
   same port survives 100 s+ standalone), the env, a port conflict, a duplicate label in
   the user domain, a `launchctl kickstart` caller (zero `launchctl` processes during a
   90 s churn window), cron, hermes jobs, a second agent sharing the log path, and
   `ProcessType` — switching Interactive→Background left the rate unchanged at 27/hour
   across five hours, so it was reverted. Remaining suspects need dtrace/sudo.
4. ~~`~/.local/bin/cc` shadows the real compiler~~ — **FIXED 2026-09-20.** It was a
   symlink to `rig-cmd` (slash-command dispatcher) created 2026-06-15, sitting ahead of
   `/usr/bin` in PATH, so every Rust/maturin build died on "Unknown command: …symbols.o".
   The alias is now `rcmd`; `cc` is the C compiler again. No `CC=` override needed.
5. **Splash "native protocol reached EOF" is an OOM, not a crash.** Check `ollama ps` for a
   resident model before blaming Splash.
6. **ollama `Compute error` after an engine upgrade**: restart the server once; stale
   runner state, not a bad model.
7. Remote `nohup` needs `< /dev/null` **and** `disown`, or it dies with the ssh session.
   Long ssh commands to rig-36gb drop at ~100 s — run detached and poll.
8. Abliterated Qwen models are reasoning models: with a small `num_predict` the whole
   budget goes to `thinking` and `content` comes back empty. Use `"think": false` or
   `num_predict ≥ 600` when testing.
