# Scorecard and critic: how a draft is judged

## Critic discipline

The drafter never scores its own draft. The critique runs in a separate session and, where a choice
exists, a model family different from the writer's. If they share a session or family, refuse to score
and report `blocked` instead of a number. Read only the draft, the hooks, the stated lane and the
classifier line: the drafter's rationale biases the review toward defense [lg-critique].

## The scorecard (8 criteria x 5 = 40, reported as /10, ship floor 8/10)

| # | Criterion | 1 | 3 | 5 |
|---|---|---|---|---|
| 1 | Classifiable | reader is a category | reader implied | reader named in line one |
| 2 | Hook | generic | states topic | survives the word budget, opens a loop the body pays off |
| 3 | One idea | several | two | exactly one, one point per line |
| 4 | Dwell shaping | wall of text | some breaks | whitespace, rhythm, mobile-legible, no orphan lines |
| 5 | Save-worthiness | opinion | interesting | a framework or checklist someone deploys later |
| 6 | Voice | AI-sounding | mostly Mike | unmistakably him, no slop tells |
| 7 | Truth | unverified claims as fact | mostly sourced | every number carries an evidence class; none is another creator's |
| 8 | Next step | none or hard sell | a CTA | one soft step, the week's only ask if give-4:take-1 is spent |

Output shape: `score`, `failing` (numbered criteria with the specific defect), `block` (any hit),
`verdict` (ship / rewrite / kill). No praise paragraphs: "8/10, good work" is a failed output. "Kill"
is a valid answer when the post does not need to exist this week [scorecard, lg-critique].

A claim without an evidence class fails criterion 7 even when the prose is excellent. A claim only Mike
can settle is flagged for him, never silently softened [lg-critique].

## Data-backed scoring (when the account has history)

Generic advice is the weak baseline. When post history exists, score the draft against the account's
own top-decile performers instead:

- Compute a simple engagement score per historical post (reactions plus a weighted comment count) and
  take the top decile as the reference set [post-scorer].
- Extract from that set: which hook types recur, typical length, format mix, CTA patterns, topic
  clusters and sentence rhythm. Note the bottom decile too, so what fails is visible [post-scorer].
- Score the draft on hook, voice match, value density, structure/format and publish readiness, each
  against those observed patterns, and say which pattern a fix serves [post-scorer].
- Never score a draft as top-tier unless it genuinely matches the top-decile patterns; an inflated
  score is worse than no score [post-scorer].
- Data older than about two weeks is flagged as stale before it is used. Pulling fresh history through
  a paid scraper needs a heads-up about the cost first [post-scorer].
- If no history exists, say so and score against the structural scorecard only. Do not import another
  creator's benchmark numbers as this account's bar [post-scorer].

## Second opinions

A multi-voice critic panel may run as a second opinion. When the panel and the primary critic differ by
more than 2 points, escalate the disagreement to Mike with both rationales; never average [lg-critique].

Absorbed from: scorecard, lg-critique, post-scorer.
