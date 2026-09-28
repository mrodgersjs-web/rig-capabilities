# Daily and weekly tracker: what to measure, where, when

## Per-post metrics and their surfaces

Source: the post analytics page for the activity URN. Impressions (raw reach), members reached
(deduped), in-network percentage (how much leaked past followers), reactions (weakest signal), comments
(weighted about double a reaction), saves (strongest signal), organic reposts minus self-reposts, sends
(DM shares, top-weighted, usually zero), profile views, followers gained, website clicks (the only
metric tied to revenue) [linkedin-analytics-tracker].

Group posts: read the group page header for member count and the post page for reactions and comments;
group post impressions are unavailable, so use engagement as the proxy. Reddit and trade-pub status
rows live in the same cross-channel log (upvotes, comments, upvote ratio, pitch/response/published
dates, UTM-tagged referral traffic) [linkedin-analytics-tracker].

## Cadence

| When | What |
|---|---|
| Post day, T+1h | first read: impressions, reactions, comments |
| Post day, T+4h | second read: the delta series, is distribution still expanding |
| Post day, T+24h | full snapshot of all post metrics plus group metrics |
| End of day | profile views, follower count |
| Weekly (Friday) | cross-channel summary: posts, groups, Reddit, trade, podcast |
| Monthly | trend analysis: engagement rate, reach per post, follower growth rate |

Capture also runs at t0 and t+90 minutes per post for the loop's scoreboard [measurement-kpi-loop,
linkedin-analytics-tracker].

## The delta series

One before-and-after number is a story, not a rate. Measure the same post at 10-20 minute intervals and
report the series: rising delta means distribution is still expanding and effort is worth spending;
falling delta means second-day decay is starting (switch to save assets and follow-up); flat delta means
the distribution test stopped expanding and the post is done [linkedin-analytics-tracker].

## Storage

Daily metrics go to the account's routine memory and the lane's project page in this block: date, post
identifier, impressions with day-over-day delta, reactions / comments / saves / sends, organic versus
self reposts, profile views, group rows, Reddit rows, trade-pub and podcast status. Per-post rows also
go to the dated scoreboard files, and the TRUE publish state is appended to `publish_log.json` (every
entry frozen at QUEUE is the defect this loop exists to end) [linkedin-analytics-tracker,
measurement-kpi-loop].

## Reporting rules

- Separate organic from self-generated: a repost from Mike's own company page is a distribution action,
  not a virality signal.
- Report what did NOT change beside what did ("sends stayed at zero" is as important as "comments rose").
- Never report a number from a cached or stale snapshot; re-read the analytics page immediately before
  reporting.
- A burst of activity that coincides with a metric rise is correlation; say so instead of claiming cause
  [linkedin-analytics-tracker].
- Report what moved, what did not, what the number cannot tell you, and the one decision it forces;
  state plainly when a post's expansion window has closed [lg-measure].

## Baselines

Establish per-account baselines from the first 10 measured posts; until then, report raw numbers without
trend claims. The existing cross-account table has the client account's historical post count and
reaction/comment averages, but its per-post impressions are still to be measured; Mike's row is
unmeasured. That is a gap, not a zero [linkedin-analytics-tracker].

Absorbed from: linkedin-analytics-tracker, lg-measure.
