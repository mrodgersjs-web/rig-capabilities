# how-to corpus — coverage report (never estimated; generated from disk)

Generated: 2026-09-08 (post batch1/2/3 authenticated scrape, errors-prune, think-media retry)

agent-craft: 248 transcripts
comms-craft: 250 transcripts

Manifest: 498 rows, 498 unique video_ids, 0 duplicates.
Errors: 88 rows (80 per-video + 8 channel-level terminal).
Attempt-complete (G3): manifest ∩ errors by video_id = 0 (90 stale error rows
pruned 2026-09-08 — each superseded by a later successful fetch, err_at < fetched_at, verified per row).

## agent-craft (12 targets)

| transcripts | errors | channel | status |
|---:|---:|---|---|
| 25 | 0 | indydevdan | complete |
| 25 | 0 | sonny-sangha | complete |
| 25 | 0 | cole-medin | complete |
| 25 | 0 | matt-wolfe | complete |
| 25 | 0 | 1littlecoder | complete |
| 25 | 0 | david-ondrej | complete |
| 25 | 0 | ai-jason | complete |
| 25 | 0 | liam-ottley | complete |
| 25 | 0 | wes-roth | complete |
| 19 | 6 | prompt-engineering | 6 no-vtt failures |
| 3 | 2 | vellum | live enumeration holds 3 videos (@vellumai dead → @vellumhq, verified via yt-dlp 2026-09-08) |
| 1 | 0 | brandon-hancock | live channel holds 1 candidate video (fetched=1, errors=0) |

## comms-craft (13 targets)

| transcripts | errors | channel | status |
|---:|---:|---|---|
| 25 | 0 | charisma-on-command | complete |
| 25 | 0 | alex-hormozi | complete |
| 25 | 0 | garyvee | complete |
| 25 | 0 | noah-kagan | complete |
| 25 | 0 | thomas-frank | complete |
| 25 | 0 | ali-abdaal | complete |
| 21 | 4 | nathan-barry | 4 no-vtt failures |
| 15 | 10 | the-futur | 10 no-vtt failures |
| 12 | 3 | roberto-nickson | live enumeration 12 fresh + 12 existing (@RobertoNickson 404 → @rpn, ownership verified via per-video titles 2026-09-08) |
| 2 | 0 | marketing-examples | live channel holds 2 candidate videos (fetched=2, errors=0) |
| 0 | 3 | justin-welsh | TERMINAL: no usable upload channel — @thejustinwelsh 404; @justinwelsh live with zero uploads (no videos/shorts/streams tabs); channel-type YouTube search finds no Welsh upload channel; his appearances are guest slots on other channels (verified 2026-09-08) |
| 0 | 8 | think-media | live /videos enumeration returns 4 candidates only; all 4 failed both lanes (3× no-vtt, 1× transcript-too-short) on two independent runs 2026-09-08 |
| 50 | 2 | shannon-jenkins | 51 enumerated, 50 fetched (1× no-vtt for qZh5_oFfMLY), 335k words; storytelling/presenting/speaking credibility (2026-09-10) |

## Terminal handle replacements (probe evidence 2026-09-08)

- Vellum: `@vellumai` (no tabs) → `@vellumhq` (3 videos, all fetched)
- Roberto Nickson: `@RobertoNickson` (404) → `@rpn` (legacy path `youtube.com/robertonickson` resolves identically; per-video titles match)
- Justin Welsh: `@thejustinwelsh` (404) → `@justinwelsh` (official empty upload channel; zero candidates — terminal id-list error rows are the honest outcome)

## Method notes

- Every yt-dlp call authenticated (`--cookies-from-browser chrome`, `COMMS_COOKIES=1`); channel tabs use
  `--extractor-args youtubetab:skip=authcheck` (public channels fail authcheck under foreign-account cookies).
- One channel per worker (`COMMS_ONLY=<slug>`), sleep 4s, batches of ≤7 against the quota bucket.
- Scraper: scripts/scrape_writing_craft.py, MAX_PER_SOURCE=25 (env override via COMMS_MAX_PER_SOURCE), idempotent on manifest video_ids.
- Shannon Jenkins scrape used COMMS_MAX_PER_SOURCE=60 and `--remote-components ejs:github` (yt-dlp JS challenge solver).

## build-craft (2026-09-25)

tubeguruji: 220 transcripts (channel @tubeguruji, "TubeGuruji" / Rahul, 2022-2026; full-channel enumeration
via YouTube innertube browse pagination: 221 videos total, 220 fetched + 1 no-caption failure in errors.jsonl).
~6.6M words / 39MB. Method: Aside browser youtube global (timestamped caption tracks), NOT yt-dlp.
Manifest rows carry title/url/duration_seconds/views/published + sha256; transcripts are timestamped ASR text.
Distilled into capabilities/skills/tubeguruji-doctrine (+ tg-* pillar/sub skills).
