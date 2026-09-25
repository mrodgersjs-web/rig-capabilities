---
name: tg-auth-wiring
description: >
  Sub-skill of tg-saas-skeleton: drop-in auth wiring per the TubeGuruji corpus —
  Clerk middleware + provider recipe, Kinde, NextAuth, Firebase auth, Supabase
  auth, Convex email/password — and the production OAuth failures the corpus hit
  repeatedly (access-blocked origins, Clerk production instances, redirect URLs).
tags: [rig, doctrine, auth, clerk, oauth, tubeguruji]
metadata:
  source: "corpus — VjimQ-VEIiE (Clerk middleware recipe), saoW6BaNamc (Clerk production flip), fh1s6UbzJ7k + hCSX5zSb3b4 (OAuth access-blocked), MbiAwAp3lCA (Expo Google SHA-1), bpP7PKuEjgI (Kinde), lpHQCzXoP_g (NextAuth), UgLN9O930vE (Convex email/password)"
  extracted: "2026-09-25"
  parent: tg-saas-skeleton
outcome: "Working sign-in on the deployed domain — not just localhost — with the provider's production settings verified."
activation: "Load when adding auth to any skeleton build, or when a deployed app throws access-blocked / silent login failure that works locally."
instruction: >
  Pick the provider by the app's needs (dedicated auth = Clerk; DB+auth in one =
  Supabase; Firebase-native mobile = Firebase auth; realtime backend = Convex
  email/password). Copy the provider's own docs wiring, then before calling auth
  done, verify sign-in on the DEPLOYED URL — the corpus' most repeated failure is
  auth that works locally and breaks in production.
applies_when:
  env: "local repo + deployed preview (Vercel) + provider dashboard access"
  runtime: "Next.js middleware-capable app, or Expo mobile app"
  deps: "chosen provider SDK/package; Google Cloud console project for Google providers"
  params: "protected routes list; public routes list must include '/'; providers per product"
  budget: "under an hour per provider; the production-origin check adds minutes"
  scale: "single app, one provider (two max: social + email)"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
flow:
  - Choose provider by need; record the choice and why.
  - Copy the provider's documented wiring verbatim (Clerk: .env key → middleware.js → ClerkProvider in layout.js → protected route list, VjimQ-VEIiE; Firebase Storage/upload: docs walkthrough, jP28ISnh69g).
  - Wire social + email providers; surface the signed-in user via the provider hook (Clerk useUser() for primary email, s28yOCBVgGw).
  - Verify locally: sign in, sign out, protected-route redirect.
  - Production pass: add the deployed origin + redirect URI in the provider console (Google Cloud credentials for Google OAuth, fh1s6UbzJ7k, hCSX5zSb3b4); flip Clerk to its production instance with the real domain and client secret (saoW6BaNamc); configure login AND logout redirect URLs for Kinde (zrdbOx0eGtM).
  - Mobile pass (Expo): register package name + SHA-1 fingerprint in the Google Cloud OAuth client or sign-in fails with a docs-shaped dead end (MbiAwAp3lCA: "you will not find the single video" covering it).
  - Re-verify sign-in on the deployed URL and record it.
done_when:
  - "grep:capabilities/skills/tg-auth-wiring/SKILL.md:SHA-1"
  - "grep:capabilities/skills/tg-auth-wiring/SKILL.md:production instance"
  - "grep:data/corpora/how-to/manifest.jsonl:fh1s6UbzJ7k"
out_of_scope:
  - custom password auth, session/refresh-token engineering, MFA
  - IAM/SSO enterprise patterns
  - storing or printing provider secrets (reference keychain/env names only)
quality_floor: "Auth is not done until sign-in is demonstrated on the deployed domain; a localhost-only demo is a RED."
---

# Auth Wiring (corpus recipes)

## The provider table

| Need | Provider | Corpus evidence |
|---|---|---|
| Dedicated auth, fastest | Clerk — `.env` key → `middleware.js` → `ClerkProvider` in `layout.js` → list protected routes | VjimQ-VEIiE (exact recipe); sponsored build V2AE0YS8WYs |
| DB + auth in one | Supabase auth (email/password + GitHub/Google OAuth) | rcEUVADmH2g: "we use Supabase for the database as well as for the authentication" |
| Google-first portal | NextAuth | lpHQCzXoP_g, SGsDxZukodQ |
| Firebase-native mobile | Firebase auth (Google or email/password) | 0-NwPCCzXv0, 2ua_Eu0LhcI |
| Simple social, no Clerk | Kinde (Google/Facebook/email) | bpP7PKuEjgI |
| Realtime backend | Convex with email/password hand-rolled | UgLN9O930vE |
| Mobile Google sign-in | Expo Google sign-in + manual OAuth client config | MbiAwAp3lCA |

## The production failures (all corpus-observed, all repeatable)

1. **Deployed Google OAuth throws "access blocked"** while localhost works. Fix:
   add the production domain as authorized origin + redirect URI in Google Cloud
   credentials. Observed three separate times (fh1s6UbzJ7k, hCSX5zSb3b4) — the
   single most-repeated real-world auth failure in the corpus.
2. **Clerk works in dev, silently fails in prod** until flipped to a **production
   instance** with a real custom domain (not the virtual `.clerk.accounts.dev`
   one) plus the Google/GCP client secret (saoW6BaNamc).
3. **Kinde silent login failure on deploy**: both login AND logout redirect URLs
   must be configured for production (zrdbOx0eGtM).
4. **Middleware public-routes list missing `/`**: the deployed app demands sign-in
   on the landing page itself; fix the list, commit, push, redeploy (zjwj21wzs4U).
5. **Expo Google sign-in**: needs the Android package name registered in `app.json`
   AND the SHA-1 fingerprint added to the Google Cloud OAuth client — the docs
   don't make the fingerprint step obvious (MbiAwAp3lCA).

## Ownership checks are part of auth

Authorization got its own corpus demo: change the owner email on a record and show
the delete button disappear for the original user (P6dha4Sq8gQ). Gate mutations on
ownership, not just authentication.
