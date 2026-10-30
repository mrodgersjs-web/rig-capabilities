---
name: "adopted-apps"
description: "Self-hosted apps adopted from GitHub into ~/Developer/adopted: what is installed, how to boot it, and which ones are walled behind a paid API key."
---

# adopted-apps — layer 1 (index only)

**Filed under:** `when-building-or-fixing-agents` (agent infra) and `when-producing-media` (media apps).
**Provenance:** every adopted repo carries `PROVENANCE.md` at its root (source, commit, license, adopt date, verdict, walls).
**Canonical store:** `rig-capabilities` ids `adopted-apps-index` (skill) and `anil-matcha-scout-2026-10-27` (data).

## Batch: Anil-matcha (muapi.ai) — adopted 2026-10-27

Scraped all 285 public repos of the author; 182 are own (non-fork). Outcome: 35 install-tier, 86 catalogs (knowledge, not installs), 43 stale/coursework, 18 license-flagged. Clones are shallow (`--depth 1`) under `~/Developer/adopted/anil-matcha/`.

### Runs here, no new account
- **open-agent-connector** — self-hosted Composio/Nango alternative. FastAPI + SQLite, MCP over `POST /mcp` (JSON-RPC 2.0) and `GET /mcp/tools`, plus a stdio transport. Boot: `cd ~/Developer/adopted/anil-matcha/open-agent-connector/server && ../.venv/bin/python -m uvicorn main:app --port 8010`. Cold start takes ~30 s the first time (macOS assesses the freshly downloaded native extensions). Load test 2026-10-27: boot OK, `/mcp/tools` returned 401 fail-closed with a JSON token error, which is the documented behavior.
- **open-agent-email** — agent inboxes with REST + MCP, SMTP, and a human-approval workflow. Same native-venv path as the connector; the shipped `docker-compose.yaml` also wants mailpit (1025/8025) and optionally clamav. Not booted yet; Docker is not installed on this Mac.

### Walled, kept as reference
32 of the 34 clones need a **MUAPI_API_KEY** (muapi.ai is pay-per-generation, e.g. Seedance mini ~$0.073/sec), or Docker, or Slack/app secrets. The three shipped `SKILL.md` files (`Seedance-2-API/skills/seedance-v2`, `Seedream-5-Pro-API/skills/seedream-5-pro`, `AI-Youtube-Shorts-Generator`) all declare `MUAPI_API_KEY` as a hard requirement, so they are staged, not installed. Do not open a muapi account to use them; the local lane already reaches the same models through Maestro/WanGP.

### Dupe check before adopting more from this author
`open-duet` was already cloned at `~/Developer/open-duet` (Apache-2.0). `rig-connector` predates `open-agent-connector` — compare before either becomes load-bearing. The `awesome-*` catalogs are a scout feed, not capability.

## Adding a repo to this estate
1. Shallow-clone into `~/Developer/adopted/<owner>/<repo>`.
2. Read the LICENSE file itself, not the GitHub badge: NOASSERTION means flagged, not free.
3. `uv venv --python 3.11 .venv && uv pip install -r <requirements>`; then `xattr -c -r .venv` and ad-hoc `codesign --force --sign -` the `.so` files, or macOS refuses to load them.
4. Load test = the app answers something real (endpoint, tool list, skill resolve). No evidence, no registration.
5. `PROVENANCE.md` at the repo root, then `rig-capabilities add <id> --kind skill|data --path <path>`.
