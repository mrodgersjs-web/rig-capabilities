---
name: "web-imagery"
description: "Choose, shoot, source, crop and place the imagery that makes a web page prove something. Covers image roles, a specificity ladder for picking assets, crop and grade rules, and the paint
outcome: "A page image set where every asset has a named role, the whole set shares one grade and one crop system, an assets/SOURCES.md record exists, and the hero paints as the largest element inside the weight budget."
done_when:
  - cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/web-imagery/SKILL.md
  - observable: every image on the page has a named role and no more than 5 roles are in use
  - observable: the hero image is the largest content element, is preloaded, is not lazy-loaded, and delivers under 200KB
  - observable: moving any page image onto a competitor's page would break a claim on the page, so no asset is pure decoration
  - observable: the squint test leaves the headline and the primary CTA as the two things that still read
great_example: examples/great/design-ux/web-imagery.md
quality_floor: "Every image on the page has a named role and a recorded source, the set is graded to one look, the hero preloads under 200KB, and no asset could move to a competitor's page without
activation: "A page needs an image chosen, shot, sourced, cropped or placed, or an existing page reads as generic because its imagery is decorative, interchangeable with a competitor's, or slow to paint."
instruction: "Assign every image a named role before choosing an asset, then climb the specificity ladder as far as the budget allows, from raw stock up to a real product screenshot. Refuse any hero
applies_when:
  env: "macOS or Linux designer/developer workstation with the project checked out locally"
  runtime: "static site, Next.js, Astro, Webflow or Squarespace build producing a public web page"
  deps: "an image editor such as Figma or Photoshop, a converter that emits AVIF and WebP, and the page template under build"
  params: "the largest content element is an image; target viewports are 1440x900 desktop and 390x844 mobile"
  budget: "3 to 5 distinct image roles per page and 2MB total page weight"
  scale: "one marketing or product page at a time, up to 30 assets in the working set"
permissions:
  - Read the project template, the copy deck and the existing asset folder
  - Write image files and an assets/SOURCES.md record into the project
  - Read public stock and asset sites to find candidates
  - Bash for image conversion, resizing and dimension checks only
  - Outward, deploy, paid or public actions (buying a licence, publishing the page, uploading to a CDN, commissioning a shoot) need Gate-D approval from
flow:
  - Write the page job as one sentence naming the buyer and the action the imagery has to support
  - List the image roles the page needs (hero, product shot, feature, proof face, texture, icon) and cut any role that carries no information
  - Climb the specificity ladder for each role and record which rung you landed on and why
  - Shoot or source to the crop rather than from it, fixing the ratio first (16:9 hero, 4:3 card, 1:1 avatar) before picking any file
  - Grade and crop the set to one look, keeping text quiet zones clear and steering faces, gazes and pointing limbs toward the copy
  - Export at twice source to AVIF with WebP and JPEG fallbacks, preload the largest image, lazy-load everything below the fold
  - Record every kept asset in assets/SOURCES.md, then run web-imagery-provenance over the record before handoff
out_of_scope:
  - Buying stock licences, commissioning shoots or paying for any asset (Gate-D, Mike approves)
  - Licence, release and rights verification (see web-imagery-provenance)
  - 3D, WebGL, video and generative motion assets (see web-imagery-3d)
  - Brand identity, logo design and icon set authoring
  - Print, packaging, out-of-home and social-card crop systems
  - Image editing that fabricates evidence, such as faking a product screen or a customer photo
---
# Web Imagery

Imagery on a web page is evidence or it is wallpaper. This skill is about making it evidence:
a photo that could sit on any competitor's home page has cost you bytes, attention and
credibility and bought nothing.

## Method

### 1. Name the role before you choose the file

Every image gets one of six roles, written down, before any file is opened.

| role | job it does | failure it prevents |
|---|---|---|
| hero | carries the promise and is the largest element | a mood shot that proves nothing |
| product shot | makes the mechanism legible | a claim with no visible product |
| feature | proves one specific capability | one generic image reused three times |
| proof face | attaches a real person to a real claim | anonymous praise |
| texture / pattern | gives a section weight without competing | gradient soup |
| icon | labels a step or a category | decoration at 64px |

If you cannot say what a candidate image proves in one sentence, it has no role. Cut it.

### 2. Climb the specificity ladder

Pick the highest rung the budget and the rights allow. Record the rung per asset.

1. Real product screenshot at readable size
2. Real photograph of the real customer, place or object
3. Commissioned shoot with a model release
4. Custom illustration or diagram built for this claim
5. Composited stock (stock base, custom foreground or treatment)
6. Raw stock
7. Gradient, abstract or blob

Two rules follow from the ladder. Rung 1 beats rung 2 for anything about software, because
a screenshot is the only image that cannot be disputed. And the hero should never sit below
rung 4. Below that you are paying for bytes to say nothing.

The stock default test is the whole skill in one line: swap your hero image for a
competitor's hero image. If the page still makes sense, the image is decoration.

### 3. Shoot or source to the crop

Fix ratios before picking files, never after.

- Hero 16:9 at 2400x1600 source (delivered 1200x800 and 2400x1600)
- Feature and card 4:3 at 1600x1200 source
- Avatar and proof face 1:1 at 800x800 source
- Full-bleed band 21:9 at 2560x1098 source

Then hold these crop rules. Keep the subject off dead centre when text overlays, and
leave a quiet zone at least 30% of the frame at the same luminance for the headline. Never
crop a face, a hand or a logo through the frame edge. Keep enough of a product in frame
that the claim it supports is visible, which usually means showing the column of numbers,
not the whole app.

### 4. Grade the set to one shoot

Three images from three sources read as three purchases. Unify them. One white balance
(around 5600K), one contrast curve, one subtle vignette, one colour that matches the brand
accent and no second saturated colour anywhere in the set. Where you must mix a photograph
and an illustration, put the illustration in a hard-edged frame so the difference is
deliberate rather than accidental.

### 5. Steer the eye

The first fixation on a page is a human face, and the second follows its gaze. Put faces on
the outer third looking inward toward the headline and the button. Pointing limbs and
leading lines do the same job. A model staring off the right edge of the frame is sending
your visitor to the browser chrome.

### 6. Hold the paint and weight budget

The hero image is almost always the largest content element, which means it decides the
largest contentful paint. Treat that as a hard constraint.

- Preload the hero. Never give it `loading="lazy"`.
- Serve AVIF with a WebP and a JPEG fallback through `srcset` and `sizes`.
- Ship 2x source and let the browser downsample for retina.
- Target under 200KB for the hero and under 80KB for a card image.
- Lazy-load everything below the fold. Eager-load only the hero and the wordmark.
- Set explicit width and height or `aspect-ratio` on every image so nothing shifts.

Budget the page at 2MB total and keep the whole image set inside 40% of it. Above seven
distinct images a marketing page stops reading as an argument and starts reading as a
gallery.

### 7. Record what you kept

One row per kept asset in `assets/SOURCES.md`, filled before handoff. The licence column is
never empty. That record is the input to web-imagery-provenance, which is where the rights
questions get settled.

## Corpus evidence

self-made-web-designer / The Easiest Way to Build Killer Websites / O7MaPnRy5Us / [12:19] / "I don't just want to have a stock image here in the hero section"
self-made-web-designer / How to Grow a Strong Web Design Business with SEO / bhR0HaeFwJg / [31:01] / "just use this cheesy stock photo"
self-made-web-designer / The ONLY 6 Web Design Styles that Matter (2026) / N1Cl5cYmegE / [06:29] / "The main thing that you need to pull this off is, is good photography"
designcourse / Modern LOGO / BRAND Design with David Airey | Q&A / 5fKijXrToWM / [17:21] / "so they prefer stock photography to AI"
self-made-web-designer / 6 EASY Tips to 10x Any Site's Design / pbhLsV-Dyho / [07:19] / "We, we want it to feel a little bit more abstract"
self-made-web-designer / The Best Way to Market Your Web Design Business / iLyf8XvwNgw / [40:59] / "best images in the hero spot of your"

Corpus coverage for this topic is real but narrow. The corpus supports the anti-stock-default
position and the preference for real photography, and it says nothing systematic about
colour grading, gaze steering or crop ratios. UNVERIFIED - the six-role table, the
specificity ladder rung order, the crop ratio set, the grade targets and every byte and
pixel number in the paint budget are studio doctrine written at authoring time. All caption
tracks in the corpus are automatic, so no numeric claim here is sourced from them.

## Anti-patterns

- Stock wallpaper: a sector-mood photograph that would work unchanged on four competitors' sites.
- The 1x screenshot: a product shot scaled so small the detail it is meant to prove is unreadable.
- Gaze hijack: a model looking out of the frame while the CTA sits behind their head.
- Seven-shoot page: seven sources, seven grades and seven ratios on one page.
- Lazy hero: the largest image marked `loading="lazy"`, so the page paints late and shifts.

## Links

- parent: when-designing-websites
- children: web-imagery-provenance, web-imagery-3d

## description (full text)

"Choose, shoot, source, crop and place the imagery that makes a web page prove something. Covers image roles, a specificity ladder for picking assets, crop and grade rules, and the paint and weight budget. Use when picking, shooting, sourcing, cropping or laying out photos, screenshots, illustrations or icons on a web page."

## quality_floor (full text)

"Every image on the page has a named role and a recorded source, the set is graded to one look, the hero preloads under 200KB, and no asset could move to a competitor's page without breaking a claim. Anything weaker fails the job and is not shipped."

## instruction (full text)

"Assign every image a named role before choosing an asset, then climb the specificity ladder as far as the budget allows, from raw stock up to a real product screenshot. Refuse any hero image that would still make sense on a competitor's home page. Hold the paint budget, because the hero image is the largest element on the page and has to preload, ship at twice source, and stay under 200KB delivered. Record every asset you keep in assets/SOURCES.md and hand provenance to web-imagery-provenance before handoff."

## Contract detail (full text)

- Outward, deploy, paid or public actions (buying a licence, publishing the page, uploading to a CDN, commissioning a shoot) need Gate-D approval from Mike before they run
