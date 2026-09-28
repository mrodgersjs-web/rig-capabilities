# Profile audit and read-only probes

Run the audit against a real profile and output pass/fail per row plus the fix. A strong post dies on a weak profile: content is judged alongside the profile, never by itself [profile-audit].

## The audit (10 rows)

| # | Check | Pass when |
|---|---|---|
| 1 | Follow mode | Settings > Visibility > Followers: follow is the primary action. It retro-converts connections to followers and counts rejected requests as follows. Two minutes, do it first [profile-audit] |
| 2 | Headline | job title plus who is helped plus how; a title alone fails [profile-audit] |
| 3 | Photo | shoulders up, current, professional; not a camera-roll crop [profile-audit] |
| 4 | Banner | sells what is posted about, not the product; no stock art, no hard sell, light on text [profile-audit] |
| 5 | About | addressed to the reader with worked examples of people like them; a CV shape fails [profile-audit] |
| 6 | Featured | best trophies first: a strong post, a case study, a testimonial [profile-audit] |
| 7 | Custom URL | the name, not digits [profile-audit] |
| 8 | Next step | exactly one explicit route: email, DM, or booking page. Spoon-feed it [profile-audit] |
| 9 | Keywords | the 10-target extraction woven into headline and About as prose [profile-audit] |
| 10 | 60-second classifier audit | who viewed the profile; if the titles are not the ICP, fix content, messaging and profile together and re-check in about a month [profile-audit] |

## Executor / verifier pair (step 8)

- Executor: read the live profile and record current field values verbatim; run the 60-second audit and report a ratio with a denominator; extract the keyword set from 10 real targets; produce a field-by-field change list (field, current, proposed, why, which reader); emit the envelope with the surface-hydration probe result attached [step-8-profile].
- Verifier: re-read at least two current field values independently (a change to an unconfirmed field is a blind write); refuse any plan that submits into an overlay whose dialog was not observed; verdict pass / fail / unsure [step-8-profile].
- One change set per month unless the measured audit says otherwise; the audit re-checks in weeks, not days [step-8-profile].

## Read-only probe mechanics (profile-probe)

1. Assert identity first (getMe-style read) and compare against the expected handle; halt on mismatch. The browser can hold Mike's and a client's LinkedIn at once and an account chooser showing both is a live condition [profile-probe].
2. If the identity read throws "no cookies", invalidate the cache once and retry; that error is not proof of logout. If it still fails, report blocked and never click through an account chooser [profile-probe].
3. The profile API read returns headline, experience, education but no About and no follower count: record those as unknown, never zero, never "absent" [profile-probe].
4. Post history: use the posts API read first (cheapest full history, works on public slugs). Fallback: the author's own recent-activity URL taken verbatim from a URL already in hand, never a constructed vanity URL (a guessed slug returned "page doesn't exist" where the real one was known) [profile-probe].
5. A profile's recent-activity module does not render until scrolled, and scrolling is write-class to the guard; prefer the recent-activity page's links over scrolling a profile [profile-probe, classifier-sync].
6. Record which route produced the numbers (posts API / recent-activity / DOM evaluation); the three differ in reliability and the artifact must say which made them [profile-probe].
7. Quantify render quality (body text length plus count of feed-update anchors) into the artifact; a shell render (nav plus right rail, zero feed anchors) is a stop signal [profile-probe].

## Hard stops

- Never click Follow, Connect, Message, or any composer; never submit a form; never navigate to edit routes, the contact-info overlay, or a Page-admin route [profile-probe].
- Overlay write hazard: contact-info and custom-button overlays have failed to mount their dialog after ~30s of polling while the base profile rendered fine, and an unhydrated contact-info save can blank real emails and phone numbers. Probe the specific overlay, poll for the dialog, then stop and hand the edit to Mike [lg-profile].
- Recovery is per-surface: a page coming back is not evidence its edit overlays are writable [about-and-featured].
- Returns blocked on identity mismatch, shell render, or both post-read routes failing; names the failing surface, never substitutes a remembered value [profile-probe].
- Outward anything needs Gate-D (approval token per batch) plus a human [profile-probe].

Absorbed from: profile-audit, step-8-profile, profile-probe, lg-profile, about-and-featured
