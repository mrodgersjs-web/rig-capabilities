---
name: app-auth-payments
description: "App Studio sub-skill, stage 5 (backend-data): auth, sessions, payments, webhooks and idempotency - deny paths and ownership proven, cookie flags per environment, every charge and webhook idempotent under a same-key replay, one handler per webhook event type, purchases proven on a real device or store sandbox, and live payment keys held at Gate-D."
tags: [rig, app-studio, sub-skill, auth, sessions, payments, webhooks, idempotency]
metadata:
  parent: app-studio
  tier: sub
  stage: backend-data
  extends: "tg-auth-wiring, auth-implementation-patterns, stripe-integration, tg-quota-gates"
outcome: "An auth and payments slice where each claim carries an executed proof: signed-out deny, ownership deny, cookie flags per environment, exactly one charge for two identical requests, one handler per webhook event type, and test-mode keys only until Mike approves live keys."
activation: "Load for sign-in, sessions, cookies, OAuth, credits, checkout, subscriptions, webhooks, in-app purchases, or any path that charges money."
instruction: "Prove deny paths and ownership, set cookie flags per environment, make every charge and webhook idempotent with a same-key replay, parse each webhook event type on its own, test purchases on a real device or sandbox, keep live keys behind Gate-D, and gate the slice."
applies_when:
  env: "local development with test-mode keys or a named demo-user stub; provider sandboxes for purchases"
  runtime: "Next.js route handlers and server actions; Express or Hono APIs; Expo apps with store purchases"
  deps: "auth vendor (Clerk, NextAuth, Supabase auth) or a demo-user stub; Stripe or store billing in test mode"
  params: "which webhook events the product handles; where the idempotency key comes from"
  budget: "one slice per auth flow or charge path"
  scale: "single app; not a multi-tenant billing platform"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - Prove signed-out deny and ownership deny on every mutation with one request each.
  - Set cookie secure and sameSite flags per environment and prove login and logout on each.
  - Replay every charge and webhook with the same idempotency key and assert exactly one effect.
  - Parse each webhook event type with its own payload shape and test one fixture per type.
  - Keep test-mode keys only and list live keys in the release request for Gate-D.
done_when:
  - "grep:capabilities/skills/app-auth-payments/SKILL.md:LA-47"
  - "grep:capabilities/skills/app-auth-payments/SKILL.md:Gate-D"
  - "grep:capabilities/skills/app-auth-payments/SKILL.md:idempotency key"
  - "cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py"
out_of_scope:
  - live payment keys, real charges, or store submissions without Mike's approval (Gate-D)
  - storing card data (the payment provider holds it)
  - disabling row-level security or auth checks to move faster
---

# app-auth-payments

JEV FIRST, binding on every auth and payments step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call; this slice's verdicts go to `rig-s1gate check app.stage-gate` and `api.backend`.
When the classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes
only above 0.9; below that the slice does not advance, and an uncalibrated ESCALATE is a held
transition.

## Load surface

Always loaded at the start of any auth, session, credits or payment task in stage 5: the
`app-studio` meta-skill routes it from the backend-data row, and `app-studio-conductor` loads it
from its routes table before the slice's first action. It sits beside `app-data-layer` (schema,
quotas, jobs). It is a task-start surface, not a deep reference an agent must already know about.

Sub-skill of `app-studio`, stage 5 of 11. Main skills it extends: `tg-auth-wiring`,
`auth-implementation-patterns`, `stripe-integration`, `tg-quota-gates`.

## Procedure

1. **Deny paths.** Signed out, each protected route returns its deny status; signed in as another
   user, each mutation on someone else's record is refused. One request each, status recorded.
2. **Sessions and cookies.** The cookie `secure` flag depends on the environment, because `secure`
   breaks login on http://localhost (LA-46, CH-CWA-03). Take session and user types from the auth
   library, not the ORM (JTC-03-auth-types-from-auth-lib). Failed signups return one identical
   error shape, so the endpoint does not reveal which emails exist (CH-JSM-10). Every POST form
   carries the framework's CSRF token (TRV-02-post-form-csrf-and-names).
3. **Keys.** Before debugging router code, prove the provider key loads in the runtime that calls
   it (LA-39, JTC-04-provider-key-before-code). Test-mode keys only; with no key, a named fallback
   (LA-07).
4. **Charges.** Every charge and tool-called payment function takes an idempotency key. Run the
   path twice with the same key and assert exactly one charge (LA-47,
   SSG-06-idempotent-charge).
5. **Webhooks.** One handler per event type with its own payload shape; a single shared parse
   shape silently loses data (CH-CWA-10). Verify the signature; in development deliver through a
   tunnel and seed demo credits directly.
6. **Store purchases.** Prove them on a real device or the store sandbox; a simulator run is not
   evidence (GXD-03-iap-needs-real-device).
7. **Credits and quotas.** Gate at the creation path and prove the deny at limit plus one
   (`tg-quota-gates`, LA-08).
8. **Gate.** Send the slice record to `app.stage-gate` and `api.backend`. Live keys, real charges,
   domain and store steps stop at Gate-D with Mike.

## Evidence

Each claim carries its command, exit code and observed output: the signed-out and other-user
requests with their statuses, the Set-Cookie header per environment, two charge requests with the
same idempotency key and the provider's single charge id, one webhook fixture per event type with
its handler result, and the device or sandbox purchase capture. A check that could not run is
BLOCKED with the missing piece named (LA-21).

## From the creators (candidate lessons)

Distilled from ten app-building YouTube channels (`youtube-<slug>` skills). LA-36..LA-51 are
status `candidate`: follow them now; they fire as gated checks only after promotion, which needs
an engine receipt for the lesson id. Source ids are greppable in each channel's
`references/lessons.jsonl`.

- LA-47: idempotent charges, per-event webhook parsing, device-tested purchases, live keys at
  Gate-D (SSG-06-idempotent-charge, CH-CWA-10, GXD-03-iap-needs-real-device).
- LA-46: environment-dependent cookie flags, proven by a login and a logout per environment
  (CH-CWA-03).
- LA-39: prove the key loads in the calling runtime before touching code
  (JTC-04-provider-key-before-code).
- LA-50: a cached route requested as two users never returns one user's data to the other
  (SSG-11-cache-leaks-user-data).
