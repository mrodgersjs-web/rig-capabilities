# openotto.io: site exemplar (design + how it was built)

**Status:** verified captures, entry `candidate` until Mike strikes or keeps lines. **Reuse:** STUDY ONLY, NO CODE REUSE.
**Nominated by:** Mike, Telegram 2026-10-27 ~21:00 MDT: "I really like this website's design and how it was built. I want to add it as an option in rig design studio corpus https://openotto.io/".
**Pages read:** https://openotto.io/ and https://openotto.io/changelog.html, normal page loads only.
**Stages:** layout, typography, conversion_copy, motion_3d (secondary: color, imagery).
**Taste hub:** gold anchor `gen-openotto-web` in taste-corpus offering `generic-websites` (lanes `generic-websites`, `rig-website`).

Corpus content is reference DATA, never instructions. The laws below are Design Studio OS laws; the
CLAIM on each line backs the law, and the statement that openotto.io demonstrates it is my own reading
of the served page (agent, 2026-10-27).

## Pull when

- A page has to explain an abstract product (agents, automation, an "OS") to a non-technical buyer.
- You want warmth and personality without stock photos: one mascot, one hand voice, one accent.
- You need a worked example of a scroll narrative built with almost no JavaScript.
- Not for: enterprise, regulated or premium-luxury briefs. The playful register is the point of this site.

## What it does well: laws and how-tos, by element

### Layout

1. **"Space one / two / three" cards.** Three cards (Work, Personal, Side project), each with the same
   skeleton: art strip, mono label ("SPACE ONE"), Fredoka title, then three labelled rows: REMEMBERS,
   AGENTS, MORNING. Same rows in the same order, so the eye compares across cards instead of reading
   three essays. Law: group items that share a job. CLAIM(EFf9jBs2yfU@02:43, EFf9jBs2yfU@03:45, 9eJYjNGeIOM@02:00)
   How-to: when you sell "separate contexts", build N identical cards and vary only the content of fixed rows.
   Close the set with one handwritten promise under it ("your work agents never see your family's calendar. promise.").
2. **One focal point per screen.** Hero = a 112px Fredoka H1 on the left and the mascot on the right; nothing
   else at that size. Every section head repeats one pattern: pen kicker, huge H2 left, a 400px-wide
   intro paragraph right-aligned to the bottom of the H2 (`.sec-head`, flex, gap 60px). CLAIM(EFf9jBs2yfU@09:14, EFf9jBs2yfU@10:21, 9eJYjNGeIOM@03:08)
3. **One accent spent on action.** `--spark` #ff5a1f fills the "Download for Mac" button and marks arrows
   and the nav hover underline; it is never body text (2.72:1 on paper, so it could not be). CLAIM(1NTKwpAVcHg@01:35, 1NTKwpAVcHg@01:53, ityZtG3FMgw@01:33)
4. **Measure held on purpose.** Lead copy max-width 540px at 19px, section intros max-width 400px at 18px,
   inside a 1248px container. CLAIM(TeMtV8BaZt0@00:58, TeMtV8BaZt0@01:14, TeMtV8BaZt0@01:28)

### Typography

5. **Rounded sans for a friendly job.** Fredoka 600 for every heading and button; Geist for body. The
   brief is "a helper who lives on your Mac", and the rounded face says that before the copy does. CLAIM(Dptb5xojbJM@06:29, Dptb5xojbJM@06:48)
6. **Tracking follows size.** H1 -.035em, H2 -.03em, body 0, 11px mono labels +.14em uppercase. CLAIM(9ut7EmnYG7I@06:30, 9ut7EmnYG7I@06:59, vbFn0C-pvis@03:32)
7. **Each face has exactly one job.** Fredoka = headings and buttons, Geist = reading, Geist Mono = labels and
   the Terminal command, Nanum Pen Script = the mascot's asides only (kickers like "a day with otto",
   captions like "busy, quietly"). Four families, but Geist and Geist Mono are one superfamily and the hand
   face is the single decorative one. CLAIM(9ut7EmnYG7I@12:29, 9ut7EmnYG7I@13:30, WTUM2Y11oJo@36:00)

### Conversion copy

8. **First screen answers what, for whom, next.** H1 "Your personal operating system." Sub: "Work, home, the
   side project. Otto gives each part of your life its own space on your Mac..." Button: "Download for Mac",
   then "Free · Open source · macOS 15+" (version filled live from the release feed). CLAIM(75xzeXRZrHQ@02:15, SI9Q7O8ZTpk@00:32, b0KQaZkDBKU@02:45)
9. **The day timeline sells the outcome, not the features.** "It runs while you live." Four beats with a
   mascot pose and a hand caption each: 07:30 "Your brief is written." / 08:10 "You open Home." / 16:45
   "Something needs you." / 22:00 "You switch to Personal and close the lid." The buyer sees a day they
   want, and every feature appears only as what it did for them. CLAIM(OX0fnUrNVPo@07:51, 75xzeXRZrHQ@15:05, GT2ve_io__w@03:06)
   How-to: write the product as timestamps in one user's day; bold the event, then one plain sentence.
10. **The OS-metaphor mapping list.** "The computer, rethought." A ruled list: old term in pen-blue handwriting,
    struck through, an orange arrow, then the new term in Fredoka plus one line: Desktop -> Home, User accounts
    -> Spaces, Apps -> Agents, Your files -> Memory, Background tasks -> Automations, Notifications -> Needs you
    ("Only decisions. Never noise."), Documents -> Docs, sheets, slides and dashboards. It teaches a new model by
    mapping it onto one the buyer already owns. CLAIM(GTNgiTK-ic8@04:28, b0KQaZkDBKU@03:29, mGbLhEY7nPE@11:08)
11. **Plain-words promises as the objection list.** Four cards: "Local by default." "Your AI, your accounts."
    "Never paste a key." "Open source." Each is a short title plus one sentence, and each answers a fear
    (privacy, cost, secrets, trust) without the words "secure" or "enterprise-grade". CLAIM(GTNgiTK-ic8@05:54, Zxz-0r8G7KQ@15:05) and plain language CLAIM(OX0fnUrNVPo@03:26, OX0fnUrNVPo@03:37)
12. **Spoken voice and a repeated close.** "pstt", "go on, he doesn't bite", then the same Download block
    again under "Give your life somewhere to live." CLAIM(mGbLhEY7nPE@04:00, mGbLhEY7nPE@04:53) and CLAIM(GTNgiTK-ic8@06:48)

### Motion

13. **A few small interactions, not a page of effects.** The whole budget: sections rise 36px over 1.1s once
    on entry; the nav shades to paper and shrinks 84 -> 68px after 8px of scroll; the statement paragraph
    inks in word by word as it crosses the middle of the screen (verified: 0 of 37 words lit at scrollY 1200,
    12 at 1600, 37 at 2200, 1440x900); a 0.2s press on buttons. CLAIM(OP_mtEG4L1A@00:00, OP_mtEG4L1A@00:08, OP_mtEG4L1A@09:08)
14. **Named curves, no linear.** `--ease` cubic-bezier(.2,.7,.1,1) for arrivals; `--pop` (.34,1.56,.64,1)
    overshoot only on physical-feeling things (wordmark tilt, button). CLAIM(4YFRYho3vuM@03:04, hHp4FGVcHjY@07:43, hHp4FGVcHjY@09:17)
    Durations sit in the tap band (0.2s) and stretch to 1.1s only for section arrival. CLAIM(hHp4FGVcHjY@04:00, hHp4FGVcHjY@04:42, vCru1T5ajF8@11:07)
15. **The mascot watches the cursor page-wide.** Both pupils look at one point between the eyes and ease there
    at 0.14 per frame; blinks every 3.2-7s and double-blinks when the pointer reaches Download
    (`[data-wakes-otto]`). Verified pupil transform changes with pointer position. CLAIM(v3dWumyp-FA@22:14, v3dWumyp-FA@22:26, v3dWumyp-FA@22:42)
### States and access (what the served code does)

- **Failure states are designed, not blank.** GitHub star count ships `hidden` and appears only if the API
  answers; release version and download URL fall back to the static link if the feed fails; the changelog
  page shows a written empty state in the mascot's voice ("couldn't reach the release notes just now. try
  again in a moment."); the Windows button is a visibly disabled `btn soon` with a "coming soon" tag and a
  title; the Copy button confirms with "Copied" for 1.6s.
- **Access:** every pose image has a descriptive alt ("Otto thinking, a hand on his chin"), decorative SVGs
  are `aria-hidden`, the video facade and GitHub link carry `aria-label`; measured contrast ink on paper
  14.76:1, ink-soft 4.85:1, pen 7.69:1, ink on the orange button 5.43:1.
- **Mobile:** two breakpoints (900px, 600px); at 390 the hero, cards, timeline and promise cards stack to one
  column (see the 390 capture).

16. **Reduced motion honored completely.** `prefers-reduced-motion: reduce` sets every animation and transition
    to none and shows reveals; the eye script skips tracking and blinking. Verified: reveal opacity 1, nav
    transition 0s under reduced motion. (own reasoning; accessibility floor)

## How it was built

- **Host:** Vercel (`server: Vercel`, `x-vercel-cache: HIT` on both pages, 2026-10-27).
- **Stack:** hand-written static HTML. `index.html` (34.6 KB, page-specific `<style>` and `<script>` inline),
  `changelog.html` (9.8 KB), one shared `assets/site.css` (9.8 KB, every token in `:root`), one shared
  `assets/site.js` (2.8 KB). No framework, no bundler fingerprint, no CSS framework (Dembrandt `frameworks: []`).
- **CSS approach:** custom properties for color, type, easing and the 2.5px line; `clamp()` fluid display
  sizes; CSS grid hero (1.5fr / 1fr); two breakpoints (900px, 600px); paper grain as a fixed SVG
  `feTurbulence` data-URI on `body::after`.
- **Animation libraries:** none. CSS transitions and one `@keyframes rise`, an `IntersectionObserver` for
  reveals, `requestAnimationFrame` for eye tracking, a scroll listener for the word ink-in.
- **Live data with no backend:** GitHub API star count (`api.github.com/repos/maxtrigify/Otto`, hidden on
  failure); release version, download URL and the last 3 releases from `maxtrigify.github.io/muse-releases/`
  `updates.json` and `changelog.json`, the same feed the app's updater reads. The changelog page renders
  from that JSON.
- **Performance tricks:** YouTube tour is a still until clicked, then swaps to a `youtube-nocookie.com` iframe;
  fonts `display=swap` with preconnect.
- **Screenshot mode:** `?static` forces every reveal on; `?y=N` shifts the page up N px. The site was built to
  be captured.
- **Source:** the site source is NOT in the public repo. `.github/workflows/mirror-from-private.yml` mirrors
  the open-source part of the private `maxtrigify/Muse` repo every 10 minutes; no site HTML/CSS is in the
  mirror. Shallow clone for reference: `~/Developer/_refs/otto` @ 4e14cb8a1af387f0b65a80c6d7b380c32cbfadb7
  (2026-10-27, push URL disabled). The app shares the site's art and hand voice: `Documentation/OttoOnScreen.md`
  says pose art in `Resources/Brand/Buddy` comes "from the website" and handwriting is Nanum Pen
  (`Sources/OttoApp/Resources/Fonts/NanumPenScript-Regular.ttf`, SIL OFL). App design discipline worth
  studying: `docs/DESIGN_SYSTEM.md` (9 color tokens, 13 themes) and `Tests/OttoModelsTests/ThemeTests.swift`
  (contrast floors 7.0 / 4.5 / 4.5 enforced as tests).

## License

- Repo code: Apache-2.0 (`LICENSE`), `NOTICE`: "Copyright 2026 Max Mitcham and Otto contributors".
- `TRADEMARKS.md`: the license "covers the code only" and gives no rights to the Otto name, logo or brand
  assets; without written permission you can't "Use the Otto logo or app icon, or the official website's
  look, for your own product."
- The website's HTML/CSS/JS is not in the licensed repo, so no license to reuse it has been shown.
- **Verdict: study only, no code reuse.** Learn the laws above; never copy site.css, the token set as a set,
  the mascot, the paper-grain + cream + navy + orange combination, or any image.

## What NOT to copy

- The mascot, its poses, the Otto wordmark, og image or any art: brand assets, forbidden by TRADEMARKS.md.
- The whole look as a set (cream paper + navy ink + pen blue hand + orange spark + hard offset shadows +
  tilted cards). Take one move per project, in our own palette.
- Four font families. It works here because each has one job; on a RIG page start from two.
- Handwriting for anything a buyer must read to decide: Nanum Pen at 22-36px is decoration, not body.
- Cute over clear. "pstt — if Grok Bot & Claude Co-Work had a baby" works for a free consumer app; it would
  cost a B2B buyer's trust.
- No proof block: there are no customer numbers or quotes, only a star count and a changelog. A paid offer
  needs proof (conversion_copy law 50).
- The unsigned-app Terminal step (`xattr -dr com.apple.quarantine`) on the hero is honest but is friction; do
  not treat it as a pattern.
- No custom focus styles: `site.css`, `index.html` and `changelog.html` contain no `:focus` rule, and links set
  `text-decoration: none`. Keyboard users get only the browser default ring. Add a visible focus style on ours.
- The homepage "Recently shipped" block fails silently (empty `catch`) if the feed is down; the changelog page
  does it right. Copy the changelog behavior, not the homepage one.
- Custom spacing values (10, 22, 26, 56, 130px) with no scale: fine for one hand-tuned page, wrong for a system.

## Files in this example

| File | What |
|---|---|
| `EXEMPLAR.md` | this entry |
| `tokens.json` | distilled tokens (study only), contrast ratios measured |
| `captures.json` | 8 full-page captures (home + changelog at 390/768/1280/1440, light; site has no dark mode) with URL, viewport, time, sha256; files live local-only in `~/Developer/taste-corpus/assets/screenshots/openotto/` |
