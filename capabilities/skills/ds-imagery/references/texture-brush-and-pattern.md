---
name: texture-brush-and-pattern
tier: sub
parent: ds-imagery
---

# Texture Brush And Pattern

Purpose: watercolor brushes, seamless tiles, and scatter confetti (laws 41-50).

Load when: the task touches this part of imagery and art direction, or a ds-imagery critique names it. Part of `ds-imagery`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 41 | A watercolor read needs overlap and low opacity, not a solid stroke. On a bristle brush, raise length (120 percent in the demo), drop density and thickness (20 percent), drop paint opacity (64 percent), and drop stiffness (24 percent) so the hairs flex. | Envato Tuts+ | CLAIM(APzkcH27HY0@01:37, APzkcH27HY0@01:54, APzkcH27HY0@02:21, APzkcH27HY0@02:28) | single-source | no |
| 42 | A scanned stroke placed as an art brush cannot be recolored. Trace it (high fidelity photo, then lower the color count so the path count stays usable), delete white by Select Same fill, and set the art brush colorization to tints and shades. Stretch to fit stroke length, and check adjust-corners so overlaps do not pile up. | Envato Tuts+ | CLAIM(APzkcH27HY0@04:27, APzkcH27HY0@04:57, APzkcH27HY0@05:08, APzkcH27HY0@05:26, APzkcH27HY0@05:47) | single-source | no |
| 43 | Build the object in flat vector first, then lock texture into it with a clipping mask. Edit the texture inside the mask (direct-select, then selection tool to scale) instead of releasing and remaking the mask. For a two-tone object, reuse one texture, repositioned, so the tone stays consistent. | Every Tuesday | CLAIM(M7LHzwuEX-0@11:45, M7LHzwuEX-0@12:06, M7LHzwuEX-0@12:46, M7LHzwuEX-0@12:50) | single-source | no |
| 44 | A seamless pattern tile must be a square. Whatever crosses the left edge must be copied in place and shifted by the exact tile width on X; top edge copies shift by the exact tile height on Y. After that shift, do not move the copied motif. Adjust only the neighbors. | Every Tuesday | CLAIM(ITRZ75OKrG0@01:25, ITRZ75OKrG0@02:13, ITRZ75OKrG0@03:04, ITRZ75OKrG0@03:26) | single-source | no |
| 45 | A pattern swatch counts art outside the mask. Crop a duplicate, and keep an uncropped copy so you can still edit. Two squares: one is the background fill, one is the clipping mask. Scale the pattern with Transform Objects unchecked and preview on. If resizing the shape stretches the pattern, click the swatch again to reset it. | Every Tuesday | CLAIM(ITRZ75OKrG0@07:32, ITRZ75OKrG0@08:03, ITRZ75OKrG0@08:28, ITRZ75OKrG0@10:05, ITRZ75OKrG0@10:49) | single-source | no |
| 46 | Pick a texture with hard edges, veins, and strong light-to-dark variation. Soft washes disappear as a brush. The source must be a transparent PNG with the paper removed, used at native size so pixels are not stretched. | Every Tuesday | CLAIM(dBmUQ1IWqX4@00:53, dBmUQ1IWqX4@01:25, dBmUQ1IWqX4@02:00, dBmUQ1IWqX4@02:26) | single-source | no |
| 47 | Define a brush from a merged copy, and keep the adjustment group (hue/saturation, levels, brightness/contrast) unmerged so the source stays editable. Desaturate, then push darks and lights apart until the variation is obvious, before Edit, Define Brush Preset. | Every Tuesday | CLAIM(dBmUQ1IWqX4@02:37, dBmUQ1IWqX4@03:07, dBmUQ1IWqX4@03:51, dBmUQ1IWqX4@04:20, dBmUQ1IWqX4@04:43) | single-source | no |
| 48 | Recolor a stamped texture with a gradient overlay (radial in the demo), and drag the overlay so the color lands where the texture needs it. A flat foreground click is the one-color stamp; the overlay is the watercolor variation. | Every Tuesday | CLAIM(dBmUQ1IWqX4@06:06, dBmUQ1IWqX4@06:38, dBmUQ1IWqX4@06:52, dBmUQ1IWqX4@07:47) | single-source | no |
| 49 | Start a scatter brush small. You can scale up; you cannot always go smaller. Circles: fixed scale, random spacing and scatter pushed high, no rotation. Stars: random scale kept modest, plus rotation, because a pointy shape shows the spin. Set colorization to tints and shades or every recolor means reopening the brush. | Every Tuesday, Envato Tuts+ | CLAIM(D3iJ_aVVJDE@01:06, D3iJ_aVVJDE@02:10, D3iJ_aVVJDE@02:52, D3iJ_aVVJDE@03:12, D3iJ_aVVJDE@06:11, APzkcH27HY0@05:47) | consensus | no |
| 50 | Draw one stroke before fine-tuning a scatter brush. Illustrator previews brush edits on an existing stroke, not in the dialog alone. Apply to strokes, then recolor from the color panel. Layer several strokes for variation. | Every Tuesday | CLAIM(D3iJ_aVVJDE@04:01, D3iJ_aVVJDE@04:18, D3iJ_aVVJDE@04:40, D3iJ_aVVJDE@07:03) | single-source | no |

## Anti-patterns for this sub-topic
- Leaving a texture at full opacity after it kills contrast. CLAIM(TaGO9l4EYOk@03:50)
- Pathfinder-cropping a complex vector and keeping the artifacts. CLAIM(GWa3vVQXH8M@04:05)
- Accepting the first Remove Background pass. It missed the beak and part of the branch in the demo. CLAIM(ntk3IVzfIYs@02:09, ntk3IVzfIYs@02:16)
- Using the magic wand on a close-value edge. CLAIM(ntk3IVzfIYs@11:22)
