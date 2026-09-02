# Source licence: what the capability pipeline may keep

The pipeline reads other people's work: YouTube videos, auto-generated captions,
video descriptions, arXiv papers, and open-source repositories. This file states what
RIG keeps, where, and why. `scripts/scrape_channel_corpus.py` and
`docs/CORPUS-DISCOVER-AI.md` both point here, so this is a load-bearing document, not
a disclaimer.

## The line

| artifact | whose words | where it lives | in git? |
|---|---|---|---|
| `.vtt` caption files | the creator's, machine-timed | `.context/**/raw/` | no |
| `.info.json` (uploader metadata) | the creator's, plus YouTube | `.context/**/raw/` | no |
| cleaned transcript | the creator's words, ours cleaned | `.context/**/transcripts/` | no |
| video description | the creator's | `.context/**/descriptions/` | no |
| dossier / capability matrix | ours, quoting sparsely with attribution | `.context/**/dossiers/`, `capability-matrix.json` | no (working notes) |
| provenance record | ours | `docs/CORPUS-DISCOVER-AI.md` | **yes** |
| a capability that survives verification | ours, implemented in our code and prose | `capabilities/**`, `rig_capabilities/**` | **yes** |

Auto-captions are a mechanical transcription of a creator's speech. They are not our
content, and a git repository full of other people's transcripts is a redistributable
copy of their work with our name on the commit. So the raw layer stays in the working
directory, regenerable at any time by re-running the scraper, and only **derived**
analysis ships: a mechanism described in our words, a paper id we verified, a repo we
checked exists, and at most a short quotation carrying the video id so any reader can
go to the original.

Quotation rule for anything committed: cite the video id and the paper id, quote only
the phrase that carries the claim, and never paste a run of transcript. If a claim
needs a paragraph of someone's script to stand, it is not our claim to publish.

## The paywall rule

Some uploads are channel-membership content. When yt-dlp cannot fetch captions for one,
the run records the failure string it got (`no_captions`, or `members_only` where that
is what it reported) and moves on. **There is no code path in this repository that
attempts to reach membership content by other means, and none will be added** — no
cookie injection, no third-party mirror, no downloader flag. A gap in the corpus is a
fact about the corpus.

## Papers and code

- An arXiv id may be cited only after `weekly_capability_scout.py stage` resolves it
  against the arXiv API in that week's `week.json` (`verify_arxiv`). An id that does
  not come back is a rejection, recorded as one.
- A GitHub repo may be cited only after `verify_repos` sees it via `gh api`, which also
  records stars, SPDX licence and last push. A repo that 404s is a rejection: an
  implementation claim resting on it is dropped, not softened.
- Verified repos are third-party or author-released code under whatever licence the
  API reports (`none` and `NOASSERTION` both appear). RIG may read them and describe
  the mechanism; **vendoring code out of them is a separate decision that needs the
  licence read, not assumed**, and any vendored file must carry its provenance.
  Nothing in this increment vendors code.

## Enforcement

`tests/test_source_license.py` fails the suite if any transcript, caption, or
`.info.json` under a `.context/` corpus directory is tracked by git. The check is
deliberately a *tracked-files* check, not a gitignore check: gitignore drifts, the
index is what ships. Its own plant-failure — staging a fake transcript and watching it
go red — is the regression story recorded with the test.

## Retention

`.context/` is disposable by design: `git clean -xfd` loses the corpus and nothing
that matters is unrecoverable, because the durable output is the verified matrix and
the assets built from it. Keep it local; do not sync it to a shared drive as though it
were a knowledge base.
