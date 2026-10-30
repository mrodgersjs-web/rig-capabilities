# Post-flight measurement protocol

The Nintendo post taught the expensive version of this lesson: **we measured activity and called it reach.** Five "reposts" turned out to be five of our own group posts. This protocol exists so that cannot happen again.

Rule: **count third-party actions only.** Everything Mike's own account produced is marked SELF and excluded from every reach or engagement figure that feeds a decision.

---

## 1. Denominators

| Metric | Counts toward decisions | Why |
|---|---|---|
| Impressions | yes | reach |
| Members reached | yes, above impressions | deduplicated humans |
| In-network / out-of-network split | **yes** | the only evidence distribution got past followers |
| Reactions | weak | cheapest signal, most gameable |
| **Saves** | **yes, weighted highest** | strongest "worth keeping" signal available |
| **Sends** | **yes, weighted highest** | someone forwarded it privately |
| Third-party comments | yes | must be an account that is not Mike's |
| Third-party reposts | yes | **verify the resharer is not Mike** |
| Profile viewers from this post | yes | attribution LinkedIn will actually give you |
| Followers gained from this post | yes | the conversion the campaign exists for |
| SELF group posts | **never** | self-distribution, not amplification |
| SELF author comment | **never** | it is not engagement |
| SELF reposts | **never** | measured at 2 likes median vs 28 for an original |

## 2. The one check that prevents the Nintendo error

Before reporting any repost or share count, **open the list and read the names.** The Nintendo post showed "5 reposts" for four days. Every one was Mike. Zero third-party amplification existed.

```
post page -> click the "N reposts" counter -> read each resharer
  resharer == Mike  -> label SELF, exclude
  resharer != Mike  -> label THIRD-PARTY, count
```

A repost counter you have not opened is not a measurement.

## 3. Reading procedure (read-only)

1. Assert identity first: nav "Me" menu, confirm `mike-rodgers-ai`. Halt on Coby or any other handle.
2. Post page -> "View analytics" -> read `Impressions`, `Members reached`, `In-network % / Out-of-network %`, `Profile viewers from this post`, `Followers gained from this post`, `Saves`, `Sends`.
3. Open the repost counter, classify each resharer SELF / THIRD-PARTY.
4. For each group post, open the group and read the post's own reactions and comments. A group feed that renders thin has not loaded its posts: **absence there is not proof.** Deep-scroll, or use the post's repost entry, before reporting zero.
5. Comment replies: the comments activity page shows **no reply count**. Replies only render after expanding the thread. Distinguish "observed zero" from "could not observe" explicitly.
6. Record the audience demographics and compare them to the ICP. If the top location is not the market, that is a finding even when impressions look respectable.

## 4. Checkpoints and what each one triggers

| Reading | Verdict | Action |
|---|---|---|
| Out-of-network > 30% and third-party actions > 0 | distribution is working | keep the framing |
| Out-of-network < 10% | followers-only echo | change the framing, not the schedule |
| Audience top location outside Denver/US enterprise | ICP mismatch | rewrite the head; the vocabulary selected the wrong room |
| Saves + sends == 0 | content verdict | do not amplify; fix the post first |
| Third-party reposts == 0 | no amplification exists | a self-repost will not create it |

**Hard rule:** if saves and sends are both zero, **do not amplify the post further.** Amplifying a post nobody kept pushes a declined asset back into a feed that already rejected it.

## 5. The vanity ledger

Count these, report them, and never let them decide anything on their own: impressions, reach, reactions, follower count, comment volume, self-reposts.

They are reported alongside the meaningful set so Mike sees the whole picture, and they are explicitly labelled vanity in the output so they cannot quietly become the headline.

## 6. Timing

The T+24h check exists to let a stalled post be changed while it still matters. On the Nintendo post the heartbeat fired **three days late** and the checkpoint said nothing actionable. If the T+24h read cannot run on time, that is itself the finding and must be reported as such, not silently delivered as "T+24h".
