# Reply handling on Mike's own posts

The inbound half of this stage: comments land on Mike's posts and get answered fast, in his lane voice, with something worth reading [alfred-comment-engagement]. Clark's first-24-hours rule and this SLA agree: be present in the first hour and reply to every comment, ideally with a question that extends the thread [distribution-and-algorithm].

## Windows

- **SLA window:** posts published in the last 24 hours. A comment inside this window must be answered this cycle or the 2-hour response target is missed [alfred-comment-engagement].
- **Operational scan window:** always scan the last 72 hours. Mike's cadence often has zero posts in a strict 24h window while 72h holds 5-8, and the only live comment in two validated cycles sat on a 43-47h-old post [alfred-comment-engagement].
- The SLA clock for a found comment starts at the comment's own timestamp, not at scan time [alfred-comment-engagement].
- Filter by state before the date check: only published posts are engagement-eligible; queued posts with future dates are skipped and logged as such [alfred-comment-engagement].

## Comment-type routing

- **Positive:** thank them anchored on a phrase in their comment, add one specific insight, ask a follow-up [alfred-comment-engagement].
- **Negative:** answer with evidence, never argue, thank them for the perspective, end with a question [alfred-comment-engagement].
- **Question:** answer with numbers or proof and cite the source inline [alfred-comment-engagement].
- **Spam:** ignore. No reply, no response log row [alfred-comment-engagement].
- **Prospect (ICP match):** reply publicly first, then queue a DM follow-up through the outreach stage; the DM itself is Gate-D [alfred-comment-engagement].
- On Mike's own threads, mirror and label instead of pitching: repeat back what they shared, name the dynamic, keep them talking (Firth relaying Chris Voss, MnQc73VYbJ0). Every reply ends with a question that needs their expertise [engagement-comment-led].

## The reply canon

Three parts, in order [alfred-comment-engagement]:

1. **Appreciation**, 2-5 words, anchored on a specific phrase from their comment.
2. **Value**, 1-2 sentences: one data point, named framework, or sourced insight. No self-promotion, source cited inline.
3. **Question**, open-ended, driving the next reply or DM. Yes/no fails.

Banned openers: "Great post!", "Love this!", "Couldn't agree more.", "Spot-on", "Nailed it" [alfred-comment-engagement].

## Three gates before a reply sends

1. Anti-fingerprint: unique within the batch, no shared opening paragraph across replies [alfred-comment-engagement].
2. Value: a specific number, named framework, or cited source; generic praise without a payload never sends [alfred-comment-engagement].
3. Engagement driver: ends with an open-ended question [alfred-comment-engagement].

## Transport and honest reporting

- Walk the transport ladder live each cycle before declaring no work: CDP probe, browser process check, cookie check, CLI session check with a hard timeout, public JSON-LD read of the post URL. Never cache a prior cycle's verdict; the moment a transport recovers is the moment comments become answerable [alfred-comment-engagement].
- Engagement-zero and transport-zero are independent: "no comments exist" and "we cannot read comments" are different reports and the log must say which fired [alfred-comment-engagement].
- When every transport fails, report zero honestly: posts scanned, per-post comment counts, transport status per step, and the next concrete remediation step. Never fabricate replies or reply counts [alfred-comment-engagement].
- A stable blocker state across identical cycles may report the quiet token instead of a user-facing message, but the structured log write still happens every cycle, and a first blocker, a cadence gap, or a change in transport coverage always gets a real report [alfred-comment-engagement].
- Replying still needs an authenticated transport or a human; a comment drafted from a public read is staged, not sent [alfred-comment-engagement].

## First 24 hours after a post

Be present in the first hour and reply. Ask two or three real people for real comments only on big moments. Do not delete a slow post early; distribution is spiky and can arrive hours later [viral-core, Clark in s6KMjhznXqs]. At 24 hours the learnings go to lv-measure, not here.

Absorbed from: alfred-comment-engagement, engagement-comment-led, viral-core, tommy-clark-doctrine/references/distribution-and-algorithm
