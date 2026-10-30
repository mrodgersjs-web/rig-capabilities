# Enhanced Stitch prompt — Screen 5: Mobile canvas view (390px)

An interactive design-canvas web app ("Miro meets Figma, driven by the RIG design system"), premium editorial-operational mood, warm and quiet, gold accents with meaning. Mobile viewport 390×844 (portrait phone), the same product adapted to a narrow screen — not a separate app.

**DESIGN SYSTEM (REQUIRED):**
- Platform: Web mobile UI, 390px wide portrait
- Palette: page #FAF7F2 warm ivory, cards #F5F0E8 cream, accent dark goldenrod #B8860B, hover #D4A017, text #14110D warm near-black, secondary #3A332B, tertiary #8A7E6E
- Styles: 12px standard / 16px large radius (never more), 1px golden-line borders rgba(184,134,11,.25), tap targets ≥ 44px

**PAGE STRUCTURE — mobile canvas view:**
1. **Top bar (48px):** cream background, gold-line bottom border; mono overline "RIG DESIGN STUDIO" in gold left; serif board title truncated to one line ("Iterate the Loehr HR-group landing…"); right: ghost icon button for the design-system panel (sliders icon)
2. **Segmented tab strip (44px):** three pill segments — "Board" (active, near-black fill), "Double Diamond", "Mockups" — horizontally scrollable, mono uppercase labels
3. **Canvas (fills remaining height):** subtle 24px grid on warm ivory; a vertical stack of three full-width artifact cards (16px radius, cream, gold-line, left status edge green/gold/gray): each card shows mono kind label + deviation chip ("dev +2"), serif title (2 lines), 2-line body clamp, and a gold circular connect port on the right edge; curved gold connection lines between card ports at 55% opacity; one card selected with 2px gold ring
4. **Bottom action bar (64px, cream, gold-line top border):** dark primary button "+ Artifact" (full-width left, 48px tall), ghost button "Export" (48px), floating zoom pill "− 85% +" above the bar on the right
5. **Safe-area hint (mono micro, tertiary):** "DRAG CARDS · PINCH ZOOM · TAP ○ TO LINK"

No emojis, no pure black or white, no purple gradients, max 3 typefaces (Cormorant Garamond serif titles, Hanken Grotesk body, JetBrains Mono labels), pixel values multiples of 4, mobile_considered layout with no horizontal scroll.
