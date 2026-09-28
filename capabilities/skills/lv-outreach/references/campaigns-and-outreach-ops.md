# Campaign learnings and outreach operations

What running an actual campaign taught us, the DM corpus doctrine that binds every campaign, and
how the follower-outreach engine is operated. Campaign mechanics are copied from receipts, not
reconstructed.

## Dykema 2026 campaign receipts (20/20 sent, 57 events, 27 errors, 6 browser sessions, about
55 minutes)

- Fresh browser per DM. Reusing a session degrades after about 14 sends; the compose editor stops
  appearing; the driver crashes with EPIPE after 3+ sessions. Never reuse a session for more than
  5 DMs [dykema-dm-campaign-learnings].
- Profile-page path over compose-page for batches: compose works for 1-5 DMs, fails
  intermittently at 6-14, consistently at 15+. Search, open the profile, use the Message button.
- Multiple send-button selectors with an Enter fallback, `force=True` clicks, and Escape after
  typeahead selection before clicking the editor.
- Pacing 60-120 seconds between sends. Cookie session lifetime about 24 hours (li_at); never send
  on stale cookies.
- The style correction is first-class: the first 16 DMs ran 80-150 words and formal; the rewrite
  to short, informal, positive was the entire quality gap (107 words and 45/100 quality down to
  55 words and 84/100). Predicted reply rate moved from 3-10% to 20-33% on the rewritten four.
  These are internal predictions, not measured RIG reply rates.
- Second-agent review is never skipped: research agents gather hooks from the target's actual
  content, one agent drafts, a second checks hook specificity, length, tone and ask clarity, the
  quality scorer runs (target 80+), then Mike approves.
- Variant diversity is mandatory: all 20 sent DMs were one variant (long, podcast hook,
  conference ask), which is why the campaign could not learn. Generate short (45-word) and medium
  (60-word) variants and mix ask types; the generator assigns stratified variants before drafting.
- CRM pipeline pattern: auto-sync from send and reply logs into stages target, sent, replied,
  booked, met, deal; dedup sends by rank (retries exist); cumulative funnel counts; an event audit
  trail per transition; context-aware next steps (monitor inbox for sent-with-no-reply, follow up
  HOT immediately, send a booking route to replied-not-booked).

## Darius outreach agent

Owns DM campaigns end to end: conference campaigns from attendee lists, cold campaigns with 1st
degree verification, follow-up sequences, reply monitoring every 2 hours (HOT routed to Mike
within 2h), and DM quality scoring with A/B tracking. Hard rules inherited: no live sends, no
connection requests to strangers, no replies on Mike's behalf without his approval; max 15 DMs
and 8 connection requests per day; never contact someone already in the CRM; never send on stale
cookies; a suppression list is checked before every campaign [darius-linkedin-outreach-agent].

## The DM corpus doctrine (2026-09-21, 21 practitioners)

Three competing theories of change, named not resolved: fast-triage broadcast (default for Lane B
cold lists of 100+), trust-thread (small list, high-ticket, 10-15 accounts/month), and the
chase-override (permission-led, gated). The gate layer enforces the floor; the operator picks the
model. Gates wired that stage: `no_link_in_cold_dm`, `one_question_per_dm`,
`chase_sequence_override`, `personalization_specific` extended with trigger phrases,
`message_ceiling`, `connect_note_policy`. This corpus owns the operator decision layer; the
existing DM engine code owns tracking and cadence. It is not a publisher: a blanket "approve
everything" does not clear a batch, and Lane C is excluded at every approval level. The
triangulation is mirrored in three places with the Developer repo canonical
[linkedin-dm-corpus-2026-09-21].

## Follower-outreach engine (luca-studio)

Daily LinkedIn-only batch (goal 45, followers first, vertical prospects when followers exhaust),
deterministic with no LLM calls in the send, gate, classify or rank path. Hard skip gates in
order: F1 never message Oracle / Oracle Health / Cerner employees; F2 never message anyone on the
skip list (Jon Llaguno); F3 90-day sent-log dedup; plus a CAIO/CTO/CDO cap of 5/day for the
compare-notes template. Classify to Template A (general referral, default), B (peer compare
notes, cap 5), C (clinical), then intent-rank the gated batch (ranking never re-admits a gated
person). Dry-run is the default: it seals a proof of what it would send and sends nothing. Live
sending is Gate-D: the CDP transport to the real logged-in Chrome, `RIG_LIVE=1` plus a single-day
ARMED token plus a watched 1-2 send test plus Mike's typed approval; a ban signal auto-disarms
and halts; the bot never auto-answers a prospect. North-star: booked discovery calls per week;
sends are telemetry. Sony Jacob may be messaged outside the standard flow. Every session ends with
a sealed proof packet or it is not done [linkedin-follower-outreach].

## Safety numbers to hold exactly when operating any campaign

60-120s between sends; never a browser session for more than 5 consecutive DMs; never the compose
page for batches over 5; profile loads cap about 60 per session; comments cap 30/day; cookie
refresh before the ~24h li_at expiry; DMs under 70 words; connect notes that send measured at 180
characters. Re-probe any LinkedIn platform limit before quoting it: published caps move
[dykema-dm-campaign-learnings, dm-sequences, lg-client-engine].

Absorbed from: dykema-dm-campaign-learnings, darius-linkedin-outreach-agent,
linkedin-dm-corpus-2026-09-21, linkedin-follower-outreach.
