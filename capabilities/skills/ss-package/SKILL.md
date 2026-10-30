---
name: ss-package
description: >-
  Packaging for a Substack post: title, subtitle, cover image, email subject and preview, and the opening lines. USE WHEN a post needs its title or cover, an issue under-opened, or before any post is published. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of ss-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [substack, ss-growth-os, package]
outcome: "content-publishing: every post leaves with a ranked title, a subtitle that states the payoff, a 3:2 cover image and an opening that earns the second paragraph"
done_when:
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-package/SKILL.md
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/check_family.py ss-package
quality_floor: 0.6
metadata:
  parent: "ss-growth-os"
  laws: "15"
  corpus: "data/corpora/substack (914 transcripts, 27 channels)"
---

# ss-package: title, subtitle, cover image and first lines

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `ss-growth-os`, which `when-growing-social-accounts` routes every Substack job through. An agent meets it before any stage work.

Typed judgments this stage forces: which title wins, does the subtitle state the payoff, is the cover on-brand, does the opening earn the read. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check substack.issue --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `substack.issue` is advisory until calibrated. Substack-specific rubrics `substack.issue` and `substack.note` exist since 2026-09-28 (planted-fixture separation proven, decisions 125944-125948); stages without a Substack rubric use the nearest existing one.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, send, restack, recommend or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use for every post before ss-gate, and to repackage an old post before re-sharing it. Not for the body's structure (ss-write).

## Procedure

1. **Draft five titles** across different families (number, contrarian, how-to, story, named-problem). Keep each under about 60 characters so the email subject is not cut.
2. **Rank with Jev** (`rig-s1gate rank substack.issue --file <titles separated by --->`) on the set; keep the winner and a runner-up for the social preview.
3. **Subtitle states the payoff**: what the reader walks away with, in one line. It shows in email previews and link cards.
4. **Cover image**: every post has one. A real photo or the post's existing LinkedIn image first; otherwise an Eden or generated image in the RIG palette (charcoal, antique gold), no text baked in, 3:2 safe. Set it as the post's first image so Substack uses it as the social preview.
5. **Opening**: the first two lines carry the hook; no throat-clearing, no "In this post".
6. Hand the package to ss-gate.

## Hands the next stage

`package.md`: title (winner and runner-up), subtitle, cover image path, preview text, first two lines. ss-gate checks it; ss-publish installs it.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/substack/notes/ss-package.md` (local corpus, not republished).

- L1. Write the headline before the draft and treat it as the frame of the piece; the opening line then has to pay the headline off. CLAIM(mnHTohgtAMo, NI0TSaYYv8A, ia7UNPjWpZY) | channels: 2 | status: consensus
- L2. Put the niche power words in the first few words of the title, because scanners decide on the first words, not the whole line. CLAIM(IcCoZEHAK_Q) | channels: 1 | status: single-source
- L3. On Substack the subtitle is the SEO description, so the keywords you want found belong in the title, the subtitle and the URL. CLAIM(1KoiLEtMNuk, BRXIY1GJJ7s) | channels: 1 | status: single-source
- L4. Treat the subtitle or preview text as a second hook that sells the click, never as a repeat of the title or the post's first sentence. CLAIM(Oyp2RfmymQE) | channels: 1 | status: single-source
- L5. Title and subtitle must each stand alone, because many readers never see the subtitle; run the swap test before publishing. CLAIM(C79BMJsVCo8, 4kcYqHbmJa8) | channels: 2 | status: consensus
- L6. The title and the cover or thumbnail image are the two elements that decide the click, so budget design time for both, not just the words. CLAIM(HJoqCyOFtuw, KR5XuLaxHG4, 0f89F3a4iqE) | channels: 2 | status: consensus
- L7. Use a 16:9 horizontal header image like a YouTube thumbnail, not a square or vertical, because that is how it renders on the publication page. CLAIM(mHRJfOWzdJQ) | channels: 1 | status: single-source
- L8. A/B or multi-variant test titles and subject lines on the platform itself and let the platform pick the winner, rather than trusting one guess. CLAIM(CkhTN-4aWRU, GxC2VEWFhrg, 7gm0J-aiNbw) | channels: 3 | status: consensus
- L9. The main lever on open rate is the subject line, made tangible and recognizable (name, asset, number), not the content behind it. CLAIM(EAlOdXmIqcs, PpUr7HHEd4g, quAKv-g_-Y8) | channels: 3 | status: consensus
- L10. Judge packaging by the action after the click (subscribe, reply, buy), not by raw click counts; and every post should try to earn the next click. CLAIM(3jl4VoUU_dY, EAlOdXmIqcs) | channels: 2 | status: consensus
- L11. Get the one-sentence idea and a working headline on paper before writing the body, so the piece is organized by the headline's promise. CLAIM(mnHTohgtAMo, NI0TSaYYv8A) | channels: 2 | status: consensus
- L12. The first line carries about two seconds of attention, so it must be specific and a little surprising; numbers in the first line buy extra time. CLAIM(NHlF-3aRiz0, KkCwksLWBpA, ia7UNPjWpZY) | channels: 2 | status: consensus
- L13. Ask for one click per post or per email; multiple competing links and offers make people click none of them. CLAIM(9we4vJ3joys, uhmB0ft0Sq8, xZtrPtlccBE) | channels: 3 | status: consensus
- L14. Numbered promise headlines (three reasons, five mistakes) double as the piece's outline and as a ready-made subject line for list posts. CLAIM(NI0TSaYYv8A, ZzaKLKXlgcw) | channels: 2 | status: consensus
- L15. Run the stranger test on your last five titles: if you would not click it from someone you have never heard of, the title is working against you. CLAIM(Oyp2RfmymQE) | channels: 1 | status: single-source

## Where the creators disagree

Clickbait titles. For: CLAIM(m_gtoaMiWyI, quAKv-g_-Y8) @TheCoachsAlchemist says the newsletter title should be deliberately clickbaity so people feel they must open it.
Against: CLAIM(wEfZgaCq25w, -BY2fkS0G18) @creativelyconsciousUK calls clickbait dead and warns it attracts the wrong readers, and @substackgrowth says community writing moved past titles written purely to get clicks.

Open rate as the metric to steer by. For: CLAIM(Do4_17UQu6k, 4IEBRt8X2f0) @substackgrowth treats a high open rate as the main conversion lever and the thing to protect.
Against: CLAIM(htAB9udet5M, xZtrPtlccBE) @mattgiaro notes privacy scanners inflated opens until the number lost meaning, and @substackgrowth itself says to stop worrying about it as the list grows.

When the headline gets finalized. First: CLAIM(mnHTohgtAMo) headline before the body, since the headline defines the piece.
Last: CLAIM(mb_ei6B9VUc, F2Mg9wxvBAE) @sinemgunel and @creativelyconsciousUK draft with a working title but tighten the real headline after the piece exists.

## Creator result claims (UNVERIFIED, never repeat as fact)

27% newsletter open rate against a stated 18.88% real-estate industry average. UNVERIFIED. CLAIM(EUughLjsbL8)

38.97% open rate on a 5,676-recipient send. UNVERIFIED. CLAIM(U61eyvw_lp8)

Same audience opens at 21-23% on Gumroad versus the 40% range on Kit. UNVERIFIED. CLAIM(gPVfLaswtSk)

One restacked newsletter earned $74 from five new subscribers (three free, two paid). UNVERIFIED. CLAIM(qch_WGVO4uM)

One segmented email with the subject line [quote in corpus notes] hit 74.4% open and 7% click. UNVERIFIED. CLAIM(htAB9udet5M)

Almost always 48-50% open rate across platforms. UNVERIFIED. CLAIM(VjrgK8Ah8A0)

Benchmarks offered as rules of thumb: above 50% open rate is crushing it, below 30% signals a problem, with "40ish" acceptable. UNVERIFIED. CLAIM(EAlOdXmIqcs)

## Platform mechanics (Substack's own channel)

Publication title test: say the name aloud as if on a podcast; it should be memorable, short, easy to say and spell, and the one-line description beside it signals who the publication is for. CLAIM(4qRGmBDUOIw)

Recording Studio auto-generates clip and thumbnail options by scanning the recording as it happens, and the thumbnail and title are fully editable or replaceable with a custom upload. CLAIM(6nT6G_do-6c)

Thumbnail text describing what the conversation is about increases email click-through on video sends, per Substack's own data. CLAIM(6nT6G_do-6c)

For an embedded video in a post, you can add a thumbnail image by clicking the image icon on the video, uploading a new image or selecting a still frame. CLAIM(3OmsGKwkoZo)

## RIG application (RIG synthesis, not corpus claims)

- Package before drafting. Lock a one-sentence idea and a working title first (L11), with the buyer problem and audience named in the first words of the title (L2, L9): for RIG that is phrases like [quote in corpus notes] or "agent fleet", not clever abstractions. Run the stranger test (L15) across all 9 existing post titles before shipping anything new.
- Give every post a subtitle that works as a second hook (L4) and carries the search keywords (L3), and keep title and subtitle independently readable (L5). Right now the preview text slot is doing zero work on a 2-subscriber publication, so this is free upside.
- Use Substack's built-in multi-variant title and subject test on every send (L8), keep the winners in a running repository, and steer by post-click action (booked call, reply, subscribe) rather than opens (L10), since open rates are contested as a metric and RIG's list is too small for open-rate statistics to mean anything yet.
- One click target per post (L13): at RIG's stage that is the subscribe button plus a single CTA, since the Substack exists to convert LinkedIn attention into owned email and then clients, not to sell subscriptions.
- Header images in 16:9 like a YouTube thumbnail (L7); for video or Substack Live assets, write thumbnail text that states what the conversation delivers, because Substack's own data ties that to email click-through. Creator claims about auto-generated social assets (3uMOaySeafs) are reported features worth testing, not proven results.
- First line of every post and every Note must pay off the title within two seconds (L1, L12). With LinkedIn as the only real distribution channel and external links suppressed there, the packaged first line is what travels; the link goes in the comment or the profile, and the Substack title and preview text are what the click lands on.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/title-lab.md` | generating and ranking title and subtitle options |
| `references/cover-images.md` | choosing or generating the cover image |

## Hard rules

- Every post has a cover image; a post without one ships a blank link card on LinkedIn and X.
- No clickbait the body does not pay off; the title's promise must be in the post.
- Numbers in a title need a source in the body.
- Generated images: no text, no logos of other companies, no people's faces presented as real clients.

## Done-test

`python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-package/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ss-package` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
