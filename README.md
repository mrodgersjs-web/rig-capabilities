# rig-capabilities

[![ci](https://github.com/mrodgersjs-web/rig-capabilities/actions/workflows/ci.yml/badge.svg)](https://github.com/mrodgersjs-web/rig-capabilities/actions/workflows/ci.yml)

The canonical, git-versioned home for RIG capabilities: **skills, hooks, goal
harnesses, loops, commands, and agent packs**. One stdlib-only MCP server
(stdio JSON-RPC 2.0) serves the catalog to any MCP harness, and one CLI
manages it. A wiring installer registers the server with Claude Code, Codex,
OMP, Hermes and Prime Agent. Package version **42.0.0** (`rig_capabilities.__version__`).

## Install and run

Runtime is Python 3.9+ standard library only. PyYAML is optional: with it,
`loop.yaml` files are read directly; without it, the committed `loop.json`
twins are used (`rig-loop compile <id>` regenerates them).

```sh
pip install -e ".[test]"          # add ,yaml to read loop.yaml directly
python -m rig_capabilities        # MCP server on stdio (or: python server.py)
./bin/rig-capabilities search "proof loop"
./bin/rig-capabilities get proof-loop
./bin/rig-loop test proof-loop    # run a loop-skill's planted-failure cases
python scripts/smoke_mcp.py       # end-to-end: start the server, query the catalog
```

Install editable (`-e`) or set `RIG_CAP_REPO=/path/to/checkout`: the server
reads `capabilities/`, `config.json` and `.index.json` from the checkout, not
from site-packages.

## Tests and CI

```sh
pytest -m "not live_estate"       # what CI runs
python -m unittest discover -s tests   # stdlib runner, includes live-estate tests
ruff check .
```

`.github/workflows/ci.yml` runs on every push and pull request, on Python 3.9
and 3.12, with and without PyYAML: install, `ruff check`, the test suite, then
two smoke steps (the MCP server answering `capabilities_search` and
`capabilities_get` over stdio, and the CLI plus `rig-loop test proof-loop`).
CI sets a throwaway `RIG_CAPABILITIES_SIGNING_KEY` per run so the token and
pack-signing gates are exercised for real.

Tests marked `live_estate` need the operator's machine (an external corpus
root from `config.json`, a local Postgres on port 5433) and are deselected in
CI. They still run under `unittest` on a host that has those.

## Why

Skills, hooks and goal harnesses tend to pile up in unversioned dotfile
directories (`~/.claude`, `~/.codex`, `~/.hermes`, ...) with no index, no
ownership and no changelog. This repo adds a governance layer **without moving
anything**: external roots stay where they are and are indexed read-only
(roots are listed in `config.json`; missing roots are skipped).

- **One search surface.** `capabilities_search` covers the repo plus every
  configured harness root. Search before authoring or installing anything new.
- **One owner per name.** Canonical repo entries shadow same-named installs
  elsewhere. Canonicalizing an asset is how you take ownership of it.
- **Distribute, don't copy-paste.** `capability_install <id> --harness claude`
  copies the canonical asset into a harness root and records it in
  `.install.json` (target, sha, timestamp).
- **Everything versioned.** New hooks, upgraded goal harnesses, and vendored
  OSS skills land under `capabilities/` and get git history.

## Layout

```
capabilities/
  skills/<id>/SKILL.md      agent-oriented skills (dir assets); loop-skills add
                            loop.yaml + loop.json + tests/cases.json
  hooks/<id>.sh|.py|.ts     hook scripts (canonical source for settings.json wiring)
  harnesses/<id>.yaml       goal harnesses (hA-*/hB-*/hC-*/hD-*/mh-*)
  loops/<id>.md             goal loops
  commands/<id>.md
agents/<id>/pack.json       agent packs: the skills/harnesses each agent runs on
.index.json                 generated search index (gitignored; rebuild: reindex)
.install.json               install ledger (committed)
rig_capabilities/           package: catalog, live probe, outcome taxonomy, MCP server
__main__.py                 MCP entrypoint: python -m rig_capabilities (stdio JSON-RPC 2.0)
bin/rig-capabilities        CLI (run with --help for every subcommand)
bin/rig-loop                loop-skill engine CLI
wire/wire.py                multi-harness MCP wiring installer (managed markers)
scripts/smoke_mcp.py        end-to-end stdio smoke test (used by CI)
tests/                      unittest suite (also runs under pytest)
```

Outcome browse view: `tree/` (generated symlink farm, `./bin/rig-capabilities
tree`; see docs/OUTCOMES.md). Intent routing: `route` / `capabilities_route`.

## MCP tools

29 tools (`tools/list`). Source of truth: `TOOLS` in `rig_capabilities/server.py`.

| tool | purpose |
|---|---|
| `capabilities_search` | ranked search over repo + configured harness roots |
| `capabilities_get` | metadata + content for one id (canonical preferred) |
| `capabilities_list` | filter by kind/source |
| `capability_install` | canonical asset → harness root, ledgered, backup-on-overwrite |
| `capability_add` | canonicalize any file/dir into the repo |
| `capabilities_stats` | counts by kind/source, index freshness, install ledger |
| `capabilities_reindex` | force rescan |
| `capabilities_live_status` | runtime wiring: wired/dormant/absent/down/hijacked |
| `capabilities_outcomes` | outcome-lane × kind counts |
| `capabilities_route` | intent → ranked outcome lanes + top capabilities |
| `capabilities_context_pack` | BM25 + optional dense (local ollama) + lanes + graph expansion → token-budgeted context pack with provenance, persisted under `.context/` |
| `capabilities_graph` | capability-graph adjacency expansion from one id |
| `capabilities_concepts` | concept index: normalized term → capability ids |
| `capabilities_refresh` | drift report; `apply=true` rebuilds a stale index |
| `capabilities_analytics` | per-asset pack/rating analytics |
| `capabilities_public_catalog` | assets whose `acl` contains `public` |
| `capabilities_connectors` | SQL/API connector status + last error |
| `capabilities_observe` | local traces + Langfuse reachability (reports false when unconfigured) |
| `capabilities_db_sync` | upsert the index into Postgres (`RIG_CAP_DSN`) |
| `capabilities_test` | run an asset's executable `done_when` checks |
| `capabilities_round` | improvement round in a lane: deterministic contract upgrades for the weakest assets (dry by default) |
| `capabilities_issue_token` | issue an HMAC requester token |
| `capabilities_certify` | deterministic certification gates (suite, index_fresh, done_tests, idp_integrity, acl_jake) |
| `capabilities_agent_pack` | resolve an agent pack (optionally with boot state) |
| `capabilities_gaps` | rank coverage gaps; optionally write draft harnesses |
| `capabilities_overlay_status` | LLM overlay coverage |
| `capabilities_proofchain` | verify ROADMAP packet prefixes against local proof hashes |
| `capabilities_release` | build the public-catalog zip locally |
| `capabilities_quality_report` | quality-contract coverage per canonical asset |

Most tools have a CLI twin in `bin/rig-capabilities` (`pack`, `refresh`,
`serve`, `connectors`, `observe`, `publish`, `sign`, `verify`, ...). See [docs/CONTEXT-FABRIC.md](docs/CONTEXT-FABRIC.md).

Wire into all harnesses: `./install.sh` (dry-run) then `./install.sh --apply`;
check with `./install.sh --verify`. Managed blocks sit between
`RIG CAPABILITIES MANAGED` markers.

## Loop-skills (v11) — doctrine as code-gated loops

Every RIG doctrine ships as a **loop-skill**: `capabilities/skills/<id>/{SKILL.md, loop.yaml,
tests/cases.json}`. The `rig-loop` engine (`bin/rig-loop`, stdlib) decides stage gates from
files and exit codes, refuses out-of-order advance, runs the Builder→Verifier closing loop,
enforces a kill switch, denies outward actions until a typed `APPROVE <run_id>`, and seals a
ProofPacket. Hooks fire on every prompt / tool call / stop in Claude, Codex, OMP and Prime
(`rig-loop wire --apply`); in Hermes the CLI gate is the mechanism. Contract:
[docs/LOOP-SKILLS-V11.md](docs/LOOP-SKILLS-V11.md).

| loop-skill | spine |
|---|---|
| `iqrsqpi-v20` (`/iqrsqpi`) | I1 Q1⇄R(dry) S B(slices) Q2(other-family verdict) P(calibration) I2(handoff) |
| `iqrsqpi-v20-slice` | B V C — child loop per context-sized slice |
| `iqrsqpi-v11` (reference) | I1 Q1 R S Q2 P I2 |
| `gate-d-loop` | C D R A X P |
| `proof-loop` | C E N V P |
| `adversarial-verification-loop` | G R N K P |
| `north-star-lock-loop` | L D S C P |
| `phase-discipline-loop` | O B V T C P |
| `git-push-safety-loop` | V D L A X S P |

```
rig-loop activate iqrsqpi-v11 --intent "..."   # start; hooks now enforce stages
rig-loop stage I1 pass                          # refused while the gate is red
rig-loop test iqrsqpi-v11                       # planted-failure cases (non-vacuity)
rig-loop doctor                                 # wiring + install state across 5 harnesses
```

## Doctrine

1. **Search before you build or install.** The corpus is huge; most ideas
   already exist somewhere. Canonical hits first, then external hits.
2. **Canonicalize before distributing.** Anything worth installing into a
   second harness belongs in `capabilities/` first.
3. **License boundary.** MIT/Apache upstreams may be forked into RIG-branded
   assets; CC-BY-SA (e.g. Trail of Bits) is consumed in place as marketplace
   plugins, never rebranded. Record provenance in the asset's frontmatter.
4. **No fake memory.** A capability that is a stub or mock is either wired
   real or deleted; naming lies about capability.
5. **Destructive changes are one commit, after the replacement verifies**
   (e.g. delete vendored superpowers copies only after the plugin's skills
   are confirmed loading).

## Provenance

MCP stdio transport and the wiring installer are adapted from `jake-pai-mcp`
(same owner, MIT). External-root and install-root maps default to the RIG
layout in `rig_capabilities/catalog.py` and `config.json`.

## Roadmap

The version ladder and its evidence live in [docs/ROADMAP.md](docs/ROADMAP.md).
Not yet done:

- CI coverage for the `live_estate` tests: needs a bundled fixture corpus and a
  Postgres service container instead of the operator's machine.
- Dense retrieval and Langfuse export are only exercised where a local ollama
  or Langfuse is configured; CI covers the BM25/lane/graph path and the
  "unconfigured" path.
- Hook wiring into real harness config files is tested against temp copies;
  live wiring is checked on the operator host with `rig-loop doctor` and
  `./install.sh --verify`.
- Running from a non-editable wheel without `RIG_CAP_REPO` (the catalog is
  read from the checkout, so a wheel install needs that variable today).
