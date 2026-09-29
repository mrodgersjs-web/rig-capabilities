---
name: ds-career
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate
  (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict.
  Main skill of design-studio-os for design career: Portfolio, positioning and getting hired or getting clients as a designer. 50 laws, 27
  looks-like/does-not pairs distilled from the RIG design YouTube corpus (top-10 subscribed channels
  weighted), every law cited CLAIM(<videoId>@mm:ss). Use when portfolio, positioning or getting hired as a designer is the question.
tier: main
parent: design-studio-os
activation: "Load at the start of any task that decides design career. Entered by the /design-studio command through design-studio-os, by ds-strategist, or by the ds-gate-* harness that names this stage."
owner: rig-intelligence
status: Stable
acl: internal
outcome: "design-ux: a portfolio or positioning plan with the concrete next steps, with citations or labeled own reasoning on every judgment"
done_when:
  - cmd:python3 tools/claims_check.py studio-skills/skills/ds-career/SKILL.md
  - cmd:python3 tools/check_family.py
quality_floor: 0.6
---

# Design career

JEV FIRST, and it binds every task under this skill: an agent whose only context is this excerpt
sends semantic triage, routing and classification to the rig-s1gate Jev path BEFORE any frontier LLM call
(`~/.rig/bin/rig-s1gate check plan.readiness --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`;
nearest existing rubric: plan.readiness, advisory until calibrated). When the classifier is unavailable: DEFERRED,
never a guessed verdict. A required signal passes only above 0.9.

## Load surface

Load this skill FIRST, before any design decision, whenever the job touches design career. It is an
always-loaded task-start surface, not a deep reference an agent must already know about: the `/design-studio`
command loads `design-studio-os`, which names this skill in its stage routes table; `when-designing-interfaces`
and `when-designing-websites` route design work to that front door; and the meta agent `ds-director` dispatches
`ds-strategist`, which loads this skill before its first action. The stage's gate harness
(`ds-gate-craft`, `ds-gate-brief`, `ds-gate-critique` or `ds-gate-ship`) names these requirements, so a session
running that harness loads this file to pass its gate. Paths are relative to `~/Developer/rig-design-studio-os`.

## When to use

Trigger words: "portfolio", "get hired", "design career", "freelance". Inside a build this stage runs after the stage that feeds it and
before ds-business.

## Inputs and output contract

Inputs: the target role or client type, the current work.
Output: a portfolio or positioning plan with the concrete next steps.

## Procedure

1. Career portfolio edit: what stays on the site, how many pages, how type and layout repeat (see references/career-portfolio-edit.md).
2. Career case study: problem, solution, trust, and the contact funnel (see references/career-case-study.md).
3. Career folio craft: nav, contrast, image size, motion that does not block, work separated from the page (see references/career-folio-craft.md).
4. Career positioning: who you help, one ask, proof, and the button (see references/career-positioning.md).
5. Check the decision tables below for the choices this stage forces.
6. Run the anti-patterns as a final sweep; each surviving one becomes a finding in `ds-critique`.
7. Cite every load-bearing choice (CLAIM copied from this file); label the rest own reasoning.

## Core laws (load-bearing subset)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 2 | Cut copy until a stranger can tell what you do without feeling lost. Extra paragraphs lower the chance they act. On a project page, short lines and large images beat a screen of text. | Satori Graphics, Flux Academy | CLAIM(DZ2bB8tL4O0@00:33), CLAIM(DZ2bB8tL4O0@01:00), CLAIM(mY7NFbN0e2M@08:35) | consensus |
| 4 | Put only best work on the site, shown large and sharp. Tiny, fast-moving thumbnails read as amateur. Curate every image; if you would not defend it, it does not ship. | Satori Graphics, Flux Academy | CLAIM(ITpre4-99PI@00:55), CLAIM(mq4tBpnFPbE@01:57), CLAIM(mq4tBpnFPbE@02:32), CLAIM(mY7NFbN0e2M@14:44) | consensus |
| 8 | Make the contact path obvious, and design the site so the next step is one action (talk about a project, or book a call). Do not bury it at the end of a long scroll. | Satori Graphics, Flux Academy | CLAIM(DZ2bB8tL4O0@04:22), CLAIM(DZ2bB8tL4O0@04:50), CLAIM(DZ2bB8tL4O0@17:01), CLAIM(F7IUNob5dn4@06:10) | consensus |
| 10 | Open each case with the problem in a few lines, then the solution. Buyers pay to remove a problem, not to admire a picture. For a UX case, also name the hypothesis, your role, what users can do now, the messy process, a measured effect if you have one, and what you learned. | Satori Graphics, NNgroup | CLAIM(DZ2bB8tL4O0@03:28), CLAIM(DZ2bB8tL4O0@03:28), CLAIM(DZ2bB8tL4O0@14:56), CLAIM(jt1WroGHvBs@00:26), CLAIM(jt1WroGHvBs@01:23), CLAIM(jt1WroGHvBs@02:00) | consensus |
| 12 | Add trust signals a buyer can check: who you helped, what changed, and a clear way to start a conversation. A client's own words outweigh your recap. Logos or a testimonial beat an empty proof slot. | Satori Graphics, Flux Academy | CLAIM(DZ2bB8tL4O0@02:32), CLAIM(mq4tBpnFPbE@04:26), CLAIM(mq4tBpnFPbE@04:51), CLAIM(mY7NFbN0e2M@12:28), CLAIM(F7IUNob5dn4@02:55) | consensus |
| 14 | When you have no client yet, invent a local business with a real constraint and redesign it as if you were hired. A folio of made-up clients can still get you hired if the work is strong. | Satori Graphics, Every Tuesday | CLAIM(DZ2bB8tL4O0@05:51), CLAIM(DZ2bB8tL4O0@06:17), CLAIM(carA7JNAyzQ@03:42) | consensus |
| 27 | Name your role. "We" hides whether you led, assisted, or only touched type. | Flux Academy, NNgroup | CLAIM(mY7NFbN0e2M@11:09), CLAIM(jt1WroGHvBs@00:44) | consensus |
| 37 | Never present a mark only as flat black on white. Put it in the place it has to live, and show a few sketches so the choice looks earned. | Will Paterson, Every Tuesday | CLAIM(kBAzt2Fz7cs@03:35), CLAIM(pkYXz_tEOVg@03:42), CLAIM(pkYXz_tEOVg@06:33), CLAIM(carA7JNAyzQ@03:51) | consensus |
| 1 | Treat the portfolio as the career gate. Strong craft that is badly shown still loses the click. | Satori Graphics | CLAIM(DZ2bB8tL4O0@00:00), CLAIM(ITpre4-99PI@08:21) | single-source |
| 3 | The portfolio is only as strong as its weakest piece. Remove the project you would not want a buyer to judge you by. | Satori Graphics | CLAIM(DZ2bB8tL4O0@01:30) | single-source |
| 5 | Keep one type family across the whole folio so the site reads as one practice, not a pile of jobs. | Satori Graphics | CLAIM(DZ2bB8tL4O0@08:38), CLAIM(ITpre4-99PI@00:29), CLAIM(W0UrLHrVTmk@03:54) | single-source |
| 6 | Repeat a layout system (spacing, image treatment, project titles) so each case feels like the same studio. | Satori Graphics | CLAIM(ITpre4-99PI@03:21), CLAIM(ITpre4-99PI@07:51) | single-source |

The full set of 50 laws lives in the sub-skills, plus 27 ungrouped laws below.

## Sub-skills

| sub-skill | file | owns |
|---|---|---|
| career-portfolio-edit | references/career-portfolio-edit.md | 7 laws |
| career-case-study | references/career-case-study.md | 6 laws |
| career-folio-craft | references/career-folio-craft.md | 8 laws |
| career-positioning | references/career-positioning.md | 4 laws |

## Further laws (not yet grouped into a sub-skill)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 2 | Cut copy until a stranger can tell what you do without feeling lost. Extra paragraphs lower the chance they act. On a project page, short lines and large images beat a screen of text. | Satori Graphics, Flux Academy | CLAIM(DZ2bB8tL4O0@00:33), CLAIM(DZ2bB8tL4O0@01:00), CLAIM(mY7NFbN0e2M@08:35) | consensus |
| 15 | On a long social or Behance post, tell a short visual story: context, the mark in place, then the outcome. Do not rush the alignments. | Satori Graphics | CLAIM(W0UrLHrVTmk@05:53), CLAIM(W0UrLHrVTmk@06:46) | single-source |
| 25 | On a project page, orient the visitor first: whose brand this is, what the project is, in one line, before the long story. | Flux Academy | CLAIM(mY7NFbN0e2M@02:39), CLAIM(mY7NFbN0e2M@03:00) | single-source |
| 27 | Name your role. "We" hides whether you led, assisted, or only touched type. | Flux Academy, NNgroup | CLAIM(mY7NFbN0e2M@11:09), CLAIM(jt1WroGHvBs@00:44) | consensus |
| 28 | Show the flat system before the glossy mockup, and for a real job use a photo of the thing in the place it was made for. | Every Tuesday | CLAIM(carA7JNAyzQ@03:08), CLAIM(carA7JNAyzQ@03:51) | single-source |
| 29 | Hold the folio to about six to eight projects. Put two or three in your strongest area, open and close on that strength, and park the third-best in the middle. | Every Tuesday | CLAIM(carA7JNAyzQ@04:15), CLAIM(carA7JNAyzQ@04:41), CLAIM(carA7JNAyzQ@06:11), CLAIM(carA7JNAyzQ@06:51) | single-source |
| 30 | After you publish a case, get another pair of eyes on spelling, confusion, and whether the format is usable. Plan to revise it. | NNgroup | CLAIM(jt1WroGHvBs@02:27), CLAIM(jt1WroGHvBs@02:35) | single-source |
| 31 | Before you lock a mark, test it small, in motion, and on a material (stitch, print, a favicon). If it dies at one size, it is not done. | Satori Graphics | CLAIM(UtEnQCWd0m4@03:25), CLAIM(UtEnQCWd0m4@08:07) | single-source |
| 32 | Write one emotion the piece must create, then check color, type, and motion against that one feeling. Two emotions is already a split brief. | Satori Graphics | CLAIM(UtEnQCWd0m4@06:28), CLAIM(UtEnQCWd0m4@05:55) | single-source |
| 33 | A system holds on mobile, print, and social. If it only works on the board you designed, it is a style, not a system. | Satori Graphics | CLAIM(UtEnQCWd0m4@00:30), CLAIM(UtEnQCWd0m4@07:36) | single-source |
| 34 | On a client call, ask what problem must be solved. "What design do you want?" hands them a menu they cannot use. | Satori Graphics | CLAIM(UtEnQCWd0m4@08:38) | single-source |
| 35 | Name layers, group by function, and leave a top folder of notes and font files so the next person can open the job. | Satori Graphics | CLAIM(UtEnQCWd0m4@01:26), CLAIM(UtEnQCWd0m4@01:54) | single-source |
| 36 | Tell the constraint in the case, not only the pretty end. A story with no challenge does not let a buyer see the judgment. | Will Paterson | CLAIM(pkYXz_tEOVg@02:10), CLAIM(pkYXz_tEOVg@02:43) | single-source |
| 37 | Never present a mark only as flat black on white. Put it in the place it has to live, and show a few sketches so the choice looks earned. | Will Paterson, Every Tuesday | CLAIM(kBAzt2Fz7cs@03:35), CLAIM(pkYXz_tEOVg@03:42), CLAIM(pkYXz_tEOVg@06:33), CLAIM(carA7JNAyzQ@03:51) | consensus |
| 38 | Only put a client logo on the folio if you did the work. A borrowed mark is a false trust signal. | Will Paterson | CLAIM(kBAzt2Fz7cs@06:26) | single-source |
| 39 | If an NDA hides the best client work, say so, and fill the gap with a passion project aimed at the jobs you want. Show the three to five pieces you would take again. | Will Paterson | CLAIM(VXziHnT38Mg@06:14), CLAIM(VXziHnT38Mg@08:24), CLAIM(VXziHnT38Mg@10:06) | single-source |
| 40 | Put the buyers you want on the first screen, list only the services you do well, and make contact a form that lands in your inbox with almost no friction. | Will Paterson, Flux Academy | CLAIM(kBAzt2Fz7cs@01:14), CLAIM(kBAzt2Fz7cs@07:33), CLAIM(kBAzt2Fz7cs@11:04), CLAIM(F7IUNob5dn4@05:13) | consensus |
| 41 | Check the folio on a phone before you call it done. A desktop-only layout fails the device most visitors actually use. | Will Paterson | CLAIM(VXziHnT38Mg@07:51) | single-source |
| 42 | A hiring glance fails on a pixelated portrait, placeholder copy, or a text effect you would not ship for a client. Hierarchy, type, and color are the bar, not the mockup glow. | Flux Academy | CLAIM(KO5eOtR2njU@01:13), CLAIM(KO5eOtR2njU@03:34), CLAIM(KO5eOtR2njU@06:00), CLAIM(KO5eOtR2njU@13:41) | single-source |
| 43 | If you do two crafts, say both in the first screen. A visitor should not have to guess whether you brand, edit, or build. | Will Paterson | CLAIM(YD0x1HBaxZc@01:21) | single-source |
| 44 | Keep the project card visual. Put the long case (goals, dialogue, process) on its own page behind a clear link. | Will Paterson | CLAIM(YD0x1HBaxZc@02:01), CLAIM(YD0x1HBaxZc@13:12) | single-source |
| 45 | Do not ship a card that is visually loud even when the words are few. Density of images can overwhelm the same way a paragraph can. | Will Paterson | CLAIM(YD0x1HBaxZc@08:56) | single-source |
| 46 | Before you polish your own folio for months, ship two practice sites (a local business and a product microsite) using strong photos, then do a small free or charity job for a referral. | Mike Locke | CLAIM(WHR7bA1tKWc@02:32), CLAIM(WHR7bA1tKWc@03:02), CLAIM(WHR7bA1tKWc@05:29) | single-source |
| 47 | Learn the basics of building a page before you chase newer syntax. A simple site you can explain beats a stack you cannot finish. | Mike Locke | CLAIM(WHR7bA1tKWc@01:00), CLAIM(WHR7bA1tKWc@01:31) | single-source |
| 48 | For a portfolio domain: short, easy to say, easy to spell, and something you will still claim in five years. Write the email four times. If you stumble, change the name. | The Futur | CLAIM(h1cI9Ti1lG0@01:22), CLAIM(h1cI9Ti1lG0@01:57), CLAIM(h1cI9Ti1lG0@10:58) | single-source |
| 49 | No hyphens in the domain. Avoid a name people already use for a different product, and avoid a homonym (pair / pear) you cannot say out loud without explaining. | The Futur | CLAIM(h1cI9Ti1lG0@05:18), CLAIM(h1cI9Ti1lG0@09:22), CLAIM(h1cI9Ti1lG0@10:09) | single-source |
| 50 | If you use your personal name, accept that it can read as a smaller practice. A brand name can read larger, but only if you can still say it once and be found. | The Futur | CLAIM(h1cI9Ti1lG0@03:08), CLAIM(h1cI9Ti1lG0@04:37) | single-source |

## Looks like / does not (strongest pairs)

| looks like | does not | why | citation |
|---|---|---|---|
| 1 | Few strong projects, each explained | A long folio whose worst piece sets the grade | Buyers remember the weak example |
| 2 | Short problem, then the solution | A wall of process text | Confusion kills the click |
| 3 | One type family across every case | A new font on every project | Repetition is what makes it feel like one studio |
| 4 | Large, sharp project images | Tiny screenshots racing past | Size and quality are the pro signal |
| 5 | Video of the interaction, scroll still instant | A loader the visitor has to wait through | Motion should show the work, not delay it |
| 6 | Contact is the designed next step | A folio with no obvious way to hire you | The visit has to end in a conversation |

Full pair set: the ds-exemplars skill and studio-exemplars/pairs/career/.

## Decision tables

| decision | option A | option B | pick A when | pick B when | citation |
|---|---|---|---|---|---|
| How many projects | A short set of best work | Every job you have ever shipped | A buyer will judge you by the worst piece | You are building a filterable library and each extra case is as strong as the first | CLAIM(DZ2bB8tL4O0@01:30) |
| Niche on the folio | One visual specialty, shown deeply | A generalist grid of unrelated styles | The specialty is what you want to be hired for | You need to prove range for a generalist role, and each style is still your best | CLAIM(ITpre4-99PI@04:27) |
| Motion | A clip of the real interaction, page still scrolls | Entrance animation that delays the content | The work itself moves | The motion is only decoration on the folio | CLAIM(mq4tBpnFPbE@02:59), CLAIM(mq4tBpnFPbE@03:53) |
| Headline | Who you help and the problem | Your title and your tool | A buyer is scanning for fit | A recruiter asked for the tool and the title is the fit | CLAIM(F7IUNob5dn4@01:10) |
| Count | About six to eight, two or three in the strength | A short set with no range, or a long set of equals | You have a strongest area and still need to show you can do adjacent work | You are early and six strong pieces do not exist yet; ship fewer rather than pad | CLAIM(carA7JNAyzQ@04:41) |
| Case ending | What users can do now, plus a number if you measured one | Pretty screens with no before and after | The viewer is an employer who must imagine working with you | You have no measurement; say what changed in behavior, and do not invent a lift | CLAIM(jt1WroGHvBs@01:23), CLAIM(jt1WroGHvBs@02:00) |
| Project count | Three to five pieces you would take again | Six to eight, with range around a strength | You are positioning for one kind of client | You still need to prove you can do adjacent work | CLAIM(VXziHnT38Mg@08:24), CLAIM(carA7JNAyzQ@04:41) |
| Domain | Personal name | Invented brand | You want to be hired as yourself and can live with a smaller read | You want a studio name and you have checked it is not already a product | CLAIM(h1cI9Ti1lG0@03:08) |
| First sites | Two practice builds, then outreach | Only your own folio for months | You have no client work yet | The folio already has real cases | CLAIM(WHR7bA1tKWc@03:02) |

## Anti-patterns

- A folio that is only as good as a project you are ashamed of. CLAIM(DZ2bB8tL4O0@01:30)
- So much text the visitor cannot tell what you do. CLAIM(DZ2bB8tL4O0@01:00)
- No contact path, or a contact path you have to hunt for. CLAIM(DZ2bB8tL4O0@04:22)
- Light type on a bright background. CLAIM(ITpre4-99PI@02:24)
- Tiny animated thumbnails instead of the work at size. CLAIM(mq4tBpnFPbE@01:57)
- Animations that make the visitor wait. CLAIM(mq4tBpnFPbE@03:28)
- A social post shipped with known alignment errors. CLAIM(W0UrLHrVTmk@05:25)
- A headline that only names your tool. CLAIM(F7IUNob5dn4@01:10)
- plus 9 more in references/<sub-skill>.md files

## Creator disagreements (stated, not resolved)

- How many projects: Satori Graphics (2023) says you do not need many pages. CLAIM(DZ2bB8tL4O0@12:24). Every Tuesday (2016) names six to eight, with strength at the open, the close, and the middle. CLAIM(carA7JNAyzQ@04:41). Will Paterson (2025) says show only the top three to five pieces you loved. CLAIM(VXziHnT38Mg@08:24). Treat six to eight as the ceiling when you need range, and three to five as the cut when you are positioning for one kind of work.
- Domain ending: Wes McDowell in the business set (2020) treats a novelty extension as a last resort behind a tweaked .com. The Futur (2018) actively sells .design for portfolios. CLAIM(h1cI9Ti1lG0@12:16). For a personal folio, .design is a dated option. For a client business, prefer the .com rule in the business file.
- First work: Mike Locke (2011) says build fictitious sites and then free charity sites before you sell. CLAIM(WHR7bA1tKWc@05:29). Later creators (Satori, Every Tuesday, Sam Crawford in the business set) still allow fictional work, but they do not require unpaid client work as the next step. Do not treat 2011 free-work advice as current pricing.
- Pictures vs process: Flux Academy (2023) says do not drown the work and keep text short. CLAIM(mY7NFbN0e2M@04:55). NNgroup (2019) says employers want the messy process, not only pretty pictures. CLAIM(jt1WroGHvBs@00:10), CLAIM(jt1WroGHvBs@01:40). Hold both: images lead, and a UX case still owes role, process, and effect in short lines.

## Creator claims (unverified)

- Small interface choices set a folio apart from "99%" of others. Satori Graphics, 2020 and 2023. CLAIM(ITpre4-99PI@01:24), CLAIM(DZ2bB8tL4O0@09:36)
- An $8 font is enough to stop a folio looking like everyone else. Flux Academy, 2025. CLAIM(mq4tBpnFPbE@01:22)
- Six to eight projects is "much less than you think." Every Tuesday, 2016. CLAIM(carA7JNAyzQ@04:27)
- A graduate folio made only of fictional clients still got this designer a job. 2016. CLAIM(carA7JNAyzQ@03:42)
- A hiring look takes about 10 to 15 seconds. Flux Academy, 2025. CLAIM(KO5eOtR2njU@00:00)
- Getting a folio off the ground can take six months if you only polish your own site. Mike Locke, 2011. CLAIM(WHR7bA1tKWc@05:59)

## Tool-specific (dated)

- Portfolio social post built in Photoshop: about 1300px wide and a very tall canvas, layer blend modes to seat a logo in a photo, rectangle blocks for process, mockup files for context. Satori Graphics, 2019. CLAIM(W0UrLHrVTmk@01:55), CLAIM(W0UrLHrVTmk@03:24), CLAIM(W0UrLHrVTmk@06:20)
- Paid type sourced from YouWorkForThem rather than the default free web fonts. Flux Academy, 2025. CLAIM(mq4tBpnFPbE@00:57)
- NordPass promo segment in the 2023 portfolio video is a sponsor read, not a portfolio law. CLAIM(DZ2bB8tL4O0@07:12)
- Framer named as the tool on a portfolio being critiqued in 2025. The critique says clients usually want a site, not a named builder, unless they are hiring that builder. CLAIM(F7IUNob5dn4@01:10), CLAIM(F7IUNob5dn4@01:28)
- iStock named as the photo source for a practice restaurant site. Mike Locke, 2011. CLAIM(WHR7bA1tKWc@03:02)
- .design sold as a portfolio extension in 2018, with Facebook, Adobe, Amazon, and Airbnb cited as users of that ending. The Futur. CLAIM(h1cI9Ti1lG0@12:16)
- Framer called out as the build surface for a mobile check of the folio. Will Paterson, 2025. CLAIM(VXziHnT38Mg@07:51)
- Envato Elements is a sponsor read in the 2022 portfolio videos, not a portfolio law. CLAIM(pkYXz_tEOVg@00:00), CLAIM(kBAzt2Fz7cs@00:00)

## Hand-off
- Next stage: ds-business. Agent: `ds-strategist`.
- Corpus source: studio-corpus/laws/career.md (regenerate skills with tools/build_skills.py after a corpus refresh).
- Nothing outward (deploy, publish, push) without Gate-D: `ds-pre-publish-gate-d` enforces it once wired.
