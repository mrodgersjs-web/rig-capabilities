# Lane hook rules, the hook brief, and A/B design

## Lane differences that change the hook

- **Lane A (personal brand, Eden, Ted Lasso register):** a pop-culture opening is allowed and proven.
  Mike's best-performing post opened on a pop-culture frame carrying an AI-hiring thesis, which is the
  borrowed-credibility lever in practice. Keep the cast rules tight: Birch is Tuesday only, The Coach
  appears only from behind or in silhouette, and no cast member appears on Lane B or the client lane.
- **Lane B (RIG B2B):** evidence-led, named receipts for every number, no mascots, no pop-culture
  frame. The strongest shapes are results-first with a real number, contrarian with a receipt, and an
  admission about a killed project. A vulnerable hook must land on an operational lesson, not on
  feeling. [hook-lab, draft-hooks]
- **Ideawake client lane (Coby Skonord's account):** hooks are drafted only. The browser may be
  signed in as Coby, so assert the handle before any action; nothing fires without Mike's explicit
  client approval, and Mike's voice and cast never travel to this lane.
- **Job-search lane:** a hook may not assert anything the resume cannot evidence.
- **Lane C (a minor):** out of scope in this stage entirely. Refuse the envelope and hand it to Mike.

## The hook brief (the contract handed to Eden)

Eden generates the final copy and brand assets. The brief below is what this stage produces; the
draft line is a starting point for Eden to beat, not the copy.

```
family: <name + library score if one of the five scored tracks>
why_this_family: <1-2 lines, including which receipts are available>
classification: "This post is for <person> who struggles with <thing>"
hook_line: <draft line for Eden to beat>
rehook: <the line-two payoff pointer>
receipts: <source per number, or NONE>
lane: A | B | client | job
body_architecture: <from lv-draft: references/post-architecture.md>
constraints: no link in body, 2-3 hashtags max, no engagement bait, receipts gate passed <date/who>
```

## A/B pair design

- Pair variants that differ in exactly one named variable: number versus no number, question versus
  statement, benefit versus curiosity. Never two variables in one pair. [content-headline-a-b-generator]
- State for every pair: the isolated variable, the hypothesis, and the metric that resolves it. A
  test with no hypothesis is not a test.
- Rank pairs by expected information value, not by which line sounds best.
- Enforce length limits and banned words mechanically, not by eye.
- The resolving metric is the account's own baseline signal (dwell, saves, in-ICP profile views),
  not another creator's reported numbers. [viral-core]

## Validation sequence for a hook set

1. Selection gates pass (see `hook-selection.md`).
2. Jev ranking recorded or explicitly DEFERRED.
3. Hook validator prompts run (hook gate first; image and reference gates when those apply).
4. Brief written and handed to Eden; no copy leaves this stage authored here.

## Conflict log (kept and dropped)

- Formula-style generator output (fixed two-line shape with a hard character budget) versus the 2026
  rule that formula phrasing reads as machine output: the 2026 rule wins, and the generator's angles
  survive as raw material only.
- The prompt library allows 3-5 hashtags while house law caps hashtags at 2-3: the stricter cap wins.
- The hand-raiser opt-in pattern's comment-word delivery versus the engagement-bait kill list: prefer
  a saveable first-comment asset over comment-gated delivery until the contradiction is resolved.

Absorbed from: hook-selection, hook-lab, li-hooks, content-headline-a-b-generator,
hook-validation-prompts, draft-hooks, clark:hooks-and-media, viral-core.
