# rig-capabilities

The canonical, git-versioned home for RIG capabilities — **skills, agents,
hooks, goal harnesses, loops, and commands** — served to every harness
(Claude Code, Codex, OMP, Hermes, Prime Agent) over one stdlib-only MCP
server, and managed from one CLI. Package version **5.1.0**.

Quick health: `./bin/rig-capabilities registry status --fetch`,
`refresh`, `observe`, `connectors`.

## Why

The estate had 1,700+ Claude skills, 1,400+ Codex skills, 2,200+ Hermes
skills, 56 goal harnesses, and 45 hook scripts living in unversioned
dotfile directories — no index, no ownership, no changelog, three roots
colliding by name. This repo adds a governance layer **without moving
anything**: external roots stay exactly where they are and are indexed
read-only.

- **One search surface.** `capabilities_search` covers the repo plus every
  installed harness root. Search before authoring or installing anything new.
- **One owner per name.** Canonical repo entries shadow same-named installs
  elsewhere. Canonicalizing an asset is how you take ownership of it.
- **Distribute, don't copy-paste.** `capability_install <id> --harness claude`
  copies the canonical asset into a harness root and records it in
  `.install.json` (target, sha, timestamp).
- **Everything versioned.** New hooks, upgraded goal harnesses, and vendored
  OSS skills land under `capabilities/` and get the git history the dotfile
  dirs never had.

## Layout

```
capabilities/
  skills/<id>/SKILL.md      agent-oriented skills (dir assets)
  agents/<id>.md|.toml|.json
  hooks/<id>.sh|.py|.ts     hook scripts (canonical source for settings.json wiring)
  harnesses/<id>.yaml       goal harnesses (hA-*/hB-*/hC-*/hD-*/mh-*)
  loops/<id>.md             goal loops
  commands/<id>.md
.index.json                 generated search index (gitignored; rebuild: reindex)
.install.json               install ledger (committed)
rig_capabilities/           package: catalog, live probe, outcome taxonomy, MCP server
__main__.py                 MCP entrypoint: python -m rig_capabilities (stdio JSON-RPC 2.0)
bin/rig-capabilities        CLI: stats|reindex|search|list|get|add|install|wire|live|tree|route|outcomes
wire/wire.py                multi-harness MCP wiring installer (managed markers)
tests/                      stdlib unittest suite
```

Outcome browse view: `tree/` (generated symlink farm, `./bin/rig-capabilities
tree`; see docs/OUTCOMES.md). Intent routing: `route` / `capabilities_route`.

## MCP tools

| tool | purpose |
|---|---|
| `capabilities_search` | ranked search over repo + all harness roots |
| `capabilities_get` | metadata + content for one id (canonical preferred) |
| `capabilities_list` | filter by kind/source |
| `capability_install` | canonical asset → harness root, ledgered, backup-on-overwrite |
| `capability_add` | canonicalize any file/dir into the repo |
| `capabilities_stats` | counts by kind/source + ledger |
| `capabilities_reindex` | force rescan |
| `capabilities_live_status` | runtime wiring: wired/dormant/absent/down/hijacked |
| `capabilities_outcomes` | outcome-lane × kind counts over the whole estate |
| `capabilities_route` | intent → ranked outcome lanes + top capabilities |
| `capabilities_context_pack` | **context fabric** — BM25 + ollama dense + lanes + graph expansion → token-budgeted, trust/freshness-filtered context pack with per-bundle provenance; persisted under `.context/` |
| `capabilities_graph` | capability-graph adjacency expansion from one id |
| `capabilities_concepts` | concept index: normalized term → capability ids |
| `capabilities_refresh` | v3 drift report; apply=true rebuilds a stale index |
| `capabilities_analytics` | v5 per-asset pack/rating analytics |
| `capabilities_public_catalog` | v5 assets whose `acl` contains `public` |
| `capabilities_connectors` | SQL/API connector status + last error |
| `capabilities_observe` | local traces + Langfuse reachability (honest false if unkeyed) |

CLI twins: `pack --requester`, `refresh`, `serve`, `connectors`, `observe`,
`publish`, `sign`, `verify`. See [docs/CONTEXT-FABRIC.md](docs/CONTEXT-FABRIC.md).

Wire into all harnesses: `./install.sh` (dry-run) then `./install.sh --apply`;
check with `./install.sh --verify`. Managed blocks sit between
`RIG CAPABILITIES MANAGED` markers — same discipline as jake-pai-mcp.

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

MCP transport vendored from `~/Developer/jake-pai-mcp` (same owner, MIT).
Wiring installer mirrors `jake-pai-mcp/wire/wire.py`. External-root and
install-root maps default to the live RIG layout in `rig_capabilities/catalog.py`.
