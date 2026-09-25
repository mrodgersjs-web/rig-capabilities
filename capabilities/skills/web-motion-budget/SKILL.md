---
name: "web-motion-budget"
description: "Hold the motion performance budget so animation stays at 60fps on safe properties with honest reduced-motion fallbacks: use before shipping any animated page."
outcome: "A measured motion budget: a per-animation property list, frame-trace evidence of zero dropped frames, and a reduced-motion build that loses movement and nothing else."
done_when:
  - cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/web-motion-budget/SKILL.md
  - observable: a performance trace of the busiest sequence shows zero dropped frames during scroll
  - observable: every animation runs on transform or opacity
  - observable: no more than five elements animate at once
  - observable: the reduced-motion build shows every state change without movement
great_example: examples/great/design-ux/web-motion-budget.md
quality_floor: "Zero dropped frames in the busiest sequence trace, transform and opacity only, at most five simultaneous animations, and a working reduced-motion path. Any dropped frame or motion-only state change fails the job."
activation: "Load when animation is about to ship or is already hurting: before building motion on a heavy page, when scrolling stutters or jank appears, when a page must satisfy reduced-motion expectations, or when someone claims motion is smooth and there is no trace."
instruction: "Budget every frame: at 60fps a frame has 16.7ms and animation work must fit in half of it. Animate transform and opacity only, keep simultaneous animated elements under five, and prove the result in a real performance trace rather than by eye. Ship a reduced-motion path that keeps every state change visible, and hold the budget before adding any new motion."
applies_when:
  env: "developer workstation with device access or emulation and a performance panel"
  runtime: "web page or app surface with CSS, JS or scroll-driven animation"
  deps: "the page code, the build output and trace tooling"
  params: "real devices from mid-tier phones to laptops; 60fps target with 16.7ms frames"
  budget: "animation work under 8ms per frame, at most 5 simultaneous animations"
  scale: "one page or flow at a time, up to 30 animations inventoried"
permissions:
  - Read the page code, build output and performance traces
  - Write motion code, tokens and a performance note in the named project
  - Bash for trace capture and greps only
  - Outward, deploy, paid or public actions (publishing, deploys, paid tooling) need Gate-D approval from Mike before they run
flow:
  - Inventory every animation and name the state change each explains
  - Classify each as safe-property or not, and rewrite or delete the unsafe ones
  - Set duration bands and cap simultaneous animations at five
  - Build the reduced-motion path and confirm every state change survives it
  - Trace the busiest sequence and count dropped frames
  - Cut anything over budget before shipping and record the trace as evidence
out_of_scope:
  - Motion design, choreography and scroll narrative (see web-motion, web-motion-narrative)
  - Image and asset weight, and network or server performance
  - Accessibility beyond motion sensitivity
  - Video production, game engines and native app animation
---
# Web Motion Budget: frames, properties, honesty

## Method

60fps is a deadline, not a vibe: 16.7ms per frame, and animation work must land in about 8ms of it
(UNVERIFIED - studio doctrine figure) because input handling, style recalc and the browser's own
work share the same frame. Spend the budget in code, then verify it in a trace.

Property discipline:

- Animate transform and opacity only. Those are the properties a browser can composite without
  relaying out the page (UNVERIFIED - engineering claim with no corpus support at authoring time).
- Never animate width, height, top, left, margin, padding, box-shadow, filter, or background
  position. Each one forces layout or paint work per frame. Replace with transform: scale or
  translate, and with opacity for shadow-like emphasis.
- Read layout values before you write them. Interleaved reads and writes force synchronous layout,
  which is where single frames go from 4ms to 40ms.
- Drive script animation with requestAnimationFrame, and pause it when the tab is hidden or the
  element leaves the viewport.

Volume discipline:

- At most 5 elements animating at once per screen. A stagger of 20 items is 20 animations wearing a
  costume; cut the tail.
- No infinite decorative loops while a section is off-screen.
- will-change sparingly and only for the duration of an interaction (UNVERIFIED - no corpus support
  at authoring time). will-change on every element in a stylesheet costs memory and earns nothing.

Reduced motion:

- Respect prefers-reduced-motion: reduce. In that mode, replace travel with instant swaps or opacity
  changes of 100ms or less, and never remove content or state feedback to achieve it.
- Reduced motion is a second build, not an afterthought: the state change must be readable with the
  motion deleted. Test by deleting the animation entirely and confirming nothing is lost.
- The corpus teaches this rarely and briefly (see evidence rows): treat reduced-motion practice here
  as studio doctrine, UNVERIFIED against the corpus at authoring time.

Evidence discipline:

- A claim of smooth motion without a trace is noise. Record a performance trace of the busiest
  sequence before and after every motion change, and count dropped frames in the timeline.
- The honest order is measure, cut, measure again. Never declare a frame budget held from a design
  file.

## Corpus evidence

Format: channel / video title / videoId / [MM:SS] / quote.

- designcourse / SVG Clip Masking Video is Awesome | Tutorial / hhnzPijhHio / [06:50] / "method prefers reduced motion then we're"
- designsense / UI/UX Design Trends 2026 / -ic0kMt_IMY / [03:50] / "for reduced motions preferences"
- every-tuesday / Procreate Animation for Beginners - How to Create a Birthday Sparkler / mXiA2Tri1vU / [06:53] / "looped animation the frames per second"
- punit-chawla / Most Exciting UI Design Tool! - Unicorn Studio | Create Stunning Web Animations / N9FV8VfYhqg / [06:05] / "the frame rate, etc. Amazing. And all of"
- flux-academy / Don't make these rookie mistakes in Framer / ihulImRXz9U / [14:40] / "pretty janky and sometimes people just"

Corpus coverage measured across the 2,399 timestamped transcripts at authoring time: reduced-motion
phrasing 2 rows, frame rate and frames-per-second phrasing 89 rows, jank and janky 14 rows, 60 FPS
4 rows, while compositor, will-change and transform-and-opacity phrasing have zero rows. The frame
budget and safe-property rules above are marked UNVERIFIED and are studio doctrine until primary
sources check them. The two reduced-motion rows are the strongest evidence in this file.

## Anti-patterns

- Layout-property animation: transitioning height or top and dragging the main thread every frame.
- Infinite ambient loop: a decorative loop still running while its section is off-screen.
- Motion-only state: an error or success that is readable only if the reader watches the animation.
- will-change wallpaper: will-change declared on every element in the base stylesheet.
- Untraced smooth: calling motion performant with no performance trace and no frame count.

## Links

parent: when-designing-websites
children: none (leaf skill under web-motion)
