# Hook selection: gates, tie-breakers, receipts, ranking

Order is mandatory. A hook that fails any gate is out, regardless of family preference.

## Gate 1: classification

Write: "This post is for <named person> struggling with <specific thing>." A category ("founders",
"agencies") in the sentence is a stop: rewrite before touching hooks. The 2026 feed culls posts it
cannot place. [hook-selection, lg-draft]

## Gate 2: specificity floor

Score the candidate 0-10 for specificity (named entities, dollar amounts, ratios, odd numbers).
Recorded correlation: specificity 8 or more with curiosity 7 or more and contrarian 7 or more lands
in the top verdict band, while specificity 4 or below caps at Reserve. Practical floor: 6, target 8.
Below 6: do not proceed; re-angle the insight instead of decorating a generic one. [hook-selection]

## Gate 3: receipts (hard rule, never waived)

- Every number in the hook traces to a named source: a receipt, a transcript, a named company's
  published figure, or our own measured scoreboard.
- The audit or ledger-reveal family (93) requires named dollar figures with named sources. No ledger,
  no ledger hook. Precedent: a 2026-09-18 package ran the numbered-takeaway family (71) instead and
  recorded why.
- The two-line koan (51) runs only with a named mechanism attached.
- The hook's promise must match what the body delivers. [hook-selection]

## Gate 4: lane check

Lane A and Lane B voice separation is enforced here; the proprietary cast is banned from generic use,
and a hook that needs the other lane's register is a re-lane, not a rewrite. Lane C (a minor) is out
of scope entirely: refuse. [hook-selection, draft-hooks]

## Gate 5: clarity and length

One hook line plus one rehook. Three lines on mobile is too much. Clear beats clever. [hook-selection]

## Scoring and ranking (Jev before any model opinion)

1. Run `rig-s1gate check post.viral --file <hook-set> --subject "hook <id> sha256:<hash>" --json`
   (rubric `post.linkedin` for Lane B). This is a typed judgment and it goes to the classifier
   BEFORE any frontier model is asked which hook it prefers.
2. A pass needs every required noul and confidence above 0.9. Classifier down or rubric missing:
   the ranking is DEFERRED, not guessed, and the hooks stay drafts. [clark:hooks-and-media]
3. Every surviving hook also carries its own two numeric scores from the cross-platform generator
   method: pattern-interrupt strength and fidelity to the claim, each 1-5. Reject anything scoring
   below 3 on fidelity no matter how strong the interrupt. Rank survivors on the combined score.
   [content-hook-generator]
4. Cite the decision id from `~/.rig/s1gate/decisions.db` in any claim that Jev judged the ranking.

## Tie-breakers (in order)

1. Higher honest specificity: odd or unrounded numbers, named entities.
2. Ease-of-use modifier when it is true ("4 simple steps"), never when it is decoration.
3. Family diversity across the week. Do not run one family back to back; the series-cadence family
   is the exception and must be scheduled with every part committed.
4. The recorded library scores rank equals: 93 > 84 > 72 > 71 > 51. Never invent a score. Only those
   five tracks are scored and none is proven on this account.
5. Positioning honesty: without the wins, run student-shaped families (transformation, confession,
   experimentor) and learn in public. Authority-shaped hooks without earned receipts burn trust.
   [creator: Caleb Ralston, n7b0tRx5G6k]
6. Optimize for trust over virality: would the audience police an off-positioning post for Mike?
   If yes, the positioning is doing the work. [creator: Caleb Ralston, n7b0tRx5G6k]

## Validation before the hook leaves the stage

Run the hook validator prompts (`~/.hermes/archived/linkedin-studio/prompts/hook-validation-prompts.md`)
in these three moments: after the hook and before drafting continues, before generating any image or
video asset, and before any sports, song or movie reference post. Any BLOCK is logged and the hook is
fixed or killed; a blocked hook never reaches publish. [hook-validation-prompts]

Absorbed from: hook-selection, content-hook-generator, content-headline-a-b-generator, li-hooks,
hook-validation-prompts, clark:hooks-and-media.
