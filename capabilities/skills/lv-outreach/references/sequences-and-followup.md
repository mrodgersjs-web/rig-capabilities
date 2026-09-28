# Sequences, follow-up, and reply ops

Spacing, ceilings, what silence routes to, how replies are classified, and what happens between
booking and call. The sequence owns the ask and the spacing; it never owns the send.

## Sequence shape

Warm-up-led (default Model A): blank connect at day 0; wait about 5 days for the accept, then 2
more; a profile view; one like a day later; then the first DM with the offer and the ABCD close;
follow-ups at +3 and +6 days under the message ceiling [dm-sequences].

Multi-touch structure, for any channel: touches sized by warmth (hot at most 2, warm at most 4,
cold at most the cap), geometric spacing (2d, 4d, 8d), asks escalating value-first then soft then
direct, and a final breakup-style close. Exit immediately on any reply, a booked meeting, a hard
bounce, or an explicit opt-out [gtm-outreach-sequence-architect, synthesized]. A 4-6 touch cold
sequence keeps every touch under 90 words, one idea each, a new angle or value per touch (never a
bump), and a CTA answerable in one word [cold-outreach-sequence, synthesized].

Engine variant for the follower queue: Day 0 initial DM, Day 3 follow-up (3 sentences, 30-40
words), Day 7 final nudge (2 sentences, 15-25 words), then stop permanently. Shorter each time,
a different angle each time, and never a touch after any reply. Kill an underperforming variant
after 10 sends, scale the winner [linkedin-followup-sequence].

Darius campaign cadence matches: Day 0 initial, Day 3 different angle, Day 7 final nudge, Day 10
stop. Reply monitoring every 2 hours, HOT replies routed to Mike within a 2h SLA
[darius-linkedin-outreach-agent].

## Ceilings and the named contradiction

- Three messages per prospect, then stop. "Replies start going a bit sour anything above three
  messages" [creator, lg-convert].
- The 9-step chase is an override, not a default: `chase_sequence_override` requires a
  `chase_reason` naming the moment permission to pitch was granted, `cross_platform: ["linkedin"]`,
  `pattern_interrupt_only: true`, and a declared `followup_step_max` of 4-9 [opener-recipes].
- One corpus voice follows up open-endedly "until they say yes or no" [creator]; refused in favor
  of the 3-message ceiling [followup-cadence].
- A prospect who ran a Model A sequence and stayed silent is not fresh for Model B; either dormant
  for 6 months, then one re-engagement with a fresh current signal, or a noted-connect override
  with a named reason [followup-cadence].

## Follow-ups carry value or they are bumps

Five shapes, never the same shape twice in one sequence: one-pager or framework; a YouTube video
with no opt-in; a case study after they name the problem; a specific observation of them for
re-engagement; a single question. Model B gaps are 5-7 days, each touch answering one named
objection ("has this worked for anyone else", "could I do it myself", "how long until results").
No breakup template exists yet in this packet; when `dormant_6mo` fires, send nothing for 6
months; when `stop_permanently` fires, never again on any channel [followup-cadence,
pre-call-nurture].

## Reply routing

Queues [inbox-triage]: HOT (ABCD A, or a price/scope/timing question) same working day; WARM
(ABCD B, substantive reply) within 48h with one specific artefact attached; DORMANT (ABCD C or
3-message silence) untouched for about 6 months; CLOSED (ABCD D or explicit no) never touched
again from this lane; NOISE (recruiter, vendor, spam) no reply. Anything unclassifiable goes to
Mike, never into a queue: a wrong D ends a relationship and the cost is invisible in metrics.

Expanded shapes [reply-handling]: B2 qualified ("how much is it") clarify value then call; B3
punt ("send info") value drop then call; C2 soft reject park 3 months; warm-busy ("busy this
week") re-engage in 72h; silent-positive (liked or commented, no reply) re-engage with value;
D-urgent ("stop") terminate immediately on all channels; a low-energy reply (looks like a no,
ends with no question) gets the ask lowered for one round, value delivered, then the question
re-posed. The probe ladder (surface state, trigger, duration and cause, desired state, then the
specific close question) is for B2, warm-busy and silent-positive only. A silence is not a
verdict: four mundane reasons beat one narrative about being ghosted.

A reply is a continuation, not a new pitch; read the whole thread first. A replies get a real slot
offered, never a bare link. Every outbound reply is Gate-D like any send, with the signed-in
identity asserted first [inbox-triage].

## Pre-call nurture (between booking and call)

Confirm-and-thank immediately (may be a video); 2-4 value touches on alternate days, each
pre-answering one objection (testimonial, case study, result timeline); a day-before reminder
that states the call structure; one same-day cross-channel reminder. Ben's acceleration vehicles:
social proof pasted into the DM 2-3 days out, a no-opt-in YouTube video 3-5 days out, a lead
magnet 5-7 days out only when the value is mechanism-shaped. Links are permitted here because the
prospect has booked. Skip the nurture for short calls and small deals, and for prospects who asked
for minimal contact [pre-call-nurture].

## Measurement that keeps it honest

Track reply latency per queue and the A/B/C/D distribution per batch: a batch of mostly C and D is
a qualification or offer failure and routes there, not to better copy. Every claimed creator
reply-rate figure (24% cold, 85%, 10x, 70-80% warm) is a creator claim and may not appear in RIG
or client copy; RIG's reply rate comes from RIG's own ledger or it is not stated
[dm-sequences, followup-cadence].

Absorbed from: dm-sequences, followup-cadence, no-reply-ladder, reply-handling, inbox-triage,
pre-call-nurture, cold-outreach-sequence, gtm-outreach-sequence-architect,
linkedin-followup-sequence, darius-linkedin-outreach-agent.
