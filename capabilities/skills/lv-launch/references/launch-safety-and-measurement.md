# Launch safety, verification and measurement

## Caps and pacing

- Per session: about 30 comments or about 45 follows, not both. Roughly 100 profile loads in one session degrades profile rendering.
- Count the day's comments across every surface, including replies written on his own post. Replies count toward the cap and toward whatever a scheduled sweep adds later the same day; if an interactive batch ran, say so in the routine's memory so it caps itself.
- Space actions 60-210 seconds apart with real jitter, never a fixed interval. Comments and follows go on separate days.
- Behave like a person, because detected automation is capped, not blocked: vary comment length deliberately, vary the opening clause, like a post before commenting, sometimes answer inside an existing thread. A uniform block of same-length, same-shaped comments is the recognizable pattern.
- A link in roughly one comment in four or five. Repeating the same link at volume reads as spam.

## Stop signals: halt writes immediately

Blank page shells where only the nav renders. Redirects to an auth wall, a checkpoint, or an unavailable-company page. "Hold on a bit" or any maximum-limit or restriction copy. Edit overlays that never mount. Feed and search working while profiles render empty is still a stop signal; the healthy surfaces mask it.

## Verification rules

- Verify every write by reading the result: hard reload plus the posted string present exactly once. Never `document.body.innerText`, which includes unsent composer drafts and once "confirmed" 13 of 16 replies that had never posted.
- Never report a write as done from a click. Unsent composer drafts make page text a lie.
- Never submit into a degraded render; a thin body is a stop signal.
- Assert the signed-in handle before every write. This browser holds Mike's and a client's session at once.
- Read the live draft back out of Eden after staging; a write call is not persistence evidence.

## Measurement discipline

- One before-and-after number is a story, not a rate. Measure the same post at repeated short intervals (10-20 minutes) and report the delta series, because the shape is the finding: a rising delta means distribution is still expanding and effort is worth spending; a falling delta means second-day decay has begun and the remaining levers are a second save asset and a follow-up post, not more comments.
- A burst of activity that coincides with a rise is correlation; say which it is.
- Log into the scoreboard file the measurement routines already read, never a new one. Each record is stamped at the moment the number was read, and no local offset is ever attached to a UTC instant.
- Watch Sends and Reposts in post analytics. Both are cheap to move and a DM share is a top-weighted signal.

## The launch report

Always report: post age; impressions before and after; comment count before and after; each write verified individually; the delta series if more than one reading was taken; every action not taken with its reason. Never claim "viral" is achievable on demand.

## Funnel note (why the launch is not the end)

The attention a launch buys lands on the profile and then has to be converted: comment or post reach, profile visit, follow or connect, conversation, pipeline. Engagement volume placed before the profile funnel is closed wastes the attention it buys, so a launch on an unfinished profile is a known leak. The conservative automation rule also lives here: almost all automation violates the platform's terms and three shutdowns is permanent, so nothing on this account sends or connects in volume without Mike's explicit approval.

Absorbed from: linkedin-post-launch, lg-amplify, step-6-amplify, distribution-pipeline.
