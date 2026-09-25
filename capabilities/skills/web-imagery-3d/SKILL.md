---
name: "web-imagery-3d"
description: "Decide when 3D, WebGL and generative assets earn their cost on a web page, then build them with a poster fallback, a frame floor
outcome: "A 3D or generative element with a written justification, a poster that paints first and survives JavaScript off and WebGL
done_when:
  - cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/web-imagery-3d/SKILL.md
  - observable: a written sentence states what a still loses, and the still equivalent is quoted in bytes and days beside it
  - observable: the poster renders as the real first paint and the renderer initialises over it on intersection
  - observable: with JavaScript disabled, with reduced-motion set, and with WebGL unavailable, the section still shows a complete convincing visual
  - observable: the payload is compressed and recorded (triangles, texture size, total bytes) and fits inside the page weight budget
  - observable: frames are measured at or above 60fps on a mid-tier laptop and 30fps on a mid-tier phone, or the scene degrades to the poster
great_example: examples/great/design-ux/web-imagery-3d.md
quality_floor: "The poster paints first and is convincing on its own, every fallback branch is implemented and proven rather than described, the
activation: "Someone proposes a 3D, WebGL, Spline, Three.js or generative visual for a page, or a page is already shipping one and is slow
instruction: "Demand a written reason a still cannot do the job before any 3D work starts, and kill the element if the reason is only that 3D
applies_when:
  env: "macOS or Linux workstation with a 3D tool (Spline, Blender) and the web project available locally"
  runtime: "browser with WebGL or WebGL2; Three.js, React Three Fiber, Spline runtime, or a canvas shader"
  deps: "a still-render path for the poster, an asset exporter that emits glb with Draco or Meshopt and KTX2 textures, and a device-capability check at init"
  params: "largest content element may be the 3D canvas; target 1440x900 desktop and 390x844 mobile with reduced-motion honoured"
  budget: "the 3D payload must fit inside a 2MB page weight budget and cost no more than one sprint of design plus one of engineering"
  scale: "one 3D element per page, at most two per site, one hero scene up to 150k triangles"
permissions:
  - Read the page template, the brand asset folder and the existing performance traces
  - Write scene files, exported models, poster images and the runtime code into the project
  - Bash for asset conversion, size inspection and local performance measurement
  - Read public documentation for the rendering library and the exporter in use
  - Outward, deploy, paid or public actions (publishing the page, buying a 3D asset or a tool seat, uploading to a CDN) need Gate-D approval from Mike before they run
flow:
  - Write the reason a still cannot do the job in one sentence, and cancel the element if the sentence is only that 3D looks impressive
  - Quote the still equivalent (a 2x PNG or WebP) in bytes and in days, and put it beside the 3D cost before anyone commits
  - Render the poster first at 2400x1600 and make it the painted state of the section
  - Build the scene, then export compressed (glb with Draco or Meshopt, KTX2 textures) and record triangles, texture sizes and total bytes
  - Implement the fallback ladder and wire every branch - reduced motion, low memory, few cores, no WebGL context, all landing on the poster
  - Initialise on intersection rather than on load, never blocking first paint, and settle the scene instead of looping
  - Measure frames on a mid-tier laptop and a mid-tier phone, then hold the floor or drop to the poster
out_of_scope:
  - Video backgrounds and cinemagraphs (treat as a separate media decision)
  - Buying 3D models, tool seats or compute (Gate-D, Mike approves)
  - Interactive product configurators with real pricing and cart logic
  - Native game or simulation work and VR or AR targets
  - Image sourcing and rights for textures (see web-imagery-provenance)
---
# Web Imagery 3D

3D on a web page is the most expensive way to make a point and the easiest way to make none.
This skill exists to spend that budget only where a photograph genuinely cannot, and to make
the failure mode a good still rather than a white rectangle.

## Method

### 1. The one-sentence justification

Before any tool opens, write one sentence of the form "a still cannot show X, and X is what
the buyer decides on." Three jobs clear that bar.

- **Angles no photo covers.** A product whose underside or interior is the selling point.
- **A material property made legible.** Finish, transparency, light response, assembly. This
  is the one case where motion genuinely carries information.
- **A signature the competition cannot buy.** A scene so specific to the brand that stock
  could never substitute.

Anything else fails. "It looks premium" fails. "It shows we are technical" fails. If the
sentence is only about how it looks, the still wins on every axis that matters.

### 2. Quote the still beside it

Put the two numbers in front of whoever is deciding:

| | still (2x WebP) | 3D scene |
|---|---|---|
| design time | 0.5 to 1 day | 2 to 5 days |
| engineering time | 0 to 0.5 day | 3 to 10 days |
| delivered bytes | 150 to 300KB | 800KB to 6MB |
| failure mode | none | blank canvas |
| works with JS off | yes | only with a poster |

The 3D column has to buy something real for that spread. Often it does not, and saying so is
the job.

### 3. The poster is the product's insurance policy

Render the scene to a 2400x1600 WebP, ship it, and paint it as the actual first paint of the
section. The renderer then initialises on intersection and swaps in over the top. Consequences
you must accept: the poster is not a placeholder you skip, it is a deliverable with its own
grade and crop, and it must be convincing enough that nobody notices when it is all they get.

### 4. The fallback ladder is mandatory

Every branch is a real `if`, tested before handoff.

1. `prefers-reduced-motion: reduce` - never construct the renderer, keep the poster.
2. `navigator.deviceMemory` below 4, or `hardwareConcurrency` at or below 2 - skip init.
3. WebGL or WebGL2 context creation returns null - catch it, keep the poster, log once.
4. Intersection-based init, so a scene below the fold costs nothing until scrolled to.
5. Frame rate below floor for 2 seconds - stop the animation and settle on the poster.

Branch 3 is the one everybody forgets and the one that shows up as a blank hero on exactly
the devices you cannot afford to look broken on.

### 5. Build the payload like it is going over a wire

- Export `.glb`, not loose `.gltf` with PNGs.
- Draco or Meshopt for the mesh. Expect 60 to 80% off the mesh payload.
- KTX2 or Basis textures. Expect 50 to 75% off the texture payload.
- Cap a hero at 150k triangles and textures at 1024px unless the object is seen close.
- Serve the scene lazily and keep it out of the critical request chain.

As a working comparison, an uncompressed export of a single product shell was 4.1MB and the
compressed build of the same scene was 412KB. That is the difference between a page that
ships and one that does not.

### 6. Motion must change information

If a loop runs longer than 6 seconds and the viewer learns nothing after the first 2, it is
decoration and it should lose its budget. The three acceptable motions are reveal (show a
surface or an angle), respond (track the pointer so a material reads), and transition (carry
the eye from one state to the next). Everything else is a screensaver on your customer's
battery.

### 7. Measure on the devices that matter

60fps is the floor on a mid-tier laptop, 30fps on a mid-tier phone. Measure, do not estimate.
Below the floor the answer is not to reduce quality until it stutters acceptably: it is to
settle on the poster.

## Corpus evidence

self-made-web-designer / The ONLY 5 Tools You Need to Build Insane Sites / dROkEnvxch4 / [05:12] / "it used to be that any kind of 3D interaction on a website"
self-made-web-designer / The ONLY 5 Tools You Need to Build Insane Sites / dROkEnvxch4 / [05:17] / "you had to do some pretty deep work in JavaScript or the canvas"
self-made-web-designer / The ONLY 5 Tools You Need to Build Insane Sites / dROkEnvxch4 / [05:28] / "It's called Spline"
self-made-web-designer / The ONLY 6 Web Design Styles that Matter (2026) / N1Cl5cYmegE / [12:20] / "get you there quicker, like Unicorn Studio or, or Spline"
punit-chawla / New UX/UI Trends for 2026 Are Amazing! - Neural Interface, Next Level Motion, Voice & More / 6LW9bV9xmEQ / [21:04] / "it up on their website or lazy loading"
self-made-web-designer / The ONLY 6 Web Design Styles that Matter (2026) / N1Cl5cYmegE / [10:27] / "maybe it's a small 3D object that stands out"

**Corpus coverage thin at authoring time.** The corpus supports three narrow claims: that
browser 3D used to require deep JavaScript or WebGL work and tooling has changed that, that
Spline and Unicorn Studio are the named tools, and that heavy assets on a page need lazy
loading. It says nothing about when 3D earns its cost. UNVERIFIED against this corpus - the
one-sentence justification test, the still-versus-3D cost table and both figures in it, the
whole fallback ladder, the triangle and texture caps, the compression comparison figures,
the 2MB page budget and the 60fps and 30fps frame floors. Those are studio doctrine written
at authoring time and every number in them must be re-measured on your own project. All
caption tracks in the corpus are automatic, so no figure quoted from one is treated as
verified.

## Anti-patterns

- WebGL or blank: no poster, so a failed context renders an empty hero on the worst devices.
- Paint-blocking renderer: scene initialisation on the critical path before first paint.
- Screensaver on the meter: a looping scene carrying no information while burning GPU and battery.
- Raw export shipped: loose glTF with PNG textures sent to production at full size.
- Demo-spec hero: a heavy scene built against a desktop GPU and then served to phones.

## Links

- parent: when-designing-websites
- parent: web-imagery
- children: none (leaf skill)

## description (full text)

"Decide when 3D, WebGL and generative assets earn their cost on a web page, then build them with a poster fallback, a frame floor and a compressed payload. Use when proposing or shipping a 3D hero, a WebGL scene, Spline or Three.js work, generative canvas art, or when rescuing a page that loads slowly because of one."

## outcome (full text)

"A 3D or generative element with a written justification, a poster that paints first and survives JavaScript off and WebGL missing, a compressed and recorded payload inside the page weight budget, and a measured frame floor with a defined drop-to-poster path."

## quality_floor (full text)

"The poster paints first and is convincing on its own, every fallback branch is implemented and proven rather than described, the payload is compressed and recorded inside the budget, and the frame floor is measured on a mid-tier laptop and phone. Any branch left unimplemented fails the job."

## instruction (full text)

"Demand a written reason a still cannot do the job before any 3D work starts, and kill the element if the reason is only that 3D looks impressive. Build the poster first and treat it as the real first paint, then let the renderer swap in over it on intersection. Make the fallback ladder mandatory and test it, because a failed WebGL context must degrade to a convincing still rather than a white hole. Compress the payload hard, hold a frame floor, and drop to the poster when the device or the motion preference says no."

## description (full text)

"Decide when 3D, WebGL and generative assets earn their cost on a web page, then build them with a poster fallback, a frame floor and a compressed payload. Use when proposing or shipping a

## outcome (full text)

"A 3D or generative element with a written justification, a poster that paints first and survives JavaScript off and WebGL missing, a compressed and recorded payload inside the page weight

## quality_floor (full text)

"The poster paints first and is convincing on its own, every fallback branch is implemented and proven rather than described, the payload is compressed and recorded inside the budget, and

## instruction (full text)

"Demand a written reason a still cannot do the job before any 3D work starts, and kill the element if the reason is only that 3D looks impressive. Build the poster first and treat it as the

## description (full text)

"Decide when 3D, WebGL and generative assets earn their cost on a web page, then build them with a poster fallback, a frame floor and a compressed payload. Use

## outcome (full text)

"A 3D or generative element with a written justification, a poster that paints first and survives JavaScript off and WebGL missing, a compressed and recorded

## quality_floor (full text)

"The poster paints first and is convincing on its own, every fallback branch is implemented and proven rather than described, the payload is compressed and

## activation (full text)

"Someone proposes a 3D, WebGL, Spline, Three.js or generative visual for a page, or a page is already shipping one and is slow, blank on some devices, or burning battery."

## instruction (full text)

"Demand a written reason a still cannot do the job before any 3D work starts, and kill the element if the reason is only that 3D looks impressive. Build the
