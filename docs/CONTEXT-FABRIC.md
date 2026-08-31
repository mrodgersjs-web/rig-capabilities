# Context Fabric — v2 through v5.1

One hub (`rig-capabilities`). Package version **5.1.0**.

## Version ladder

| Version | What it is | Evidence |
|---|---|---|
| **v2** | Catalog + MCP + 4-tier context fabric (metadata / BM25 / ollama dense / graph+concepts) | `fabric.py` |
| **v3** | Drift vs `.last_seen.json`, auto-refresh, observation-decay, ACL policy | `refresh.py`, `policy.py` |
| **v4** | Local-path federation, ratings→trust, per-agent workspaces | `federation.py` |
| **v5.0** | HMAC-SHA256 pack signatures, public catalog, analytics | `surface.py` |
| **v5.1** | SQLite/HTTP/optional-Postgres connectors; `serve` HTTP surface + URL federates; traces.jsonl always, Langfuse when keyed | `connectors.py`, `serve.py`, `observe.py` |

## Layer map

| Infographic layer | Implementation |
|---|---|
| Open Knowledge Bundles | Git + `connectors[]` (sqlite/http/postgres) + `federates[]` (`path` or `url`). Provenance is `sha`. |
| Bundle contract | OKF trust + decay + ratings delta. Prefix bases: `sql:`/`api:` 0.55, `fed:` 0.5. ACL enforced for named requesters. |
| Knowledge catalog | `.index.json`; `refresh --apply` rebuilds on drift. |
| Discovery | BM25 always-on; dense ollama; graph; concepts (IDF). |
| Context fabric | `pack --requester` / `capabilities_context_pack`. |
| Runtime context graph | `.context/pack-*.json` + optional HMAC `signature`. |
| Agent feedback | `rate` → ratings.jsonl; observations.jsonl; traces.jsonl. |
| Cross-machine | `rig-capabilities serve --port 8765` exposes `/health /index.json /public-catalog.json`. Peers set `"url": "http://host:8765"`. |
| Observability | Local JSONL always. Langfuse POST `/api/public/ingestion` only when `LANGFUSE_HOST` + keys are set; otherwise `langfuse: false`. |

## Degradation contract

Nothing is faked. Missing sqlite file / HTTP timeout / unknown connector type → skip + `.context/connector-last-error.json`. URL federate down → skip + `federation-last-error.json`. No Langfuse keys → local traces only. No ollama → `dense_ollama: false`. No signing key → `signed: false`. Postgres type without `psycopg2` → skip, error recorded.

## Still not built

- Org-wide IdP (ACL is still `acl_policy.json` agent→scopes).
- LLM concept tagging (IDF heuristics remain).
- Authenticated `serve` (bind + your firewall; no tokens on the HTTP surface).
