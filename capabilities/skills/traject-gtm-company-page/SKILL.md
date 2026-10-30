---
name: traject-gtm-company-page
description: "Traject GTM stage: the LinkedIn company (business) page package for Traject - exact field drafts, logo and banner specs with Eden briefs, follower seeding within Mike's LinkedIn safety limits, and the ordered human clicks that create the page from his personal account. Use when creating, populating, or auditing the Traject LinkedIn Page."
tags: [rig, gtm, linkedin, company-page, brand, traject]
metadata:
  tier: sub
  purpose: stage-skill
  category: gtm-sales-revenue
  family: traject-gtm
  built: "2026-09-28"
outcome: "A page package where every LinkedIn field carries a clearly-marked DRAFT value, both brand assets exist as Eden briefs rather than agent-made art, the seeding plan respects the account-level daily ceilings, and page creation is a numbered Gate-D checklist Mike executes himself."
activation: "Load from traject-gtm when the stage is COMPANY-PAGE, or when any Traject LinkedIn Page field, asset, follower action, or admin step is drafted or reviewed."
instruction: "Draft field values as DRAFT text for Mike's approval, write Eden briefs for logo and banner instead of rendering them, keep the seeding plan inside the safety limits, and end in ordered steps Mike clicks. Nothing is typed into LinkedIn by the agent."
applies_when:
  env: "draft/audit only; LinkedIn UI is human-operated"
  runtime: "linkedin.com Pages (created from a personal account)"
  deps: "lv-profile references/company-page.md; eden-mcp for asset briefs; Mike's personal account with Page admin rights"
  params: "page name, lane (Traject product page, not RIG consulting page)"
  budget: "one page; one change set per month"
  scale: "single page, 1-2 employees listed at launch"
permissions:
  - fs.read
  - fs.write
  - browser.read
  - gate-d-required:publish
  - gate-d-required:page-create
  - gate-d-required:dm-send
flow:
  - Route through traject-gtm first; JEV-first paragraph applies.
  - Field drafts (Name, Tagline <=120 chars, About <=2000 chars, Website, Industry, size, Type, Specialties, CTA) each labelled DRAFT.
  - Logo and banner as Eden briefs with exact pixel specs; no agent-authored art.
  - Seeding plan capped at <=10 DMs/day, no mass connection invites, page invite-connections used sparingly and only to warm 1st-degree ties.
  - Ordered Gate-D steps for creation; the human clicks every one.
done_when:
  - "cmd:bash capabilities/skills/traject-gtm/scripts/verify_paths.sh"
  - "Every field value is labelled DRAFT and fits its character limit (tagline <=120, about <=2000)"
  - "Logo and banner exist as Eden briefs with dimensions named; no final asset is agent-rendered"
  - "Seeding plan states the daily ceiling and the no-mass-invite rule explicitly"
  - "Creation steps are ordered, each ending in a state the human can verify"
---

# traject-gtm-company-page

## JEV FIRST
Typed judgments here (is this About section admissible, does this tagline pass, is this claim
allowed) go to `/Users/rig128gb/.rig/bin/rig-s1gate check <rubric> --file <abs path> --subject <kind>
--json` BEFORE any frontier LLM call, decision id recorded. Fail closed: classifier down = DEFERRED.
An advisory PASS is never permission to create the Page or send an invite; that is Gate-D, and the
human performs the click.

## Field drafts (all DRAFT, held for Mike)
See the GTM package for the exact strings. Hard limits that bind every draft: Tagline <= 120 chars,
About <= 2,000 chars, Specialties <= 20 entries. Company name must be a real operating name; the
draft uses "Traject" with "A product of Rodgers Intelligence Group" carried in the About, and Mike
decides whether the legal entity name appears instead.

## Asset rule (binding)
Eden (eden.so) is the generator of record for brand imagery. Logo and banner are written as briefs
in `comms` form for Eden, never hand-authored or model-rendered here. If Eden is unavailable the
asset slot stays empty and the gap is reported; a placeholder made by the agent is a defect.

## Specs to put in the Eden brief
- Logo: 300x300 px minimum, square, PNG with transparent or solid background; renders at 56x56, so
  the mark must survive small display. No text smaller than ~24 px equivalent.
- Banner: 1128x191 px (1128x364 for the larger display variant on some surfaces); keep critical
  content inside the centre 1000x150 because member avatars and UI chrome overlap the edges.

## Follower seeding (inside Mike's stated limits)
- <= 10 DMs/day total across Mike's account activities, positive-only tone, no pitch in message one.
- No mass connection invites and no bulk "invite all connections" run. The Page's invite-connections
  feature is used in batches of ~10-20 warm 1st-degree ties who already work in hiring, coaching or
  senior career topics, and only after the page carries 3 posts of substance.
- The page is followed by Mike and by RIG first; a page with zero followers and zero posts cannot be
  seeded credibly.

## Ordered steps Mike clicks (Gate-D checklist)
1. From his personal account: For Business icon -> Create a LinkedIn Page -> Small business.
2. Name `Traject`; tagline pasted from the approved DRAFT; public URL claim checked for collisions
   (a name collision with an existing page is reported, never worked around).
3. Upload the Eden-rendered logo and banner (approved render only).
4. Paste About, Industry, size (2-10), Type (Privately held), Specialties, Website, CTA button.
5. Preview desktop + mobile before Publish. Publish is a Gate-D action; the page is not created by
   the agent under any circumstance.
6. After publish: verify by cold reload and an unauthenticated browser profile; then follow from
   personal + RIG accounts.

## Known hazards
- Page-admin surfaces have been observed redirecting to an unavailable state; probe before trusting a
  saved field (lv-profile lessons).
- A missing follower count on the read path is `unknown`, never zero.
- No metric in any field unless RIG measured it; with zero paying customers there is no testimonial,
  no user count and no outcome claim anywhere on the page.
