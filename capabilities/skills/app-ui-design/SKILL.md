---
name: app-ui-design
description: "App Studio sub-skill, stage 3 (design-ux): design the screens the spec names by routing through the design lane, keeping the brand identity while treating composition as open to measurement, judging real screens with the image judge and JEV ui.design, and checking accessibility with cited results. Use before and during any UI slice of a web or mobile app."
tags: [rig, app-studio, sub-skill, design, ui, ux, accessibility]
metadata:
  parent: app-studio
  tier: sub
  stage: design-ux
  extends: "when-designing-interfaces, impeccable, baseline-ui, fixing-accessibility, make-interfaces-feel-better, pick-ui-library, web-design-guidelines, adrien-design-top-10, design-mobile-responsive-tester"
outcome: "Every spec screen designed and captured at its target viewports, each with an image-judge verdict and a JEV ui.design receipt above 0.9, and accessibility checks cited per screen."
activation: "Load when the spec's screens need designing, when a UI slice is ready for review, or when a screen is called generic, cluttered, or off-brand."
instruction: "Route the design task through when-designing-interfaces, keep the brand identity, capture real screens at each viewport, judge each with advisor-plus judge-image and rig-s1gate ui.design, fix until clean or escalate, and cite accessibility results."
applies_when:
  env: "the running app (dev or production build) plus the Aside browser for captures"
  runtime: "web or mobile UI"
  deps: "spec.md done-screens; the brand's DESIGN.md or tokens when they exist; advisor-plus"
  params: "viewports (mobile, tablet, desktop) or devices; the design brief per screen"
  budget: "up to three fix rounds per screen before escalating"
  scale: "the screens the spec names"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
flow:
  - Route the design task through when-designing-interfaces and load one design skill.
  - Keep the brand identity and treat layout and composition as open.
  - Capture each spec screen at every target viewport from the real app.
  - Judge each capture with the image judge and ui.design and fix until clean or escalate.
  - Cite accessibility results per screen in the slice record.
done_when:
  - "grep:capabilities/skills/app-ui-design/SKILL.md:judge-image"
  - "grep:capabilities/skills/app-ui-design/SKILL.md:LA-16"
  - "grep:capabilities/skills/app-ui-design/SKILL.md:when-designing-interfaces"
  - "cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py"
out_of_scope:
  - brand imagery and LinkedIn creative that a designated generator owns (Eden)
  - replacing a brand identity Mike has not asked to replace
  - rating a screen from source code or a render instead of the real app
---

# app-ui-design

JEV FIRST, binding on every design-ux step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call; this stage's verdicts go to `advisor-plus judge-image` and `rig-s1gate check ui.design`. When the classifier is
unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9;
below that the stage does not advance, and an uncalibrated ESCALATE is a held transition.

## Load surface

Always loaded at the start of every design-ux task: the `app-studio` meta-skill routes
stage 3 here and `app-studio-conductor` loads it from its routes table before the
stage's first action. It is a task-start surface, not a deep reference an agent
must already know about.

Sub-skill of `app-studio`, stage 3 of 11. Main skills it extends:
`when-designing-interfaces` (the design lane router), `impeccable`, `baseline-ui`,
`fixing-accessibility`, `make-interfaces-feel-better`, `pick-ui-library`,
`web-design-guidelines`, `adrien-design-top-10`, `design-mobile-responsive-tester`.
Agent: `app-ui-judge`. Loop: `app-ui-judge-loop`.

## Procedure

1. **Route first.** Enter `when-designing-interfaces` and load the one design skill the
   task needs (build, polish, critique, audit). Do not bulk-load the design estate.
2. **Identity stays, composition is measured.** Keep palette, type, and imagery from the
   brand's DESIGN.md or tokens. Mike called an approved and shipped homepage "AI slop"
   about 22 hours later (memory/USER.md#L33), so a past approval is not a reason to
   resist a redesign: measure the defect.
3. **Real screens (LA-16).** Capture each spec screen from the running app at mobile,
   tablet, and desktop widths, or on the simulator for mobile. Renders and mockups are
   inputs, never evidence.
4. **Judge.** `advisor-plus judge-image --image <png> --brief "<spec screen and intent>"`,
   then `rig-s1gate check ui.design` on a short screen record (screen, viewport, what it
   must do, judge verdict). Fix and re-judge until clean; after three rounds ESCALATE with
   the failing signals named (`app-ui-judge-loop`).
5. **Accessibility.** Run the `fixing-accessibility` checks (contrast, labels, focus order,
   touch target size) and cite each result in the slice record.
6. **Source is not render (LA-23).** Confirm a visual defect on the rendered screen before
   filing it.

## Lessons that fire here

LA-16 real screens, LA-23 source versus render. List them per task with
`scripts/fire_lessons.py`.

## From the creators (candidate lessons)

Distilled from ten app-building YouTube channels (`youtube-<slug>` skills). LA-36..LA-51 are
status `candidate`: follow them now; they fire as gated checks only after promotion, which needs
an engine receipt for the lesson id. Source ids below are greppable in each channel's
`references/lessons.jsonl`.

- LA-49: judge every screen with zero records and, on mobile, with the keyboard up
  (TRV-10-empty-state-element-guard, GXD-07-keyboard-overlap, CH-NJD-01).
- Import a design section by section and check each renders; a whole-page import can fail silently
  (TRV-05-import-design-section-by-section).
- LA-37: a failed request shows an in-page error state for that section, never a blank screen or a
  raw popup (CH-JSM-06, CH-JSM-08).
