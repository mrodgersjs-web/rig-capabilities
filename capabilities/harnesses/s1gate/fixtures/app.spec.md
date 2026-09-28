# Spec: Grok Bot clone (source: TubeGuruji video oqUyyB7ROHA, 5h52m)

| # | Feature | Source | Acceptance check |
|---|---|---|---|
| 1 | Clerk sign-in gate on /dashboard | oqUyyB7ROHA @00:14:10 | GET /dashboard signed out -> 307 to /sign-in |
| 2 | Create agent with name, instructions, tools | oqUyyB7ROHA @01:02:30 | POST /api/agents -> 201; agent card visible on /dashboard |
| 3 | Structured agent response (answer, steps, toolCalls, usedDesktop, summary) | oqUyyB7ROHA @01:48:05 | Zod parse of /api/chat response succeeds |
| 4 | Recurring routines with cron + timezone | oqUyyB7ROHA @03:20:40 | invalid cron -> 400; due routine tick -> {"ran":1} |
| 5 | Credits gate | oqUyyB7ROHA @04:55:00 | limit+1 request -> 402 |

What done looks like: thumbnail data/corpora/how-to/build-craft/tubeguruji-images/oqUyyB7ROHA.jpg plus screens /dashboard, /dashboard/agent/new, /chat/[id].
Out of scope: Stripe checkout and email (skipped in the video; shipped as named stubs), deploy (Gate-D).
