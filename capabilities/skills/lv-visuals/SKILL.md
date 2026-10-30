---
name: lv-visuals
description: >-
  Visual stage of the LinkedIn pipeline: pick the format, architect carousels, images and video
  shorts, write the exact Eden briefs, enforce the Lane A cast rules and run the Lane B portrait
  harness. Use when a post needs media, when an Eden image brief is due, or when a rendered asset
  needs QA before it ships. JEV-FIRST MANDATE, findable at task start: every typed judgment in this
  stage (format choice, asset lane call, cover and slide ranking, render QA screening) goes to
  rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the
  classifier is down. Child of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, visuals, carousels, eden, media]
outcome: "content-publishing: every post leaves this stage with one chosen format, a complete Eden brief, and a QA'd asset that obeys lane cast rules and carries no unreceipted number"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-visuals
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  absorbed: "10"
---

# LV Visuals: media is the second hook

## JEV-first mandate (read first)

Typed judgments this stage forces: which format wins, which lane an asset belongs to, which cover or
slide variant ranks first, and whether a render clears QA. Each goes to Jev before any frontier LLM
call: `rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`.
Stored rubrics: `post.linkedin` (Lane B), `post.viral`, `post.eden`, `comment.linkedin`,
`doctrine.surface`. A pass needs every required noul and confidence above 0.9; exactly 0.90 fails.
Fail closed: classifier down, rubric missing, or a judgment no stored rubric covers (render QA has
none) is DEFERRED to Mike. Never guess a verdict locally, never substitute a frontier model's opinion.
An advisory PASS is not permission to publish. Eden stays the only publisher; Gate-D governs any live
post, and this stage never schedules.

## When to use / when not to

Use when a LinkedIn post needs media (photo, carousel, graphic, GIF, video short, banner, newsletter
cover card), when an Eden image or video brief is due, when a Lane A Coach or Birch image prompt is
needed, when a Lane B authored portrait is in production, or when a rendered asset needs QA before it
goes to the gate. Do not use for post copy (lv-draft), hook writing (lv-hooks), scheduling
(lv-launch) or measurement (lv-measure). Lane C, anything about a minor, is out of scope here and
never inherits a mascot, a hook or a commercial CTA.

## Procedure

1. Pin the lane (A, B, client, job). If the request does not name it, ask; never infer it from the
   topic. Visuals never borrow across lanes [li-visuals].
2. Classify the asset in one sentence: "This visual is for <named person> struggling with <specific
   thing>." A category fails the classifier [li-visuals].
3. Choose the moat and the format with media as the second hook: ask of every post whether a photo,
   graphic or video can carry it [hooks-and-media]. Default is a real photo of Mike; escalate to a
   carousel when the payload is saveable; escalate to video when the payload is a demonstration or a
   story that needs his voice [li-visuals]. Real photos of real people and places out-pull branded
   graphics, which read as ads [szN0DF3Oqik].
4. Rank format and cover variants through Jev (mandate above). DEFERRED keeps the decision open; it
   never becomes a guess.
5. Write the Eden brief in full from `references/eden-briefs.md`. Eden generates all brand imagery;
   this stage briefs and QA's only. No brief, no asset [li-visuals].
6. Build to the matching sub-skill: `references/carousel-system.md`, `references/image-and-graphics.md`
   or `references/video-shorts.md`.
7. QA the render against the quality bar. Inspect the first and last unit at feed size; QA or internal
   text in artwork is a defect, not a footnote [li-visuals].
8. If generated imagery names the cast, apply `references/cast-and-generated-imagery.md` first. Lane A
   Coach prompts come from the Eden-resident `coach-image-prompter` skill; Lane B authored portraits
   run the Higgsfield harness and need human approval before anything is sealed.
9. Hand the asset, the brief and the QA state to lv-gate. This stage never publishes.

## Quality bar

- Lane pinned, voice matches, cast rules enforced (A: Birch Tuesday-only, Coach from behind or in
  silhouette; B: no proprietary cast)
- Classifier sentence present and specific enough to name a person
- No QA, instruction or internal text anywhere in the artwork
- First and last slide or frame visually inspected at feed size; legible on a phone
- One idea per slide; at most 50 words per slide; slide counter and headshot placement correct
- Document title present and written like a headline (LinkedIn shows it publicly)
- One consistent palette and typography across the whole asset
- Every number in the artwork traces to a receipt, or it is removed
- The image matches the copy [uYVwSbaztJ4]
- Delivery target is an Eden draft or an approved harness output: not scheduled, not published

## Lanes

- **A (personal brand, Eden, Ted Lasso register):** pop-culture opening allowed; Birch and its
  sign-off are Tuesday-only; Wednesday to Saturday imagery is The Coach only, photoreal, from behind
  or in silhouette, 16:9 landscape. Coach prompts are generated by `coach-image-prompter` in Eden.
- **B (RIG B2B):** evidence-led, named receipts, no mascots. Birch / Unit 7 / The Coach / "Be more
  Birch" never appear. Test real photos of Mike's work, desk and events against generated art and log
  the result [hooks-and-media]. Authored portraits run the Higgsfield harness.
- **Client (Ideawake, Coby's account):** briefs may be drafted and staged; nothing renders to
  Coby's account or ships without Mike's explicit client approval.
- **Job search:** banner and profile assets use the banner brief; profile edits are shown as exact
  before/after values and applied only after Mike approves.

## Tools and runners

| name | kind | path | when to call |
|---|---|---|---|
| coach-image-prompter | tool | `coach-image-prompter` (Eden-resident skill, cite by name) | Wed-Sat Coach posts, or any request for The Coach cast: it returns one ready photoreal prompt with its character, style, scene and ratio blocks |
| rig-linkedin-image-harness | tool | `~/.hermes/skills/rig-linkedin-image-harness` | Lane B authored portraits plus editorial and pull-quote cards: run its harness CLI, score frames against the gate stack, human approval before any ProofPacket |

## Sub-skills

| file | covers |
|---|---|
| `references/format-and-media-decision.md` | format matrix, photo-first rule, moat choice, Clark media evidence |
| `references/eden-briefs.md` | the brief templates and the common gates every brief carries |
| `references/carousel-system.md` | carousel architecture, the HTML render pipeline, per-slide image prompts |
| `references/image-and-graphics.md` | photos, graphics, GIFs, quote cards, banner, stock licensing |
| `references/video-shorts.md` | feed video, vertical shorts, captions, copy pairing, cadence |
| `references/cast-and-generated-imagery.md` | Lane A cast rules, Coach prompts, Lane B portrait harness gates |
| `references/creator-playbook.md` | cross-creator consensus, conflicts and gaps for this stage (11 doctrines) |

## Hard rules carried forward

- Eden generates every brand asset; this family briefs and QA's only. An agent-rendered carousel was
  rejected outright, so a weak Eden render is fixed with a sharper brief or a second Eden pass, never
  an agent render [li-visuals].
- QA text and internal instructions never enter artwork; inspect the first and last rendered unit
  before anything ships [li-visuals].
- Real photo first: a graphic earns its place only on framework, stat or quick-insight payloads
  [li-visuals, szN0DF3Oqik]. The image must match the copy [uYVwSbaztJ4].
- No engagement-bait visuals, no fake screenshots or fabricated analytics panels, no bought or
  templated stock faces, no auto-publish [li-visuals].
- Never quote a reach multiplier in artwork or copy; the corpus contradicts itself on carousel versus
  video supremacy, so pick by payload [carousel-architecture, video-shorts].
- One idea per slide, at most 50 words per slide, 6-9 slides unless justified; one CTA on the closing
  slide, never a menu of asks [carousel-architecture].
- The saveable asset or its delivery promise belongs in the first comment, never an external link in
  the body [carousel-architecture].
- House carousel default is 1080x1350 (4:5); use the generator preset and verify legibility rather
  than hand-pixeling dimensions [carousel-architecture, gemini-carousel]. Two carousels a week is the
  reported ceiling [carousel-architecture].
- At most 8 words on a single graphic, at most 15 words in a quote; quote posts are written fresh and
  never attributed to a real person without a source [image-system, quote-post].
- Replicate a viral pattern, never another creator's asset [image-system].
- Stock images need the licence re-checked before publish, and link-preview text is checked before
  shipping [image-system].
- Video: burned-in captions, not auto-captions; hook in the first 3 seconds; house default vertical
  9:16, 45-90 seconds [video-shorts].
- Every number in an asset carries a receipt or comes out [li-visuals]. A chart without a labelled
  source is a fabricated metric in a nicer font [carousel-html].
- VOID-named assets are never reused, and a visual Mike deleted after approving needs a fresh yes
  before any repost [li-visuals].
- The Coach is never face-on, never close-up, never illustrated, and never a real person's likeness;
  Birch never appears outside its days; no Coach visual is produced for Lane C [coach-image-prompter,
  li-visuals].
- Identity in the portrait harness fails closed: without an embedder and a reference set there is no
  identity pass, and a human approves before a ProofPacket is sealed. Pretty is not done
  [rig-linkedin-image-harness].
- Not scheduled, not published here: Eden drafts only, Mike publishes [li-visuals].

## Lessons from measured outcomes (added 2026-10-01)

Provenance tag `[measured:...]` marks an observation on this estate's own tooling; `[ext:...]` marks
an outside finding.

- **The image ship gate must be fail-closed on inspection, never on file metadata.** As built, the
  viral ship score awarded `scene_fidelity: 85` for a `reference_image` path merely existing and
  `brand_fidelity: 80` for the file being larger than 1 MB, summing 85+90+80 = SHIP for an image
  nobody had looked at. Nothing in it read a single word of the artwork. This is the mechanical
  reason the account's imagery is weak: the check that was meant to stop a bad image was scoring
  file size. A fail-closed patch was written on 2026-09-17 and **left uncommitted**, so the defect is
  live at time of writing. Rule: a fidelity score may only be awarded from a read of the rendered
  pixels or an explicit human pass, and a missing check is a FAIL, never a default.
  [measured:rig-viral viral_ship_score, 2026-09-17 patch, uncommitted]
- **Carousel length evidence disagrees with the house default.** This stage says 6-9 slides;
  getcreator's 8,400-post benchmark puts the engagement sweet spot at 9-12 slides (5.4% engagement,
  68-76% swipe-through), and AuthoredUp's 3M-post study found that when median impressions fell 47%
  platform-wide, native documents fell 43% while video fell 72%. The house default has no baseline
  on this account, so the two are in conflict until measured. Named as a conflict, not changed
  silently. [ext:getcreator.io/stats/linkedin-carousel-benchmarks, ext:authoredup.com/newsletter/linkedin-vanishing-audience]
- **Mixed-media carousels are the open format edge.** Image plus 3-5 second video clips measured
  2.33% engagement against 1.80% for image-only, and only about 7% of accounts use the form. Worth
  one briefed Eden test before the format is written off. [ext:socialinsider.io via Bruna Keller,
  instagram.com/p/DZYTutKE8Ne]

## Done-test

`python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-visuals`
verifies that the frontmatter name matches the folder and the description carries the JEV-FIRST
MANDATE, that the body opens with the JEV-first mandate, that references/ holds at least three
sub-skills of 400+ bytes plus a ledger with a named action for every stage-map row of this stage, that
every backticked path resolves on disk, and that no sub-skill shares a 12-word run with a third-party
merge source. It prints GREEN and exits 0 only when all of that holds.
