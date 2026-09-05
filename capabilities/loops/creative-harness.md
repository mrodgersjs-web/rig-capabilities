---
outcome: agent-engineering:
done_when:
  - file:capabilities/loops/creative-harness.md
  - cmd:python3 scripts/assert_loop_termination.py capabilities/loops/creative-harness.md
great_example: examples/great/agent-engineering/creative-harness.md.md
quality_floor: 0.6
---

# Creative Goal Harness — H_creative(GL-CB)

Governs GL-CB (creative/brand) loops.
This is a runtime gate loop. Each gate must produce evidence before the session
may advance to publishing or public display. No gate evidence, no progress.

## 0. Identity Lock

The session starts as Jake RIG Agent executing a creative task. Before any
content is drafted, designed, or produced, identity must be locked.

Gate 0.1 ❏ Session declared as GL-CB in first 3 lines.
Gate 0.2 ❏ RIG procedures loaded — `~/.hermes/jake/rig-operating-procedures.md`
   read or cited by line range.
Gate 0.3 ❏ Coordinate stated: `L{level}-D{diamond}-A{mode}-{step}`.
Gate 0.4 ❏ Creative brief stated before production begins.
   Proof: "This session produces: <format> for <audience> on <channel>,
   with <tone>, referencing <brand elements>, measured by <quality bar>."
   Not "make a post" — a specific brief with constraints.

## 1. Brand Consistency

### 1.1 Visual Identity
Gate VI.1 ❏ Colors match brand palette.
   Proof: hex codes in the output match the brand palette. If no brand
   palette is defined, state that explicitly and use RIG defaults
   (or request palette before proceeding).
Gate VI.2 ❏ Typography matches brand.
   Proof: fonts used match brand typography. If web-based, font-family
   declarations match brand spec. If undefined, state that.
Gate VI.3 ❏ Logo usage follows brand guidelines.
   Proof: logo is not stretched, recolored, cropped, or overlaid on
   busy backgrounds. Clear space around logo >= brand minimum. If no
   guidelines exist, use conservative defaults (original colors, 2x
   clear space, never below 24px height).

### 1.2 Content Identity
Gate CI.1 ❏ Content is identifiable as RIG/Mike without seeing the logo.
   Proof: strip all brand marks — does the content still feel like RIG?
   Specific voice, specific angle, specific references. Not generic
   "thought leadership" that any consultancy could publish.
Gate CI.2 ❏ No competitor visual language.
   Proof: content does not mimic the visual style of competitors. If
   a competitor is referenced, it's explicit and contrastive ("Unlike X,
   we do Y"), not accidental resemblance.

## 2. Voice Audit

### 2.1 Voice Consistency
Gate VA.1 ❏ Written content matches Mike's voice profile.
   Proof: the content reads like Mike wrote it, not like an AI wrote it
   about Mike. Voice markers: direct, specific, no hedging, uses real
   numbers, references real work, conversational but authoritative.
   If voice profile exists at `~/.rig/voice/` or equivalent, check against it.
Gate VA.2 ❏ Tone matches the context.
   Proof: LinkedIn post ≠ internal memo ≠ client proposal ≠ tweet.
   Tone is appropriate for the channel and audience. Show: "This is a
   <channel> post for <audience>, so the tone is <tone>, which is
   correct because <reason>."
Gate VA.3 ❏ No AI-isms in creative output.
   Proof: zero instances of:
   - "I hope this finds you well"
   - "In today's fast-paced world"
   - "It's important to note that"
   - "Leverage" (when "use" works)
   - "Unlock" (when "enable" works)
   - "Harness the power of"
   - "Game-changer" / "game-changing"
   - "Revolutionize" / "transformative"
   - "Delve" / "embark" / "navigate"
   - "Robust" / "cutting-edge" / "next-gen"
   - "I'm excited to share" / "Thrilled to announce"
   - Excessive exclamation marks (> 1 per 200 words)
   - Emoji in professional context (unless brand-idiomatic)

## 3. Anti-Generic Check

### 3.1 Specificity Gate
Gate AG.1 ❏ Anti-generic score >= 85 for all creative output.
   Proof: run through AntiGenericForce scorer or manual equivalent.
   Scoring: +15 per specific number/stat, +10 per named entity,
   +10 per unique angle, +10 per personal experience/reference,
   +10 per specific audience insight, +15 per "only RIG/Mike would
   say this" factor, +15 per proprietary data/insight, +10 per
   unexpected connection.
   -20 per generic advice, -15 per template feel, -10 per obvious
   fact, -10 per filler sentence, -15 per stock photo language.
Gate AG.2 ❏ No stock/generic content.
   Proof: zero instances of:
   - Generic motivational quotes without context
   - "According to a study" without naming the study
   - "Experts say" without naming the experts
   - Generic stock photo descriptions (if image prompts)
   - Template structures that could be about any company
   - Lorem ipsum or placeholder text in final output

### 3.2 Originality
Gate OR.1 ❏ Content has at least one original insight or angle.
   Proof: the output contains something that couldn't be found by
   searching the first page of Google for the topic. A unique
   perspective, proprietary data, or personal experience that adds
   genuine value.
Gate OR.2 ❏ Content does not duplicate recent output.
   Proof: check against last 30 days of published content. No repeat
   angles, hooks, or structures. If revisiting a topic, show what's
   different this time.

## 4. Visual Quality

### 4.1 Design Standards
Gate VQ.1 ❏ Visual output meets minimum quality bar.
   Proof: for images — correct aspect ratio for platform, readable
   text at mobile size, no compression artifacts, consistent visual
   language. For videos — proper framing, readable captions, audio
   levels correct. For documents — consistent formatting, no orphans/
   widows, page breaks at logical points.
Gate VQ.2 ❏ Accessibility basics met.
   Proof: color contrast >= 4.5:1 for text, alt text on images,
   captions on videos, readable font sizes (>= 16px body for web).
Gate VQ.3 ❏ Platform specifications met.
   Proof: output dimensions match the target platform's requirements.
   LinkedIn: 1200x627 (landscape), 1080x1080 (square), 1080x1350
   (portrait). Twitter: 1600x900. Instagram: 1080x1080 or 1080x1350.
   State the platform and dimensions explicitly.

### 4.2 Image Integrity
Gate II.1 ❏ No unlicensed or unattributed visual assets.
   Proof: all images are either original, licensed, Creative Commons
   (with attribution), or generated. Source of each visual asset stated.
Gate II.2 ❏ No visual artifacts or errors.
   Proof: images have no text glitches, no misaligned elements, no
   placeholder text visible, no unclosed shapes or broken gradients.

## 5. Gate-D for Public Release

Gate D.1 ❏ No creative content published externally without approval.
   Proof: all creative output is prepared as a gated artifact. Social
   posts, blog articles, ad creative, email designs — all require
   explicit Mike approval before going live.
Gate D.2 ❏ No brand representation in new channels without approval.
   Proof: if this is the first content for a new channel (e.g., first
   YouTube video, first TikTok), require explicit approval for the
   channel itself, not just the content.
Gate D.3 ❏ No external imagery of Mike without approval.
   Proof: if content includes photos or video of Mike, verify approval
   was given for this specific use. Headshot for bio = likely approved.
   Candid photo for ad = requires explicit approval.

## 6. Proof Requirements

Every creative session produces a ProofPacket:

```json
{
  "schema_version": "rig.creative.v1",
  "run_id": "<uuid>",
  "loop": "GL-CB",
  "brief": "...",
  "format": "post | article | image | video | deck | email",
  "channel": "linkedin | twitter | blog | email | web | ad",
  "word_count": 350,
  "gates": {
    "identity_lock": {"pass": true, "evidence": "..."},
    "brand_consistency": {"pass": true, "visual": true, "content": true},
    "voice_audit": {"pass": true, "ai_isms": 0},
    "anti_generic": {"pass": true, "score": 89},
    "originality": {"pass": true, "evidence": "..."},
    "visual_quality": {"pass": true, "accessibility": true},
    "gate_d": {"pass": true, "evidence": "gated artifact, not published"}
  },
  "verdict": "PASS | FAIL",
  "proof_hash": "sha256:..."
}
```

## 7. Definition of Done

A creative session is done when:
1. All applicable gates in §0–§5 passed.
2. Anti-generic score >= 85.
3. Zero AI-isms in output.
4. Brand consistency verified (visual + voice).
5. Output meets platform specs and accessibility basics.
6. Gate-D enforced — nothing published without approval.
7. ProofPacket written.
8. One improvement entry to `~/.hermes/jake/improvements.log`.
9. Identity closure: coordinate, verdict, format/channel, quality score,
   next safe action.

## 8. What Happens When a Gate Fails

| Gate | On Failure |
|------|-----------|
| 0.1–0.4 (Identity) | HALT. No production without locked brief and scope. |
| VI.1–VI.3 (Visual Identity) | Block. Fix colors/typography/logo before proceeding. |
| CI.1–CI.2 (Content Identity) | Block. Rewrite until content is identifiable as RIG. |
| VA.1–VA.3 (Voice Audit) | Block. Strip AI-isms. Rewrite to match Mike's voice. |
| AG.1–AG.2 (Anti-Generic) | Block. Rewrite until score >= 85. Generic creative = invisible. |
| OR.1–OR.2 (Originality) | Block. Add original angle or insight. No rehashing. |
| VQ.1–VQ.3 (Visual Quality) | Block. Fix specs, accessibility, quality before delivery. |
| II.1–II.2 (Image Integrity) | Block. Replace unlicensed assets. Fix visual artifacts. |
| D.1–D.3 (Gate-D) | HALT. No public release without approval. Immediate stop. |

## 9. Self-Improvement Loop

After each creative session, append to `~/.hermes/jake/improvements.log`:

```text
[YYYY-MM-DD HH:MM] creative session: GL-CB
  gates passed: <count>/<total>
  gates failed/skipped: <which>
  format: <format>
  channel: <channel>
  anti-generic score: <score>
  ai_isms found: <count>
  capability gap: <what was missing>
  improvement: <what to add or change>
```

Every 5 entries: extract pattern. If voice audit fails 3+ times,
update voice profile. If anti-generic < 90 consistently, update
creative templates. If same gate fails 3+ times, update this harness.

## 10. Final Rule

```text
No brand match, no publish.
No voice audit, no content.
No Gate-D approval, no public exposure.
Every creative session leaves the brand stronger than it found it.
```

---

*Companion to: hermes-conductor.md, doer-checker-validator.md*
*Governs: GL-CB (creative/brand)*

## What Great Looks Like (WGLL)

Amazing creative output from this harness:

- **Visual assets are real** — generated images, not placeholders or descriptions
- **Brand voice is consistent** — passes voice audit with zero banned words
- **Mike appears in images** — brand doctrine compliance on every asset
- **No text in images** — clean visuals that work at any size
- **Aspect ratio is platform-correct** — 16:9 for LinkedIn, 9:16 for Stories, 1:1 for feeds
- **Proof surfaces are complete** — evidence links real, no placeholder sections
- **Anti-generic score ≥ 85** — no stock-photo energy or corporate jargon

