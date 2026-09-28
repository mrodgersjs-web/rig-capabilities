# Cast and generated imagery: who may appear, and which harness makes it

## Lane A cast rules (hard)

- Birch and its sign-off belong to Tuesday only. Never render Birch outside its days, and never end a
  non-Tuesday post with the Birch sign-off [li-visuals, voice-law-checker].
- Wednesday through Saturday imagery is The Coach only: the Ted Lasso archetype figure, photoreal,
  always shot from behind or in silhouette. Never face-on, never a frontal close-up, never illustrated
  [li-visuals, coach-image-prompter].
- The Coach is a parody archetype, not a person: never name a real individual and never render features
  that match a known real person [coach-image-prompter].
- The image carries BOTH the joke and the post's argument in one frame. It is not decoration
  [coach-image-prompter].
- Text overlays are banned on Coach images; the "Believe" sign appears in the background only when the
  post calls for it [coach-image-prompter].
- 16:9 landscape (1920x1080) for Coach scenes. Never vertical, never square [coach-image-prompter].

## Generating Coach prompts

The Eden-resident skill `coach-image-prompter` owns the Coach prompt: call it (day-aware) and use the
prompt it returns, which carries the character block, the photoreal style block, the day-specific scene
seed and the aspect ratio, under 350 words. Do not hand-write a Coach prompt that drops those blocks,
and do not paste them from here: the tool is the source of truth for them. Its day seeds map Wednesday
to the book-of-rules mood, Thursday to the machine-under-the-cabinet empathy scene, Friday to the sober
receipt-counting scene, Saturday to the dog-explaining scene [coach-image-prompter].

## Lane B: no cast, and a different image engine

The proprietary cast (Birch / Unit 7 / The Coach / "Be more Birch") never appears in Lane B. Lane B
imagery is evidence-led: real photos of Mike's work, desk and events tested against generated art, with
the result logged in the tracker [li-visuals, hooks-and-media].

Authored portraits and on-brand cards run through the Higgsfield goal-harness at
`~/.hermes/skills/rig-linkedin-image-harness`, a converge-until-proven loop: generate, score every
frame, route gate-passers to a mandatory human approval, seal a ProofPacket only after it [rig-linkedin-image-harness].

## The portrait gate stack (HERO-MAX)

A frame passes only if all four hold [rig-linkedin-image-harness]:

1. tech: the image QA aesthetic score at or above 90% with no failing verdict
2. aspect: dimensions within 3% of the target ratio
3. brand palette: saturated blue/purple coverage at most 5% (off-brand hue guard)
4. identity: face-embedding similarity at or above 0.40 against the reference set, and it FAILS CLOSED
   without an embedder and reference set. There is no fake identity pass.

Then a human must approve before anything is sealed. Pretty is not done [rig-linkedin-image-harness].
An advisory mode that skips identity can generate and score on the other three gates for eyeballing,
but it is not the hero-max bar and never auto-seals [rig-linkedin-image-harness].

Registers: mission-control-soft (daily hero), 3am-architect (manifesto), polestar-hero (keynote/press),
beautiful-beginning (personal). Shots: headshot, editorial, half, environmental [rig-linkedin-image-harness].

The same engine composes on-brand pull-quote cards (design gate, not photo QA) and routes editorial,
pull-quote, portrait and proof concepts from an article extract [rig-linkedin-image-harness].

## Shared prohibitions for any generated asset

No living-person likenesses, no named real humans, no cartoon or illustrated Coach, no photo-realism
that could pass as a real named coach or personality, no text overlays on Coach frames, no fabricated
analytics panels or fake screenshots, no bought or templated stock faces, no QA text in artwork
[coach-image-prompter, li-visuals]. Nothing here schedules or publishes; an approved asset goes to
lv-gate and then to Eden as a draft.

Absorbed from: rig-linkedin-image-harness, li-visuals; tool contract cited: coach-image-prompter.
