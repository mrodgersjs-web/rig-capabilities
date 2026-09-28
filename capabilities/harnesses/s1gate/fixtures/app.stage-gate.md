# Stage close: backend-data (Grokbot clone, mission grokbot-clone)

Stage: backend-data. Deliver schema, credits gate, quota gate and the routines tick endpoint.

| Claim | Executed check | Observed |
|---|---|---|
| Schema applied | `psql -h 127.0.0.1 -p 5433 -c '\dt'` via PGlite service | 6 tables: users, agents, runs, routines, credits, tool_calls |
| Credits gate decrements | POST /api/chat as seeded user, then GET /api/credits | credits 5 -> 4, sidebar screenshot shows 4 |
| Quota deny at limit+1 | create agent #4 on free plan | HTTP 402 {"error":"agent_limit"} |
| Routines tick runs due jobs | backdate next_run_at, POST /api/routines/tick | {"ran":1} (was {"ran":0} before the camelCase consumer fix) |

Blockers: none for this stage. Stripe checkout stays a named stub (skipped in the source video) and is listed as out of scope.
No deploy, push or purchase happened in this stage.
