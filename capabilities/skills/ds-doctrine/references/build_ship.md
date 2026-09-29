# Build & ship laws (Design Studio OS corpus)

Coverage: 8 videos read so far (P5H7zs0RsUM, xHXqj006Q2k, WLDfFqnqbxI, BNYLKuIlazA, FGIPeIql9d4, y4Rv-vf01LY, 63USLByBGNM, 1xAfVDiX1ps). Channels: Flux Academy (4), Jesse Showalter (4). Date range 2023-02-02 to 2025-03-31. Top-10 channels present: flux-academy, jesse-showalter.

## Laws

### Design-to-build handoff (structure that survives the copy)

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 1 | Before touching the builder, read the design and write down the structure it implies: how many top-level groups, what grid it sits on, which elements must resize and which stay fixed. | Flux Academy | CLAIM(WLDfFqnqbxI@00:30, WLDfFqnqbxI@00:50) | single-source | yes |
| 2 | Name every frame by its role (hero, container, nav, button) before exporting; the names become class names in the builder, and a well named file is a reusable style guide on arrival. | Flux Academy | CLAIM(xHXqj006Q2k@05:03, xHXqj006Q2k@05:12, P5H7zs0RsUM@05:51) | consensus | yes |
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

### Layout construction in the builder

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 9 | Define shared colors as named styles at the start of the build, before placing elements, so reuse costs one click instead of a re-picked hex. | Flux Academy | CLAIM(P5H7zs0RsUM@00:46, P5H7zs0RsUM@01:00) | single-source | yes |
| 10 | Take the platform's own navigation component instead of drawing one; it arrives with the mobile collapse already handled. | Flux Academy | CLAIM(P5H7zs0RsUM@01:08, P5H7zs0RsUM@01:19) | single-source | yes |
| 11 | A web layout is never free-positioned: every element lives inside a stack (or wrapper) whose alignment controls it, so nothing can be dragged off its line. | Flux Academy | CLAIM(P5H7zs0RsUM@07:37, P5H7zs0RsUM@07:50) | single-source | yes |
| 12 | Give full-bleed sections 100 percent width (or 100 viewport height for a one-screen hero) and keep the content inside a centered container so the page scales and the copy stays on a readable measure. | Flux Academy | CLAIM(P5H7zs0RsUM@06:16, BNYLKuIlazA@00:16, BNYLKuIlazA@01:47) | consensus | yes |
| 13 | Split a single-screen composition into separate top-level groups (nav, text block, card area) rather than one giant grid, so each part can be restacked at tablet and mobile without breaking the others. | Flux Academy | CLAIM(WLDfFqnqbxI@01:20, WLDfFqnqbxI@14:47) | single-source | yes |
| 14 | Define one grid class (column count plus gap) and reapply it to every group that shares the grid; use a combo class when a single group needs a local override. | Flux Academy | CLAIM(WLDfFqnqbxI@03:30, WLDfFqnqbxI@04:40) | single-source | yes |
| 15 | Wrap a section's children in a vertical flex parent when you need controlled gaps and one child that grows to fill the remaining height. | Flux Academy | CLAIM(WLDfFqnqbxI@04:21, WLDfFqnqbxI@04:34) | single-source | yes |
| 16 | Pull an element out of normal grid flow with absolute positioning when it is decoration rather than content (a 3D or image backdrop), and size it to 100 percent of its frame so it stays behind the copy. | Flux Academy | CLAIM(BNYLKuIlazA@05:58, BNYLKuIlazA@06:14) | single-source | yes |
| 17 | Set any image that could exceed its cell to fill its box and clip the parent with overflow hidden, otherwise one oversized asset pushes the next row below the fold. | Flux Academy | CLAIM(WLDfFqnqbxI@10:01, WLDfFqnqbxI@11:49) | single-source | yes |
| 18 | Use space-between on a card's vertical flex to pin one element to the top and one to the bottom instead of hard-coding margins. | Flux Academy | CLAIM(WLDfFqnqbxI@13:04, WLDfFqnqbxI@13:18) | single-source | yes |
| 19 | Size a display headline in viewport units (13 viewport width was used) when it must scale with the screen, then set line height from the text and cap its width. | Flux Academy | CLAIM(WLDfFqnqbxI@06:47, WLDfFqnqbxI@07:23, WLDfFqnqbxI@07:50) | single-source | yes |
| 20 | Align to type baselines, not to bounding boxes: when a bottom-aligned block lands visually short, nudge its margin until the baselines read level. | Flux Academy | CLAIM(WLDfFqnqbxI@08:25, WLDfFqnqbxI@08:52) | single-source | yes |
| 21 | Cap text width (max width or a percentage of the parent) on every long block so a wide viewport cannot stretch a paragraph into one unbroken line. | Flux Academy | CLAIM(P5H7zs0RsUM@14:48, WLDfFqnqbxI@08:47) | consensus | yes |
| 21a | Give the page one containing element at 100 percent width with a max width (1200 was used) and let children fill it: responsive growth needs a documented stop. | Jesse Showalter | CLAIM(1xAfVDiX1ps@18:56, 1xAfVDiX1ps@19:06) | single-source | yes |
| 21b | Keep the page artboard width fixed (it defines the breakpoints) and its height fit-content, or added content is pushed off a canvas that stops growing. | Jesse Showalter | CLAIM(1xAfVDiX1ps@20:52, 1xAfVDiX1ps@21:11) | single-source | yes |
| 21c | Set a horizontal group to fill its parent when logo and call-to-action must sit at opposite ends. | Jesse Showalter | CLAIM(1xAfVDiX1ps@12:08, 1xAfVDiX1ps@12:20) | single-source | yes |
| 21d | Add side padding on a nav or wrapper (24 left and right, 12 top and bottom was used) so content never touches the browser edge. | Jesse Showalter | CLAIM(1xAfVDiX1ps@08:26, 1xAfVDiX1ps@08:42) | single-source | yes |
| 21e | Lay the content in first and group it afterwards: drop the copy, buttons and images, then collect them into stacks and named sections that stack cleanly. | Jesse Showalter | CLAIM(1xAfVDiX1ps@13:21, 1xAfVDiX1ps@13:41) | single-source | yes |
| 21f | Wrap a bare image in its own stack when it needs surrounding space; an image on its own cannot take the padding. | Jesse Showalter | CLAIM(1xAfVDiX1ps@24:07, 1xAfVDiX1ps@24:20) | single-source | yes |
| 21g | Reuse the container element (copy it, clear it, refill it) for the next section so the left and right edges of the page stay on one line. | Jesse Showalter | CLAIM(1xAfVDiX1ps@23:13, 1xAfVDiX1ps@23:38) | single-source | yes |
| 21h | When a decorative background is cut off by its parent, that is the container's overflow setting, not the image's size: switch it to visible. | Jesse Showalter | CLAIM(1xAfVDiX1ps@25:07, 1xAfVDiX1ps@25:17) | single-source | yes |
| 21i | Push a decorative layer behind content with a negative z-index rather than reordering the layer list, and lock it once placed. | Jesse Showalter | CLAIM(1xAfVDiX1ps@22:04, 1xAfVDiX1ps@22:23, 1xAfVDiX1ps@30:06) | single-source | yes |
| 21j | Add breakpoints before the layout visibly breaks, and work from the largest breakpoint down: a change made on a smaller artboard applies to that size and every size below it, never above. | Jesse Showalter | CLAIM(1xAfVDiX1ps@25:49, 1xAfVDiX1ps@26:00, 1xAfVDiX1ps@26:34) | single-source | yes |
| 21k | Set a type style's size once per breakpoint inside the style itself (64, 54, 38 was used) and reduce line height with it, instead of overriding headings one by one. | Jesse Showalter | CLAIM(1xAfVDiX1ps@28:37, 1xAfVDiX1ps@28:56, 1xAfVDiX1ps@29:26) | single-source | yes |
| 21l | On narrow layouts, switch a button row to vertical and set both the buttons and their group to fill so they become edge-to-edge tap targets. | Jesse Showalter | CLAIM(1xAfVDiX1ps@30:13, 1xAfVDiX1ps@30:26) | single-source | yes |

### Components, variants and tokens

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 22 | Anything reused twice (button, nav, footer, card) becomes a component the moment it is styled; edit the master and every instance follows. | Flux Academy | CLAIM(P5H7zs0RsUM@16:35, P5H7zs0RsUM@01:43, BNYLKuIlazA@03:43) | consensus | yes |
| 23 | Put state differences into variants on the same component (main, hover) rather than into a second copy, so the styles cannot drift apart. | Flux Academy | CLAIM(P5H7zs0RsUM@18:14, P5H7zs0RsUM@18:20) | single-source | yes |
| 24 | A press-feel hover is built by changing the fill and collapsing the shadow offset to zero in the hover variant. | Flux Academy | CLAIM(P5H7zs0RsUM@18:23, P5H7zs0RsUM@18:35) | single-source | yes |
| 25 | A hard-edged shadow is zero blur with a small spread and a small offset; blur is what makes a shadow look soft and generic. | Flux Academy | CLAIM(P5H7zs0RsUM@17:52, P5H7zs0RsUM@18:03) | single-source | yes |
| 26 | Build a button as a hug-sized frame with text inside, more horizontal than vertical padding and a small radius, then componentize it. | Flux Academy | CLAIM(BNYLKuIlazA@02:36, BNYLKuIlazA@03:02, BNYLKuIlazA@03:13) | single-source | yes |
| 27 | Any value repeated in two or more places (corner radius, color) becomes a variable so a later change lands everywhere at once. | Flux Academy | CLAIM(WLDfFqnqbxI@11:09, WLDfFqnqbxI@11:20) | single-source | yes |
| 28 | Reuse the project's predefined heading and paragraph styles instead of hand-setting each text block; only genuinely one-off display type gets its own class. | Flux Academy | CLAIM(P5H7zs0RsUM@14:15, WLDfFqnqbxI@07:10) | consensus | yes |
| 29 | Set the base type once on the body/all-pages class and let it cascade to everything below. | Flux Academy | CLAIM(WLDfFqnqbxI@02:25, WLDfFqnqbxI@02:33) | single-source | yes |
| 29a | Name the layer before converting it to a component: the component inherits the layer name, and an unnamed component is unfindable later. | Jesse Showalter | CLAIM(1xAfVDiX1ps@10:39, 1xAfVDiX1ps@10:50) | single-source | yes |
| 29b | Create the variants and states a component will need at creation time (a second style plus hover), not after ten instances exist. | Jesse Showalter | CLAIM(1xAfVDiX1ps@10:56, 1xAfVDiX1ps@11:51) | single-source | yes |
| 29c | Expose the editable text of a component as a variable with a default value so each instance can carry its own label without leaving the master. | Jesse Showalter | CLAIM(1xAfVDiX1ps@17:54, 1xAfVDiX1ps@18:06) | single-source | yes |
| 29d | Nest components (a button inside a nav) rather than duplicating the button markup into the nav. | Jesse Showalter | CLAIM(1xAfVDiX1ps@11:57, y4Rv-vf01LY@04:26) | consensus | yes |
| 29e | Brand a supplied component by pointing its parts at the project's color styles, and set every state (default, hover, pressed, disabled) while you are there. | Jesse Showalter, Flux Academy | CLAIM(FGIPeIql9d4@01:30, FGIPeIql9d4@01:40, P5H7zs0RsUM@18:14) | consensus | yes |
| 29f | Build small repeated parts (chip, tag, button) from a fit-content stack with more horizontal than vertical padding and a full radius, then componentize on the spot when a second use is likely. | Jesse Showalter | CLAIM(1xAfVDiX1ps@15:45, 1xAfVDiX1ps@16:10, 1xAfVDiX1ps@16:39) | single-source | yes |
| 29g | Start a hard part (navigation) from a pre-built component and restyle it instead of building it from scratch; it arrives with the mobile collapse already wired. | Jesse Showalter, Flux Academy | CLAIM(1xAfVDiX1ps@07:02, 1xAfVDiX1ps@07:09, P5H7zs0RsUM@01:19) | consensus | yes |
| 29h | Where a template is the starting point, restyle its colors and text styles from the assets panel first; that is what turns a stock layout into a client-unique site. | Jesse Showalter | CLAIM(y4Rv-vf01LY@10:26, y4Rv-vf01LY@10:56) | single-source | yes |
| 29i | Rebuild a repeated card from stacks so its padding, internal gaps and radius are all container properties, never manual positions. | Jesse Showalter | CLAIM(y4Rv-vf01LY@01:56, y4Rv-vf01LY@02:41, y4Rv-vf01LY@02:53) | single-source | yes |

### Motion and effects while building

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 30 | Reveal hero text by line rather than by letter; line-level entrance stays readable, letter-level looks like a typewriter. | Flux Academy | CLAIM(P5H7zs0RsUM@07:18, P5H7zs0RsUM@09:27) | single-source | yes |
| 31 | Sequence entrance effects: delay the secondary element (the hero image) by around half a second so the text lands first and the load reads as one motion. | Flux Academy | CLAIM(P5H7zs0RsUM@11:11, P5H7zs0RsUM@11:34) | single-source | yes |
| 32 | When a headline animates and resizes on the same element, keep the animation and the responsive size as two separate settings and test the preview at more than one width before accepting it. | Flux Academy | CLAIM(P5H7zs0RsUM@06:38, WLDfFqnqbxI@07:31) | consensus | yes |
| 32a | Author an entrance animation as an off-state plus a destination (start at zero opacity, travel about 20px, half a second), then copy the effect and only change the delay to stagger a group. | Jesse Showalter | CLAIM(1xAfVDiX1ps@31:16, 1xAfVDiX1ps@31:38, 1xAfVDiX1ps@32:16) | single-source | yes |
| 32b | Keep a scroll effect small on one hero asset: a few pixels of translate or scale, not an opacity change, or the page reads as busy. | Jesse Showalter | CLAIM(1xAfVDiX1ps@33:11, 1xAfVDiX1ps@33:26, 1xAfVDiX1ps@33:34) | single-source | yes |
| 32c | The layers panel should mark which elements carry an effect, so an animation audit is a panel read and not a guess. | Jesse Showalter | CLAIM(y4Rv-vf01LY@06:14, y4Rv-vf01LY@06:19) | single-source | yes |
| 32d | A hover state written once on the component master is applied to every instance automatically; do it there and preview immediately. | Jesse Showalter | CLAIM(y4Rv-vf01LY@05:01, y4Rv-vf01LY@05:13) | single-source | yes |

### Forms and data

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 33 | Use the platform's form builder rather than hand-building inputs: it arrives responsive and generates the input and button components for you. | Jesse Showalter | CLAIM(FGIPeIql9d4@00:38, FGIPeIql9d4@02:16) | single-source | yes |
| 34 | Style a form by editing the input components it created (including loading, disabled, success and hover states), not by styling the copy on the canvas. | Jesse Showalter | CLAIM(FGIPeIql9d4@01:01, FGIPeIql9d4@01:22) | single-source | yes |
| 35 | Give every form a primary destination plus a fallback sink (sheet first, email as backup) before publishing. | Jesse Showalter | CLAIM(FGIPeIql9d4@03:11, FGIPeIql9d4@03:38) | single-source | yes |
| 36 | Add an explicit opt-in checkbox for anything beyond the contact request, such as a newsletter subscription. | Jesse Showalter | CLAIM(FGIPeIql9d4@02:05, FGIPeIql9d4@02:11) | single-source | yes |
| 37 | Verify a form on the published URL: submit a real value, confirm the success and redirect behavior, then confirm the row actually landed in the sink. | Jesse Showalter | CLAIM(FGIPeIql9d4@04:00, FGIPeIql9d4@04:10, FGIPeIql9d4@04:42) | single-source | yes |

### Performance and ship checks

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 38 | Test before and after every optimization pass with an objective scoring tool, and read the mobile and desktop results separately; a single score is not a result. | Jesse Showalter | CLAIM(63USLByBGNM@00:47, 63USLByBGNM@01:20, 63USLByBGNM@01:22) | single-source | yes |
| 39 | Run three questions against every image before upload: right format, right size, right compression. | Jesse Showalter | CLAIM(63USLByBGNM@02:02, 63USLByBGNM@02:07) | single-source | yes |
| 40 | Downscale an image to the width it is actually displayed at before exporting; a 1200-pixel-wide asset on a small slot wastes most of its bytes and weakens the platform's own conversion. | Jesse Showalter | CLAIM(63USLByBGNM@03:19, 63USLByBGNM@03:31, 63USLByBGNM@02:50) | single-source | yes |
| 41 | Pick the format by content: a lossy format when transparency is not needed, a transparency-capable format when it is, and a vector file for logos and icons. | Jesse Showalter | CLAIM(63USLByBGNM@03:43, 63USLByBGNM@03:49, 63USLByBGNM@03:57) | single-source | yes |
| 42 | Losslessly compress each export (metadata and unreferenced data stripped) before uploading, and re-measure after the platform converts it. | Jesse Showalter | CLAIM(63USLByBGNM@04:26, 63USLByBGNM@05:00, 63USLByBGNM@05:24) | single-source | yes |
| 43 | Decide per video whether it is hosted or embedded: a short looping clip of a person talking earns the weight, long-form content belongs on a third-party host so the page stays fast. | Jesse Showalter | CLAIM(63USLByBGNM@06:12, 63USLByBGNM@06:30, 63USLByBGNM@06:46) | single-source | yes |
| 44 | Export video at the size and compression the slot needs and run it through a compressor; an untouched high-resolution master is the slowest asset on the page. | Jesse Showalter | CLAIM(63USLByBGNM@07:08, 63USLByBGNM@07:21, 63USLByBGNM@07:34) | single-source | yes |
| 45 | Count the dynamic elements (tickers, slideshows, carousels, iframe embeds, 3D scenes) as a budget: each one costs bandwidth, so cut the count instead of the quality. | Jesse Showalter | CLAIM(63USLByBGNM@08:07, 63USLByBGNM@08:15, 63USLByBGNM@08:36) | single-source | yes |
| 46 | Treat blur and heavy drop shadows as performance decisions: keep them selective, and respect the browser's limits the way print design respects paper. | Jesse Showalter | CLAIM(63USLByBGNM@08:52, 63USLByBGNM@09:12, 63USLByBGNM@09:31) | single-source | yes |
| 47 | Reduce the render tree: split an endless one-page site into real pages, use fewer animated elements, and flatten stacks that only exist to group things visually. | Jesse Showalter | CLAIM(63USLByBGNM@10:41, 63USLByBGNM@11:07, 63USLByBGNM@11:25) | single-source | yes |
| 48 | Depth in a layers panel understates cost: a visible list of about ten layers can still compile to more than a thousand rendered nodes, so inspect nesting, not layer count. | Jesse Showalter | CLAIM(63USLByBGNM@11:56, 63USLByBGNM@12:01) | single-source | yes |
| 49 | Publish to a staging URL and walk the live site before calling the build done; the preview and the published page are the acceptance surface. | Jesse Showalter | CLAIM(y4Rv-vf01LY@11:07, y4Rv-vf01LY@11:13, 1xAfVDiX1ps@34:06) | consensus | yes |

## Looks like / does not (good vs bad pairs)

| # | looks like (good) | does not (bad) | why | citation |
|---|-------------------|----------------|-----|----------|
| 1 | A pasted design that arrives with responsive behavior, working buttons and named classes. | A pasted design that arrives as fixed or absolutely placed boxes. | The exporter can only transfer layout logic that was authored as layout logic. | CLAIM(xHXqj006Q2k@00:44, xHXqj006Q2k@02:49) |
| 2 | A hero whose text sits in a wrapper with center alignment and cannot be moved. | A hero where an element is dragged to a spot that happens to look right. | Free placement looks right at one width and breaks at every other. | CLAIM(P5H7zs0RsUM@07:37, P5H7zs0RsUM@08:14) |
| 3 | Content centered in a fixed container with equal side tracks on a wide screen. | Content pinned to the full canvas width of the desktop artboard. | The container is what makes one design work across screen widths. | CLAIM(BNYLKuIlazA@01:54, xHXqj006Q2k@00:26) |
| 4 | One grid class shared by every aligned group, with a combo class for the single exception. | Three near-identical grids styled separately. | Separate copies must be re-tuned three times per breakpoint. | CLAIM(WLDfFqnqbxI@03:38, WLDfFqnqbxI@04:40) |
| 5 | A card whose corner radius clips its own image via overflow hidden. | A rounded card whose square image still bleeds past the corners. | Radius applies to the container, the child image needs clipping to obey it. | CLAIM(WLDfFqnqbxI@11:34, WLDfFqnqbxI@11:49) |
| 6 | A button reused from one master with a hover variant. | Several hand-styled button copies with slightly different padding. | Copies drift; a master keeps the system consistent. | CLAIM(P5H7zs0RsUM@16:40, P5H7zs0RsUM@18:14) |
| 7 | Text aligned on a shared baseline after a deliberate margin nudge. | Text that looks aligned by box but sits high or low on the line. | Bounding boxes include descender space, so box alignment is not optical alignment. | CLAIM(WLDfFqnqbxI@08:25, WLDfFqnqbxI@09:00) |
| 8 | A heading that scales down smoothly with the window. | A heading fixed in pixels that overflows the narrow viewport. | Viewport sizing keeps a display line to one piece across widths. | CLAIM(WLDfFqnqbxI@07:23, WLDfFqnqbxI@07:35) |

## Decision tables (option A vs B -> pick when)

| Decision | Pick A when | Pick B when | citation |
|---|---|---|---|
| Hand-build the site vs import the design | Import: standard layout blocks and a well structured design file (the estimate is minutes rather than an hour). | Hand-build: first time on the platform, or a bespoke layout the exporter cannot express (sliders, custom interaction logic). | CLAIM(xHXqj006Q2k@06:32, xHXqj006Q2k@07:02, P5H7zs0RsUM@00:25) |
| One big grid vs several grouped grids | One grid: everything on the screen truly shares one column rhythm and no breakpoint work is expected. | Grouped grids under one parent: a bento or dashboard page that must restack per breakpoint. | CLAIM(WLDfFqnqbxI@01:37, WLDfFqnqbxI@14:47) |
| Pixels vs viewport units for type | Pixels: body and UI text that must stay legible at a floor size. | Viewport units: a single display headline that must fit one line at every width. | CLAIM(WLDfFqnqbxI@07:23, WLDfFqnqbxI@16:03) |
| Absolute positioning | Decoration and backdrops that must sit behind content. | Never for content; it is what makes an export unmaintainable. | CLAIM(BNYLKuIlazA@06:14, xHXqj006Q2k@02:49) |

## Anti-patterns (cited)

| # | anti-pattern | what breaks | citation |
|---|---|---|---|
| 1 | Designing with loose groups and hoping the exporter guesses the layout. | The transfer drops to fixed placement with no responsive behavior. | CLAIM(xHXqj006Q2k@02:25, xHXqj006Q2k@02:49) |
| 2 | Pasting into the builder before the fonts exist in the project. | Every text node needs its face re-assigned by hand. | CLAIM(xHXqj006Q2k@04:44) |
| 3 | Placing elements by eye in a canvas-style editor. | Nothing is anchored, so the first resize breaks the composition. | CLAIM(P5H7zs0RsUM@07:37) |
| 4 | Leaving one oversized image at natural size inside a grid cell. | It pushes following rows past the intended fold. | CLAIM(WLDfFqnqbxI@10:01) |
| 5 | Accepting the design file's type size without re-judging it in the browser. | A 18px design spec read as too large on the live page and had to come down to 16. | CLAIM(WLDfFqnqbxI@02:37) |
| 6 | Building a page with only desktop in mind and no per-breakpoint pass. | A dense bento grid stops holding together at tablet width until columns are re-spanned. | CLAIM(WLDfFqnqbxI@13:58, WLDfFqnqbxI@14:08) |

## Creator claims (unverified)

| # | claim | creator | citation |
|---|---|---|---|
| 1 | A structured Figma page transfers to the builder in minutes instead of the roughly hour the manual rebuild took. | Flux Academy | CLAIM(xHXqj006Q2k@06:32, xHXqj006Q2k@06:46) |
| 2 | The auto-layout-based transfer covers something like 80 to 90 percent of common layout blocks. | Flux Academy | CLAIM(xHXqj006Q2k@07:17) |

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

## Disagreements between creators (who says what, cited)

| # | topic | position A | position B | citations |
|---|---|---|---|---|
| 1 | Should the design be imported or rebuilt | Import a properly auto-laid-out file; the time saving is large and class names and styles come free. | Rebuild by hand for the first version so you understand the platform and can fix what the import leaves broken. | CLAIM(xHXqj006Q2k@06:32), CLAIM(P5H7zs0RsUM@00:25) |
| 2 | Does a fixed design spec translate directly to the live page | Not automatically: the 18px spec came down to 16 once it was rendered. | Text should keep the design's declared size unless the rendered result looks wrong. | CLAIM(WLDfFqnqbxI@02:37), CLAIM(P5H7zs0RsUM@08:42) |

## Suggested sub-skills (2-5 names, one line each, which law #s they own)

| sub-skill | owns |
|---|---|
| design-to-build-handoff | Prepare a design file so a builder can consume it: auto layout, containers, naming, fonts, sizing checks. Laws 1-8. |
| builder-layout-construction | Stacks, grids, wrappers, containers, overflow and baseline work inside Framer/Webflow. Laws 9-21. |
| components-tokens-variants | Component and variable discipline plus button and card construction. Laws 22-29. |
| build-motion-and-effects | Entrance animation sequencing, hover states and embedded 3D or video layers. Laws 25, 30-32. |
