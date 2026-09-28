# Surfaces and reach math: where the numbers live and what a target means

## Where each number lives

| Number | Surface | Trap |
|---|---|---|
| 7-day post impressions, reach, engagements | creator content analytics | windowed: label the window every time |
| one post's impressions | post analytics via the activity URN | a post is editable; re-read before quoting |
| profile appearances and channel split | search-appearances analytics | the "% change" is versus the prior window, not absolute |
| avg view time, clicks | creator analytics, engagement view | dwell is what the current ranker weights; read it beside impressions |
| "post impressions" in the feed sidebar | right rail on the feed | unlabelled and longer than 7 days: never compare to a 7-day figure |
| follower count | not exposed by the available API | missing is unknown, not zero |
| comment impressions | the individual comment's analytics | own comments can earn their own impressions |

Access notes: the creator analytics URL can hard-redirect to login while a tab shows an authenticated
feed, so the cookie cache and the browser session are two separate surfaces. `getUserPosts` can fail in
a cold session that worked hours earlier; fall back to the author's recent-activity page. Degraded
renders are surface-specific: a thin render is a stop signal, and never submit a form into one
[analytics-surface].

## The 16x lesson

Comparing the feed sidebar's unlabelled "post impressions" to the creator-analytics 7-day figure
produced a 16x error on first pass. Compare like for like: 7-day against 7-day, window label attached
[analytics-surface, reach-math].

## How to state a target

Impressions = posts x per-post distribution. Per-post distribution is decided in the first 60-90
minutes by whether the post clears a small interest-matched test group. Exactly four levers exist and
they have hard ceilings [reach-math]:

| Lever | Ceiling | Notes |
|---|---|---|
| Effort on own posts | about 5,000-15,000/week from this base | an honest 8-25x on current numbers |
| Fake, ghost or pod engagement | negative | inert under percentile scoring and re-classifies the audience |
| Paid amplification | about 7,000-10,000 per $300 at a $30-45 CPM | the standing cap is $300 total; buying 200K costs roughly $1,300-3,000 |
| Borrowed distribution (a larger relevant account reshares) | one event, unbounded, unschedulable | the only route to six figures in a week |

The rule: report a target as range + basis + which lever it depends on. "200K this week" is a tail
event, not a schedule. State ticket count, per-ticket odds and expected value separately; expected value
is where the plan lives [reach-math].

Context for any 2025-vintage target: independent benchmarking puts views down about half year over
year, engagement down about a quarter, follower growth down about 59%. The denominator shrank, so a
2025 target applied to 2026 is not the same ask [reach-math].

Absorbed from: analytics-surface, reach-math.
