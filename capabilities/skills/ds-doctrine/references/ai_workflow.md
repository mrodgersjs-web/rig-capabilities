# ai_workflow laws (Design Studio OS corpus)

Coverage: 22 videos read (uStjewbLoA0, h_CPuUpsiEg, qeqearWwBpg, EUPbdk972JI, a_mZ4Kp3lTM, IIXupZAGvDk, QKUnUrsDzk0, yO3Wr7DEWF0, XftHdIqqgNM, 5lDUy7JFNrg, yRBu2jU2d1w, bOXbC5HwpiM, oechHZEX8PM, xmL99KEycU0, eXQQxaS0CCA, Rkq_eDeGIMw, Iup1WlUyj9M, vHWRS-ZhsuY, EiIZBOu4MHk, jT5YdajTg6I, djSx_k0OKjU, SPemggbhoeo). Channels: flux-academy (5), adrien-ai-designer (5), grow-with-alex (3), jesse-showalter (3), designcourse (2), will-paterson (1), griffin-wooldridge (2), satori-graphics (1). Publish dates 2022-01-24 to 2026-06-22.

## Laws

### A. Agent-readable design files (how you set up the source file)

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 1 | Apply auto layout to every container before any AI tool reads the file; without it the tool rebuilds your layout as absolute positions with frozen pixel values. | flux-academy, designcourse, jesse-showalter | CLAIM(uStjewbLoA0@01:02, yO3Wr7DEWF0@01:30, eXQQxaS0CCA@06:52) | consensus | yes |
| 2 | Write the auto-layout requirement into the prompt as well as the file; when the instruction is absent the generator falls back to loose frames. | flux-academy | CLAIM(XftHdIqqgNM@02:22, qeqearWwBpg@12:27) | single-source | yes |
| 3 | Rename layers to describe content and position before handoff; arbitrary frame labels leave the agent with no semantics to read. | flux-academy, designcourse | CLAIM(uStjewbLoA0@01:39, yO3Wr7DEWF0@02:50) | consensus | yes |
| 4 | Bind colors, font families, type sizes and spacing numbers to named styles or variables so the connection passes design-system values instead of raw hex and pixel numbers. | flux-academy, designcourse | CLAIM(uStjewbLoA0@02:03, yO3Wr7DEWF0@02:33, XftHdIqqgNM@05:33) | consensus | yes |
| 5 | Name grid and repeated items by their row and column when order is load-bearing; unnamed cells get scrambled on import. | designcourse | CLAIM(yO3Wr7DEWF0@02:50) | single-source | no |
| 6 | Delete or hide decorative and stray layers before you paste a frame into a generator; leftover art complicates its reading of the structure. | flux-academy, designcourse | CLAIM(qeqearWwBpg@12:12, eXQQxaS0CCA@07:18) | consensus | yes |
| 7 | Bring decorative art back as an absolutely positioned layer behind content and pin its constraints to center so resizing does not distort it. | designcourse | CLAIM(eXQQxaS0CCA@08:28, eXQQxaS0CCA@09:01) | single-source | no |
| 8 | Keep component variants and properties organized; the agent mirrors your component architecture in the code it writes. | flux-academy | CLAIM(uStjewbLoA0@02:25) | single-source | yes |

### B. Briefs, context packs and prompt construction

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 9 | Never open with an empty prompt: seed the run with a component-library prompt, real reference screens, or a written requirements document. | adrien-ai-designer, jesse-showalter, flux-academy, griffin-wooldridge | CLAIM(a_mZ4Kp3lTM@00:54, EUPbdk972JI@03:00, qeqearWwBpg@12:12, vHWRS-ZhsuY@01:36, EiIZBOu4MHk@04:33) | consensus | yes |
| 10 | Drop a markdown context file into the project folder and name it in the prompt: design brief, animation best practices, or product architecture. Without it the output drifts off what the client asked for. | adrien-ai-designer, jesse-showalter | CLAIM(h_CPuUpsiEg@05:28, oechHZEX8PM@06:58, yRBu2jU2d1w@04:09) | consensus | yes |
| 11 | Fill the brief by pointing the agent at the empty brief file and asking it to interview you line by line. | adrien-ai-designer | CLAIM(oechHZEX8PM@02:11) | single-source | yes |
| 12 | Use a second chat model to draft the build prompt or the project guidelines file, then hand that text to the build agent. | adrien-ai-designer, jesse-showalter | CLAIM(h_CPuUpsiEg@06:10, yRBu2jU2d1w@05:00) | consensus | yes |
| 13 | Make the first prompt exhaustive: screen list, aesthetic, exact accent colors, frame dimensions, and required layout behaviors. First-prompt thoroughness sets the floor for the whole project. | flux-academy, jesse-showalter, griffin-wooldridge | CLAIM(XftHdIqqgNM@01:44, XftHdIqqgNM@02:36, yRBu2jU2d1w@02:15, vHWRS-ZhsuY@00:33, jT5YdajTg6I@11:38) | consensus | yes |
| 14 | Name the exact model or vendor the integration must use, twice, so the agent does not silently substitute another. | designcourse | CLAIM(eXQQxaS0CCA@10:03) | single-source | no |
| 15 | Spell out what the build must not create: for a prototype, forbid databases and login persistence, or order browser-local storage instead of a full backend. | designcourse, jesse-showalter | CLAIM(eXQQxaS0CCA@11:12, yRBu2jU2d1w@06:38) | consensus | no |
| 16 | Include a step-by-step flow spec when behavior spans screens and permissions, and say which platform it runs on. | designcourse | CLAIM(eXQQxaS0CCA@10:55, eXQQxaS0CCA@10:03) | single-source | no |
| 17 | On style-first generators, write the opening prompt heavy on content and light on styling: name the mood broadly and tune styling afterwards. | flux-academy | CLAIM(QKUnUrsDzk0@00:53, QKUnUrsDzk0@02:00) | single-source | yes |

### C. References and visual inputs

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 18 | Attach a real reference screen to the prompt and ask for its layout and styling to be matched; the same brief without a reference returns average output. | adrien-ai-designer, flux-academy, griffin-wooldridge | CLAIM(5lDUy7JFNrg@01:52, 5lDUy7JFNrg@02:03, XftHdIqqgNM@04:15, vHWRS-ZhsuY@05:05) | consensus | yes |
| 19 | Build video from paired first and last frames per clip, then animate each pair into a clip. | adrien-ai-designer | CLAIM(h_CPuUpsiEg@01:01, h_CPuUpsiEg@02:52) | single-source | yes |
| 20 | Give asset generators a brand kit (logo, palette, typeface, voice) instead of an open prompt; ungrounded image prompts come back off brand. | adrien-ai-designer | CLAIM(a_mZ4Kp3lTM@02:20, 5lDUy7JFNrg@03:14, EiIZBOu4MHk@05:25) | single-source | yes |
| 21 | Tell the asset generator where copy will sit so it reserves clear space in the composition. | adrien-ai-designer | CLAIM(a_mZ4Kp3lTM@02:45, 5lDUy7JFNrg@04:51) | single-source | yes |
| 22 | Feed your own drawn or vector artwork as the structure reference and let the model supply material and texture; you keep form control and skip 3D software. | will-paterson | CLAIM(Rkq_eDeGIMw@02:36, Rkq_eDeGIMw@04:27) | single-source | no |
| 23 | Raise structure strength and lower visual intensity when the reference form must survive; stack a second reference when you also need a material. | will-paterson | CLAIM(Rkq_eDeGIMw@02:48, Rkq_eDeGIMw@03:23) | single-source | no |
| 24 | Build composite elements (circular avatar, handle pair, verification badge) in a layout tool, export them flat, and hand that composite to the image model as an input. | grow-with-alex | CLAIM(IIXupZAGvDk@02:42, IIXupZAGvDk@03:28) | single-source | yes |
| 25 | Copy a proven, high-performing design or post as the style source and swap in your own subject and story. | grow-with-alex, adrien-ai-designer | CLAIM(IIXupZAGvDk@00:46, bOXbC5HwpiM@00:26, 5lDUy7JFNrg@01:00) | consensus | yes |
| 26 | Strip inherited logos, badges and watermarks from reference-driven generations before use. | grow-with-alex | CLAIM(IIXupZAGvDk@01:38) | single-source | yes |

### D. Iteration, verification and handoff

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 28 | Second prompt lists every defect you observed and adds an open clause letting the agent implement the functionality the design implies but never drew. | flux-academy | CLAIM(uStjewbLoA0@05:48, uStjewbLoA0@06:52) | single-source | yes |
| 29 | Re-inspect the build after every prompt: later passes that add function routinely break earlier spacing and styling. | flux-academy, designcourse | CLAIM(uStjewbLoA0@07:13, eXQQxaS0CCA@12:26) | consensus | yes |
| 30 | When output comes back broken, send a screenshot of the defect plus a concrete diagnosis of the cause, not a bare complaint. | designcourse | CLAIM(eXQQxaS0CCA@12:26, eXQQxaS0CCA@12:55) | single-source | no |
| 31 | Verify on the real delivery path: publish to a URL and run the flow on the target device instead of trusting the editor preview. | designcourse | CLAIM(eXQQxaS0CCA@13:45, eXQQxaS0CCA@17:14) | single-source | no |
| 32 | Publish a staging link and send it to stakeholders or developers so they can operate the thing rather than read static mockups. | jesse-showalter, adrien-ai-designer | CLAIM(EUPbdk972JI@05:04, yRBu2jU2d1w@10:00, h_CPuUpsiEg@07:57, EiIZBOu4MHk@01:47) | consensus | yes |
| 33 | Run parallel agent sessions while one works: separate windows for separate directions or screens. | adrien-ai-designer, flux-academy | CLAIM(oechHZEX8PM@04:00, XftHdIqqgNM@02:51) | consensus | yes |
| 34 | Generate two or three full directions from different references before committing, and send the set to the client to choose. | adrien-ai-designer | CLAIM(oechHZEX8PM@05:24, oechHZEX8PM@06:10) | single-source | yes |
| 35 | Once a direction is chosen, order every later screen to hold that exact visual direction. | adrien-ai-designer | CLAIM(oechHZEX8PM@06:27) | single-source | yes |
| 36 | Sequence animations by prompting an explicit delay value instead of hand-writing timing code. | flux-academy, designcourse | CLAIM(qeqearWwBpg@08:14, eXQQxaS0CCA@15:00) | consensus | yes |
| 37 | Keep motion subtle and short; heavy animation costs performance and pulls attention off the task. | adrien-ai-designer | CLAIM(5lDUy7JFNrg@05:47) | single-source | yes |
| 38 | Install a design or motion skill into the coding agent with its install command so aesthetics and animation conventions are enforced by the agent, not by you. | adrien-ai-designer, flux-academy, griffin-wooldridge | CLAIM(XftHdIqqgNM@03:46, 5lDUy7JFNrg@02:09, a_mZ4Kp3lTM@05:12, Iup1WlUyj9M@01:29, vHWRS-ZhsuY@02:05, jT5YdajTg6I@00:42) | consensus | yes |
| 39 | Keep the edits loop on version control: the agent edits, you approve, the agent pushes, you approve upstream, and only then does the live site change. | adrien-ai-designer | CLAIM(h_CPuUpsiEg@09:00) | single-source | yes |

### E. Systems, templates and batch production

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 40 | Derive the design system from the finished screens: palette styles, type scale and a reusable component page, then re-apply those styles across the UI. | flux-academy | CLAIM(XftHdIqqgNM@05:00, XftHdIqqgNM@06:01, jT5YdajTg6I@07:07) | single-source | yes |
| 41 | Copy generated screens that came out well back into the design file as editable layers and componentize them there. | jesse-showalter, adrien-ai-designer | CLAIM(yRBu2jU2d1w@09:07, EUPbdk972JI@05:37, EiIZBOu4MHk@08:23) | consensus | yes |
| 42 | Build one master template first, then duplicate it and swap only image and copy for every later asset. | grow-with-alex | CLAIM(bOXbC5HwpiM@02:08, xmL99KEycU0@05:46) | single-source | yes |
| 43 | Scale output by batching: LLM generates a list of items, a spreadsheet turns it into data, and the design tool's bulk create renders the whole set at once. | grow-with-alex | CLAIM(bOXbC5HwpiM@10:38, bOXbC5HwpiM@11:33) | single-source | yes |
| 44 | Run LLM copy through a simplifying rewriter before it enters a layout; pasted raw model prose reads heavy and repetitive. | grow-with-alex | CLAIM(xmL99KEycU0@03:18, xmL99KEycU0@04:37) | single-source | yes |
| 45 | Enhance or upscale sourced and generated images before compositing, and expect the enhancer to overshoot detail sometimes. | grow-with-alex, will-paterson | CLAIM(bOXbC5HwpiM@01:07, Rkq_eDeGIMw@05:55) | consensus | yes |
| 46 | Guarantee text legibility by darkening the image under it or laying a bottom gradient, since the photo then need not fill the frame. | grow-with-alex | CLAIM(bOXbC5HwpiM@01:41, bOXbC5HwpiM@11:53) | single-source | yes |
| 47 | Before any UI code, run a skill that forces a design pass on purpose, tone, constraints, and differentiation. | griffin-wooldridge | CLAIM(Iup1WlUyj9M@00:41) | single-source | yes |
| 48 | Write a ban list into that skill: Inter and Arial, purple gradients, and white cards with heavy corner radius. | griffin-wooldridge, flux-academy | CLAIM(Iup1WlUyj9M@01:02, Iup1WlUyj9M@01:15, vHWRS-ZhsuY@03:06, jT5YdajTg6I@03:07, jT5YdajTg6I@03:45) | consensus | yes |
| 49 | Hand design-to-code a file URL so it reads auto layout, type, color, and spacing from the source, then check the build against a screenshot of that frame. | griffin-wooldridge | CLAIM(Iup1WlUyj9M@01:58, Iup1WlUyj9M@02:44) | single-source | yes |
| 50 | Map generated UI onto the project's existing components instead of rebuilding buttons, inputs, and type from scratch. | griffin-wooldridge | CLAIM(Iup1WlUyj9M@02:36) | single-source | yes |
| 51 | When you are not pulling a live file, apply a packaged theme (palette plus header and body font pair) so slides, docs, and pages stay consistent. | griffin-wooldridge, flux-academy | CLAIM(Iup1WlUyj9M@03:19, Iup1WlUyj9M@04:00, jT5YdajTg6I@01:47) | consensus | yes |
| 52 | Fork a brand-guidelines skill and replace its tokens with your hex codes, font stacks, spacing, logo rules, and tone. | griffin-wooldridge | CLAIM(Iup1WlUyj9M@04:31, Iup1WlUyj9M@04:48) | single-source | yes |
| 53 | For posters and static graphics, write the visual rules (forms, color, composition) before rendering the image file. | griffin-wooldridge | CLAIM(Iup1WlUyj9M@05:52) | single-source | yes |
| 54 | Build a missing skill by stating the job, answering questions on edge cases and output shape, then revising against test prompts before you share the folder. | griffin-wooldridge, flux-academy | CLAIM(Iup1WlUyj9M@07:07, Iup1WlUyj9M@07:26, jT5YdajTg6I@19:03, jT5YdajTg6I@20:08) | consensus | yes |
| 55 | For a real product screen, the first prompt names user type, their primary goals, constraints such as screen size, data density, and platform, and a success checklist. Subjective adjectives are not a spec. | griffin-wooldridge | CLAIM(vHWRS-ZhsuY@01:18, vHWRS-ZhsuY@00:44) | single-source | yes |
| 56 | Put a markdown file in the project root that the agent reads at the start of every session, holding the brief or design principles, so you do not restate that context in each prompt. | griffin-wooldridge, flux-academy | CLAIM(vHWRS-ZhsuY@02:29, vHWRS-ZhsuY@03:59, jT5YdajTg6I@07:13) | consensus | yes |
| 57 | Name a component system, yours or a public one, before generation so the UI fits the product instead of reading as a one-off demo. | griffin-wooldridge, flux-academy | CLAIM(vHWRS-ZhsuY@04:08, vHWRS-ZhsuY@04:55, jT5YdajTg6I@16:56) | consensus | yes |
| 58 | When you want another visual system, order a component swap on the existing screen instead of opening a new project. | griffin-wooldridge | CLAIM(vHWRS-ZhsuY@04:38) | single-source | yes |
| 59 | Connect the tools that already hold the work (design file, meeting notes, tickets, docs) so the agent reads that source instead of a summary you retype. | griffin-wooldridge | CLAIM(vHWRS-ZhsuY@06:14, vHWRS-ZhsuY@06:36) | single-source | yes |
| 60 | Attach screenshots of shipped product flows as a visual target, and say it is not a copy job. Skip concept shots that were never built. | griffin-wooldridge | CLAIM(vHWRS-ZhsuY@05:45, vHWRS-ZhsuY@05:49) | single-source | yes |
| 61 | Before client generation, import a brand source (repo, design file, or logo and fonts) and confirm the extracted colors, type, logo, and spacing before you design from that system. | adrien-ai-designer | CLAIM(EiIZBOu4MHk@02:46, EiIZBOu4MHk@03:34) | single-source | yes |
| 62 | Fix leftovers either by direct property edits or by a comment pinned to the wrong region that names the system asset to use. Expect one such fix to update every repeated instance. | adrien-ai-designer | CLAIM(EiIZBOu4MHk@05:53, EiIZBOu4MHk@06:25, EiIZBOu4MHk@06:47) | single-source | yes |
| 63 | If you still need edit freedom, move the screen into the layout tool. If the design is already acceptable, hand the export command to the coding agent in the project folder and deploy from there. | adrien-ai-designer | CLAIM(EiIZBOu4MHk@07:11, EiIZBOu4MHk@08:40) | single-source | yes |
| 64 | Let the design app finish its own screenshot-and-fix pass before you start manual edits. | adrien-ai-designer | CLAIM(EiIZBOu4MHk@05:17) | single-source | yes |
| 65 | Invoke the skill by name for the prompt. Do not assume its description will fire it. | flux-academy | CLAIM(jT5YdajTg6I@04:40) | single-source | yes |
| 66 | When you call a skill, name how large the change should be and which of its libraries to use. An undirected skill call barely moves the design. | flux-academy | CLAIM(jT5YdajTg6I@12:14, jT5YdajTg6I@12:21) | single-source | yes |
| 67 | If a pass is visually loud (gradient text, heavy heading weights, emoji), run a quieting pass that lists each issue by severity and then fixes it. | flux-academy | CLAIM(jT5YdajTg6I@08:19, jT5YdajTg6I@08:42) | single-source | yes |
| 68 | Ban emoji, soft drop shadows, and side-tab accent borders in the skill and in your own review. They read as generated. | flux-academy | CLAIM(jT5YdajTg6I@03:56, jT5YdajTg6I@09:45) | single-source | yes |
| 69 | Near the finish, run an interface-guidelines audit and have the agent mark the defects on the page, not only in a list. | flux-academy | CLAIM(jT5YdajTg6I@14:48, jT5YdajTg6I@15:24) | single-source | yes |
| 70 | After install, edit the skill file to override defaults you reject, including font policy and styles you never want. A preset is not a lock. | flux-academy | CLAIM(jT5YdajTg6I@06:03, jT5YdajTg6I@13:58) | single-source | yes |
| 71 | Read the skill's banned-pattern gallery yourself so manual work avoids the same tells. | flux-academy | CLAIM(jT5YdajTg6I@09:36) | single-source | yes |
| 72 | Install a small set matched to the job. Do not load every design skill in a catalog onto one project. | flux-academy | CLAIM(jT5YdajTg6I@01:20, jT5YdajTg6I@16:12) | single-source | yes |
| 73 | A custom design skill must name product type first (dashboard, landing page, mobile) and infer the screen goal before it styles. | flux-academy | CLAIM(jT5YdajTg6I@19:21, jT5YdajTg6I@20:35) | single-source | yes |
| 74 | When the visual direction is already chosen, pick a previewed style skill instead of writing a long style essay. | flux-academy | CLAIM(jT5YdajTg6I@17:39, jT5YdajTg6I@18:05) | single-source | yes |
| 75 | A style skill should search its own library, then run a quality checklist after it writes code. | flux-academy | CLAIM(jT5YdajTg6I@10:22, jT5YdajTg6I@10:32) | single-source | yes |
| 76 | If the page has no motion, add it with a dedicated motion command instead of a full redesign. | flux-academy | CLAIM(jT5YdajTg6I@07:46) | single-source | yes |
| 77 | Drag panels out so each name is visible. Do not rely on memorizing icon-only tabs. | satori-graphics | CLAIM(djSx_k0OKjU@00:38, djSx_k0OKjU@00:45) | single-source | yes |
| 78 | On stacked art, select the object beneath with a modifier-click. Do not hunt the layers list for every overlap. | satori-graphics | CLAIM(djSx_k0OKjU@01:16, djSx_k0OKjU@01:27) | single-source | yes |
| 79 | A global appearance edit applies only to one shape or a group. Group first, then one edit copies onto every duplicate. | satori-graphics | CLAIM(djSx_k0OKjU@02:08, djSx_k0OKjU@02:35) | single-source | yes |
| 80 | Kern live text in place. Do not outline type just to move letters. | satori-graphics | CLAIM(djSx_k0OKjU@03:29, djSx_k0OKjU@03:40) | single-source | yes |
| 81 | Save a full appearance (color, gradient, effects, stroke) as a named style and build a project library. The defaults are not enough. | satori-graphics | CLAIM(djSx_k0OKjU@04:10, djSx_k0OKjU@04:26) | single-source | yes |
| 82 | Hide construction handles when you step back to review, so they do not obscure the work. | satori-graphics | CLAIM(djSx_k0OKjU@05:01, djSx_k0OKjU@05:07) | single-source | yes |
| 83 | Build a custom component inside the design tool so the code matches that tool's component model. Do not prompt in a separate chat and hope it drops in. | jesse-showalter | CLAIM(SPemggbhoeo@02:02, SPemggbhoeo@02:09) | single-source | yes |
| 84 | Keep the prompt history on the component. Select it and reopen the workshop so prior prompts and next steps are still there. | jesse-showalter | CLAIM(SPemggbhoeo@02:34, SPemggbhoeo@02:47) | single-source | yes |
| 85 | After insert, set position (fixed, anchor, relative width) and bind exposed properties to the project's color styles, then preview on the canvas. | jesse-showalter | CLAIM(SPemggbhoeo@03:32, SPemggbhoeo@04:06, SPemggbhoeo@03:50) | single-source | yes |
| 86 | When a shadow or transform must not clip, tell the prompt to include that overflow in the component's size. | jesse-showalter | CLAIM(SPemggbhoeo@04:52, SPemggbhoeo@04:56) | single-source | yes |
| 87 | For motion that should start only when its section is in view, prompt scroll position relative to that section, then confirm in preview that it does not run early. | jesse-showalter | CLAIM(SPemggbhoeo@06:36, SPemggbhoeo@07:33) | single-source | yes |
| 88 | Pick the model before a custom prompt. Keep the default for a straight component; switch to a more creative model for organic motion. | jesse-showalter | CLAIM(SPemggbhoeo@06:26, SPemggbhoeo@06:32) | single-source | yes |
| 89 | Start a known effect from the tool's prompt gallery, then customize. Do not invent the first version from a blank box when an example exists. | jesse-showalter | CLAIM(SPemggbhoeo@01:15, SPemggbhoeo@01:19) | single-source | yes |

## Looks like / does not (good vs bad pairs)

| # | looks like (good) | does not (bad) | why | citation |
|---|-------------------|----------------|-----|----------|
| 1 | A file where every section is a named auto-layout container | A file of loosely placed frames the agent re-measures as fixed pixels | Structure is the only layout information the agent gets | CLAIM(uStjewbLoA0@01:02) |
| 2 | Layer names that read as content and position | Layers still called by default frame numbers | Names supply the semantics the code copies | CLAIM(uStjewbLoA0@01:39) |
| 3 | Colors and type bound to named styles | Hex values and pixel numbers scattered through the file | Styles survive into code as a design system; numbers do not | CLAIM(uStjewbLoA0@02:03) |
| 4 | First prompt with screens, palette, frame size and layout rules named | First prompt that just asks for a nice app | Thoroughness of prompt one caps the quality floor | CLAIM(XftHdIqqgNM@02:36, vHWRS-ZhsuY@00:38) |
| 5 | Prompt plus a screenshot of a reference screen worth matching | Prompt alone, hoping for taste to appear | The model reproduces averages without a target | CLAIM(5lDUy7JFNrg@02:03, vHWRS-ZhsuY@05:52) |
| 6 | Custom brand assets generated from a kit | Stock photos dropped into the same layout | Assets are what removes the generated look | CLAIM(a_mZ4Kp3lTM@05:45) |
| 7 | Subtle entrance and hover motion | Big decorative animation everywhere | Heavy motion costs speed and attention | CLAIM(5lDUy7JFNrg@05:47) |
| 8 | A requirements document pasted whole into a fresh build | A frame pasted with no written intent | The document build came out cleaner and already mobile-correct | CLAIM(EUPbdk972JI@04:07) |
| 9 | A markdown guidelines file living inside the build project | Relying on the model's defaults each session | The file constrains every later choice the agent makes | CLAIM(yRBu2jU2d1w@04:09) |
| 10 | A screenshot of the defect plus a stated cause and fix | Sending it back with only a complaint | The agent fixes what you diagnose precisely | CLAIM(eXQQxaS0CCA@12:55) |
| 11 | A published URL tested on the device that will use it | Trusting the editor preview | Camera and layout paths only prove themselves on hardware | CLAIM(eXQQxaS0CCA@13:45) |
| 12 | A staging link a developer can click through | A static file plus an explanation of the intent | Interaction carries states and behavior the file cannot | CLAIM(yRBu2jU2d1w@10:00) |
| 13 | Three directions generated in parallel from three references | One direction refined endlessly before anyone has seen options | Choice beats polishing the first guess | CLAIM(oechHZEX8PM@04:00) |
| 14 | One master template duplicated per asset | Each asset rebuilt from scratch | Duplication keeps the series coherent and fast | CLAIM(bOXbC5HwpiM@02:08) |
| 15 | LLM copy run through a rewriter, then laid out | Raw model paragraphs pasted straight into the design | Raw prose is heavy and repetitive for readers | CLAIM(xmL99KEycU0@03:18) |
| 16 | Your own artwork as structure plus generated material | Fully generated form with no authored shape | Authoring the form is what keeps the result specific | CLAIM(Rkq_eDeGIMw@02:36) |
| 17 | A 20-item batch produced from one data file | Twenty separate generation runs typed by hand | Batch pipelines turn an hour into seconds | CLAIM(bOXbC5HwpiM@11:33) |
| 18 | Prototype data kept in local storage | Wiring a real database into a throwaway prototype | Persistence is scope, not a default | CLAIM(yRBu2jU2d1w@06:38) |
| 19 | A skill that names purpose, tone, and constraints, and bans generic type | A bare prompt that asks for a landing page | The skill decides design before code; a bare prompt returns the average look | CLAIM(Iup1WlUyj9M@00:41) |
| 20 | A design-file URL so layout tokens are read from the source | A screenshot handed over with a request to become code | The URL path reads auto layout and spacing; a picture guess comes back wrong | CLAIM(Iup1WlUyj9M@03:06) |
| 21 | Your own hex, type, and logo rules swapped into a brand skill | The vendor's sample brand left in the skill | You do not ship someone else's palette | CLAIM(Iup1WlUyj9M@04:23) |
| 22 | A screenshot of a shipped app flow used as a visual target | A polished concept that was never built, or an order to copy the reference | Shipped flows were tested; the agent should hit the look, not reproduce the file | CLAIM(vHWRS-ZhsuY@05:45) |
| 23 | Client generation locked to an imported brand system whose tokens you confirmed | A new project with no system selected | Without colors, type, and logo, the tool returns the same generic result as everyone else | CLAIM(EiIZBOu4MHk@05:25) |
| 24 | A comment pinned to the wrong logo, applied across every slide | Fixing one frame and leaving the copies stale | One named system asset updates the repeated instances | CLAIM(EiIZBOu4MHk@06:47) |
| 25 | The same prompt with the design skill invoked by name | The same prompt with no skill: purple gradients, a white field, emoji, misaligned cards | The ban list is what changes the first pass | CLAIM(jT5YdajTg6I@03:45) |
| 26 | A skill call that names how drastic the change is and which library to use | A skill call with no further direction | An undirected pass barely moves the design | CLAIM(jT5YdajTg6I@12:21) |
| 27 | Defects drawn on the page itself | A text list of accessibility issues | Annotation shows where and how often | CLAIM(jT5YdajTg6I@15:24) |
| 28 | Panels that show their names | Icon-only tabs you have to memorize | The name removes the hunt | CLAIM(djSx_k0OKjU@00:45) |
| 29 | Live text kerned in place | Type outlined just to move letters | Outlining kills later edits | CLAIM(djSx_k0OKjU@03:40) |
| 30 | One grouped edit updating every duplicate | Each copy edited by hand | Grouping is what makes the edit global | CLAIM(djSx_k0OKjU@02:35) |
| 31 | A component generated inside the design tool | Code prompted elsewhere and pasted in hope | In-tool generation matches the component model | CLAIM(SPemggbhoeo@02:05) |
| 32 | Prompt history still attached to the selected component | A one-shot chat you cannot find again | History stays on the component | CLAIM(SPemggbhoeo@02:47) |
| 33 | Exposed properties bound to project color styles, then previewed | The default color left on and trusted | Overrides are how it matches the project | CLAIM(SPemggbhoeo@04:14) |
| 34 | A path animation that waits until its section enters the viewport | Motion that runs against the whole page | The prompt named section-relative scroll | CLAIM(SPemggbhoeo@07:33) |

## Decision tables (option A vs B -> pick when)

| Choice | Pick A when | Pick B when | citation |
|--------|-------------|-------------|----------|
| A: coding agent plus design-file connection / B: in-tool prototype generator | You need production-grade code, a repo, and deploy control | You need a clickable prototype today for buy-in or developer context | CLAIM(uStjewbLoA0@02:50, EUPbdk972JI@01:29) |
| A: paste existing frames / B: paste a written requirements doc | You already have approved screens to convert | You have direction but no pixels yet, or the last frame build came back with layout damage | CLAIM(EUPbdk972JI@01:29, EUPbdk972JI@04:07) |
| A: browser-local storage in the prompt / B: real backend integration | It is a prototype or demo | It must survive logins and multi-user data for real | CLAIM(yRBu2jU2d1w@06:38, uStjewbLoA0@07:32) |
| A: parallel agent windows / B: one long session | Directions or screens are independent and can be compared | One coherent file must stay consistent across many dependent edits | CLAIM(oechHZEX8PM@04:00, XftHdIqqgNM@02:51) |
| A: reference screenshot in the prompt / B: written styling spec only | You can point at a layout worth matching | The direction is genuinely new and no reference exists | CLAIM(5lDUy7JFNrg@01:52, XftHdIqqgNM@01:44, vHWRS-ZhsuY@05:52) |
| A: paid all-in-one asset tool / B: free image tool plus manual cleanup | Brand consistency across many assets is the requirement | Budget is zero and you will clean each asset by hand | CLAIM(a_mZ4Kp3lTM@02:20, IIXupZAGvDk@01:57) |
| A: design-file connection for implement-from-URL / B: a brand-guidelines skill with your tokens | You already have a frame and need layout fidelity | You need on-brand UI faster and have no connected file | CLAIM(Iup1WlUyj9M@05:17) |
| A: hand the design to the coding agent and deploy / B: paste it into the layout tool and refine | The screen is already acceptable to build | You still need edit freedom the design app does not give | CLAIM(EiIZBOu4MHk@07:43, EiIZBOu4MHk@07:11) |
| A: guidelines audit near the end / B: a taste skill on the first pass | The layout is close and you need accessibility and UX defects | You still need a visual direction | CLAIM(jT5YdajTg6I@14:57, jT5YdajTg6I@02:33) |
| A: generate the component inside the design tool / B: prompt code elsewhere and paste | The widget must match that tool's component model and stay on the canvas | You are writing production code in a repo, not a design-tool widget | CLAIM(SPemggbhoeo@02:05) |

## Anti-patterns (cited)

- Starting from a blank canvas and prompting from scratch: it is slow, uninspiring and returns average output. CLAIM(a_mZ4Kp3lTM@00:54, EUPbdk972JI@00:16)
- Opening with subjective adjectives and no user, constraint, or success test. CLAIM(vHWRS-ZhsuY@00:44)
- Invoking a skill and telling it to run with no further direction. CLAIM(jT5YdajTg6I@12:14)
- Trusting a generated page on accessibility without a guidelines audit. CLAIM(jT5YdajTg6I@16:00)
- Installing every skill in a catalog onto one project. CLAIM(jT5YdajTg6I@01:20)
- Prompting for component code in another tool and hoping it matches the design tool. CLAIM(SPemggbhoeo@02:03)
- Handing over a file with no auto layout, no variables and no styles, then blaming the tool for pixel drift. CLAIM(yO3Wr7DEWF0@01:30)
- Forgetting to demand auto layout in the prompt itself, so the generator writes loose absolute frames. CLAIM(XftHdIqqgNM@02:22)
- Feeding screenshots only, without the file's typography, color and spacing data, and expecting accurate code. CLAIM(uStjewbLoA0@04:11, Iup1WlUyj9M@03:06)
- Shipping stock photography in a generated layout and wondering why it reads generic. CLAIM(5lDUy7JFNrg@02:46)
- Pasting model-written copy straight into a layout without editing it. CLAIM(xmL99KEycU0@03:18)
- Adding large decorative animation, which hurts performance and distracts from the goal. CLAIM(5lDUy7JFNrg@05:47)
- Treating the editor preview as proof: layouts squash and device-only features never trigger there. CLAIM(eXQQxaS0CCA@12:00, eXQQxaS0CCA@13:45)
- Letting a prototype grow a real database and login stack it never needed. CLAIM(eXQQxaS0CCA@11:12)
- Assuming an in-tool prototype can be sent back into a design file without checking: one generation of that tool had no round trip at all. CLAIM(qeqearWwBpg@16:52)

## Creator claims (unverified)

- A three-clip scroll-animation site with deploy was built in about 30 minutes end to end. CLAIM(h_CPuUpsiEg@00:00)
- A branded animated dashboard can be built in under 10 minutes on the three-step workflow. CLAIM(a_mZ4Kp3lTM@00:15)
- Three complete design directions can be produced in about 3 minutes once the brief is filled. CLAIM(oechHZEX8PM@05:24)
- A full landing page can be generated from one prompt in roughly 30 seconds. CLAIM(QKUnUrsDzk0@02:26)
- The referenced image model was described as the best available at the time of recording. CLAIM(h_CPuUpsiEg@01:15)
- The 2024 image model release was described as far ahead of competitors in the creator's opinion. CLAIM(Rkq_eDeGIMw@00:13)
- Carousel replications were shown against reference posts reported at tens of thousands of likes. CLAIM(IIXupZAGvDk@05:16, IIXupZAGvDk@06:33)
- Generated mockups were stated to be commercially safe for client work because of the vendor's stock training data. CLAIM(Rkq_eDeGIMw@10:27)
- The design-file connection was described as the first tool that translates layouts to code accurately. CLAIM(yO3Wr7DEWF0@00:16)
- A 20-asset content batch is claimed to be producible in seconds once the template exists. CLAIM(bOXbC5HwpiM@11:33)
- One installed front-end design skill is claimed to move output from obviously generated to looking designed. CLAIM(Iup1WlUyj9M@01:29, jT5YdajTg6I@04:54)
- Four named web-design skills were claimed to cover 90% of project work. Front-end design was called the most popular designer skill. One third-party skill was claimed to ship 22 subcommands; another, eight tech stacks. One install was timed at about 10 seconds and one redesign at about 5 minutes. CLAIM(jT5YdajTg6I@16:12, jT5YdajTg6I@02:33, jT5YdajTg6I@07:38, jT5YdajTg6I@10:07, jT5YdajTg6I@07:31, jT5YdajTg6I@13:00)
- A reference library used for shipped UI shots was described as holding over 500,000 screenshots. CLAIM(vHWRS-ZhsuY@05:13)
- A brand-system setup inside the design app was claimed to save hours every week versus building the system by hand. CLAIM(EiIZBOu4MHk@00:32, EiIZBOu4MHk@03:59)
- Output from the same design app was called a large improvement versus generations from about six months earlier. CLAIM(EiIZBOu4MHk@04:18)
- A board tool for mapping projects and live client collaboration was described as used for three years, and as free with no time limit. CLAIM(djSx_k0OKjU@05:15, djSx_k0OKjU@05:40)

## Tool-specific (dated)

All rows describe tool builds as they existed at the video's publish date; verify before relying on them.

- 2025-06 (designcourse): the design-file connection was set up in two places: add the server URL in the code editor's MCP settings, and enable the dev-mode server inside the design tool's preferences. CLAIM(yO3Wr7DEWF0@01:19)
- 2026-04 (flux-academy): the same capability is installed from a connectors panel, choosing the listing described as the design-tool MCP server and authorizing the account; two similar listings exist. CLAIM(XftHdIqqgNM@01:11)
- 2026-03 (adrien-ai-designer): the coding agent runs inside a code editor, and MCP installation is done by a terminal command followed by a check of the MCP panel. CLAIM(oechHZEX8PM@00:27)
- 2025-09 (flux-academy): the in-tool prototyping generator offered a code-from-design entry on selected layers, split code/preview view, and converted elements into code layers that land in the document grid. CLAIM(qeqearWwBpg@00:58, qeqearWwBpg@04:02)
- 2025-09 (flux-academy): that generator had no path back into a design file, and non-default fonts did not preview or publish in its site product. CLAIM(qeqearWwBpg@09:13, qeqearWwBpg@16:52)
- 2025-10 and 2026-01 (jesse-showalter): the same tool had gained copy-out of the whole design as layers with auto layout, point-and-edit on elements, a per-project guidelines markdown file, and staging publishes. CLAIM(EUPbdk972JI@05:37, yRBu2jU2d1w@04:09)
- 2025-12 (designcourse): the prototyping generator defaulted to adding a hosted database, required an API key pasted manually when it forgot to ask, and published testable URLs for on-device checks. CLAIM(eXQQxaS0CCA@11:12, eXQQxaS0CCA@12:26, eXQQxaS0CCA@13:45)
- 2023-06 (flux-academy): the site builder's AI entry point was a start-with-AI button with a prompt box, theme shuffle, per-section themes, inline copy rewriting on text layers, and context carried across generated pages. CLAIM(QKUnUrsDzk0@00:32, QKUnUrsDzk0@04:06, QKUnUrsDzk0@05:43)
- 2024-05 (will-paterson): the image model offered style reference and structure reference slots with independent strength sliders, an enhance-detail option in the variations panel, and in-app whole-image generation in a beta editor. CLAIM(Rkq_eDeGIMw@02:20, Rkq_eDeGIMw@07:42, Rkq_eDeGIMw@09:15)
- 2025-09 to 2026-03 (adrien-ai-designer, grow-with-alex): image work ran through named model builds (a 2025 image-preview model in an AI studio, then a 2026 second-generation image model and a 2026 video model on generation platforms). CLAIM(IIXupZAGvDk@00:54, h_CPuUpsiEg@01:15, h_CPuUpsiEg@02:52)
- 2026 (adrien-ai-designer): agent capability was extended by pasting install commands for named design, front-end and animation skills, and one creator's brand-asset service was promoted as the asset source. CLAIM(5lDUy7JFNrg@02:09, a_mZ4Kp3lTM@05:12)
- 2024-2025 (grow-with-alex): layout finishing relied on one design platform's enhancer app, magic-expand, background removal, and bulk-create from a CSV upload. CLAIM(bOXbC5HwpiM@01:20, IIXupZAGvDk@03:52, bOXbC5HwpiM@11:21)
- 2026-03 (griffin-wooldridge): Claude skills named for designers were front-end design, a Figma implement skill that needs the Figma MCP enabled in Claude, a 10-theme package, a brand-guidelines skill that ships with the vendor's tokens, a canvas skill that writes a philosophy then exports PNG or PDF, and a skill creator that writes skill.md. Finished skills package as a .skill file whose description controls when they trigger. CLAIM(Iup1WlUyj9M@00:28, Iup1WlUyj9M@02:53, Iup1WlUyj9M@07:51, Iup1WlUyj9M@07:56)
- 2026-05 (griffin-wooldridge): Claude Code reads a project-root Claude.md at the start of every session; the init slash command generates that file. Starter systems named in the prompt were shadcn, Radix, and Tailwind. Reference shots came from Mobbin. MCP connections named were Figma, Granola, and Linear, with docs pulled from Notion; the Figma MCP was said to read components and styles and to design in the file. CLAIM(vHWRS-ZhsuY@02:29, vHWRS-ZhsuY@04:44, vHWRS-ZhsuY@04:14, vHWRS-ZhsuY@05:11, vHWRS-ZhsuY@06:14, vHWRS-ZhsuY@06:30)
- 2026-04 (adrien-ai-designer): Claude Design was a separate app at claude.ai, gated to Pro (stated around $20 a month) and described as running Opus 4.7. System import paths were GitHub, a local code upload, a Figma file, or fonts, logo, and assets. The Figma path was File, Save local copy, to a .fig, then drag in and attach frames. Present opened a live URL in a new tab. Export had no Figma option; the workaround was present, an HTML-to-design browser extension, copy, paste into a new Figma file. Handoff was Export, hand off to Claude Code, paste the command into a folder session, with permission prompts bypassed, then a Vercel connect and a custom domain. CLAIM(EiIZBOu4MHk@00:43, EiIZBOu4MHk@00:14, EiIZBOu4MHk@00:55, EiIZBOu4MHk@02:46, EiIZBOu4MHk@03:04, EiIZBOu4MHk@07:54, EiIZBOu4MHk@08:08, EiIZBOu4MHk@08:40, EiIZBOu4MHk@08:51, EiIZBOu4MHk@09:02)
- 2026-05 (flux-academy): Claude desktop skills lived under Customize, Skills. Install paths shown were a GitHub zip uploaded via plus, create skill, upload, with the toggle on, or a one-line install prompt. Invoke with a slash command. Official skills named for web design were theme factory, brand guidelines, web artifacts builder, and front-end design; canvas design shipped a fonts folder. Third-party skills demoed were Impeccable (subcommands including animate, colorize, audit, document, quieter, plus a slop-pattern tab), UI UX Pro Max, and Vercel Labs web design guidelines. Libraries named were UI skills, Type UI (visual previews), and MCP Market (agent skills, categories, design tools, then search). Create-with-Claude used the skill-creator interview. Edit path was the skill dropdown, edit with Claude, or a direct markdown edit. CLAIM(jT5YdajTg6I@01:27, jT5YdajTg6I@04:06, jT5YdajTg6I@04:24, jT5YdajTg6I@04:42, jT5YdajTg6I@02:10, jT5YdajTg6I@07:34, jT5YdajTg6I@09:30, jT5YdajTg6I@10:00, jT5YdajTg6I@14:15, jT5YdajTg6I@16:30, jT5YdajTg6I@17:37, jT5YdajTg6I@18:16, jT5YdajTg6I@19:00, jT5YdajTg6I@06:45)
- 2022-01 (satori-graphics): Illustrator workflow shown was drag panels out of the icon dock so names show; command or control-click with the selection tool selects the object beneath; shift-click on the color bar cycles CMYK, HSB, grayscale, and RGB; global edit after command or control-G; alt or option plus arrow keys kerns between characters without outlining; the graphic styles panel saves appearance and renames on double-click; command or control-H hides anchors. A sponsored board tool (caption: miller note / millinock / millennial) was pitched as a wall for ideas, references, and live client collaboration. CLAIM(djSx_k0OKjU@00:38, djSx_k0OKjU@01:16, djSx_k0OKjU@01:47, djSx_k0OKjU@02:15, djSx_k0OKjU@03:35, djSx_k0OKjU@04:04, djSx_k0OKjU@04:55, djSx_k0OKjU@05:30)
- 2025-05 (jesse-showalter): Framer Workshop opened with command or control-K, then the native workshop plugin, as a floating panel. Example prompts lived at framer.com/workshop and were copied back in. The component appeared on the canvas; full code sat under the code-components list. Reselecting the component and reopening Workshop kept prompt history and next steps. Overrides in the bottom-right bound colors to project styles and set radius, stroke width, and speed. Preview was the play control. He drew the path with the vector tools first, then asked Workshop to animate it. The caption names the models he switched as GBT4.1 and claw 3.7, the second called more creative. CLAIM(SPemggbhoeo@00:42, SPemggbhoeo@01:03, SPemggbhoeo@02:18, SPemggbhoeo@04:06, SPemggbhoeo@06:08, SPemggbhoeo@06:30)

## Disagreements between creators (who says what, cited)

- How specific the first prompt should be. Flux Academy (2026) tells you to be thorough: frame size, exact colors, explicit layout rules, because prompt one sets the foundation. CLAIM(XftHdIqqgNM@02:36) Flux Academy's own earlier Framer video (2023) says the opposite for its site generator: describe content richly, keep styling broad, and adjust style later. CLAIM(QKUnUrsDzk0@00:53) DesignCourse (2025) sits between them: the prompt need not be long if the file is well prepared. Griffin Wooldridge (2026-05) joins the thorough side for coding-agent UI: name user type, goals, constraints, and a success checklist, and do not rely on words like beautiful. CLAIM(vHWRS-ZhsuY@01:18) Resolution: specificity belongs where the tool cannot infer it; a structured file lets the prompt stay short, a blank canvas demands detail.
- Copy the reference, or only aim at it. Grow With Alex and Adrien treat a high-performing post as a style source you copy, then swap subject and story. CLAIM(IIXupZAGvDk@00:46, 5lDUy7JFNrg@01:00) Griffin Wooldridge (2026-05) says do not ask the agent to copy; attach a shipped flow as a visual target, and skip concept shots that were never built. CLAIM(vHWRS-ZhsuY@05:49, vHWRS-ZhsuY@05:45) Resolution: match structure and styling, strip inherited marks (law 26), and prefer shipped flows when the goal is product UI.
- Whether generated work can return to the design file. Flux Academy (2025-09) reports no route back from the prototyping generator to design layers. CLAIM(qeqearWwBpg@16:52) Jesse Showalter (2025-10, 2026-01) demonstrates copying the whole generated design out as editable layers. CLAIM(EUPbdk972JI@05:37, yRBu2jU2d1w@09:07) Adrien (2026-04) found no Figma export on Claude Design and used present-in-a-new-tab plus an HTML-to-design capture, then paste; the layers were editable. CLAIM(EiIZBOu4MHk@07:54, EiIZBOu4MHk@08:27) Treat as a dated capability change, not a contradiction.
- How often the coding agent must ask before it edits. Adrien's earlier site workflow keeps an approve-then-push loop before the live site changes. CLAIM(h_CPuUpsiEg@09:00) In the 2026-04 Claude Design handoff he tells you to bypass permission prompts so the agent is not interrupted during the local build. CLAIM(EiIZBOu4MHk@08:51) Resolution: bypass is a speed choice while you are watching a local build. It does not replace approval before a live push (law 39).
- Attach a design system or not. Jesse Showalter deliberately skips attaching a published design system on the first prototype run to get moving. CLAIM(yRBu2jU2d1w@02:06) Flux Academy instead generates the design system from the finished screens and applies it back. CLAIM(XftHdIqqgNM@05:00) Adrien (2026-04) skips the system for a throwaway interactive demo, then requires an imported system before client work, or every tool returns the same generic result. CLAIM(EiIZBOu4MHk@01:27, EiIZBOu4MHk@05:25) Resolution: skip the system only for a throwaway exploration; import and confirm tokens before any client generation.
- Who holds creative direction. Flux Academy frames the agent as a fast literal junior designer you brief and review. CLAIM(XftHdIqqgNM@07:29) Jesse Showalter frames the designer as a creative director whose thought work lives in the requirements doc. CLAIM(EUPbdk972JI@06:15) Adrien frames it as the end of design effort once research and architecture are done. CLAIM(oechHZEX8PM@07:31) Practically: the more the brief carries, the less the generation step decides.

## Suggested sub-skills

- agent-ready-figma-prep: turn any file into an agent-readable source (laws 1-8).
- ai-build-prompting: briefs, context files and prompt construction for build agents (laws 9-17, 55-60).
- reference-driven-visuals: references, brand kits and image-generation inputs (laws 18-27).
- ai-iteration-verification: defect loops, device testing and staging handoff (laws 28-39).
- template-batch-production: design systems, master templates and batch asset pipelines (laws 40-46).
- claude-skill-authoring: design-pass skills, ban lists, brand-token forks, explicit invoke, audits, and skill-file edits (laws 47-54, 65-76).
- design-app-handoff: import a system, confirm tokens, comment fixes, then layout-tool or code deploy (laws 61-64).
- vector-production-hygiene: named panels, select-beneath, grouped global edits, live kerning, graphic styles (laws 77-82).
- in-tool-code-components: generate inside the design tool, keep prompt history on the component, bind overrides, section-scoped motion (laws 83-89).
