---
name: traject-gtm-launch-content
description: "Traject GTM stage: the launch content engine - Eden briefs for the first five LinkedIn posts (angle, the proof each rests on, CTA), the content pillars that keep the feed coherent, the gate every draft passes before Mike sees it, and the amplification plan. Use when planning, brief-writing, gating, or scheduling Traject launch content."
tags: [rig, gtm, content, linkedin, eden, traject]
metadata:
  tier: sub
  purpose: stage-skill
  category: gtm-sales-revenue
  family: traject-gtm
  built: "2026-09-28"
outcome: "Five post briefs an Eden session can turn into drafts today, each naming its angle, the evidence it stands on, and one CTA - plus a pillar map, a pre-publish gate run, and an amplification plan that never fabricates a customer result."
activation: "Load from traject-gtm when the stage is LAUNCH-CONTENT, or when a Traject post, brief, pillar, hook set, or content calendar is being drafted or reviewed."
instruction: "Write briefs, not finished posts - Eden is the generator of record for LinkedIn copy and brand imagery. Ground every brief in a mechanism or a documented fact. Route hook ranking and post-gate judgments to rig-s1gate before any frontier generation. Hold every publish at Gate-D."
applies_when:
  env: "draft/audit only; nothing posts"
  runtime: "Eden (eden.so) as copy generator; LinkedIn as the eventual surface"
  deps: "lv-plan, lv-gate, lv-hooks via linkedin-viral; content-pillar-architect; content-cta-optimizer"
  params: "lane (RIG B2B / product lane - NO mascot lanes), goal (waitlist signups), window (launch 14 days)"
  budget: "5 launch briefs + 1 reserve; one gate run per draft"
  scale: "1-2 posts/week on the company page, Mike's personal lane kept separate"
permissions:
  - fs.read
  - fs.write
  - net.read
  - gate-d-required:publish
  - gate-d-required:send
flow:
  - Route through traject-gtm first; JEV-first paragraph applies.
  - Set pillars (mechanism, senior-candidate reality, build-in-public, offer) with kill criteria.
  - Write five briefs: angle, proof it rests on, CTA. No finished copy.
  - Route hook choice to rig-s1gate; DEFERRED means no hook is chosen.
  - Gate any draft through lv-gate before it reaches Mike as "ready".
  - Amplification plan (personal account reshares, comment lanes) capped by the account ceilings.
done_when:
  - "cmd:bash capabilities/skills/traject-gtm/scripts/verify_paths.sh"
  - "Five briefs exist, each with angle + named proof + exactly one CTA"
  - "No brief asserts a customer outcome; zero paying customers is stated where social proof would normally go"
  - "Hook selection carries a recorded JEV decision id or an explicit DEFERRED"
  - "No post is published or scheduled by this skill"
---

# traject-gtm-launch-content

## JEV FIRST
Hook ranking, brief quality, lane fit and post-gate verdicts go to
`/Users/rig128gb/.rig/bin/rig-s1gate check <rubric> --file <abs path> --subject <kind> --json` BEFORE
any frontier LLM call, decision id recorded. Fail closed: classifier down = DEFERRED and the brief is
not promoted. An advisory PASS is never permission to post; publishing is Gate-D.

## Pillars (each with a kill criterion)
1. **Mechanism** - what Traject actually does (ownership map, regulation reality, numbers to prove,
   restraint story). Kill if it drifts into generic interview tips.
2. **Senior-candidate reality** - why prep breaks at Director/VP/C-level rooms. Kill if it becomes
   complaints about hiring.
3. **Build-in-public** - the product being built, with receipts (screens, spec text). Kill if it
   becomes founder diary.
4. **Offer** - the Room Pass, the waitlist, the invite. Max 1 in 4 posts.

## Hard content law (from Mike's rules)
- No pop-culture mascot lanes (Birch / The Coach) on Traject. Ever.
- No claim about an outcome no customer has had. Traject has zero paying customers on record: there
  are no testimonials, no "candidates landed offers", no user counts. Where proof would go, use the
  mechanism and the built artifact instead.
- Eden generates the copy and the imagery. This skill writes briefs. If Eden is down, the slot stays
  empty and that is reported.
- Comments on other people's posts stay positive-only; the comment lane is not a debate lane.

## The five launch briefs
Each brief = angle / proof it rests on / CTA. Full text in the GTM package (section 4). Shape:

| # | Angle | Proof it rests on | CTA |
|---|---|---|---|
| 1 | The problem, named precisely | the room concept and the four moves | join the waitlist |
| 2 | Why generic prep breaks at senior level | the ownership/regulation analysis on the page | read the landing |
| 3 | Build-in-public: the room, from the posting | shipped product surface (landing, onboarding flow) | waitlist |
| 4 | The restraint story idea | mechanism text, not a testimonial | waitlist |
| 5 | The offer, plainly | $49 one-time Room Pass, what it contains | waitlist / buy when live |

## Gate before Mike sees a draft
Run lv-gate: JEV rubrics, the executable post gate, an independent critic pass, anti-slop, and the
claim-hygiene check (no unearned outcome claims). A draft that fails goes back for rewrite, not to
Mike with a caveat.

## Amplification
Mike's personal account may reshare company-page posts after they are live (his call, Gate-D). DM
amplification is capped at <= 10 DMs/day account-wide and positive-only. No engagement pods, no
mass invites, no bought engagement - these are standing prohibitions in the LinkedIn lane.
