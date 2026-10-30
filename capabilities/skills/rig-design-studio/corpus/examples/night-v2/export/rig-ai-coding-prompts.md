# RIG AI-CODING PROMPT BUNDLE — Iterate the Loehr HR-group landing page (JEV-audit-driven)

## Board brief (read this first)
You are implementing work tracked on a Double Diamond design board: 16 artifacts
(4 Discover · 4 Define · 4 Develop · 4 Deliver), 20 dependency links.
Each artifact below carries its own task, its place in the board, and its deviation budget.
Treat the design system section of each prompt as REQUIRED. Where artifacts conflict, prefer the
later phase (Deliver over Develop over Define over Discover) and flag the conflict instead of guessing.

## Board map
### Discover — What is the real human problem?
- c1 · research question · approved · dev 0: Where did the JEV audit leave the page, honestly?
- c2 · research question · approved · dev 0: Which sections already carry evidence the buyer trusts?
- c3 · persona · in-review · dev +1: Who is the reader the audit could not score well — and why?
- c4 · research question · approved · dev 0: What do the demand-thread pain numbers say?

### Define — What are we actually solving?
- c5 · HMW · approved · dev 0: HMW lift named_pain_lead (0.73) to top-of-page strength?
- c6 · HMW · approved · dev +1: HMW hold diagnostic_wedge (0.69) without sales pressure?
- c7 · HMW · in-review · dev +2: HMW let the pricing page carry the qualifying burden?
- c8 · HMW · in-review · dev 0: HMW close the accessible-apply-form gap on #book?

### Develop — What could the answer look like?
- c9 · variant sketch note · in-review · dev +1: Variant A — #hero named-pain spine rewrite
- c10 · variant sketch note · approved · dev 0: Variant B — #sequence year-in-the-room timeline
- c11 · variant sketch note · in-review · dev +2: Variant C — #members bring/take ledger with pain numbers
- c12 · variant sketch note · draft · dev +5: Variant D — #pricing fee-sheet decode table

### Deliver — What ships, and how is it built?
- c13 · dev handoff · approved · dev 0: Dev handoff — #hero + #sequence spine (Variants A, B)
- c14 · dev handoff · in-review · dev 0: Dev handoff — accessible #book apply form (c8)
- c15 · dev handoff · draft · dev +5: Dev handoff — #pricing clarity block (Variant D, flagged)
- c16 · dev handoff · in-review · dev +1: Dev handoff — this board exported as a coding bundle

## Dependency links
c1 → c5
c1 → c6
c2 → c6
c2 → c7
c3 → c7
c4 → c5
c4 → c11
c2 → c8
c5 → c9
c5 → c10
c6 → c11
c7 → c12
c8 → c14
c9 → c13
c10 → c13
c11 → c15
c12 → c15
c13 → c16
c14 → c16
c15 → c16

## Design system (MASTER-CREATIVE-PROMPT v3.0 — REQUIRED)
- --void #FAF7F2 — page background — warm ivory [light]
- --cream #F5F0E8 — card background — warm cream [light]
- --warm #EDE7DC — hover/elevated — warm sand [light]
- --gold #B8860B — primary accent — dark goldenrod [light]
- --gold-h #D4A017 — hover accent — brighter gold [light]
- --ink #14110D — primary text — warm near-black [light]
- --void #050810 — page background — deep void [dark]
- --mid #111827 — card background — dark blue-gray [dark]
- --gold #D4A017 — primary accent — brighter gold [dark]
- --t1 #F5E6C8 — primary text — warm ivory [dark]
- --success #2D7A2D — production ROI, positive results [functional]
- --energy #E65C00 — urgency, attention, executive [functional]
- --loss #C62828 — waste, pilot trap, negative [functional]
- --trust #1A5276 — trust signals, used sparingly [functional]
- Display: Cormorant Garamond 300 · clamp(2.5rem,7vw,5.5rem) · -0.03em
- Body / UI: Hanken Grotesk 300–500 · 0.9375rem · 1.47
- Data: JetBrains Mono 400–600 · uppercase · 0.1em–0.4em
- Radii: 12px standard · 16px large · 999px pills (max 16px)
- Shadows: sh-sm / sh-md / sh-lg / sh-gold (hover only)

## Anti-patterns (MUST NOT)
- Pure #000 or #FFF anywhere
- Blue primary (RIG is gold)
- Purple gradients
- Radius > 16px
- Emoji as UI elements
- Lorem ipsum / placeholder text
- Pixels not multiples of 4

## Acceptance
- Every artifact implemented with real copy — never placeholder text.
- Token values match exactly; deviation outside |d| <= 3 is flagged for human review, never shipped silently.
- Verifiable: build passes; visual check against app/.stitch/DESIGN.md.

---

# RIG AI-CODING PROMPT — Where did the JEV audit leave the page, honestly?

## Context
Board: "Iterate the Loehr HR-group landing page (JEV-audit-driven)"
Phase: Discover — What is the real human problem?
Artifact: research question · status: approved · deviation: 0 (within the deviation budget (|d| <= 3), no extra review required)
Downstream artifacts:
- HMW lift named_pain_lead (0.73) to top-of-page strength?
- HMW hold diagnostic_wedge (0.69) without sales pressure?

## Task
JEV-AUDIT.md: web.market FINAL 0.747 (baseline 0.649), no BLOCK at any point, but the 0.9 mean was never reached. Strongest fit items: boring_reliable_job 0.96, rulebook_accountability 0.88. Weakest: diagnostic_wedge (0.17→0.69 after the r4 rewrite), named_pain_lead (0.46→0.73). The iteration target is those two, not a redesign.

## Design system (MASTER-CREATIVE-PROMPT v3.0 — REQUIRED)
- Platform: Web, desktop-first.
- Palette (light): --void #FAF7F2 · --cream #F5F0E8 · --gold #B8860B · --gold-h #D4A017 · --ink #14110D
- Palette (dark): --void #050810 · --mid #111827 · --gold #D4A017 · --t1 #F5E6C8
- Type: Cormorant Garamond (display, 300) · Hanken Grotesk (body/UI, 300-500) · JetBrains Mono (data/labels, uppercase 0.1em-0.4em tracking)
- Radii: 12px standard, 16px large, 999px pills. Shadows: sh-sm/md/lg + gold glow. Line heights: 1.47 body, 1.05 headlines.
- Components to use: OVERLINE, DISPLAY H1 (max 2 gold <em>), LEDE (max 55ch), BUTTON PRIMARY (ink bg, 12px radius, hover gold), CARD (cream bg, 1px gold-line border), TRUST STRIP (max 5 stats).

## Anti-patterns (MUST NOT)
No pure #000/#FFF · no blue primary · no purple gradients · no text drop shadows · radius <= 16px · no emoji UI · no lorem ipsum · no load-blocking animation · CSS animation <= 1.5s · max 3 font families · pixel values multiples of 4.

## Acceptance
- Renders the artifact above with real copy (never placeholder text).
- Token values match exactly; components follow the inventory rules.
- Deviation from this system is limited to the card's declared deviation budget.
- Verifiable: build passes; visual check against .stitch/DESIGN.md.

---

# RIG AI-CODING PROMPT — Which sections already carry evidence the buyer trusts?

## Context
Board: "Iterate the Loehr HR-group landing page (JEV-audit-driven)"
Phase: Discover — What is the real human problem?
Artifact: research question · status: approved · deviation: 0 (within the deviation budget (|d| <= 3), no extra review required)
Downstream artifacts:
- HMW hold diagnostic_wedge (0.69) without sales pressure?
- HMW let the pricing page carry the qualifying burden?
- HMW close the accessible-apply-form gap on #book?

## Task
Live page audit: #hero leads with the named pain ("Your renewal just jumped 27% and nobody can show you what the service fee actually buys"); #operator gives James Loehr — 18 years running operations, largest 37 locations / ~550 employees; #pricing shows the fee in writing plus market context (SHRM Executive Network $3,995/yr, Hacking HR $2,000, Mile High SHRM cap 12 — same cap). These are the credibility spine; the iteration must not dilute them.

## Design system (MASTER-CREATIVE-PROMPT v3.0 — REQUIRED)
- Platform: Web, desktop-first.
- Palette (light): --void #FAF7F2 · --cream #F5F0E8 · --gold #B8860B · --gold-h #D4A017 · --ink #14110D
- Palette (dark): --void #050810 · --mid #111827 · --gold #D4A017 · --t1 #F5E6C8
- Type: Cormorant Garamond (display, 300) · Hanken Grotesk (body/UI, 300-500) · JetBrains Mono (data/labels, uppercase 0.1em-0.4em tracking)
- Radii: 12px standard, 16px large, 999px pills. Shadows: sh-sm/md/lg + gold glow. Line heights: 1.47 body, 1.05 headlines.
- Components to use: OVERLINE, DISPLAY H1 (max 2 gold <em>), LEDE (max 55ch), BUTTON PRIMARY (ink bg, 12px radius, hover gold), CARD (cream bg, 1px gold-line border), TRUST STRIP (max 5 stats).

## Anti-patterns (MUST NOT)
No pure #000/#FFF · no blue primary · no purple gradients · no text drop shadows · radius <= 16px · no emoji UI · no lorem ipsum · no load-blocking animation · CSS animation <= 1.5s · max 3 font families · pixel values multiples of 4.

## Acceptance
- Renders the artifact above with real copy (never placeholder text).
- Token values match exactly; components follow the inventory rules.
- Deviation from this system is limited to the card's declared deviation budget.
- Verifiable: build passes; visual check against .stitch/DESIGN.md.

---

# RIG AI-CODING PROMPT — Who is the reader the audit could not score well — and why?

## Context
Board: "Iterate the Loehr HR-group landing page (JEV-audit-driven)"
Phase: Discover — What is the real human problem?
Artifact: persona · status: in-review · deviation: 1 (within the deviation budget (|d| <= 3), no extra review required)
Downstream artifacts:
- HMW let the pricing page carry the qualifying burden?

## Task
JEV-AUDIT.md website.buyer: mean 0.634 on best-fit section packets, ~0.40 full page. Structural ceiling documented: ~11 rubric questions (vert_healthcare_regulated, typ_free_kit, typ_paid_review, design_visual_evidence…) score the RIG AI-intake product shape — a membership group can score ≤0.1 on them regardless of copy. Doctrine applied: split the bimodal distribution, never average it away. The page should serve the real buyer (Denver HR leader), not chase the mismatched questions.

## Design system (MASTER-CREATIVE-PROMPT v3.0 — REQUIRED)
- Platform: Web, desktop-first.
- Palette (light): --void #FAF7F2 · --cream #F5F0E8 · --gold #B8860B · --gold-h #D4A017 · --ink #14110D
- Palette (dark): --void #050810 · --mid #111827 · --gold #D4A017 · --t1 #F5E6C8
- Type: Cormorant Garamond (display, 300) · Hanken Grotesk (body/UI, 300-500) · JetBrains Mono (data/labels, uppercase 0.1em-0.4em tracking)
- Radii: 12px standard, 16px large, 999px pills. Shadows: sh-sm/md/lg + gold glow. Line heights: 1.47 body, 1.05 headlines.
- Components to use: OVERLINE, DISPLAY H1 (max 2 gold <em>), LEDE (max 55ch), BUTTON PRIMARY (ink bg, 12px radius, hover gold), CARD (cream bg, 1px gold-line border), TRUST STRIP (max 5 stats).

## Anti-patterns (MUST NOT)
No pure #000/#FFF · no blue primary · no purple gradients · no text drop shadows · radius <= 16px · no emoji UI · no lorem ipsum · no load-blocking animation · CSS animation <= 1.5s · max 3 font families · pixel values multiples of 4.

## Acceptance
- Renders the artifact above with real copy (never placeholder text).
- Token values match exactly; components follow the inventory rules.
- Deviation from this system is limited to the card's declared deviation budget.
- Verifiable: build passes; visual check against .stitch/DESIGN.md.

---

# RIG AI-CODING PROMPT — What do the demand-thread pain numbers say?

## Context
Board: "Iterate the Loehr HR-group landing page (JEV-audit-driven)"
Phase: Discover — What is the real human problem?
Artifact: research question · status: approved · deviation: 0 (within the deviation budget (|d| <= 3), no extra review required)
Downstream artifacts:
- HMW lift named_pain_lead (0.73) to top-of-page strength?
- Variant C — #members bring/take ledger with pain numbers

## Task
#group / #members carry pain numbers that are JEV scores from a September 2026 sweep of HR-leader demand threads on Reddit (quotes and sources in the research file): pain 6.0 — the solo HR lead paying $1,300/month for tools and getting no human; pain 6.90 — the price jack gets read out loud in the room before the vendor writes it into your renewal. Language rule from the audit: named pain first, product language never.

## Design system (MASTER-CREATIVE-PROMPT v3.0 — REQUIRED)
- Platform: Web, desktop-first.
- Palette (light): --void #FAF7F2 · --cream #F5F0E8 · --gold #B8860B · --gold-h #D4A017 · --ink #14110D
- Palette (dark): --void #050810 · --mid #111827 · --gold #D4A017 · --t1 #F5E6C8
- Type: Cormorant Garamond (display, 300) · Hanken Grotesk (body/UI, 300-500) · JetBrains Mono (data/labels, uppercase 0.1em-0.4em tracking)
- Radii: 12px standard, 16px large, 999px pills. Shadows: sh-sm/md/lg + gold glow. Line heights: 1.47 body, 1.05 headlines.
- Components to use: OVERLINE, DISPLAY H1 (max 2 gold <em>), LEDE (max 55ch), BUTTON PRIMARY (ink bg, 12px radius, hover gold), CARD (cream bg, 1px gold-line border), TRUST STRIP (max 5 stats).

## Anti-patterns (MUST NOT)
No pure #000/#FFF · no blue primary · no purple gradients · no text drop shadows · radius <= 16px · no emoji UI · no lorem ipsum · no load-blocking animation · CSS animation <= 1.5s · max 3 font families · pixel values multiples of 4.

## Acceptance
- Renders the artifact above with real copy (never placeholder text).
- Token values match exactly; components follow the inventory rules.
- Deviation from this system is limited to the card's declared deviation budget.
- Verifiable: build passes; visual check against .stitch/DESIGN.md.

---

# RIG AI-CODING PROMPT — HMW lift named_pain_lead (0.73) to top-of-page strength?

## Context
Board: "Iterate the Loehr HR-group landing page (JEV-audit-driven)"
Phase: Define — What are we actually solving?
Artifact: HMW · status: approved · deviation: 0 (within the deviation budget (|d| <= 3), no extra review required)
Upstream artifacts:
- Where did the JEV audit leave the page, honestly?
- What do the demand-thread pain numbers say?
Downstream artifacts:
- Variant A — #hero named-pain spine rewrite
- Variant B — #sequence year-in-the-room timeline

## Task
From c1 + c4. The hero already opens on the renewal shock; the fix is named-pain precision: one sentence a Denver HR leader says verbatim ("nobody can show you what the service fee actually buys"), kept above the fold in #hero, with the CTA "Apply for the Denver room — 12 seats" directly under it. Target: named_pain_lead ≥ 0.9 on re-run.

## Design system (MASTER-CREATIVE-PROMPT v3.0 — REQUIRED)
- Platform: Web, desktop-first.
- Palette (light): --void #FAF7F2 · --cream #F5F0E8 · --gold #B8860B · --gold-h #D4A017 · --ink #14110D
- Palette (dark): --void #050810 · --mid #111827 · --gold #D4A017 · --t1 #F5E6C8
- Type: Cormorant Garamond (display, 300) · Hanken Grotesk (body/UI, 300-500) · JetBrains Mono (data/labels, uppercase 0.1em-0.4em tracking)
- Radii: 12px standard, 16px large, 999px pills. Shadows: sh-sm/md/lg + gold glow. Line heights: 1.47 body, 1.05 headlines.
- Components to use: OVERLINE, DISPLAY H1 (max 2 gold <em>), LEDE (max 55ch), BUTTON PRIMARY (ink bg, 12px radius, hover gold), CARD (cream bg, 1px gold-line border), TRUST STRIP (max 5 stats).

## Anti-patterns (MUST NOT)
No pure #000/#FFF · no blue primary · no purple gradients · no text drop shadows · radius <= 16px · no emoji UI · no lorem ipsum · no load-blocking animation · CSS animation <= 1.5s · max 3 font families · pixel values multiples of 4.

## Acceptance
- Renders the artifact above with real copy (never placeholder text).
- Token values match exactly; components follow the inventory rules.
- Deviation from this system is limited to the card's declared deviation budget.
- Verifiable: build passes; visual check against .stitch/DESIGN.md.

---

# RIG AI-CODING PROMPT — HMW hold diagnostic_wedge (0.69) without sales pressure?

## Context
Board: "Iterate the Loehr HR-group landing page (JEV-audit-driven)"
Phase: Define — What are we actually solving?
Artifact: HMW · status: approved · deviation: 1 (within the deviation budget (|d| <= 3), no extra review required)
Upstream artifacts:
- Where did the JEV audit leave the page, honestly?
- Which sections already carry evidence the buyer trusts?
Downstream artifacts:
- Variant C — #members bring/take ledger with pain numbers

## Task
From c2. The wedge is the Guest offer in #pricing/#offers: $0, one diagnostic session a year, bring one document, leave with the room's written read on it — yours to keep whether or not you apply. It must read as the room already working for you, not a lead magnet. No "book a demo" energy.

## Design system (MASTER-CREATIVE-PROMPT v3.0 — REQUIRED)
- Platform: Web, desktop-first.
- Palette (light): --void #FAF7F2 · --cream #F5F0E8 · --gold #B8860B · --gold-h #D4A017 · --ink #14110D
- Palette (dark): --void #050810 · --mid #111827 · --gold #D4A017 · --t1 #F5E6C8
- Type: Cormorant Garamond (display, 300) · Hanken Grotesk (body/UI, 300-500) · JetBrains Mono (data/labels, uppercase 0.1em-0.4em tracking)
- Radii: 12px standard, 16px large, 999px pills. Shadows: sh-sm/md/lg + gold glow. Line heights: 1.47 body, 1.05 headlines.
- Components to use: OVERLINE, DISPLAY H1 (max 2 gold <em>), LEDE (max 55ch), BUTTON PRIMARY (ink bg, 12px radius, hover gold), CARD (cream bg, 1px gold-line border), TRUST STRIP (max 5 stats).

## Anti-patterns (MUST NOT)
No pure #000/#FFF · no blue primary · no purple gradients · no text drop shadows · radius <= 16px · no emoji UI · no lorem ipsum · no load-blocking animation · CSS animation <= 1.5s · max 3 font families · pixel values multiples of 4.

## Acceptance
- Renders the artifact above with real copy (never placeholder text).
- Token values match exactly; components follow the inventory rules.
- Deviation from this system is limited to the card's declared deviation budget.
- Verifiable: build passes; visual check against .stitch/DESIGN.md.

---

# RIG AI-CODING PROMPT — HMW let the pricing page carry the qualifying burden?

## Context
Board: "Iterate the Loehr HR-group landing page (JEV-audit-driven)"
Phase: Define — What are we actually solving?
Artifact: HMW · status: in-review · deviation: 2 (within the deviation budget (|d| <= 3), no extra review required)
Upstream artifacts:
- Which sections already carry evidence the buyer trusts?
- Who is the reader the audit could not score well — and why?
Downstream artifacts:
- Variant D — #pricing fee-sheet decode table

## Task
From c2 + c3. Targeting carries the data burden: #pricing already prices under national networks and inside the local band, caps at 12, bans vendors (including as guests), and prints the fee sheet before the first conversation. The iteration should make "who this is NOT for" a visible line so the wrong applicants self-select out — the structural ceiling stays disclosed, not papered over.

## Design system (MASTER-CREATIVE-PROMPT v3.0 — REQUIRED)
- Platform: Web, desktop-first.
- Palette (light): --void #FAF7F2 · --cream #F5F0E8 · --gold #B8860B · --gold-h #D4A017 · --ink #14110D
- Palette (dark): --void #050810 · --mid #111827 · --gold #D4A017 · --t1 #F5E6C8
- Type: Cormorant Garamond (display, 300) · Hanken Grotesk (body/UI, 300-500) · JetBrains Mono (data/labels, uppercase 0.1em-0.4em tracking)
- Radii: 12px standard, 16px large, 999px pills. Shadows: sh-sm/md/lg + gold glow. Line heights: 1.47 body, 1.05 headlines.
- Components to use: OVERLINE, DISPLAY H1 (max 2 gold <em>), LEDE (max 55ch), BUTTON PRIMARY (ink bg, 12px radius, hover gold), CARD (cream bg, 1px gold-line border), TRUST STRIP (max 5 stats).

## Anti-patterns (MUST NOT)
No pure #000/#FFF · no blue primary · no purple gradients · no text drop shadows · radius <= 16px · no emoji UI · no lorem ipsum · no load-blocking animation · CSS animation <= 1.5s · max 3 font families · pixel values multiples of 4.

## Acceptance
- Renders the artifact above with real copy (never placeholder text).
- Token values match exactly; components follow the inventory rules.
- Deviation from this system is limited to the card's declared deviation budget.
- Verifiable: build passes; visual check against .stitch/DESIGN.md.

---

# RIG AI-CODING PROMPT — HMW close the accessible-apply-form gap on #book?

## Context
Board: "Iterate the Loehr HR-group landing page (JEV-audit-driven)"
Phase: Define — What are we actually solving?
Artifact: HMW · status: in-review · deviation: 0 (within the deviation budget (|d| <= 3), no extra review required)
Upstream artifacts:
- Which sections already carry evidence the buyer trusts?
Downstream artifacts:
- Dev handoff — accessible #book apply form (c8)

## Task
JEV-AUDIT.md ui.design: clarity 0.98, mobile_considered 0.93, primary_action_obvious 0.83, accessible 0.75 — the audit's weakest ui item. The #book form (Name, Work email, Company, What would you put on the table?) needs real labels, error states, contrast that survives the no-pure-#000/#FFF rule, and 44px tap targets. Target: accessible ≥ 0.9 on re-run.

## Design system (MASTER-CREATIVE-PROMPT v3.0 — REQUIRED)
- Platform: Web, desktop-first.
- Palette (light): --void #FAF7F2 · --cream #F5F0E8 · --gold #B8860B · --gold-h #D4A017 · --ink #14110D
- Palette (dark): --void #050810 · --mid #111827 · --gold #D4A017 · --t1 #F5E6C8
- Type: Cormorant Garamond (display, 300) · Hanken Grotesk (body/UI, 300-500) · JetBrains Mono (data/labels, uppercase 0.1em-0.4em tracking)
- Radii: 12px standard, 16px large, 999px pills. Shadows: sh-sm/md/lg + gold glow. Line heights: 1.47 body, 1.05 headlines.
- Components to use: OVERLINE, DISPLAY H1 (max 2 gold <em>), LEDE (max 55ch), BUTTON PRIMARY (ink bg, 12px radius, hover gold), CARD (cream bg, 1px gold-line border), TRUST STRIP (max 5 stats).

## Anti-patterns (MUST NOT)
No pure #000/#FFF · no blue primary · no purple gradients · no text drop shadows · radius <= 16px · no emoji UI · no lorem ipsum · no load-blocking animation · CSS animation <= 1.5s · max 3 font families · pixel values multiples of 4.

## Acceptance
- Renders the artifact above with real copy (never placeholder text).
- Token values match exactly; components follow the inventory rules.
- Deviation from this system is limited to the card's declared deviation budget.
- Verifiable: build passes; visual check against .stitch/DESIGN.md.

---

# RIG AI-CODING PROMPT — Variant A — #hero named-pain spine rewrite

## Context
Board: "Iterate the Loehr HR-group landing page (JEV-audit-driven)"
Phase: Develop — What could the answer look like?
Artifact: variant sketch note · status: in-review · deviation: 1 (within the deviation budget (|d| <= 3), no extra review required)
Upstream artifacts:
- HMW lift named_pain_lead (0.73) to top-of-page strength?
Downstream artifacts:
- Dev handoff — #hero + #sequence spine (Variants A, B)

## Task
Keep the hero photo plate and the "run by an operator, not an association" line; rewrite the lede so the named pain is the first full sentence and the fee-sheet promise is the second. CTA unchanged: "Apply for the Denver room — 12 seats · 30-minute conversation first. No employee data needed." Risk: over-tilting to pain reads alarmist — the no-BLOCK calm from the audit must survive.

## Design system (MASTER-CREATIVE-PROMPT v3.0 — REQUIRED)
- Platform: Web, desktop-first.
- Palette (light): --void #FAF7F2 · --cream #F5F0E8 · --gold #B8860B · --gold-h #D4A017 · --ink #14110D
- Palette (dark): --void #050810 · --mid #111827 · --gold #D4A017 · --t1 #F5E6C8
- Type: Cormorant Garamond (display, 300) · Hanken Grotesk (body/UI, 300-500) · JetBrains Mono (data/labels, uppercase 0.1em-0.4em tracking)
- Radii: 12px standard, 16px large, 999px pills. Shadows: sh-sm/md/lg + gold glow. Line heights: 1.47 body, 1.05 headlines.
- Components to use: OVERLINE, DISPLAY H1 (max 2 gold <em>), LEDE (max 55ch), BUTTON PRIMARY (ink bg, 12px radius, hover gold), CARD (cream bg, 1px gold-line border), TRUST STRIP (max 5 stats).

## Anti-patterns (MUST NOT)
No pure #000/#FFF · no blue primary · no purple gradients · no text drop shadows · radius <= 16px · no emoji UI · no lorem ipsum · no load-blocking animation · CSS animation <= 1.5s · max 3 font families · pixel values multiples of 4.

## Acceptance
- Renders the artifact above with real copy (never placeholder text).
- Token values match exactly; components follow the inventory rules.
- Deviation from this system is limited to the card's declared deviation budget.
- Verifiable: build passes; visual check against .stitch/DESIGN.md.

---

# RIG AI-CODING PROMPT — Variant B — #sequence year-in-the-room timeline

## Context
Board: "Iterate the Loehr HR-group landing page (JEV-audit-driven)"
Phase: Develop — What could the answer look like?
Artifact: variant sketch note · status: approved · deviation: 0 (within the deviation budget (|d| <= 3), no extra review required)
Upstream artifacts:
- HMW lift named_pain_lead (0.73) to top-of-page strength?
Downstream artifacts:
- Dev handoff — #hero + #sequence spine (Variants A, B)

## Task
"Monthly. Quarterly. Renewal season. Year two." rendered as a four-stop timeline card set — this is the boring_reliable_job 0.96 evidence made visible: the room keeps a rhythm that outlasts the renewal cycle. Mono data labels overline each stop; one concrete meeting cadence per stop.

## Design system (MASTER-CREATIVE-PROMPT v3.0 — REQUIRED)
- Platform: Web, desktop-first.
- Palette (light): --void #FAF7F2 · --cream #F5F0E8 · --gold #B8860B · --gold-h #D4A017 · --ink #14110D
- Palette (dark): --void #050810 · --mid #111827 · --gold #D4A017 · --t1 #F5E6C8
- Type: Cormorant Garamond (display, 300) · Hanken Grotesk (body/UI, 300-500) · JetBrains Mono (data/labels, uppercase 0.1em-0.4em tracking)
- Radii: 12px standard, 16px large, 999px pills. Shadows: sh-sm/md/lg + gold glow. Line heights: 1.47 body, 1.05 headlines.
- Components to use: OVERLINE, DISPLAY H1 (max 2 gold <em>), LEDE (max 55ch), BUTTON PRIMARY (ink bg, 12px radius, hover gold), CARD (cream bg, 1px gold-line border), TRUST STRIP (max 5 stats).

## Anti-patterns (MUST NOT)
No pure #000/#FFF · no blue primary · no purple gradients · no text drop shadows · radius <= 16px · no emoji UI · no lorem ipsum · no load-blocking animation · CSS animation <= 1.5s · max 3 font families · pixel values multiples of 4.

## Acceptance
- Renders the artifact above with real copy (never placeholder text).
- Token values match exactly; components follow the inventory rules.
- Deviation from this system is limited to the card's declared deviation budget.
- Verifiable: build passes; visual check against .stitch/DESIGN.md.

---

# RIG AI-CODING PROMPT — Variant C — #members bring/take ledger with pain numbers

## Context
Board: "Iterate the Loehr HR-group landing page (JEV-audit-driven)"
Phase: Develop — What could the answer look like?
Artifact: variant sketch note · status: in-review · deviation: 2 (within the deviation budget (|d| <= 3), no extra review required)
Upstream artifacts:
- What do the demand-thread pain numbers say?
- HMW hold diagnostic_wedge (0.69) without sales pressure?
Downstream artifacts:
- Dev handoff — #pricing clarity block (Variant D, flagged)

## Task
"What Members Bring. What Members Take." as a two-column CARD ledger, each row footnoted with the JEV pain score and its source note (September 2026 Reddit sweep, quotes in the research file): pain 6.0 tools-with-no-human, pain 6.90 renewal price jack. Real numbers with provenance, never unattributed stats.

## Design system (MASTER-CREATIVE-PROMPT v3.0 — REQUIRED)
- Platform: Web, desktop-first.
- Palette (light): --void #FAF7F2 · --cream #F5F0E8 · --gold #B8860B · --gold-h #D4A017 · --ink #14110D
- Palette (dark): --void #050810 · --mid #111827 · --gold #D4A017 · --t1 #F5E6C8
- Type: Cormorant Garamond (display, 300) · Hanken Grotesk (body/UI, 300-500) · JetBrains Mono (data/labels, uppercase 0.1em-0.4em tracking)
- Radii: 12px standard, 16px large, 999px pills. Shadows: sh-sm/md/lg + gold glow. Line heights: 1.47 body, 1.05 headlines.
- Components to use: OVERLINE, DISPLAY H1 (max 2 gold <em>), LEDE (max 55ch), BUTTON PRIMARY (ink bg, 12px radius, hover gold), CARD (cream bg, 1px gold-line border), TRUST STRIP (max 5 stats).

## Anti-patterns (MUST NOT)
No pure #000/#FFF · no blue primary · no purple gradients · no text drop shadows · radius <= 16px · no emoji UI · no lorem ipsum · no load-blocking animation · CSS animation <= 1.5s · max 3 font families · pixel values multiples of 4.

## Acceptance
- Renders the artifact above with real copy (never placeholder text).
- Token values match exactly; components follow the inventory rules.
- Deviation from this system is limited to the card's declared deviation budget.
- Verifiable: build passes; visual check against .stitch/DESIGN.md.

---

# RIG AI-CODING PROMPT — Variant D — #pricing fee-sheet decode table

## Context
Board: "Iterate the Loehr HR-group landing page (JEV-audit-driven)"
Phase: Develop — What could the answer look like?
Artifact: variant sketch note · status: draft · deviation: 5 (OUTSIDE the deviation budget (|d| <= 3) — flag for human review before shipping)
Upstream artifacts:
- HMW let the pricing page carry the qualifying burden?
Downstream artifacts:
- Dev handoff — #pricing clarity block (Variant D, flagged)

## Task
Solo seat, Company pack (3 seats, one org, different functions, $6,600/year), Guest diagnostic ($0 · one session) as a three-row comparison, with the verified 2026-09-30 market context as a TRUST STRIP (max 5 stats): SHRM $3,995 · Hacking HR $2,000 · Mile High SHRM cap 12 · this room under the national band · monthly seat = leave any month. Deviation +5 from the system table component — outside the |d| ≤ 3 budget, flagged for human review before shipping.

## Design system (MASTER-CREATIVE-PROMPT v3.0 — REQUIRED)
- Platform: Web, desktop-first.
- Palette (light): --void #FAF7F2 · --cream #F5F0E8 · --gold #B8860B · --gold-h #D4A017 · --ink #14110D
- Palette (dark): --void #050810 · --mid #111827 · --gold #D4A017 · --t1 #F5E6C8
- Type: Cormorant Garamond (display, 300) · Hanken Grotesk (body/UI, 300-500) · JetBrains Mono (data/labels, uppercase 0.1em-0.4em tracking)
- Radii: 12px standard, 16px large, 999px pills. Shadows: sh-sm/md/lg + gold glow. Line heights: 1.47 body, 1.05 headlines.
- Components to use: OVERLINE, DISPLAY H1 (max 2 gold <em>), LEDE (max 55ch), BUTTON PRIMARY (ink bg, 12px radius, hover gold), CARD (cream bg, 1px gold-line border), TRUST STRIP (max 5 stats).

## Anti-patterns (MUST NOT)
No pure #000/#FFF · no blue primary · no purple gradients · no text drop shadows · radius <= 16px · no emoji UI · no lorem ipsum · no load-blocking animation · CSS animation <= 1.5s · max 3 font families · pixel values multiples of 4.

## Acceptance
- Renders the artifact above with real copy (never placeholder text).
- Token values match exactly; components follow the inventory rules.
- Deviation from this system is limited to the card's declared deviation budget.
- Verifiable: build passes; visual check against .stitch/DESIGN.md.

---

# RIG AI-CODING PROMPT — Dev handoff — #hero + #sequence spine (Variants A, B)

## Context
Board: "Iterate the Loehr HR-group landing page (JEV-audit-driven)"
Phase: Deliver — What ships, and how is it built?
Artifact: dev handoff · status: approved · deviation: 0 (within the deviation budget (|d| <= 3), no extra review required)
Upstream artifacts:
- Variant A — #hero named-pain spine rewrite
- Variant B — #sequence year-in-the-room timeline
Downstream artifacts:
- Dev handoff — this board exported as a coding bundle

## Task
Ship the named-pain hero and the year-in-the-room timeline. Tokens: light theme (--void #FAF7F2, --cream #F5F0E8, --gold #B8860B, --ink #14110D). Components: OVERLINE, DISPLAY H1 (Cormorant 300, max 2 gold ems), LEDE max 55ch, BUTTON PRIMARY. Acceptance: named_pain_lead ≥ 0.9 and boring_reliable_job held ≥ 0.9 on JEV re-run; mobile_considered ≥ 0.9 at 390px.

## Design system (MASTER-CREATIVE-PROMPT v3.0 — REQUIRED)
- Platform: Web, desktop-first.
- Palette (light): --void #FAF7F2 · --cream #F5F0E8 · --gold #B8860B · --gold-h #D4A017 · --ink #14110D
- Palette (dark): --void #050810 · --mid #111827 · --gold #D4A017 · --t1 #F5E6C8
- Type: Cormorant Garamond (display, 300) · Hanken Grotesk (body/UI, 300-500) · JetBrains Mono (data/labels, uppercase 0.1em-0.4em tracking)
- Radii: 12px standard, 16px large, 999px pills. Shadows: sh-sm/md/lg + gold glow. Line heights: 1.47 body, 1.05 headlines.
- Components to use: OVERLINE, DISPLAY H1 (max 2 gold <em>), LEDE (max 55ch), BUTTON PRIMARY (ink bg, 12px radius, hover gold), CARD (cream bg, 1px gold-line border), TRUST STRIP (max 5 stats).

## Anti-patterns (MUST NOT)
No pure #000/#FFF · no blue primary · no purple gradients · no text drop shadows · radius <= 16px · no emoji UI · no lorem ipsum · no load-blocking animation · CSS animation <= 1.5s · max 3 font families · pixel values multiples of 4.

## Acceptance
- Renders the artifact above with real copy (never placeholder text).
- Token values match exactly; components follow the inventory rules.
- Deviation from this system is limited to the card's declared deviation budget.
- Verifiable: build passes; visual check against .stitch/DESIGN.md.

---

# RIG AI-CODING PROMPT — Dev handoff — accessible #book apply form (c8)

## Context
Board: "Iterate the Loehr HR-group landing page (JEV-audit-driven)"
Phase: Deliver — What ships, and how is it built?
Artifact: dev handoff · status: in-review · deviation: 0 (within the deviation budget (|d| <= 3), no extra review required)
Upstream artifacts:
- HMW close the accessible-apply-form gap on #book?
Downstream artifacts:
- Dev handoff — this board exported as a coding bundle

## Task
Form fields Name, Work email, Company, "What would you put on the table?" — explicit <label>s, inline error states, focus rings in --gold, contrast ≥ 4.5:1 within the token palette, tap targets ≥ 44px, submit "Apply for a seat" with the honest note ("This form opens the 30-minute conversation…"). Acceptance: ui accessible ≥ 0.9 on JEV re-run; no pure #000/#FFF anywhere.

## Design system (MASTER-CREATIVE-PROMPT v3.0 — REQUIRED)
- Platform: Web, desktop-first.
- Palette (light): --void #FAF7F2 · --cream #F5F0E8 · --gold #B8860B · --gold-h #D4A017 · --ink #14110D
- Palette (dark): --void #050810 · --mid #111827 · --gold #D4A017 · --t1 #F5E6C8
- Type: Cormorant Garamond (display, 300) · Hanken Grotesk (body/UI, 300-500) · JetBrains Mono (data/labels, uppercase 0.1em-0.4em tracking)
- Radii: 12px standard, 16px large, 999px pills. Shadows: sh-sm/md/lg + gold glow. Line heights: 1.47 body, 1.05 headlines.
- Components to use: OVERLINE, DISPLAY H1 (max 2 gold <em>), LEDE (max 55ch), BUTTON PRIMARY (ink bg, 12px radius, hover gold), CARD (cream bg, 1px gold-line border), TRUST STRIP (max 5 stats).

## Anti-patterns (MUST NOT)
No pure #000/#FFF · no blue primary · no purple gradients · no text drop shadows · radius <= 16px · no emoji UI · no lorem ipsum · no load-blocking animation · CSS animation <= 1.5s · max 3 font families · pixel values multiples of 4.

## Acceptance
- Renders the artifact above with real copy (never placeholder text).
- Token values match exactly; components follow the inventory rules.
- Deviation from this system is limited to the card's declared deviation budget.
- Verifiable: build passes; visual check against .stitch/DESIGN.md.

---

# RIG AI-CODING PROMPT — Dev handoff — #pricing clarity block (Variant D, flagged)

## Context
Board: "Iterate the Loehr HR-group landing page (JEV-audit-driven)"
Phase: Deliver — What ships, and how is it built?
Artifact: dev handoff · status: draft · deviation: 5 (OUTSIDE the deviation budget (|d| <= 3) — flag for human review before shipping)
Upstream artifacts:
- Variant C — #members bring/take ledger with pain numbers
- Variant D — #pricing fee-sheet decode table
Downstream artifacts:
- Dev handoff — this board exported as a coding bundle

## Task
Fee-sheet decode table + TRUST STRIP of verified market context (dates on every number — "Market context, verified 2026-09-30"). Deviation +5 is outside the |d| ≤ 3 budget: human review required before this block ships. If review rejects the custom table, fall back to standard CARD rows with identical copy.

## Design system (MASTER-CREATIVE-PROMPT v3.0 — REQUIRED)
- Platform: Web, desktop-first.
- Palette (light): --void #FAF7F2 · --cream #F5F0E8 · --gold #B8860B · --gold-h #D4A017 · --ink #14110D
- Palette (dark): --void #050810 · --mid #111827 · --gold #D4A017 · --t1 #F5E6C8
- Type: Cormorant Garamond (display, 300) · Hanken Grotesk (body/UI, 300-500) · JetBrains Mono (data/labels, uppercase 0.1em-0.4em tracking)
- Radii: 12px standard, 16px large, 999px pills. Shadows: sh-sm/md/lg + gold glow. Line heights: 1.47 body, 1.05 headlines.
- Components to use: OVERLINE, DISPLAY H1 (max 2 gold <em>), LEDE (max 55ch), BUTTON PRIMARY (ink bg, 12px radius, hover gold), CARD (cream bg, 1px gold-line border), TRUST STRIP (max 5 stats).

## Anti-patterns (MUST NOT)
No pure #000/#FFF · no blue primary · no purple gradients · no text drop shadows · radius <= 16px · no emoji UI · no lorem ipsum · no load-blocking animation · CSS animation <= 1.5s · max 3 font families · pixel values multiples of 4.

## Acceptance
- Renders the artifact above with real copy (never placeholder text).
- Token values match exactly; components follow the inventory rules.
- Deviation from this system is limited to the card's declared deviation budget.
- Verifiable: build passes; visual check against .stitch/DESIGN.md.

---

# RIG AI-CODING PROMPT — Dev handoff — this board exported as a coding bundle

## Context
Board: "Iterate the Loehr HR-group landing page (JEV-audit-driven)"
Phase: Deliver — What ships, and how is it built?
Artifact: dev handoff · status: in-review · deviation: 1 (within the deviation budget (|d| <= 3), no extra review required)
Upstream artifacts:
- Dev handoff — #hero + #sequence spine (Variants A, B)
- Dev handoff — accessible #book apply form (c8)
- Dev handoff — #pricing clarity block (Variant D, flagged)

## Task
The loop closes here: Export dev handoff renders rig-dev-handoff.json (cards, phase, links, deviation scores, token set) + rig-ai-coding-prompts.md (board-level prompt then per-card prompts) into the side panel. A coding agent consumes the bundle directly; the Stitch mockups in the Mockups tab (export handoff modal, mobile canvas 390px) are the visual contract for the same surfaces.

## Design system (MASTER-CREATIVE-PROMPT v3.0 — REQUIRED)
- Platform: Web, desktop-first.
- Palette (light): --void #FAF7F2 · --cream #F5F0E8 · --gold #B8860B · --gold-h #D4A017 · --ink #14110D
- Palette (dark): --void #050810 · --mid #111827 · --gold #D4A017 · --t1 #F5E6C8
- Type: Cormorant Garamond (display, 300) · Hanken Grotesk (body/UI, 300-500) · JetBrains Mono (data/labels, uppercase 0.1em-0.4em tracking)
- Radii: 12px standard, 16px large, 999px pills. Shadows: sh-sm/md/lg + gold glow. Line heights: 1.47 body, 1.05 headlines.
- Components to use: OVERLINE, DISPLAY H1 (max 2 gold <em>), LEDE (max 55ch), BUTTON PRIMARY (ink bg, 12px radius, hover gold), CARD (cream bg, 1px gold-line border), TRUST STRIP (max 5 stats).

## Anti-patterns (MUST NOT)
No pure #000/#FFF · no blue primary · no purple gradients · no text drop shadows · radius <= 16px · no emoji UI · no lorem ipsum · no load-blocking animation · CSS animation <= 1.5s · max 3 font families · pixel values multiples of 4.

## Acceptance
- Renders the artifact above with real copy (never placeholder text).
- Token values match exactly; components follow the inventory rules.
- Deviation from this system is limited to the card's declared deviation budget.
- Verifiable: build passes; visual check against .stitch/DESIGN.md.
