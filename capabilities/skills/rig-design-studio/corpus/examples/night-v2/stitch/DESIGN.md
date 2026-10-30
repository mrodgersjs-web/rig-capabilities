# .stitch/DESIGN.md — RIG Design Studio mockups

Synthesized from `site-v2/docs/design-system/MASTER-CREATIVE-PROMPT.md` (v3.0) +
the seeded Double Diamond board ("Design a launch page for a Denver HR leaders group").
This file is the source of truth every Stitch screen must follow.

## Platform
- Web, desktop-first (1440 × 900 reference viewport).
- Product: interactive design canvas — "Miro meets Figma, driven by the RIG design system".

## Vibe
Premium, editorial, warm-operational. A working instrument for design leaders: quiet chrome,
gold accents only where they carry meaning, serif for titles, mono for metadata. No generic AI
aesthetic.

## Palette (REQUIRED)
| Role | Light (default) | Dark (cinematic) |
|---|---|---|
| page bg | --void #FAF7F2 | --void #050810 |
| section bg | --warm #EDE7DC | --dark #0A0E1A |
| card bg | --cream #F5F0E8 | --mid #111827 |
| accent | --gold #B8860B | --gold #D4A017 |
| accent hover | --gold-h #D4A017 | --gold-h #F0C75E |
| text primary | --ink #14110D | --t1 #F5E6C8 |
| text secondary | --graphite #3A332B | rgba(232,217,181,.5) |
| text tertiary | --mist #8A7E6E | rgba(232,217,181,.25) |

Functional: --success #2D7A2D · --energy #E65C00 · --loss #C62828 · --trust #1A5276 (sparingly).

## Typography
- Display / headlines: Cormorant Garamond, 300 (hero clamp(2.5rem,7vw,5.5rem), -0.03em), 500 for card titles.
  Max 2 gold italic `<em>` per headline. Never bold, never all-caps.
- Body / UI: Hanken Grotesk, 300–500, 0.9375rem, 1.47 line-height, max-width 65ch.
- Data / labels: JetBrains Mono, 400–600, uppercase, 0.1em–0.4em tracking (overlines 0.65rem, micro 0.55rem).
- Max 3 font families per screen.

## Shape & elevation
- Radii: 12px standard, 16px large cards, 999px pills. Never > 16px.
- Shadows: sh-sm 0 1px 3px rgba(28,24,20,.04) · sh-md 0 2px 12px …06 · sh-lg 0 8px 32px …08 ·
  sh-gold 0 4px 20px rgba(184,134,11,.1). Shadows on hover only.
- Borders: 1px gold-line (rgba(184,134,11,.25)); selected state = 2px gold ring.

## Components (Section 6 inventory)
OVERLINE · DISPLAY H1 · SECTION H2 · LEDE (max 55ch) · BUTTON PRIMARY (ink bg, void text, .75rem mono,
uppercase, 12px radius, hover = gold bg + translateY(-2px) + sh-gold) · BUTTON GHOST (mono, gold border) ·
CARD (cream bg, 1px gold-line, 16px radius, 2.25rem padding) · TRUST STRIP (max 5 stats).

## Layout — the 3 required screens + 2 round-2 screens
1. **Canvas board view** — infinite pan/zoom grid (24px minor grid), artifact cards (240×172, cream,
   gold-line, left status edge: green=approved, gold=in-review, gray=draft), curved gold connection
   lines, marquee selection, floating zoom control bottom-left, design-system side panel right (340px).
2. **Double Diamond stage view** — double-diamond SVG banner (Discover/Define/Develop/Deliver), then
   4 equal rails; each rail: mono overline (phase · N artifacts), serif question, artifact cards.
3. **Design system panel** — token table with swatches (colors + type + radii/shadows), light/dark
   "Apply tokens" toggle, selected-artifact editor (title, body, phase, kind, status, deviation
   slider -10..+10), "Generate AI-coding prompt" block.
4. **Export handoff modal (round 2)** — modal (720px, cream, 16px radius, gold-line) over a dimmed
   canvas: serializer stat tiles (artifacts / links / phases / out-of-budget), export rows for
   rig-dev-handoff.json + rig-ai-coding-prompts.md, JSON preview pane, "Download both files".
5. **Mobile canvas view, 390px (round 2)** — same product on a phone viewport: 48px top bar,
   segmented tab strip, full-width artifact cards (16px radius, gold-line, status edge), curved
   gold connection lines, bottom action bar with "+ Artifact" / "Export", tap targets ≥ 44px.

## Anti-patterns (MUST NOT)
No pure #000/#FFF · no blue primary · no purple gradients · no text drop shadows · radius > 16px ·
emoji as UI · lorem ipsum · load-blocking animation · CSS animation > 1.5s · > 3 font families ·
pixel values not multiples of 4 · glassmorphism on > 2 elements per viewport.

## Deviation budget
Every artifact card carries a deviation score -10..+10 (0 = on-system). |deviation| ≤ 3 ships
without review; outside the budget is flagged for human review and is always rendered visibly
(red chip). The budget is a design-system control, not a quality score.

## Copy
Real content only — the seed board copy derives from the live Loehr HR-group landing page
(`/Users/rig128gb/Developer/loehr-hr-group/site/index.html`, sections #hero…#book) and its JEV audit
(`research/JEV-AUDIT.md`, honest scores kept). Voice: first person, business outcomes,
no vendor jargon.
