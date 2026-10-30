# RIG client-mirror site process (v2 evidence repair candidate, 2026-10-04)

One offering = one client-branded site = one folder `sites/<slug>/`. A named actual client or directly user-named private project, such as TransformFit, is required. Several distinct source-supported offerings may belong to the same client. RIG-branded offers cannot count.

The current acceptance owner is canonical `jev-site-gate`. Read `../../jev-site-gate/references/EVIDENCE-V2.md` before execution. It supersedes the v1 evidence shortcuts below: Markdown presence, source regex, copied Lighthouse values, image size and `SCORE:` prose never establish completion. Every phase needs ordered native Miro item evidence and bound executed artifacts. Production trust is pending; no caller-generated signer can grant acceptance. Coordinate production propagation with its active writer.
Phase model: the 7-phase Double Black Box from `~/Developer/ux-design-scraper` `src/shared/workflow-constants.ts`
(Discover > Define > Gate > Diverge > Develop > Deliver > Measure), cross-walked to the Preface Studios board in Miro
(`https://miro.com/app/board/uXjVEez017g=/`: Contact, Discovery, Content, UI/UX, Coding, Launch, Support).
Taste law: `~/Developer/transformfit-flutter/design/TASTE.md` (T1-T6). Landing bar: `~/Developer/transform-fit-launch/docs/design/LANDING_PAGE_60_POINT_SCORING_RUBRIC.md`.
Acceptance: canonical `jev-site-gate/scripts/gate.py` plus its v2 evidence contract. The production `_tools/gate.py` is a separately owned, older runtime copy until coordinated migration.

"Client-mirrored" means: the site is built for the buyer, so it looks like what that buyer already trusts
(their own category's best sites), lifted by the images Mike pinned, and it sells a solution to pains the buyer
actually wrote (Social Fetch / STRAT tables). Mike's taste is not the target; the client's is.

## 1. Discover  -> discover.md, demand.md
- Read the board pins: `_inputs/pinterest/<board>/index.json` + images. Open every image. Write what each pin teaches (layout, type, color, motion, imagery). Pull more with `_tools/pull_board.py` if the board grew.
- Mirror set: find 3-5 real, live websites of the TARGET CLIENT category (the buyer's own industry leaders), screenshot their heroes from the served page. List URLs.
- Award set: 3+ motion-forward references (Awwwards SOTD, motionsites, godly.website) that match the board's mood. List URLs.
- demand.md: buyer pains from Airtable RIG Command Center (base app0aAXlSUFPbuTBL): `STRAT · Demand Screen` tbli1s5mwhZ7To7gz, `STRAT · Verified Stories` tblUaVHxqaiGtxd5m, `STRAT · Social Comments` tblPTqaduGtfmHvWH, `STRAT · Collected Comments` tblwcDWTMudQ2ehez, plus `~/Developer/strategy-studio-pro/2026-10-03-market-strategy-v2/` (pinterest_candidates.csv, opportunity_trees.csv, sources_and_assumptions.csv). Each pain line carries its record id. Social Fetch live calls only if the tables hold nothing for this buyer: max 30 credits per site, `x-api-key` from `~/.hermes/.env` SOCIALFETCH_API_KEY, host `api.socialfetch.dev`, log every call in demand.md.
## 2. Define  -> define.md, claims.md
- Buyer (one role/business type), top 3 pains with ids, the offer (from pinterest_candidates.csv price_basis; no invented prices), one-sentence promise, primary CTA text, section map, the named **wow moment** (section id), the 3D moment, the scroll story.
- claims.md: every number that will appear on the page with its source file path. If it has no source, it does not go on the page.
## 3. Gate  -> gate.md
- Run the brief through JEV before building: `python3 -c` with `_tools/jev.py` jev_noul on (a) "Does the promise address one of these pains?" (b) "Is the CTA a single concrete next step?" Record scores. Below 0.85: rewrite define.md and re-run.
## 4. Diverge  -> diverge.md (+ evidence/diverge-*.png)
- Three directions, each mapped to named pins and mirror sites. Render each as a quick hero mock on the served dev server and screenshot it. Pick one with a reason tied to the buyer, not to taste.
## 5. Develop  -> develop.md, app/
- Build in `sites/<slug>/app/`. Static Vite or plain HTML/JS is fine; Next.js only if needed. Libraries allowed: GSAP + ScrollTrigger, Lenis, three.js, Motion One. Assets: Pinterest images (local copies) used as inspiration and as imagery where they fit; generate original imagery when a pin is a UI screenshot of someone else's product (never pass off another brand's UI as ours).
- Must have: full-bleed hero (>=50% viewport) with `data-pinterest-source`, a scroll-driven story, one real 3D moment (three.js or CSS 3D) that reacts to scroll/pointer, a wow section, `prefers-reduced-motion` fallback, max 2 font families, accent in <=3 places per section, CTA usable within 1s (motion never blocks it). Follow the markup contract in `_tools/PROBE.md`.
- Banned: fake logos, testimonials, invented client names/stats, banned words (see gate), lorem, stock-icon rows. A supported actual client/project name is required for client branding.
## 6. Deliver  -> deliver.md
- `cd app && npx -y vercel deploy --yes` (PREVIEW only: never `--prod`, never alias a custom domain; that is Gate-D). Record the preview URL. Check it returns 200.
## 7. Measure  -> measure.md, critique.md, evidence/probe.json, evidence/gate-result.json
- Probe the served Vercel page (`_tools/PROBE.md`), Lighthouse mobile, screenshots 1440 + 390.
- An independent reviewer inspects actual desktop/mobile captures and records structured screenshot-bound findings, resolved blockers and retest artifacts in `evidence/critique.json`. Human-readable critique is commentary. No award or superiority guarantee.
- Gate: use the canonical owner with `--root <workspace> --verifier-key <existing-authorized-key>` after approved trust is established. No permanent signer or trust enrollment is authorized by this process. Only perform Airtable writes when separately scoped. Loop within the declared fix budget; FAIL must remain In progress with Done=false and reasons.
