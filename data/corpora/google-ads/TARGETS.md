# Google Ads corpus - targets and selection evidence

Built 2026-09-28, worker ADS-SKILL (Jake fleet brief `~/.rig/jake/briefs/2026-09-28/ads-skill.md`). Request (Mike, 2026-09-28): "let's do the full meta skill for Google Ads... with skills and subskills... scrape YouTube how-to videos... at least the top channels and then all their videos, including how to do this effectively... put in Jev to make sure all this stuff is done."

## How the channels were chosen (reproducible)

1. Candidate pool from web research (Google Ads teaching channels, 2025-2026): each candidate's full `/videos` catalog enumerated through `yt-dlp --flat-playlist` (uv venv wrapper; the PyInstaller binary is sandbox-blocked). Evidence per channel: `discovery/<slug>.json` — subscriber count, unique video count, long-form (>= 3 min) count, Google-Ads-topic title share, newest/oldest upload, 20 most recent titles, 20 topic titles, full id list.
2. Two probe handles failed (404) and are recorded, not guessed: `@definedigitalacademy`, `@isaacrudansky`, `@adventuremediagroup`, `@PPCMasteryPodcast`; `@MilesMcNair` has no videos tab. The real handles (`@AaronYoungGoogleAds`, `@ppcmasterycom`) were then resolved from search evidence and verified by enumeration.
3. Jev judged every candidate with the `corpus.source` rubric against a SEED defined as Google Ads campaign doctrine from an account practitioner (structure, tracking, keywords, PMax/local, bidding, copy, landing pages, budget, optimization, local B2B). State per candidate = catalog counts computed in code + 20 recent titles + 10 topic titles: `discovery/jev/<slug>.txt`, answers in `discovery/jev/<slug>.json`.
4. Non-vacuity proven first-class: a planted off-subject control (Bon Appetit cooking state) scored composite 0.078 (decision 122018) vs peers 0.401-0.703. The rubric discriminates.
5. **Jev's verdict: every candidate is ESCALATE under the strict bar** (nouls must exceed 0.90; uncalibrated rubric, same outcome as the Substack corpus the same day). The corpus takes the closest available peers, not twins. Decisions 122008-122017.
6. Ordering is code, not opinion: `composite = mean(same_domain, practitioner_voice, argues_not_lists, seed_similarity/5)` from the typed Jev answers (`../../.context/google-ads-creators/jev_rank.py`). Eligibility: >= 15 long-form videos.
7. Scope per channel: full catalog where `--limit` is the quota below (newest first, `--since-days 100000`); channels under 160 videos are captured complete. The quota rule was fixed before any transcript was read: channels with <= 160 videos get full coverage (357 videos), the remaining 1,143 slots are shared proportionally to catalog size across the six large channels. This preserves multi-channel consensus measurement over raw global-newest-first fill.
8. Platform ground truth (not a peer): Google's own @GoogleAds channel scored below several practitioners on practitioner_voice/argues_not_lists by design (corporate channel), and is named here for platform mechanics only. It is NOT captured under the 1,500-transcript cap; platform-mechanics statements in the doctrine cite teaching-corpus windows or are flagged "re-verify in the live product".

## Selected (9 teaching channels; ranking = Jev composite)

| # | channel | handle | subscribers | videos | long-form | topic share | newest upload | composite | Jev decision | scope (targets) |
|---:|---|---|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Aaron Young \| Google Ads \| Define Digital Academy | [@AaronYoungGoogleAds](https://www.youtube.com/@AaronYoungGoogleAds) | 134,000 | 472 | 471 | 86% | 2026-09-28 | 0.703 | 122009 | newest 141 |
| 2 | Jyll Saskin Gales \| Google Ads Coach | [@the_google_pro](https://www.youtube.com/@the_google_pro) | 9,310 | 385 | 343 | 87% | 2026-09-25 | 0.677 | 122013 | newest 115 |
| 3 | The Paid Search Podcast | [@ThePaidSearchPodcast](https://www.youtube.com/@ThePaidSearchPodcast) | 9,210 | 612 | 586 | 65% | 2026-09-28 | 0.669 | 122014 | newest 183 |
| 4 | Grow My Ads | [@growmyads](https://www.youtube.com/@growmyads) | 42,200 | 158 | 151 | 73% | 2026-09-28 | 0.648 | 122012 | full 158 |
| 5 | Ben Heath - Google Ads | [@ben-heath](https://www.youtube.com/channel/UCbQUXtMwQM9QWQ15yDDN1BA) | 101,000 | 143 | 143 | 92% | 2026-08-29 | 0.633 | 122010 | full 143 |
| 6 | Surfside PPC | [@Surfsideppc](https://www.youtube.com/@Surfsideppc) | 267,000 | 983 | 964 | 50% | 2026-09-25 | 0.625 | 122008 | newest 293 |
| 7 | Solutions 8 | [@solutions8](https://www.youtube.com/channel/UCKukXk_pm3om3If9FUsBKew) | 39,100 | 1,014 | 976 | 55% | 2026-09-08 | 0.594 | 122011 | newest 303 |
| 8 | Optmyzr | [@optmyzr](https://www.youtube.com/@optmyzr) | 6,350 | 363 | 263 | 42% | 2026-09-24 | 0.420 | 122015 | newest 108 |
| 9 | Miles & Bob - PPC Mastery | [@ppcmasterycom](https://www.youtube.com/@ppcmasterycom) | 5,860 | 56 | 50 | 91% | 2026-09-08 | 0.401 | 122016 | full 56 |
| - | Google Ads (official) | [@GoogleAds](https://www.youtube.com/@GoogleAds) | 918,000 | 495 | 266 | 61% | 2026-09-23 | 0.445 | 122017 | platform ground truth, not captured |

Planned total: 1,500 transcripts (cap). Beyond the cap each channel keeps its newest videos; skipped catalogs are listed under "Skipped".

## Capture outcome (2026-09-28, final)

1,052 of 1,500 targeted transcripts captured (3,701,862 words, 8 of 9 channels). The shortfall is throttling, not missing captions: YouTube rate-limited the parallel capture (HTTP 429 / "Sign in to confirm you're not a bot"); a paced retry recovered 59 rows before the unauthenticated cookie wall made further grinding pointless (single live probe still 429). Members-only videos were never circumvented.

| channel | targeted | captured | not captured (why) |
|---|---:|---:|---|
| Solutions 8 | 303 | 256 | 47 throttled (429) |
| Surfside PPC | 293 | 76 | 72 members-only (excluded by design) + 145 throttled |
| The Paid Search Podcast | 183 | 164 | 19 throttled |
| Aaron Young | 141 | 123 | 18 throttled |
| Jyll Saskin Gales | 115 | 89 | 26 throttled |
| Optmyzr | 108 | 78 | 30 throttled |
| Grow My Ads | 158 | 133 | 25 throttled |
| Ben Heath | 143 | 133 | 10 throttled |
| Miles & Bob - PPC Mastery | 56 | 0 | 56 throttled (bot wall on the whole channel; selected, uncaptured) |

Machine-readable: `counts.json`, `skipped.json` (target rows not captured), `discovery/<slug>.json` (catalog rows never targeted under the quota).

## Practitioner vs influencer (evidence-backed character of each source)

| channel | character | evidence |
|---|---|---|
| Aaron Young | practitioner-educator; manages accounts since 2010 (agency, retail/health/travel/B2B SaaS) | definedigitalacademy.com "I'm not a marketer who teaches theory"; search evidence |
| Jyll Saskin Gales | ex-Google (6 years) coach; argues from platform internals, coaching audience | jyll.ca about; channel bio |
| The Paid Search Podcast | two working agency specialists (Chris Schaeffer, Jason Rothman) in long-form Q&A argument | paidsearchpodcast.com; 586 long-form episodes |
| Grow My Ads | agency founders (Austin LeClear, Luke Donoghue) teaching from client ecom accounts | channel bio; audit-style video titles |
| Ben Heath | agency founder (Lead Guru); tactic-dense tutorials, some lead-gen framing | channel bio; 92% topic share |
| Surfside PPC | practitioner tutorials (Corey Frankosky); broad PPC/SEO, half the catalog is Google Ads | surfsideppc.com; 50% topic share |
| Solutions 8 | large Google Ads agency (Kasim Aslam, John Moran); PMax/Shopping case-driven, account footage | sol8.com; 55% topic share over 1,014 videos |
| Optmyzr | tool vendor (Fred Vallaeys, Navah Hopkins); panel/webinar formats, product-adjacent | Jev practitioner_voice 0.31 (122015); composite 0.420 |
| PPC Mastery | two agency founders (Miles McNair, Bob Meijer), ecommerce specialist training | ppcmastery.com; 91% topic share over 56 videos |

## Sources

- Per-channel evidence on disk: `data/corpora/google-ads/discovery/<slug>.json` (counts, titles, dates, id lists — generated by `.context/google-ads-creators/discover.py` from yt-dlp flat-playlist enumerations on 2026-09-28).
- Jev state and typed answers: `data/corpora/google-ads/discovery/jev/<slug>.txt|.json`; decision ids 122008-122018 in `~/.rig/s1gate/decisions.db` (rubric `capabilities/harnesses/s1gate/rubrics/corpus.source.json`).
- Subscribers/claims cross-check (web): [surfsideppc.com/pages/youtube](https://surfsideppc.com/pages/youtube) (266K), [definedigitalacademy.com](https://www.definedigitalacademy.com/), [jyll.ca/about-jyll](https://www.jyll.ca/pages/about-jyll), [paidsearchpodcast.com](http://www.paidsearchpodcast.com/), [milesmcnair.com](https://www.milesmcnair.com/), [ppcmastery.com](https://ppcmastery.com/), [sol8.com/about-us](https://sol8.com/about-us).

## Skipped (beyond the 1,500 cap)

Targets were cut newest-first per the quota rule above; per-channel skip lists are the tail of each `discovery/<slug>.json` `all_ids_newest_first` (anything after the quota index) and are re-listed in `manifest.jsonl`'s companion `skipped.json` after capture. Channels not selected at all (probed, kept out of the corpus):

| channel | handle | reason |
|---|---|---|
| ppcmastery (unrelated) | @ppcmastery | 3 subscribers, 3 videos; name collision with @ppcmasterycom |
| Isaac Rudansky / AdVenture Media | @isaacrudansky, @adventuremediagroup | no enumerable channel under probed handles; no verified handle found |

Recording rules for all downstream doctrine: transcripts stay local (creators' copyrighted words; `data/corpora/google-ads` carries derived analysis only). Skills paraphrase and cite `CLAIM(videoId)`; creator result numbers are UNVERIFIED and never repeated as fact; advice tied to a platform feature is dated and flagged for re-verification.
