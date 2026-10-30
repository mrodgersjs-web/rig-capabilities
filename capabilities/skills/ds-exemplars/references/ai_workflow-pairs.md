# ai_workflow: looks like / does not

Owning main skill: ds-ai-workflow. Every row paraphrases a good-versus-bad contrast a creator showed, cited to the moment. Use as calibration before judging a screen; a card is only reusable as a visual reference after Jev ui.design scores the good side above the bad side.

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
