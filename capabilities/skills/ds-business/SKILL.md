---
name: ds-business
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate
  (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict.
  Main skill of design-studio-os for design business: Run the practice: pricing, proposals, client process and boundaries. 60 laws, 30
  looks-like/does-not pairs distilled from the RIG design YouTube corpus (top-10 subscribed channels
  weighted), every law cited CLAIM(<videoId>@mm:ss). Use when pricing, proposals, client process or scope boundaries are the question.
tier: main
parent: design-studio-os
activation: "Load at the start of any task that decides design business. Entered by the /design-studio command through design-studio-os, by ds-strategist, or by the ds-gate-* harness that names this stage."
owner: rig-intelligence
status: Stable
acl: internal
outcome: "design-ux: a priced scope with boundaries named and a process the client can follow, with citations or labeled own reasoning on every judgment"
done_when:
  - cmd:python3 tools/claims_check.py studio-skills/skills/ds-business/SKILL.md
  - cmd:python3 tools/check_family.py
quality_floor: 0.6
---

# Design business

JEV FIRST, and it binds every task under this skill: an agent whose only context is this excerpt
sends semantic triage, routing and classification to the rig-s1gate Jev path BEFORE any frontier LLM call
(`~/.rig/bin/rig-s1gate check plan.readiness --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`;
nearest existing rubric: plan.readiness, advisory until calibrated). When the classifier is unavailable: DEFERRED,
never a guessed verdict. A required signal passes only above 0.9.

## Load surface

Load this skill FIRST, before any design decision, whenever the job touches design business. It is an
always-loaded task-start surface, not a deep reference an agent must already know about: the `/design-studio`
command loads `design-studio-os`, which names this skill in its stage routes table; `when-designing-interfaces`
and `when-designing-websites` route design work to that front door; and the meta agent `ds-director` dispatches
`ds-strategist`, which loads this skill before its first action. The stage's gate harness
(`ds-gate-craft`, `ds-gate-brief`, `ds-gate-critique` or `ds-gate-ship`) names these requirements, so a session
running that harness loads this file to pass its gate. Paths are relative to `~/Developer/rig-design-studio-os`.

## When to use

Trigger words: "price this", "quote", "client process", "proposal", "retainer". Inside a build this stage runs after the stage that feeds it and
before ds-discovery.

## Inputs and output contract

Inputs: the scope, the client type, the market.
Output: a priced scope with boundaries named and a process the client can follow.

## Procedure

1. Business offer diagnosis: what to sell, what to refuse, and which tradeoff wins (see references/business-offer-diagnosis.md).
2. Business scope and proposal: scoped yes, templated proposal, deposit, discovery metrics (see references/business-scope-and-proposal.md).
3. Business client presentation: live reveal structure from brief to next steps (see references/business-client-presentation.md).
4. Business onboarding revisions: asset deadlines, revision caps, project folder, kickoff direction check (see references/business-onboarding-revisions.md).
5. Business launch and retain: launch checks, handoff docs, and the follow-up that creates the next job (see references/business-launch-and-retain.md).
6. Business price and scale: platform niche, case-study portfolio, stage pricing, channel order, hire order. Laws 59, 60, plus the price and hire rows in Decision tables (see references/business-price-and-scale.md).
7. Check the decision tables below for the choices this stage forces.
8. Run the anti-patterns as a final sweep; each surviving one becomes a finding in `ds-critique`.
9. Cite every load-bearing choice (CLAIM copied from this file); label the rest own reasoning.

## Core laws (load-bearing subset)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 8 | Pick one loud element. If the headline, subhead, and button all shout, none of them win. The same rule answers "make everything bold." | Self-Made Web Designer, CharliMarieTV | CLAIM(WxZHUe8mvhU@04:05), CLAIM(WxZHUe8mvhU@04:15), CLAIM(vNL4PS1KCHY@02:09), CLAIM(vNL4PS1KCHY@02:26) | consensus |
| 12 | State the reason for each choice in the review, using the client's own brief words. Silence is what turns a normal note into a fight. A cold outreach recording uses the same shape: who you are, one thing you liked, the critique, then how to reply. | Self-Made Web Designer, Flux Academy, CharliMarieTV, Will Paterson | CLAIM(WxZHUe8mvhU@05:48), CLAIM(WxZHUe8mvhU@06:07), CLAIM(_WyYr1p1XVk@00:16), CLAIM(_WyYr1p1XVk@12:54), CLAIM(Y-JFVdiimS4@07:59), CLAIM(Y-JFVdiimS4@08:17), CLAIM(vNL4PS1KCHY@00:23), CLAIM(vNL4PS1KCHY@04:45), CLAIM(GzTWvwtJVRU@06:40), CLAIM(GzTWvwtJVRU@07:30) | consensus |
| 14 | If your gut says decline, decline. Need for the fee is not a reason to take a bad-fit project. Pass fast when budget, timing, and portfolio value are all weak. | Self-Made Web Designer, Flux Academy | CLAIM(WxZHUe8mvhU@06:39), CLAIM(WxZHUe8mvhU@06:44), CLAIM(tvKZEhUg3Eg@03:47), CLAIM(tvKZEhUg3Eg@03:56) | consensus |
| 19 | Discovery must answer three things: what you are building, who it is for, and which success measures the client will use later. Also name the point of contact, who gives feedback, and how much creative freedom you actually have. | Jesse Showalter, Self-Made Web Designer, Flux Academy | CLAIM(3TIYR3ekvjI@02:05), CLAIM(3TIYR3ekvjI@02:13), CLAIM(O96t2rfwmak@05:33), CLAIM(O96t2rfwmak@05:55), CLAIM(tvKZEhUg3Eg@01:12), CLAIM(tvKZEhUg3Eg@01:47), CLAIM(tvKZEhUg3Eg@02:59) | consensus |
| 21 | Do not ask a client to pick from mood boards alone. Translate each direction into a page-like sample (type, color, hero, buttons) before any full design. Two or three directions, each with a board plus a hero, is enough to choose. | Jesse Showalter, Self-Made Web Designer, Flux Academy | CLAIM(3TIYR3ekvjI@04:47), CLAIM(3TIYR3ekvjI@05:09), CLAIM(O96t2rfwmak@08:07), CLAIM(O96t2rfwmak@08:41), CLAIM(tvKZEhUg3Eg@07:39) | consensus |
| 30 | Warn that a first look at a mark feels stark, especially in black and white. Attachment comes after seeing it in use. Say plainly that a first look is not supposed to wow them. | Flux Academy, Will Paterson | CLAIM(_WyYr1p1XVk@05:12), CLAIM(_WyYr1p1XVk@05:33), CLAIM(GzTWvwtJVRU@02:11), CLAIM(GzTWvwtJVRU@02:58) | consensus |
| 31 | Make relevant applications the longest section. Tie each mock back to a brief point while people are looking at the work, not at bullets. Do not show an option you do not want them to pick. | Flux Academy, Will Paterson | CLAIM(_WyYr1p1XVk@07:30), CLAIM(_WyYr1p1XVk@08:07), CLAIM(GzTWvwtJVRU@05:59), CLAIM(GzTWvwtJVRU@09:05) | consensus |
| 36 | Put delay consequences in the terms before kickoff: a fee for late content, and a restart fee if silence puts the project on hold. A weekly fee for a late approval that blocks the build is the same idea. | Self-Made Web Designer, Flux Academy | CLAIM(O96t2rfwmak@01:05), CLAIM(O96t2rfwmak@01:15), CLAIM(tvKZEhUg3Eg@06:27) | consensus |
| 1 | Get layout, color, type, and imagery solid before you add motion. Motion on a weak base reads as decoration. | Self-Made Web Designer | CLAIM(WxZHUe8mvhU@00:14), CLAIM(WxZHUe8mvhU@00:37) | single-source |
| 2 | Treat the words as the main closer. The design job is to keep attention on those words, not to compete with them. | Self-Made Web Designer | CLAIM(WxZHUe8mvhU@01:00), CLAIM(WxZHUe8mvhU@01:07) | single-source |
| 3 | Start sparse. Cut the palette and the element count, then add pieces back only when this project needs them. | Self-Made Web Designer | CLAIM(WxZHUe8mvhU@01:23), CLAIM(WxZHUe8mvhU@01:30) | single-source |
| 4 | Visual taste is not the fee. Paid designers also explain their value, run a clean process, and decode vague client requests. | Self-Made Web Designer | CLAIM(WxZHUe8mvhU@01:35), CLAIM(WxZHUe8mvhU@01:46) | single-source |

The full set of 60 laws lives in the sub-skills, plus 26 ungrouped laws below.

## Sub-skills

| sub-skill | file | owns |
|---|---|---|
| business-offer-diagnosis | references/business-offer-diagnosis.md | 5 laws |
| business-scope-and-proposal | references/business-scope-and-proposal.md | 5 laws |
| business-client-presentation | references/business-client-presentation.md | 9 laws |
| business-onboarding-revisions | references/business-onboarding-revisions.md | 10 laws |
| business-launch-and-retain | references/business-launch-and-retain.md | 3 laws |
| business-price-and-scale | references/business-price-and-scale.md | 2 laws |

## Further laws (not yet grouped into a sub-skill)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 1 | Get layout, color, type, and imagery solid before you add motion. Motion on a weak base reads as decoration. | Self-Made Web Designer | CLAIM(WxZHUe8mvhU@00:14), CLAIM(WxZHUe8mvhU@00:37) | single-source |
| 3 | Start sparse. Cut the palette and the element count, then add pieces back only when this project needs them. | Self-Made Web Designer | CLAIM(WxZHUe8mvhU@01:23), CLAIM(WxZHUe8mvhU@01:30) | single-source |
| 5 | Use composition and color rules as a start. Stop following a rule the moment it blocks a result your eye already trusts. | Self-Made Web Designer | CLAIM(WxZHUe8mvhU@02:35), CLAIM(WxZHUe8mvhU@02:51) | single-source |
| 6 | Design each breakpoint for its own problems. Do not treat one device as the whole brief. | Self-Made Web Designer | CLAIM(WxZHUe8mvhU@03:22), CLAIM(WxZHUe8mvhU@03:28) | single-source |
| 7 | Make the first screen do four jobs fast: stop the visitor, name what the site is, create a reason to act, and show the next step. | Self-Made Web Designer | CLAIM(WxZHUe8mvhU@03:47), CLAIM(WxZHUe8mvhU@03:51) | single-source |
| 8 | Pick one loud element. If the headline, subhead, and button all shout, none of them win. The same rule answers "make everything bold." | Self-Made Web Designer, CharliMarieTV | CLAIM(WxZHUe8mvhU@04:05), CLAIM(WxZHUe8mvhU@04:15), CLAIM(vNL4PS1KCHY@02:09), CLAIM(vNL4PS1KCHY@02:26) | consensus |
| 10 | Borrow a pattern that already works, then adapt it to this client's context. Do not spend the budget inventing a new pattern. | Self-Made Web Designer | CLAIM(WxZHUe8mvhU@05:00), CLAIM(WxZHUe8mvhU@05:09) | single-source |
| 13 | Before you call a flow done, watch someone outside the project try the task (sign up, or a fake purchase) and fix what they miss. | Self-Made Web Designer | CLAIM(WxZHUe8mvhU@06:18), CLAIM(WxZHUe8mvhU@06:28) | single-source |
| 15 | Do not treat solo grinding as a virtue. Keep people around you who can help when a project stalls. | Self-Made Web Designer | CLAIM(WxZHUe8mvhU@06:55), CLAIM(WxZHUe8mvhU@07:09) | single-source |
| 21 | Do not ask a client to pick from mood boards alone. Translate each direction into a page-like sample (type, color, hero, buttons) before any full design. Two or three directions, each with a board plus a hero, is enough to choose. | Jesse Showalter, Self-Made Web Designer, Flux Academy | CLAIM(3TIYR3ekvjI@04:47), CLAIM(3TIYR3ekvjI@05:09), CLAIM(O96t2rfwmak@08:07), CLAIM(O96t2rfwmak@08:41), CLAIM(tvKZEhUg3Eg@07:39) | consensus |
| 22 | If reviews keep looping on abstract artifacts (sitemap, wireframe, mood board), deliver a more concrete sample earlier. Clarity up front shortens the calendar. | Jesse Showalter | CLAIM(3TIYR3ekvjI@05:37), CLAIM(3TIYR3ekvjI@05:45) | single-source |
| 23 | Lock palette and type from the first real feedback, then keep later pages inside that system so the site can grow. | Jesse Showalter | CLAIM(3TIYR3ekvjI@07:39), CLAIM(3TIYR3ekvjI@08:43) | single-source |
| 24 | When the same person designs and builds, skip a separate handoff packet. The usual bottleneck is translating intent to another builder. | Jesse Showalter | CLAIM(3TIYR3ekvjI@09:26), CLAIM(3TIYR3ekvjI@09:41) | single-source |
| 25 | Promise a smaller scope than you can finish, then spend leftover days on extra pages or motion only after the agreed work is done. | Jesse Showalter | CLAIM(3TIYR3ekvjI@12:22), CLAIM(3TIYR3ekvjI@12:32) | single-source |
| 41 | Name folders for a later you who has many more jobs: medium, then project, then a file name that states the brief. | CharliMarieTV | CLAIM(pKquP_em-Bs@00:23), CLAIM(pKquP_em-Bs@00:48) | single-source |
| 42 | Number versions (V1, V2). Never label a file final. Keep only the latest outside a process folder; drag the previous latest in when you bump the number. | CharliMarieTV | CLAIM(pKquP_em-Bs@02:12), CLAIM(pKquP_em-Bs@02:28), CLAIM(pKquP_em-Bs@02:45) | single-source |
| 43 | Inside each project, split reference images, client drafts, and final exports into their own folders, and prefix those folder names so they sort to the top. | CharliMarieTV | CLAIM(pKquP_em-Bs@01:32), CLAIM(pKquP_em-Bs@01:56) | single-source |
| 46 | On the first call, the client talks. Ask about the business, what they want, what the current site frustrates, and what past freelancers got wrong. | Self-Made Web Designer | CLAIM(T5JglDcd54A@00:53), CLAIM(T5JglDcd54A@01:10) | single-source |
| 48 | Raise fidelity in steps. Do not open the homepage design before a sitemap and a wireframe the client has seen. | Self-Made Web Designer | CLAIM(T5JglDcd54A@03:35), CLAIM(T5JglDcd54A@03:59) | single-source |
| 49 | Keep early wireframes free of type and layout choices. A placeholder font that gets approved becomes a demand later. | Self-Made Web Designer | CLAIM(T5JglDcd54A@04:34), CLAIM(T5JglDcd54A@05:08) | single-source |
| 50 | Spend the design hours on the homepage, then reuse those sections on inner pages instead of inventing a new system per page. | Self-Made Web Designer | CLAIM(T5JglDcd54A@05:57), CLAIM(T5JglDcd54A@06:06) | single-source |
| 54 | On a public cover, show a customer using the offer, plus a headline that names the change you create or the problem you remove. | Wes McDowell | CLAIM(junHy_vvoXU@03:01), CLAIM(junHy_vvoXU@03:17) | single-source |
| 55 | Write the short public description as what you do plus two or three concrete benefits, inside the character cap. | Wes McDowell | CLAIM(junHy_vvoXU@04:50), CLAIM(junHy_vvoXU@04:59) | single-source |
| 56 | About copy states the customer's problem, your fix, then one short block per top benefit. Do not spend it on company history. | Wes McDowell | CLAIM(junHy_vvoXU@12:50), CLAIM(junHy_vvoXU@13:06) | single-source |
| 57 | Pin one value post at the top (a quote request or a free resource) and point it at one action. Hide setup clutter from the public timeline. If nobody is watching the inbox, set an automatic reply that names the next step. | Wes McDowell | CLAIM(junHy_vvoXU@16:15), CLAIM(junHy_vvoXU@18:02), CLAIM(junHy_vvoXU@21:02), CLAIM(uVSdCJCvzag@16:29), CLAIM(uVSdCJCvzag@23:53) | single-source |
| 58 | Give every offer an end date. A discount with no deadline does not create a reason to act today. | Wes McDowell | CLAIM(junHy_vvoXU@15:10), CLAIM(junHy_vvoXU@15:18) | single-source |

## Looks like / does not (strongest pairs)

| looks like | does not | why | citation |
|---|---|---|---|
| 1 | Basics locked, then motion added only where it helps | Animation on a site that fails layout, color, type, or images | Motion cannot cover a weak foundation |
| 2 | Words lead; design keeps eyes on them | Decoration that pulls attention off the offer | Copy is the closer; design is the frame |
| 3 | Small palette, elements added only when needed | Many colors and a new gadget every scroll | Noise hides the one thing that must be seen |
| 4 | One loud element, the rest quiet | Headline, subhead, and button at the same weight | If everything is important, nothing is |
| 5 | Borrowed pattern, refit to this client | A copied site that still belongs to someone else | Context is the difference between reference and theft of fit |
| 6 | Problem diagnosed, then the right next step sold | A website sold because that is the only offer | Consultants get paid for the diagnosis, not the pixels |

Full pair set: the ds-exemplars skill and studio-exemplars/pairs/business/.

## Decision tables

| decision | option A | option B | pick A when | pick B when | citation |
|---|---|---|---|---|---|
| Device priority | Design each breakpoint for its own job | Mobile-only first, desktop as a shrink | The client's real traffic and tasks differ by screen | You have measured that this audience almost only uses one device | CLAIM(WxZHUe8mvhU@03:22) |
| Deadline vs craft | Shrink the page count, keep exploration | Skip mood boards and style samples to go faster | The date is fixed and quality still has to hold | Never, in this corpus. Speed is scope, not skipped stages | CLAIM(3TIYR3ekvjI@04:07) |
| Reveal format | Live presentation with commentary | Email the deck and wait | It is a first look, a big idea, or a brand/site reveal | It is a small check-in or a minor edit | CLAIM(_WyYr1p1XVk@00:43) |
| Who builds | Designer builds the site | Separate developer handoff | The tool lets the designer publish without a translation layer | The build needs engineering the designer cannot own | CLAIM(3TIYR3ekvjI@09:41) |
| Extra ideas | Show rough stretch ideas after the asked-for work | Build extras into the base delivery | You want future work and talking points, without hurting margin | The extra is already in the signed scope | CLAIM(_WyYr1p1XVk@10:32) |
| Late assets | Fee and restart terms, named up front | Keep asking nicely | You have explained the terms before kickoff | You never wrote the consequence, so a surprise fee is a fight | CLAIM(O96t2rfwmak@01:15) |
| Wireframe fidelity | Section topics only, no type or layout | Gray-box wireframe that implies images, icons, and a font | A past placeholder font got approved and then demanded | You need the client to react to structure, and you will not show type | CLAIM(T5JglDcd54A@04:17) |
| Niche | Platform niche, many industries, filter on the work page | Industry niche (sites only for one trade) | You want a wide net and case studies you can filter | You will spend the next year building only inside one category and you are sure of it | CLAIM(Gx1bopqOfMU@02:51) |
| First clients | Warm job boards, then referrals, then short cold notes | Cold outreach as the permanent engine | You are under about ten clients and people are already looking | Warm and referral volume already covers the month | CLAIM(Gx1bopqOfMU@11:10) |
| First hire | A designer who can take your delivery seat | A junior or an assistant | You are the bottleneck on every pixel and call | Delivery is already covered and the next gap is a specialist the work is already paying for | CLAIM(Gx1bopqOfMU@17:52) |
| Domain | Short branded .com; tweak the name if the exact .com is taken | New extension (.net, .co, or a novelty ending) as the first fallback | You can still say the name out loud and people will type .com | The branded .com is impossible and a .net or .co is the third choice, not the second | CLAIM(RUFV897DAGg@02:40), CLAIM(RUFV897DAGg@03:04) |
| Keyword in the name | One broad keyword inside a brand name | The whole search phrase as the domain | One word still helps recall and search | The phrase is so long people will not type it or trust it | CLAIM(RUFV897DAGg@05:25), CLAIM(RUFV897DAGg@06:01) |
| Take the job | Budget and timing are solid, and you have assets or creative freedom | Budget, timing, and portfolio value are all weak | The output will be something you can stand behind | It fails the four-bucket sort; pass | CLAIM(tvKZEhUg3Eg@03:27) |
| Cold outreach recording | Five or six specific notes, sent the same day | A long audit you polish for days | You need volume while you are starting | The prospect already asked for a paid review | CLAIM(Y-JFVdiimS4@03:38), CLAIM(Y-JFVdiimS4@09:42) |

## Anti-patterns

- Shipping motion before layout, color, type, and imagery are solved. CLAIM(WxZHUe8mvhU@00:37)
- Eight-color palettes and a new element every few scrolls. CLAIM(WxZHUe8mvhU@01:23)
- Selling a website when the real problem is something else. CLAIM(WxZHUe8mvhU@05:27)
- Getting angry at revisions you never explained. CLAIM(WxZHUe8mvhU@05:54)
- Taking a project your gut already rejected. CLAIM(WxZHUe8mvhU@06:39)
- Asking a client to approve a mood board with no page context. CLAIM(3TIYR3ekvjI@04:55)
- Promising stretch pages inside the base timeline. CLAIM(3TIYR3ekvjI@12:32)
- Emailing a big reveal and hoping the framing survives. CLAIM(_WyYr1p1XVk@00:43)
- plus 19 more in references/<sub-skill>.md files

## Creator disagreements (stated, not resolved)

- Device order: Self-Made Web Designer (2026) says stop defaulting to mobile-first and design each screen size for its own problems, and says the "most traffic is mobile" line has not held for his website clients. CLAIM(WxZHUe8mvhU@02:56). No other video in the first four argues the opposite with a measured counter. Hold this as single-source until later videos speak.
- Wireframes: Jesse Showalter (2025) says do not draw wireframes from scratch; generate them and move on. CLAIM(3TIYR3ekvjI@07:04). Flux Academy (2022) still lists wireframes as a useful thing to show in the process section of a presentation. CLAIM(_WyYr1p1XVk@04:26). Self-Made Web Designer (2025) still requires a sitemap and a wireframe before homepage design, but wants that wireframe so plain it cannot imply a font. CLAIM(T5JglDcd54A@03:59), CLAIM(T5JglDcd54A@04:34). Not a hard conflict: generate structure fast, show it, and keep type out of it.
- Niche: Sam Crawford (2026) says niche by platform and serve many industries, and treats industry-only niches as the narrower path. CLAIM(Gx1bopqOfMU@02:51). No other video in the first eight argues the opposite with a measured counter. Hold until later videos speak.
- Job boards: Sam Crawford (2026) says boards are the right first-client channel and that advice to avoid them is wrong for beginners. CLAIM(Gx1bopqOfMU@12:00). No counter in this set yet.
- Revision window: Self-Made Web Designer sets 48 hours in one 2025 video and 24 hours in another. CLAIM(O96t2rfwmak@02:32), CLAIM(T5JglDcd54A@03:04). Same creator, two windows. The checkable rule is: pick one window, write it, and treat silence as approval.
- How the first clients arrive: Sam Crawford (2026) puts job boards first for beginners and treats cold notes as a short-term lever. CLAIM(Gx1bopqOfMU@11:10). Flux Academy (2022) teaches Loom critiques of local sites as the beginner motion. CLAIM(Y-JFVdiimS4@00:00). Flux Academy (2025) says this creator does no outreach and that almost all leads arrive from content and the network. CLAIM(tvKZEhUg3Eg@00:36). Read them as stages, not as one rule: cold recordings while you have no proof, boards if people are already hiring, inbound once the content exists.

## Creator claims (unverified)

- About 85% of visitors care only about the top of the homepage. Self-Made Web Designer, 2026. CLAIM(WxZHUe8mvhU@03:35)
- A widely repeated "about 90% of traffic is mobile" figure has not matched this creator's website clients. Treat it as a claim to measure, not a default. CLAIM(WxZHUe8mvhU@03:02)
- Nine times out of ten, a gut-reject project is not worth the fee. CLAIM(WxZHUe8mvhU@06:50)
- A templated proposal can be customized in a 45 to 60 minute scoping call. CLAIM(3TIYR3ekvjI@01:55)
- An AI pass on a discovery doc was described as almost fully aligned with what the client wanted, in about 35 minutes. CLAIM(3TIYR3ekvjI@03:08)
- One client site went from a four-page plan to roughly nine or ten pages, design and build inside about a week, with the agreed work done in about four days. CLAIM(3TIYR3ekvjI@12:22), CLAIM(3TIYR3ekvjI@14:22)
- Presentation time split attributed to George Lois: 1% inspiration, 9% perspiration, 90% justification. CLAIM(_WyYr1p1XVk@00:00)
- Late content fee of $150, and a $500 restart if the client goes silent for a month. Self-Made Web Designer, 2025. CLAIM(O96t2rfwmak@01:15)

## Tool-specific (dated)

- Figma file as the proposal, with a Stripe deposit link on the acceptance step. Jesse Showalter, 2025. CLAIM(3TIYR3ekvjI@01:06), CLAIM(3TIYR3ekvjI@01:47)
- ChatGPT used as a stand-in to draft discovery answers from the current site, then sent to the client for approval. 2025. CLAIM(3TIYR3ekvjI@02:52)
- Relume for a quick sitemap and wireframe layouts; Framer wireframe tool instead of blank wireframes. 2025. CLAIM(3TIYR3ekvjI@03:26), CLAIM(3TIYR3ekvjI@07:04)
- Framer as the build surface: styles page first, Figma-to-HTML plugin to paste sections, breakpoints, stacks, page templates for nav and footer, effects panel for motion, publish plus DNS. 2025. CLAIM(3TIYR3ekvjI@10:18), CLAIM(3TIYR3ekvjI@13:39)
- HubSpot forms dropped into extra landing pages on that same build. 2025. CLAIM(3TIYR3ekvjI@12:56)
- Google Drive as the single project folder, cloned with a Copy Folder browser extension; page Google Docs for copy. Self-Made Web Designer, 2025. CLAIM(O96t2rfwmak@03:48), CLAIM(O96t2rfwmak@05:02)
- Style samples built in a Figma onboarding template, idea credited to Chris Do. 2025. CLAIM(O96t2rfwmak@07:02), CLAIM(O96t2rfwmak@08:07)
- Presentation deck can be Keynote, a PDF, or a walkthrough of a Figma file. Flux Academy, 2022. CLAIM(_WyYr1p1XVk@02:07)
- plus 15 more in the corpus law file studio-corpus/laws/business.md

## Hand-off
- Next stage: ds-discovery. Agent: `ds-strategist`.
- Corpus source: studio-corpus/laws/business.md (regenerate skills with tools/build_skills.py after a corpus refresh).
- Nothing outward (deploy, publish, push) without Gate-D: `ds-pre-publish-gate-d` enforces it once wired.
