# Stack decision: Grok Bot clone

Lane: web SaaS (auth, dashboard, agents, credits).
- Next.js App Router + TypeScript, scripts use `next build --webpack` and `next dev --webpack`: Turbopack needs native bindings the Aside sandbox blocks.
- Tailwind v3 (pure-JS PostCSS), not v4: v4 needs @tailwindcss/oxide and lightningcss native binaries. Deviation from the default table, reason stated.
- Data: PGlite as a standalone local service on 127.0.0.1:5433 for build and test; Neon Postgres in production. Drizzle schema is the source of truth.
- LLM: OpenAI via lib/openai, env-gated; without OPENAI_API_KEY the app runs a named mock responder so every route still works.
- Tools: Composio env-gated with a static tool list fallback. Desktop sandbox: E2B env-gated with a mock viewer fallback.
- Auth: Clerk free tier. Jobs: Inngest dev server locally, free tier in production.
Paid spend: none until the product forces it.
