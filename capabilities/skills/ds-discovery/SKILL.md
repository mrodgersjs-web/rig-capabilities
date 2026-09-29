---
name: ds-discovery
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate
  (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict.
  Main skill of design-studio-os for discovery and brief: Turn a request into a design brief: buyer, job to be done, success metric, constraints, references and sitemap before any artboard opens. 55 laws, 28
  looks-like/does-not pairs distilled from the RIG design YouTube corpus (top-10 subscribed channels
  weighted), every law cited CLAIM(<videoId>@mm:ss). Use when the ask is a new site or a redesign and no brief exists, or a sitemap and reference set are due.
tier: main
parent: design-studio-os
activation: "Load at the start of any task that decides discovery and brief. Entered by the /design-studio command through design-studio-os, by ds-strategist, or by the ds-gate-* harness that names this stage."
owner: rig-intelligence
status: Stable
acl: internal
outcome: "design-ux: brief.md (buyer, job, metric, constraints), references.md (3-5 sites, pattern per site), sitemap or page list, with citations or labeled own reasoning on every judgment"
done_when:
  - cmd:python3 tools/claims_check.py studio-skills/skills/ds-discovery/SKILL.md
  - cmd:python3 tools/check_family.py
quality_floor: 0.6
---

# Discovery and brief

JEV FIRST, and it binds every task under this skill: an agent whose only context is this excerpt
sends semantic triage, routing and classification to the rig-s1gate Jev path BEFORE any frontier LLM call
(`~/.rig/bin/rig-s1gate check plan.readiness --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`;
nearest existing rubric: plan.readiness, advisory until calibrated). When the classifier is unavailable: DEFERRED,
never a guessed verdict. A required signal passes only above 0.9.

## Load surface

Load this skill FIRST, before any design decision, whenever the job touches discovery and brief. It is an
always-loaded task-start surface, not a deep reference an agent must already know about: the `/design-studio`
command loads `design-studio-os`, which names this skill in its stage routes table; `when-designing-interfaces`
and `when-designing-websites` route design work to that front door; and the meta agent `ds-director` dispatches
`ds-strategist`, which loads this skill before its first action. The stage's gate harness
(`ds-gate-craft`, `ds-gate-brief`, `ds-gate-critique` or `ds-gate-ship`) names these requirements, so a session
running that harness loads this file to pass its gate. Paths are relative to `~/Developer/rig-design-studio-os`.

## When to use

Trigger words: "design a site", "redesign", brief, sitemap, who is this for, what pages. Inside a build this stage runs after the stage that feeds it and
before ds-brand-identity, ds-layout.

## Inputs and output contract

Inputs: the raw request (or a URL to an existing site), who the buyer is, any business constraints.
Output: brief.md (buyer, job, metric, constraints), references.md (3-5 sites, pattern per site), sitemap or page list.

## Procedure

1. Goal and problem lock: one-sentence goal, audience rank, viewing context, decision filter, and the sandbox (see references/goal-and-problem-lock.md).
2. Research synthesis: empathy maps, thematic clusters, personas, need statements, requirements, stories, and task flows (see references/research-synthesis.md).
3. Sitemap and page jobs: planning diagram, nav cap, page jobs, competitor shots, wireframe review, and the three sitemap types (see references/sitemap-and-page-jobs.md).
4. Client content intake: copy ownership, per-page briefs, brand words, photos, proof, positioning, first screen, and launch measurement (see references/client-content-intake.md).
5. Workshop and first artifact: two directions, rationale, creative-block sequence, mood-board parts, minimum ship, and named workshop votes (see references/workshop-and-first-artifact.md).
6. Check the decision tables below for the choices this stage forces.
7. Run the anti-patterns as a final sweep; each surviving one becomes a finding in `ds-critique`.
8. Cite every load-bearing choice (CLAIM copied from this file); label the rest own reasoning.

## Core laws (load-bearing subset)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 1 | Write the project goal as one sentence before any visual work. If the sentence will not fit, the brief is not ready. | The Futur, Sam Crawford | CLAIM(xM-0aeHbk5Y@01:09), CLAIM(wCiM8jYE5yg@01:54), CLAIM(mXLPMFo6KYM@01:54) | consensus |
| 3 | Name the blocking problem in the kickoff, before options: who it is for, the takeaway, and what is in the way. | The Futur, NNgroup, Mike Locke | CLAIM(xM-0aeHbk5Y@02:11), CLAIM(kT0ZqwdPYRM@00:03), CLAIM(15QY5NPPQGQ@01:21) | consensus |
| 4 | When several audiences exist, list the top three and design the structure around the one that matters most. Give the others their own route. | The Futur, Sam Crawford | CLAIM(xM-0aeHbk5Y@02:42), CLAIM(wCiM8jYE5yg@02:54) | consensus |
| 9 | Write the sandbox before ideation: what it may look like, what it may sound like, and what is out. Use that list to kill guesses. | The Futur, Mike Locke | CLAIM(xM-0aeHbk5Y@04:22), CLAIM(owV1GDsPpno@02:29) | consensus |
| 16 | Write the need as a specific user, a verb (access, learn, reorder), and the outcome. Ban interface nouns such as buttons and menus. | NNgroup, Mike Locke | CLAIM(kT0ZqwdPYRM@01:11), CLAIM(kT0ZqwdPYRM@01:48), CLAIM(kT0ZqwdPYRM@02:23), CLAIM(8RPhZcYeGr0@04:41) | consensus |
| 21 | Draw the planning diagram (pages, groups, relationships) before wireframes or visual design, once the site has more than a couple of pages. | Flux Academy, Sam Crawford | CLAIM(R_UYM9yEuYg@00:43), CLAIM(wCiM8jYE5yg@02:06), CLAIM(mXLPMFo6KYM@01:46), CLAIM(44o2Tm2DFtQ@02:36) | consensus |
| 22 | Collapse a long page list into about four to eight top groups. Do not put more than nine choices in the main navigation. | Flux Academy, Sam Crawford | CLAIM(R_UYM9yEuYg@04:32), CLAIM(R_UYM9yEuYg@04:38), CLAIM(mXLPMFo6KYM@01:50) | consensus |
| 23 | Point every page at one primary action. If the goal is a booked call, every page needs a path there. | Sam Crawford, Flux Academy | CLAIM(wCiM8jYE5yg@02:46), CLAIM(R_UYM9yEuYg@04:08), CLAIM(mXLPMFo6KYM@01:54) | consensus |
| 2 | Open the first client conversation with success, who arrives, what they already know, and what they must grasp before they act. Do not open with look and feel. | Sam Crawford | CLAIM(wCiM8jYE5yg@00:59), CLAIM(wCiM8jYE5yg@01:38) | single-source |
| 24 | Give each core page one job: home makes the first impression, about builds trust, services create desire, contact removes friction. | Sam Crawford | CLAIM(mXLPMFo6KYM@02:07), CLAIM(mXLPMFo6KYM@02:17) | single-source |
| 25 | Set navigation labels with the client, in their words. Kill generic labels that could mean the topic instead of the company. | Flux Academy, Paige Brunton | CLAIM(R_UYM9yEuYg@08:37), CLAIM(R_UYM9yEuYg@08:57), CLAIM(VsgdbhE1kgQ@02:31) | consensus |
| 26 | Audit competitor pages for what to keep, drop, and improve. Screenshot headers and footers and set them beside the draft before you lock groups. | Flux Academy, Mike Locke, Sam Crawford | CLAIM(R_UYM9yEuYg@05:40), CLAIM(R_UYM9yEuYg@06:19), CLAIM(B6uPHUPoUGA@02:26), CLAIM(B6uPHUPoUGA@03:14), CLAIM(mXLPMFo6KYM@01:05) | consensus |

The full set of 55 laws lives in the sub-skills.

## Sub-skills

| sub-skill | file | owns |
|---|---|---|
| goal-and-problem-lock | references/goal-and-problem-lock.md | 9 laws |
| research-synthesis | references/research-synthesis.md | 11 laws |
| sitemap-and-page-jobs | references/sitemap-and-page-jobs.md | 13 laws |
| client-content-intake | references/client-content-intake.md | 14 laws |
| workshop-and-first-artifact | references/workshop-and-first-artifact.md | 8 laws |

## Looks like / does not (strongest pairs)

| looks like | does not | why | citation |
|---|---|---|---|
| 1 | One-sentence goal written before any pixels | Template opened, look decided, purpose figured out later | Guesswork sites can look fine and still fail the job |
| 2 | First question is what success looks like | First question is what it should look like | Look-and-feel answers skip the visitor and the action |
| 3 | One action repeated, always to the same place | Three buttons sending people three ways | Split actions leave no path |
| 4 | Offer visible in the first scroll, strong photos, tight hierarchy | Auto-playing slideshows, parallax, and a palette with no job | Same offer, buried under noise, does not get chosen |
| 5 | Empty space left on purpose | Every gap filled | The designer likes a full page; the visitor needs room to read |
| 6 | Owner can edit, with a live walkthrough | Clever build only the agency can touch | A site that stays current beats a site that waits on a ticket |

Full pair set: the ds-exemplars skill and studio-exemplars/pairs/discovery/.

## Decision tables

### Which sitemap you are making

| Choice A | Choice B | Pick when |
|----------|----------|-----------|
| Planning diagram for the team | HTML page a visitor can open | A is the discovery artifact. B is a published index after the site exists (CLAIM(R_UYM9yEuYg@00:21), CLAIM(R_UYM9yEuYg@00:43)) |
| Planning diagram | XML crawl file | XML is for search engines after upload, then submitted. It is not the brief (CLAIM(R_UYM9yEuYg@13:35), CLAIM(R_UYM9yEuYg@15:20)) |

### Which research artifact

| Choice A | Choice B | Pick when |
|----------|----------|-----------|
| Empathy map (said, thought, did, felt) | Persona document | Map when the team must share one user on one task. Persona when segments already show repeating attribute patterns (CLAIM(9HwpR3Njq00@00:37), CLAIM(rIwoweiC3n4@03:29)) |
| Need statement (user, verb, outcome) | User story (actor can do X on this screen) | Need statement before ideas, to ban feature nouns. Story when a screen list already exists and you are checking coverage (CLAIM(kT0ZqwdPYRM@02:10), CLAIM(8RPhZcYeGr0@04:41)) |
| User story | Task flow | Story checks one capability. Flow checks one job across screens, such as buying an item (CLAIM(8RPhZcYeGr0@06:38)) |
| Thematic clusters | Competitor audit | Clusters when you have interview or field transcripts. Audit when you need keep, drop, and improve from live sites (CLAIM(KUZ6iGvJlGI@00:17), CLAIM(B6uPHUPoUGA@03:14)) |

### How to run the workshop

| Choice A | Choice B | Pick when |
|----------|----------|-----------|
| Paper or whiteboard | Shared digital board | Paper is enough for a sitemap or requirements list. A shared board when a remote group must vote, follow a speaker, and leave an agenda (CLAIM(R_UYM9yEuYg@01:37), CLAIM(Xe40x9gb0yU@03:03)) |
| Human draft, then a generator for gaps | Generator first | Always draft first on a client site. A generator-first pass is the anti-pattern, even if it is faster (CLAIM(R_UYM9yEuYg@09:39)) |
| Two client-facing directions | Many private sketches, then one | Two when a client must choose. Many private versions when you are unblocking yourself, then hone to one (CLAIM(44o2Tm2DFtQ@08:18), CLAIM(owV1GDsPpno@06:50)) |
| Keyword form plus live why-call | Ask for four words in email | Use the workshop whenever the words will steer later visual decisions (CLAIM(qO0TbOdWado@01:18)) |

### Who supplies content

| Choice A | Choice B | Pick when |
|----------|----------|-----------|
| Client writes from a per-page brief | Hire a copywriter | Writer when budget allows. Client prompts when it does not. Name the owner before booking either way (CLAIM(VsgdbhE1kgQ@01:28), CLAIM(VsgdbhE1kgQ@01:46)) |
| Client shoot or real phone photos | Paid photo search by the studio | Shoot or phone photos when people and place are the trust signal. Paid search when they will not, and you still need control (CLAIM(mXLPMFo6KYM@05:51), CLAIM(VsgdbhE1kgQ@05:12)) |
| Stock library as a stopgap | No images until a shoot | Stock only if the alternative is empty or embarrassing, and say so. Do not treat stock as the brand (CLAIM(VsgdbhE1kgQ@05:04), CLAIM(mXLPMFo6KYM@05:37)) |

## Anti-patterns

- Opening a template and deciding the look before the job is named (CLAIM(wCiM8jYE5yg@00:13)).
- Designing on a blank artboard with no written problem (CLAIM(15QY5NPPQGQ@01:58), CLAIM(8RPhZcYeGr0@01:15)).
- A great-looking build aimed at the wrong problem (CLAIM(kT0ZqwdPYRM@00:00)).
- Need statements that name buttons, menus, or a technology (CLAIM(kT0ZqwdPYRM@01:48)).
- Switching names for the same statement across the team (CLAIM(kT0ZqwdPYRM@00:31)).
- Empathy maps with no interviews or observation behind them (CLAIM(9HwpR3Njq00@01:43)).
- Tiny transcript scraps with no participant id (CLAIM(KUZ6iGvJlGI@01:26), CLAIM(KUZ6iGvJlGI@01:33)).
- Personas built without a grid of experience-changing attributes (CLAIM(rIwoweiC3n4@00:21)).
- plus 18 more in references/<sub-skill>.md files

## Creator disagreements (stated, not resolved)

- Paper versus a digital board. Flux (2024) says paper is the usual sitemap medium, and FigJam is only so the camera can see it (CLAIM(R_UYM9yEuYg@01:37)). CharliMarieTV (2023) spends more planning time in FigJam than in the design file, and runs agendas there (CLAIM(Xe40x9gb0yU@00:08), CLAIM(Xe40x9gb0yU@03:03)). Reading: paper is enough for a solo diagram. A shared board earns its place when several people must vote and follow along.
- Who thinks first, the human or the generator. Flux (2024) says draft the diagram yourself, then ask a model to fill gaps, or the tool will lead (CLAIM(R_UYM9yEuYg@09:39)). The same channel's studio episode (2023) used Relume to turn the sitemap into wireframes and draft copy as the working method (CLAIM(44o2Tm2DFtQ@02:41)). Sam Crawford (2026) allows a model for layout ideas, palettes, and small style snippets, and says the finished site must still be human-made (CLAIM(mXLPMFo6KYM@03:47), CLAIM(mXLPMFo6KYM@04:01)). Reading: generators may propose sections. They do not own the first structure or the final judgment. Weight Flux and Sam above the studio shortcut when they conflict.
- How many options to show. Flux studio (2023) refuses to present ten sites and narrows to two (CLAIM(44o2Tm2DFtQ@08:18)). Mike Locke (2011) may make about ten private concepts, then hone to one, and does not say the client sees all ten (CLAIM(owV1GDsPpno@06:50)). The Futur (2016) narrows the sandbox before exploration and does not set a count (CLAIM(xM-0aeHbk5Y@04:22)). Reading: many sketches in private, two directions in front of the client.
- Whether a digital wireframe is required. Mike Locke (2017) calls digital wireframes overrated and says scratch requirements, stories, and flows are the prep (CLAIM(8RPhZcYeGr0@09:38)). The same designer in 2010, plus Sam Crawford (2026) and Flux (2023), use a wireframe as the client review artifact before visual design (CLAIM(B6uPHUPoUGA@04:44), CLAIM(wCiM8jYE5yg@03:05), CLAIM(44o2Tm2DFtQ@02:49)). Reading: scratch prep is mandatory. A digital wireframe is mandatory only when a client must comment on order before style.
- Stock photos. Paige Brunton (2021) tells designers to put stock sources in the welcome pack if a shoot is impossible (CLAIM(VsgdbhE1kgQ@05:04)). Sam Crawford (2026) says stock, and synthetic portraits, get spotted and erode trust, and that a candid phone photo is better (CLAIM(mXLPMFo6KYM@05:37), CLAIM(mXLPMFo6KYM@05:51)). Reading: stock is a labeled stopgap, not the brand system. Weight the 2026 top-10 source when the two conflict.
- Who writes the argument. Paige Brunton (2021) says a writer is ideal, the designer should not silently inherit copy, and the client can write from prompts (CLAIM(VsgdbhE1kgQ@01:28), CLAIM(VsgdbhE1kgQ@01:46)). Sam Crawford (2026) has the strategist decide what each page must say before build (CLAIM(mXLPMFo6KYM@02:04)). Reading: the studio owns the page job. The sentences can still come from a writer or a prompted client. Do not assume both.

## Creator claims (unverified)

- A solution aimed at the wrong problem always fails (CLAIM(kT0ZqwdPYRM@00:00)).
- More than one sentence for the goal waters down later solutions (CLAIM(xM-0aeHbk5Y@01:27)).
- A skippable pre-roll must hook in the next 5 seconds or it gets skipped (CLAIM(xM-0aeHbk5Y@03:33)).
- Eight to twelve customers are enough to find persona segments (CLAIM(rIwoweiC3n4@03:15)).
- Top navigation should sit around four to eight groups, and more than nine is too much choice. About seven is a comfortable middle (CLAIM(R_UYM9yEuYg@04:32), CLAIM(R_UYM9yEuYg@04:38), CLAIM(R_UYM9yEuYg@05:23)).
- Competitive page audits take about 30 minutes to an hour. A low-fidelity wireframe can be knocked out in about 30 minutes (CLAIM(B6uPHUPoUGA@02:59), CLAIM(B6uPHUPoUGA@05:40)).
- Without a requirements list, a designer may guess on one screen for 30 minutes to an hour (CLAIM(8RPhZcYeGr0@01:22)).
- Brand-value lists of five to ten words narrow focus. Gather about ten similar sites. Expect about ten private concepts before one survives (CLAIM(owV1GDsPpno@02:25), CLAIM(owV1GDsPpno@04:56), CLAIM(owV1GDsPpno@06:50)).

## Tool-specific (dated)

- FigJam in 2023: use stamps, not stickers, when you need to see who voted. A polling widget can count votes. Use sections, not shape rectangles, so notes travel with the group. Connect arrows to the blue dots or they will not follow. Timer and shared music for rounds. Pasted links become previews. YouTube embeds play in the file. Click a face to follow, or Spotlight Me to pull the room (CLAIM(Xe40x9gb0yU@00:53), CLAIM(Xe40x9gb0yU@01:31), CLAIM(Xe40x9gb0yU@01:49), CLAIM(Xe40x9gb0yU@02:21), CLAIM(Xe40x9gb0yU@05:01), CLAIM(Xe40x9gb0yU@05:39), CLAIM(Xe40x9gb0yU@06:14), CLAIM(Xe40x9gb0yU@06:26)).
- FigJam agenda templates and a spinner widget for who runs the next meeting (2023) (CLAIM(Xe40x9gb0yU@03:31), CLAIM(Xe40x9gb0yU@03:36)).
- ChatGPT sitemap prompts, Octopus, and Relume site builder (2024): useful for gap-filling and suggested page sections, not as the first thinker. Relume was also used in 2023 to turn a sitemap into a wireframe plus draft copy (CLAIM(R_UYM9yEuYg@10:16), CLAIM(R_UYM9yEuYg@10:56), CLAIM(R_UYM9yEuYg@11:46), CLAIM(44o2Tm2DFtQ@02:41)).
- XML files via xml-sitemaps.com, or the Webflow site settings SEO tab, then submit to Google (2024) (CLAIM(R_UYM9yEuYg@14:26), CLAIM(R_UYM9yEuYg@14:51), CLAIM(R_UYM9yEuYg@15:17)).
- Keyword workshop mechanics in 2021: a multiple-choice form, clusters in the design tool, then a Zoom screen-share (CLAIM(qO0TbOdWado@01:28), CLAIM(qO0TbOdWado@02:26)).
- Empathy-map materials in 2019: big notes and markers, or remote boards such as Mural or Realtime (CLAIM(9HwpR3Njq00@01:35)).
- Low-fidelity wireframes in 2010: Visio, OmniGraffle, or Mockingbird. High-fidelity and specs in Fireworks or Photoshop (CLAIM(B6uPHUPoUGA@04:47), CLAIM(B6uPHUPoUGA@05:00), CLAIM(B6uPHUPoUGA@06:01)).
- High-fidelity UI in Sketch (2017). Blank-artboard stall described in Photoshop or Sketch (2018) (CLAIM(8RPhZcYeGr0@01:02), CLAIM(15QY5NPPQGQ@02:00)).
- plus 3 more in the corpus law file studio-corpus/laws/discovery.md

## Hand-off
- Next stage: ds-brand-identity, ds-layout. Agent: `ds-strategist` (sub: ds-reference-hunter).
- Corpus source: studio-corpus/laws/discovery.md (regenerate skills with tools/build_skills.py after a corpus refresh).
- Nothing outward (deploy, publish, push) without Gate-D: `ds-pre-publish-gate-d` enforces it once wired.
