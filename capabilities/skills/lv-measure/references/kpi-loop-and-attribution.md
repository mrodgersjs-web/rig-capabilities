# KPI loop and attribution: reading the numbers into next week's plan

Rule zero: write what you measure; anything unmeasurable is recorded as null, never estimated. The
baselines were deliberately left empty at the start so nothing downstream could inherit invented
winners. Preserve that discipline [measurement-kpi-loop].

## Per-post capture

Impressions at t0, t+90 minutes and end of day from post analytics; comments with commenter identity
(flagging commenters who match the ICP segments); profile views as the attribution path for
comment-led growth; website clicks per post paired with GA4 as a FLOOR ONLY (consent defaults deny and
global privacy control is honored, so it is never a count); follower delta weekly, not per-post. Rows go
to the dated scoreboard files, and the true publish state goes to `publish_log.json`
[measurement-kpi-loop].

## The evidence bar

- No tactic is called a winner before about 10 posts of data carry that tactic.
- Only measured winners enter the hook library. The stub copy of that library is intentionally empty:
  do not "fix" it by copying scores over. Until 10 posts prove otherwise, nothing has won, and that is
  the honest state.
- One day's observation proved tail-extension, not breakout. Single observations are not laws
  [measurement-kpi-loop].

## Attribution caveats

- Eden's link tracking rewrites post links to its redirect domain, which is not in the site's
  measurement allowlist, so that traffic collapses into other. Either the allowlist gains the redirect
  label or link tracking stays off. The site script is cached immutably, so a returning visitor may run
  the old allowlist: confirm the asset URL changed, not just the origin bytes [measurement-kpi-loop].
- UTM vocabulary is closed: only allowlisted campaign and content labels attribute. Anything invented
  collapses into other [measurement-kpi-loop].
- Self-reported attribution is first-class: ask every lead how they heard about us and log the answer
  where the tracker reads it [outbound-and-pipeline].
- Newsletter metrics, if opened, are impressions and engagement only; subscriber emails are not
  exposed, so a newsletter funnel's downstream is unmeasurable from the platform side: record null
  [measurement-kpi-loop].

## Hypothesis arbitration

The corpus carries two competing algorithm models: dwell plus early-velocity semantics versus
buyer-matching with views down and revenue up. Both stay live as hypotheses; only measured account data
arbitrates, one variable at a time (for example impressions-versus-qualified-clicks divergence per
post). Platform-general heuristics from other creators are never imported as targets without a
LinkedIn-measured counterpart here [measurement-kpi-loop].

## The loop (weekly, Friday)

1. Pull per-post rows for the week: impressions, comments, profile views, clicks, ICP match.
2. Score formats against each other (carousel vs photo-text vs text-only vs video), one variable at a
   time; never two changes inside one comparison window.
3. Feed winners into next week's plan: hook family choices (lv-hooks), format choices (lv-visuals),
   slot choices. Losers get one second life as a re-cut in a new format before being retired.
4. Record deltas in the scoreboard with dates, and name what did NOT change in the same file.
5. Weight the loop toward clicks over vanity: impressions, likes and comments have trended down
   platform-wide while clicks trended up. A 5,000-impression post that produced qualified clicks beats a
   100,000-impression post that produced none [measurement-kpi-loop].

## Program-level KPI

The measurement program reports against its own outcome contract: from no analytics to real
analytics with engagement prediction and optimization, and at program level the north star is booked
ICP calls per week with impressions and followers as corroboration only. Every metric maps to one
action or it is dropped [rig-top100-analytics-content, li-measurement].

Absorbed from: measurement-kpi-loop, rig-top100-analytics-content; cross-referenced: outbound-and-pipeline
(self-reported attribution).
