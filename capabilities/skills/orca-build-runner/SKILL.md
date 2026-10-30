---
name: orca-build-runner
description: "Launch and supervise multi-file builds as visible Orca terminal sessions (orca-buildout + the orca CLI). Use when a grokbot, Prime, or any agent needs to get a build, app, site, pipeline, or multi-file code task done: pick the harness, launch, check liveness, judge DONE. Never git push or merge."
---

# Orca build runner

Every build-out (app, site, code, pipeline, multi-file change) runs as a VISIBLE Orca session, not chat-side work. Never `git push` or merge: that is Mike's step.

## Tools
- Orca CLI: `/Applications/Orca.app/Contents/Resources/bin/orca` (`orca agent-context` prints the machine-readable command schema; `orca status`, `orca terminal list|show|read|send|close`, `orca repo add`, `orca worktree list`, `orca skills list|get`).
- Build launcher: `/Users/rig128gb/.rig/bin/orca-buildout` (registers the goal in `~/.rig/orca-goals/goals.json`; the orca-goals daemon nudges, relaunches and re-checks DONE).
- Bundled Orca skill guides: `orca-cli` (worktrees, terminals, handoffs), `orchestration` (supervised workers, task DAGs), `computer-use`, `orca-emulator`, `orca-emulator-android`, `orca-linear`, `orca-jira`, `orca-per-workspace-env`. Read one with `orca skills get <name>`.
- Note: PATH `orca` may be a different messaging tool; always call the full app path above. `orca-run` in ~/.local/bin is a scala orca-shell shim, not the Orca app.

## Launch
Run over ssh so `~` is the real home (never from inside a sandbox):
```
ssh -o BatchMode=yes localhost '/Users/rig128gb/.rig/bin/orca-buildout --id <short-id> --title "<title>" \
  --host local --harness <omp|prime|pi|claude|hermes|kimi> --worktree <selector> --workdir <repo dir> \
  --model <provider/model> --job-file <abs brief path> \
  --done-test "<shell cmd exiting 0 only when truly done>" --done-statement "<one sentence>" --owner <session id>'
```
- `--worktree` is required. A brand-new repo must be registered first: `orca repo add --path <abs>` then use `id:<repoId>::<abs path>`.
- `--done-statement` is required. Grok, Codex, Gemini, Droid, Aider, Qwen are NOT routable harnesses yet; a grokbot launches the build on a routable harness and supervises it.
- If the call looks failed, check `orca terminal list` / the goals registry before retrying (a truncated JSON can hide a terminal that already started).

## Liveness and DONE
- Liveness = the Orca terminal list, not the registry. `orca terminal show --terminal <h> --json`: strip everything before the first `{`; `result.terminal.lastOutputAt` is milliseconds; `preview` is ~300 chars.
- A terminal whose first line is `no such file or directory` is dead.
- DONE = done-test exits 0 AND Jev >= 0.9 on the evidence. Evidence: `~/rig-builds/<id>/DONE.txt`, first line `DONE PASS <summary>`, and the first 1,500 chars must restate the done_statement verbatim.
- Stop a goal: back up goals.json, remove the entry atomically, then `orca terminal close --terminal <h>`.

## Floors
No push, merge, publish, send, or spend. Never unpause an owner-paused routine. Never load-test the live Aside account.
