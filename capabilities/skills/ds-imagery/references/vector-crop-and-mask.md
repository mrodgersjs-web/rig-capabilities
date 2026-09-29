---
name: vector-crop-and-mask
tier: sub
parent: ds-imagery
---

# Vector Crop And Mask

Purpose: web file setup, motif clusters, editable type masks, and crop choice (laws 11-25).

Load when: the task touches this part of imagery and art direction, or a ds-imagery critique names it. Part of `ds-imagery`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 11 | For web graphics, start the file in RGB at 72 ppi. Screen effects and vibrant gradients read correctly there; do not build that background in a print document. | Satori Graphics | CLAIM(y1zR4h2aEDw@00:44, y1zR4h2aEDw@00:48, eFHxknDs4Mk@00:37) | single-source (one creator, two videos) | yes |
| 12 | Lock a full-bleed gradient before drawing motifs on top of it. Pick the ground colors so later shapes pop against them (dark blue into a pink-red is one working pair), then spread one gradient across a united shape with the gradient tool instead of filling each piece separately. | Satori Graphics | CLAIM(y1zR4h2aEDw@01:26, y1zR4h2aEDw@01:36, y1zR4h2aEDw@02:19, y1zR4h2aEDw@05:42) | single-source | yes |
| 13 | Build a splat or cluster by duplicating rectangles with smart guides, uniting them, then rounding every corner in one direct-selection click (or the round-corners effect on older builds). Rotate the cluster 45 degrees so it reads as a graphic, not a stack of boxes. | Satori Graphics | CLAIM(y1zR4h2aEDw@03:15, y1zR4h2aEDw@04:23, y1zR4h2aEDw@04:34, y1zR4h2aEDw@05:02) | single-source | yes |
| 14 | Split a motif with a pen shape and Pathfinder divide, then fill the cut with black-to-black where one stop is 0 percent opacity. That is the sheen. Add the drop shadow only after every motif is in, with preview on, and clip the whole stack to the artboard. | Satori Graphics | CLAIM(y1zR4h2aEDw@07:54, y1zR4h2aEDw@08:02, y1zR4h2aEDw@08:40, y1zR4h2aEDw@09:50) | single-source | yes |
| 15 | To keep type editable inside a clipping mask, turn on compound shape in Pathfinder before masking, and keep the type on top of the art. After the mask, the type tool can still change the words and the font. | Satori Graphics | CLAIM(_iafygrxKMI@00:40, _iafygrxKMI@01:08, _iafygrxKMI@01:28) | single-source | yes |
| 16 | For a photo broken into shapes (hex brochure, flyer, magazine), duplicate and align with smart guides, drop opacity so you can see the photo, unite only the shapes that should reveal the photo, convert that union to a compound path, then mask. Recolor the shapes you left out. | Satori Graphics | CLAIM(_iafygrxKMI@02:17, _iafygrxKMI@03:13, _iafygrxKMI@03:42, _iafygrxKMI@03:54, _iafygrxKMI@04:18) | single-source | yes |
| 17 | Trim anything that spills past the artboard with a rectangle snapped to the canvas edge, fill not stroke, used as a clipping mask. Do not manually delete overflow paths. | Satori Graphics, Envato Tuts+ | CLAIM(_iafygrxKMI@04:30, _iafygrxKMI@04:44, _iafygrxKMI@04:56, y1zR4h2aEDw@09:50, GWa3vVQXH8M@02:49) | consensus | yes |
| 18 | Sketch the first draft small and fast. The drawing is almost never right the first time; the job of the sketch is to move the idea from brain to paper, not to survive into the final file. | Flux Academy | CLAIM(q3ACHGp6bFA@00:16, q3ACHGp6bFA@00:27, q3ACHGp6bFA@00:45) | single-source | yes |
| 19 | Use square, rectangular, angled, and circular guides both on paper and in software. Snap-to-grid produces alignment and proportion fast enough that a simple mark can go pencil to vector without a trace. Clean a hand-drawn wordmark with guidelines before calling the logo type done. | Flux Academy, Satori Graphics | CLAIM(q3ACHGp6bFA@00:58, q3ACHGp6bFA@01:07, q3ACHGp6bFA@01:15, q3ACHGp6bFA@01:26, eFHxknDs4Mk@02:53) | consensus | yes |
| 20 | Pick the vector tool for the job. Use the curvature tool for smooth curves and the width tool on one center path instead of drawing both edges of a taper. Learn the pen, but do not force it when a stylus, mouse, or width tool is the shorter path. | Flux Academy | CLAIM(q3ACHGp6bFA@01:39, q3ACHGp6bFA@01:51, q3ACHGp6bFA@02:06, q3ACHGp6bFA@02:16) | single-source | yes |
| 21 | Start a simple vector figure from regular shapes, then add a few paths and finish in Shape Builder. Enduring logos are basic shapes; that regularity is what makes the mark iconic. A photo or a rough sketch is a legal starting point for the same build. | Flux Academy | CLAIM(q3ACHGp6bFA@02:21, q3ACHGp6bFA@02:24, q3ACHGp6bFA@02:35, q3ACHGp6bFA@02:44) | single-source | yes |
| 22 | Write the stock brief before searching: subject, feel, aspect ratio, clear space. Never ship stock as supplied. Recolor it, add elements, add texture, until it has a personality that fits the brand. An image someone has already seen loses impact. | Flux Academy | CLAIM(q3ACHGp6bFA@03:07, q3ACHGp6bFA@03:10, q3ACHGp6bFA@03:20, q3ACHGp6bFA@03:31) | single-source | yes |
| 23 | Plan the crop on the artboard before you cut anything. Pick the crop by what you need: visual hide versus permanent delete, photo versus vector. A clipping mask or opacity mask hides and stays editable; Pathfinder crop and the eraser (alt-drag a rectangle) delete forever. | Envato Tuts+, Satori Graphics | CLAIM(GWa3vVQXH8M@00:05, GWa3vVQXH8M@00:28, GWa3vVQXH8M@03:08, GWa3vVQXH8M@03:23, GWa3vVQXH8M@04:22, _iafygrxKMI@04:30) | consensus | yes |
| 24 | Do not Pathfinder-crop a complex vector. It leaves tiny artifacts that ruin the picture. Use a clipping mask, or export a raster of the artboard (Use Artboards on) so the original file stays whole. | Envato Tuts+ | CLAIM(GWa3vVQXH8M@04:05, GWa3vVQXH8M@02:17, GWa3vVQXH8M@02:30) | single-source | no |
| 25 | To crop a vector with the CC Crop Image command, place it into a new file first. Cropping the original in place is the wrong path; embedding via Place is what the command accepts. | Envato Tuts+ | CLAIM(GWa3vVQXH8M@01:22, GWa3vVQXH8M@01:29) | single-source | no |

## Anti-patterns for this sub-topic
- Leaving snap-to-grid on for a free vector background when you do not use it. CLAIM(y1zR4h2aEDw@01:02)
- Pathfinder-cropping a complex vector and keeping the artifacts. CLAIM(GWa3vVQXH8M@04:05)
- Accepting the first Remove Background pass. It missed the beak and part of the branch in the demo. CLAIM(ntk3IVzfIYs@02:09, ntk3IVzfIYs@02:16)
- Using the magic wand on a close-value edge. CLAIM(ntk3IVzfIYs@11:22)
