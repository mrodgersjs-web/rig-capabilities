---
name: traject-gtm-waitlist
description: "Traject GTM stage: design, spec and audit the waitlist / early-access capture for Traject (interview rooms for senior candidates) - field spec, consent line, storage with insert-only RLS, confirmation email, referral mechanic and the funnel metric that proves the waitlist is working. Use when adding, moving, or reviewing any Traject email-capture surface."
tags: [rig, gtm, waitlist, lead-capture, supabase, traject]
metadata:
  tier: sub
  purpose: stage-skill
  category: gtm-sales-revenue
  family: traject-gtm
  built: "2026-09-28"
outcome: "A waitlist spec an engineer can implement unchanged: fields with optionality named, a consent line that survives GDPR/CCPA review, one storage decision with its tradeoff stated, DRAFT confirmation copy held for Mike, a referral mechanic, and one funnel metric with a target that is labelled as a target."
activation: "Load from traject-gtm when the stage is WAITLIST, or when a Traject capture form, waitlist page, or early-access flow is being built, moved, or audited."
instruction: "Spec the fields first (email required; target role, seniority, next interview date optional), write the consent line, pick storage with the tradeoff named, draft the confirmation email as DRAFT only, define the referral mechanic and the single funnel metric. Never send, never publish, never create the table."
applies_when:
  env: "draft/audit only; no platform writes"
  runtime: "Supabase (Postgres) or a form provider (Tally / Loops / Formspree)"
  deps: "Traject landing at https://cockpit-nine-black.vercel.app/; Stripe products in code (room_pass $49 one-time, active_search $49/month, coach 3 seats + overage)"
  params: "surface (landing, post-checkout, LinkedIn), audience (candidate, coach)"
  budget: "one spec per surface; one storage decision, no parallel lists"
  scale: "single public waitlist; no multi-tenant list segmentation until 100 signups"
permissions:
  - fs.read
  - fs.write
  - net.read
  - gate-d-required:publish
  - gate-d-required:send
  - gate-d-required:db-write
flow:
  - Route through traject-gtm first; JEV-first paragraph applies.
  - Field spec: email (required), target_role (optional), seniority (optional, single-select), next_interview_date (optional, date), consent timestamp + source URL + UTM fields (required, hidden).
  - Consent line must name what is sent and how to leave.
  - Storage decision records the tradeoff in one line (see body).
  - Confirmation email is written as DRAFT in the draft-preview JSON format and held for Mike.
  - Referral mechanic and one funnel metric with target labelled TARGET.
done_when:
  - "cmd:bash capabilities/skills/traject-gtm/scripts/verify_paths.sh"
  - "Field list names required vs optional explicitly; no field exists without a purpose line"
  - "Storage tradeoff named in one sentence; insert-only RLS named when Supabase is chosen"
  - "Confirmation email marked DRAFT and not sent"
  - "One funnel metric with a TARGET label, not a measured claim"
---

# traject-gtm-waitlist

## JEV FIRST
Typed judgments in this stage (is this form publishable, does this consent line pass, is this email
ready to send) go to `/Users/rig128gb/.rig/bin/rig-s1gate check <rubric> --file <abs path> --subject
<kind> --json` BEFORE any frontier LLM call, decision id recorded. Fail closed: classifier down =
DEFERRED, never a guessed verdict. An advisory PASS is never permission to publish a form or send an
email; publishing and sending are Gate-D.

## Field spec (canonical)

| Field | Required | Purpose |
|---|---|---|
| email | yes | the only thing the waitlist must capture |
| target_role | no | segments demand; names which room to build first |
| seniority | no (single-select: Senior IC / Director / VP / C-level / Other) | validates ICP-1 without asking salary |
| next_interview_date | no | urgency signal; drives who gets invited first |
| consent_at, source_url, utm_* | yes (hidden) | proves consent and measures channel |

Never add "company" or "current employer" to a public form for a job-search product. It reads as surveillance to a candidate who is quietly searching.

## Consent line (DRAFT)
"Email me when Traject opens, plus occasional product notes. One click to unsubscribe in every email.
We never sell or share your address." (Shorter is better; the unsubscribe promise is the load-bearing half.)

## Storage tradeoff (name one, do not run both)
- **Supabase table `traject_waitlist` with insert-only RLS** (policy: `with check (true)` on INSERT for
  the anon role, no SELECT/UPDATE/DELETE for anon; reads only from service role or a gated admin view).
  Tradeoff: full control and UTM-level analytics, but you own double-opt-in, bounce handling and the
  export when the list grows. Use when the list feeds Stripe invites directly.
- **Form provider (Tally free / Loops / Formspree)**. Tradeoff: instant double-opt-in and delivery
  tooling, but the list lives outside the product DB and every export is manual. Use only while the
  list is under ~200 and unproven.

Recommendation for Traject at zero customers: Supabase insert-only, because the waitlist is the invite
source for a Stripe checkout and should live one query away from it.

## Confirmation email (DRAFT, never sent from this skill)
Subject: You're on the Traject list.
Body gist: what Traject is in one line ("a per-company, per-role interview room built from the actual
job posting"), what happens next (invite to build a room before general availability), and one ask
(reply with the role you're chasing). No outcome claims, no customer counts, no "join 500 candidates"
line - Traject has zero paying customers.

## Referral mechanic
"Share your link. Two friends who confirm, and you move up the invite list; five, and your first room
is free." Caps: the free-room grant is per-account, granted by an admin, and recorded. A referral
link must never auto-send on the referrer's behalf.

## Metric
North star: **waitlist-to-paid conversion within 30 days of invite** (TARGET 12%, unmeasured).
Leading: confirmed opt-ins per week and % who supply `next_interview_date` (urgency signal quality).
A raw signup count is not a metric unless the invite actually follows.

## Boundaries
Draft and audit only. No form is created, no table is created, no email is sent. The human types the
values and presses the buttons. Anything that publishes, sends or writes to a database is Gate-D.
