---
name: "web-motion"
description: "Design web motion as a grammar of duration bands, easing and choreography so interface change is felt and understood: use for hover, state, entrance and scene motion."
outcome: "A motion language: three duration bands, one easing family, a declared choreography order, and interface animations that each explain a change."
done_when:
  - cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/web-motion/SKILL.md
  - observable: every animation maps to a named state change
  - observable: all durations fall inside the three declared bands and every curve comes from the declared family
  - observable: the busiest sequence holds 60fps and the reduced-motion build still shows every state change
great_example: examples/great/design-ux/web-motion.md
quality_floor: "Every animation explains a state change and sits in a declared duration band and easing family. A decorative animation, or one whose information only exists in motion, fails the job."
activation: "Load when motion decisions are on the table: hover and state feedback, page or section entrances, view transitions, a motion language for a product, or a page where animation feels random, slow, bouncy or distracting."
instruction: "Give the product one motion vocabulary and hold it: one easing family, three duration bands, and choreography ordered by importance. Motion must explain a change of state or place and never decorate a thin design. Honor the studio motion law: motion-driven, never scroll-and-appear, because scroll means things happen, not things appear."
applies_when:
  env: "developer or designer workstation with motion tokens under version control"
  runtime: "CSS, GSAP, Framer Motion, Lottie or a builder animation model on a web page"
  deps: "the design file, page code and a browser performance panel"
  params: "input is keyboard, mouse or touch; motion must explain a state change"
  budget: "3 duration bands, 1 easing family, at most 6 staggered elements"
  scale: "one page or flow at a time, up to 30 animations in the working set"
permissions:
  - Read the design file, page code and motion tokens
  - Write motion code and one duration and easing token file in the named project
  - Bash for greps and trace capture only
  - Outward, deploy, paid or public actions (publishing, deploys, paid assets) need Gate-D approval from Mike before they run
flow:
  - Name the state change each animation explains and delete any that explain nothing
  - Assign each survivor a duration band
  - Pick every curve from the one easing family
  - Order the choreography by importance so the eye lands where the job is
  - Build each animation on the safe property list and hand heavy pages to web-motion-budget
  - Test the sequence at full speed, at a fast flick, and under reduced motion
out_of_scope:
  - Scroll narrative structure and scene beats (see web-motion-narrative)
  - Frame budgets, safe properties and reduced-motion engineering (see web-motion-budget)
  - Layout and hierarchy (see web-layout family)
  - WebGL and 3D scenes, film and game cinematics
---
# Web Motion: the craft of moving interface

## Method

Motion is a sentence, not an adjective. Every animation answers one of three questions: what changed,
where did it go, what happens next. If an animation answers none of them, it is decoration and it
costs frames.

Duration bands (studio doctrine, UNVERIFIED against the corpus at authoring time):

- Micro, state and hover feedback: 150 to 300ms. Below 150ms reads as a glitch; above 300ms reads
  as lag on a control the finger is already on.
- Meso, entrances and element swaps: 300 to 500ms.
- Macro, section and scene changes: 500 to 800ms. Never above 800ms unless the motion is bound to
  scroll, where the reader owns the clock.
- Exits run at 0.6 to 0.75x their entrance duration. Arrive composed, leave fast.

Easing: one family per product.

- Studio default curve: cubic-bezier(0.2, 0, 0, 1). Fast departure, soft landing, reads as intent
  rather than as an effect.
- Exits and dismissals: cubic-bezier(0.4, 0, 1, 1), same family, mirrored.
- Linear only for continuous progress (loaders, scrubbers) where eased speed would lie.
- Springs belong to direct manipulation only (drag, swipe, pull): settle under 400ms with under 5
  percent overshoot. A spring on a hover state is a personality disorder.

Choreography:

- Stagger 30 to 60ms per element, at most 6 elements in one stagger. Past 6 the tail is wasted.
- Order by importance. The element the job depends on lands first or last, never buried in a middle.
- Hover: 120 to 200ms, scale at most 1.02, no layout movement, identical duration on leave.
- Never animate two adjacent tiers with the same weight, and never run more than one attention
  getter (a scale, a shake, a pulse) per screen.
- One vocabulary means one audit: grep the codebase for duration and curve literals and confirm
  they only come from the token file.

The studio's standing motion law, honored verbatim in this family: "Motion-driven, never
scroll-and-appear. Scroll = things HAPPEN, not things APPEAR." A scene that only fades in on entry
has no motion language at all. Route scroll scenes to web-motion-narrative.

## Corpus evidence

Format: channel / video title / videoId / [MM:SS] / quote.

- flux-academy / How to get micro-interactions right using Figma / hHp4FGVcHjY / [00:00] / "micro interactions are simple and subtle"
- self-made-web-designer / Let's See Who's Better...Human or AI Web Design / 5LW_-J9q9h8 / [06:11] / "really cool micro interactions."
- self-made-web-designer / Steal These Web Design Trends 2026 / waHuVF3XuMA / [07:52] / "a story within the website so the animations don't distract you."
- self-made-web-designer / Steal These Web Design Trends 2026 / waHuVF3XuMA / [07:08] / "Democratized fancy animations."
- designcourse / Go from VIBE DESIGNS to PRO DESIGN - 2 TIPS / pg-37Yh_A50 / [05:39] / "transitions to create simple animations."
- designcourse / Mind blowing: New 3D Animation No Code Tool ROCKS! / Vus3KQWevxs / [05:21] / "and we do want a hover State you know"

Corpus coverage is real for micro-interactions, hover states and motion restraint: 4,819 animation
rows, 1,964 hover rows and 667 easing rows measured across the 2,399 timestamped transcripts at
authoring time. Duration bands, curve values and stagger numbers above are studio doctrine,
UNVERIFIED against the corpus at authoring time.

## Anti-patterns

- Fade-up army: every section fading up 30px on scroll, so the page has motion and no language.
- Two clocks: 150ms on one button and 600ms on its sibling in the same toolbar.
- Decorative loop: an animation running with nothing to explain.
- Layout mover: animating height, margin or top so text reflows while it moves.
- Entrance without exit: elements arrive over 600ms and vanish instantly, so departure reads as a cut.

## Links

parent: when-designing-websites
children: web-motion-narrative, web-motion-budget
