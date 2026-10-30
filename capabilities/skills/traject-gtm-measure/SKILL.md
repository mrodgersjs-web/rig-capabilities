---
name: traject-gtm-measure
description: "Traject GTM stage: measurement - the Traject funnel (visit, waitlist, invite, checkout, activated room), the definitions that make the numbers comparable, and the weekly read that turns each number into one action. Use when reporting Traject traction, defining a Traject metric, or running the weekly GTM review."
tags: [rig, gtm, measurement, analytics, funnel, traject]
metadata:
  tier: sub
  purpose: stage-skill
  category: gtm-sales-revenue
  family: traject-gtm
  built: "2026-09-28"
outcome: "One funnel with five named stages, each with a definition, a data source and an owner; a weekly read format where every number is paired with one action; and a rule that a metric nobody can act on is a dashboard, not a decision."
activation: "Load from traject-gtm when the stage is MEASURE, or when Traject traction, conversion, or a GTM metric is defined, reported, or questioned."
instruction: "Define before you count. Every metric names its event, source and denominator. Targets are labelled TARGET and never reported as results. No metric is published as a claim until its collection path has been proven end to end. Reporting is read-only; anything that goes outward is Gate-D."
applies_when:
  env: "read/report only"
  runtime: "Stripe (revenue), Supabase or form provider (waitlist), Vercel/analytics (traffic)"
  deps: "waitlist metric from traject-gtm-waitlist; activation event from traject-gtm-onboarding-activation"
  params: "window (week), stage"
  budget: "one weekly read"
  scale: "single product"
permissions:
  - fs.read
  - net.read
  - gate-d-required:publish
flow:
  - Route through traject-gtm first; JEV-first paragraph applies.
  - Load the funnel definitions below; refuse to report a stage with no proven collection path.
  - Produce the weekly read: number, source, delta, and exactly one action.
  - Label every target as TARGET and every unmeasured figure as UNVERIFIED.
done_when:
  - "cmd:bash capabilities/skills/traject-gtm/scripts/verify_paths.sh"
  - "Each reported number names its event, source and denominator"
  - "Every number in the read carries one action; a metric with no action is removed, not published"
  - "No target is presented as an achieved result"
---

# traject-gtm-measure

## JEV FIRST
Typed judgments here (is this metric real, is this a true outlier, is this claim publishable) go to
`/Users/rig128gb/.rig/bin/rig-s1gate check <rubric> --file <abs path> --subject <kind> --json` BEFORE
any frontier LLM call, decision id recorded. Fail closed: classifier down = DEFERRED. A metric is
never published outward without Gate-D, and a zero is never reported from an unproven collector -
an instrument that can only read zero looks exactly like rigour.

## The funnel (five stages, each with one definition)

| Stage | Event | Source | Denominator |
|---|---|---|---|
| Visit | landing page view | Vercel/analytics (UNVERIFIED until instrumented) | - |
| Waitlist | confirmed opt-in (double-opt-in if provider, consent row if Supabase) | waitlist store | visits |
| Invite | invite email sent and accepted | email log | confirmed opt-ins |
| Purchase | Stripe checkout completed for room_pass | Stripe | invites |
| Activated | first completed room (see traject-gtm-onboarding-activation) | product event log | purchases |

North star: **purchase -> activated within 7 days**, and **waitlist -> purchase within 30 days of
invite** (TARGET 12%, unmeasured). Both are targets; Traject has zero paying customers as of
2026-09-28, so every revenue line currently reads zero from a true zero, not from a broken pipe.

## Weekly read format
For each stage: the number, its source, the delta vs last week, and ONE action. Examples of actions:
"reorder the landing hero", "change who gets invited first", "fix the upload step". A number with no
available action is cut from the read rather than displayed - a score that only informs is a
dashboard, and Mike's rule is that a metric must drive a verb.

## Metric hygiene rules
- Derive every key in a metric from one source; two sources that disagree mean one is wrong, and the
  disagreement is reported, not averaged.
- A suspiciously round or suspiciously small number is re-measured by a second method before it is
  reported.
- Claim law: no result is published that no customer has produced. There are no Traject success
  stories to report, and none may be inferred from a waitlist count.

## Boundaries
Read and report only. Publishing a number externally (LinkedIn, site, deck) is Gate-D and requires
the collection path to have been proven, not just configured.
