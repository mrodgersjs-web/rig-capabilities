# UX laws (Design Studio OS corpus)

Coverage: 16 videos read (EDtgsIn1meM, D29KL52Srtw, cCun-ReLTFI, bNh54LNUtv8, dmlFRCZI9gQ, 23AQBZzDUIo, TKZl_UlXhYk, d-IaU9qcDGg, EKjCC4PwjFo, JavCEJ5hodc, 9viTvO0Okoo, 5-caRWzSQd4, 470go6su3Ys, P2W2AnK5aDE, -5jSCHZIHlg, HGsMNYq889U). Channels: Flux Academy, DesignCourse, NNgroup, Self-Made Web Designer, Mike Locke, DesignSense, Satori Graphics, CharliMarieTV. Publish dates 2017-11 to 2026-07. Top-10 sources in this set: flux-academy (2 videos), self-made-web-designer (1), satori-graphics (1).

## Laws

### Navigation and wayfinding

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 1 | Mark the current page in the nav with a distinct active state: color, weight, background, or icon. | DesignCourse | CLAIM(D29KL52Srtw@00:40) | single-source | no |
| 2 | Style the logo so it reads as a brand mark, not as another nav item. | DesignCourse | CLAIM(D29KL52Srtw@00:18) | single-source | no |
| 3 | Include an explicit Home entry in the nav; never make the logo the only path home. | DesignCourse | CLAIM(D29KL52Srtw@01:12) | single-source | no |
| 4 | Separate primary nav from secondary nav, and top-level items from dropdown items, with typographic hierarchy (weight, size, color). | DesignCourse | CLAIM(D29KL52Srtw@02:16), CLAIM(D29KL52Srtw@02:39) | single-source | no |
| 5 | Give every nav link a hover state that confirms the pointer target. | DesignCourse | CLAIM(D29KL52Srtw@03:07) | single-source | no |
| 6 | Place logo top-left and nav top-right; treat any other placement as a redesign risk and test it against user expectations before shipping. | DesignCourse, Self-Made Web Designer | CLAIM(D29KL52Srtw@05:40), CLAIM(d-IaU9qcDGg@02:52) | consensus | yes |
| 7 | Collapse the nav into a hamburger only when the links do not fit the viewport; never hide desktop links behind one. | DesignCourse | CLAIM(D29KL52Srtw@04:33) | single-source | no |
| 8 | Size nav items and icons so they are easy to hit on touch, with clear space around each (at least 44px for icon-only controls), and keep frequently tapped primary controls apart from destructive or secondary ones so mis-taps do not fire them. | Flux Academy, DesignCourse | CLAIM(D29KL52Srtw@06:37), CLAIM(EDtgsIn1meM@09:05), | consensus | yes |
| 9 | Keep a visible keyboard focus state on every interactive element; if the default outline is removed, design a replacement. | Flux Academy, DesignCourse | CLAIM(D29KL52Srtw@05:58), | consensus | yes |
| 10 | Write link text that names the destination or action; never ship a link whose text is a generic call like click-through wording. | Flux Academy | CLAIM(EDtgsIn1meM@07:45) | single-source | yes |
| 11 | Use real heading tags (H1, H2, H3) for page structure so screen-reader users and scanners can navigate the outline. | Flux Academy | CLAIM(EDtgsIn1meM@06:57) | single-source | yes |
| 12 | Never convey an instruction or a state through color or shape alone, and when an icon meaning is unclear, replace the icon with a plain word that matches platform conventions users already know. | Flux Academy | CLAIM(EDtgsIn1meM@08:26), CLAIM(TKZl_UlXhYk@04:43), CLAIM(TKZl_UlXhYk@04:50) | single-source | yes |

### Forms and input

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 13 | Give every input a persistent visible label; a placeholder is never the label. | DesignCourse, Flux Academy | CLAIM(5-caRWzSQd4@04:02), CLAIM(EDtgsIn1meM@09:51) | consensus | yes |
| 14 | Name fields explicitly (First name, not Name) so the expected input is unambiguous. | DesignCourse | CLAIM(5-caRWzSQd4@04:12) | single-source | no |
| 15 | Design every form control as a component with named states: default, focus, typed, error. | DesignCourse | CLAIM(5-caRWzSQd4@00:20), CLAIM(EKjCC4PwjFo@09:02) | single-source | no |
| 16 | Show focus by darkening and thickening the field border (roughly 1px to 1.5px or 1px to 3px), not by other decoration. | DesignCourse | CLAIM(5-caRWzSQd4@14:34), CLAIM(EKjCC4PwjFo@11:14) | single-source | no |
| 17 | Give the field fill and border enough contrast to be perceived; when the fill is close to the page color, add a mid-gray stroke rather than leaving the field almost invisible. | DesignCourse | CLAIM(EKjCC4PwjFo@03:12), CLAIM(5-caRWzSQd4@06:27) | single-source | no |
| 18 | Size field height to a middle value with generous inner padding; never ship cramped or over-tall inputs. | DesignCourse | CLAIM(5-caRWzSQd4@05:42), CLAIM(EKjCC4PwjFo@04:52) | single-source | no |
| 19 | Keep one field aesthetic across the whole form: the same fill, stroke, and radius on text fields, text areas, checkboxes, selects, and buttons. | DesignCourse | CLAIM(5-caRWzSQd4@24:05) | single-source | no |
| 20 | Place error text directly under the failing field, not near the submit button. | DesignCourse | CLAIM(EKjCC4PwjFo@06:15) | single-source | no |
| 21 | Write error copy that states what happened in plain language and how to fix it, naming the rule that failed (for example a banned character), and color the failing field outline and its message with the error color so label, field, and message read as one problem. | NNgroup, DesignCourse | CLAIM(cCun-ReLTFI@00:41), CLAIM(5-caRWzSQd4@08:36), CLAIM(5-caRWzSQd4@09:32), | consensus | no |
| 22 | Put the fix inside the error message: a one-click remedy (removable filters, a corrected value) beats instructions the user must go apply elsewhere. | NNgroup | CLAIM(cCun-ReLTFI@01:06), CLAIM(cCun-ReLTFI@01:14) | single-source | no |
| 24 | Set error and helper type no smaller than 14px, and keep label, value, and error text at three distinct hierarchy levels inside one field. | DesignCourse | CLAIM(5-caRWzSQd4@09:05), CLAIM(5-caRWzSQd4@09:05) | single-source | no |
| 25 | Make the form primary submit button the strongest-colored element in the form, using the theme primary color. | DesignCourse, Satori Graphics | CLAIM(5-caRWzSQd4@21:40), | consensus | yes |
| 26 | Change button hover by a subtle lightening only; a hover that flips background and text color is too large a jump. | DesignCourse | CLAIM(5-caRWzSQd4@23:13) | single-source | no |
| 27 | Constrain form fields to a readable column (one column centered, or a two-column split such as 60/40); never stretch inputs across the full screen width. | DesignCourse | CLAIM(EKjCC4PwjFo@21:30) | single-source | no |
| 28 | Mask password fields on entry, style the terms link as a link beside its checkbox, and give checkbox marks breathing room inside their box. | DesignCourse | CLAIM(EKjCC4PwjFo@19:18), CLAIM(EKjCC4PwjFo@19:14), CLAIM(EKjCC4PwjFo@20:30) | single-source | no |

### Accessibility

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 29 | Hold text contrast at 4.5:1 or better against its background, and verify it with a contrast checker rather than by eye. | Flux Academy, DesignCourse | CLAIM(EDtgsIn1meM@04:23), CLAIM(D29KL52Srtw@03:40) | consensus | yes |
| 30 | Write alt text that describes the image content; for a linked image, describe its function (home, search) instead of its artwork. | Flux Academy | CLAIM(EDtgsIn1meM@00:43), CLAIM(EDtgsIn1meM@01:12) | single-source | yes |
| 31 | Keep meaningful copy as real page text; if text must sit inside an image, repeat it in surrounding text and in the alt attribute. | Flux Academy | CLAIM(EDtgsIn1meM@02:35) | single-source | yes |
| 32 | Caption video, publish a transcript for audio, and warn before fast or flashing motion. | Flux Academy | CLAIM(EDtgsIn1meM@02:59), CLAIM(EDtgsIn1meM@02:40) | single-source | yes |
| 33 | Choose legible body type, keep it resizable by browser controls, and test the layout at enlarged text sizes. | Flux Academy | CLAIM(EDtgsIn1meM@03:34), CLAIM(EDtgsIn1meM@04:23) | single-source | yes |
| 34 | Test the whole site with the keyboard alone (tab, arrows, enter, escape) before calling it done. | Flux Academy, DesignCourse | CLAIM(EDtgsIn1meM@09:19), CLAIM(D29KL52Srtw@05:58) | consensus | yes |
| 35 | Run the design past multiple testers, including people with disabilities when budget allows; the designer is the worst judge of their own navigation. | Flux Academy | CLAIM(EDtgsIn1meM@12:04) | single-source | yes |
| 36 | For users with motor or vision impairment: maximize contrast, prefer sans-serif, use very large type and targets, and offer the fewest choices per screen. | DesignCourse | CLAIM(JavCEJ5hodc@03:42), CLAIM(JavCEJ5hodc@03:52), CLAIM(JavCEJ5hodc@03:07) | single-source | no |
| 37 | Hide caregiver or setup controls away from the main task flow when the primary user is easily distracted. | DesignCourse | CLAIM(JavCEJ5hodc@08:26) | single-source | no |

### Psychology and visual hierarchy

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 38 | Keep page structure predictable to the visitor mental model (logo top-left, nav nearby, footer at the bottom) and spend novelty inside that structure, on small pleasant surprises such as micro-interactions. | Self-Made Web Designer, DesignCourse | CLAIM(d-IaU9qcDGg@03:25), CLAIM(d-IaU9qcDGg@04:29), CLAIM(D29KL52Srtw@05:40) | consensus | yes |
| 39 | Make micro-interactions small: a gentle hover reaction or a slight scale on scroll works; motion big enough to startle pushes safety-seeking visitors away. | Self-Made Web Designer | CLAIM(d-IaU9qcDGg@04:47) | single-source | yes |
| 40 | Group reasons to buy in chunks of three or four; express pricing tiers as deltas (everything in the lower tier plus these items) rather than repeated full feature lists. | Self-Made Web Designer | CLAIM(d-IaU9qcDGg@07:25), CLAIM(d-IaU9qcDGg@07:25) | single-source | yes |
| 41 | Isolate the one element that must be remembered or clicked (the CTA, the recommended price) so it differs from its siblings in color, size, or outline, and keep that isolation to a single spot, since several strong outliers starve each other of attention. | Satori Graphics | CLAIM(-5jSCHZIHlg@00:36), CLAIM(-5jSCHZIHlg@02:06), | single-source | yes |
| 42 | Place related elements together (title, body, CTA in one block) and separate unrelated blocks with spacing, so grouping does the explaining. | Satori Graphics, DesignCourse | CLAIM(-5jSCHZIHlg@22:27), CLAIM(EKjCC4PwjFo@18:32) | consensus | yes |
| 43 | Group by similarity too: elements sharing color, shape, or size read as related even when they are spread across the layout. | Satori Graphics | CLAIM(-5jSCHZIHlg@21:08) | single-source | yes |
| 44 | Plan the eye path with lines and shape direction, and keep compositions balanced and orderly, because visible imbalance sends viewers hunting for the missing piece instead of reading the message. | Satori Graphics | CLAIM(-5jSCHZIHlg@17:51), CLAIM(-5jSCHZIHlg@20:04) | single-source | yes |
| 45 | Before choosing shapes, write down the feelings the design must convey, then match shapes to them (circle for community, square for strength, diagonal for motion, horizontal for calm). | Satori Graphics | CLAIM(-5jSCHZIHlg@09:41), CLAIM(-5jSCHZIHlg@08:25) | single-source | yes |
| 46 | Choose colors from brand keywords and audience data, check cultural meaning for the target market, and default to one or two brand colors unless every hue can be defended. | Satori Graphics | CLAIM(-5jSCHZIHlg@14:04), CLAIM(-5jSCHZIHlg@17:10), CLAIM(-5jSCHZIHlg@15:33) | single-source | yes |
| 47 | Pick a typeface whose personality matches the brand message; study the font character before placing it. | Satori Graphics | CLAIM(-5jSCHZIHlg@23:53), CLAIM(-5jSCHZIHlg@24:15) | single-source | yes |
| 48 | Break sector color convention only when the alternative still fits the industry; an outlier color wins recall inside a category of near-identical palettes. | Satori Graphics | CLAIM(-5jSCHZIHlg@04:20) | single-source | yes |

### Research, flows and process

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 49 | Start from evidence: run a short survey or interviews plus a competitor pass before drawing screens, and record the audience goals and pain points. | DesignSense | CLAIM(P2W2AnK5aDE@01:30), CLAIM(P2W2AnK5aDE@01:40) | single-source | no |
| 50 | Wireframe low-fidelity first (structure and flow only, simple shapes) and only then build high-fidelity screens with real color, type, and imagery. | DesignSense | CLAIM(P2W2AnK5aDE@03:48), CLAIM(P2W2AnK5aDE@04:27) | single-source | no |
| 51 | Define a style guide page (palette, type sizes, spacing, buttons, icons) before hi-fi work, and structure the file as named pages (brief, screens, style guide, components) so the source of any element is findable. | DesignSense | CLAIM(P2W2AnK5aDE@06:01), CLAIM(P2W2AnK5aDE@02:58) | single-source | no |
| 52 | A storyboard needs a specific scenario, sequenced visuals, and captions, kept to one persona and one path; stick figures are enough, so spend the effort on the story, not the drawing. | NNgroup | CLAIM(bNh54LNUtv8@00:06), CLAIM(bNh54LNUtv8@01:37), CLAIM(bNh54LNUtv8@01:04) | single-source | no |
| 53 | Run scenario mapping early with four to six people of different roles: write the scenario from five elements (persona, motivator, intent, action, resolution), break it into four to six steps, then brainstorm ideas, questions, and considerations on separate sticky-note colors with about ten minutes of silent work before discussion. | NNgroup | CLAIM(dmlFRCZI9gQ@00:36), CLAIM(dmlFRCZI9gQ@01:05), CLAIM(dmlFRCZI9gQ@01:23), CLAIM(dmlFRCZI9gQ@01:53), CLAIM(dmlFRCZI9gQ@01:09) | single-source | no |
| 54 | Prototype the flows before development and share the clickable file with the client and the developer; refine from what testers do with it. | DesignSense | CLAIM(P2W2AnK5aDE@13:53) | single-source | no |
| 55 | Keep testing after launch with a small user group plus analytics and reviews, and treat the feedback as a continuing loop rather than a one-time gate. | DesignSense | CLAIM(P2W2AnK5aDE@14:05) | single-source | no |
| 56 | Run five-minute informal usability sessions on personal projects: give the tester a task with no briefing, have them narrate their choices, log every dead end, fix it, and confirm the flow completes on a retest. | Mike Locke | CLAIM(9viTvO0Okoo@02:02), CLAIM(9viTvO0Okoo@02:24), CLAIM(9viTvO0Okoo@04:07), CLAIM(9viTvO0Okoo@04:47) | single-source | no |
| 57 | For data-heavy tables: order columns by importance left to right, keep headers and the identifier column pinned while scrolling, expand rows in place instead of covering the table with a modal, and replace machine codes with human-readable values. | NNgroup | CLAIM(23AQBZzDUIo@00:27), CLAIM(23AQBZzDUIo@01:13), CLAIM(23AQBZzDUIo@01:31), CLAIM(23AQBZzDUIo@01:52) | single-source | no |
| 58 | Match exported assets to the target platform (vector or raster per framework) and produce the store graphics (launcher icon at 1024px, listing shots) as part of handoff. | DesignSense | CLAIM(P2W2AnK5aDE@15:14), CLAIM(P2W2AnK5aDE@15:42) | single-source | no |
| 59 | Practice redesigns of shipped products as a skill drill: collect the public complaints first, then fix the named interaction problems in a mockup. | Flux Academy | CLAIM(TKZl_UlXhYk@00:18), CLAIM(TKZl_UlXhYk@00:36) | single-source | yes |
| 60 | Map the information architecture visually (color-coded shapes, connectors, a legend) and share the live file so the whole team works from one structure. | CharliMarieTV | CLAIM(HGsMNYq889U@02:56), CLAIM(HGsMNYq889U@03:47) | single-source | no |

## Looks like / does not (good vs bad pairs)

| # | looks like (good) | does not (bad) | why | citation |
|---|-------------------|----------------|-----|----------|
| 1 | Current nav item marked with color, weight, or a background | Every nav item identical with nothing showing where you are | Orientation costs less than guessing | CLAIM(D29KL52Srtw@00:40) |
| 2 | A labeled Home item in the nav | Logo as the only way back to home | Not every user knows the logo convention | CLAIM(D29KL52Srtw@01:12) |
| 3 | Secondary nav visibly lighter or smaller than primary nav | Primary and secondary items styled the same | Hierarchy tells the user which set matters | CLAIM(D29KL52Srtw@02:16) |
| 4 | Dropdown parents and their children at different weights | All menu items bold and equally strong | Equal emphasis hides the structure | CLAIM(D29KL52Srtw@02:39) |
| 5 | Hover state that highlights the link under the cursor | Links that do not react to the pointer | Confirmation prevents mis-clicks | CLAIM(D29KL52Srtw@03:07) |
| 6 | Logo left, nav right, footer at the bottom | Nav moved to the bottom or side for novelty | Visitors arrive with a learned blueprint; one site moved its menu to the thumb zone and had to revert | CLAIM(D29KL52Srtw@05:40), CLAIM(d-IaU9qcDGg@02:52) |
| 7 | Hamburger menu on a phone where links do not fit | Hamburger menu on a desktop with plenty of room | Every extra tap is extra work to reach key links | CLAIM(D29KL52Srtw@04:33) |
| 8 | Nav targets enlarged with space around them | Tiny nav items that fingers miss | Touch accuracy is a sizing problem | CLAIM(D29KL52Srtw@06:37) |
| 9 | Link text naming the destination | Generic call-to-click link text | Descriptive text works out of context and for screen readers | CLAIM(EDtgsIn1meM@07:45) |
| 10 | Alt text describing the actual product in the photo | Alt text naming the file or one bare word | Blind users get content, not a filename | CLAIM(EDtgsIn1meM@00:43) |
| 11 | Linked icon with function alt text (home, search) | Linked icon with alt text describing the drawing | The function is what the link does | CLAIM(EDtgsIn1meM@01:12) |
| 12 | Meaningful copy as real page text | Long text baked into an image | Image text is invisible to screen readers and translation | CLAIM(EDtgsIn1meM@02:35) |
| 13 | Text at 4.5:1 contrast or better, checked with a tool | Text at a ratio in the high 3s, judged by eye | Low contrast fails low-vision users and looks accidental | CLAIM(D29KL52Srtw@03:40) |
| 14 | Empty-result message with the offending filters removable in place | Error text explaining the problem with instructions only | The fix should be one click from the message | CLAIM(cCun-ReLTFI@01:14) |
| 15 | Sent-message confirmation with an undo option | Send with no way back | Prevention beats recovery, recovery beats nothing | CLAIM(cCun-ReLTFI@01:34) |
| 16 | Error message under the field it belongs to | Error summary near the submit button | Proximity ties the message to the input | CLAIM(EKjCC4PwjFo@06:15) |
| 17 | Field with a visible border against the page | Field fill barely distinguishable from the background | If you cannot see where to type, you will not type | CLAIM(EKjCC4PwjFo@03:12) |
| 18 | Error copy naming the broken rule | One generic sentence for every failure | Specifics tell the user what to change | CLAIM(5-caRWzSQd4@08:36) |
| 19 | Persistent label above the field | Placeholder-only field that empties on focus | The label must survive typing | CLAIM(5-caRWzSQd4@04:02) |
| 20 | Field labeled First name | Field labeled Name | Ambiguous labels produce ambiguous data | CLAIM(5-caRWzSQd4@04:12) |
| 21 | Submit button in the theme's primary color, strongest element on the form | Submit styled like every other button | The click is the conversion; it must be findable | CLAIM(5-caRWzSQd4@21:40) |
| 22 | Button hover that only lightens the fill | Hover that flips the whole button to a new color and text | Large state jumps read as errors | CLAIM(5-caRWzSQd4@23:13) |
| 23 | Checkboxes, selects, and fields sharing one stroke and fill language | A form where each control has its own styling | Inconsistency reads as a different, weaker control | CLAIM(5-caRWzSQd4@24:05) |
| 24 | Pricing compared as tier deltas in a few groups | Every tier repeating the full feature list in rows | Working memory drops half the list before the page ends | CLAIM(d-IaU9qcDGg@07:25) |
| 25 | Predictable layout with one or two tasteful micro-interactions | Either total sameness everywhere, or big animated surprises | The safety-seeking visitor and the novelty-seeking visitor both need serving | CLAIM(d-IaU9qcDGg@04:29), CLAIM(d-IaU9qcDGg@04:47) |
| 26 | Title, body, and CTA grouped in one block with clear gaps between blocks | Related items scattered with equal spacing everywhere | Proximity is read as relationship | CLAIM(-5jSCHZIHlg@22:27) |
| 27 | Two or three large yes/no targets for an impaired user | Fifty small options crammed on one screen | Shaky hands and low vision punish dense screens | CLAIM(JavCEJ5hodc@03:07) |
| 28 | Table row expanding in place, headers and identifier column pinned | Modal covering the table while you inspect one row | Context must stay visible when comparing rows | CLAIM(23AQBZzDUIo@01:13), CLAIM(23AQBZzDUIo@01:31) |
| 29 | Human-readable values in table cells | Raw generated IDs and codes in the table | Decoding codes is unpaid work for the user | CLAIM(23AQBZzDUIo@01:52) |
| 30 | Form constrained to a column with equal side margins | Fields stretched edge to edge across the screen | Wide fields destroy scanning and line length | CLAIM(EKjCC4PwjFo@21:30) |

## Decision tables (option A vs B -> pick when)

### Where to innovate

| Choice A | Choice B | Pick when |
|----------|----------|-----------|
| Follow the standard placement (logo left, nav right, footer bottom) | Deviate for concept or brand reasons | A for any task-driven or client site; B only with a testable reason and a usability check, because the visitor's mental model punishes novelty in structure (CLAIM(D29KL52Srtw@05:40), CLAIM(d-IaU9qcDGg@02:52)) |
| Total predictability everywhere | Small pattern breaks inside a predictable frame | The frame is settled and the delight lives in micro-interactions; drastic motion drives away the safety-first visitor (CLAIM(d-IaU9qcDGg@04:29), CLAIM(d-IaU9qcDGg@04:47)) |
| Hamburger menu | Inline links | Links fit the viewport: inline. Space runs out: collapse (CLAIM(D29KL52Srtw@04:33)) |

### Form error handling

| Choice A | Choice B | Pick when |
|----------|----------|-----------|
| Inline message under the field | Summary message near submit | Inline for field-level problems; a summary only as a supplement (CLAIM(EKjCC4PwjFo@06:15)) |
| Explain the rule in text | One-click fix in the message | Prefer the click-able fix; keep the explanation when no shortcut is possible (CLAIM(cCun-ReLTFI@01:06)) |
| Block the invalid submit | Allow and offer undo | Block when data quality matters; allow plus undo when the action is cheap to reverse (CLAIM(cCun-ReLTFI@01:34)) |

### Color and emphasis

| Choice A | Choice B | Pick when |
|----------|----------|-----------|
| One brand color plus neutrals | Multiple brand colors | Beginners and most projects: one or two. Multi-color only with a designer who can defend every hue (CLAIM(-5jSCHZIHlg@15:33)) |
| Match the sector's palette | Break the sector palette | Break it only when the new color still fits the industry and the category is a sea of the same hue (CLAIM(-5jSCHZIHlg@04:20)) |
| One strong isolated CTA | Several equally strong elements | Isolate when a single action matters; several strong spots cancel each other (CLAIM(-5jSCHZIHlg@00:36), ) |

### Research artifact choice

| Choice A | Choice B | Pick when |
|----------|----------|-----------|
| Stick-figure storyboard | Polished illustrated storyboard | Low-fi for ideation and feedback; polished only for a client deliverable or a wide audience (CLAIM(bNh54LNUtv8@01:37)) |
| Scenario mapping workshop | Solo flow sketch | Cross-role uncertainty: workshop with four to six people early in the project (CLAIM(dmlFRCZI9gQ@00:36), CLAIM(dmlFRCZI9gQ@02:36)) |
| Five-minute family usability pass | Formal recruited test | Personal projects and portfolio work: the five-minute pass; funded client work: recruit testers including people with disabilities (CLAIM(9viTvO0Okoo@02:02), CLAIM(EDtgsIn1meM@12:04)) |

## Anti-patterns (cited)

- Generic link text on buttons and inline links: describe the destination instead (CLAIM(EDtgsIn1meM@07:45)).
- Text baked into images where the words matter (CLAIM(EDtgsIn1meM@02:35)).
- Instructions that rely on color or shape alone (CLAIM(EDtgsIn1meM@08:26)).
- Nav with no active state and no Home item (CLAIM(D29KL52Srtw@00:40), CLAIM(D29KL52Srtw@01:12)).
- Hamburger menu used on a roomy desktop layout (CLAIM(D29KL52Srtw@04:33)).
- Nav placed at the bottom or the side for the sake of being original (CLAIM(D29KL52Srtw@05:40)).
- Text fields that are barely visible against the page (CLAIM(EKjCC4PwjFo@03:28)).
- Placeholder used as the only label (CLAIM(5-caRWzSQd4@04:02)).
- Vague error copy that never names the failed rule (CLAIM(5-caRWzSQd4@08:36)).
- Error text parked next to the submit button (CLAIM(EKjCC4PwjFo@06:15)).
- Mixed aesthetics between fields, checkboxes, and selects in one form (CLAIM(5-caRWzSQd4@24:05)).
- Over-large hover or state changes that swap colors wholesale (CLAIM(5-caRWzSQd4@23:13)).
- Fifty small options on one screen for users with impaired motor control (CLAIM(JavCEJ5hodc@03:07)).
- Modal overlays that hide the table row being inspected (CLAIM(23AQBZzDUIo@01:31)).
- Raw database codes and generated IDs shown to users (CLAIM(23AQBZzDUIo@01:52)).
- Full-screen-width text inputs (CLAIM(EKjCC4PwjFo@21:30)).
- Isolation effect applied to several competing spots at once (CLAIM(-5jSCHZIHlg@05:02)).
- Many-color logo without a rationale (the rebrand example named overuse of color as a flaw) (CLAIM(-5jSCHZIHlg@16:16)).
- Feature sprawl and unclear iconography in an app until users cannot find core functions (CLAIM(TKZl_UlXhYk@00:36), CLAIM(TKZl_UlXhYk@00:21)).

## Creator claims (unverified)

- Roughly a billion bits of sensory information per second with only about ten reaching awareness (CLAIM(d-IaU9qcDGg@00:50)).
- Working memory holds about three or four items at once (CLAIM(d-IaU9qcDGg@06:13)).
- Knowing this psychology makes a designer worth a five-figure fee on a project (CLAIM(d-IaU9qcDGg@07:38)).
- Studies reportedly show navigation is easier when a separate Home button exists (CLAIM(D29KL52Srtw@01:17)).
- A 2015 study of top brands reportedly found circles as the main shape in about twenty of fifty logos (CLAIM(-5jSCHZIHlg@06:33)).
- Reported audience data: a large majority of a chocolate brand's social audience was female, which its purple branding targets (CLAIM(-5jSCHZIHlg@14:15)).
- Viewer attention spans can be only a few seconds (CLAIM(-5jSCHZIHlg@05:18)).
- The chat app under redesign was reportedly made confusing on purpose to reward its teenage audience (CLAIM(TKZl_UlXhYk@01:42)).

## Tool-specific (dated)

- Sketch 49 (2018) added native prototyping: hotspots, per-object links, transition direction, and a starting-point artboard (CLAIM(470go6su3Ys@02:33), CLAIM(470go6su3Ys@01:52)).
- Figma component variants (2022 and 2024 workflows) carry form states as variant properties wired with on-tap change-to interactions; instant for state swaps, smart animate around 300ms when something physically moves (CLAIM(5-caRWzSQd4@20:12), CLAIM(5-caRWzSQd4@20:12), CLAIM(EKjCC4PwjFo@08:57)).
- FigJam (2022) supplies a brainstorming toolkit distinct from Figma: stickers with authorship, sections that move as a group, stamp voting, cursor chat, and in-file audio (CLAIM(HGsMNYq889U@04:28), CLAIM(HGsMNYq889U@04:43), CLAIM(HGsMNYq889U@05:58), CLAIM(HGsMNYq889U@06:58)).
- Contrast checking via the Stark plugin for Figma and XD, plus browser devtools accessibility panels (2021) (CLAIM(D29KL52Srtw@03:59)).
- Iconify plugin (2022, 2024) for pulling icons and checkmarks into Figma designs (CLAIM(5-caRWzSQd4@09:45), CLAIM(EKjCC4PwjFo@20:42)).
- Recraft AI (2024) for themed raster and vector imagery that matches the app palette (CLAIM(P2W2AnK5aDE@07:37)).
- Showit cited (2026) as a drag-and-drop builder where size changes do not break the layout (CLAIM(d-IaU9qcDGg@05:15)).

## Disagreements between creators (who says what, cited)

- How far to push originality: DesignCourse tells designers not to be original with nav and logo placement (CLAIM(D29KL52Srtw@05:40)), while Satori Graphics pushes breaking the sector's color convention to stand out (CLAIM(-5jSCHZIHlg@04:20)). Reading: structure stays conventional, brand color may break convention; the two rules operate on different layers.
- Hover intensity: DesignCourse's nav lesson allows bold, underline, icon, or border changes on hover (CLAIM(D29KL52Srtw@03:07)), while its forms lesson insists button hover stay a subtle lightening (CLAIM(5-caRWzSQd4@23:13)). Reading: link hover may add emphasis; a filled button should barely move.
- Testing protocol: Mike Locke has the tester narrate their intended taps rather than perform them (CLAIM(9viTvO0Okoo@03:05)), while DesignSense has users try the shipped app and report what happened (CLAIM(P2W2AnK5aDE@14:10)). Reading: narrated intent is fast and cheap for a personal project; observed use plus feedback is the stronger evidence when the product is real.
- Delight versus safety: Self-Made Web Designer warns that an all-safe design bores the visitor and prescribes small surprises (CLAIM(d-IaU9qcDGg@04:29)), while Satori Graphics warns that any strong contrast point drains attention from the rest of the design (CLAIM(-5jSCHZIHlg@05:02)). Reading: micro-interactions and single-point emphasis are compatible if only one element is isolated and the delight stays small.

## Suggested sub-skills

- navigation-wayfinding: nav structure, states, placement, and keyboard paths. Owns laws 1-12.
- form-input-design: field anatomy, states, error handling, and CTA emphasis. Owns laws 13-28.
- accessibility-audit: contrast, alt text, media alternatives, keyboard, and assistive-user tuning. Owns laws 29-37.
- psychology-visual-hierarchy: mental models, chunking, isolation, Gestalt grouping, color and type personality. Owns laws 38-48.
- research-flows-process: research, wireframe fidelity, storyboards, scenario mapping, usability passes, table design, handoff. Owns laws 49-60.
