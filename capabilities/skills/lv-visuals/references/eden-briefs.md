# Eden briefs: what the generator receives

Eden is the assigned generator of brand imagery and copy. These briefs are this stage's actual output:
fill one completely, hand it to the Eden workspace as a draft, stop. Never render brand assets in the
agent lane. Never schedule. Mike publishes [eden-brief-templates].

## Common gates every brief carries

- Lane pinned (A or B); voice matches the lane; cast rules enforced (A: Birch Tuesday-only, Coach
  silhouette Wednesday to Saturday; B: no proprietary cast ever)
- One classifier sentence: "This asset is for <person> struggling with <thing>"
- No QA or internal text in the artwork (inspect first and last rendered unit)
- Every number in the artwork traces to a receipt, or it is removed
- Mobile legibility at feed size
- VOID-named assets never reused; a deleted-after-approval visual needs a fresh yes to repost
- Delivery target is an Eden draft; house slots 7-9 AM or 12-1 PM Denver; the bridge routine owns
  idempotency, not the brief

## 1. Carousel brief

```
objective:        <one line>
lane:             A | B
classifier:       This asset is for <person> struggling with <thing>.
format:           document post (PDF carousel), 1080x1350, 4:5
slide_count:      6-9 (justify anything over 9)
template:         <house template / brand frame name>
slides:
  1. COVER: <hook title, at most 8 words> | face: yes/no | swipe cue: yes
  2..N. BODY: one idea per slide, at most 50 words, bold phrase marked, visual note
  N. CLOSE: single CTA (follow prompt OR comment-word delivery, pick ONE)
content_type:     listicle | case study | technical how-to
gem_tease:        <post-text line naming a later slide; real value only>
document_title:   <public headline-style title>
post_copy:        <companion copy on related-not-duplicated ground, under 500 chars>
mentions:         <tagged people or companies, and why>
palette_refs:     <house palette / typography refs>
receipts:         <number to receipt ledger ref, or "none in artwork">
```

## 2. Image brief

```
objective:        <one line>
lane:             A | B
classifier:       <sentence>
format:           single image (default: real photo of Mike) | graphic | GIF (at most 6s, one message)
photo_direction:  <context, expression, what it must communicate> (photo only)
graphic_spec:     at most 8 words on image, headline block, contrast pair, palette refs
sizes:            feed default; use the generator preset and verify the render
banned:           stock faces, AI infographics as post images, watermarks, QA text
companion:        <state only whether the image accompanies text; the copy is lv-draft's>
```

## 3. Video brief

```
objective:        <one line>
lane:             A | B
classifier:       <sentence>
format:           vertical 9:16 or feed video (state length cap); target 45-90s
hook:             first-3-seconds line: <text>; by-10-seconds payoff: <text>
structure:        get clear (audience + message) / engage (hook) / map (key points) / sum (one takeaway)
captions:         burned-in graphic captions, styled, accurate; headline block at top
thumbnail:        screenshot of a key captioned moment, trimmed vertical (no custom design spend)
companion_copy:   transcribe, then rewrite as post copy (caption length is an open A/B)
cta:              <single ask or NONE>
batch_context:    <part of batch #_, session date>
tags:             <people or companies featured>
quality_gates:    mic | light (window or behind camera, never overhead) | clean edit
```

## 4. Banner / profile-asset brief (rare, high leverage)

```
objective:        profile conversion asset: what a first-time visitor must understand in 3 seconds
lane:             <account surface: Mike personal / RIG page>
elements:         one-line value prop | industry-relevant visual | one palette | ONE CTA route
resolution:       use the generator's LinkedIn-banner preset; transcript dimensions are unreliable
banner_bar:       <name + 2-3 descriptors from {title, top skills, passion, one personal interest}>
mistake_check:    not pixelated | not text-crowded | contrast passes
```

## 5. Newsletter issue brief

```
objective:        <what this issue does for the subscriber>
lane:             A | B
classifier:       <sentence>
newsletter_title: <titled so only the ideal prospect would subscribe>
issue_cover:      <cover card spec: one palette, one message, mobile-legible>
post_copy:        <announcement copy for the issue>
receipts:         <number to receipt ref, or "none">
```

Brief hygiene: an incomplete brief is not a brief. Eden fills gaps with generic choices, and generic
is the failure mode this stage exists to prevent [eden-brief-templates].

Absorbed from: eden-brief-templates, li-visuals.
