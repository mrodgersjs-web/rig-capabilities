# ui_system laws (Design Studio OS corpus)

Coverage: 22 videos read: GUupJJC5Ac4, vf1BZ1mG2WE, aGvWDDPsjUM, 1JZcMnecWHI, z7amr9d5ORA, z3B1pUzyarM (Flux Academy); oCVG6DFCTz4, Sfy5wG5ZB3A, oXDAmwEWlDc, M8msUKBSBlY, AdNOcgK_6Bs, 6XcDHOlBARc (Jesse Showalter); Tx45NcbU6aA, 4BEEoYYDmUg, KWUlkXZOj4g, iLWaIx7tMnU, jXEn5IFxmAc (DesignCourse); beUlX6L2NMg, 3ERrrTcx09c, IO30Ta7aqF0 (Punit Chawla); _NTvNAaetCM (Mike Locke); VMQasbs3Xkk (Satori Graphics). Channels: 6 (Flux Academy, Jesse Showalter, and Satori Graphics are top-10 sources). Date range: 2009-09-11 to 2026-03-06.

## Laws

### Token and variable architecture

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 1 | Store every repeated design value (color, gap, radius, spacing) as a named variable and bind the property to it, so one edit updates all usages instead of re-entering values per element | Flux Academy, Jesse Showalter | CLAIM(GUupJJC5Ac4@00:18), CLAIM(oCVG6DFCTz4@10:15) | consensus | yes |
| 2 | Build tokens in two layers: a primitives collection of raw values, then a semantic collection whose names state the role (button, link, heading, body) and reference the primitives | Flux Academy | CLAIM(GUupJJC5Ac4@04:07), CLAIM(GUupJJC5Ac4@04:07) | single-source | yes |
| 3 | Choose variables over shared styles whenever one role must recolor without touching the others: repointing the button token leaves link and logo usages intact | Flux Academy | CLAIM(GUupJJC5Ac4@05:35) | single-source | yes |
| 4 | Group variables into collections by kind (colors, numbers, booleans) and attach a short description to each naming where it applies | DesignCourse, Punit Chawla | CLAIM(Tx45NcbU6aA@02:35), CLAIM(IO30Ta7aqF0@01:06) | consensus | no |
| 5 | Name number variables as scale levels (five for 40px radius, two for a 16px gap) and bind components to the level, never to the raw pixel value | Jesse Showalter | CLAIM(oCVG6DFCTz4@10:15) | single-source | yes |
| 6 | Implement themes as one extra mode per variable (light, dark), fill each mode with its own values, then flip the frame mode from the layer panel selector | Flux Academy, DesignCourse, Punit Chawla | CLAIM(GUupJJC5Ac4@06:13), CLAIM(Tx45NcbU6aA@25:42), CLAIM(IO30Ta7aqF0@03:40) | consensus | yes |
| 7 | Keep the default mode first in the collection by dragging rows into order, so the mode picker shows it first | Jesse Showalter | CLAIM(M8msUKBSBlY@03:27) | single-source | yes |
| 8 | Bind boolean variables to layer visibility (right-click the visibility icon in the layer controls) so one click can show or hide content per state | DesignCourse, Flux Academy | CLAIM(Tx45NcbU6aA@19:26), CLAIM(vf1BZ1mG2WE@20:46) | consensus | yes |

### Component architecture

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 9 | Convert anything reused more than once into a component and edit only the master, so every instance follows | Flux Academy, Jesse Showalter, DesignCourse | CLAIM(aGvWDDPsjUM@00:57), CLAIM(oCVG6DFCTz4@03:30), CLAIM(1JZcMnecWHI@00:57), CLAIM(z7amr9d5ORA@02:05), CLAIM(z7amr9d5ORA@06:00), CLAIM(jXEn5IFxmAc@04:08) | consensus | yes |
| 10 | Put interchangeable items (icon types, button shapes, tab states) in one component set with one variant each, so instances swap from the properties panel | Flux Academy, Jesse Showalter | CLAIM(1JZcMnecWHI@01:23), CLAIM(vf1BZ1mG2WE@03:13), CLAIM(6XcDHOlBARc@04:30), CLAIM(z7amr9d5ORA@15:41) | consensus | yes |
| 11 | Give every variant axis a real option name (State equals default, hovered, active) and rename the property itself; never ship a set labeled with generator defaults | Flux Academy, Jesse Showalter, DesignCourse | CLAIM(1JZcMnecWHI@02:35), CLAIM(aGvWDDPsjUM@05:21), CLAIM(iLWaIx7tMnU@17:08), CLAIM(6XcDHOlBARc@02:41), CLAIM(6XcDHOlBARc@03:42), CLAIM(z7amr9d5ORA@04:14) | consensus | yes |
| 12 | Slash-name frames before combining them (button/default, filters/abstract) so the finished set reads as a legend | Flux Academy, Jesse Showalter | CLAIM(vf1BZ1mG2WE@01:58), CLAIM(vf1BZ1mG2WE@06:22), CLAIM(6XcDHOlBARc@02:03) | consensus | yes |
| 13 | Reserve variants for state and shape; express content differences with properties (text field, show/hide boolean, instance swap) or the variant count explodes | Flux Academy, Jesse Showalter, DesignCourse | CLAIM(aGvWDDPsjUM@02:57), CLAIM(oCVG6DFCTz4@03:57), CLAIM(KWUlkXZOj4g@11:38) | consensus | yes |
| 14 | On an instance-swap property, set preferred values to the few components that slot accepts, so the picker stops offering the whole library | Flux Academy | CLAIM(aGvWDDPsjUM@10:18) | single-source | yes |
| 15 | Order each component property panel as: show/hide toggle first, then the editable field it reveals | Flux Academy | CLAIM(aGvWDDPsjUM@11:25) | single-source | yes |
| 16 | Nest components on purpose (a button row holding buttons, an accordion holding panels) and make style changes at the deepest master so they propagate up through every parent | Jesse Showalter | CLAIM(Sfy5wG5ZB3A@13:20), CLAIM(Sfy5wG5ZB3A@13:58) | single-source | yes |
| 17 | For regions whose content will change later (cards, popups, dropdowns), convert an auto-layout frame inside the component into a slot, then set a preferred instance and a written note describing what belongs there | Punit Chawla | CLAIM(beUlX6L2NMg@01:21), CLAIM(beUlX6L2NMg@02:30) | single-source | no |
| 18 | Enumerate the full option set (label only, icon left, icon right, icon only) before creating the component, and build those controls in at creation time | Jesse Showalter | CLAIM(Sfy5wG5ZB3A@01:32) | single-source | yes |

### Responsive and adaptive construction

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 19 | Construct from the inside out: auto-layout the smallest group, then wrap groups in another auto layout, instead of dropping loose layers into one outer frame | Jesse Showalter | CLAIM(oXDAmwEWlDc@02:42), CLAIM(oXDAmwEWlDc@07:48) | single-source | yes |
| 20 | After wrapping, set each child explicitly to hug contents or fill container; children left on defaults break the moment the parent stretches | Jesse Showalter, DesignCourse | CLAIM(oXDAmwEWlDc@08:23), CLAIM(iLWaIx7tMnU@06:58) | consensus | yes |
| 21 | Anchor fixed decorations with constraints first (avatar top-right, caption bottom-left), then add auto layout on top | Jesse Showalter | CLAIM(oXDAmwEWlDc@02:32) | single-source | yes |
| 22 | Design one layout that stretches until it breaks, and add a breakpoint variant (desktop, tablet, mobile) only at the size where it fails; do not design each device separately | Jesse Showalter | CLAIM(oXDAmwEWlDc@22:48) | single-source | yes |
| 23 | Give fill-container children a min and a max width and turn on wrap so rows reflow; fixed-width children under wrap leave dead space at the row end | Jesse Showalter | CLAIM(oXDAmwEWlDc@20:25), CLAIM(oXDAmwEWlDc@21:04) | single-source | yes |
| 24 | When hiding a child changes a bar's height, set the bar height explicitly so sibling screens stay aligned | Jesse Showalter | CLAIM(oXDAmwEWlDc@14:32) | single-source | yes |
| 25 | Stretch-test the element on the canvas before componentizing, and fix constraints and auto layout until the stretch behaves | Jesse Showalter, DesignCourse | CLAIM(oXDAmwEWlDc@06:29), CLAIM(KWUlkXZOj4g@03:55) | consensus | yes |
| 26 | Keep padding, gaps, and margins on an 8px grid, choosing values divisible by eight | Flux Academy, Jesse Showalter | CLAIM(vf1BZ1mG2WE@16:54), | consensus | yes |

### Interactive states and prototyping

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 27 | Ship every interactive element as a state matrix: default, hover or focus, active or typed, plus any popup or suggestion row, each as its own variant | DesignCourse, Flux Academy | CLAIM(iLWaIx7tMnU@07:43), CLAIM(z7amr9d5ORA@03:51) | consensus | yes |
| 28 | Wire prototype links on the component set rather than on instances, so every placement inherits the behavior | Flux Academy, Jesse Showalter | CLAIM(1JZcMnecWHI@07:03), CLAIM(z7amr9d5ORA@04:49) | consensus | yes |
| 29 | Standard timing set: smart animate around 300ms for small hover feedback, 500ms ease-in-out for card and theme changes, and an after-delay trigger near 500ms for content that appears while typing | Flux Academy, DesignCourse | CLAIM(1JZcMnecWHI@06:22), CLAIM(vf1BZ1mG2WE@21:50), CLAIM(iLWaIx7tMnU@17:41), CLAIM(z7amr9d5ORA@04:54) | consensus | yes |
| 30 | Drive state changes with a click interaction that both swaps the variant and writes variables through set-variable actions | DesignCourse, Flux Academy | CLAIM(Tx45NcbU6aA@04:40), CLAIM(vf1BZ1mG2WE@25:35) | consensus | yes |
| 31 | Wrap any decrement or bounded counter in a conditional so the value cannot cross its floor | DesignCourse | CLAIM(Tx45NcbU6aA@11:25) | single-source | no |
| 32 | Every filter or tab click sets the chosen variable true and all sibling variables false in the same interaction; the all-option sets every variable true | Flux Academy | CLAIM(vf1BZ1mG2WE@26:23), CLAIM(vf1BZ1mG2WE@27:53) | single-source | yes |
| 33 | Name the animated layer identically in every variant (the highlight layer on all states) or smart animate will not interpolate it | Flux Academy | CLAIM(1JZcMnecWHI@05:29) | single-source | yes |
| 34 | Zero the pass-through of inactive layers before combining states into one component set | DesignCourse | CLAIM(iLWaIx7tMnU@13:25) | single-source | no |

### Pattern recipes

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 36 | Search input carries a floating label: about 18px at rest, about 14px floated up when typing starts, so the field name never disappears | DesignCourse | CLAIM(iLWaIx7tMnU@08:00), CLAIM(iLWaIx7tMnU@08:32) | single-source | no |
| 37 | Search input ships four states: resting, focus with the float animation, typed with a suggestion list (rows with hover), and a did-you-mean row whose corrected keyword is bold and colored | DesignCourse | , CLAIM(iLWaIx7tMnU@12:41) | single-source | no |
| 38 | Derive strokes and secondary fills from the background hue darkened slightly; never drop a pure gray next to a colored surface; reserve full saturation for the focus state | DesignCourse | CLAIM(iLWaIx7tMnU@03:12), CLAIM(iLWaIx7tMnU@04:31) | single-source | no |
| 39 | Relate a nested control radius to its container (inner about half the outer) so the edges flow instead of clashing | DesignCourse | CLAIM(iLWaIx7tMnU@04:58) | single-source | no |
| 40 | For a hover ripple on a button, mask the growing shape with a copy of the button shape so the effect cannot escape the button bounds | DesignCourse | CLAIM(KWUlkXZOj4g@06:25) | single-source | no |
| 41 | Glass panels: hold one light direction and intensity across the whole site, keep glass depth low (under roughly 20-30), and raise frost to about 20 so overlaid text stays readable | Punit Chawla | CLAIM(3ERrrTcx09c@01:33), CLAIM(3ERrrTcx09c@02:30) | single-source | no |
| 42 | Neobrutalist card recipe: remove the soft shadow, add thick high-contrast strokes to container and image, then a hard shadow offset about 4/4 with zero blur at full opacity, vibrant colors, one playful graphic | DesignCourse | CLAIM(4BEEoYYDmUg@02:39), CLAIM(4BEEoYYDmUg@02:37) | single-source | no |
| 43 | Design a control inside its real layout context (grid on, target artboard) rather than in isolation on the canvas | DesignCourse | CLAIM(KWUlkXZOj4g@02:02) | single-source | no |
| 44 | Glassmorphism recipe (background-blur method): rounded shape near 20px radius, angled light-gray gradient fill with stops near 60 and 10 percent opacity, background blur near 50, then a 2px white gradient stroke on that same diagonal with the same opacity stops | Jesse Showalter | CLAIM(AdNOcgK_6Bs@00:30), CLAIM(AdNOcgK_6Bs@01:17), CLAIM(AdNOcgK_6Bs@01:51) | single-source | yes |
| 45 | Do not ship a glass panel until colored shapes sit behind it and the card has been tested on a saturated surface; an empty backdrop hides the frost and the rim | Jesse Showalter | CLAIM(AdNOcgK_6Bs@02:10), CLAIM(AdNOcgK_6Bs@02:24) | single-source | yes |
| 46 | Never delete the master once instances exist; park it and hide it so the source stays available | Jesse Showalter | CLAIM(6XcDHOlBARc@01:30) | single-source | yes |
| 47 | Size the button to its label so editing the word resizes the control; in Figma, auto-layout and center the label before you componentize | Jesse Showalter, Satori Graphics | CLAIM(6XcDHOlBARc@00:30), CLAIM(6XcDHOlBARc@01:01), CLAIM(VMQasbs3Xkk@00:55) | consensus | yes |
| 48 | Style each new variant on that variant alone, then rename it before adding the next: outline strips the fill, uses a 2px brand stroke, and recolors the label to that brand; shadow uses a brand drop shadow near 10 percent opacity with the blur raised | Jesse Showalter | CLAIM(6XcDHOlBARc@02:45), CLAIM(6XcDHOlBARc@03:18), CLAIM(6XcDHOlBARc@03:33) | single-source | yes |
| 49 | Before drawing, pull the reference typeface and grays, line a screenshot against the live layout to record gap and frame size, and unclip the source so you count the real item set | Flux Academy | CLAIM(z7amr9d5ORA@01:11), CLAIM(z7amr9d5ORA@02:25), CLAIM(z7amr9d5ORA@07:46) | single-source | yes |
| 50 | Horizontal scroller: set overflow to horizontal, keep position as scroll-with-parent, and shrink the frame so the content is wider than the viewport; put trailing air on a wrapper around the last item | Flux Academy | CLAIM(z7amr9d5ORA@07:47), CLAIM(z7amr9d5ORA@07:56), CLAIM(z7amr9d5ORA@08:41) | single-source | yes |
| 51 | Make every interactive control at least 44px tall | Flux Academy | CLAIM(z7amr9d5ORA@11:53) | single-source | yes |
| 52 | Multi-hue stroke: put a gradient on the stroke, add one stop per sampled source color, and spread the stops so no hue clumps | Flux Academy | CLAIM(z7amr9d5ORA@13:14), CLAIM(z7amr9d5ORA@13:36), CLAIM(z7amr9d5ORA@14:15) | single-source | yes |
| 53 | Accordion hit target is the whole heading row, not the chevron alone; the open row shows the matching image and an up chevron, and closed rows point down | Flux Academy | CLAIM(z7amr9d5ORA@17:40), CLAIM(z7amr9d5ORA@20:46) | single-source | yes |
| 54 | Replace a dividing line with a 1px-tall rectangle: it snaps to whole pixels, accepts a fill and stacked strokes, and has a selectable hit area | Flux Academy | CLAIM(z3B1pUzyarM@01:14), CLAIM(z3B1pUzyarM@01:09), CLAIM(z3B1pUzyarM@01:42) | single-source | yes |
| 55 | Build circular avatars as squares with radius 9999 and proportions constrained, so the same component can become a rounded rect or return to a circle | Flux Academy | CLAIM(z3B1pUzyarM@06:44), CLAIM(z3B1pUzyarM@08:02), CLAIM(z3B1pUzyarM@08:19) | single-source | yes |
| 56 | Do not ship pencil paths as interface shapes: an open path takes neither a fill nor a reversed stroke until you close it; use the pen tool or a scanned drawing | Flux Academy | CLAIM(z3B1pUzyarM@03:21), CLAIM(z3B1pUzyarM@03:40) | single-source | yes |
| 57 | Name frames as you create them; a stack of generator names cannot be found once nesting gets deep | Flux Academy | CLAIM(z3B1pUzyarM@04:07), CLAIM(z3B1pUzyarM@04:13) | single-source | yes |
| 58 | Keep a symbol cutout as a compound path and rotate it from an explicit anchor, including the visual center, so the edit stays non-destructive | Satori Graphics | CLAIM(VMQasbs3Xkk@01:12), CLAIM(VMQasbs3Xkk@01:58), CLAIM(VMQasbs3Xkk@02:15) | single-source | yes |
| 59 | Transform each repeated object on its own center (rotate, move, scale, or reflect); do not rotate the selection as one group when each copy should turn in place | Satori Graphics | CLAIM(VMQasbs3Xkk@02:56), CLAIM(VMQasbs3Xkk@03:07) | single-source | yes |
| 60 | Generate a swatch ramp from the brief's two to four colors, then curate before those squares enter the library | Satori Graphics | CLAIM(VMQasbs3Xkk@03:36), CLAIM(VMQasbs3Xkk@03:51), CLAIM(VMQasbs3Xkk@04:24) | single-source | yes |
| 61 | Turn construction geometry for a grid into guides, not leftover strokes | Satori Graphics | CLAIM(VMQasbs3Xkk@04:47), CLAIM(VMQasbs3Xkk@04:58) | single-source | yes |
| 62 | Hand off a multi-artboard file as one file per artboard when another person must open a single board | Satori Graphics | CLAIM(VMQasbs3Xkk@05:14), CLAIM(VMQasbs3Xkk@05:25) | single-source | yes |
| 63 | A card can be a filled container or a borderless stack of the same fields; a background is not required. On a light page, a card lighter than the page pulls emphasis | DesignCourse | CLAIM(jXEn5IFxmAc@02:17), CLAIM(jXEn5IFxmAc@03:21), CLAIM(jXEn5IFxmAc@13:05) | single-source | no |
| 64 | Set card width by placing duplicates in the row and stopping where the gap is neither cramped nor sparse | DesignCourse | CLAIM(jXEn5IFxmAc@03:39), CLAIM(jXEn5IFxmAc@03:54) | single-source | no |
| 65 | Keep inner card padding in the middle: text at the edge fails, and a huge inset fails. Group the title with its description tighter than the gap down to the button | DesignCourse | CLAIM(jXEn5IFxmAc@07:22), CLAIM(jXEn5IFxmAc@07:38) | single-source | no |
| 66 | Do not reuse the hero button at hero scale inside a card; shrink the control and the type so hierarchy survives | DesignCourse | CLAIM(jXEn5IFxmAc@08:26) | single-source | no |
| 67 | A status chip is a small label, about 14px, on a padded rounded plate that reuses a color already in the file | DesignCourse | CLAIM(jXEn5IFxmAc@05:58), CLAIM(jXEn5IFxmAc@06:19) | single-source | no |
| 68 | Cards inherit the page type and color. A display face used for a three-word lockup does not enter card body or titles | DesignCourse | CLAIM(jXEn5IFxmAc@14:53), CLAIM(jXEn5IFxmAc@15:24) | single-source | no |
| 69 | On a borderless card over a colored page, drop the button stroke and give it a solid fill so the control still reads | DesignCourse | CLAIM(jXEn5IFxmAc@13:25) | single-source | no |

## Looks like / does not (good vs bad pairs)

| # | looks like (good) | does not (bad) | why | citation |
|---|-------------------|----------------|-----|----------|
| 1 | Every repeated color and radius bound to a named variable | Raw values retyped into each element | One edit propagates; drift is impossible | CLAIM(GUupJJC5Ac4@00:18) |
| 2 | Button recolor done by repointing its semantic token | Editing one shared style that also repaints links and the logo | Semantic tokens isolate roles | CLAIM(GUupJJC5Ac4@05:35) |
| 3 | Variant set whose axis reads State equals default, hovered | Set labeled property 1 with variant 2 inside | Readable sets survive handoff | CLAIM(aGvWDDPsjUM@05:21) |
| 4 | Icon swap through an instance-swap property with preferred values | Scrolling a full icon library on every instance | Preferred values constrain the picker | CLAIM(aGvWDDPsjUM@10:18) |
| 5 | Nested auto layouts built inner group first | One basket frame stuffed with loose layers | Nesting survives resizing | CLAIM(oXDAmwEWlDc@03:45) |
| 6 | Each child told to fill the container or hug | Children left on defaults so the stretch scatters them | Parent control needs explicit child sizing | CLAIM(oXDAmwEWlDc@08:23) |
| 7 | Gallery rows that reflow via min/max width plus wrap | Fixed-width rows under wrap with a dead gap at each line end | Fill plus bounds distributes the remainder | CLAIM(oXDAmwEWlDc@21:04) |
| 8 | Nav that swaps to a hamburger variant at the breakpoint | Nav that keeps shrinking until buttons collide | Crowding is the failure signal | CLAIM(oXDAmwEWlDc@13:45) |
| 9 | Floating label that rises and shrinks when typing starts | Placeholder-only field whose label vanishes on focus | Field name stays visible | CLAIM(iLWaIx7tMnU@08:00) |
| 10 | Search shown as default, focus, typed, suggestions, did-you-mean states | A single static bar with no state documentation | Developers cannot infer behavior | CLAIM(iLWaIx7tMnU@14:23) |
| 11 | Stroke taken from the background hue and darkened a step | Pure gray stroke beside a colored panel | Hue-derived neutrals read as one system | CLAIM(iLWaIx7tMnU@04:31) |
| 12 | Inner control radius half the container radius | Rounded button sitting in a square container | Related radii flow | CLAIM(iLWaIx7tMnU@04:58) |
| 13 | Seat counter with a conditional that stops at the floor | Counter that decrements into negative numbers | Prototypes should refuse impossible states | CLAIM(Tx45NcbU6aA@11:25) |
| 14 | One gallery whose visibility is driven by boolean variables | A duplicated page per filter with a hand-wired switcher | Variables keep one source of truth | CLAIM(vf1BZ1mG2WE@19:42) |
| 15 | Highlight layer named the same in every state | Layers renamed per variant so the animation snaps | Smart animate matches by name | CLAIM(1JZcMnecWHI@05:29) |
| 16 | Images with aspect ratio locked inside an auto layout | Images that squash and stretch with the card | Locked ratio keeps proportions | CLAIM(M8msUKBSBlY@01:23) |
| 17 | Glass card with frost around 20 over readable text | Heavy frost that reads as plastic, or none at all | Frost is the accessibility lever | CLAIM(3ERrrTcx09c@02:30) |
| 18 | Neobrutalist card with hard 4/4 zero-blur shadow and thick stroke | The same card with a soft blurred drop shadow | The recipe is defined by hard edges | CLAIM(4BEEoYYDmUg@02:37) |
| 19 | Button animated on the component so every instance inherits it | Re-animating the tab bar per instance | Component-level prototype links scale | CLAIM(1JZcMnecWHI@07:03) |
| 20 | Property panel ordered show-toggle first, editable value below | Toggles and fields in creation order | Editors find controls predictably | CLAIM(aGvWDDPsjUM@11:25) |
| 21 | Glass card with shapes behind it and a thin gradient rim, also tested on a saturated field | Pale rounded rectangle on an empty canvas | Frost and rim only read when something shows through | CLAIM(AdNOcgK_6Bs@02:15) |
| 22 | One Button asset whose instance swaps fill, outline, or shadow | A separate component for every button style | Variants keep the assets panel to one control | CLAIM(6XcDHOlBARc@04:27) |
| 23 | Horizontal overflow with the frame smaller than the card row, and trailing padding on the last item | A card row set to no scrolling, last card flush to the clip | The viewport is the frame; content must exceed it, and the end needs air | CLAIM(z7amr9d5ORA@07:56) |
| 24 | Whole heading row as the accordion click target, chevron direction matching open versus closed | Only the tiny chevron is clickable | The live control accepts a click on the heading, not just the icon | CLAIM(z7amr9d5ORA@20:46) |
| 25 | Stroke gradient sampled stop by stop from the reference | A two-stop gradient that only approximates the rainbow | Sampling each stop keeps the hue order | CLAIM(z7amr9d5ORA@13:32) |
| 26 | 1px rectangle divider on whole pixels, with a fill | A line on decimal coordinates and a 1px hit target | A rectangle matches a web divider and stays selectable inside auto layout | CLAIM(z3B1pUzyarM@01:14) |
| 27 | Avatar built as a square at radius 9999 inside a component | A true ellipse used everywhere, then a request to round the corners | An ellipse cannot become a rounded rectangle | CLAIM(z3B1pUzyarM@08:10) |
| 28 | Closed pen shape, or a scanned drawing traced with the pen | Pencil squiggle used as an icon, fill doing nothing | Open paths cannot take a fill | CLAIM(z3B1pUzyarM@03:23) |
| 29 | Label whose plate grows when the word changes | Fixed button you retype into until the text clips | The container is a function of the label | CLAIM(VMQasbs3Xkk@00:55) |
| 30 | Each repeated mark rotated on its own center | The whole selection rotated as one group | In-place rotation keeps the layout | CLAIM(VMQasbs3Xkk@02:56) |
| 31 | Swatch ramp expanded into individual squares and added to the library | A two-color guess with no steps between | The steps are the ramp; the library is the system | CLAIM(VMQasbs3Xkk@04:08) |
| 32 | Lighter card than the page, gap tested by duplication, title grouped with the description | Darker card, text flush to the edge, hero-scale button inside | Emphasis, padding, and hierarchy are the card | CLAIM(jXEn5IFxmAc@03:21) |
| 33 | Status chip at about 14px reusing an existing color | A second title-size label in a new color | The chip is a label, not another heading | CLAIM(jXEn5IFxmAc@06:01) |
| 34 | Borderless stack whose button has a solid fill | Borderless stack whose stroked button disappears on the page | The control still has to read | CLAIM(jXEn5IFxmAc@13:28) |

## Decision tables (option A vs B -> pick when)

| choice | pick A when | pick B when | citation |
|--------|-------------|-------------|----------|
| Variables vs styles | A role must be recolored or resized without touching other roles; spacing, radius, counts need binding | You only need a single shared type or color definition with no role separation | CLAIM(GUupJJC5Ac4@00:44) |
| Variant vs component property | The difference is state or shape (hover, pill versus rounded, horizontal versus vertical) | The difference is content or presence (label text, icon shown, which icon) | CLAIM(aGvWDDPsjUM@02:57) |
| Auto layout vs constraints | Children must reflow with content size and container growth | An element is a fixed decoration anchored to one corner | CLAIM(oXDAmwEWlDc@01:42) |
| Stretch vs breakpoint variant | The layout still reads at the smaller size | Elements crowd or collide; then swap to a purpose-built variant | CLAIM(oXDAmwEWlDc@22:48) |
| Fill vs hug vs fixed width | Row items should share available space (fill), size to their content (hug) | A spec mandates one exact width, and wrap plus min/max cannot express it | CLAIM(oXDAmwEWlDc@06:08) |
| Boolean filter vs variable mode vs page copy | Filtering visible items (booleans); theme swaps (modes) | Never use page copies; they are the rejected path | CLAIM(vf1BZ1mG2WE@19:42) |
| Hover trigger vs click trigger vs after-delay | Hover for passive feedback, click for committed state change, after-delay for progressive disclosure like suggestions | Mixing them: do not use click where hover feedback is enough | CLAIM(iLWaIx7tMnU@17:41) |
| Component slot vs nested component | The region will hold swappable content decided later by other designers | The region content is fixed and just needs reuse | CLAIM(beUlX6L2NMg@02:30) |
| One component set vs one asset per style | The objects are styles of the same control (fill, outline, shadow, size) | The objects are different controls | CLAIM(6XcDHOlBARc@04:43) |
| Smart animate vs instant | The change is size, position, or a hover expansion | The change is which accordion section is open | CLAIM(z7amr9d5ORA@04:54) |
| 1px rectangle vs line tool | The mark is a divider, rule, or bar that must snap, fill, and be selectable | You need an open stroke with arrow ends | CLAIM(z3B1pUzyarM@01:14) |
| Rounded square vs ellipse | The circle may later become a rounded rect, or it lives in a component | The shape must stay a non-circular oval | CLAIM(z3B1pUzyarM@08:12) |
| Transform each vs rotate the selection | Every copy should turn, move, or scale on its own center | The group should move as one object | CLAIM(VMQasbs3Xkk@03:02) |
| Filled card vs borderless card | The section needs a plate and higher contrast against the page | The page already groups the fields and a plate would add noise | CLAIM(jXEn5IFxmAc@13:41) |
| Icon before title vs title before icon | Either order is allowed; pick one per system and keep it across sibling cards | Do not mix the order across sibling cards | CLAIM(jXEn5IFxmAc@04:22) |

## Anti-patterns (cited)

- Duplicating one page per filter state and wiring a switcher between the copies (CLAIM(vf1BZ1mG2WE@18:46)).
- Duplicating an element and editing each copy every time the design changes (CLAIM(aGvWDDPsjUM@00:02)).
- Designing a button in isolation on an empty canvas, then dropping it into layouts (CLAIM(KWUlkXZOj4g@02:02)).
- One outer frame holding loose children with no nested auto layout (CLAIM(oXDAmwEWlDc@02:53)).
- Placeholder text as the only field label (CLAIM(iLWaIx7tMnU@08:00)).
- Pure neutral gray fills placed next to colored surfaces (CLAIM(iLWaIx7tMnU@04:31)).
- Rounded control inside a square container with no radius relationship (CLAIM(iLWaIx7tMnU@04:58)).
- A quantity control that can decrement past its floor (CLAIM(Tx45NcbU6aA@10:55)).
- Animating each instance separately instead of the master (CLAIM(1JZcMnecWHI@07:03)).
- Editing instance internals instead of the master component (CLAIM(1JZcMnecWHI@00:57)).
- Changing glass lighting direction panel by panel (CLAIM(3ERrrTcx09c@01:33)).
- Soft blurred shadow on a card that is meant to read as neobrutalist (CLAIM(4BEEoYYDmUg@01:35)).
- Leaving variant property names at tool defaults in a shipped component set (CLAIM(iLWaIx7tMnU@17:08)).
- Letting children keep default sizing inside an auto layout parent (CLAIM(oXDAmwEWlDc@08:23)).
- Calling a pale rounded rectangle glass before anything sits behind it (CLAIM(AdNOcgK_6Bs@02:01)).
- Deleting the master component after instances exist (CLAIM(6XcDHOlBARc@01:30)).
- Building a horizontal scroller without shrinking the frame below the content width (CLAIM(z7amr9d5ORA@07:56)).
- Making only the chevron the accordion hit target (CLAIM(z7amr9d5ORA@20:46)).
- Using the line tool for dividers inside auto layout (CLAIM(z3B1pUzyarM@01:02)).
- Drawing avatars with the ellipse tool when the radius may still change (CLAIM(z3B1pUzyarM@06:49)).
- Leaving frames at generator names such as frame 69 (CLAIM(z3B1pUzyarM@04:07)).
- Rotating a multi-selection when each object should rotate in place (CLAIM(VMQasbs3Xkk@02:56)).
- Pushing card text to the inner edge (CLAIM(jXEn5IFxmAc@07:22)).
- Dropping the hero button into a card at hero size (CLAIM(jXEn5IFxmAc@08:26)).
- Using a display lockup face for card body (CLAIM(jXEn5IFxmAc@15:24)).

## Creator claims (unverified)

- Jesse Showalter says his tips multiply design speed and beat 90 percent of designers (CLAIM(oCVG6DFCTz4@00:05)); no measurement given.
- Jesse Showalter advertises a 30-day program with over 150 lessons and 35 hours of curriculum (CLAIM(oXDAmwEWlDc@11:38)).
- Gary Simon claims his course lifts layouts he would rate four or five up to eight and beyond (CLAIM(iLWaIx7tMnU@00:48)).
- Punit Chawla expects slots to save substantial time on large projects with many swappable elements (CLAIM(beUlX6L2NMg@03:17)).
- Mike Locke calls the silver gradient button neutral enough to work on any background (CLAIM(_NTvNAaetCM@06:08)).
- Jesse Showalter calls Mobbin the premier inspiration library for interface designers (CLAIM(M8msUKBSBlY@01:41)).
- Gary Simon dates neobrutalism as the most popular trend of 2022, continuing into 2023 (CLAIM(4BEEoYYDmUg@00:05)).
- Jesse Showalter (2021) treats glassmorphism as a live trend already used by Apple and Microsoft and common on Dribbble (CLAIM(AdNOcgK_6Bs@00:01)); no count or study given.
- Jesse Showalter says variants let you work smart rather than hard and that Figma makes a pattern library very easy (CLAIM(6XcDHOlBARc@00:15), CLAIM(6XcDHOlBARc@05:00)); no measurement.
- Maddy at Flux Academy (2024) says recreating an Apple page is simple and a good beginner Figma exercise (CLAIM(z7amr9d5ORA@00:11)); opinion, no outcome measure.
- Devin at Flux Academy (2023) says dropping the line tool, hand tool, pencil, layer list, and circles makes you faster within a week (CLAIM(z3B1pUzyarM@08:30)); no measurement.
- Satori Graphics (2022) says these Illustrator functions are hidden and that few people know transform-each or path-to-guide (CLAIM(VMQasbs3Xkk@00:04), CLAIM(VMQasbs3Xkk@03:25)); no survey.
- Gary Simon (2024) says icon-before-title versus title-first has no right answer (CLAIM(jXEn5IFxmAc@04:27)), and that a card button fill versus a stroke has no single correct style (CLAIM(jXEn5IFxmAc@09:59)). Judgment, not a test.

## Tool-specific (dated)

- Figma variables, collections, and modes, 2023: variables were in beta on desktop; set-variable prototype actions and extra modes required the file to live in a team (CLAIM(Tx45NcbU6aA@04:26), CLAIM(Tx45NcbU6aA@04:23)).
- Figma variables, 2023 limitation: modes could not be switched by a prototype interaction, only manually per frame (CLAIM(Tx45NcbU6aA@25:50)).
- Figma Slots, public beta 2026: a frame inside a component can be converted to a slot; dev mode emits a slot tag in generated code (CLAIM(beUlX6L2NMg@00:30), CLAIM(beUlX6L2NMg@01:21)).
- Figma glass effect, beta 2025: applies to frames only, not bare shapes or rectangles; lighting and refraction are adjustable per panel (CLAIM(3ERrrTcx09c@00:40), CLAIM(3ERrrTcx09c@01:00)).
- Figma 2024-2025 updates: aspect-ratio lock replacing constrain proportions (CLAIM(M8msUKBSBlY@00:23)), a collapse-all-layers control in the layers panel (CLAIM(M8msUKBSBlY@00:30)), drag-to-reorder of modes and collections (CLAIM(M8msUKBSBlY@02:56)), contrast readout inside the color picker (CLAIM(M8msUKBSBlY@03:55)), copy and paste of text/color/effect styles between files (CLAIM(M8msUKBSBlY@04:50)).
- Framer components 2024: text, color, and visibility variables attach to main-component layers and appear on every variant; interactions between variants auto-wire a transition you can edit per instance (CLAIM(Sfy5wG5ZB3A@08:33), CLAIM(Sfy5wG5ZB3A@06:25)).
- Adobe Fireworks 2009 button recipe: pill rectangle with white-to-dark gray linear gradient, larger backing shape at 30 percent opacity as a shadow plate, drop shadow near 3/4/80, dark gray label with a white 2px softness-1 shadow to fake engraving (CLAIM(_NTvNAaetCM@02:14), CLAIM(_NTvNAaetCM@03:25)).
- Figma community Breakpoints plugin (paid, 2023) drives multi-width responsive preview; without it, breakpoint behavior is documented as separate frames (CLAIM(oXDAmwEWlDc@17:34)).
- Figma 2021 glassmorphism is built from a background-blur effect plus a gradient fill and a gradient stroke, not a native glass material (CLAIM(AdNOcgK_6Bs@01:15), CLAIM(AdNOcgK_6Bs@01:31)).
- Figma variants, 2021: select the master and use the inspector plus, which wraps it in a dashed variant frame; a slash in the layer name becomes the property; further plus clicks append variants (CLAIM(6XcDHOlBARc@01:48), CLAIM(6XcDHOlBARc@02:03), CLAIM(6XcDHOlBARc@03:10)).
- Figma 2024 prototype overflow: horizontal scrolling is a scroll-behavior setting; position stays scroll with parent (CLAIM(z7amr9d5ORA@07:44)).
- Figma 2024 stroke gradients accept extra color stops you can sample from a reference (CLAIM(z7amr9d5ORA@13:20)).
- Figma 2023 canvas habits Devin treats as replacements, not as laws of the interface: pan with spacebar-drag (trackpad: two-finger swipe) instead of the hand tool; hide the layer panel with command or ctrl shift backslash; drill with command or ctrl click, enter down, shift-enter up, tab to the next sibling; outline mode is command-Y (CLAIM(z3B1pUzyarM@02:35), CLAIM(z3B1pUzyarM@04:29), CLAIM(z3B1pUzyarM@04:48), CLAIM(z3B1pUzyarM@06:09)).
- Adobe Illustrator 2022: a responsive label is an appearance fill converted to a rounded rectangle, with corner nudges on the arrow keys and shift stepping by about 10 (CLAIM(VMQasbs3Xkk@00:16), CLAIM(VMQasbs3Xkk@00:31), CLAIM(VMQasbs3Xkk@00:44)). Outline mode is command or ctrl Y; group selection sits under the direct selection tool; alt or option click sets the rotate anchor (CLAIM(VMQasbs3Xkk@01:28), CLAIM(VMQasbs3Xkk@01:52)). Transform each is a right-click (CLAIM(VMQasbs3Xkk@03:07)). Swatch ramps use the blend tool (W), specified steps, expand, ungroup, then add to swatches (CLAIM(VMQasbs3Xkk@03:40)). Command or ctrl 5 turns a path into a guide (CLAIM(VMQasbs3Xkk@04:47)). Save As can write each artboard as its own file (CLAIM(VMQasbs3Xkk@05:20)).
- Figma 2024 card build: Iconify is a keyword-search plugin; drag icons in (CLAIM(jXEn5IFxmAc@01:28)). Paste with formatting is ctrl-V; paste without formatting is ctrl-shift-V (CLAIM(jXEn5IFxmAc@11:14)). Shift held on the pen tool draws the 45-degree card corners instead of a plain rectangle (CLAIM(jXEn5IFxmAc@02:48)).
- Figma bulk image replace by keyboard shortcut, documented 2024 (CLAIM(oCVG6DFCTz4@07:33)); GuideGuide plugin for guides and columns on individual elements (CLAIM(oCVG6DFCTz4@07:33)).

## Disagreements between creators (who says what, cited)

- Swapping icons inside a component: DesignCourse (2021) stacks several icons in the master and toggles visibility per instance, calling direct swap unworkable (); Flux Academy (2023) uses an instance-swap property with preferred values (CLAIM(aGvWDDPsjUM@10:00)). Later method supersedes.
- Hover feedback mechanism: DesignCourse (2021) grows a masked ripple shape (CLAIM(KWUlkXZOj4g@05:36)); Flux Academy (2023) changes opacity on the hovered variant (); DesignCourse (2022) darkens the fill one step (CLAIM(iLWaIx7tMnU@05:50)); Flux Academy (2024) scales the card image with smart animate on hover (CLAIM(z7amr9d5ORA@04:54)). No consensus on the mechanism, only that a hover state must exist.
- Section change timing: Flux Academy (2024) uses smart animate with ease in and out for a hover size change (CLAIM(z7amr9d5ORA@04:54)) and instant for accordion section swaps (CLAIM(z7amr9d5ORA@21:46)). Law 29's 300ms and 500ms figures are not restated here.
- Dividers: Maddy at Flux Academy (2024) draws accordion rules with the line tool (CLAIM(z7amr9d5ORA@16:37)); Devin at Flux Academy (2023) says replace lines with a 1px rectangle because lines land on decimals and cannot take a fill (CLAIM(z3B1pUzyarM@01:14)). Same channel, different teachers. Prefer the rectangle unless you need arrow ends.
- Card container: DesignCourse (2024) says a card does not need a background and shows a borderless stack as still a card (CLAIM(jXEn5IFxmAc@02:17)). The same channel's 2022 neobrutalist recipe assumes a stroked container (CLAIM(4BEEoYYDmUg@02:39)). Optional container versus a named style recipe, not a factual conflict.
- One-frame-per-state: Flux Academy (2024) rejects duplicated pages for filter states in favor of variables (CLAIM(vf1BZ1mG2WE@18:46)), while Jesse Showalter (2023) builds one frame per responsive width and switches between them at breakpoints (CLAIM(oXDAmwEWlDc@13:45)). Different problems: content filtering versus breakpoint demonstration; variables are still the wrong tool for showing three layout widths to a stakeholder.
- Button aesthetic: Mike Locke (2009) builds a skeuomorphic engraved gradient button with layered shadows (CLAIM(_NTvNAaetCM@04:38)); DesignCourse (2022) removes soft shadows and uses flat high-contrast strokes and hard offset shadows (CLAIM(4BEEoYYDmUg@01:35)). Era disagreement, not a factual conflict; both recipes are checkable and the choice is stylistic.
- Frost strength: Jesse Showalter (2021) sets background blur near 50 (CLAIM(AdNOcgK_6Bs@01:19)); Punit Chawla (2025) keeps native-glass depth under roughly 20-30 and frost near 20 so type stays readable (CLAIM(3ERrrTcx09c@02:30)). Different effects; do not copy the number from one tool year to the other.

## Suggested sub-skills

- ui-tokens-modes: variables as two-layer tokens, named scale levels, theme modes, boolean visibility bindings, curated swatch ramps (laws 1-8, 60).
- ui-components-variants: component sets, variant naming, properties over variants, slots, nesting, rectangle dividers, radius-9999 circles (laws 9-18, 46-48, 54-57).
- ui-responsive-construction: inside-out auto layout, explicit child sizing, constraints, min/max wrap, breakpoint variants, 8px grid, horizontal scrollers (laws 19-26, 50).
- ui-prototype-states: state matrices, component-level prototype links, timing standards, set-variable interactions, accordion hit targets (laws 27-35, 53).
- ui-pattern-recipes: search input states, surface color derivation, radius relationships, button ripple, glass, neobrutalist, tap target, multi-hue stroke, and card recipes (laws 36-45, 51-52, 63-69).
