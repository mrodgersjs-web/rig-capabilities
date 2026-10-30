# Builder brief (every site agent reads this first)

Mission (Mike, 2026-10-04 18:30): by 07:00 Denver Mon 2026-10-05 he wakes up to 10+ new client-mirrored offering
websites that look award-winning (imagery, animation, wow moments, 3D scroll), built from the images he pinned to
Pinterest and selling a solution to pains scraped through Social Fetch. They must look better than what you see on
motion-site galleries and Awwwards. Those are design aspirations, not an award or superiority guarantee. Process: `DESIGN-PROCESS.md` with seven executed phases and native per-offering Miro artifacts. Acceptance owner: canonical `jev-site-gate`, v2 evidence contract. The production `_tools/gate.py` remains an older, separately owned copy until coordinated migration.

Before visual work, require an actual client/project identity, client branding, raw source/run evidence, a source-supported solution and visually inspected Pinterest references in `offering.json`. Multiple distinct offerings for one client count; ten different companies are not required. RIG-branded offers and renamed clones do not count. Mike-named TransformFit may use private-project identity without an invented public URL. Mark proposed features as proposed and category evidence as category evidence.

Workspace: `/Users/rig128gb/Developer/rig-client-mirror-sites/`. Your site folder: `sites/<slug>/`. Inputs: `_inputs/pinterest/<board>/`.
Airtable row ids per site: `_gate/airtable-rows.json`. Only `gate.py` checks a row off.

## Hard rules
- PREVIEW deploys only (`npx -y vercel deploy --yes` from `sites/<slug>/app`). Never `--prod`, never a custom domain, never touch existing TransformFit/RIG production projects or repos. Do not `git push` anything.
- No Pinterest writes (no saving pins, no board edits). Reads and `_tools/pull_board.py` only.
- Social Fetch: use the Airtable STRAT tables first. Live calls max 30 credits per site, logged in demand.md. Never print the key.
- No invented numbers, prices, client names, logos or testimonials. Prices only from `pinterest_candidates.csv` price_basis. Unknown = leave it off the page.
- Never mention James Loehr, Jacob, Avis, or comp anywhere. Nothing outward: no emails, DMs, posts, form submissions.
- Do not write under `~/Desktop/Projects/firstmate/projects/`. Do not edit other agents' site folders.
- Dev server ports: use only your assigned range. Kill your servers when done.
- Open questions or decisions for Mike: one line to Aside session `SP4ikIin7S6GmLBw` via message_agent (source, item, who decides, your recommendation), then keep going on reversible work.
- If a tool is dead (bash, REPL, Vercel auth, Lighthouse), say `[blocked]` with the exact error. Never fake a capture or a score.

## Quality bar (what "award-winning" means here)
- A full-bleed, image-led hero built from the board's strongest pins (or original imagery in that style), with cinematic type.
- A scroll story: pinned sections, scrubbed transforms, parallax depth (GSAP ScrollTrigger + Lenis are fine).
- One real 3D scrolling moment (WebGL or genuine CSS 3D depth/rotation) that changes with actual scroll position on desktop and mobile. Hold pointer/control state fixed to isolate the scroll response; pointer effects are supplemental evidence. A canvas is not mandatory.
- One wow section a visitor would screenshot. Restraint everywhere else (TASTE.md T1-T6).
- Looks like the buyer's world (mirror their category's best sites), sells the buyer's own words back to them.
- Fast: Lighthouse mobile perf >= 80, a11y >= 90; reduced-motion fallback; CTA usable in <1s.

## Done = for each of your sites
Use independently captured browser interactions, actual Lighthouse JSON, decoded desktop/mobile PNGs, ordered native Miro execution artifacts and structured independent critique. Read `../../jev-site-gate/references/EVIDENCE-V2.md`. Production trust is pending; supplied or builder-generated keys cannot grant acceptance. Do not enroll a new signer. Preview deployment, source spend and Airtable writes still need their own scoped authorization.

Report the honest current verdict, reasons and attempted fixes, preview URL, source/build/capture hashes, Jev decisions, review findings and the actual runtime identity. Keep pending acceptance explicit. Never mark a row Done from builder-only evidence or a human-readable score.
