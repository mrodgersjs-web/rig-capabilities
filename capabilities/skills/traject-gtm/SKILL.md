---
name: traject-gtm
description: "META skill: the front door for Traject go-to-market (interview rooms for senior candidates, a product of RIG). Routes every Traject GTM job to exactly one stage sub-skill (waitlist, company-page, launch-content, pricing-offer, onboarding-activation, measure) and to the estate skills that carry the doctrine, with exact paths. JEV-first; Gate-D on anything published, sent, spent, or created on a platform. Use for any Traject marketing, sales, pricing, launch, LinkedIn Page, waitlist or traction request."
tags: [rig, meta-skill, gtm, traject, launch, linkedin]
metadata:
  tier: meta
  purpose: meta-skill
  category: gtm-sales-revenue
  family: traject-gtm
  built: "2026-09-28"
outcome: "A Traject GTM job routed to one stage sub-skill whose output is a draft or audit with evidence: findings with fixes, ICP verdicts with scores, a waitlist spec, a company-page package of DRAFT fields plus Eden briefs, content briefs rather than hand-authored posts, and a measured funnel - with nothing published, sent, deployed, or created on any platform."
activation: "Load first for any request that markets, sells, prices, launches, measures, or writes GTM copy for Traject, and whenever a Traject landing page, offer, waitlist, LinkedIn Page, or content plan is being drafted or audited."
instruction: "Name the stage, load exactly that stage sub-skill, use the estate skills it names at their exact paths, route typed judgments to rig-s1gate before any frontier call, and hold every outward action at Gate-D. Eden is the generator of record for LinkedIn copy and brand imagery: briefs here, never finished creative. Never imply a customer outcome - Traject has zero paying customers."
applies_when:
  env: "draft and audit only; this family never publishes"
  runtime: "Traject web product (https://cockpit-nine-black.vercel.app/), Stripe, LinkedIn Pages, Eden (eden.so)"
  deps: "rig-capabilities checkout; rig-s1gate available at /Users/rig128gb/.rig/bin/rig-s1gate; Eden for copy and imagery"
  params: "stage (waitlist | company-page | launch-content | pricing-offer | onboarding-activation | measure)"
  budget: "one stage per task step; one change set per week"
  scale: "one product, one company page, three priced products maximum"
permissions:
  - fs.read
  - fs.write
  - net.read
  - browser.read
  - gate-d-required:publish
  - gate-d-required:send
  - gate-d-required:spend
  - gate-d-required:deploy
  - gate-d-required:page-create
flow:
  - Name the stage the request belongs to; if it spans two, run them in dependency order (pricing-offer before launch-content before company-page before measure).
  - Load exactly one stage sub-skill from this family.
  - Inventory the decisions the task forces and route each: CODE -> JEV (rig-s1gate) -> SYSTEM 2 -> HUMAN (Gate-D).
  - Produce drafts and audits with evidence; label DRAFT, UNVERIFIED and TARGET honestly.
  - Hold every outward action at Gate-D; report per-surface impact and what did not change.
done_when:
  - "cmd:bash capabilities/skills/traject-gtm/scripts/verify_paths.sh"
  - "cmd:/Users/rig128gb/Developer/rig-capabilities/capabilities/skills/traject-gtm/scripts/verify_paths.sh --plant /nonexistent/traject-plant; test $? -eq 2"
  - "Every referenced path in the traject-gtm family resolves (the same script is the proof)"
  - "Typed judgments carry a rig-s1gate decision id or an explicit DEFERRED"
  - "Nothing was published, sent, deployed, or created on a platform by this family"
---

# traject-gtm

Tier-1 meta-skill for Traject go-to-market. Traject: a per-company, per-role interview room built
from the actual job posting - ownership map, regulation reality, numbers to prove, restraint story,
ruin and recall drills. $49 one-time Room Pass (Stripe live in code), plus active_search $49/month
and a Coach plan (3 seats + overage). **Zero paying customers on record: no claim of any customer
outcome is ever made, implied, or allowed into copy.**

## Hierarchy
1. **Meta-skill (this file)** - routes only.
2. **Stage sub-skills** (this family) - hold the Traject-specific procedure.
3. **Estate skills** - hold the doctrine. Load by exact path, one per task step.

## Stage routing (load exactly one)

| Stage | Sub-skill | Use when |
|---|---|---|
| WAITLIST | `traject-gtm-waitlist` | capture form, early access, confirmation email, referral |
| COMPANY-PAGE | `traject-gtm-company-page` | LinkedIn Page fields, logo/banner briefs, seeding, admin steps |
| LAUNCH-CONTENT | `traject-gtm-launch-content` | post briefs, pillars, hooks, amplification |
| PRICING-OFFER | `traject-gtm-pricing-offer` | prices, packages, guarantee, offer doc, pricing page |
| ONBOARDING-ACTIVATION | `traject-gtm-onboarding-activation` | onboarding steps, first session, activation metric |
| MEASURE | `traject-gtm-measure` | funnel, definitions, weekly read, traction claims |

## Estate skills (exact paths; load one per task step)
- `/Users/rig128gb/.aside/u/0/skills/user/when-selling-or-running-gtm/SKILL.md` - the tier-1 router for any GTM job; read `references/routing.md` when no stage fits.
- `/Users/rig128gb/.aside/u/0/skills/user/gtm-launch-readiness-checklist/SKILL.md` - go/no-go board before any launch.
- `/Users/rig128gb/.aside/u/0/skills/user/gtm-pricing-page-auditor/SKILL.md` - pricing-page friction audit.
- `/Users/rig128gb/.aside/u/0/skills/user/gtm-icp-fit-evaluator/SKILL.md` - criterion-by-criterion ICP verdicts.
- `/Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-money-pages/SKILL.md` - landing/money-page conversion framework (the retired pmm-service-landing-pages-cro skill is not on disk).
- Offer design and price setting: no skill on disk (pmm-productized-service-offers retired); use traject-gtm-pricing-offer.
- `/Users/rig128gb/.aside/u/0/skills/user/content-cta-optimizer/SKILL.md` - CTA copy for every surface.
- `/Users/rig128gb/.aside/u/0/skills/user/content-pillar-architect/SKILL.md` - pillar design with kill criteria.
- `/Users/rig128gb/.aside/u/0/skills/user/linkedin-viral/SKILL.md` - the LinkedIn front door; routes to the lv-* stages.
- `/Users/rig128gb/.aside/u/0/skills/user/lv-profile/SKILL.md` and `/Users/rig128gb/.aside/u/0/skills/user/lv-profile/references/company-page.md` - company-page material and Page procedure.
- `/Users/rig128gb/.aside/u/0/skills/user/lv-plan/SKILL.md` - calendar, cadence, idea sourcing.
- `/Users/rig128gb/.aside/u/0/skills/user/lv-gate/SKILL.md` - the single pre-publish gate for anything Mike sees as ready.
- `/Users/rig128gb/.aside/u/0/skills/user/eden-mcp/SKILL.md` - Eden, the generator of record for LinkedIn copy and brand imagery.
- Taki rules applied to LinkedIn: no skill on disk (rig-linkedin-taki retired); use /Users/rig128gb/.aside/u/0/skills/user/rig-website-taki/SKILL.md for the Taki method.
- MicroMagnet, Offer Doc, Hot Button Map: taki-doctrine is retired; see /Users/rig128gb/.aside/u/0/skills/user/rig-website-taki/SKILL.md.
- `/Users/rig128gb/.aside/u/0/skills/user/rig-website-taki/SKILL.md` - Taki rules for landing-page structure.
- `/Users/rig128gb/.aside/u/0/skills/user/s1gate/SKILL.md` - the governed Jev gate; the rubric path is `/Users/rig128gb/.rig/bin/rig-s1gate check <rubric> --file <abs path> --subject <kind> --json`.

## JEV FIRST (binding)
Once the mission is known, inventory the decisions it forces and route each, first match wins: CODE
(deterministic rule) -> JEV (rig-s1gate, decision id recorded) -> SYSTEM 2 (generation) -> HUMAN
(Gate-D: publish, send, spend, deploy, page creation). Typed judgments - hook ranking, post gate,
ICP fit, pricing verdict, claim admissibility, lane call - go to rig-s1gate BEFORE any frontier LLM
call. **Fail closed:** if rig-s1gate errors or the classifier is unreachable, report DEFERRED and
never guess a verdict locally. An advisory PASS is not permission to publish, send, spend, or deploy.

## Hard content law (from Mike's rules)
1. Eden generates LinkedIn copy and brand imagery. This family writes briefs. If Eden is down, the
   slot stays empty and that is reported.
2. Company-page field values are DRAFT text for Mike's approval; the human types every value.
3. No pop-culture mascot lanes (Birch / The Coach) on Traject.
4. Zero paying customers: no testimonials, no user counts, no outcome claims. Where proof would go,
   put the mechanism and the artifact.
5. LinkedIn safety limits hold: <= 10 DMs/day account-wide, no mass invites, positive-only comments.
6. Nothing here publishes, sends, deploys, spends, or creates an account. Every one of those is
   Gate-D, and the payload with exact values is shown to Mike before it is executed.

## Done test
`traject-gtm/scripts/verify_paths.sh` exits 0 only when every path referenced across the traject-gtm
family resolves on disk; `--plant broken_path` must exit 2. A green that cannot go red is theater.
