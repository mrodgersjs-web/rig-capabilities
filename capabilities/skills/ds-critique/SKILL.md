---
name: ds-critique
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate
  (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict.
  Main skill of design-studio-os for critique and quality gates: Judge the work: taste, anti-slop, accessibility and the looks-like / does-not calibration, from real captures, with a cited law per finding. 95 laws, 40
  looks-like/does-not pairs distilled from the RIG design YouTube corpus (top-10 subscribed channels
  weighted), every law cited CLAIM(<videoId>@mm:ss). Use when the ask is to judge, audit or de-slop work that already exists.
tier: main
parent: design-studio-os
activation: "Load at the start of any task that decides critique and quality gates. Entered by the /design-studio command through design-studio-os, by ds-critic, or by the ds-gate-* harness that names this stage."
owner: rig-intelligence
status: Stable
acl: internal
outcome: "design-ux: critique.md: findings table (stage, finding, law cited, severity), verdict GO / REVISE / DEFERRED, with citations or labeled own reasoning on every judgment"
done_when:
  - cmd:python3 tools/claims_check.py studio-skills/skills/ds-critique/SKILL.md
  - cmd:python3 tools/check_family.py
quality_floor: 0.6
---

# Critique and quality gates

JEV FIRST, and it binds every task under this skill: an agent whose only context is this excerpt
sends semantic triage, routing and classification to the rig-s1gate Jev path BEFORE any frontier LLM call
(`~/.rig/bin/rig-s1gate check ui.design --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`;
nearest existing rubric: ui.design, advisory until calibrated). When the classifier is unavailable: DEFERRED,
never a guessed verdict. A required signal passes only above 0.9.

## Load surface

Load this skill FIRST, before any design decision, whenever the job touches critique and quality gates. It is an
always-loaded task-start surface, not a deep reference an agent must already know about: the `/design-studio`
command loads `design-studio-os`, which names this skill in its stage routes table; `when-designing-interfaces`
and `when-designing-websites` route design work to that front door; and the meta agent `ds-director` dispatches
`ds-critic`, which loads this skill before its first action. The stage's gate harness
(`ds-gate-craft`, `ds-gate-brief`, `ds-gate-critique` or `ds-gate-ship`) names these requirements, so a session
running that harness loads this file to pass its gate. Paths are relative to `~/Developer/rig-design-studio-os`.

## When to use

Trigger words: "critique", "audit", "review this", "looks like AI slop", "make it better". Inside a build this stage runs after the stage that feeds it and
before nothing outward without Gate-D.

## Inputs and output contract

Inputs: real captures at 375/768/1440 (never source code), the brief, the design docs.
Output: critique.md: findings table (stage, finding, law cited, severity), verdict GO / REVISE / DEFERRED.

## Procedure

1. Critique six pass: the ordered edit (cut, read, color, space, unify, say), including the 4.5 contrast floor and the wide-screen container. Owns 4, 8, 14, 15, 20, 39-43, 82, 84, 94, 95 (see references/critique-six-pass.md).
2. Ui screen audit: login, form, action weight, desktop nav, and controls that must look clickable. Owns 6, 7, 16-19, 72, 83, 85-88 (see references/ui-screen-audit.md).
3. Dashboard chrome audit: data over brand, system colors, shadow as symptom, control scope. Owns 11-13, 31-38 (see references/dashboard-chrome-audit.md).
4. Message match critique: type tone, font cap, poster and ad rescue, logo brief, swoosh geometry, hero statement vs question. Owns 9, 10, 21-27, 44, 53-60, 68-70, 89-93 (see references/message-match-critique.md).
5. Good to great lift: what to add only after the basics pass, and what to demote rather than delete. Owns 3, 5, 29, 30, 45-52, 61-67, 71-81, 90, 91 (see references/good-to-great-lift.md).
6. Check the decision tables below for the choices this stage forces.
7. Run the anti-patterns as a final sweep; each surviving one becomes a finding in `ds-critique`.
8. Cite every load-bearing choice (CLAIM copied from this file); label the rest own reasoning.

## Core laws (load-bearing subset)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 2 | Prefer the smallest edit that fixes the defect: color, hierarchy, spacing, then imagery. A full restyle is not the first move. | Jesse Showalter, Satori Graphics | CLAIM(XZf5A0wcruE@00:16), CLAIM(k2DWClcoHFI@10:43) | consensus |
| 14 | Heavy shadows and extra divider lines are a failed-contrast symptom. Raise value difference between regions before adding shadow or rules. | Jesse Showalter, Flux Academy | CLAIM(XZf5A0wcruE@15:24), CLAIM(s9XlAUisl8Q@00:50) | consensus |
| 62 | A bright utility strip (survey bar, star row) on a dark hero fails hierarchy. Move it to a delayed corner prompt that states the time cost, or darken it, so the offer is read first. | Jesse Showalter, Flux Academy | CLAIM(XZf5A0wcruE@01:28), CLAIM(S1yMcIicf0c@07:11), CLAIM(PnnbPz6G6gs@03:00) | consensus |
| 72 | Do not hide the work behind hover, a typewriter headline, or a console prompt unless mystery is the brand and the reveal pays back the time. A gimmick can be a case study. It cannot be the front door. | Jesse Showalter, DesignCourse | CLAIM(HY_Ea1la6BM@05:29), CLAIM(HY_Ea1la6BM@05:47), CLAIM(DXUC3S-y4E0@08:21), CLAIM(DXUC3S-y4E0@14:26), CLAIM(DXUC3S-y4E0@25:28) | consensus |
| 76 | On a modern page, left-align body type, including a two-column hero against the photo edge. Center only copy you want ignored, or a strong display. A drop cap, a double rule, and a headline buried in a photo read as old-fashioned inside a modern grid. Do not mix left and right alignment in one block. | The Futur, Satori Graphics, DesignCourse | CLAIM(DLeSPCTA9Wg@02:15), CLAIM(DLeSPCTA9Wg@03:41), CLAIM(DLeSPCTA9Wg@04:28), CLAIM(Tm25IxJQPWM@05:36), CLAIM(DXUC3S-y4E0@03:00), CLAIM(DXUC3S-y4E0@03:23) | consensus |
| 1 | Before redrawing, name the defects in writing. Change only what those defects require. | Satori Graphics | CLAIM(k2DWClcoHFI@06:10) | single-source |
| 3 | When a live brand already works, keep its cues and raise execution. Do not invent a new style unless the brief asks for one. | Flux Academy | CLAIM(iNseBcTOJ58@04:32) | single-source |
| 4 | Run a finished page through six passes in order: cut extras, fix legibility, limit color, lock spacing, unify style, then lift what the pictures and cards say. | Flux Academy | CLAIM(s9XlAUisl8Q@00:16), CLAIM(s9XlAUisl8Q@00:22) | single-source |
| 5 | If the page already follows basic rules, the next critique is boredom: missing imagery, flat type, and no motion. Do not stop at "no errors". | Flux Academy | CLAIM(iNseBcTOJ58@00:09), CLAIM(iNseBcTOJ58@03:03) | single-source |

The full set of 95 laws lives in the sub-skills, plus 3 ungrouped laws below.

## Sub-skills

| sub-skill | file | owns |
|---|---|---|
| critique-six-pass | references/critique-six-pass.md | 15 laws |
| ui-screen-audit | references/ui-screen-audit.md | 12 laws |
| dashboard-chrome-audit | references/dashboard-chrome-audit.md | 11 laws |
| message-match-critique | references/message-match-critique.md | 26 laws |
| good-to-great-lift | references/good-to-great-lift.md | 32 laws |

## Further laws (not yet grouped into a sub-skill)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 1 | Before redrawing, name the defects in writing. Change only what those defects require. | Satori Graphics | CLAIM(k2DWClcoHFI@06:10) | single-source |
| 2 | Prefer the smallest edit that fixes the defect: color, hierarchy, spacing, then imagery. A full restyle is not the first move. | Jesse Showalter, Satori Graphics | CLAIM(XZf5A0wcruE@00:16), CLAIM(k2DWClcoHFI@10:43) | consensus |
| 28 | If navigation type is both too small and too thin, change at least one. Do not ship both defects together. | Flux Academy | CLAIM(s9XlAUisl8Q@01:31) | single-source |

## Looks like / does not (strongest pairs)

| looks like | does not | why | citation |
|---|---|---|---|
| 1 | Primary color only on the submit control | Same pink on icon, label, outline, header, and minor links | If every element shouts, none can lead |
| 2 | Link underlined or otherwise distinct from placeholder | Link set in the same style as placeholder text | The alternate path is invisible |
| 3 | One large sign-in button, register as small text | Two buttons of equal size and weight | The user has to guess which action the page wants |
| 4 | Icon, title, and subhead in one even lockup | Icon hovering just close enough to look accidental | Proximity either groups or it does not |
| 5 | Labels above fields, different from placeholders | No labels, placeholder doing the label's job | States and roles must be readable without guessing |
| 6 | Charts and tables as the focal point, chrome quiet | Giant sidebar and title bar outranking the data | A tool exists to be used, not admired |

Full pair set: the ds-exemplars skill and studio-exemplars/pairs/critique/.

## Decision tables

| decision | pick A when | pick B when | citation |
|---|---|---|---|
| Bright brand color vs restrained neutrals | The screen is marketing and needs one remembered accent | The screen is a tool; data must lead and brand color is noise | CLAIM(XZf5A0wcruE@09:37), CLAIM(iNseBcTOJ58@03:05) |
| Second equal button vs text link | Never for the alternate account path on a sign-in screen | The page's job is one action; the other path is recovery | CLAIM(XZf5A0wcruE@02:51) |
| Box every region vs space and headlines | Regions still collide after color and type are fixed | Chrome has been stripped and repeated headlines already separate the data | CLAIM(XZf5A0wcruE@10:09) |
| Add shadow vs fix contrast | A control must lift off a photographic map and the shadow is faint | Regions are muddy; shadow is hiding a value problem | CLAIM(XZf5A0wcruE@15:36) |
| Keep two-column balance vs shift all type to one side | The offer is already findable and the split is even | The buy control is quiet or the focal image is too small to lead | CLAIM(k2DWClcoHFI@04:56), CLAIM(k2DWClcoHFI@05:28) |
| Sans vs slab serif | The picture is blunt, dirty, or contemporary | The piece is retro or traditional and the photo already implies motion (use italic slab) | CLAIM(k2DWClcoHFI@02:27), CLAIM(k2DWClcoHFI@11:13) |
| Remove Home from nav vs keep a home target | Logo already returns home and the nav is crowded | Users in this audience do not treat the logo as home (test before deleting) | CLAIM(s9XlAUisl8Q@00:29) |
| Stop at correct vs add imagery and motion | The surface is a working tool | The surface is marketing, already correct, and feels blank | CLAIM(iNseBcTOJ58@03:03), CLAIM(XZf5A0wcruE@07:21) |
| Center the lockup vs left-align | The format is small and symmetric (a card) and nothing else occupies a corner | A poster already has its focal mass in one corner; centered small lines fight that mass | CLAIM(bu_UC-9kwiQ@01:44), CLAIM(Tm25IxJQPWM@05:36) |
| Keep the official seal vs simplify the website mark | Print, signage, or a legal lockup | A website nav where three logo lines create an empty band | CLAIM(S1yMcIicf0c@05:46) |
| Same heading style vs a break | Every ordinary section | Only a true call-to-action band that is not another heading | CLAIM(S1yMcIicf0c@09:19), CLAIM(S1yMcIicf0c@16:10) |
| Upscale and recompose a weak photo vs demand a new shoot | The subject is right and only sharpness or crop is wrong | The picture does not mean the sentence (night city for a comfort claim) | CLAIM(S1yMcIicf0c@01:50), CLAIM(S1yMcIicf0c@14:14) |
| Commit the concept vs stay plain | The brand is a game, a riot, or a feeling people should remember | The job is wayfinding; a clean traditional hero with a visible next section is enough | CLAIM(HY_Ea1la6BM@00:17), CLAIM(HY_Ea1la6BM@06:45) |
| Hide work on hover vs show it | The brand is curiosity and the reveal is the point | Anyone else; making people hunt is a fail | CLAIM(HY_Ea1la6BM@05:47) |
| Dense pages vs airy pages | A newspaper or journal whose job is a lot of information | A marketing hero or a tool, where one job must lead | CLAIM(DLeSPCTA9Wg@24:21), CLAIM(XZf5A0wcruE@07:16) |
| Swiss-clean vs expressive type | The system should disappear | The piece is one poster or one cover, and the middle would look undecided | CLAIM(DLeSPCTA9Wg@11:07) |

## Anti-patterns

- Painting the whole form in the action color, then wondering why the button does not lead. CLAIM(XZf5A0wcruE@01:10)
- Two calls to action of equal size on a sign-in screen. CLAIM(XZf5A0wcruE@02:47)
- Dashboard chrome (avatar, logo, the word Dashboard) louder than the charts. CLAIM(XZf5A0wcruE@06:51)
- Brand color forced onto every chart and every badge. CLAIM(XZf5A0wcruE@08:03)
- Logout or price in error red or action blue. CLAIM(XZf5A0wcruE@16:12)
- Heavy drop shadow used because the panel will not stand on color alone. CLAIM(XZf5A0wcruE@15:36)
- Detail type so small and light it should have been omitted. CLAIM(XZf5A0wcruE@15:12)
- Hero that repeats the logo tagline. CLAIM(s9XlAUisl8Q@00:36)
- plus 38 more in references/<sub-skill>.md files

## Creator disagreements (stated, not resolved)

- Marketing spice vs tool quiet. Flux Academy (2023) says a site that already follows the rules still fails if it is boring, and should gain a photo, a contrasting headline face, extra color, and small motion. CLAIM(iNseBcTOJ58@03:05), CLAIM(iNseBcTOJ58@11:08). Jesse Showalter (2024) says dashboards and web apps should often be plainer, and that brand color and decoration must get out of the way of the data. CLAIM(XZf5A0wcruE@07:16), CLAIM(XZf5A0wcruE@09:37). Scope split used in the decision table: marketing pages earn spice after the basics pass; tools do not.
- Layout shifts as taste vs hierarchy as law. Satori Graphics marks enlarging the product and moving all type to one side as subjective; the original two-sided balance was already good enough. CLAIM(k2DWClcoHFI@04:56), CLAIM(k2DWClcoHFI@05:33). Jesse treats equal button weight and undifferentiated type roles as failures, not taste. CLAIM(XZf5A0wcruE@02:44). Rule used here: CTA weight, color reserve, and label treatments are non-negotiable; column rebalance is taste unless it hides the offer.
- Home in the nav. Flux Academy (2025) deletes a Home item because the logo is the convention for returning home, and calls a repeated logo line a waste of the hero. CLAIM(s9XlAUisl8Q@00:29). No second creator in the videos read so far contradicts this inside a critique. Hold it as single-source until a later video argues for an explicit Home label.
- Center vs left. Satori Graphics (2020) centers card content and pulls it off the edges. CLAIM(bu_UC-9kwiQ@01:44). The same creator (2021) says when unsure, align left, and moves centered lines off a wordmark when the figure already owns the top corner. CLAIM(Tm25IxJQPWM@05:36). Scope: center a symmetric small format; left-align a poster whose focal mass is already in a corner.
- Consistency vs a deliberate break. Flux Academy (2024) calls a new heading style per section a junior mistake. CLAIM(S1yMcIicf0c@09:12). Minutes later the same video breaks type consistency on a call-to-action band because it is not another section heading. CLAIM(S1yMcIicf0c@16:06). The break is allowed once, on the band whose job is the ask, not as a license to restyle every block.
- Center vs left, third voice. The Futur (2016) treats centered body type on a modern layout as old-fashioned and wants left alignment, with center reserved for legal lines or a strong display. CLAIM(DLeSPCTA9Wg@02:15), CLAIM(DLeSPCTA9Wg@06:11). That agrees with Satori's 2021 poster rule and conflicts with Satori's 2020 card rule. Scope stands: center a symmetric small format; left-align editorial and posters.
- Air vs density. Jesse Showalter and Flux Academy want tools and heroes to breathe. CLAIM(XZf5A0wcruE@07:16). The Futur wants a newspaper full, with expressive emptiness limited to one or two spreads. CLAIM(DLeSPCTA9Wg@24:21). Scope: density follows the format's job.
- Mystery hero. Jesse Showalter (2024) calls required exploration a usual fail, then shows one studio site where hover-to-reveal is the brand. CLAIM(HY_Ea1la6BM@05:47). DesignCourse (2021) is stricter: a typewriter headline or a console portfolio is extra work, and it must not be the front door for clients or employers. CLAIM(DXUC3S-y4E0@14:34), CLAIM(DXUC3S-y4E0@25:42). Exception only when mystery is the offer, and never on a hiring portfolio.
- Cut vs reorganize. Flux Academy (2025) deletes a Home item, a repeated tagline, and rules that add nothing. CLAIM(s9XlAUisl8Q@00:22). Sam Crawford (2026) says required program facts must stay, moved off the first screen rather than deleted. CLAIM(EA7wnpFAJd4@05:00). Scope: delete decoration and duplicates; demote facts the buyer still needs.
- Full-bleed art vs a fixed web container. The Futur (2016) likes type that bleeds off a modern editorial edge. CLAIM(DLeSPCTA9Wg@03:27). DesignCourse (2021) says a 100 percent fluid web layout on a wide monitor makes sentences unreadable, and wants a centered fixed container. CLAIM(DXUC3S-y4E0@18:28). Scope: bleed is an editorial device; a website on a large screen gets a max width.
- Home label. Flux Academy (2025) still stands alone in deleting Home. CLAIM(s9XlAUisl8Q@00:29). DesignCourse wants the logo left and the links visible, which does not require a Home word. CLAIM(DXUC3S-y4E0@14:08). No creator in this set argues for an explicit Home label.

## Creator claims (unverified)

- Fixing the color abuse on a junior login would multiply effectiveness by ten. Jesse Showalter, 2024. CLAIM(XZf5A0wcruE@00:54)
- Fixing hierarchy on the mid-level login would multiply effectiveness by ten. Jesse Showalter, 2024. CLAIM(XZf5A0wcruE@03:31)
- A six-step edit fixes 80% of the problems on 80% of websites. Flux Academy, 2025. CLAIM(s9XlAUisl8Q@00:01)
- The same school has taught over 10,000 students. Flux Academy, 2025. CLAIM(s9XlAUisl8Q@00:11)
- Moving buried work photos into the hero communicates the trade in a fraction of a second. Flux Academy, 2025. CLAIM(s9XlAUisl8Q@04:25) (the speed claim is the unverified part; the placement law is above)
- A rebuilt mark looks ten times better than the thin original. Satori Graphics, 2020. CLAIM(bu_UC-9kwiQ@07:26)
- Building a quality site probably takes more than a week, even when the offer says seven days. Flux Academy, 2024. CLAIM(PnnbPz6G6gs@00:25)
- Amateur versus professional is not explained by tools, budget, or talent. Flux Academy, 2024. CLAIM(S1yMcIicf0c@00:00) (stance, not a measured result)

## Tool-specific (dated)

- Group a broken lockup with auto layout so gaps are equal. Figma, cited 2024. CLAIM(XZf5A0wcruE@04:33)
- Prototype the redesigned hero on a laptop frame before judging motion. Figma, cited 2023. CLAIM(iNseBcTOJ58@10:54)
- A textured cut of a named display face was used to match a polluted image. Font choice is 2021-specific; the law is the texture match, not the family name. CLAIM(k2DWClcoHFI@03:05)
- Results-row illustrations came from one stock set, recolored. Stock-set dependence is 2023. CLAIM(iNseBcTOJ58@09:14)
- Import a live page with an HTML-to-Figma plugin before critiquing in place. Cited 2024. CLAIM(PnnbPz6G6gs@01:56), CLAIM(S1yMcIicf0c@01:08)
- A 2024 portfolio fix names a free face built on a game-console model as the thing to remove, and a grotesque from a retail foundry as the replacement. The law is quality-face vs novelty-face, not those family names. CLAIM(PnnbPz6G6gs@00:59), CLAIM(PnnbPz6G6gs@04:17)
- Icon search and a calendar-like glyph were used to picture a seven-day offer. Icon library, 2024. CLAIM(PnnbPz6G6gs@06:37)
- Weak hero photos were upscaled, then recomposed with generative fill and a sky swap. Those tool steps are 2024. The law is sharper subject, clear ground for type. CLAIM(S1yMcIicf0c@01:55), CLAIM(S1yMcIicf0c@02:55)
- plus 7 more in the corpus law file studio-corpus/laws/critique.md

## Hand-off
- Next stage: nothing outward without Gate-D. Agent: `ds-critic` (sub: ds-slop-linter).
- Corpus source: studio-corpus/laws/critique.md (regenerate skills with tools/build_skills.py after a corpus refresh).
- Nothing outward (deploy, publish, push) without Gate-D: `ds-pre-publish-gate-d` enforces it once wired.
