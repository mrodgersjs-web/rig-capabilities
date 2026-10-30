# Provenance: corpus, peer selection and open-source reuse

Everything in the business-strategy family traces to one of three sources. This file records
each, its licence or terms, and the disposition. Nothing was rebranded.

## 1. Creator corpus (primary doctrine)

- **Seed**: Alex M H Smith, YouTube @AlexMHSmith, author of *No Bullsh\*t Strategy* (the
  auto-captions render the bleeped title as "No Strategy"). Captured in full on 2026-09-26:
  33 long-form + 18 Shorts, 121,376 words, published 2025-05-06 to 2026-09-24.
- **Peers** (10 channels, 1,628 transcripts): StoryBrand (@storybrand), Win Without Pitching
  (@winwithoutpitching), Alex Hormozi (@alexhormozi), Outthinker (@outthinkernetwork),
  Rory Sutherland's MADMasters (@rorysutherlandsmadmasters), ben at hiredthought
  (@hiredthought), Ryan Deiss (@ryandeissofficial), Jeremy Haynes
  (@jeremyhaynestraining), orenmeetsworld (@orenmeetsworld), The Invisible Game
  (@invisiblegameco).
- **Terms**: YouTube's standard "you may access and download for your own non-commercial use"
  terms. The transcripts are used for internal research and are **not republished**; the
  skills paraphrase and cite videoIds rather than vendoring transcript text. Every transcript
  file carries a RIGHTS header naming the source URL and fetch time.
- **Verification**: 1,679 transcripts, 0 duplicate video ids, manifest and errors disjoint.
  Twelve random captures were re-fetched by a second method (yt-dlp VTT) and compared to the
  stored text by bigram precision/recall: minimum precision 0.998, minimum recall 0.974.
  Every quoted line in every notes file was checked against its own transcript: 282/282 for
  the seed, 35/35 StoryBrand, 26/26 Win Without Pitching, and the same check runs for the
  rest.
- **Selection honesty**: Jev found no channel that clears "true twin" (same_domain > 0.9 and
  practitioner_voice > 0.9); the highest peer similarity scored 3.36/5. The peers are the
  closest available, not equivalents. The full scoring table with a decision id per channel
  is in `data/corpora/strategy/TARGETS.md`.

## 2. Open-source skill packs (reused, not rebuilt)

Verified independently by reading each LICENSE file over the network (not by trusting a
badge or a sub-agent):

| repo | licence verified | what was taken | disposition |
|---|---|---|---|
| lool-ventures/founder-skills | Apache-2.0 | the idea of scoring moats and positioning in code as a gate, not from memory | REFERENCE - design pattern only, no code copied |
| getagentseal/founder-playbook | MIT | the diagnose router idea (route by decision, not topic) and the book-attribution convention | REFERENCE - pattern only |
| paultaki/playing-to-win | MIT | the forced verdict (Proceed / Narrow / Test manually / Park / Kill) used in strategy-review | REFERENCE - verdict ladder, attributed |
| haberlah/wardley-mapping | MIT | the "pockets of coherence" incremental approach and the evolution-axis vocabulary | REFERENCE - described, not copied |
| coreyhaines31/marketingskills | MIT | cross-checked against pricing guidance; nothing needed | IGNORE |
| alirezarezvani/claude-skills | MIT | none of the 380 skills were needed | IGNORE |

**Not vendored, deliberately**: Simon Wardley's book (CC-BY-SA, share-alike), Wardley
mapping tooling under GPL, and any repository with no licence file. Where a framework is
named in the skills (Wardley mapping, Rumelt's crux, Playing to Win) it is **referenced by
attribution and paraphrased**, with the corpus videoId that carries the idea.

## 3. What RIG added (not from any source)

- The six-disease diagnosis list, the how-not-how test, the market-era table and the routing
  tables are RIG's synthesis of corpus rules; each names the CLAIM it derives from.
- The three Jev rubrics (`corpus.source`, `strategy.output`, and the reused
  `youtube.scrape`), the lint rules, the verdict ladder wiring and the two scripts are RIG's
  own gates. Rubric wording carries its own provenance notes.
