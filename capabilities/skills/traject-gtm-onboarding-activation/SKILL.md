---
name: traject-gtm-onboarding-activation
description: "Traject GTM stage: activation - the four-step onboarding (Goal, Sources, Crew, First session), the first-room moment that must land in one sitting, and the activation metric that separates a signup from a user. Use when changing, auditing, or measuring Traject onboarding or first-run experience."
tags: [rig, gtm, activation, onboarding, product, traject]
metadata:
  tier: sub
  purpose: stage-skill
  category: gtm-sales-revenue
  family: traject-gtm
  built: "2026-09-28"
outcome: "An activation definition with one measurable event, a step-by-step onboarding audit with the friction named per step, and the first-session design that gets a buyer to a finished room before the novelty wears off."
activation: "Load from traject-gtm when the stage is ONBOARDING-ACTIVATION, or when a Traject onboarding step, first-run flow, empty state, or activation metric is designed or reviewed."
instruction: "Define the activation event before touching screens. Audit each onboarding step for the question it asks and the cost of answering it. Ship nothing that sends email, data, or invites on a user's behalf without an explicit human action. Route UI-quality judgments through the design gate; anything user-visible ships at Gate-D."
applies_when:
  env: "draft/audit only for GTM work; product changes live in the app repo and its own harness"
  runtime: "Traject web app (Next.js/Vercel at https://cockpit-nine-black.vercel.app/)"
  deps: "Traject onboarding: 4 steps Goal -> Sources -> Crew -> First session; Lucy-order room template (Run of Show, DECISIONS, debrief); Traject Coach drill /20"
  params: "segment (candidate, coach), step id"
  budget: "one change set per release"
  scale: "single-product funnel"
permissions:
  - fs.read
  - fs.write
  - net.read
  - gate-d-required:deploy
  - gate-d-required:email-send
flow:
  - Route through traject-gtm first; JEV-first paragraph applies.
  - Define the activation event (named below) and its measurement path.
  - Audit the four steps: question asked, cost to answer, exit risk, and the fix.
  - Design the first-session outcome: one finished room, shareable, in one sitting.
  - Report per-surface impact and name what did not change.
done_when:
  - "cmd:bash capabilities/skills/traject-gtm/scripts/verify_paths.sh"
  - "Activation event named as one observable product event, with its query or log line"
  - "Each onboarding step carries a friction note and a fix"
  - "No user-visible change is claimed shipped without a deployed URL or artifact"
---

# traject-gtm-onboarding-activation

## JEV FIRST
Typed judgments here (does this step pass, is this empty state acceptable, is this activation event
the right one) go to `/Users/rig128gb/.rig/bin/rig-s1gate check <rubric> --file <abs path> --subject
<kind> --json` BEFORE any frontier LLM call, decision id recorded. Fail closed: classifier down =
DEFERRED. An advisory PASS is never permission to deploy; deployment is Gate-D.

## Activation event (canonical)
**Activation = the first completed room** - a room built from one job posting that contains all four
sections (ownership map, regulation reality, numbers to prove, restraint story) and at least one
drill run. Not "signed up", not "created a room". If the funnel cannot observe this event today, the
gap is the first item to fix, because every GTM number downstream of it is unmeasurable.

## The four onboarding steps - audit shape
| Step | Question it asks | Cost to the user | Friction risk | Fix direction |
|---|---|---|---|---|
| Goal | what role are you chasing | low | vague goals stall later | offer 3 preset shapes |
| Sources | paste posting + resume/LinkedIn | medium (paste + upload) | resume upload anxiety | allow paste-text; say what happens to the file |
| Crew | who else is in the room | low but undefined | "Crew" is jargon; users do not know what it earns them | reframe as "who reviews your room" with a skip |
| First session | start the first drill | high (novelty moment) | a long first drill kills the sitting | time-box the first drill to ~10 minutes |

The landing page shows a 4-step story ("paste a URL, add your context, get your room, share it")
that does not match the product's Goal -> Sources -> Crew -> First session; the two stories must be
made to agree before launch, because message match is the first conversion lever.

## First-session design
The payoff in one sitting: a finished room, a printed/shared link, and one drill graded. The
Traject Coach drill (/20 across five criteria) is the moment the product proves itself; nothing may
be inserted before it that delays it. The follow-up draft, salary script and ask live after the
debrief, never before.

## Claim law
No onboarding copy may promise an outcome ("walk in and win the room"). Describe what the product
does. Traject has zero paying customers: no step may cite user counts or results.

## Boundaries
This skill drafts and audits. Product code changes are executed inside the app's own build harness
(`~/Developer` worktree Mike named), and anything deployed, emailed, or sent on a user's behalf is
Gate-D. Report per-surface impact and name what did not change.
