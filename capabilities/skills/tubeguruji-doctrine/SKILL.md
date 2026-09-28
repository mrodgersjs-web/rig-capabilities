---
name: tubeguruji-doctrine
description: "Meta skill and router for the TubeGuruji build doctrine - full-stack AI SaaS applications distilled from the complete @tubeguruji YouTube corpus (221 videos, 2022-2026). The channel's repeatable unit is the AI SaaS skeleton: landing, auth gate, sidebar dashboard, input form with quota, durable generation job with progress, artifact view/share, credits gate. Use when building, reviewing, or teaching a full-stack AI SaaS app, when picking a stack for a ship-fast build, or when deciding whether an app matches the skeleton or needs its own architecture. Fail-closed boundary: deploys, publishes, purchases, and pushes stop at Gate-D; a JEV ESCALATE on a doctrine surface blocks enforcement until calibrated."
tags: [rig, doctrine, fullstack, ai-saas, nextjs, react-native, tubeguruji]
metadata:
  source: "YouTube @tubeguruji full channel 2022-2026; corpus data/corpora/how-to/build-craft/tubeguruji/"
  extracted: "2026-09-25"
  method: "221 videos enumerated, 220 caption transcripts (1 no-caption failure in errors.jsonl), distilled with per-claim videoId citations"
outcome: "A full-stack AI SaaS app built on the corpus skeleton with the default stack, quotas wired, and the corpus' known deploy gotchas pre-checked — every architecture claim traceable to a corpus videoId."
activation: "Load for a full-stack AI SaaS app build or review (web or React Native), a fastest-credible-stack question, or a build matching the landing-auth-dashboard-form-generation-artifact-credits shape; App Studio routes video clones here."
instruction: "Treat the skeleton as the default architecture and the default-stack table as the default vendor set. Route to the tg-* pillar skill that matches the situation before improvising. When a decision contradicts a law (e.g. a long AI job inside a request handler, or a public deploy without Gate-D), stop and apply the law, not the habit. Cite videoIds from the corpus for any doctrine claim you carry outward."
applies_when:
  env: "local repo plus optional Vercel/Expo account; corpus checked out at data/corpora/how-to/build-craft/tubeguruji"
  runtime: "Next.js or Vite web app, or React Native/Expo mobile app, Node 18+ toolchain"
  deps: "node package manager; optional Clerk/Kinde, Neon/Convex/Firebase, Inngest/Trigger.dev, Gemini or OpenRouter keys — all substitutable"
  params: "skeleton ordering fixed; vendor choices per default-stack table; quota numbers are product decisions (corpus range 1/day to 15/24h)"
  budget: "skeleton assembly is minutes-to-hours; per-vendor signup and free tiers keep cash cost at zero until scale"
  scale: "single app, one team, free-tier traffic; not a multi-tenant enterprise architecture"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
  - net.api-calls
  - gate-d-required:deploy
  - gate-d-required:publish
  - gate-d-required:purchase
flow:
  - Classify the build against the skeleton; name which skeleton stages are in scope.
  - Pick the stack from the default-stack table; record any deviation and its reason.
  - Route to the matching tg-* pillar skill and follow it for that stage.
  - Check the build against the eight laws before calling any stage done.
  - On ship, run tg-deploy-gotchas checks and stop at Gate-D before any public action.
done_when:
  - "grep:data/corpora/how-to/manifest.jsonl:build-craft"
  - "cmd:test $(ls data/corpora/how-to/build-craft/tubeguruji | wc -l | tr -d ' ') -eq 220"
  - "grep:capabilities/skills/tubeguruji-doctrine/SKILL.md:default stack"
  - "grep:capabilities/skills/tubeguruji-doctrine/SKILL.md:5qF8w6ISIKg"
great_example: examples/great/code-engineering/great-tg-grok-bot-clone.md
out_of_scope:
  - enterprise multi-tenant architecture, compliance regimes, SOC2-style controls
  - test/CI strategy and backend-security hardening (corpus has almost none — add from RIG doctrine, not from tubeguruji-doctrine)
  - any public deploy, publish, purchase, or push without Gate-D approval
  - quoting sponsored corpus claims (credit totals, discounts) as verified numbers
---

# TubeGuruji Build Doctrine

JEV FIRST, and it binds every build under this doctrine: an agent whose only
context is this excerpt sends semantic triage, routing, and classification to the
rig-s1gate Jev path BEFORE any frontier LLM call - stack picks, gate placement,
stage transitions, and artifact verdicts are typed judgments, not vibes. When the
fast classifier is unavailable: DEFER, never guess a verdict locally. A required
noul passes only above 0.9; below that the stage does not advance.


## Load surface

This doctrine is an always-loaded task-start surface for app-building work: the
tg-app-studio-session harness, the app-studio-conductor agent, and every tg-*
builder agent load it before their first action - not a deep reference an agent
must already know about.

## JEV-first decision routing (binding on every build that loads this doctrine)

Concretely, before any frontier LLM call during an app build, route each typed decision:
CODE first (deterministic rule: stack table, quota numbers, deploy gotcha catalog),
then JEV via `rig-s1gate check <rubric> --file <artifact> --subject <kind> --json`
(a required noul passes only above 0.9), then SYSTEM 2 (generation: writing the
feature), then HUMAN (Gate-D: deploy, publish, purchase, push). When the fast
classifier is unavailable or the kind is absent from work-criteria.json: DEFER -
never guess a verdict locally, and never let an unjudged stage advance. Stage
transitions in this doctrine's processes are JEV-scored surfaces: BUILD before
VERIFY, VERIFY before SHIP, and SHIP stops at Gate-D.

<objective>
The governed distillation of one creator's 221-video corpus on building and shipping
full-stack AI SaaS apps fast. Use it as the default architecture for quick, real,
monetizable web/mobile AI products — and as the checklist of known deployment and
integration gotchas the corpus already paid for. RIG hard law still governs: no public
deploy, spend, or push without Gate-D; the corpus teaches Vercel-deploy-as-default,
RIG wraps that default behind approval.
</objective>

## The corpus in one paragraph

One creator (Rahul, "TubeGuruji"), 2022→2026. The stack evolves on camera:
CRA → Vite+React (2022-23) → Next.js 13/14 App Router full-stack (2023-24) →
AI SaaS wave (2024-25: Gemini, Clerk, Neon+Drizzle, Convex, Inngest, Supabase) →
agentic builds (2025-26: Cursor, Factory.ai, Google Antigravity, Claude Code, Codex,
Replit Agent 4, Traycer, Jolli AI). A parallel mobile lane runs React Native + Expo
end to end. The teaching format never changes: walk the finished app, name the stack,
build from zero, deploy.

## The laws

1. **Demo-first, build-second.** Every course opens with a full click-through of the
   finished app before any scaffold. Build the same way: know the shipped surface
   before the first file (e.g. zcYM_Gqoph4, Dsw0pMnblWg, zrdbOx0eGtM).
2. **The skeleton is the product; the vendor is a swap.** Landing → auth → sidebar
   dashboard → form+quota → generation with progress → artifact/share → credits gate
   is the repeatable unit (zcYM_Gqoph4 vs zjwj21wzs4U are the same app in two domains:
   recruiter and medical). Swap Clerk↔Kinde↔Supabase-auth, Neon↔Convex↔Firebase
   without touching the skeleton.
3. **Free tier is a design constraint, not an afterthought.** Tools are chosen by
   free-tier first: Gemini for free daily credits (ciXiibK7Gds), Neon/Convex/Firebase
   free DBs, Vercel free deploys, EAS free build queue (~30/mo, cxto0P5DSYU). Build
   before revenue; pay only when the product forces it.
4. **Quota gates are product logic.** Free limits are implemented three ways and the
   choice is per-app: edge rate limit (Arcjet token bucket, refill 86400s = 2/day,
   ciXiibK7Gds; 15 msgs/24h, saoW6BaNamc; 1 itinerary/day, sXRDL-EPtrM), DB counter
   (3 forms free, s28yOCBVgGw), entitlement flag (paid-only chapters, rdaSPdCkoFQ).
5. **Long AI jobs never run in-request.** Multi-step generation (fetch → script → TTS
   → captions → images → render → save) goes to durable workflows — Inngest step.run
   chains (-h1O73T0jmo, 31-Qfr2Pc5Q, 6niOEjus2Vg), Trigger.dev (kxM_oEMn3IM,
   rcEUVADmH2g), or n8n (b_4Z_QpEd2Q) — with per-step progress in the UI.
6. **Build with the agent you teach.** From 2025 the corpus itself is agent-built:
   plan mode before implementation (kxM_oEMn3IM Codex), paste-the-error-to-fix loops
   (5VK8rc3GXdc), automated PR review after each feature (CodeRabbit, WmWJNSxCiZc).
   Review every agent plan before it implements (31-Qfr2Pc5Q).
7. **Ship ritual is fixed.** `npm run build` locally first (-AVtkiG0laE) → push to
   GitHub → import on Vercel → paste whole `.env` (auto key/value split, dJPVV0nFFWY)
   → deploy → attach domain. Any env change requires a redeploy without cache
   (zrdbOx0eGtM, s28yOCBVgGw).
8. **Bugs are shown, not edited.** The corpus teaches via live failures: duplicate
   writes from StrictMode (zlZ_7VTfxUs), a deployed app demanding login because the
   middleware public-route list is missing `/` (zjwj21wzs4U), an admitted wrong
   percentage left on screen (qop_fAoayWI). Reproduce the failure before fixing it.

## The default stack (2025-26 AI SaaS lane)

| Layer | Default | Swap options seen | Evidence |
|---|---|---|---|
| Framework | Next.js App Router + TypeScript | Vite+React (frontend-only), React+Expo (mobile) | dJPVV0nFFWY, egQajXL7nn4 |
| UI | Tailwind CSS + shadcn/ui + Sonner toasts | NextUI, daisyUI, HyperUI | YwcyE1XlUZU, sVYNEqlx3Nc |
| Auth | Clerk (middleware + ClerkProvider + useUser) | Kinde, NextAuth, Firebase auth, Supabase auth, Convex | VjimQ-VEIiE, bpP7PKuEjgI |
| DB | Neon serverless Postgres + Drizzle ORM | Convex (realtime), Firebase/Firestore, Supabase, Strapi+MySQL, HyGraph | sVYNEqlx3Nc, UgLN9O930vE |
| Long jobs | Inngest (step.run chains) | Trigger.dev, n8n | 6niOEjus2Vg, kxM_oEMn3IM, b_4Z_QpEd2Q |
| LLM | Gemini via AI Studio (free daily credits) | OpenAI, OpenRouter (multi-model fan-out), Azure OpenAI | ciXiibK7Gds, saoW6BaNamc, BamV5jDeJeU |
| Media | ImageKit (gen + URL-param transforms), Remotion (render) | Luma, Replicate models, Akool | PdVSn-w419g, ciXiibK7Gds, O_f55bWzsik |
| Voice | Vapi (agent), AssemblyAI (streaming STT) | Murf, Replicate Chatterbox, Deepgram | zcYM_Gqoph4, zjwj21wzs4U, kxM_oEMn3IM |
| Money | Stripe checkout + webhook credits | PayPal, Clerk billing (one line), UPI | 1DXV4LCWkic, sVYNEqlx3Nc, saoW6BaNamc, YbUJpaOlUbk |
| Abuse | Arcjet (injection detection + token buckets) | DB counters, entitlement flags | -h1O73T0jmo, s28yOCBVgGw |
| Deploy | Vercel (git push) | Expo EAS (APK/AAB), Hostinger cPanel zip | zrdbOx0eGtM, cxto0P5DSYU, irHMPFrQWrA |

## Router

| Situation | Load |
|---|---|
| Standing up the app shell, nav, CRUD screens, optimistic UI | tg-saas-skeleton |
| Wiring auth for web or mobile, OAuth breaking in production | tg-auth-wiring |
| A voice-agent product (recruiter, medical, tutor) | tg-voice-agent-stack |
| Multi-step AI generation: script/voice/image/video chains | tg-durable-ai-pipelines |
| Media generation specifics: TTS, captions, images, video render | tg-ai-media-pipeline |
| Free-tier selection, quotas, credits, upgrade UX | tg-free-tier-engineering |
| Implementing a quota gate (rate limit vs counter vs flag) | tg-quota-gates |
| Driving the build with a coding agent | tg-agentic-build-workflow |
| React Native / Expo mobile lane of the same skeleton | tg-expo-mobile-ai |
| Prompt + loop craft for the coding agent | tg-agent-prompt-craft |
| Deploy day: env vars, domains, webhooks, signing keys, EAS | tg-deploy-gotchas |

## Citation and hygiene rules for this family

- Every doctrinal claim carries a videoId (e.g. `zcYM_Gqoph4`). Resolve it against
  `data/corpora/how-to/manifest.jsonl` (surface `build-craft`, channel `tubeguruji`);
  the transcript lives at `data/corpora/how-to/build-craft/tubeguruji/<id>.txt`.
- Transcripts are auto-generated ASR: product names garble (Inngest as "Inforge/injest",
  Vercel as "versel/veral", shadcn as "shaden", axios as "exos"). Never quote a garbled
  name as the vendor's name; verify against the vendor's own docs before external use.
- One video failed capture (no caption track): `5qF8w6ISIKg`, logged in
  `data/corpora/how-to/errors.jsonl`. Do not fabricate its content.
- Sponsored claims in the corpus (credit-stacking totals, hosting discounts) are the
  creator's claims, not verified facts. Carry them labeled, never as numbers of record.

## Known gaps in the corpus (do not invent)

Almost no testing/CI content, no Redux/Zustand, thin backend-security discussion
(one video deliberately disables Supabase RLS to get moving, bpP7PKuEjgI), API keys
pasted in source "for simplicity" in early videos (lUMIj6I9fR8). Treat security and
test practice as RIG-side additions, not corpus doctrine.
