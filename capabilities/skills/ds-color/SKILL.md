---
name: ds-color
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate
  (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict.
  Main skill of design-studio-os for color: Build the palette: hue selection, palette construction and roles, usage rules, light and dark conversion, all contrast-verified. 59 laws, 27
  looks-like/does-not pairs distilled from the RIG design YouTube corpus (top-10 subscribed channels
  weighted), every law cited CLAIM(<videoId>@mm:ss). Use when the task names palettes, theming, dark mode, brand color or contrast failures.
tier: main
parent: design-studio-os
activation: "Load at the start of any task that decides color. Entered by the /design-studio command through design-studio-os, by ds-brand-designer, or by the ds-gate-* harness that names this stage."
owner: rig-intelligence
status: Stable
acl: internal
outcome: "design-ux: color.md: seed hue with rationale, palette with role names and values, contrast table (4.5:1 body, 3:1 large and UI), dark-mode mapping, usage rules, with citations or labeled own reasoning on every judgment"
done_when:
  - cmd:python3 tools/claims_check.py studio-skills/skills/ds-color/SKILL.md
  - cmd:python3 tools/check_family.py
quality_floor: 0.6
---

# Color

JEV FIRST, and it binds every task under this skill: an agent whose only context is this excerpt
sends semantic triage, routing and classification to the rig-s1gate Jev path BEFORE any frontier LLM call
(`~/.rig/bin/rig-s1gate check ui.design --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`;
nearest existing rubric: ui.design, advisory until calibrated). When the classifier is unavailable: DEFERRED,
never a guessed verdict. A required signal passes only above 0.9.

## Load surface

Load this skill FIRST, before any design decision, whenever the job touches color. It is an
always-loaded task-start surface, not a deep reference an agent must already know about: the `/design-studio`
command loads `design-studio-os`, which names this skill in its stage routes table; `when-designing-interfaces`
and `when-designing-websites` route design work to that front door; and the meta agent `ds-director` dispatches
`ds-brand-designer`, which loads this skill before its first action. The stage's gate harness
(`ds-gate-craft`, `ds-gate-brief`, `ds-gate-critique` or `ds-gate-ship`) names these requirements, so a session
running that harness loads this file to pass its gate. Paths are relative to `~/Developer/rig-design-studio-os`.

## When to use

Trigger words: "color", "palette", "theme", "dark mode", "contrast". Inside a build this stage runs after the stage that feeds it and
before ds-layout.

## Inputs and output contract

Inputs: the brief, any existing brand color, the accessibility target (WCAG AA default).
Output: color.md: seed hue with rationale, palette with role names and values, contrast table (4.5:1 body, 3:1 large and UI), dark-mode mapping, usage rules.

## Procedure

1. Color brief and hue selection: run the four pre-questions, derive feeling and personality keywords, and pick the hue from audience and cultural evidence rather than preference (see references/color-brief-and-hue-selection.md).
2. Color palette construction: choose a harmony, match tones, build tints and shades, assign neutrals, and lay the result out at 60/30/10 (see references/color-palette-construction.md).
3. Color application rules: the usage contract that makes a palette work in a layout - reserved action color, text values, background extremes, accent discipline, function-first review (see references/color-application-rules.md).
4. Color mode conversion: move a design between light and dark while preserving relationships, contrast and value ordering instead of copying values (see references/color-mode-conversion.md).
5. Color palette operations: keep one authoritative palette with named swatches and exported files so brand color never drifts between tools (see references/color-palette-operations.md).
6. Check the decision tables below for the choices this stage forces.
7. Run the anti-patterns as a final sweep; each surviving one becomes a finding in `ds-critique`.
8. Cite every load-bearing choice (CLAIM copied from this file); label the rest own reasoning.

## Core laws (load-bearing subset)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 2 | Choose the primary hue from the message and the audience, not from the swatch that looks best in isolation. | Satori Graphics, Flux Academy | CLAIM(HKtTNOgfhAU@00:25, Co75kmQtbaA@02:11) | consensus |
| 4 | Test the hue against local meaning before committing: regional customs, political parties, religions, and sports teams all load colors with meaning that the global palette chart does not show. | Flux Academy, Satori Graphics | CLAIM(RBNu4dzaqK8@03:45, HKtTNOgfhAU@07:35, Co75kmQtbaA@02:46, HKtTNOgfhAU@20:47) | consensus |
| 5 | Set saturation and brightness for the age and position of the buyer. A youth brand can carry a full-strength bright hue; the same hue for a mature or premium audience needs saturation pulled well down. | Flux Academy, Satori Graphics | CLAIM(Co75kmQtbaA@05:36, Co75kmQtbaA@06:35, XNkV6m4fosw@05:02) | consensus |
| 8 | Treat the standard hue associations as defaults to confirm or override with customer research: blue for trust and seriousness, green for nature and health, purple for luxury and femininity, orange and yellow for energy, red for attention and danger, black for high end. Generate keyword research on the actual customer base before a logo or brand hue is chosen. | Satori Graphics, Envato Tuts+, Flux Academy | CLAIM(RBNu4dzaqK8@02:14, 2QTHs7QSR9o@13:58, HKtTNOgfhAU@15:40, HKtTNOgfhAU@17:37, HKtTNOgfhAU@17:47, Co75kmQtbaA@02:29) | consensus |
| 9 | Pick the color space at file creation and budget for the medium: RGB for anything that emits light, CMYK for anything printed. Assume printed color returns duller than the screen showed, since very bright screen colors do not survive a four-color press without a spot reference. | Envato Tuts+, Jesse Showalter | CLAIM(2QTHs7QSR9o@10:34, 2QTHs7QSR9o@11:10, 2QTHs7QSR9o@11:44, -4lMJ4is2pE@00:51) | consensus |
| 13 | Name the three modifiers and use them consistently: a tint adds white, a shade adds black, a tone adds gray. | Envato Tuts+, Jesse Showalter, Satori Graphics, Flux Academy | CLAIM(2QTHs7QSR9o@03:24, -4lMJ4is2pE@04:47, HKtTNOgfhAU@26:45, Co75kmQtbaA@02:19) | consensus |
| 17 | Complementary pairs deliver maximum contrast and attention, they jar at full strength, and they read as a naturally balanced pairing that can carry a luxury story when the values are rich. Pair a hue with a tint of its opposite to get four working colors instead of two blunt ones, and make the photography follow the same scheme. | Satori Graphics, Paige Brunton Business, Flux Academy | CLAIM(HKtTNOgfhAU@28:14, HKtTNOgfhAU@28:48, CxXKHiCpKs4@01:02, wnkAguggRCQ@05:18, wnkAguggRCQ@05:59) | consensus |
| 18 | Analogous schemes (neighbors on the wheel) are the low-risk choice for calm, trustworthy, understated brands. They are easy to make work and they read as one family. | Paige Brunton Business, Flux Academy, Envato Tuts+ | CLAIM(CxXKHiCpKs4@01:38, Co75kmQtbaA@14:20, 2QTHs7QSR9o@05:30) | consensus |
| 1 | Answer four questions before opening any software: what limits you (brand rules, print format), what material already exists, what action the viewer must take, what the viewer should feel at the moment of seeing it. | Flux Academy | CLAIM(Co75kmQtbaA@00:41, Co75kmQtbaA@01:20) | single-source |
| 3 | Write two keyword lists before picking a hue: the feeling the viewer should get, then the personality of the design itself. Map those words to one to three colors through published color association references. | Satori Graphics | CLAIM(HKtTNOgfhAU@08:32, HKtTNOgfhAU@10:43, HKtTNOgfhAU@11:19) | single-source |
| 6 | Treat hue as the weakest lever. Brightness and saturation decide whether a palette feels soft or hard, calm or active. | Satori Graphics | CLAIM(XNkV6m4fosw@00:54, HKtTNOgfhAU@04:42, XNkV6m4fosw@01:06) | single-source (two videos, one creator) |
| 7 | Expect the palette to carry only part of the message. Type, imagery and layout have to agree with it or the meaning does not land. | Flux Academy | CLAIM(Co75kmQtbaA@03:23) | single-source |

The full set of 59 laws lives in the sub-skills, plus 57 ungrouped laws below.

## Sub-skills

| sub-skill | file | owns |
|---|---|---|
| color-brief-and-hue-selection | references/color-brief-and-hue-selection.md | 0 laws |
| color-palette-construction | references/color-palette-construction.md | 2 laws |
| color-application-rules | references/color-application-rules.md | 0 laws |
| color-mode-conversion | references/color-mode-conversion.md | 0 laws |
| color-palette-operations | references/color-palette-operations.md | 0 laws |

## Further laws (not yet grouped into a sub-skill)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 1 | Answer four questions before opening any software: what limits you (brand rules, print format), what material already exists, what action the viewer must take, what the viewer should feel at the moment of seeing it. | Flux Academy | CLAIM(Co75kmQtbaA@00:41, Co75kmQtbaA@01:20) | single-source |
| 2 | Choose the primary hue from the message and the audience, not from the swatch that looks best in isolation. | Satori Graphics, Flux Academy | CLAIM(HKtTNOgfhAU@00:25, Co75kmQtbaA@02:11) | consensus |
| 3 | Write two keyword lists before picking a hue: the feeling the viewer should get, then the personality of the design itself. Map those words to one to three colors through published color association references. | Satori Graphics | CLAIM(HKtTNOgfhAU@08:32, HKtTNOgfhAU@10:43, HKtTNOgfhAU@11:19) | single-source |
| 4 | Test the hue against local meaning before committing: regional customs, political parties, religions, and sports teams all load colors with meaning that the global palette chart does not show. | Flux Academy, Satori Graphics | CLAIM(RBNu4dzaqK8@03:45, HKtTNOgfhAU@07:35, Co75kmQtbaA@02:46, HKtTNOgfhAU@20:47) | consensus |
| 5 | Set saturation and brightness for the age and position of the buyer. A youth brand can carry a full-strength bright hue; the same hue for a mature or premium audience needs saturation pulled well down. | Flux Academy, Satori Graphics | CLAIM(Co75kmQtbaA@05:36, Co75kmQtbaA@06:35, XNkV6m4fosw@05:02) | consensus |
| 6 | Treat hue as the weakest lever. Brightness and saturation decide whether a palette feels soft or hard, calm or active. | Satori Graphics | CLAIM(XNkV6m4fosw@00:54, HKtTNOgfhAU@04:42, XNkV6m4fosw@01:06) | single-source (two videos, one creator) |
| 7 | Expect the palette to carry only part of the message. Type, imagery and layout have to agree with it or the meaning does not land. | Flux Academy | CLAIM(Co75kmQtbaA@03:23) | single-source |
| 8 | Treat the standard hue associations as defaults to confirm or override with customer research: blue for trust and seriousness, green for nature and health, purple for luxury and femininity, orange and yellow for energy, red for attention and danger, black for high end. Generate keyword research on the actual customer base before a logo or brand hue is chosen. | Satori Graphics, Envato Tuts+, Flux Academy | CLAIM(RBNu4dzaqK8@02:14, 2QTHs7QSR9o@13:58, HKtTNOgfhAU@15:40, HKtTNOgfhAU@17:37, HKtTNOgfhAU@17:47, Co75kmQtbaA@02:29) | consensus |
| 9 | Pick the color space at file creation and budget for the medium: RGB for anything that emits light, CMYK for anything printed. Assume printed color returns duller than the screen showed, since very bright screen colors do not survive a four-color press without a spot reference. | Envato Tuts+, Jesse Showalter | CLAIM(2QTHs7QSR9o@10:34, 2QTHs7QSR9o@11:10, 2QTHs7QSR9o@11:44, -4lMJ4is2pE@00:51) | consensus |
| 11 | For a website palette land near five colors: at least two of them neutral enough to sit behind content alongside white, a couple of punchier accents, and one contrasting color reserved for the call to action. | Wes McDowell | CLAIM(HMT_7esBbVA@01:54, HMT_7esBbVA@02:05, HMT_7esBbVA@02:13) | single-source |
| 12 | Always keep one very dark neutral for text. It is used sparingly but it has to exist in the palette. | Paige Brunton Business | CLAIM(CxXKHiCpKs4@09:12) | single-source |
| 13 | Name the three modifiers and use them consistently: a tint adds white, a shade adds black, a tone adds gray. | Envato Tuts+, Jesse Showalter, Satori Graphics, Flux Academy | CLAIM(2QTHs7QSR9o@03:24, -4lMJ4is2pE@04:47, HKtTNOgfhAU@26:45, Co75kmQtbaA@02:19) | consensus |
| 14 | Build UI palettes from tints and shades of the primary so that a bold value is available for a button while row highlights and secondary text get the lighter rungs instead of more saturated color. | Jesse Showalter | CLAIM(-4lMJ4is2pE@05:27, -4lMJ4is2pE@05:08) | single-source |
| 15 | Match tones across the whole palette. Colors whose gray content differs will look like they came from different projects no matter how well the hues relate, and a palette of many hues is only safe when every color shares a tone and holds a narrow job. | Flux Academy | CLAIM(wnkAguggRCQ@10:02, wnkAguggRCQ@10:40, wnkAguggRCQ@11:01, Co75kmQtbaA@22:35, Co75kmQtbaA@23:14) | single-source (one channel) |
| 16 | Desaturate any color that competes with the dominant one. Saturation is the dial that decides which color wins the page. | Flux Academy | CLAIM(Co75kmQtbaA@23:54, Co75kmQtbaA@23:56) | single-source |
| 17 | Complementary pairs deliver maximum contrast and attention, they jar at full strength, and they read as a naturally balanced pairing that can carry a luxury story when the values are rich. Pair a hue with a tint of its opposite to get four working colors instead of two blunt ones, and make the photography follow the same scheme. | Satori Graphics, Paige Brunton Business, Flux Academy | CLAIM(HKtTNOgfhAU@28:14, HKtTNOgfhAU@28:48, CxXKHiCpKs4@01:02, wnkAguggRCQ@05:18, wnkAguggRCQ@05:59) | consensus |
| 18 | Analogous schemes (neighbors on the wheel) are the low-risk choice for calm, trustworthy, understated brands. They are easy to make work and they read as one family. | Paige Brunton Business, Flux Academy, Envato Tuts+ | CLAIM(CxXKHiCpKs4@01:38, Co75kmQtbaA@14:20, 2QTHs7QSR9o@05:30) | consensus |
| 19 | Split-complementary keeps contrast but drops the in-your-face quality of a straight complement. It suits brands that want energy without chaos, and it takes more balancing than analogous. | Paige Brunton Business, Satori Graphics, Flux Academy | CLAIM(CxXKHiCpKs4@02:26, HKtTNOgfhAU@30:58, Co75kmQtbaA@15:58) | consensus |
| 20 | Monochromatic is one hue with saturation and lightness varied around it. It moves the eye smoothly and never pops, so use it to keep a brand color dominant across UI states and to signal calm or curation, and do not use it where the design must grab attention (signs, alerts, charts). | Satori Graphics, Jesse Showalter, Paige Brunton Business, Flux Academy | CLAIM(HKtTNOgfhAU@27:17, HKtTNOgfhAU@27:51, -4lMJ4is2pE@09:41, CxXKHiCpKs4@03:18, wnkAguggRCQ@02:50, wnkAguggRCQ@03:32, wnkAguggRCQ@04:41) | consensus |
| 21 | Triadic (three hues evenly spaced) is high contrast and easy to overpower. Take it into charts and infographics and check that no label gets lost in the collision. | Satori Graphics, Envato Tuts+ | CLAIM(HKtTNOgfhAU@30:03, HKtTNOgfhAU@30:33, 2QTHs7QSR9o@07:43) | consensus |
| 22 | Tetradic (two complementary pairs) only works when one hue dominates and the other three stay in accent roles. Four equals means four competitors. | Envato Tuts+ | CLAIM(2QTHs7QSR9o@08:37, 2QTHs7QSR9o@09:02) | single-source |
| 23 | Deliberately vary the blues in one scheme when the brand wants to feel human rather than formal. Uniform values read as institutional. | Flux Academy | CLAIM(wnkAguggRCQ@07:40, wnkAguggRCQ@08:36) | single-source |
| 24 | Warm against cool on the same surface creates dynamic tension. Pick that when the subject is meant to feel unsettled or playful, and avoid it when the subject is meant to feel safe. | Flux Academy | CLAIM(wnkAguggRCQ@18:43, wnkAguggRCQ@19:03) | single-source |
| 25 | Desaturate a vintage or retro read. The same two hues at full digital saturation look like a flag or a cheap product; pulling saturation down makes them look crafted. | Flux Academy | CLAIM(wnkAguggRCQ@20:01, wnkAguggRCQ@21:00, wnkAguggRCQ@14:24) | single-source |
| 26 | Test palette balance with a value check: flatten the colors under a black or gray overlay and confirm each one shows a distinct value instead of collapsing into the same gray. | Envato Tuts+ | CLAIM(2QTHs7QSR9o@17:12, 2QTHs7QSR9o@17:22) | single-source |
| 27 | Derive neutrals from a palette hue rather than defaulting to pure black and white. A tinted neutral keeps the whole scheme in one family. | Envato Tuts+, DesignCourse, Flux Academy | CLAIM(2QTHs7QSR9o@17:51, 2QTHs7QSR9o@19:52, wqTZuEQ2P-s@01:59, Co75kmQtbaA@07:22) | consensus |
| 28 | Apply the 60/30/10 proportion: dominant color about sixty percent of the surface, secondary thirty, accent ten. The sixty percent band may be two shades of one color, which keeps a single dominant read while still varying the layout. | Flux Academy, Paige Brunton Business | CLAIM(vo_lUWK_deo@02:13, CxXKHiCpKs4@05:08, CxXKHiCpKs4@10:10, Co75kmQtbaA@32:53) | consensus |
| 29 | A near-white is a workable neutral for large fields. It gives the content breathing room so the page does not turn into a wall of color. | Wes McDowell, Flux Academy | CLAIM(HMT_7esBbVA@10:10, wnkAguggRCQ@06:10) | consensus |
| 31 | Body copy is black or a very dark gray. Colored type is acceptable in headlines, never at reading size. | Wes McDowell, Flux Academy | CLAIM(HMT_7esBbVA@13:27, Co75kmQtbaA@08:56) | consensus |
| 32 | Never put bolder colors on large background fields. Keep surfaces white or neutral and spend the bold colors in small doses: icons, rules, headlines, buttons. | Wes McDowell | CLAIM(HMT_7esBbVA@12:57, HMT_7esBbVA@13:14) | single-source |
| 33 | Keep interface backgrounds at the extremes: a very light off-white or a very dark off-black. Mid-value surfaces kill contrast and make every element work harder. | Flux Academy | CLAIM(wnkAguggRCQ@06:10) | single-source |
| 34 | A gray control reads as disabled. Never let an enabled button or link sit in gray, because users will not attempt to click it. | Flux Academy | CLAIM(RBNu4dzaqK8@05:12, RBNu4dzaqK8@05:33) | single-source |
| 35 | In interface work, red and green already carry a stop and go reading. That functional meaning outranks whatever the brand book says the color means. | Flux Academy | CLAIM(RBNu4dzaqK8@05:46, RBNu4dzaqK8@06:04) | single-source |
| 36 | Spend one accent color on orientation: active nav state, current position, the first phrase of a scannable block. Small marks are enough to guide the eye, and one accent is also how a near-monochrome scheme gets a point of difference without adding a second hue family. | Flux Academy | CLAIM(wnkAguggRCQ@00:43, wnkAguggRCQ@00:55, wnkAguggRCQ@02:15, wnkAguggRCQ@00:24, wnkAguggRCQ@18:20) | single-source |
| 37 | Diagnose in grayscale before blaming color. Convert the layout to black and white: if the hierarchy still works the problem is color application, and if it does not the problem is layout. | Flux Academy | CLAIM(vo_lUWK_deo@01:15, vo_lUWK_deo@01:44) | single-source |
| 38 | Do not color separate blocks and separate lines of type differently in one layout. It fragments the reading path instead of guiding it. | Flux Academy | CLAIM(vo_lUWK_deo@00:58) | single-source |
| 39 | Small type needs both saturation and contrast raised to stay legible. Muted values that work at display size disappear at caption size. | Satori Graphics | CLAIM(XNkV6m4fosw@05:51) | single-source |
| 40 | Raise contrast and saturation to signal activity; lower both to signal calm. A low saturation, weak contrast build is how you say safe and settled. | Satori Graphics | CLAIM(XNkV6m4fosw@01:06, XNkV6m4fosw@01:34, HKtTNOgfhAU@05:21) | single-source (one creator, two videos) |
| 41 | When the product photography is loud, keep the interface quiet. Let the product carry the color, hold the UI near neutral with one accent, and do not pass every brand color into the interface just because the brand owns them. | Flux Academy | CLAIM(Co75kmQtbaA@29:00, Co75kmQtbaA@30:28, Co75kmQtbaA@27:12, Co75kmQtbaA@28:20, Co75kmQtbaA@36:30) | single-source |
| 42 | Write usage rules into the brand guidelines: which color is dominant, which is secondary, which is accent, and what each may be applied to. Without that, every deliverable will drift toward the brightest color. | Flux Academy | CLAIM(Co75kmQtbaA@32:28, Co75kmQtbaA@34:21) | single-source |
| 43 | Review the finished work in two passes. First function: does the color support the information, lead to the intended action, stay legible and consistent, and guide the viewer. Then appeal: does it look like something a person wants to engage with. | Flux Academy | CLAIM(Co75kmQtbaA@35:09, Co75kmQtbaA@38:20) | single-source |
| 44 | Match the accent palette to the subject matter so the color itself helps the reader choose (flavor codes, product codes). It is navigation disguised as decoration. | Flux Academy | CLAIM(Co75kmQtbaA@35:34, Co75kmQtbaA@36:22) | single-source |
| 45 | Keep one or two colors on a logo. A multi-hue logo is defensible only when the designer can explain every hue's job. | Satori Graphics | CLAIM(HKtTNOgfhAU@19:04, HKtTNOgfhAU@19:41) | single-source |
| 46 | Avoid both ends of the value range on page surfaces. A dark surface is never pure black: keep the tint the real fill carries and build the light version one rung brighter from it. A light page background is never pure white, because a card needs headroom to read as elevated. | DesignCourse | CLAIM(wqTZuEQ2P-s@01:33, wqTZuEQ2P-s@01:44, wqTZuEQ2P-s@01:59, wqTZuEQ2P-s@02:23) | single-source |
| 47 | Convert a mode starting with the largest surfaces and working down to the smallest details: page fill, then cards, then type, then strokes and shadows. | DesignCourse | CLAIM(Y8g3YtZckco@00:56, Y8g3YtZckco@01:18) | single-source |
| 48 | Preserve relationships, not values. Card stays one step lighter than the page, icon keeps matching the stroke it sits beside, whatever was high contrast in one mode stays high contrast in the other, and thin borders or rules that read on a dark ground must be pushed darker to survive a light one. | DesignCourse | CLAIM(wqTZuEQ2P-s@02:11, wqTZuEQ2P-s@03:06, wqTZuEQ2P-s@04:27, wqTZuEQ2P-s@02:26, wqTZuEQ2P-s@03:27) | single-source |
| 49 | Re-derive each shadow from the surface it falls on instead of copying the value across modes. A dark-mode shadow carried into light mode looks dirty and wrong. | DesignCourse | CLAIM(Y8g3YtZckco@02:51, Y8g3YtZckco@03:04) | single-source |
| 50 | Remap every instance of one color in a single edit through the selection color panel rather than hunting elements one at a time. Verify the panel shows the color you think you are changing. | DesignCourse | CLAIM(wqTZuEQ2P-s@07:03, Y8g3YtZckco@02:10) | single-source (one creator, two videos) |
| 51 | In a mode conversion change colors and values only. Do not move the layout and do not add shadows, gradients or other embellishments. | DesignCourse | CLAIM(wqTZuEQ2P-s@13:00, Y8g3YtZckco@05:15) | single-source (one creator, two videos) |
| 52 | Label the theme toggle with a text label or a moon icon so its state is readable at a glance. An unlabeled pill is ambiguous. | DesignCourse | CLAIM(wqTZuEQ2P-s@10:43) | single-source |
| 53 | Do the conversion by hand with an eye on contrast. Automated color inversion will not hold the type legibility or the tonal relationships. | DesignCourse | CLAIM(Y8g3YtZckco@00:15, Y8g3YtZckco@06:01) | single-source |
| 54 | Never maintain a brand color by sampling it out of an image or an export. Sampling drifts and you end up with twenty near-identical blues. | CharliMarieTV | CLAIM(zl_7yHh2PSc@00:29, zl_7yHh2PSc@00:36) | single-source |
| 55 | Store the palette as named swatches in a folder, name each swatch with its hex value so a developer can read the code off the swatch list, and make anything used across the document a global swatch so one edit recolors every element that uses it. | CharliMarieTV, Satori Graphics | CLAIM(zl_7yHh2PSc@03:41, zl_7yHh2PSc@04:56, F_XiBUXY8cU@04:51, HKtTNOgfhAU@14:26) | consensus |
| 56 | Export the palette as a swatch exchange file from the design tool first. Converting that format to the platform native one is far easier than the reverse. | CharliMarieTV | CLAIM(zl_7yHh2PSc@03:01, zl_7yHh2PSc@04:46) | single-source |
| 57 | A working brand palette needs ramps, not single values: several shades of the primary for icons over colored ground and for buttons, several shades of the light neutral, several shades of the dark neutral for text. | CharliMarieTV | CLAIM(zl_7yHh2PSc@00:50, zl_7yHh2PSc@01:15, zl_7yHh2PSc@01:21) | single-source |
| 58 | When a color has to survive another person's screen or a press, carry a spot reference rather than a screen value. The reference is what makes the color reproducible. | Satori Graphics | CLAIM(PjreouILiAY@01:12, 2QTHs7QSR9o@12:01) | consensus |
| 59 | Build the palette on a written base color drawn from research, then cycle harmony rules against it rather than improvising hues. | Satori Graphics, Envato Tuts+ | CLAIM(HKtTNOgfhAU@11:55, HKtTNOgfhAU@12:12, 2QTHs7QSR9o@16:45) | consensus |

## Looks like / does not (strongest pairs)

| looks like | does not | why | citation |
|---|---|---|---|
| 1 | The same card layout redrawn with a neutral cream ground, dark type and one orange button that carries the action. | The card with brand green behind the mark, orange headline on green, a button that blends in, and three differently colored blocks stacked down the page. | Equal-weight color blocks fragment the reading path; a proportioned palette directs it. |
| 2 | A layout that still reads when everything is set to gray. | A layout that falls apart in gray and only appears to work once color is applied. | Grayscale exposes a hierarchy problem that color was hiding. |
| 3 | One dominant green running through header, image overlay and sections, dark neutral for text, the boldest hue only on buttons. | The same five colors split into equal thirds, a muted button that does not stand out, footer links nearly invisible on a dark ground. | If nothing dominates, nothing is dominant and the eye has no entry point. |
| 4 | Red softened to a pink and green desaturated and darkened until the pair sits comfortably. | A vibrant red next to a vibrant green at full strength. | Complements at full saturation vibrate and read as unpleasant. |
| 5 | A muted, low saturation palette on an upmarket fashion piece. | The identical layout rebuilt in loud saturated color for a teenage audience. | Saturation and brightness carry the market position more than the hues do. |
| 6 | Skincare advertising carried in pale skin tones and pastels. | The same artwork with saturation cranked up. | High saturation reads aggressive and contradicts a calm beauty product. |

Full pair set: the ds-exemplars skill and studio-exemplars/pairs/color/.

## Decision tables

### Harmony choice

| Option A | Option B | Pick A when | Pick B when | citation |
|----------|----------|-------------|-------------|----------|
| Complementary | Analogous | You need contrast, drama, and a button or headline that separates from the ground. | You need calm, cohesion, and a brand that should whisper rather than shout. | CLAIM(CxXKHiCpKs4@01:02, CxXKHiCpKs4@01:38) |
| Split-complementary | Straight complementary | You want energy without the harshness of a direct opposite pair. | Maximum contrast matters more than comfort and the content can carry the intensity. | CLAIM(CxXKHiCpKs4@02:26, HKtTNOgfhAU@28:14) |
| Monochromatic | Triadic | The goal is calm, curation, and one dominant brand hue. | The design needs to grab attention (charts, infographics, signage) and can survive the collision. | CLAIM(HKtTNOgfhAU@27:51, HKtTNOgfhAU@30:03) |
| One hue plus black and white | Five-color palette | The project is small and the risk of mistakes has to stay near zero. | The interface needs states, sections and a dedicated action color. | CLAIM(Co75kmQtbaA@10:32, HMT_7esBbVA@01:54) |
| Tetradic with one dominant | Tetradic at equal weight | You can commit to one hue owning the frame and three staying in accent roles. | Never. Four equal hues read as four competitors. | CLAIM(2QTHs7QSR9o@08:37, 2QTHs7QSR9o@09:02) |

### Value and proportion

| Option A | Option B | Pick A when | Pick B when | citation |
|----------|----------|-------------|-------------|----------|
| Desaturate the competing color | Raise contrast between them | Two hues are fighting for the same attention. | One element genuinely has to win the frame. | CLAIM(Co75kmQtbaA@23:54, XNkV6m4fosw@01:06) |
| 60/30/10 | Flat equal distribution | Any layout with a clear primary action or reading order. | Never in client work; it removes the hierarchy entirely. | CLAIM(CxXKHiCpKs4@05:08, CxXKHiCpKs4@10:28) |
| Tinted neutral for surfaces | Pure black or pure white | The palette must feel like one family and needs room for elevation. | The brand explicitly runs a hard black-and-white identity. | CLAIM(2QTHs7QSR9o@17:51, wqTZuEQ2P-s@01:59) |
| Bold color in small doses | Bold color as a field | The content needs breathing room and the action needs to stand out. | The brand identity is itself a bold color block and the copy is minimal. | CLAIM(HMT_7esBbVA@12:57) |
| Black or dark gray body text | Colored body text | Always, at reading size. | Headlines and display type only. | CLAIM(HMT_7esBbVA@13:27, Co75kmQtbaA@08:56) |

### Mode conversion

| Option A | Option B | Pick A when | Pick B when | citation |
|----------|----------|-------------|-------------|----------|
| Tinted off-white page background | Pure white page background | A card must sit above the page and read as a separate layer. | There are no layered surfaces at all. | CLAIM(wqTZuEQ2P-s@01:59) |
| Push the border darker in light mode | Keep the border value unchanged | The border needs to keep the contrast it had in the dark version. | Never; unchanged values lose their relationship to the ground. | CLAIM(wqTZuEQ2P-s@02:26) |
| Rebuild shadows from the surface | Reuse the shadow value | Always in a mode change. | Never. | CLAIM(Y8g3YtZckco@02:51) |
| Colors and values only | Layout and embellishment changes too | Always in a mode change; the brief is a color exercise. | A genuine redesign, which is a different job. | CLAIM(wqTZuEQ2P-s@13:00, Y8g3YtZckco@05:15) |

## Anti-patterns

- Equal thirds of three colors across a layout with no dominant. CLAIM(CxXKHiCpKs4@10:28)
- A call to action painted in a muted color that blends into the surface. CLAIM(CxXKHiCpKs4@10:46)
- Footer or secondary links set at almost no contrast against a dark ground. CLAIM(CxXKHiCpKs4@11:32)
- Bold color blocking filling large background areas. CLAIM(HMT_7esBbVA@12:57)
- Brand color used for body copy. CLAIM(HMT_7esBbVA@13:27)
- The reserved action color reused anywhere other than the action. CLAIM(HMT_7esBbVA@13:44)
- A gray control for an action that is available. CLAIM(RBNu4dzaqK8@05:12)
- Choosing a hue that contradicts the category the product sits in. CLAIM(RBNu4dzaqK8@00:56)
- plus 9 more in references/<sub-skill>.md files

## Creator disagreements (stated, not resolved)

- **Does red help or hurt a call to action.** Satori Graphics cites a test where a red button beat a green one on click-through by twenty-one percent (CLAIM(XNkV6m4fosw@03:09)); Flux Academy (Ran) argues a red buy-now button reads as danger and makes people wary of clicking (CLAIM(RBNu4dzaqK8@06:04)). Flux Academy (Matt) elsewhere points at a red signup button on an otherwise monochrome site as the correct way to draw the eye (CLAIM(Co75kmQtbaA@37:36)). Reading: red reliably attracts attention; whether it converts depends on the functional reading of the context, so test it rather than adopting either rule.
- **What a tone is.** Envato Tuts+ defines a tone as the hue with gray added (CLAIM(2QTHs7QSR9o@03:36)); Satori Graphics defines it as the hue with both white and black added (CLAIM(HKtTNOgfhAU@26:54)); Flux Academy describes it as tint and shade together, roughly adding gray (CLAIM(Co75kmQtbaA@23:14)). Reading: all three arrive at the same desaturated mid-value; the practical rule is law 16 as stated by Envato, and the disagreements are definitional rather than behavioural.
- **How many colors.** Wes McDowell wants about five including two neutrals for a website (CLAIM(HMT_7esBbVA@01:54)); Flux Academy wants the fewest that work and shows one hue plus black and white as a complete scheme (CLAIM(Co75kmQtbaA@10:06)); Satori Graphics says one or two colors is the safe bet for a logo (CLAIM(HKtTNOgfhAU@19:04)). Reading: these are scopes rather than contradictions. Logo one to two, small site one plus neutrals, interface five.
- **How much weight color psychology carries.** Satori Graphics treats color psychology as near-universal and dismisses skeptics (CLAIM(HKtTNOgfhAU@09:41)); Flux Academy says you cannot rely on any one element and that a hue alone does not create the feeling (CLAIM(Co75kmQtbaA@03:23)); Flux Academy (Matt) notes people disagree about color psychology but accepts that meaning exists within a cultural context (CLAIM(wnkAguggRCQ@11:34)). Reading: use association as a starting hypothesis to be checked against the audience, never as a mechanism claim on its own.
- **Whether monochrome can carry a brand.** Satori Graphics says monochrome never pops and should not be used where attention is needed (CLAIM(HKtTNOgfhAU@27:51)); Flux Academy uses a monochrome scheme precisely to make one brand hue dominate a racing driver's site (CLAIM(wnkAguggRCQ@03:42)). Reading: both hold. Monochrome concentrates a brand color without competing hues and simultaneously removes contrast-based attention-grabbing.

## Creator claims (unverified)

- Roughly nine in ten consumers judge a brand on color alone, attributed to unspecified studies. CLAIM(XNkV6m4fosw@00:00)
- A 1974 study by K.W. Jacobs found red more stimulating than green and green more than blue, with measurable heart-rate effects. CLAIM(XNkV6m4fosw@00:18)
- A 1981 study attributed to Richard Cooler found color affects EEG readings, heart rate and emotional perception of objects. CLAIM(XNkV6m4fosw@00:32)
- A HubSpot test found a red call-to-action button beating a green one by twenty-one percent click-through. CLAIM(XNkV6m4fosw@03:09, HKtTNOgfhAU@06:56)
- Studies show women prefer softer pastel colors and men prefer bolder ones, presented as an average only. CLAIM(XNkV6m4fosw@04:07)
- Seventy-eight percent of people who encountered Cadbury on Facebook were female, used to explain the purple branding. CLAIM(HKtTNOgfhAU@17:58)
- Nine out of ten designers struggle to choose colors because they lack a defined process. CLAIM(Co75kmQtbaA@00:00)
- A printed reference color wheel cost about ten dollars and shows complement, split complement, tetrad, analogous and triad relations. CLAIM(HKtTNOgfhAU@22:04)

## Tool-specific (dated)

- Adobe Illustrator: shift-click the color swatch area to open sliders, then shift-drag to move all channels together for fast tints and highlights (2019, repeated 2023). CLAIM(F_XiBUXY8cU@01:15, HKtTNOgfhAU@13:04)
- Adobe Illustrator: a complement command inside the color panel returns the opposite on the wheel (2019, repeated 2023). CLAIM(F_XiBUXY8cU@02:34, HKtTNOgfhAU@13:33)
- Adobe Illustrator: the Edit Colors menu converts a whole selection to grayscale or other presets in one action (2019, repeated 2023). CLAIM(F_XiBUXY8cU@04:06, HKtTNOgfhAU@14:00)
- Adobe Illustrator: global swatches are created from the swatches panel with the global box checked and recolor every usage when edited (2019, repeated 2023). CLAIM(F_XiBUXY8cU@04:51, HKtTNOgfhAU@14:26)
- Adobe Illustrator Recolor Artwork with the link icon checked shifts a whole scheme at once (2023). CLAIM(HKtTNOgfhAU@23:19)
- Photoshop: a hue and saturation adjustment layer with the eyedropper targets a color range with no masking (2023). CLAIM(HKtTNOgfhAU@25:57)
- Adobe Color explore accepts a keyword and returns themed schemes; a saved theme lands in the Illustrator libraries panel and can be added to swatches (2017, 2022, 2023). CLAIM(ZBpMMD4Pyyk@01:17, ZBpMMD4Pyyk@03:21, Co75kmQtbaA@12:54, HKtTNOgfhAU@21:08)
- Coolors: pull a palette from a logo image, lock the colors you want to keep, and regenerate the rest on the spacebar (2021). CLAIM(HMT_7esBbVA@03:16, HMT_7esBbVA@04:24)
- plus 7 more in the corpus law file studio-corpus/laws/color.md

## Hand-off
- Next stage: ds-layout. Agent: `ds-brand-designer` (sub: ds-contrast-checker).
- Corpus source: studio-corpus/laws/color.md (regenerate skills with tools/build_skills.py after a corpus refresh).
- Nothing outward (deploy, publish, push) without Gate-D: `ds-pre-publish-gate-d` enforces it once wired.
