# Build & ship laws (Design Studio OS corpus)

Coverage: 14 videos read so far (P5H7zs0RsUM, xHXqj006Q2k, WLDfFqnqbxI, BNYLKuIlazA, FGIPeIql9d4, y4Rv-vf01LY, 63USLByBGNM, 1xAfVDiX1ps, MGvGiu6WjYk, c6AGaxigBAY, KZGLz0Glafo, 2YBCdCZkT5Q, dCJ3LYF3wFA, mititlWcEco). Channels: Flux Academy (6), Jesse Showalter (5), Sam Crawford (2), Satori Graphics (1). Date range 2020-04-04 to 2026-01-08. Top-10 channels present: flux-academy, jesse-showalter, sam-crawford, satori-graphics.

## Laws

### Design-to-build handoff (structure that survives the copy)

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 1 | Before touching the builder, read the design and write down the structure it implies: how many top-level groups, what grid it sits on, which elements must resize and which stay fixed. | Flux Academy | CLAIM(WLDfFqnqbxI@00:30, WLDfFqnqbxI@00:50) | single-source | yes |
| 2 | Name every frame by its role (hero, container, nav, button) before exporting; the names become class names in the builder, and a well named file is a reusable style guide on arrival. | Flux Academy | CLAIM(xHXqj006Q2k@05:03, xHXqj006Q2k@05:12, P5H7zs0RsUM@05:51, KZGLz0Glafo@09:39, KZGLz0Glafo@12:07, KZGLz0Glafo@25:14) | consensus | yes |
| 3 | Build the Figma file with auto layout on every container, nested the way the page is nested (page frame, navbar, section, container, columns). A design made of unlogical groups cannot be transferred. | Flux Academy | CLAIM(xHXqj006Q2k@01:34, xHXqj006Q2k@01:47, xHXqj006Q2k@02:23) | single-source | yes |
| 4 | Set the design container to a fixed max width (1200px was used) so it lands as the builder's container width instead of a hard-coded 1440 wrapper that must be deleted after pasting. | Flux Academy | CLAIM(xHXqj006Q2k@02:05, xHXqj006Q2k@00:26) | single-source | yes |
| 5 | Load the fonts into the builder project's settings before copying anything over, otherwise pasted text falls back and the type has to be re-set element by element. | Flux Academy | CLAIM(xHXqj006Q2k@04:32, xHXqj006Q2k@04:49) | single-source | yes |
| 6 | Auto layout in the design tool and flex in the builder are the same model: same properties, same job of telling the renderer how to place children. Learn the mapping once and use it in both. | Flux Academy | CLAIM(xHXqj006Q2k@01:10, P5H7zs0RsUM@04:30) | consensus | yes |
| 7 | Importing a design with one click is fine for speed, but build the first version by hand so you can fix anything the import produces badly. | Flux Academy | CLAIM(P5H7zs0RsUM@00:25, P5H7zs0RsUM@00:33) | single-source | yes |
| 8 | Check fill and hug settings on every frame before an import: the design tool's fill/hug choices become the builder's flex sizing, and a wrong one silently breaks the layout. | Flux Academy | CLAIM(xHXqj006Q2k@07:59, xHXqj006Q2k@08:14) | single-source | yes |
| 8a | Pull the design file's type styles, color styles and export-ready assets onto one side board and export them (logos as SVG) before opening the builder, so tokens and files are ready instead of hunted for mid-build. | Jesse Showalter | CLAIM(1xAfVDiX1ps@01:16, 1xAfVDiX1ps@01:29, 1xAfVDiX1ps@01:37) | single-source | yes |
| 8b | Do not prototype hovers and interactions in the design file; build them once in the host tool, where an approved build is also the shipped build. | Jesse Showalter | CLAIM(1xAfVDiX1ps@00:54, 1xAfVDiX1ps@01:02) | single-source | yes |
| 8c | Load every token from the design into the builder as named site styles before laying out anything, then apply styles rather than raw values from the first section onward. | Jesse Showalter | CLAIM(1xAfVDiX1ps@02:09, 1xAfVDiX1ps@02:57, 1xAfVDiX1ps@03:12) | single-source | yes |
| 8d | Build the type scale as styles with named slots (three headings plus small, medium and large body) and order the style panel so the scale reads in sequence. | Jesse Showalter | CLAIM(1xAfVDiX1ps@05:00, 1xAfVDiX1ps@05:38, 1xAfVDiX1ps@06:33) | single-source | yes |
| 8e | If the reference face is not available, load a close substitute and set it before styling, instead of leaving the builder default. | Flux Academy | CLAIM(KZGLz0Glafo@02:24, KZGLz0Glafo@02:29) | single-source | yes |

### Layout construction in the builder

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 9 | Define shared colors as named styles at the start of the build, before placing elements, so reuse costs one click instead of a re-picked hex. | Flux Academy, Satori Graphics | CLAIM(P5H7zs0RsUM@00:46, P5H7zs0RsUM@01:00, mititlWcEco@00:24, mititlWcEco@00:35, mititlWcEco@00:48) | consensus | yes |
| 10 | Take the platform's own navigation component instead of drawing one; it arrives with the mobile collapse already handled. | Flux Academy | CLAIM(P5H7zs0RsUM@01:08, P5H7zs0RsUM@01:19) | single-source | yes |
| 11 | A web layout is never free-positioned: every element lives inside a stack (or wrapper) whose alignment controls it, so nothing can be dragged off its line. | Flux Academy | CLAIM(P5H7zs0RsUM@07:37, P5H7zs0RsUM@07:50, KZGLz0Glafo@05:06, KZGLz0Glafo@05:12) | single-source | yes |
| 12 | Give full-bleed sections 100 percent width (or 100 viewport height for a one-screen hero) and keep the content inside a centered container so the page scales and the copy stays on a readable measure. | Flux Academy | CLAIM(P5H7zs0RsUM@06:16, BNYLKuIlazA@00:16, BNYLKuIlazA@01:47) | consensus | yes |
| 13 | Split a single-screen composition into separate top-level groups (nav, text block, card area) rather than one giant grid, so each part can be restacked at tablet and mobile without breaking the others. | Flux Academy | CLAIM(WLDfFqnqbxI@01:20, WLDfFqnqbxI@14:47) | single-source | yes |
| 14 | Define one grid class (column count plus gap) and reapply it to every group that shares the grid; use a combo class when a single group needs a local override. | Flux Academy | CLAIM(WLDfFqnqbxI@03:30, WLDfFqnqbxI@04:40) | single-source | yes |
| 15 | Wrap a section's children in a vertical flex parent when you need controlled gaps and one child that grows to fill the remaining height. | Flux Academy | CLAIM(WLDfFqnqbxI@04:21, WLDfFqnqbxI@04:34) | single-source | yes |
| 16 | Pull an element out of normal grid flow with absolute positioning when it is decoration rather than content (a 3D or image backdrop), and size it to 100 percent of its frame so it stays behind the copy. | Flux Academy | CLAIM(BNYLKuIlazA@05:58, BNYLKuIlazA@06:14, KZGLz0Glafo@09:27, KZGLz0Glafo@13:28) | single-source | yes |
| 17 | Set any image that could exceed its cell to fill its box and clip the parent with overflow hidden, otherwise one oversized asset pushes the next row below the fold. | Flux Academy | CLAIM(WLDfFqnqbxI@10:01, WLDfFqnqbxI@11:49) | single-source | yes |
| 18 | Use space-between on a card's vertical flex to pin one element to the top and one to the bottom instead of hard-coding margins. | Flux Academy | CLAIM(WLDfFqnqbxI@13:04, WLDfFqnqbxI@13:18) | single-source | yes |
| 19 | Size a display headline in viewport units (13 viewport width was used) when it must scale with the screen, then set line height from the text and cap its width. | Flux Academy | CLAIM(WLDfFqnqbxI@06:47, WLDfFqnqbxI@07:23, WLDfFqnqbxI@07:50) | single-source | yes |
| 20 | Align to type baselines, not to bounding boxes: when a bottom-aligned block lands visually short, nudge its margin until the baselines read level. | Flux Academy | CLAIM(WLDfFqnqbxI@08:25, WLDfFqnqbxI@08:52) | single-source | yes |
| 21 | Cap text width (max width or a percentage of the parent) on every long block so a wide viewport cannot stretch a paragraph into one unbroken line. | Flux Academy | CLAIM(P5H7zs0RsUM@14:48, WLDfFqnqbxI@08:47) | consensus | yes |
| 21a | Give the page one containing element at 100 percent width with a max width (1200 was used) and let children fill it: responsive growth needs a documented stop. | Jesse Showalter | CLAIM(1xAfVDiX1ps@18:56, 1xAfVDiX1ps@19:06) | single-source | yes |
| 21b | Keep the page artboard width fixed (it defines the breakpoints) and its height fit-content, or added content is pushed off a canvas that stops growing. | Jesse Showalter, Flux Academy | CLAIM(1xAfVDiX1ps@20:52, 1xAfVDiX1ps@21:11, KZGLz0Glafo@05:24, KZGLz0Glafo@05:29) | consensus | yes |
| 21c | Set a horizontal group to fill its parent when logo and call-to-action must sit at opposite ends. | Jesse Showalter | CLAIM(1xAfVDiX1ps@12:08, 1xAfVDiX1ps@12:20) | single-source | yes |
| 21d | Add side padding on a nav or wrapper (24 left and right, 12 top and bottom was used) so content never touches the browser edge. | Jesse Showalter | CLAIM(1xAfVDiX1ps@08:26, 1xAfVDiX1ps@08:42) | single-source | yes |
| 21e | Lay the content in first and group it afterwards: drop the copy, buttons and images, then collect them into stacks and named sections that stack cleanly. | Jesse Showalter | CLAIM(1xAfVDiX1ps@13:21, 1xAfVDiX1ps@13:41) | single-source | yes |
| 21f | Wrap a bare image in its own stack when it needs surrounding space; an image on its own cannot take the padding. | Jesse Showalter | CLAIM(1xAfVDiX1ps@24:07, 1xAfVDiX1ps@24:20) | single-source | yes |
| 21g | Reuse the container element (copy it, clear it, refill it) for the next section so the left and right edges of the page stay on one line. | Jesse Showalter | CLAIM(1xAfVDiX1ps@23:13, 1xAfVDiX1ps@23:38) | single-source | yes |
| 21h | When a decorative background is cut off by its parent, that is the container's overflow setting, not the image's size: switch it to visible. | Jesse Showalter | CLAIM(1xAfVDiX1ps@25:07, 1xAfVDiX1ps@25:17) | single-source | yes |
| 21i | Push a decorative layer behind content with a negative z-index rather than reordering the layer list, and lock it once placed. | Jesse Showalter, Flux Academy | CLAIM(1xAfVDiX1ps@22:04, 1xAfVDiX1ps@22:23, 1xAfVDiX1ps@30:06, KZGLz0Glafo@09:44, KZGLz0Glafo@29:47, KZGLz0Glafo@33:45) | consensus | yes |
| 21j | Add breakpoints before the layout visibly breaks, and work from the largest breakpoint down: a change made on a smaller artboard applies to that size and every size below it, never above. | Jesse Showalter, Flux Academy | CLAIM(1xAfVDiX1ps@25:49, 1xAfVDiX1ps@26:00, 1xAfVDiX1ps@26:34, KZGLz0Glafo@04:54, KZGLz0Glafo@04:57) | consensus | yes |
| 21k | Set a type style's size once per breakpoint inside the style itself (64, 54, 38 was used) and reduce line height with it, instead of overriding headings one by one. | Jesse Showalter | CLAIM(1xAfVDiX1ps@28:37, 1xAfVDiX1ps@28:56, 1xAfVDiX1ps@29:26) | single-source | yes |
| 21l | On narrow layouts, switch a button row to vertical and set both the buttons and their group to fill so they become edge-to-edge tap targets. | Jesse Showalter | CLAIM(1xAfVDiX1ps@30:13, 1xAfVDiX1ps@30:26) | single-source | yes |
| 21m | Inspect the live reference and record measured widths, padding, type size, and image ratio before placing the first frame. | Flux Academy | CLAIM(KZGLz0Glafo@00:37, KZGLz0Glafo@01:06, KZGLz0Glafo@03:40) | single-source | yes |
| 21n | Derive the content max width from the reference canvas minus its side padding, and set that max on the content wrapper (1440 with 64 side padding landed at 1312). | Flux Academy | CLAIM(KZGLz0Glafo@01:26, KZGLz0Glafo@01:34, KZGLz0Glafo@15:36) | single-source | yes |
| 21o | A hero that must keep the photo's ratio is an aspect-ratio frame, not a viewport-height frame; change both the ratio and the image at the phone breakpoint. | Flux Academy | CLAIM(KZGLz0Glafo@03:37, KZGLz0Glafo@03:52, KZGLz0Glafo@04:06) | single-source | yes |
| 21p | To pin copy to the bottom of a tall hero, wrap it in a stack, set that stack sticky with a bottom offset equal to the padding, and set every parent overflow to visible. | Flux Academy | CLAIM(KZGLz0Glafo@07:18, KZGLz0Glafo@07:33, KZGLz0Glafo@07:52) | single-source | yes |
| 21q | A bar that must stay over the hero is fixed to the top of the page, not nested inside the hero, and its width goes back to 100 percent after the position change. | Flux Academy | CLAIM(KZGLz0Glafo@23:34, KZGLz0Glafo@23:39, KZGLz0Glafo@23:55) | single-source | yes |
| 21r | Center a logo between two side groups by setting both groups to fill and aligning one to the start and one to the end; space-between breaks when one child is fit and the other is fill. | Flux Academy | CLAIM(KZGLz0Glafo@21:54, KZGLz0Glafo@22:02, KZGLz0Glafo@24:36) | single-source | yes |
| 21s | Size an icon smaller than its hit box (16 inside 24 was measured) and match the gap to that box, so the target and the space beside it are the same. | Flux Academy | CLAIM(KZGLz0Glafo@01:47, KZGLz0Glafo@01:56, KZGLz0Glafo@02:01) | single-source | yes |

### Components, variants and tokens

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 22 | Anything reused twice (button, nav, footer, card) becomes a component the moment it is styled; edit the master and every instance follows. | Flux Academy, Satori Graphics | CLAIM(P5H7zs0RsUM@16:35, P5H7zs0RsUM@01:43, BNYLKuIlazA@03:43, KZGLz0Glafo@08:16, KZGLz0Glafo@08:18, mititlWcEco@01:46, mititlWcEco@02:12, mititlWcEco@02:19) | consensus | yes |
| 23 | Put state differences into variants on the same component (main, hover) rather than into a second copy, so the styles cannot drift apart. | Flux Academy | CLAIM(P5H7zs0RsUM@18:14, P5H7zs0RsUM@18:20) | single-source | yes |
| 24 | A press-feel hover is built by changing the fill and collapsing the shadow offset to zero in the hover variant. | Flux Academy | CLAIM(P5H7zs0RsUM@18:23, P5H7zs0RsUM@18:35) | single-source | yes |
| 25 | A hard-edged shadow is zero blur with a small spread and a small offset; blur is what makes a shadow look soft and generic. | Flux Academy | CLAIM(P5H7zs0RsUM@17:52, P5H7zs0RsUM@18:03) | single-source | yes |
| 26 | Build a button as a hug-sized frame with text inside, more horizontal than vertical padding and a small radius, then componentize it. | Flux Academy | CLAIM(BNYLKuIlazA@02:36, BNYLKuIlazA@03:02, BNYLKuIlazA@03:13) | single-source | yes |
| 27 | Any value repeated in two or more places (corner radius, color) becomes a variable so a later change lands everywhere at once. | Flux Academy | CLAIM(WLDfFqnqbxI@11:09, WLDfFqnqbxI@11:20) | single-source | yes |
| 28 | Reuse the project's predefined heading and paragraph styles instead of hand-setting each text block; only genuinely one-off display type gets its own class. | Flux Academy | CLAIM(P5H7zs0RsUM@14:15, WLDfFqnqbxI@07:10) | consensus | yes |
| 29 | Set the base type once on the body/all-pages class and let it cascade to everything below. | Flux Academy | CLAIM(WLDfFqnqbxI@02:25, WLDfFqnqbxI@02:33) | single-source | yes |
| 29a | Name the layer before converting it to a component: the component inherits the layer name, and an unnamed component is unfindable later. | Jesse Showalter, Satori Graphics | CLAIM(1xAfVDiX1ps@10:39, 1xAfVDiX1ps@10:50, mititlWcEco@02:12) | consensus | yes |
| 29b | Create the variants and states a component will need at creation time (a second style plus hover), not after ten instances exist. | Jesse Showalter | CLAIM(1xAfVDiX1ps@10:56, 1xAfVDiX1ps@11:51) | single-source | yes |
| 29c | Expose the editable text of a component as a variable with a default value so each instance can carry its own label without leaving the master. | Jesse Showalter, Flux Academy | CLAIM(1xAfVDiX1ps@17:54, 1xAfVDiX1ps@18:06, KZGLz0Glafo@10:50, KZGLz0Glafo@11:08) | consensus | yes |
| 29d | Nest components (a button inside a nav) rather than duplicating the button markup into the nav. | Jesse Showalter | CLAIM(1xAfVDiX1ps@11:57, y4Rv-vf01LY@04:26) | consensus | yes |
| 29e | Brand a supplied component by pointing its parts at the project's color styles, and set every state (default, hover, pressed, disabled) while you are there. | Jesse Showalter, Flux Academy | CLAIM(FGIPeIql9d4@01:30, FGIPeIql9d4@01:40, P5H7zs0RsUM@18:14) | consensus | yes |
| 29f | Build small repeated parts (chip, tag, button) from a fit-content stack with more horizontal than vertical padding and a full radius, then componentize on the spot when a second use is likely. | Jesse Showalter | CLAIM(1xAfVDiX1ps@15:45, 1xAfVDiX1ps@16:10, 1xAfVDiX1ps@16:39) | single-source | yes |
| 29g | Start a hard part (navigation) from a pre-built component and restyle it instead of building it from scratch; it arrives with the mobile collapse already wired. | Jesse Showalter, Flux Academy | CLAIM(1xAfVDiX1ps@07:02, 1xAfVDiX1ps@07:09, P5H7zs0RsUM@01:19) | consensus | yes |
| 29h | Where a template is the starting point, restyle its colors and text styles from the assets panel first; that is what turns a stock layout into a client-unique site. | Jesse Showalter | CLAIM(y4Rv-vf01LY@10:26, y4Rv-vf01LY@10:56) | single-source | yes |
| 29i | Rebuild a repeated card from stacks so its padding, internal gaps and radius are all container properties, never manual positions. | Jesse Showalter | CLAIM(y4Rv-vf01LY@01:56, y4Rv-vf01LY@02:41, y4Rv-vf01LY@02:53) | single-source | yes |
| 29j | When the host has no native control for the button the design needs (a second header action, or a summary read-more that should look like a button), restyle the existing element with scoped CSS instead of adding a second header or swapping the block. | Sam Crawford | CLAIM(MGvGiu6WjYk@00:25, c6AGaxigBAY@00:13) | single-source | yes |
| 29k | Read the live class in the inspector before writing a selector; do not invent the header item's name. | Sam Crawford | CLAIM(MGvGiu6WjYk@00:33, MGvGiu6WjYk@00:51) | single-source | yes |
| 29l | Scope the override to the exact nodes (nth-child of the last two nav items, or the block then item then link chain) so the rest of the site's links stay untouched. | Sam Crawford | CLAIM(MGvGiu6WjYk@01:11, MGvGiu6WjYk@01:15, c6AGaxigBAY@01:11) | single-source | yes |
| 29m | After you border the buttonized nav items, add side padding on those items only, and give every nav item the same vertical padding so the row does not look uneven. | Sam Crawford | CLAIM(MGvGiu6WjYk@01:37, MGvGiu6WjYk@01:49, MGvGiu6WjYk@02:06) | single-source | yes |
| 29n | Set a filled button's label color on the anchor inside the item, not on the item, or the text keeps the old color. | Sam Crawford | CLAIM(MGvGiu6WjYk@02:40, MGvGiu6WjYk@02:53) | single-source | yes |
| 29o | Size a CSS button with padding, and set an explicit width when the link box already spans the card (about 60 percent was kept; 100 percent fills the whole item). | Sam Crawford | CLAIM(c6AGaxigBAY@01:30, c6AGaxigBAY@01:49, c6AGaxigBAY@02:09) | single-source | yes |
| 29p | Center the label and keep a top margin so the button does not sit on the body copy (about 30 was kept; zero was rejected). | Sam Crawford | CLAIM(c6AGaxigBAY@02:23, c6AGaxigBAY@02:39, c6AGaxigBAY@02:44) | single-source | yes |
| 29q | Put the same short transition on the resting rule and the hover rule (0.2 to 0.3 seconds was the working range; instant and multi-second both fail). | Sam Crawford | CLAIM(MGvGiu6WjYk@03:20, c6AGaxigBAY@03:08, c6AGaxigBAY@03:22) | single-source | yes |
| 29r | On a filled hover, change the label color with the background, or the text vanishes into the fill. Make each button's hover the inverse of its own resting state. | Sam Crawford | CLAIM(c6AGaxigBAY@05:05, c6AGaxigBAY@05:10, MGvGiu6WjYk@04:43) | single-source | yes |
| 29s | A font-family name in custom CSS only resolves if that face is already loaded on the site. | Sam Crawford | CLAIM(c6AGaxigBAY@03:27, c6AGaxigBAY@03:48) | single-source | yes |
| 29t | Do not start with !important; keep it for the case where another rule on the same element will not yield. | Sam Crawford | CLAIM(c6AGaxigBAY@05:18, c6AGaxigBAY@05:31) | single-source | yes |
| 29u | Save the custom CSS panel and confirm the edit stuck before you leave it. | Sam Crawford | CLAIM(c6AGaxigBAY@05:46, c6AGaxigBAY@05:48) | single-source | yes |
| 29v | A hover that should scale only the fill is an absolute background frame at full width, under the label, not a background on the component. | Flux Academy | CLAIM(KZGLz0Glafo@09:07, KZGLz0Glafo@09:27, KZGLz0Glafo@09:44) | single-source | yes |
| 29w | Read the hover scale off the live control (0.95 and 0.9 were both present) instead of inventing one. | Flux Academy | CLAIM(KZGLz0Glafo@10:09, KZGLz0Glafo@10:22) | single-source | yes |
| 29x | Variants cannot change which parent a layer sits in; to reposition a logo between variants, set it absolute so each variant can move it without re-nesting. | Flux Academy | CLAIM(KZGLz0Glafo@28:00, KZGLz0Glafo@28:11, KZGLz0Glafo@28:21) | single-source | yes |
| 29y | Wrap an SVG in a ratio-locked frame and scale the frame, not the SVG, or the mark breaks the bar. | Flux Academy | CLAIM(KZGLz0Glafo@25:48, KZGLz0Glafo@26:00, KZGLz0Glafo@26:15) | single-source | yes |

### Motion and effects while building

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 30 | Reveal hero text by line rather than by letter; line-level entrance stays readable, letter-level looks like a typewriter. | Flux Academy | CLAIM(P5H7zs0RsUM@07:18, P5H7zs0RsUM@09:27) | single-source | yes |
| 31 | Sequence entrance effects: delay the secondary element (the hero image) by around half a second so the text lands first and the load reads as one motion. | Flux Academy | CLAIM(P5H7zs0RsUM@11:11, P5H7zs0RsUM@11:34) | single-source | yes |
| 32 | When a headline animates and resizes on the same element, keep the animation and the responsive size as two separate settings and test the preview at more than one width before accepting it. | Flux Academy | CLAIM(P5H7zs0RsUM@06:38, WLDfFqnqbxI@07:31) | consensus | yes |
| 32a | Author an entrance animation as an off-state plus a destination (start at zero opacity, travel about 20px, half a second), then copy the effect and only change the delay to stagger a group. | Jesse Showalter, Flux Academy | CLAIM(1xAfVDiX1ps@31:16, 1xAfVDiX1ps@31:38, 1xAfVDiX1ps@32:16, KZGLz0Glafo@17:54, KZGLz0Glafo@18:01) | consensus | yes |
| 32b | Keep a scroll effect small on one hero asset: a few pixels of translate or scale, not an opacity change, or the page reads as busy. | Jesse Showalter | CLAIM(1xAfVDiX1ps@33:11, 1xAfVDiX1ps@33:26, 1xAfVDiX1ps@33:34) | single-source | yes |
| 32c | The layers panel should mark which elements carry an effect, so an animation audit is a panel read and not a guess. | Jesse Showalter | CLAIM(y4Rv-vf01LY@06:14, y4Rv-vf01LY@06:19) | single-source | yes |
| 32d | A hover state written once on the component master is applied to every instance automatically; do it there and preview immediately. | Jesse Showalter | CLAIM(y4Rv-vf01LY@05:01, y4Rv-vf01LY@05:13) | single-source | yes |
| 32e | Put a scaling image on its own absolute frame; an appear effect on the frame that also holds the copy scales the copy too. | Flux Academy | CLAIM(KZGLz0Glafo@12:56, KZGLz0Glafo@13:01, KZGLz0Glafo@13:28) | single-source | yes |
| 32f | Turn off the default fade-from-zero when the reference only scales in, and clip that scale with overflow hidden on a ratio-locked container. | Flux Academy | CLAIM(KZGLz0Glafo@15:06, KZGLz0Glafo@15:13, KZGLz0Glafo@15:22) | single-source | yes |
| 32g | Fire a scroll variant from a thin absolute trigger near the top of the section (about 8 to 16 pixels), not on load, and name the trigger. | Flux Academy | CLAIM(KZGLz0Glafo@29:34, KZGLz0Glafo@29:39, KZGLz0Glafo@29:54) | single-source | yes |
| 32h | Do not paint the scroll-state color on the component that also scales the logo; use a separate absolute bar and change its opacity or height between variants. | Flux Academy | CLAIM(KZGLz0Glafo@31:10, KZGLz0Glafo@31:23, KZGLz0Glafo@32:11) | single-source | yes |
| 32i | If light type sits on the hero photo, darken the image (brightness 0.9 was measured on the reference) so the type stays readable. | Flux Academy | CLAIM(KZGLz0Glafo@12:29, KZGLz0Glafo@14:45) | single-source | yes |

### Forms and data

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 33 | Use the platform's form builder rather than hand-building inputs: it arrives responsive and generates the input and button components for you. | Jesse Showalter | CLAIM(FGIPeIql9d4@00:38, FGIPeIql9d4@02:16) | single-source | yes |
| 34 | Style a form by editing the input components it created (including loading, disabled, success and hover states), not by styling the copy on the canvas. | Jesse Showalter | CLAIM(FGIPeIql9d4@01:01, FGIPeIql9d4@01:22) | single-source | yes |
| 35 | Give every form a primary destination plus a fallback sink (sheet first, email as backup) before publishing. | Jesse Showalter | CLAIM(FGIPeIql9d4@03:11, FGIPeIql9d4@03:38) | single-source | yes |
| 36 | Add an explicit opt-in checkbox for anything beyond the contact request, such as a newsletter subscription. | Jesse Showalter | CLAIM(FGIPeIql9d4@02:05, FGIPeIql9d4@02:11) | single-source | yes |
| 37 | Verify a form on the published URL: submit a real value, confirm the success and redirect behavior, then confirm the row actually landed in the sink. | Jesse Showalter | CLAIM(FGIPeIql9d4@04:00, FGIPeIql9d4@04:10, FGIPeIql9d4@04:42) | single-source | yes |
| 37a | Do not ship a client blog as static pages; generate detail pages from collections so a new entry creates its page, and keep one index page as the landing that is not generated per entry. | Flux Academy | CLAIM(2YBCdCZkT5Q@00:02, 2YBCdCZkT5Q@00:53, 2YBCdCZkT5Q@01:09) | single-source | yes |
| 37b | Let the folder around CMS pages be the URL prefix, and singularize detail slugs so the path stays clean. | Flux Academy | CLAIM(2YBCdCZkT5Q@01:38, 2YBCdCZkT5Q@01:58, 2YBCdCZkT5Q@02:05) | single-source | yes |
| 37c | Connect collections with fields before drawing pages: a single reference when an entry has one category or one author, a multi-reference when it has many tags, and fill those fields on every entry. | Flux Academy | CLAIM(2YBCdCZkT5Q@02:21, 2YBCdCZkT5Q@02:30, 2YBCdCZkT5Q@02:46) | single-source | yes |
| 37d | Put a current-page color on the text link style, not on the collection wrapper, and keep an all-link outside the collection so it is not repeated per item. | Flux Academy | CLAIM(2YBCdCZkT5Q@03:47, 2YBCdCZkT5Q@04:15, 2YBCdCZkT5Q@04:28) | single-source | yes |
| 37e | An absolutely placed load-more control needs bottom padding on its container, or it covers the last row. | Flux Academy | CLAIM(2YBCdCZkT5Q@05:06, 2YBCdCZkT5Q@05:10) | single-source | yes |
| 37f | Build one article list and paste it onto the other templates; on a nested list, filter where the reference equals the parent variable and cap the count instead of paginating every group. | Flux Academy | CLAIM(2YBCdCZkT5Q@07:04, 2YBCdCZkT5Q@06:49, 2YBCdCZkT5Q@07:26) | single-source | yes |
| 37g | A featured slot is a second list limited to one and gated by a feature field; the main list must exclude that entry so it does not appear twice. | Flux Academy | CLAIM(2YBCdCZkT5Q@08:57, 2YBCdCZkT5Q@09:01, 2YBCdCZkT5Q@09:42) | single-source | yes |
| 37h | Render a multi-reference (tags) as its own collection with a contains filter, point the link at that collection's slug, and remove a second link if the component already has one. | Flux Academy | CLAIM(2YBCdCZkT5Q@10:15, 2YBCdCZkT5Q@11:31, 2YBCdCZkT5Q@11:52) | single-source | yes |

### Performance and ship checks

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 38 | Test before and after every optimization pass with an objective scoring tool, and read the mobile and desktop results separately; a single score is not a result. | Jesse Showalter | CLAIM(63USLByBGNM@00:47, 63USLByBGNM@01:20, 63USLByBGNM@01:22, dCJ3LYF3wFA@04:31, dCJ3LYF3wFA@04:37) | single-source | yes |
| 39 | Run three questions against every image before upload: right format, right size, right compression. | Jesse Showalter | CLAIM(63USLByBGNM@02:02, 63USLByBGNM@02:07, dCJ3LYF3wFA@00:18, dCJ3LYF3wFA@00:20, dCJ3LYF3wFA@00:23) | single-source | yes |
| 40 | Downscale an image to the width it is actually displayed at before exporting; a 1200-pixel-wide asset on a small slot wastes most of its bytes and weakens the platform's own conversion. | Jesse Showalter | CLAIM(63USLByBGNM@03:19, 63USLByBGNM@03:31, 63USLByBGNM@02:50, dCJ3LYF3wFA@00:45, dCJ3LYF3wFA@00:49) | single-source | yes |
| 41 | Pick the format by content: a lossy format when transparency is not needed, a transparency-capable format when it is, and a vector file for logos and icons. | Jesse Showalter | CLAIM(63USLByBGNM@03:43, 63USLByBGNM@03:49, 63USLByBGNM@03:57, dCJ3LYF3wFA@00:27, dCJ3LYF3wFA@00:30) | single-source | yes |
| 42 | Losslessly compress each export (metadata and unreferenced data stripped) before uploading, and re-measure after the platform converts it. | Jesse Showalter | CLAIM(63USLByBGNM@04:26, 63USLByBGNM@05:00, 63USLByBGNM@05:24, dCJ3LYF3wFA@00:58, dCJ3LYF3wFA@01:03) | single-source | yes |
| 43 | Decide per video whether it is hosted or embedded: a short looping clip of a person talking earns the weight, long-form content belongs on a third-party host so the page stays fast. | Jesse Showalter | CLAIM(63USLByBGNM@06:12, 63USLByBGNM@06:30, 63USLByBGNM@06:46) | single-source | yes |
| 44 | Export video at the size and compression the slot needs and run it through a compressor; an untouched high-resolution master is the slowest asset on the page. | Jesse Showalter | CLAIM(63USLByBGNM@07:08, 63USLByBGNM@07:21, 63USLByBGNM@07:34) | single-source | yes |
| 45 | Count the dynamic elements (tickers, slideshows, carousels, iframe embeds, 3D scenes) as a budget: each one costs bandwidth, so cut the count instead of the quality. | Jesse Showalter | CLAIM(63USLByBGNM@08:07, 63USLByBGNM@08:15, 63USLByBGNM@08:36) | single-source | yes |
| 46 | Treat blur and heavy drop shadows as performance decisions: keep them selective, and respect the browser's limits the way print design respects paper. | Jesse Showalter | CLAIM(63USLByBGNM@08:52, 63USLByBGNM@09:12, 63USLByBGNM@09:31) | single-source | yes |
| 47 | Reduce the render tree: split an endless one-page site into real pages, use fewer animated elements, and flatten stacks that only exist to group things visually. | Jesse Showalter | CLAIM(63USLByBGNM@10:41, 63USLByBGNM@11:07, 63USLByBGNM@11:25) | single-source | yes |
| 48 | Depth in a layers panel understates cost: a visible list of about ten layers can still compile to more than a thousand rendered nodes, so inspect nesting, not layer count. | Jesse Showalter | CLAIM(63USLByBGNM@11:56, 63USLByBGNM@12:01) | single-source | yes |
| 49 | Publish to a staging URL and walk the live site before calling the build done; the preview and the published page are the acceptance surface. | Jesse Showalter | CLAIM(y4Rv-vf01LY@11:07, y4Rv-vf01LY@11:13, 1xAfVDiX1ps@34:06) | consensus | yes |
| 49a | Cut the number of server round trips on each page: every image, stylesheet, and script is a request, and fewer trips means a faster load. | Jesse Showalter | CLAIM(dCJ3LYF3wFA@01:12, dCJ3LYF3wFA@01:26, dCJ3LYF3wFA@01:39) | single-source | yes |
| 49b | Combine stylesheets into one file and scripts into one file, then minify that file so whitespace and comments are not shipped. | Jesse Showalter | CLAIM(dCJ3LYF3wFA@01:53, dCJ3LYF3wFA@02:02, dCJ3LYF3wFA@03:25) | single-source | yes |
| 49c | Use text wherever words can carry the meaning; a blog index does not need a photo on every row. | Jesse Showalter | CLAIM(dCJ3LYF3wFA@02:39, dCJ3LYF3wFA@02:49, dCJ3LYF3wFA@03:01) | single-source | yes |
| 49d | Serve static assets from a content delivery network instead of the origin shared host. | Jesse Showalter | CLAIM(dCJ3LYF3wFA@03:57, dCJ3LYF3wFA@04:14, dCJ3LYF3wFA@04:17) | single-source | yes |
| 49e | If a photo will sit under other content and never be seen sharp, export it at low quality. | Jesse Showalter | CLAIM(dCJ3LYF3wFA@00:33, dCJ3LYF3wFA@00:36, dCJ3LYF3wFA@00:40) | single-source | yes |
| 49f | Preview a template's motion before you apply it, and filter the library to free when the job will not pay for one. | Satori Graphics | CLAIM(mititlWcEco@03:54, mititlWcEco@04:06, mititlWcEco@04:13) | single-source | yes |
| 49g | Reach a repeated action from the command palette instead of hunting menus. | Satori Graphics | CLAIM(mititlWcEco@03:06, mititlWcEco@03:12) | single-source | yes |
| 49h | Invite a second editor into the project when the build needs more than one person, instead of passing exports around. | Satori Graphics | CLAIM(mititlWcEco@05:12, mititlWcEco@05:18) | single-source | yes |

## Looks like / does not (good vs bad pairs)

| # | looks like (good) | does not (bad) | why | citation |
|---|-------------------|----------------|-----|----------|
| 1 | A pasted design that arrives with responsive behavior, working buttons and named classes. | A pasted design that arrives as fixed or absolutely placed boxes. | The exporter can only transfer layout logic that was authored as layout logic. | CLAIM(xHXqj006Q2k@00:44, xHXqj006Q2k@02:49) |
| 2 | A hero whose text sits in a wrapper with center alignment and cannot be moved. | A hero where an element is dragged to a spot that happens to look right. | Free placement looks right at one width and breaks at every other. | CLAIM(P5H7zs0RsUM@07:37, P5H7zs0RsUM@08:14, KZGLz0Glafo@05:06) |
| 3 | Content centered in a fixed container with equal side tracks on a wide screen. | Content pinned to the full canvas width of the desktop artboard. | The container is what makes one design work across screen widths. | CLAIM(BNYLKuIlazA@01:54, xHXqj006Q2k@00:26) |
| 4 | One grid class shared by every aligned group, with a combo class for the single exception. | Three near-identical grids styled separately. | Separate copies must be re-tuned three times per breakpoint. | CLAIM(WLDfFqnqbxI@03:38, WLDfFqnqbxI@04:40) |
| 5 | A card whose corner radius clips its own image via overflow hidden. | A rounded card whose square image still bleeds past the corners. | Radius applies to the container, the child image needs clipping to obey it. | CLAIM(WLDfFqnqbxI@11:34, WLDfFqnqbxI@11:49) |
| 6 | A button reused from one master with a hover variant. | Several hand-styled button copies with slightly different padding. | Copies drift; a master keeps the system consistent. | CLAIM(P5H7zs0RsUM@16:40, P5H7zs0RsUM@18:14, mititlWcEco@01:46) |
| 7 | Text aligned on a shared baseline after a deliberate margin nudge. | Text that looks aligned by box but sits high or low on the line. | Bounding boxes include descender space, so box alignment is not optical alignment. | CLAIM(WLDfFqnqbxI@08:25, WLDfFqnqbxI@09:00) |
| 8 | A heading that scales down smoothly with the window. | A heading fixed in pixels that overflows the narrow viewport. | Viewport sizing keeps a display line to one piece across widths. | CLAIM(WLDfFqnqbxI@07:23, WLDfFqnqbxI@07:35) |
| 9 | Two header actions that read as buttons, one outlined and one filled, with even vertical padding across the nav. | A header that can only show one button, or buttonized items whose padding makes the row look broken. | The platform will not ship the second button; CSS on the existing items is the fix, and vertical padding has to be shared or the row breaks. | CLAIM(MGvGiu6WjYk@00:25, MGvGiu6WjYk@01:37) |
| 10 | A summary read-more with a border, padding, a partial width and centered type. | The default text read-more, or that same link stretched to the full card width. | The link is already there; the button is a scoped restyle, and full width stops reading as a button. | CLAIM(c6AGaxigBAY@00:55, c6AGaxigBAY@01:49) |
| 11 | A hover that fills and flips the label color over about a fifth of a second. | A hover that only fills, so the label matches the fill, or a two-second fade. | Contrast and a short timing are what make the state readable. | CLAIM(c6AGaxigBAY@05:05, c6AGaxigBAY@03:13) |
| 12 | Copy that stays pinned to the bottom of a tall hero until the container ends. | Copy that scrolls away immediately because a parent clips overflow. | Sticky only engages when the stack is pinned to the bottom and every parent overflow is visible. | CLAIM(KZGLz0Glafo@07:33, KZGLz0Glafo@07:52) |
| 13 | A button hover that scales only the fill while the label stays still. | A hover that scales the whole component, type included. | The fill has to be its own absolute frame under the label. | CLAIM(KZGLz0Glafo@09:14, KZGLz0Glafo@10:05) |
| 14 | A hero image that scales in and stays clipped to the ratio frame. | A scale that spills past the hero and flashes the page color, or a fade the reference never had. | The image needs its own frame, overflow hidden, and the default opacity tween removed. | CLAIM(KZGLz0Glafo@14:54, KZGLz0Glafo@15:13) |
| 15 | A blog whose category, author, and tag pages are generated from filled reference fields. | A set of static post pages that must be rewired every time an entry changes. | Collections plus filters are what keep one edit from becoming a page rebuild. | CLAIM(2YBCdCZkT5Q@00:10, 2YBCdCZkT5Q@12:39) |
| 16 | A featured post shown once, then a list that excludes it. | The same post repeated in the feature slot and the grid. | The second query needs an exclusion filter, not just a limit. | CLAIM(2YBCdCZkT5Q@09:01, 2YBCdCZkT5Q@09:42) |
| 17 | A blog row carried by its title. | A photo on every article card when the title would do. | Text is cheaper for the browser than another image request. | CLAIM(dCJ3LYF3wFA@02:46, dCJ3LYF3wFA@02:53) |
| 18 | One combined, minified stylesheet and one script. | A separate request for every CSS file and every script. | Each file is a round trip; combining and minifying cuts both count and bytes. | CLAIM(dCJ3LYF3wFA@01:56, dCJ3LYF3wFA@03:25) |
| 19 | A color saved as a named style and applied from the panel. | The same hex re-picked on every frame. | A named style is one later edit; a raw hex is a hunt. | CLAIM(mititlWcEco@00:35, mititlWcEco@00:48) |
| 20 | A template whose motion you have played, then applied. | A template applied blind, or a paid one chosen when a free filter was available. | Preview is the try-before-apply step; the free filter is the budget check. | CLAIM(mititlWcEco@03:59, mititlWcEco@04:13) |

## Decision tables (option A vs B -> pick when)

| Decision | Pick A when | Pick B when | citation |
|---|---|---|---|
| Hand-build the site vs import the design | Import: standard layout blocks and a well structured design file (the estimate is minutes rather than an hour). | Hand-build: first time on the platform, or a bespoke layout the exporter cannot express (sliders, custom interaction logic). | CLAIM(xHXqj006Q2k@06:32, xHXqj006Q2k@07:02, P5H7zs0RsUM@00:25) |
| One big grid vs several grouped grids | One grid: everything on the screen truly shares one column rhythm and no breakpoint work is expected. | Grouped grids under one parent: a bento or dashboard page that must restack per breakpoint. | CLAIM(WLDfFqnqbxI@01:37, WLDfFqnqbxI@14:47) |
| Pixels vs viewport units for type | Pixels: body and UI text that must stay legible at a floor size. | Viewport units: a single display headline that must fit one line at every width. | CLAIM(WLDfFqnqbxI@07:23, WLDfFqnqbxI@16:03) |
| Absolute positioning | Decoration and backdrops that must sit behind content. | Never for content; it is what makes an export unmaintainable. | CLAIM(BNYLKuIlazA@06:14, xHXqj006Q2k@02:49) |
| Invert filter vs per-button hover colors | Invert: one hover should flip both header buttons with the least CSS. | Per-button colors: each button must invert its own fill and label. | CLAIM(MGvGiu6WjYk@03:34, MGvGiu6WjYk@03:47) |
| Full-width summary link vs partial width | Full width: the style wants a card-footer bar. | About 60 percent: it should read as a button, not a bar. | CLAIM(c6AGaxigBAY@01:52, c6AGaxigBAY@02:01) |
| Viewport-height hero vs image-ratio hero | 100 viewport height: the hero must fill one screen regardless of the photo. | Aspect ratio: the reference locks the photo's ratio, and the copy sticks until that frame ends. | CLAIM(P5H7zs0RsUM@06:16, KZGLz0Glafo@03:37) |
| Single reference vs multi-reference | Single: the entry has one category or one author. | Multi: the entry has many tags, and the filter is contains, not equals. | CLAIM(2YBCdCZkT5Q@02:25, 2YBCdCZkT5Q@02:36) |
| Load more vs infinite scroll | Load more: a landing list with a visible control and a small page size (six was used). | Infinite: a filtered category or tag page where a button would just repeat. | CLAIM(2YBCdCZkT5Q@05:00, 2YBCdCZkT5Q@08:48) |
| Named color style vs raw hex | The color will be used in more than one place. | A one-off swatch that will never repeat. | CLAIM(mititlWcEco@00:18, mititlWcEco@00:24) |
| Text vs image on a repeated row | Words can carry the meaning. | The image is the content, such as a portfolio still or a product shot. | CLAIM(dCJ3LYF3wFA@02:41, dCJ3LYF3wFA@02:51) |
| Free template vs paid template | The job will not pay for a library file, or a free result matches the search. | A paid template is the only match, and the budget allows it. | CLAIM(mititlWcEco@04:06, mititlWcEco@04:13) |

## Anti-patterns (cited)

| # | anti-pattern | what breaks | citation |
|---|---|---|---|
| 1 | Designing with loose groups and hoping the exporter guesses the layout. | The transfer drops to fixed placement with no responsive behavior. | CLAIM(xHXqj006Q2k@02:25, xHXqj006Q2k@02:49) |
| 2 | Pasting into the builder before the fonts exist in the project. | Every text node needs its face re-assigned by hand. | CLAIM(xHXqj006Q2k@04:44) |
| 3 | Placing elements by eye in a canvas-style editor. | Nothing is anchored, so the first resize breaks the composition. | CLAIM(P5H7zs0RsUM@07:37) |
| 4 | Leaving one oversized image at natural size inside a grid cell. | It pushes following rows past the intended fold. | CLAIM(WLDfFqnqbxI@10:01) |
| 6 | Building a page with only desktop in mind and no per-breakpoint pass. | A dense bento grid stops holding together at tablet width until columns are re-spanned. | CLAIM(WLDfFqnqbxI@13:58, WLDfFqnqbxI@14:08) |
| 7 | Writing a header selector from memory instead of the inspector. | The rule misses the item and nothing on the page changes. | CLAIM(MGvGiu6WjYk@00:42, MGvGiu6WjYk@00:51) |
| 8 | Setting color on the nav item when the label is an anchor. | The filled button keeps dark text on a dark fill. | CLAIM(MGvGiu6WjYk@02:40, MGvGiu6WjYk@02:49) |
| 9 | Filling a hover without changing the label color. | The word disappears into the background. | CLAIM(c6AGaxigBAY@05:03, c6AGaxigBAY@05:08) |
| 10 | Reaching for !important before a more specific selector. | Later overrides have nothing left to beat. | CLAIM(c6AGaxigBAY@05:23, c6AGaxigBAY@05:33) |
| 11 | Dragging a hero image or headline into a frame that has no layout. | The first resize leaves it where you dropped it. | CLAIM(KZGLz0Glafo@05:03, KZGLz0Glafo@05:08) |
| 12 | Setting sticky while a parent overflow is hidden. | The pin never engages and the copy scrolls away. | CLAIM(KZGLz0Glafo@07:48, KZGLz0Glafo@07:56) |
| 13 | Putting an appear effect on the frame that also holds the copy. | The headline scales with the photo. | CLAIM(KZGLz0Glafo@12:56, KZGLz0Glafo@13:00) |
| 14 | Painting the scroll color on the same component that scales the logo. | The bar grows and shrinks with the mark. | CLAIM(KZGLz0Glafo@31:16, KZGLz0Glafo@31:25) |
| 15 | Shipping a client blog as static pages. | Every new post is a manual page rebuild. | CLAIM(2YBCdCZkT5Q@00:00, 2YBCdCZkT5Q@00:04) |
| 16 | Leaving an all-link inside a collection list. | The link is generated once per item. | CLAIM(2YBCdCZkT5Q@04:25, 2YBCdCZkT5Q@04:30) |
| 17 | Uploading a multi-megabyte photo at camera size. | The page waits on bytes nobody will see at that resolution. | CLAIM(dCJ3LYF3wFA@00:47, dCJ3LYF3wFA@00:52) |
| 18 | Putting an image on every list row because a picture feels easier than a sentence. | Each row adds a request the title did not need. | CLAIM(dCJ3LYF3wFA@02:51, dCJ3LYF3wFA@02:57) |

## Creator claims (unverified)

| # | claim | creator | citation |
|---|---|---|---|
| 1 | A structured Figma page transfers to the builder in minutes instead of the roughly hour the manual rebuild took. | Flux Academy | CLAIM(xHXqj006Q2k@06:32, xHXqj006Q2k@06:46) |
| 2 | The auto-layout-based transfer covers something like 80 to 90 percent of common layout blocks. | Flux Academy | CLAIM(xHXqj006Q2k@07:17) |
| 3 | Keep really large images under 150 kilobytes. | Jesse Showalter | CLAIM(dCJ3LYF3wFA@00:42, dCJ3LYF3wFA@00:43) |
| 4 | A CDN will deliver assets faster than shared hosting. | Jesse Showalter | CLAIM(dCJ3LYF3wFA@04:15, dCJ3LYF3wFA@04:27) |

## Tool-specific (dated)

| # | item | tool / feature | year | citation |
|---|---|---|---|---|
| 1 | Figma to Webflow plugin copies styles, images (icons as SVG), class names and turns layers named as buttons into links. | Figma to Webflow plugin | 2023 | CLAIM(xHXqj006Q2k@03:14, xHXqj006Q2k@05:03) |
| 2 | The plugin cannot carry breakpoint logic from a desktop-only design; responsiveness comes from its supplied blocks. | Figma to Webflow plugin | 2023 | CLAIM(xHXqj006Q2k@03:40, xHXqj006Q2k@03:57) |
| 3 | Framer's Stack layout primitive is flexbox under the hood, with direction, gap, alignment and padding controls. | Framer Stacks | 2023 | CLAIM(P5H7zs0RsUM@04:30, P5H7zs0RsUM@04:43) |
| 4 | Framer's Supply library supplies ready-made parts such as Motion Text (animate by letter, word or line). | Framer Supply / Motion Text | 2023 | CLAIM(P5H7zs0RsUM@06:38, P5H7zs0RsUM@07:18) |
| 5 | Webflow grid child position (auto vs manual) plus shift-drag places a single item into a chosen grid cell. | Webflow CSS Grid | 2023 | CLAIM(WLDfFqnqbxI@06:08, WLDfFqnqbxI@06:28) |
| 6 | Default Webflow link styling ships blue and underlined and must be overridden on every new project. | Webflow default styles | 2023 | CLAIM(WLDfFqnqbxI@05:25, WLDfFqnqbxI@05:38) |
| 7 | Spline scenes drop into Framer through an embed component that takes the scene's public URL and reacts to the cursor. | Spline + Framer embed | 2023 | CLAIM(BNYLKuIlazA@05:02, BNYLKuIlazA@05:33) |
| 8 | Squarespace has no native two-button header; the fix is custom CSS on header nav items via nth-child. | Squarespace custom CSS | 2023 | CLAIM(MGvGiu6WjYk@00:25, MGvGiu6WjYk@01:06) |
| 9 | A filled nav item's label color is set by appending the anchor to the selector. | Squarespace custom CSS | 2023 | CLAIM(MGvGiu6WjYk@02:51, MGvGiu6WjYk@02:55) |
| 10 | filter invert is the short hover for two header buttons; a bespoke background and color swap is the alternative. | Squarespace custom CSS | 2023 | CLAIM(MGvGiu6WjYk@03:34, MGvGiu6WjYk@03:49) |
| 11 | A summary-block read-more link is restyled through the block, item, then read-more-link chain in custom CSS. | Squarespace custom CSS | 2023 | CLAIM(c6AGaxigBAY@01:11, c6AGaxigBAY@01:17) |
| 12 | A custom CSS font-family only resolves faces already in the site's loaded families (Adobe Fonts was the path named). | Squarespace custom CSS | 2023 | CLAIM(c6AGaxigBAY@03:41, c6AGaxigBAY@03:51) |
| 13 | Framer sticky does nothing unless parent overflow is visible; the default appear effect also fades from zero opacity unless that tween is removed. | Framer sticky / appear | 2025 | CLAIM(KZGLz0Glafo@07:52, KZGLz0Glafo@15:13) |
| 14 | Switching a layer to fixed position resets its width to a pixel value; set it back to 100 percent. | Framer fixed position | 2025 | CLAIM(KZGLz0Glafo@23:51, KZGLz0Glafo@23:55) |
| 15 | Framer variants cannot change a layer's parent; reposition with absolute instead of re-nesting. | Framer component variants | 2025 | CLAIM(KZGLz0Glafo@28:08, KZGLz0Glafo@28:14) |
| 16 | A Framer scroll variant can be driven by a named section-in-view trigger rather than by page load. | Framer scroll variant | 2025 | CLAIM(KZGLz0Glafo@29:00, KZGLz0Glafo@30:06) |
| 17 | Scaling an SVG directly breaks the bar; wrap it in a frame first. | Framer SVG | 2025 | CLAIM(KZGLz0Glafo@25:48, KZGLz0Glafo@25:53) |
| 18 | Framer CMS index pages are not generated per entry; detail pages are. Reference is one link, multi-reference is many, and a load-more control arrives absolute. | Framer CMS | 2026 | CLAIM(2YBCdCZkT5Q@00:53, 2YBCdCZkT5Q@02:25, 2YBCdCZkT5Q@05:08) |
| 19 | ImageOptim strips metadata weight before upload. | ImageOptim | 2020 | CLAIM(dCJ3LYF3wFA@00:58, dCJ3LYF3wFA@01:03) |
| 20 | Sass or Less combines many stylesheets into one file before minify. | Sass / Less | 2020 | CLAIM(dCJ3LYF3wFA@01:53, dCJ3LYF3wFA@01:59) |
| 21 | Google PageSpeed Insights is the free score-and-recommendations pass. | Google PageSpeed Insights | 2020 | CLAIM(dCJ3LYF3wFA@04:36, dCJ3LYF3wFA@04:37) |
| 22 | Amazon S3 and Cloudflare are named CDN options versus shared hosting. | CDN (S3, Cloudflare) | 2020 | CLAIM(dCJ3LYF3wFA@04:03, dCJ3LYF3wFA@04:06) |
| 23 | Framer saves a color as a named style with a stable id from the Styles panel. | Framer Styles | 2024 | CLAIM(mititlWcEco@00:24, mititlWcEco@00:42) |
| 24 | In Framer, I opens insert, F creates a frame, and Command-K or Control-K opens the action search. | Framer shortcuts | 2024 | CLAIM(mititlWcEco@02:32, mititlWcEco@02:44, mititlWcEco@03:06) |
| 25 | Adding /templates to the project URL opens the library; the play control previews motion; a toggle limits the list to free. | Framer templates library | 2024 | CLAIM(mititlWcEco@03:36, mititlWcEco@03:54, mititlWcEco@04:13) |

## Disagreements between creators (who says what, cited)

| # | topic | position A | position B | citations |
|---|---|---|---|---|
| 1 | Should the design be imported or rebuilt | Import a properly auto-laid-out file; the time saving is large and class names and styles come free. | Rebuild by hand for the first version so you understand the platform and can fix what the import leaves broken. | CLAIM(xHXqj006Q2k@06:32), CLAIM(P5H7zs0RsUM@00:25) |
| 2 | Does a fixed design spec translate directly to the live page | Not automatically: the 18px spec came down to 16 once it was rendered. | Text should keep the design's declared size unless the rendered result looks wrong. | CLAIM(WLDfFqnqbxI@02:37), |
| 3 | How tall is a one-screen hero | Fill the viewport height so the first screen is always one screen. | Lock the hero to the photo's aspect ratio and sticky the copy; this reference does not fill the viewport, and the ratio plus the image both change on the phone. | CLAIM(P5H7zs0RsUM@06:16), CLAIM(KZGLz0Glafo@03:37) |
| 4 | Blank canvas vs a library template | Build the first version by hand so you understand the platform and can fix a bad import. | Apply a library template after playing its motion, and filter to free if you will not pay. | CLAIM(P5H7zs0RsUM@00:25), CLAIM(mititlWcEco@05:00) |

## Suggested sub-skills (2-5 names, one line each, which law #s they own)

| sub-skill | owns |
|---|---|
| design-to-build-handoff | Prepare a design file so a builder can consume it: auto layout, containers, naming, fonts, sizing checks. Laws 1-8e. |
| builder-layout-construction | Stacks, grids, wrappers, containers, overflow and baseline work inside Framer/Webflow. Laws 9-21s. |
| components-tokens-variants | Component and variable discipline plus button and card construction. Laws 22-29y. |
| platform-css-overrides | Restyle a missing native control with scoped CSS: inspector first, exact nodes, padding, hover contrast, no early !important. Laws 29j-29u. |
| cms-dynamic-pages | Generate blog pages from collections: references, filters, one shared list, featured exclusion. Laws 37a-37h. |
| ship-performance | Image weight, request count, minify, CDN, and a scored before/after. Laws 38-49h. |
| build-motion-and-effects | Entrance animation sequencing, hover states and embedded 3D or video layers. Laws 25, 30-32i. |
