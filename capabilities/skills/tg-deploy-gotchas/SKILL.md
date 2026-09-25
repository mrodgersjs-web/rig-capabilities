---
name: tg-deploy-gotchas
description: >
  Sub-skill of tg-saas-skeleton: the deploy-day failure catalog from the TubeGuruji
  corpus — env-var changes require redeploy, OAuth origins, Inngest signing-key
  sync, Stripe webhook ngrok, SPA rewrites, Clerk production instances, image
  domain whitelists, and the cPanel zip alternative.
tags: [rig, doctrine, deployment, vercel, gotchas, tubeguruji]
metadata:
  source: "corpus — zrdbOx0eGtM + s28yOCBVgGw (redeploy after env change), fh1s6UbzJ7k + hCSX5zSb3b4 (OAuth origins), 6niOEjus2Vg + lHFlpc5auDY (Inngest key sync), O_f55bWzsik (ngrok webhooks), saoW6BaNamc (Clerk production), f_7grfh9TxU (SPA rewrite), OTTZEwWN4l4 (image domains), irHMPFrQWrA (cPanel), -AVtkiG0laE (build locally first), uZpwyS-0QIY (5-minute deploy)"
  extracted: "2026-09-25"
  parent: tg-saas-skeleton
outcome: "A deployed app that works for real users — sign-in, generation, payments, and background jobs verified on the production URL, with each corpus gotcha checked off."
activation: "Load on deploy day for any skeleton build, when a production-only failure appears, or before handing a deployed URL to a user."
instruction: >
  Run the ritual: build locally, push, import, paste env, deploy, domain — then
  walk the gotcha catalog BEFORE demoing to anyone. A production URL that renders
  is not a working deploy; auth, webhooks, keys, and background jobs each need a
  production-path check.
applies_when:
  env: "repo pushed to GitHub; Vercel (or alternative) account; provider dashboards"
  runtime: "Next.js on Vercel (default), Expo EAS for mobile builds, or static zip to shared hosting"
  deps: "provider consoles (Google Cloud, Clerk, Inngest/Trigger.dev, Stripe)"
  params: "one env var set per environment; production origins per provider; cache-bypass redeploy for env changes"
  budget: "an hour for the full catalog; each gotcha is minutes"
  scale: "single app, single production environment"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
  - gate-d-required:deploy
  - gate-d-required:publish
flow:
  - `npm run build` locally first — surface errors on your machine, not in the deploy log (-AVtkiG0laE).
  - Push to GitHub → import on Vercel → paste the whole `.env` (auto key/value split, dJPVV0nFFWY) → deploy → attach domain (uZpwyS-0QIY).
  - OAuth: add the production origin + redirect URI in Google Cloud credentials, or "access blocked" (fh1s6UbzJ7k, hCSX5zSb3b4); flip Clerk to its production instance with the real domain (saoW6BaNamc); Kinde needs login AND logout redirect URLs (zrdbOx0eGtM).
  - Env changes are not live until a fresh redeploy without cache (zrdbOx0eGtM, s28yOCBVgGw).
  - Background jobs: Inngest Vercel integration injects signing/event keys → REDEPLOY → "sync app" in the Inngest dashboard (lHFlpc5auDY, -h1O73T0jmo); key rotation forces another redeploy (6niOEjus2Vg); Trigger.dev Vercel connect auto-syncs its secret (rcEUVADmH2g).
  - Webhooks: local Stripe webhook testing needs ngrok; demo credits seeded manually in DB (O_f55bWzsik).
  - SPA routes: add `vercel.json` rewrite `/*` → `/` or refreshes 404 (f_7grfh9TxU); external images need `next.config` images.domains whitelist + dev-server restart (OTTZEwWN4l4).
  - Middleware public routes must include `/` or the landing page demands login (zjwj21wzs4U).
  - Verify the production path end to end: sign in, run one generation, one webhook, one background job — on the deployed URL.
  - RIG hard law: the deploy itself stops at Gate-D.
done_when:
  - "grep:capabilities/skills/tg-deploy-gotchas/SKILL.md:sync app"
  - "grep:capabilities/skills/tg-deploy-gotchas/SKILL.md:ngrok"
  - "grep:capabilities/skills/tg-deploy-gotchas/SKILL.md:Gate-D"
out_of_scope:
  - infrastructure-as-code, multi-region, blue-green deploys
  - mobile store publishing (tg-expo-mobile-ai covers EAS builds only)
  - executing the deploy without Gate-D
quality_floor: "Deploy is RED until each production-path check (auth, env, jobs, webhooks, images, routes) has been run against the live URL — not against localhost."
---

# Deploy-Day Gotcha Catalog

## The ritual

1. Build locally first: "that is the first step" — catch errors before the deploy
   log does (-AVtkiG0laE).
2. git push → import on Vercel → paste the entire `.env` into the env box (it
   auto-splits keys/values: "how cool", dJPVV0nFFWY) → deploy → rename/attach the
   domain (uZpwyS-0QIY is the 5-minute version).
3. On deploy failure: "just check the build log and then fix that error and push"
   (saoW6BaNamc); a dependency clash may need a legacy-peer-deps install override
   (rdaSPdCkoFQ).

## The catalog (each one shipped broken in the corpus first)

| Gotcha | Symptom | Fix | Evidence |
|---|---|---|---|
| Env change without redeploy | new BASE_URL/keys ignored, share links still say localhost:3000 | redeploy, do NOT use existing cache | zrdbOx0eGtM 05:26, s28yOCBVgGw |
| OAuth origins missing | deployed Google sign-in throws "access blocked" (localhost worked) | add production origin + redirect URI in Google Cloud credentials | fh1s6UbzJ7k, hCSX5zSb3b4 |
| Clerk virtual vs production instance | auth silently broken in prod | flip to production instance + real domain + GCP client secret | saoW6BaNamc |
| Kinde redirect URLs | login silently fails deployed | configure login AND logout redirect URLs | zrdbOx0eGtM |
| Inngest not synced | scheduled/generation tasks dead in prod | Vercel integration injects keys → redeploy → "sync app" in Inngest | lHFlpc5auDY, -h1O73T0jmo |
| Inngest key rotation | tasks fail after key change | "whenever you update any Inngest signing key you have to redeploy" | 6niOEjus2Vg |
| Stripe webhooks local | webhook never fires in dev | ngrok tunnel; seed demo credits manually in DB | O_f55bWzsik |
| SPA refresh 404 | deep links break on refresh | `vercel.json` rewrite `/*` → `/` | f_7grfh9TxU |
| Remote images blocked | next/image errors on CMS images | `next.config` images.domains whitelist + restart dev server | OTTZEwWN4l4 |
| Middleware public routes | landing page demands login in prod | include `/` in the public-route list, commit, push | zjwj21wzs4U |
| Duplicate effects on refresh | rows inserted twice (StrictMode) | `reactStrictMode: false` + restart (config does not hot-reload) | zlZ_7VTfxUs |
| Convex dev data expectations | production dashboard looks empty | prod starts empty; swap dev→prod deployment URL/key | fh1s6UbzJ7k, hCSX5zSb3b4, UgLN9O930vE, b_4Z_QpEd2Q |

## Alternatives when Vercel is not the answer

- Static React app to shared hosting: `npm run build` → zip `build/` → cPanel
  upload, the $3/mo path (irHMPFrQWrA).
- Replit publish for agent-built apps, with its pre-publish security scan
  (5VK8rc3GXdc).

## The verification bar

Rendered page ≠ working deploy. Sign in, generate one artifact, fire one webhook,
run one background job — on the production URL. Then, per RIG hard law, anything
public (custom domain on real users, purchase of that domain, announce) stops at
Gate-D with Mike.
