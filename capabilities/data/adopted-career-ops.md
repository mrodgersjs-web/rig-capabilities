# PROVENANCE — career-ops-hq/career-ops

- Upstream: https://github.com/career-ops-hq/career-ops @ ef9006f (2026-10-29), v1.38.0, 78,676 stars
- License: MIT (LICENSE file read)
- Adopted: 2026-10-29, shallow clone, 74 MB
- Load test: `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install` → 7 packages, then `node doctor.mjs` → **green on the machine checks** (Node 26.5.0 ≥ 22.13, deps installed, CLI skill entrypoints real, Playwright chromium present, Playwright MCP configured for claude, scan extractor mcp). 4 user files missing: `cv.md`, `config/profile.yml`, `modes/_profile.md`, `portals.yml`.
- Verdict: **adopted as the RIG Jobs scoring/tailoring engine.** Not a new ledger: RIG Jobs on :3211 (`jf_roles` 190 in queue, 613 Gmail-confirmed applications, 18 interviews) stays the record of what was applied; career-ops reads a job, returns fit 1-5 + tailored artifacts, and stops. Its own README makes Mike's gate for him: "You press Submit."
- Model routing: supports `OPENAI_BASE_URL` (docs/RUNNING_ON_A_BUDGET.md) → point at the local router :18811 for evals; the paid-API path stays off until Mike says otherwise.
- `cv.md` filled 2026-10-29 18:4x MDT **from the Mike working draft** `~/.rig/live/aside-work/resume-artifacts/r_q8z4jgd3/fc5beac…-WORKING-DRAFT.docx` (2026-10-28 12:50), whose own banner reads "WORKING DRAFT - UNCONFIRMED - DO NOT SUBMIT". The five `[EXACT ROLE AND DATES TO CONFIRM]` items are deliberately left out of cv.md. Filling the file makes the engine able to score; it does not make the content approved.
- Proof it scores (same hand-written Director-of-AI-Ops JD, local router sglang qwen3.8-flash, :18811, $0.0000): empty cv.md → **2.5/5**; filled from the working draft → **4.3/5**, archetype "AI Transformation Lead + Technical AI PM (hybrid)", legitimacy "Proceed with Caution". The 1.8-point swing is the CV being read, and the Caution flag is the unconfirmed-draft state, which is the correct behavior.
- Do not run `npx @santifer/career-ops init` until the install shape is decided: it writes into `~/.claude`, which is shared with Aside's own skill surface.
