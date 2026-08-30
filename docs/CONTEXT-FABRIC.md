# Context Fabric — v2 through v5

One hub (`rig-capabilities`). Package version **5.0.0**.

## Version ladder

| Version | What it is | Evidence |
|---|---|---|
| **v2** | Catalog + MCP + 4-tier context fabric (metadata / BM25 / ollama dense / graph+concepts). Deterministic OKF trust/freshness. 5 harnesses wired. | `fabric.py`, 13 original tools, embeddings 4559/4559 |
| **v3** | Substrate that survives without a human: drift detection vs `.last_seen.json`, auto-refresh on pack, observation-decay (unseen not punished; observed decays after 90d to floor 0.85), ACL policy (`acl_policy.json`) enforced when a requester is named. | `refresh.py`, `policy.py`, `refresh` CLI |
| **v4** | Multi-agent on one machine: `federates: [{label, path}]` merges peer `.index.json` as `fed:<label>` (read-only, no network). Ratings `useful/wasted` move trust (±0.05 / −0.10, clamp ±0.30). Per-agent workspace log under `.context/agents/<id>/`. | `federation.py`, `rate` → `ratings_delta` |
| **v5** | Public surface: HMAC-SHA256 pack signatures (`.signing.key` or `RIG_CAPABILITIES_SIGNING_KEY`; no key → `signed: false`). Public catalog = assets with `acl` containing `public`. Per-asset analytics from packs + ratings. | `surface.py`, `publish` / `sign` / `verify` / `analytics` |

## Layer map (still the infographic)

| Infographic layer | Implementation |
|---|---|
| Open Knowledge Bundles | Git + local federation. **Not built: SQL/API connectors** — nothing external to federate over the network; `sha` is the handle. |
| Bundle contract | `okf.py` trust formula + v3 decay + v4 ratings delta. ACL is now enforced for named requesters. |
| Knowledge catalog | `.index.json`; auto-rebuilds when `refresh` sees drift. |
| Discovery | BM25 always-on; dense ollama; graph; concepts. Unchanged. |
| Context fabric | `capabilities_context_pack` + CLI `pack --requester`. |
| Runtime context graph | `.context/pack-*.json` now carries `requester`, `tiers.acl_enforced/decay/ratings_trust/signed`, optional `signature`. |
| Agent feedback | `rate` → ratings.jsonl → trust table; observations.jsonl drives decay. |

## Degradation contract

`pack` never fakes a tier. `tiers` names what ran. No signing key → `signed: false`. No ollama cache → `dense_ollama: false`. No peer index → federation skips that label.

## Deliberate remaining gaps

- SQL/API bundle connectors.
- Cross-machine network federation (v4 is local-path only).
- Org-wide IdP; ACL is a file of agent→scopes.
- Concept extraction is still IDF heuristics.
- Langfuse: separate infra decision.
