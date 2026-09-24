# RIG Prompt Library

First-party, version-controlled library of production prompts for RIG. Drafts go in,
earn a measured score through [AutoPrompt](https://github.com/Eladlev/AutoPrompt)
calibration, and are versioned immutably. Any app, agent, or person pulls a prompt
by id — and every promote/pull is recorded in a hash-chained ledger.

This is the **first-party** layer. (The separate `rig-design-studio/prompt-library`
indexes *external* scaffolds — MotionSites, Magic UI, etc. — for web builds. Different job.)

## Routing (use the skill, do not reinvent it)

To pick the right prompt for a stated job, load
`capabilities/skills/prompt-router/SKILL.md` and run `node tools/route.mjs "<the job>"`.
That skill is the governed entry point: JEV decides the pick, the ranker supplies evidence,
and the pack names provenance and status. Do not author a new prompt for a job this library
already serves; route first, then draft only what is missing.

## Layout

```
registry.json            machine-readable index (id → path, version, score, model, status)
ledger.jsonl             hash-chained append log: every promote/pull (edits break the chain)
prompts/<id>/
  prompt.md              current champion (YAML frontmatter: version, score, provenance)
  versions/v<N>.md       immutable history
  eval/scores.json       AutoPrompt score history for the promoted run
  eval/dataset.csv       the edge-case dataset the score was measured on
tools/                   zero-dependency Node CLIs (see below)
```

## The loop (design → calibrate → promote → pull)

1. **Draft** — write a draft prompt as `prompts/<id>/prompt.md` with frontmatter
   `status: draft`, `score: null`, and register it in `registry.json`.
2. **Calibrate** — run AutoPrompt from a normal shell (NOT the Aside sandbox — its
   library-validation policy deletes unsigned wheel binaries):

   ```bash
   cd ~/Developer/AutoPrompt
   ./rig-run.sh \
     --basic_config_path config/config_default.yml \
     --prompt "$(cat ~/Developer/rig-capabilities/capabilities/prompts/prompts/<id>/prompt.md)" \
     --task_description "what good looks like" \
     --output_dump dump/<id>-v1 \
     --num_steps 10
   ```

   Keys come from keychain (`com.rig.env.*`) at run time; nothing is stored in the repo.
   Budget via `max_usage` in the config yaml.

3. **Promote** — file the winner:

   ```bash
   cd ~/Developer/AutoPrompt
   .venv/bin/python ~/Developer/rig-capabilities/capabilities/prompts/tools/from_dump.py dump/<id>-v1
   cd ~/Developer/rig-capabilities/capabilities/prompts
   node tools/promote.mjs --id <id> \
     --prompt-file <calibrated-prompt.txt> \
     --score <accuracy> --model gpt-4-1106-preview \
     --history-json ~/Developer/AutoPrompt/dump/<id>-v1/history.json \
     --task "<task>" --domain <domain>
   cp ~/Developer/AutoPrompt/dump/<id>-v1/dataset.csv prompts/<id>/eval/dataset.csv
   ```

4. **Pull** — use it anywhere:

   ```bash
   node tools/pull.mjs <id> --body        # print champion prompt text
   node tools/list.mjs                    # inventory with scores
   ```

5. **Regress on model change** — when migrating models or providers, rerun the
   calibration against the saved `eval/dataset.csv` and promote a new version.
   Scores are only comparable within the same dataset + judge.

## Rules

- No prompt ships to production uncalibrated (`status` must be `calibrated` with a score).
- A score is meaningless without its dataset and model; both are recorded.
- Versions are immutable; fixes mean v(N+1), never edits.
- The ledger is append-only and hash-chained (`prev` → `hash`); `git` is the second copy.
- Keys never enter this repo. Runtime injection only (`rig-run.sh` / `rig-env.sh` in AutoPrompt).

## Tools

| tool | job |
|---|---|
| `tools/promote.mjs` | version + register + ledger a calibrated prompt |
| `tools/pull.mjs` | print a prompt by id (ledger-logged) |
| `tools/list.mjs` | table of the registry |
| `tools/lib.mjs` | shared hash/ledger/registry helpers |
| `tools/route.mjs` | deterministic lexical ranker: job statement to ranked prompt ids; `--write-routing` regenerates the prompt-router skill's routing table |
| `tools/ingest.mjs` | file a DRAFT prompt with honest provenance (never marks anything calibrated) |
| `tools/mine_sessions.mjs` | read-only corpus miner over local session stores (Aside, Codex, Claude, prompt files); writes gitignored `dump/` |
| `tools/from_dump.py` | AutoPrompt `history.pkl` → JSON (run with AutoPrompt venv python) |

## GitHub

Local-first. When approved, `origin` gets added and pushed; until then this directory
is the source of truth and `git log` is local.
