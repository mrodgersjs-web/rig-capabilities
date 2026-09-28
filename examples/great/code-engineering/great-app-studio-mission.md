# Great example: an App Studio mission record (Grok Bot clone, 2026-09-25/26)

Assembled from the real Grok Bot clone mission (`~/Desktop/Projects/grokbot-clone`,
source video oqUyyB7ROHA). Sources: memory/episodic/2026-09-25.md#L2366 and
memory/episodic/2026-09-26.md#L3, #L122, #L124, #L128. What makes it great is the shape:
every claim carries its proof, the gaps are named, and the public step is held.

## Spec (stage 1, gate app.spec + plan.readiness)

| # | Feature | Source | Acceptance check |
|---|---|---|---|
| 1 | Structured agent response | oqUyyB7ROHA transcript, agent-response-schema section | Zod parse of the chat response (answer, steps, toolCalls, usedDesktop, summary) |
| 2 | Recurring routines with cron + timezone | oqUyyB7ROHA transcript, Inngest routines section | invalid cron returns 400; forced-due tick returns {"ran":1} |
| 3 | Credits gate | oqUyyB7ROHA transcript, credits section | credits 5 -> 4 after one chat; limit+1 denied |

Out of scope: Stripe and email (skipped in the video) ship as named stubs; deploy is Gate-D.

## Stack (stage 2, gate app.stack)

Web SaaS lane. `next build --webpack` and Tailwind v3 because the Aside sandbox blocks
native .node binaries; PGlite as a standalone service on 127.0.0.1:5433; Composio and E2B
env-gated with named fallbacks (static tool list, mock desktop viewer) so every route
runs with zero paid keys.

## Stage close: backend-data (gate app.stage-gate)

| Claim | Executed check | Observed |
|---|---|---|
| Credits decrement | chat as seeded user, then read the sidebar | 5 -> 4 |
| Quota deny | create agent #4 on the free plan | HTTP 402 |
| Routines tick | backdate next_run_at, call the tick | {"ran":1}; it was {"ran":0} until the camelCase consumer fix |

## Build (app-sandbox-build-verify)

Production build green, 10/10 routes, served on :3007 after :3000-:3006 proved stale or
held. The competing-builder failure (a watcher routine building on every wake) was found
and removed; one builder, detached build, log polled.

## Lessons that fired and became ledger rows

LA-01 native binaries, LA-02 process control, LA-03 single builder, LA-05 key-transform
consumers, LA-06 drizzle proxy contract, LA-07 named fallbacks, LA-08 limit+1.

## Held at Gate-D

Deploy and domain attach: held for Mike. The mission closes HELD, not faked-done.
