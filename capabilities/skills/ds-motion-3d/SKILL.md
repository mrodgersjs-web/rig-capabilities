---
name: ds-motion-3d
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate
  (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict.
  Main skill of design-studio-os for motion and 3d: Design movement with a purpose and a budget: micro-interactions, scroll narrative, 3D and WebGL, reduced-motion respected. 50 laws, 24
  looks-like/does-not pairs distilled from the RIG design YouTube corpus (top-10 subscribed channels
  weighted), every law cited CLAIM(<videoId>@mm:ss). Use when the brief calls for animation, micro-interactions, scroll narrative, 3D or WebGL.
tier: main
parent: design-studio-os
activation: "Load at the start of any task that decides motion and 3d. Entered by the /design-studio command through design-studio-os, by ds-motion-designer, or by the ds-gate-* harness that names this stage."
owner: rig-intelligence
status: Stable
acl: internal
outcome: "design-ux: motion.md: per-animation purpose, duration and easing from the budget, reduced-motion fallback, performance estimate, with citations or labeled own reasoning on every judgment"
done_when:
  - cmd:python3 ../rig-design-studio-os/tools/claims_check.py capabilities/skills/ds-motion-3d/SKILL.md
  - cmd:python3 ../rig-design-studio-os/tools/check_family.py
quality_floor: 0.6
---

# Motion and 3D

JEV FIRST, and it binds every task under this skill: an agent whose only context is this excerpt
sends semantic triage, routing and classification to the rig-s1gate Jev path BEFORE any frontier LLM call
(`~/.rig/bin/rig-s1gate check ui.design --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`;
nearest existing rubric: ui.design, advisory until calibrated). When the classifier is unavailable: DEFERRED,
never a guessed verdict. A required signal passes only above 0.9.

## Load surface

Load this skill FIRST, before any design decision, whenever the job touches motion and 3d. It is an
always-loaded task-start surface, not a deep reference an agent must already know about: the `/design-studio`
command loads `design-studio-os`, which names this skill in its stage routes table; `when-designing-interfaces`
and `when-designing-websites` route design work to that front door; and the meta agent `ds-director` dispatches
`ds-motion-designer`, which loads this skill before its first action. The stage's gate harness
(`ds-gate-craft`, `ds-gate-brief`, `ds-gate-critique` or `ds-gate-ship`) names these requirements, so a session
running that harness loads this file to pass its gate. Paths are relative to `~/Developer/rig-design-studio-os`.

## When to use

Trigger words: "animation", "motion", "micro-interaction", "3D", "WebGL", "scroll effects". Inside a build this stage runs after the stage that feeds it and
before ds-imagery, ds-build-ship.

## Inputs and output contract

Inputs: the moments worth animating, the performance budget, the platform capabilities.
Output: motion.md: per-animation purpose, duration and easing from the budget, reduced-motion fallback, performance estimate.

## Procedure

1. Prototype state machine: board the beats, name the layers, build variants, and wire only the gesture that should fire (see references/prototype-state-machine.md).
2. Micro interaction timing: pick duration, easing, and one signal per beat, then preview until the overshoot and the simultaneous start are gone (see references/micro-interaction-timing.md).
3. Scroll scrub and 3d: sticky gaps, a scrubbed product clip, and transforms or meshes that do not reflow the page (see references/scroll-scrub-and-3d.md).
4. Social motion graphic: size the canvas, stage a two-beat story, style type, and lock audio length, including a recolor of a black-field clip (see references/social-motion-graphic.md).
5. Material motion handoff: stroke-icon paths, soft materials, extruded light, atmospheric noise, and a clean send into a timeline app (see references/material-motion-handoff.md).
6. Check the decision tables below for the choices this stage forces.
7. Run the anti-patterns as a final sweep; each surviving one becomes a finding in `ds-critique`.
8. Cite every load-bearing choice (CLAIM copied from this file); label the rest own reasoning.

## Core laws (load-bearing subset)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 1 | Draw every beat as a named state before you connect anything: one frame or segment per rest, hover, press, or destination. A component set, a variant list, or a timeline cut at the moment the action changes all count. Do not invent the path while you are wiring arrows. | Flux Academy, Jesse Showalter, Punit Chawla | CLAIM(20IfkyJigKg@00:49, 20IfkyJigKg@01:54, 4YFRYho3vuM@02:28, d5ngkWU2TY8@00:54, d5ngkWU2TY8@02:38, K0Dh-8rHMLk@04:08, P8hh8K1EuWE@01:14) | consensus |
| 6 | Match the trigger to the act. Click, drag, hover, or a directional press should be what the person does. Use after-delay or on-load only for a settle or a loop that must start without a second tap. | Flux Academy, Jesse Showalter, Punit Chawla | CLAIM(hHp4FGVcHjY@04:14, hHp4FGVcHjY@04:31, vCru1T5ajF8@03:54, 20IfkyJigKg@07:44, d5ngkWU2TY8@04:36, fB7h2RxXpqA@08:12, K0Dh-8rHMLk@05:06, gXOY8Ts44dA@08:01) | consensus |
| 7 | Preview in a named flow, name the fault (knob leaving the track, a radius pop, a linear loop), change that one property, and preview again. Do not lock the first easing guess. | Flux Academy, kwoo studio, Envato Tuts+ | CLAIM(hHp4FGVcHjY@10:41, hHp4FGVcHjY@10:49, 20IfkyJigKg@09:34, 20IfkyJigKg@16:26, -QuzxYtwkyU@09:46, 8D6b3McyhhU@03:49, 8D6b3McyhhU@04:00) | consensus |
| 8 | Write the motion strategy before the timeline: a board of frames for a UI story, or research-backed intent for a brand system. Opening the editor with no path means you animate blind. | Flux Academy, kwoo studio | CLAIM(20IfkyJigKg@00:49, 20IfkyJigKg@02:00, -QuzxYtwkyU@12:06, -QuzxYtwkyU@12:26) | consensus |
| 13 | Keep a tap or a card drag near 100 to 300 ms. A hover grow can run near 450 ms, a drag that also shifts a gradient near 500 ms. Stretch past that only when the path is the content: a line draw near 3 seconds, a readable text slider near 800 ms, a liquid fill near 4 to 5 seconds, or a scroll gap tall enough to hold the beat. | Flux Academy, Punit Chawla, Jesse Showalter | CLAIM(hHp4FGVcHjY@04:00, hHp4FGVcHjY@04:42, vCru1T5ajF8@11:07, vCru1T5ajF8@04:08, vCru1T5ajF8@17:10, fB7h2RxXpqA@08:44, fB7h2RxXpqA@12:23, EEj3PYjwyC0@05:15, K0Dh-8rHMLk@05:38, P8hh8K1EuWE@04:34) | consensus |
| 15 | Do not ship linear motion. Use ease-out on a drag or an arrival, ease-in-out on a tap or a loop, and a spring only on a physical knob. If the spring leaves the track, shrink the knob and lower the damping until it kisses the edge and settles inside. | Flux Academy, Jesse Showalter, kwoo studio, Punit Chawla | CLAIM(4YFRYho3vuM@03:04, hHp4FGVcHjY@07:43, hHp4FGVcHjY@09:17, hHp4FGVcHjY@10:08, gXOY8Ts44dA@09:00, gXOY8Ts44dA@09:07, -QuzxYtwkyU@09:46, -QuzxYtwkyU@10:08, K0Dh-8rHMLk@05:25, K0Dh-8rHMLk@05:31, fB7h2RxXpqA@08:36) | consensus |
| 19 | Stagger the start. Offset layer timing so the group does not depart on one frame, and give inner chips of a 3D hover different loop offsets so they do not move as one slab. | kwoo studio, Jesse Showalter | CLAIM(-QuzxYtwkyU@10:47, -QuzxYtwkyU@10:54, -QuzxYtwkyU@11:00, gXOY8Ts44dA@04:10, gXOY8Ts44dA@08:22, gXOY8Ts44dA@08:32) | consensus |
| 35 | Kill hard edges on soft effects. Feather a smoke mask by hundreds of pixels, fade a scrubbed clip into the page, and build soft shadow with blur rather than a crisp stroke. | Envato Tuts+, Self-Made Web Designer, Punit Chawla | CLAIM(ptQ6Re6JvWM@07:45, ptQ6Re6JvWM@07:51, ptQ6Re6JvWM@08:01, q5UFK4ziDuE@08:39, fB7h2RxXpqA@02:29, fB7h2RxXpqA@02:41) | consensus |
| 2 | Give every layer that must morph the same name in every state. A matcher only interpolates layers it can pair. A long chain with default names becomes unreadable, so rename before the chain grows. | Flux Academy | CLAIM(hHp4FGVcHjY@02:26, hHp4FGVcHjY@14:51, vCru1T5ajF8@13:25, 20IfkyJigKg@05:13) | single-source |
| 3 | Leave the arriving property in the start state even when it is invisible: a fill at 0 percent, a mask parked just outside the shape, or the incoming chips sitting below a clipped frame. If the layer is missing from the previous frame, it pops or fades instead of traveling. | Flux Academy | CLAIM(hHp4FGVcHjY@02:21, hHp4FGVcHjY@02:45, vCru1T5ajF8@03:04, 20IfkyJigKg@16:45, 20IfkyJigKg@16:57) | single-source |
| 4 | Connect drag or click only between neighboring states. A finger cannot jump from the far-left card to the far-right card in one swipe, so do not draw that arrow. | Flux Academy | CLAIM(4YFRYho3vuM@03:39, 4YFRYho3vuM@03:48, vCru1T5ajF8@11:38, vCru1T5ajF8@12:06) | single-source |
| 5 | Put the prototype on the component, then drop instances into the screen. One timing fix on the main component updates every copy. | Flux Academy | CLAIM(hHp4FGVcHjY@06:02, hHp4FGVcHjY@09:46, 4YFRYho3vuM@04:17) | single-source |

The full set of 50 laws lives in the sub-skills.

## Sub-skills

| sub-skill | file | owns |
|---|---|---|
| prototype-state-machine | references/prototype-state-machine.md | 20 laws |
| micro-interaction-timing | references/micro-interaction-timing.md | 7 laws |
| scroll-scrub-and-3d | references/scroll-scrub-and-3d.md | 11 laws |
| social-motion-graphic | references/social-motion-graphic.md | 6 laws |
| material-motion-handoff | references/material-motion-handoff.md | 6 laws |

## Looks like / does not (strongest pairs)

| looks like | does not | why | citation |
|---|---|---|---|
| 1 | A board of named states drawn before any arrow | One screen, with the path invented while prototyping | You cannot animate a story you have not mapped |
| 2 | Drag arrows only between neighboring carousel states | A single drag from the far-right card straight to the far-left card | A finger cannot skip the middle card |
| 3 | Fill present at 0 percent in the empty state, then rising as the icon grows | Fill added only on the last frame, so the color pops | Interpolation needs the same layer in both states |
| 4 | One tap grows the icon, then a 1 ms delay settles it | A second click required to finish the bounce | The settle is not a user decision |
| 5 | Knob shrunk so a spring hits the track edge and returns inside | Default bounce that leaves the pill | Overshoot past the container reads as a bug |
| 6 | Plus rotates into a minus, color held constant | Plus that changes shape and color in the same beat | Two signals at once feel jarring |

Full pair set: the ds-exemplars skill and studio-exemplars/pairs/motion_3d/.

## Decision tables

| decision | option A | option B | pick when |
|----------|----------|----------|-----------|
| Trigger | click, drag, hover, or a directional press | after-delay or on-load | A when a person acts; B when the next beat should fire alone |
| Easing | ease-out or ease-in-out, under about 500 ms | spring, or a curve handle past the baseline | Spring or overshoot only for a physical knob or a playful entrance |
| Duration | under 500 ms | 800 ms to 5 s, or a tall scroll gap | Short for taps and drags; long only when the path itself is the content |
| In-between | place the object in the previous state so it travels | let the tool tween the gap | Author the path when travel must be seen; tween only when a blend is enough |
| Scroll effect | sticky block plus gap frames and variants | a scrubbed clip between two frames | Sticky variants when the content is layout states; a scrubbed clip when a product transforms |
| Depth | transform scale, rotate, perspective | changing width, height, or position in the layout | Transforms when neighbors must stay put |
| 3D meaning | CSS-style transforms on flat cards | a mesh (extrude, displace) or a scrubbed film | Transforms for hover depth; a mesh or a film when the object itself must change volume |
| Social canvas | 1080 by 1350 feed | 1080 by 1920 reel | Match the slot you will post to |
| Reuse vs build | screen-blend a black-field clip and recolor it | build named states yourself | Reuse only for a feed graphic you will recolor; build states for a product control |
| Page before motion | strip type, color, and space first | animate a busy layout | Always strip first if the goal is a costly-looking marketing site |

## Anti-patterns

- Connecting non-adjacent carousel states with one drag. CLAIM(4YFRYho3vuM@03:48)
- Deleting a layer in the start state and expecting a fade or a travel. CLAIM(hHp4FGVcHjY@02:45, 20IfkyJigKg@16:45)
- Leaving a spring so strong the knob exits the track. CLAIM(hHp4FGVcHjY@10:00)
- Recoloring an icon in the same moment it changes shape. CLAIM(hHp4FGVcHjY@15:46)
- Animating stroke radius and opacity together on an expanding panel. CLAIM(hHp4FGVcHjY@17:03)
- Cycling headline words in strict size order. CLAIM(vCru1T5ajF8@25:38)
- Returning a back control to the hover state. CLAIM(20IfkyJigKg@18:32)
- Building a frame per hover-and-active combination. CLAIM(20IfkyJigKg@03:27)
- plus 15 more in references/<sub-skill>.md files

## Creator disagreements (stated, not resolved)

- Flux Academy treats motion as a prototype of a control: short, one property at a time, and the object must already exist in the previous frame or it will not travel. CLAIM(hHp4FGVcHjY@00:00, hHp4FGVcHjY@05:30, 20IfkyJigKg@16:45)
- Jesse Showalter, on a 2025 interactive file, will let the tool fill the gap between two wiggles when the in-between path does not matter. That conflicts with the Flux rule when travel is the point. Author the path for travel; tween only for a blend. CLAIM(d5ngkWU2TY8@08:37, d5ngkWU2TY8@08:41, 20IfkyJigKg@16:57)
- Jesse Showalter will hijack the scrollbar for several tall gaps so variants can play. Self-Made Web Designer says the costly look is restraint, and that a product transformation should be a scrubbed clip, not more interface chrome. CLAIM(P8hh8K1EuWE@00:22, q5UFK4ziDuE@01:01, q5UFK4ziDuE@02:55)
- Grow with Alex, March 2024, says change the words so a reference is not a trace. The same creator, December 2023, says download a black-field animation and only swap the plate, the blend, and the curves. Use the 2024 rule when the words are the content. Use the 2023 rule only for a black-field graphic you will recolor, and do not present it as original animation. CLAIM(acjm7wBcrMs@05:24, v1hw3VUnUYc@01:04, v1hw3VUnUYc@04:34)
- Grow with Alex treats motion as a feed asset: black field, bold caps, a 3-second before and after, audio matched to length. Weight that only for a reel. Weight Flux when the artifact is a product control. CLAIM(acjm7wBcrMs@01:36, acjm7wBcrMs@03:30)
- Three different things are called 3D. Jesse Showalter, 2024, means transforms on flat cards that must not reflow. Envato Tuts+, 2019, means an extruded type scene with lights. Punit Chawla, 2022, means a displaced mesh masked by a glyph. Do not mix the recipes. CLAIM(gXOY8Ts44dA@00:08, 8D6b3McyhhU@00:31, K0Dh-8rHMLk@03:03)
- kwoo studio's December 2025 video walks through a free Figma-to-After-Effects plugin. The description on that same video says the plugin is no longer supported and names a paid replacement for 2026. Follow law 50, not the plugin clicks. CLAIM(-QuzxYtwkyU@01:11, -QuzxYtwkyU@11:33)
- Punit Chawla, 2020, taught the soft raised style as the coming look and borrowed hover lift from an older material system. Later videos in this set do not use that style. Keep the shadow checks if you choose the style; do not treat it as the default. CLAIM(fB7h2RxXpqA@02:05, fB7h2RxXpqA@07:42)

## Creator claims (unverified)

- A reference motivational clip was said to have passed 500,000 likes, and another account was said to have about 130,000 followers from about 130 posts. Not checked. CLAIM(acjm7wBcrMs@00:00, v1hw3VUnUYc@00:55)
- Share is called one of the strongest signals for this format. Platform ranking is not verified here. CLAIM(acjm7wBcrMs@11:31)
- Spending 15 to 30 minutes on research and assembly is said to lift the content. No measured lift is shown. CLAIM(acjm7wBcrMs@10:30)
- Agencies are said to charge thousands, and the look is compared to a 50,000 dollar site. No invoice is shown. CLAIM(q5UFK4ziDuE@00:14, q5UFK4ziDuE@00:46)
- The product-scroll look is dated by the creator to an earbuds page in 2019. Treat as the creator's history, not a sourced case study. CLAIM(q5UFK4ziDuE@00:06)
- Freelance animation help is quoted from 10 to 100 dollars, then a markup on top. No invoice is shown. CLAIM(v1hw3VUnUYc@06:16)
- A lifetime icon-plugin unlock is quoted at 14 dollars. Price not checked. CLAIM(EEj3PYjwyC0@02:10)
- Digital brand guidelines with motion are said to support higher rates. No rate card is shown. CLAIM(-QuzxYtwkyU@00:42)

## Tool-specific (dated)

- Figma, 2020-2024: component sets, smart animate, on-drag, while hovering, after-delay, ease-out, ease-in-out, custom spring, custom bezier, auto layout hug versus fixed, clip content, and mask. A later motion model may rename these. CLAIM(4YFRYho3vuM@02:37, 20IfkyJigKg@08:01, hHp4FGVcHjY@08:37, fB7h2RxXpqA@08:24)
- Figma custom spring values tried on a toggle in 2023: stiffness 600, damping 20, with a smaller 22 px knob. A starting point for that build, not a universal constant. CLAIM(hHp4FGVcHjY@09:17, hHp4FGVcHjY@10:14)
- Figma, 2020: the soft raised style was taught as a trend. The shadow recipe can still be checked; the "next look" claim should not be treated as current. CLAIM(fB7h2RxXpqA@02:05)
- Canva, 2023-2024: animated graphics filter, page duration, page transitions, effects glow, curves are not in Canva (recolor of reused clips is in CapCut in the 2023 video), and MP4 export of all pages. UI labels move. CLAIM(acjm7wBcrMs@01:43, acjm7wBcrMs@07:49, v1hw3VUnUYc@03:11, v1hw3VUnUYc@04:12)
- Framer, 2025: sticky position, parent overflow visible, scroll sections, and scroll-variant effects on components. Panel names will drift. CLAIM(P8hh8K1EuWE@02:18, P8hh8K1EuWE@05:04, P8hh8K1EuWE@06:08)
- Framer, 2024: 3D transforms (scale, skew, rotate, perspective, depth, origin, backface, preserve 3D), mouse enter and leave, loop mirror. Feature is dated to that release. CLAIM(gXOY8Ts44dA@00:08, gXOY8Ts44dA@02:33, gXOY8Ts44dA@08:01)
- LottieFiles state machines, 2025: segments, event and boolean inputs, click interactions, reverse or bounce playback, and a prompt assistant that builds the graph. Export is a single dotLottie. The assistant is optional; the four-part model is the check. CLAIM(d5ngkWU2TY8@03:32, d5ngkWU2TY8@04:16, d5ngkWU2TY8@09:02)
- Figma to After Effects via AEUX, 2025 video: send selection, rasterize flag, parametric shapes, 30 or 60 fps, comp duration. The same creator's description says AEUX is no longer supported and names Overlord 2 as the 2026 path. Treat the plugin steps as dated. The handoff checks in law 50 do not depend on the plugin name. CLAIM(-QuzxYtwkyU@01:11, -QuzxYtwkyU@05:38, -QuzxYtwkyU@11:33)
- plus 5 more in the corpus law file studio-corpus/laws/motion_3d.md

## Hand-off
- Next stage: ds-imagery, ds-build-ship. Agent: `ds-motion-designer`.
- Corpus source: studio-corpus/laws/motion_3d.md (regenerate skills with tools/build_skills.py after a corpus refresh).
- Nothing outward (deploy, publish, push) without Gate-D: `ds-pre-publish-gate-d` enforces it once wired.
