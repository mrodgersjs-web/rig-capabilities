# UltraPlan V2 W00 Baseline

Captured from commands run on 2026-09-20. This is an evidence snapshot, not a readiness claim.

## Git baseline

| Repository | Branch / HEAD | Last commit | Porcelain-v1 paths | Evidence |
|---|---|---|---:|---|
| `~/Developer/ultraplan` | `main` / `8d3007bdf02176f2e5c825ef9e9fe1671f098f2d` | `2026-09-18T14:38:18-06:00` | 219 | `ultraplan-status.txt` |
| `~/Developer/ultra-mcp` | `main` / no HEAD | ZERO commits; `git log` reports unborn branch | 7 staged | `ultra-mcp-status.txt` |
| `~/Developer/rig-capabilities` | `fable-2031` / `b01ec3478ba9c628578d2d1646c2d43591003531` | `2026-09-19T09:43:38-06:00` | 286 | `rig-capabilities-status.txt` |

The three full `git status --porcelain=v1` outputs are stored verbatim. `rig-capabilities-status.txt` is the pre-W00 snapshot, captured before this directory contained files. Structured metadata is in `baseline-git.json`; raw command output is in `git-metadata.txt`.

## Console and persisted drawing state

- `127.0.0.1:8902` is PID 7249, command `/Users/rig128gb/.aside/runtime/python/venv/bin/python -m http.server 8902 --bind 127.0.0.1`, cwd `~/Developer/ultraplan`. It is a plain static server, not a durable console runtime.
- `127.0.0.1:61398` is node PID 9871, cwd `~/Developer/ultraplan/ui`.
- `127.0.0.1:61399` is node PID 67242, cwd `~/Developer/ultraplan`.
- `127.0.0.1:61400` is node PID 12766, cwd `~/Developer/ultraplan`.
- The active four-page seed (`canvas-seed.js` + `gates-seed.js` + `cells-seed.js`) emits **292 unique shape IDs**: Canvas 149, Architecture 56, JevBuild 31, Cells 56. The full list is `shape-ids.txt`. `TLRAW.html` is an older standalone seed and is hashed but not double-counted.
- Source hashes for `canvas-seed.js`, `cells-seed.js`, `gates-seed.js`, `TLRAW.html`, and `STATUS.json` are recorded in `console-state.json` and `console-observations.txt`.

## JEV, models, Fusion, Earendil

UltraPlan reaches JEV through the existing `rig-capabilities` gate path; it does not own a second provider client:

```text
rig-ultra route <gate-id> --state-file <artifact> --facts <facts.json> --live [--model <model>] --json
```

- Default endpoint: `https://api.typesafe.ai/v1/systemone`.
- Default model: `jev-latest`.
- `S1GATE_JEV_ENDPOINT` and `S1GATE_JEV_MODEL` were unset, so the code defaults apply.
- Without `--live`, `rig-ultra` returns `offline_code_only` with exit 2. No live JEV provider call was made for this inventory.
- Current UltraPlan JEV packs are advisory: `STATUS.json` records zero labelled decisions.
- Codex config selects `gpt-6-astra` through `openai-rig`; Claude settings select the loopback gateway `127.0.0.1:8768` with Fable 5 defaults and Opus 5 for Opus.
- `ollama list` returned one local model: `nomic-embed-text:latest` (`0a109f422b47`, 274 MB).
- Fusion is installed as a Codex skill and three command surfaces. Its managed `codex-fusion` MCP entry exists but is disabled. The governed launcher is `~/.rig/bin/fusion-harness`.
- No Earendil mention or installed surface was found under `~/.codex/config.toml`, `~/.codex/commands`, or `~/.codex/skills`.

See `model-port-inventory.json` and `model-observations.txt` for exact source lines and hashes.

## TAC source inventory

`tac-source-manifest.yaml` contains exactly 14 lesson entries, numbered 1–14. Each entry records title, course/caption timestamps, cue and token counts, pinned source repository, verified HEAD, loot count/summary, transcript hash, disposition, and status. A Ruby YAML parse verified `lessons=14`, `loot=259`, `missing=0`.

No per-lesson `reuse`, `adapt`, `reference_only`, or `unnecessary` decision exists in `EXTRACT-BRIEF.md` or `BUILD-OUT-TODO.md`. Every lesson therefore starts as `disposition: pending_license_review` and `status: pending`, preserving the private member-content boundary.

### Contract claim: “four missing member repositories”

The requested source folder has no `README`; its `CLONE-INVENTORY.md` and `repository-inventory.json` enumerate 14 repositories and declare 14/14. The contract does not name four repositories, and no requested source enumerates four missing names. Fresh verification found:

- 14/14 local clone paths present under `~/Developer/external`.
- 14/14 HEADs exactly match `repository-inventory.json`.
- 14/14 remotes match after credential-bearing URL userinfo is redacted. No credential is persisted in W00 evidence.
- 0/14 repository names appear in either canonical registry root.

| Lesson repositories checked | Registry verdict |
|---|---|
| `tac-1`, `tac-2`, `tac-3`, `tac-4`, `tac-5`, `tac-6`, `tac-7`, `tac-8` | each `not-in-registry` |
| `elite-context-engineering`, `agentic-prompt-engineering`, `building-specialized-agents` | each `not-in-registry` |
| `multi-agent-orchestration`, `agent-experts`, `orchestrator-agent-with-adws` | each `not-in-registry` |

**Verified verdict:** the contract’s count of four missing member repositories is unsubstantiated by the current source packet and contradicted by the 14/14 clone check. There are no four names to report without fabrication. The actual registry gap is that all 14 verified lesson repositories are absent from both registry roots. Full redacted proof is in `tac-repo-verification.json`.

## Caption coverage

The requested complete-caption/incomplete-frame-review sentence does not appear in `agentic-coding-school-buildout/MANIFEST.md` or `EXTRACT-BRIEF.md`; inventing that attribution would be false. The closest ACS manifest lines are recorded verbatim in `tac-observations.txt`, including:

> | Full verbatim transcripts captured | **403 / 503 unique videos** (~632K words, timestamped segments) |

The UltraPlan contract’s exact line is:

> Full caption coverage is complete; full frame-by-frame course review remains a tracked source-audit item.

For the separate TAC course package, `SOURCE-COVERAGE.md` records 14/14 lesson videos and 36,330 normalized timestamped cues, with raw tracks retained. Thus the TAC caption set is complete while full frame-by-frame review remains incomplete; the broader ACS corpus separately reports 403/503 unique-video transcripts.

## Writable-root resolution

Source writes remain blocked:

- `ultraplan`: DIRTY (219 paths) and not registered for this build wave.
- `ultra-mcp`: unborn repository with ZERO commits and 7 staged paths; not registered for repair work.
- `rig-capabilities`: DIRTY at the pre-W00 baseline (286 paths). Only this new `plans/ultraplan-v2/w00/` evidence boundary was assigned to this worker; no other path is leased.

Before any source edit, Firstmate must register the exact writable checkout, acquire the single-writer lease for the file boundary, and receive captain approval for that wave. No source file in `ultraplan`, `ultra-mcp`, or elsewhere in `rig-capabilities` was modified. This W00 run wrote only new evidence files under `plans/ultraplan-v2/w00/`.

## Evidence hashes

Every stored command-output/evidence file is content-addressed below.

| File | SHA-256 |
|---|---|
| `baseline-git.json` | `d6aa4331c7b5887604612bae49e3605f76088b2f651e14022ec42170b1d6d9c2` |
| `console-state.json` | `7601e3ac479e69bfc4ca44e747d62f0943a3e72ca0e31675cebf95d07102e547` |
| `model-port-inventory.json` | `7edba7c9c6b9f051dd919e12b061f58a5c64fc7fdd73901d6c0d1d483e25b3e9` |
| `tac-source-manifest.yaml` | `3878b1ef039cfd3afb132b3ee732353e4e22ba4a76cea18c94d9f4589348592f` |
| `git-metadata.txt` | `8b8515c2d352cb291988d87063c607b61ab98487320ccea157e982a33d023811` |
| `console-observations.txt` | `22499d5a21ef097749bbe239556b274d2d989151d27adc09a83e4350caca5fef` |
| `model-observations.txt` | `39936c6569a89ddc9293c58a591fc2bc49ad224df5f91790318cca9b8cd70bc5` |
| `tac-observations.txt` | `2a242a8b8aa3f96292bcdc3dbdb4fdcf09d8bda854dbb9f7ea3698482be9dcba` |
| `tac-repo-verification.json` | `3431a1055b41d3e5bdf87055cc7a494c81b397ff9342e0a90073967b2b6c6c9b` |
| `shape-ids.txt` | `5ce2bf01c466e0bd9a69f61ec5b2db249813f9708d8717a866c17c7d45f5b62f` |
| `ultraplan-status.txt` | `dceff1e732ae369e63f04ad92130296656cf3061739e88293fad9de9b29c8bda` |
| `ultra-mcp-status.txt` | `dca0ae4bb06c0a3a54f39f21902601ea8a820ecbc8faa0c7b9ad379861ab49f9` |
| `rig-capabilities-status.txt` | `d891a4ab99e62e4a1cad2721c3178b5db903b221f4141c2bdda3cd927f8ae9d7` |
