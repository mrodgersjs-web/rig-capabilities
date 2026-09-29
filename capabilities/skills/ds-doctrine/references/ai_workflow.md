# ai_workflow laws (Design Studio OS corpus)

Coverage: 16 videos read (uStjewbLoA0, h_CPuUpsiEg, qeqearWwBpg, EUPbdk972JI, a_mZ4Kp3lTM, IIXupZAGvDk, QKUnUrsDzk0, yO3Wr7DEWF0, XftHdIqqgNM, 5lDUy7JFNrg, yRBu2jU2d1w, bOXbC5HwpiM, oechHZEX8PM, xmL99KEycU0, eXQQxaS0CCA, Rkq_eDeGIMw). Channels: flux-academy (4), adrien-ai-designer (4), grow-with-alex (3), jesse-showalter (2), designcourse (2), will-paterson (1). Publish dates 2023-06-15 to 2026-06-22.

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
| 9 | Never open with an empty prompt: seed the run with a component-library prompt, real reference screens, or a written requirements document. | adrien-ai-designer, jesse-showalter, flux-academy | CLAIM(a_mZ4Kp3lTM@00:54, EUPbdk972JI@03:00, qeqearWwBpg@12:12) | consensus | yes |
| 10 | Drop a markdown context file into the project folder and name it in the prompt: design brief, animation best practices, or product architecture. Without it the output drifts off what the client asked for. | adrien-ai-designer, jesse-showalter | CLAIM(h_CPuUpsiEg@05:28, oechHZEX8PM@06:58, yRBu2jU2d1w@04:09) | consensus | yes |
| 11 | Fill the brief by pointing the agent at the empty brief file and asking it to interview you line by line. | adrien-ai-designer | CLAIM(oechHZEX8PM@02:11) | single-source | yes |
| 12 | Use a second chat model to draft the build prompt or the project guidelines file, then hand that text to the build agent. | adrien-ai-designer, jesse-showalter | CLAIM(h_CPuUpsiEg@06:10, yRBu2jU2d1w@05:00) | consensus | yes |
| 13 | Make the first prompt exhaustive: screen list, aesthetic, exact accent colors, frame dimensions, and required layout behaviors. First-prompt thoroughness sets the floor for the whole project. | flux-academy, jesse-showalter | CLAIM(XftHdIqqgNM@01:44, XftHdIqqgNM@02:36, yRBu2jU2d1w@02:15) | consensus | yes |
| 14 | Name the exact model or vendor the integration must use, twice, so the agent does not silently substitute another. | designcourse | CLAIM(eXQQxaS0CCA@10:03) | single-source | no |
| 15 | Spell out what the build must not create: for a prototype, forbid databases and login persistence, or order browser-local storage instead of a full backend. | designcourse, jesse-showalter | CLAIM(eXQQxaS0CCA@11:12, yRBu2jU2d1w@06:38) | consensus | no |
| 16 | Include a step-by-step flow spec when behavior spans screens and permissions, and say which platform it runs on. | designcourse | CLAIM(eXQQxaS0CCA@10:55, eXQQxaS0CCA@10:03) | single-source | no |
| 17 | On style-first generators, write the opening prompt heavy on content and light on styling: name the mood broadly and tune styling afterwards. | flux-academy | CLAIM(QKUnUrsDzk0@00:53, QKUnUrsDzk0@02:00) | single-source | yes |

### C. References and visual inputs

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 18 | Attach a real reference screen to the prompt and ask for its layout and styling to be matched; the same brief without a reference returns average output. | adrien-ai-designer, flux-academy | CLAIM(5lDUy7JFNrg@01:52, 5lDUy7JFNrg@02:03, XftHdIqqgNM@04:15) | consensus | yes |
| 19 | Build video from paired first and last frames per clip, then animate each pair into a clip. | adrien-ai-designer | CLAIM(h_CPuUpsiEg@01:01, h_CPuUpsiEg@02:52) | single-source | yes |
| 20 | Give asset generators a brand kit (logo, palette, typeface, voice) instead of an open prompt; ungrounded image prompts come back off brand. | adrien-ai-designer | CLAIM(a_mZ4Kp3lTM@02:20, 5lDUy7JFNrg@03:14) | single-source | yes |
| 21 | Tell the asset generator where copy will sit so it reserves clear space in the composition. | adrien-ai-designer | CLAIM(a_mZ4Kp3lTM@02:45, 5lDUy7JFNrg@04:51) | single-source | yes |
| 22 | Feed your own drawn or vector artwork as the structure reference and let the model supply material and texture; you keep form control and skip 3D software. | will-paterson | CLAIM(Rkq_eDeGIMw@02:36, Rkq_eDeGIMw@04:27) | single-source | no |
| 23 | Raise structure strength and lower visual intensity when the reference form must survive; stack a second reference when you also need a material. | will-paterson | CLAIM(Rkq_eDeGIMw@02:48, Rkq_eDeGIMw@03:23) | single-source | no |
| 24 | Build composite elements (circular avatar, handle pair, verification badge) in a layout tool, export them flat, and hand that composite to the image model as an input. | grow-with-alex | CLAIM(IIXupZAGvDk@02:42, IIXupZAGvDk@03:28) | single-source | yes |
| 25 | Copy a proven, high-performing design or post as the style source and swap in your own subject and story. | grow-with-alex, adrien-ai-designer | CLAIM(IIXupZAGvDk@00:46, bOXbC5HwpiM@00:26, 5lDUy7JFNrg@01:00) | consensus | yes |
| 26 | Strip inherited logos, badges and watermarks from reference-driven generations before use. | grow-with-alex | CLAIM(IIXupZAGvDk@01:38) | single-source | yes |
| 27 | Expect generated text to misspell; regenerate with prompt variants and pick the strongest result rather than shipping the first. | grow-with-alex | CLAIM(IIXupZAGvDk@03:35) | single-source | yes |

### D. Iteration, verification and handoff

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 28 | Second prompt lists every defect you observed and adds an open clause letting the agent implement the functionality the design implies but never drew. | flux-academy | CLAIM(uStjewbLoA0@05:48, uStjewbLoA0@06:52) | single-source | yes |
| 29 | Re-inspect the build after every prompt: later passes that add function routinely break earlier spacing and styling. | flux-academy, designcourse | CLAIM(uStjewbLoA0@07:13, eXQQxaS0CCA@12:26) | consensus | yes |
| 30 | When output comes back broken, send a screenshot of the defect plus a concrete diagnosis of the cause, not a bare complaint. | designcourse | CLAIM(eXQQxaS0CCA@12:26, eXQQxaS0CCA@12:55) | single-source | no |
| 31 | Verify on the real delivery path: publish to a URL and run the flow on the target device instead of trusting the editor preview. | designcourse | CLAIM(eXQQxaS0CCA@13:45, eXQQxaS0CCA@17:14) | single-source | no |
| 32 | Publish a staging link and send it to stakeholders or developers so they can operate the thing rather than read static mockups. | jesse-showalter, adrien-ai-designer | CLAIM(EUPbdk972JI@05:04, yRBu2jU2d1w@10:00, h_CPuUpsiEg@07:57) | consensus | yes |
| 33 | Run parallel agent sessions while one works: separate windows for separate directions or screens. | adrien-ai-designer, flux-academy | CLAIM(oechHZEX8PM@04:00, XftHdIqqgNM@02:51) | consensus | yes |
| 34 | Generate two or three full directions from different references before committing, and send the set to the client to choose. | adrien-ai-designer | CLAIM(oechHZEX8PM@05:24, oechHZEX8PM@06:10) | single-source | yes |
| 35 | Once a direction is chosen, order every later screen to hold that exact visual direction. | adrien-ai-designer | CLAIM(oechHZEX8PM@06:27) | single-source | yes |
| 36 | Sequence animations by prompting an explicit delay value instead of hand-writing timing code. | flux-academy, designcourse | CLAIM(qeqearWwBpg@08:14, eXQQxaS0CCA@15:00) | consensus | yes |
| 37 | Keep motion subtle and short; heavy animation costs performance and pulls attention off the task. | adrien-ai-designer | CLAIM(5lDUy7JFNrg@05:47) | single-source | yes |
| 38 | Install a design or motion skill into the coding agent with its install command so aesthetics and animation conventions are enforced by the agent, not by you. | adrien-ai-designer, flux-academy | CLAIM(XftHdIqqgNM@03:46, 5lDUy7JFNrg@02:09, a_mZ4Kp3lTM@05:12) | consensus | yes |
| 39 | Keep the edits loop on version control: the agent edits, you approve, the agent pushes, you approve upstream, and only then does the live site change. | adrien-ai-designer | CLAIM(h_CPuUpsiEg@09:00) | single-source | yes |

### E. Systems, templates and batch production

| # | law | creators | citations | consensus/single | top-10 source? |
|---|-----|----------|-----------|------------------|----------------|
| 40 | Derive the design system from the finished screens: palette styles, type scale and a reusable component page, then re-apply those styles across the UI. | flux-academy | CLAIM(XftHdIqqgNM@05:00, XftHdIqqgNM@06:01) | single-source | yes |
| 41 | Copy generated screens that came out well back into the design file as editable layers and componentize them there. | jesse-showalter | CLAIM(yRBu2jU2d1w@09:07, EUPbdk972JI@05:37) | single-source | yes |
| 42 | Build one master template first, then duplicate it and swap only image and copy for every later asset. | grow-with-alex | CLAIM(bOXbC5HwpiM@02:08, xmL99KEycU0@05:46) | single-source | yes |
| 43 | Scale output by batching: LLM generates a list of items, a spreadsheet turns it into data, and the design tool's bulk create renders the whole set at once. | grow-with-alex | CLAIM(bOXbC5HwpiM@10:38, bOXbC5HwpiM@11:33) | single-source | yes |
| 44 | Run LLM copy through a simplifying rewriter before it enters a layout; pasted raw model prose reads heavy and repetitive. | grow-with-alex | CLAIM(xmL99KEycU0@03:18, xmL99KEycU0@04:37) | single-source | yes |
| 45 | Enhance or upscale sourced and generated images before compositing, and expect the enhancer to overshoot detail sometimes. | grow-with-alex, will-paterson | CLAIM(bOXbC5HwpiM@01:07, Rkq_eDeGIMw@05:55) | consensus | yes |
| 46 | Guarantee text legibility by darkening the image under it or laying a bottom gradient, since the photo then need not fill the frame. | grow-with-alex | CLAIM(bOXbC5HwpiM@01:41, bOXbC5HwpiM@11:53) | single-source | yes |

## Looks like / does not (good vs bad pairs)

| # | looks like (good) | does not (bad) | why | citation |
|---|-------------------|----------------|-----|----------|
| 1 | A file where every section is a named auto-layout container | A file of loosely placed frames the agent re-measures as fixed pixels | Structure is the only layout information the agent gets | CLAIM(uStjewbLoA0@01:02) |
| 2 | Layer names that read as content and position | Layers still called by default frame numbers | Names supply the semantics the code copies | CLAIM(uStjewbLoA0@01:39) |
| 3 | Colors and type bound to named styles | Hex values and pixel numbers scattered through the file | Styles survive into code as a design system; numbers do not | CLAIM(uStjewbLoA0@02:03) |
| 4 | First prompt with screens, palette, frame size and layout rules named | First prompt that just asks for a nice app | Thoroughness of prompt one caps the quality floor | CLAIM(XftHdIqqgNM@02:36) |
| 5 | Prompt plus a screenshot of a reference screen worth matching | Prompt alone, hoping for taste to appear | The model reproduces averages without a target | CLAIM(5lDUy7JFNrg@02:03) |
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

## Decision tables (option A vs B -> pick when)

| Choice | Pick A when | Pick B when | citation |
|--------|-------------|-------------|----------|
| A: coding agent plus design-file connection / B: in-tool prototype generator | You need production-grade code, a repo, and deploy control | You need a clickable prototype today for buy-in or developer context | CLAIM(uStjewbLoA0@02:50, EUPbdk972JI@01:29) |
| A: paste existing frames / B: paste a written requirements doc | You already have approved screens to convert | You have direction but no pixels yet, or the last frame build came back with layout damage | CLAIM(EUPbdk972JI@01:29, EUPbdk972JI@04:07) |
| A: browser-local storage in the prompt / B: real backend integration | It is a prototype or demo | It must survive logins and multi-user data for real | CLAIM(yRBu2jU2d1w@06:38, uStjewbLoA0@07:32) |
| A: parallel agent windows / B: one long session | Directions or screens are independent and can be compared | One coherent file must stay consistent across many dependent edits | CLAIM(oechHZEX8PM@04:00, XftHdIqqgNM@02:51) |
| A: reference screenshot in the prompt / B: written styling spec only | You can point at a layout worth matching | The direction is genuinely new and no reference exists | CLAIM(5lDUy7JFNrg@01:52, XftHdIqqgNM@01:44) |
| A: paid all-in-one asset tool / B: free image tool plus manual cleanup | Brand consistency across many assets is the requirement | Budget is zero and you will clean each asset by hand | CLAIM(a_mZ4Kp3lTM@02:20, IIXupZAGvDk@01:57) |

## Anti-patterns (cited)

- Starting from a blank canvas and prompting from scratch: it is slow, uninspiring and returns average output. CLAIM(a_mZ4Kp3lTM@00:54, EUPbdk972JI@00:16)
- Handing over a file with no auto layout, no variables and no styles, then blaming the tool for pixel drift. CLAIM(yO3Wr7DEWF0@01:30)
- Forgetting to demand auto layout in the prompt itself, so the generator writes loose absolute frames. CLAIM(XftHdIqqgNM@02:22)
- Feeding screenshots only, without the file's typography, color and spacing data, and expecting accurate code. CLAIM(uStjewbLoA0@04:11)
- Shipping stock photography in a generated layout and wondering why it reads generic. CLAIM(5lDUy7JFNrg@02:46)
- Pasting model-written copy straight into a layout without editing it. CLAIM(xmL99KEycU0@03:18)
- Adding large decorative animation, which hurts performance and distracts from the goal. CLAIM(5lDUy7JFNrg@05:47)
- Treating the editor preview as proof: layouts squash and device-only features never trigger there. CLAIM(eXQQxaS0CCA@12:00, eXQQxaS0CCA@13:45)
- Letting a prototype grow a real database and login stack it never needed. CLAIM(eXQQxaS0CCA@11:12)
- Accepting the first generation when text inside images comes back misspelled. CLAIM(IIXupZAGvDk@03:35)
- Assuming an in-tool prototype can be sent back into a design file without checking: one generation of that tool had no round trip at all. CLAIM(qeqearWwBpg@16:52)

## Creator claims (unverified)

- A three-clip scroll-animation site with deploy was built in about 30 minutes end to end. CLAIM(h_CPuUpsiEg@00:00)
- A branded animated dashboard can be built in under 10 minutes on the three-step workflow. CLAIM(a_mZ4Kp3lTM@00:15)
- Three complete design directions can be produced in about 3 minutes once the brief is filled. CLAIM(oechHZEX8PM@05:24)
- A three-screen first draft takes about 15 minutes through the design-file connection. CLAIM(XftHdIqqgNM@04:50)
- A full landing page can be generated from one prompt in roughly 30 seconds. CLAIM(QKUnUrsDzk0@02:26)
- The referenced image model was described as the best available at the time of recording. CLAIM(h_CPuUpsiEg@01:15)
- The 2024 image model release was described as far ahead of competitors in the creator's opinion. CLAIM(Rkq_eDeGIMw@00:13)
- A free-ebook funnel was presented as the creator's plan to make $100,000 in a calendar year. CLAIM(xmL99KEycU0@00:00)
- Carousel replications were shown against reference posts reported at tens of thousands of likes. CLAIM(IIXupZAGvDk@05:16, IIXupZAGvDk@06:33)
- Generated mockups were stated to be commercially safe for client work because of the vendor's stock training data. CLAIM(Rkq_eDeGIMw@10:27)
- The design-file connection was described as the first tool that translates layouts to code accurately. CLAIM(yO3Wr7DEWF0@00:16)
- A 20-asset content batch is claimed to be producible in seconds once the template exists. CLAIM(bOXbC5HwpiM@11:33)

## Tool-specific (dated)

All rows describe tool builds as they existed at the video's publish date; verify before relying on them.

- 2025-06 (designcourse): the design-file connection was set up in two places: add the server URL in the code editor's MCP settings, and enable the dev-mode server inside the design tool's preferences. CLAIM(yO3Wr7DEWF0@00:22)
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

## Disagreements between creators (who says what, cited)

- How specific the first prompt should be. Flux Academy (2026) tells you to be thorough: frame size, exact colors, explicit layout rules, because prompt one sets the foundation. CLAIM(XftHdIqqgNM@02:36) Flux Academy's own earlier Framer video (2023) says the opposite for its site generator: describe content richly, keep styling broad, and adjust style later. CLAIM(QKUnUrsDzk0@00:53) DesignCourse (2025) sits between them: the prompt need not be long if the file is well prepared. CLAIM(yO3Wr7DEWF0@04:04) Resolution: specificity belongs where the tool cannot infer it; a structured file lets the prompt stay short, a blank canvas demands detail.
- Whether generated work can return to the design file. Flux Academy (2025-09) reports no route back from the prototyping generator to design layers. CLAIM(qeqearWwBpg@16:52) Jesse Showalter (2025-10, 2026-01) demonstrates copying the whole generated design out as editable layers. CLAIM(EUPbdk972JI@05:37, yRBu2jU2d1w@09:07) Treat as a dated capability change, not a contradiction.
- Attach a design system or not. Jesse Showalter deliberately skips attaching a published design system on the first prototype run to get moving. CLAIM(yRBu2jU2d1w@02:06) Flux Academy instead generates the design system from the finished screens and applies it back. CLAIM(XftHdIqqgNM@05:00) Both agree the system matters; they disagree on when to introduce it.
- Who holds creative direction. Flux Academy frames the agent as a fast literal junior designer you brief and review. CLAIM(XftHdIqqgNM@07:29) Jesse Showalter frames the designer as a creative director whose thought work lives in the requirements doc. CLAIM(EUPbdk972JI@06:15) Adrien frames it as the end of design effort once research and architecture are done. CLAIM(oechHZEX8PM@07:31) Practically: the more the brief carries, the less the generation step decides.

## Suggested sub-skills

- agent-ready-figma-prep: turn any file into an agent-readable source (laws 1-8).
- ai-build-prompting: briefs, context files and prompt construction for build agents (laws 9-17).
- reference-driven-visuals: references, brand kits and image-generation inputs (laws 18-27).
- ai-iteration-verification: defect loops, device testing and staging handoff (laws 28-39).
- template-batch-production: design systems, master templates and batch asset pipelines (laws 40-46).
