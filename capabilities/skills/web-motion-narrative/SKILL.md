---
name: "web-motion-narrative"
description: "Choreograph scroll-driven narrative so the page tells its story as the reader moves: use for scroll scenes, staged reveals, parallax depth and motion identity."
outcome: "A scroll narrative: a beat storyboard with scroll ranges, one signature move, and scenes that resolve."
done_when:
  - cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/web-motion-narrative/SKILL.md
  - observable: the page carries 3 to 6 named beats each bound to a scroll range
  - observable: every pinned scene resolves before release and no scene is left half-told
  - observable: the signature move appears at least twice
  - observable: the story reads correctly at a fast flick, a normal read and a slow drag
great_example: examples/great/design-ux/web-motion-narrative.md
quality_floor: "Every beat advances the story, is bound to a scroll range, and no scene is left half-told. Beats that only fade in on entry fail the job."
activation: "Load when a page must tell a story through scrolling: product narratives, launch and manifesto pages, portfolios, scroll-triggered scenes, parallax depth, pinned sections, or a motion identity that must stay recognizable across a site."
instruction: "Build the page as scenes with beats, so scrolling advances the story instead of revealing boxes. Bind each beat to a scroll range, give it direction and consequence, and resolve every pinned scene before the reader leaves it. Reuse one signature move across the page so motion becomes identity, and never let a beat be mere appearance: scroll means things happen."
applies_when:
  env: "developer workstation with the narrative brief and storyboard in hand"
  runtime: "scroll-driven web page built with CSS, GSAP ScrollTrigger or equivalent"
  deps: "fixed content order, motion tokens and a browser for three-speed testing"
  params: "the reader scrolls at their own pace; content order is fixed"
  budget: "3 to 6 beats, 60 to 100vh scroll range per beat, at most 3 parallax planes"
  scale: "one narrative page at a time, up to 6 scenes"
permissions:
  - Read the narrative brief, storyboard, page code and motion tokens
  - Write scroll scene code in the named project
  - Bash for greps and trace capture only
  - Outward, deploy, paid or public actions (publishing, deploys, paid assets) need Gate-D approval from Mike before they run
flow:
  - Write the story as 3 to 6 beats, each one sentence naming what changes for the reader
  - Map each beat to a scroll range and cut any beat with no range
  - Give each beat direction and consequence: what moves, what it hands off to
  - Choose one signature move and place it at least twice
  - Pin only scenes with a defined end, and resolve each before release
  - Walk the page at three speeds (flick, normal read, slow drag) and fix beats that skip or stall
out_of_scope:
  - Per-element motion craft and duration bands (see web-motion)
  - Frame budgets and reduced-motion engineering (see web-motion-budget)
  - Layout composition (see web-layout family)
  - Writing the narrative copy itself
  - Carousels, modals, dashboards and comparison pages
---
# Web Motion Narrative: scroll as story

## Method

A scroll narrative is a storyboard with a scrollbar. Write the beats first in plain sentences, one
per scene, before any code: what the reader knows at the start of the scene and what changed by the
end. A beat with no change is a fade, and fades are appearance, which the studio motion law forbids
here.

The law, honored verbatim: "Motion-driven, never scroll-and-appear. Scroll = things HAPPEN, not
things APPEAR." Concretely: bind motion to progress, give it direction (rotation, travel, scale,
mask, handoff), and make each scene end in a different state than it began.

Structure:

- 3 to 6 beats per page. More and the story stops being tellable in one pass.
- Scroll range per beat: 60 to 100vh. Below 60vh the beat is a stutter; above 100vh the reader
  waits with nothing happening.
- Two clocks. Copy and interface use time-bound motion from web-motion (150 to 800ms bands).
  Narrative objects use scroll-bound motion mapped to scene progress. Mixing the two clocks inside
  one element reads as lag.
- Pinned scenes must resolve: the pin releases only after the beat completes its state change. An
  unresolved pin is a story stopped mid-sentence.

Depth and pacing:

- Parallax budget: at most 3 depth planes, with travel offsets of 8 to 15 percent of scroll. The
  plane nearest the reader travels most. Four or more planes read as soup.
- Stagger within a beat: 30 to 60ms per element, at most 6 elements.
- Cross-scene transitions: 500 to 800ms, one beat handing directly to the next so the page feels
  continuous rather than paged.

Motion identity:

- Choose one signature move and reuse it at least twice: a masked wipe, a skew that settles to zero,
  a letter-by-letter handoff. Reused twice it becomes the brand's fingerprint; used once it is a
  stunt.
- Hold the same easing family as web-motion (studio default cubic-bezier(0.2, 0, 0, 1)) so the
  narrative and the interface read as one product.

Numbers in this Method are studio doctrine and declared standards of this skill: corpus coverage of
scroll choreography specs is thin at authoring time, and auto-captions mishear numbers, so each is
UNVERIFIED against the corpus until checked against a primary source.

## Corpus evidence

Format: channel / video title / videoId / [MM:SS] / quote.

- designsense / UI/UX Design Trends 2026 / -ic0kMt_IMY / [05:21] / "and pacing. Scroll trigger transition"
- punit-chawla / Amazing Parallax Scroll Animations in Adobe Xd + Protopie | Design Weekly / E6AmkROjnTI / [00:19] / "as you scroll down so there are many"
- designsense / UX/UI Design Trends 2025 / XX2gZTGwZWc / [08:01] / "enhances storytelling by adding depth"
- designcourse / This cursor follow interaction is too good. Let's build it / d0ABgmu2O70 / [08:28] / "type gsap3 easings you'll see a little"
- mike-locke / Designing a Portfolio is Not Easy! - Tips and Advice for UX Designers / CG9V1WF_B9o / [06:02] / "scroll for days as you scroll you see a"

Corpus coverage measured across the 2,399 timestamped transcripts at authoring time: scroll 4,188
rows, easing and ease-curve phrasing 667 rows, parallax 193 rows. Beat structure, pin resolution,
scroll-range values and depth budgets have no corpus support and are studio doctrine, UNVERIFIED
against the corpus.

## Anti-patterns

- Scrolljack: hijacking the wheel or pinning indefinitely, so the reader loses the scrollbar.
- Fade-and-appear: every scene is an opacity fade with no direction and no consequence.
- Unresolved pin: a pinned scene that never completes before release, so the story hangs.
- Parallax soup: five depth planes at arbitrary speeds fighting the copy.
- One-hit signature: a signature move used once and abandoned across the rest of the site.

## Links

parent: when-designing-websites
children: none (leaf skill under web-motion)
