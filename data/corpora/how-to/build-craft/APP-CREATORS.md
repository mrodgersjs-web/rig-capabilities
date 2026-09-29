# App Studio creator corpus (10 channels)

Generated 2026-09-28 19:55 by capabilities/skills/app-studio/scripts/build_creator_registry.py.
Raw captions and transcripts are local and gitignored under `.context/app-creators/` (creators' copyrighted words);
these registries carry ids, titles, sha256 and word counts only. Scope: each channel's /videos tab;
Shorts and live streams are not enumerated.

| channel | url | targets | transcribed | words | still missing |
|---|---|---|---|---|---|
| Code With Antonio (`code-with-antonio`) | https://www.youtube.com/@codewithantonio | 44 | 40 | 3,277,369 | 4 |
| Codesistency (`codesistency`) | https://www.youtube.com/@codesistency | 47 | 8 | 1,102,571 | 39 |
| Simon Grimm (`galaxies-dev`) | https://www.youtube.com/@galaxies_dev | 654 | 10 | 337,050 | 644 |
| JavaScript Mastery (`javascript-mastery`) | https://www.youtube.com/@javascriptmastery | 183 | 55 | 2,318,182 | 128 |
| Josh tried coding (`josh-tried-coding`) | https://www.youtube.com/@joshtriedcoding | 250 | 6 | 709,798 | 244 |
| Lama Dev (`lama-dev`) | https://www.youtube.com/@LamaDev | 108 | 54 | 1,002,015 | 54 |
| notJust․dev (`notjust-dev`) | https://www.youtube.com/@notjustdev | 83 | 10 | 282,923 | 73 |
| Piyush Garg (`piyush-garg`) | https://www.youtube.com/@piyushgargdev | 549 | 4 | 36,017 | 545 |
| Sonny Sangha (`sonny-sangha`) | https://www.youtube.com/@SonnySangha | 137 | 46 | 2,012,557 | 91 |
| Traversy Media (`traversy-media`) | https://www.youtube.com/@TraversyMedia | 1032 | 51 | 678,356 | 981 |
| **total** | | 3087 | 284 | 11,756,838 | |

Why coverage is partial: YouTube answered HTTP 429 and a bot check after the first parallel pass
(2026-09-28 ~09:10 MDT). `.context/app-creators/resume_scrape.py` keeps fetching one video at a time
when the block clears (status in `.context/app-creators/status.json`; stop it with a PAUSE file).
