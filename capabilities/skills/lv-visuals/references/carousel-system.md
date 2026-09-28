# Carousel system: architecture, HTML pipeline, per-slide prompts

## Why carousels, honestly

Creators report carousels as a top format on reach and engagement because swiping reads as dwell, and
document posts carry the highest average engagement rate in the trade data [carousel-architecture].
Both are self-reports and one creator's multiplier is never quoted in artwork or copy. The corpus also
claims video dominates, which contradicts it: pick by payload, not by multiplier [video-shorts].

## Template discipline (the recognition play)

Build ONE carousel template and reuse it so the audience recognizes the content in feed on sight.
Anatomy: cover page + body pages + closing page. Keep several body layouts keyed to topic types inside
the same brand frame [carousel-architecture].

**Cover:** a face on the cover is a scroll stopper; title as large as possible; the cover carries the
hook with the same budget as a post hook; add an explicit swipe cue [carousel-architecture].

**Body:** one idea per slide (non-negotiable), 25-50 words maximum, the load-bearing phrase in bold,
slides read as a sequence rather than a stack, alternating background tones when the palette allows, a
visible slide counter, headshot and name on first and last slide only [carousel-architecture].
Slide count: house standard 6-9; the corpus says about 12; test 10-12 only behind the 10-post evidence
bar [carousel-architecture, measurement-kpi-loop].

**Close:** one CTA only (follow prompt, or a comment-word delivery of the asset), never a menu of asks
[carousel-architecture].

## Dimensions (corpus contradicts itself; house rule pins it)

Creators variously cite 1200x1500, 1080x1350 and 1080x1280. House default is 1080x1350, 4:5,
mobile-first. Use the chosen generator's preset when it differs and verify legibility at feed size in
QA. Never hand-pixel dimensions into a brief without checking the tool preset [carousel-architecture].

## Content shapes that work

Listicles (one item per slide), case studies (numbers receipt-gated before they enter slides),
technical how-to (one specific problem), and the hand-raiser lead-magnet deck: contrarian slide-1 hook,
absolve the reader, one visual model of the new way, a curiosity loop, a receipt-gated proof line, and
an invitation close with comment-word delivery. Design the deck before writing copy: mark every slide
teach / sell / both. A deck where nothing sells is a lecture; one where everything sells is an ad
[carousel-architecture].

Tease a real later-slide item in the post text so readers swipe deep ("slide 8 is the one nobody
uses"), and only when that slide earns it [carousel-architecture].

## Post copy and upload mechanics

- Never upload the PDF naked: real companion copy on related-not-duplicated ground, under about 500
  characters [carousel-architecture].
- The saveable asset or its promise goes in the first comment, not a body link [carousel-architecture].
- Carousels are document posts: PDF only, uploaded as Add document. The document title is public, so
  name it like a headline. Preview before publishing and fix clipped or tiny text [carousel-architecture].
- Cadence: two carousels a week is the reported ceiling; house posting slots already constrain timing
  [carousel-architecture].

## HTML/CSS render pipeline (reproducible variant)

Platform mechanics only; no creator teaches this method [carousel-html].

1. Outline the slides as text and gate the outline first: 6-10 slides, slide 1 a hook, middle slides
   one point each, final slide one soft next step.
2. Author as HTML: one section per slide at 1080x1350, overflow hidden; body type at least 42px,
   display type 76-110px on the cover; check legibility at about 270px wide, roughly the mobile feed.
3. No page chrome: no scrollbars, nav or footer boilerplate; small slide numbers bottom-right only.
4. Render each section to PNG at 1080x1350 with a 2x scale factor, clipped to the section box. Look at
   slide 1 before rendering the rest.
5. Assemble to PDF, one slide per page, exact page size, no margin. PDF is what LinkedIn accepts.
6. Verify by reopening the PDF: page count must equal slide count. A carousel that silently drops
   slides publishes as a truncated argument.
7. Hand to the gate with the slide text included, so the words are gated and not just the images.

Charts label their axes and their source. An unsourced chart is a fabricated metric in a nicer font
[carousel-html].

## Per-slide image prompts (generated variant)

When slides are generated rather than composed: approve a slide-by-slide design brief BEFORE any image
prompt is written, then output one prompt per slide with the brand style locked identical across the
set so the deck reads as one carousel. Slides are 1080x1350; body text in a slide stays under about 15
words because readability loses on the feed; the cover and the CTA slide are visually distinct from
body slides. A single combined one-shot prompt is faster but less consistent, so it is offered as an
explicit alternative, not the default [gemini-carousel]. The brief approval gate is not optional
[gemini-carousel]. House word budget for body slides is 25-50 words of real slide text [carousel-architecture];
the tighter 15-word figure is the generated-image legibility limit [gemini-carousel].

Absorbed from: carousel-architecture, carousel-html, gemini-carousel.
