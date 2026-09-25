---
name: tg-saas-skeleton
description: >
  The TubeGuruji AI SaaS skeleton — landing page, auth gate, sidebar dashboard,
  input form with quota, generation with progress, artifact view/share, credits
  gate — plus the build order and UI habits (optimistic updates, toasts, skeleton
  loaders, component discipline, responsive-by-default) from the 221-video corpus.
  Use when standing up any new full-stack AI SaaS app or judging whether an
  existing one follows the skeleton.
tags: [rig, doctrine, nextjs, saas, fullstack, tubeguruji]
metadata:
  source: "corpus data/corpora/how-to/build-craft/tubeguruji/ — skeleton instances zcYM_Gqoph4, zjwj21wzs4U, s28yOCBVgGw, saoW6BaNamc, sXRDL-EPtrM, rdaSPdCkoFQ, sxn2GPQjJgc, 6GKFEqB8LWo, eMplIjZ80Zs"
  extracted: "2026-09-25"
  parent: tubeguruji-doctrine
  subs: [tg-auth-wiring, tg-voice-agent-stack, tg-deploy-gotchas]
outcome: "A working SaaS shell (landing, auth, dashboard, feature screen, artifact surface, quota/credits) assembled in skeleton order with optimistic UI and toasts, matching a named corpus instance."
activation: "Load when starting a new full-stack SaaS app, when a build feels unstructured, or when reviewing whether an app covers landing/auth/dashboard/quota/artifact/monetization."
instruction: >
  Build the seven skeleton stages in order, demoing each against a real UI before
  starting the next. Defer auth wiring to tg-auth-wiring and deploy to
  tg-deploy-gotchas. Keep one artifact stage per app: the skeleton is the product,
  vendors are swaps.
applies_when:
  env: "local dev repo, Node 18+, Vercel-ready"
  runtime: "Next.js App Router (web) or React Native/Expo (mobile shell)"
  deps: "Tailwind + shadcn/ui (or NextUI/daisyUI), an auth provider, a hosted DB, toast library"
  params: "sidebar nav items dashboard/studio/settings; toast on every mutation; responsive check at 390px"
  budget: "shell in hours, not days; no custom auth, no custom component library"
  scale: "single-product SaaS, free-tier traffic"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
flow:
  - Walk the intended finished app screen by screen before scaffolding (demo-first law).
  - Scaffold (create-next-app / Vite / Expo) and set up Tailwind + component kit + Sonner Toaster in root layout (6GKFEqB8LWo).
  - Build the landing page; generate it with an agent if one is in the loop (-h1O73T0jmo, 5VK8rc3GXdc).
  - Wire the auth gate and protected dashboard route (see tg-auth-wiring).
  - Build the dashboard shell: left sidebar (dashboard/studio/settings/account), bento/card grid (zcYM_Gqoph4, rcEUVADmH2g).
  - Build the input form stage with its quota check (see tg-quota-gates) and generation stage with progress (see tg-durable-ai-pipelines).
  - Build the artifact stage: view, edit, share link via navigator.clipboard.writeText + toast (zcYM_Gqoph4).
  - Wire the credits/membership gate and upgrade toast (6GKFEqB8LWo free-file-cap toast; zcYM_Gqoph4 credits<=0 gate).
  - Close with the responsive pass (390px reflow, collapsible menu) and the deploy ritual (tg-deploy-gotchas).
done_when:
  - "grep:capabilities/skills/tg-saas-skeleton/SKILL.md:credits"
  - "grep:capabilities/skills/tg-saas-skeleton/SKILL.md:navigator.clipboard.writeText"
  - "grep:data/corpora/how-to/manifest.jsonl:zcYM_Gqoph4"
great_example: examples/great/code-engineering/great-tg-voice-agent-saas.md
out_of_scope:
  - auth provider mechanics (tg-auth-wiring)
  - background job internals (tg-durable-ai-pipelines)
  - payment integration beyond the gate/credits surface
  - public deploy or domain purchase without Gate-D
quality_floor: "No skeleton stage is 'done' from a code-only claim — each stage is demoed in a real browser/device with its toast or state change observed."
---

# The AI SaaS Skeleton

Seven stages, fixed order. The corpus built this skeleton dozens of times; two 2025
voice-agent builds — recruiter (zcYM_Gqoph4, Vapi/Supabase) and medical
(zjwj21wzs4U, AssemblyAI/Clerk) — are the same app in two domains, which is the proof
the skeleton, not the vendor, is the repeatable unit.

## The seven stages

1. **Landing** — hero, feature grid, pricing cards. Often AI-generated even inside
   the tutorials (-h1O73T0jmo, 31-Qfr2Pc5Q, iVVG9wOXEqQ).
2. **Auth gate** — public landing, everything else behind sign-in, enforced by
   middleware. The classic shipped bug is a missing `/` in the public-route list
   (zjwj21wzs4U). Mechanics: tg-auth-wiring.
3. **Dashboard shell** — left sidebar (dashboard/studio/calendar/account/settings),
   bento/card grid, credits counter visible (egQajXL7nn4 puts the credit counter in
   the sidebar).
4. **Input form + quota** — the form that starts generation, gated by the app's free
   quota. Gate implementations: tg-quota-gates.
5. **Generation with progress** — per-step progress bar driven by the background job
   (ciXiibK7Gds Inngest progress; kxM_oEMn3IM Trigger.dev step progress).
6. **Artifact view/share** — generated artifact with edit and a shareable link;
   copy via `navigator.clipboard.writeText(...)` + toast (zcYM_Gqoph4 02:51).
7. **Credits/upgrade gate** — `user.credits <= 0` → toast "please add credits"
   before creating (zcYM_Gqoph4 05:44); free-file cap → "upgrade to add new file"
   toast (6GKFEqB8LWo).

## UI habits that recur across the corpus

- **Optimistic/local-state updates**: cart count and totals change "without
  refreshing" (sVYNEqlx3Nc, V2AE0YS8WYs); portfolio edits render instantly (pyVwMi48-6U).
- **Toast on every mutation** — folder created, link copied, meeting created,
  please-add-credits (zlZ_7VTfxUs, zrdbOx0eGtM, zcYM_Gqoph4).
- **Skeleton loaders**: `animate-pulse` placeholder divs sized per block; skeleton
  effect replacing broken images (Dsw0pMnblWg).
- **Component discipline**: sections split into components/pages folders; ES7 `RFC`
  snippet for boilerplate; reuse one listing component parameterized by type
  (2lNjK9IwGlI, cEb1aIRfqrY).
- **Guard-before-render**: conditional render on `list.length > 0` because the first
  render runs before fetch resolves (PSee8mtiaWA shows the exact undefined error).
- **Central API module**: one `services/GlobalApi.jsx` with `axios.create({baseURL})`
  and exported endpoint functions (lUMIj6I9fR8, cRlRuJhM7WQ).
- **Soft delete over hard delete**: an `archive` boolean flipped instead of row
  deletion, recycle-bin restore (sxn2GPQjJgc, ruIK7LFBjHI).
- **Pagination + per-column search** on data grids; reset offset to 0 on new query
  (qop_fAoayWI, sVYNEqlx3Nc).

## Skeleton variants seen

- **Learning platforms**: stage 6 becomes chapters + progress ticks stored per user
  (HbKq40txPjY, zMMcxWORZvg `user enrolled course` model with reference fields).
- **Marketplaces**: stage 6 becomes listing detail + chat with seller + share sheet
  (VOFJ1wBJcUo); payments move from credits to cart/checkout (PdVSn-w419g).
- **Agent platforms**: stage 4 becomes a node graph (start/agent/if-else/user-approval
  nodes persisted to the DB, -AVtkiG0laE) or a chat with generative-UI question cards
  (sXRDL-EPtrM).
