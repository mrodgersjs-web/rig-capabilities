# Enhanced Stitch prompt — Screen 4: Export dev handoff modal

An interactive design-canvas web app ("Miro meets Figma, driven by the RIG design system"), premium editorial-operational mood, warm and quiet, gold accents with meaning. Desktop-first SaaS work surface, 1440×900.

**DESIGN SYSTEM (REQUIRED):**
- Platform: Web, desktop-first application UI (not a marketing page)
- Palette: page #FAF7F2 warm ivory, cards #F5F0E8 cream, accent dark goldenrod #B8860B, hover #D4A017, text #14110D warm near-black, secondary #3A332B, tertiary #8A7E6E
- Styles: 12px standard / 16px large radius (never more), 1px golden-line borders rgba(184,134,11,.25), subtle hover shadows only

**PAGE STRUCTURE — "Export dev handoff" modal over a dimmed canvas board:**
1. **Background (60% visible):** the design canvas with artifact cards and gold connection lines, dimmed under a warm scrim rgba(20,17,13,.45)
2. **Modal (720px wide, cream #F5F0E8, 16px radius, 1px gold-line border, centered):**
   - mono overline "EXPORT DEV HANDOFF" in gold; serif H2 "Board → coding agent"
   - summary strip: 4 small stat tiles (mono labels + serif numbers): 16 ARTIFACTS · 20 LINKS · 4 PHASES · 2 OUT-OF-BUDGET
   - two export rows, each a CARD-like row: file icon block (mono extension chip "JSON" / "MD"), serif filename ("rig-dev-handoff.json" / "rig-ai-coding-prompts.md"), small description ("cards, phase, links, deviation scores, token set" / "board-level prompt + per-card prompt bundle"), ghost button "Preview" and a green check chip "serializer check PASS · 13/13"
   - a small code preview pane (dark #14110D background, JetBrains Mono 11px, warm ivory text) showing 6 lines of JSON: schema "rig.design-studio.dev-handoff.v1", counts, first card title
   - footer row: ghost button "Cancel", dark primary button "Download both files"
3. **Modal corner note (mono micro):** "deviation budget |d| ≤ 3 · 2 artifacts flagged for human review"

No emojis, no pure black or white, no purple gradients, max 3 typefaces (Cormorant Garamond serif titles, Hanken Grotesk body, JetBrains Mono labels), pixel values multiples of 4.
