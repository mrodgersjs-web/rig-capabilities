# Miner brief: one stage dossier -> one doctrine notes file

You are mining one Google Ads corpus dossier into doctrine notes. The dossier is
deterministic evidence windows cut from captured YouTube auto-captions; every window
is headed `[videoId | @handle | title]`.

Input: `data/corpora/google-ads/dossiers/<stage>.md`
Output: `data/corpora/google-ads/notes/<stage>.md` (write it exactly)

## Output format (exact sections, in order)

```
# <stage>: <one-line stage title>

## Laws

L1. <paraphrased law in one or two sentences> CLAIM(<videoId1>, <videoId2>) | channels: <N> | status: consensus
> "<verbatim quote>" (<videoId1>, @<handle1>)

L2. ... status: single-source
> "<verbatim quote>" (<videoId2>, @<handle2>)

## Contested

<points where the corpus disagrees; quote both sides with citations>

## Dated advice

<advice in the corpus tied to platform mechanics or eras that have changed (e.g. SKAGs,
old match-type behaviour); name the video date; state what changed>

## Creator result claims

<numbers creators claim about their own results ("we cut CPA 40%"); each line ends
UNVERIFIED and is never repeated as fact>

## Platform mechanics

<mechanics claims (settings, UI, policy) with citations; each flagged re-verify in live product>

## RIG application

<3-6 lines: how RIG applies these laws to local B2B / small-budget accounts. RIG synthesis,
not corpus claims. No quotes here.>
```

## Hard rules

1. Every law is a PARAPHRASE, never transcript wording. Verbatim transcript text appears ONLY
   inside `> "..." (videoId, @handle)` quote lines. The quote must be a verbatim substring of
   that video's transcript window (normalised punctuation allowed); a checker enforces this and
   fabricated quotes are a failure.
2. `CLAIM(...)` carries only real 11-character YouTube ids that appear in the dossier.
   A checker resolves every id against the corpus registry; a fake id is a failure.
3. `status: consensus` requires the law in windows from >= 2 distinct channels (count channels,
   not videos). Otherwise `status: single-source`.
4. 8-14 laws per stage. Prefer consensus laws; keep single-source ones that are actionable.
5. Nothing may be attributed to a creator by name in Laws unless the quote carries it.
6. If the dossier for your stage is thin on a topic, say so under Contested or omit; never pad.
