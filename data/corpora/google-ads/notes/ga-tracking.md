# ga-tracking: conversion tracking as the foundation

## Laws

L1. Until conversion actions exist and fire, campaign spend can neither be steered nor judged — buying traffic before measurement is burning budget instead of learning. CLAIM(UOQK73bobyM, Yaniuwsxd60, vICMCqsa7DQ, 2TdOEFcS2bg, Nf1apn0Ju2Q, XcxGaBvYsW8, IrB1oSftw8c) | channels: 7 | status: consensus
> "conversion tracking you have to have conversion tracking set up there's no way of knowing what's going to work then if you don't have conversion tracking set up so it's absolutely crucial" (UOQK73bobyM, @growmyads)

L2. Prove the tag is actually recording a test conversion before a campaign goes live; weak or broken measurement poisons every decision made after launch. CLAIM(KbZofs6q7R8, XcxGaBvYsW8, C_g9hTd-UgE) | channels: 3 | status: consensus
> "Make sure your conversion tracking is right before you run your campaigns." (KbZofs6q7R8, @ben-heath)

L3. For lead forms and phone leads, count each unique lead once (count = one, not every), so page reloads, repeat submissions, and spam cannot inflate totals that bidding then optimizes toward. CLAIM(azlz9DqcALU, vICMCqsa7DQ, gu2qDwlmpiU, 3ok2qX3Iock) | channels: 2 | status: consensus
> "you have the count set to one and not every" (vICMCqsa7DQ, @aaron-young)

L4. Fire the form conversion on a thank-you/success page rather than on the form click or button press, so only completed submissions register as leads. CLAIM(azlz9DqcALU, O3QZLz21V3k, vICMCqsa7DQ) | channels: 3 | status: consensus
> "a lot of people like doing it by clicks I don't like doing that I like doing it by a thank you or success page URL" (azlz9DqcALU, @growmyads)

L5. Set the call-conversion duration threshold to whatever a genuinely qualified call lasts in your own call data, not the platform's short default, or bidding will chase disconnected or spam calls. CLAIM(C_g9hTd-UgE, 3ok2qX3Iock, waC1p1CLnA0, 2Y_prev5fb8) | channels: 3 | status: consensus
> "if you are tracking calls, be sure to track call duration limits that are meaningful to you. Therefore, not 10 seconds." (C_g9hTd-UgE, @growmyads)

L6. Use the native Google Ads conversion tag (with enhanced conversions) as the primary source instead of a GA4 import — the GA4 import path cannot carry enhanced conversions and consistently attributes less back to Google Ads. CLAIM(i_YMgSCUSBo, 17wfLxcRLdE, zMDsA7h8uGo, 6BhGaQ-RTyw, C_g9hTd-UgE) | channels: 2 | status: consensus
> "you cannot set up enhanced conversions on a G4 import and enhanced conversions gives you more attribution back" (i_YMgSCUSBo, @growmyads)

L7. Give the account exactly one primary conversion goal to optimize against and hold everything else as secondary; secondary actions still collect data without steering bids. CLAIM(EwsDW3OQj5k, 4Cgc9PsCWrY, O3QZLz21V3k, 3W0XeR3va20) | channels: 4 | status: consensus
> "you cannot have all of the conversion actions set to primary" (EwsDW3OQj5k, @solutions8)

L8. For lead-gen businesses, the strongest feedback loop is the offline conversion import: send back which form fills and calls became paying customers so bidding learns toward revenue rather than toward raw leads. CLAIM(vICMCqsa7DQ, KbZofs6q7R8, Nf1apn0Ju2Q, 6rfn9UdT4lg, 8DgOX5aizyE) | channels: 4 | status: consensus
> "Google Ads has an offline conversion import feature that lets you feed that downstream data back into the platform." (KbZofs6q7R8, @ben-heath)

L9. Click-ID (GCLID) based offline imports still match leads at higher rates than enhanced conversions for leads; EC4L is the lighter-lift option that improves identity matching but does not teach the algorithm about revenue. CLAIM(ARR-wcgFC1s, oWSHR2_8uE0) | channels: 2 | status: consensus
> "the match rates are uh still the best if you compare to enhanced conversions for leads" (ARR-wcgFC1s, @aaron-young)

L10. Enhanced conversions for leads depend on capturing user-provided data (name, email) from the form on the thank-you page and passing it through a user-provided-data event in the tag or GTM before Google can match it to later offline outcomes. CLAIM(YtxsHL2w-bA, 4FPgR9a_3c4, r3rv1qugGYw) | channels: 3 | status: consensus
> "Once you get the information back into Google Tag Manager, you can then use an event called a user provided data event." (YtxsHL2w-bA, @aaron-young)

L11. Consent mode and enhanced conversions are baseline measurement requirements, not optional upgrades — omitting them silently shrinks the conversion data the account optimizes from. CLAIM(6rfn9UdT4lg, 2TdOEFcS2bg, ShUDhQpmyds, XcxGaBvYsW8) | channels: 2 | status: consensus
> "features like enhanced conversions, consent mode, these are not optional for you" (6rfn9UdT4lg, @jyll-saskin-gales)

L12. Instrument every contact path the business genuinely relies on — calls, forms, chat, bookings — so no real lead route is invisible to optimization, but track nothing that is not a true lead path. CLAIM(fNRvEj9jf3w, O3QZLz21V3k, UOQK73bobyM) | channels: 3 | status: consensus
> "if you have four different ways that people contact you they have contact form uh booking chat and a phone call you know do all four" (fNRvEj9jf3w, @paid-search-podcast)

L13. Optimization learning accrues per conversion action, so reporting must be segmented by conversion action (plus an all-conversions column) to see which lead type a campaign is really producing behind its headline total. CLAIM(X9xCF5lCzuU, ZoQ30fw4Q5s, 7twmzrtQdpo) | channels: 2 | status: consensus
> "there's also learning that happens at the conversion action level" (X9xCF5lCzuU, @jyll-saskin-gales)

L14. Re-labeling a conversion action between primary and secondary only applies from the moment of the change — previously recorded conversions are never reclassified. CLAIM(bcQKmH1cvzE) | channels: 1 | status: single-source
> "any changes you make to your goal settings are not retroactive" (bcQKmH1cvzE, @solutions8)

## Contested

GA4 as the conversion source: one camp treats Google Analytics as the default tracking route, another actively warns against it as the primary conversion action.
> "The best way to do that is with Google Analytics" (i3-Dvy4Wjb4, @ben-heath)
> "we do not recommend G4 as your primary conversion action" (zMDsA7h8uGo, @growmyads)
> "it is not a requirement for you to use ga4 for your conversion tracking you can use manually created codes that you place on your website" (6BhGaQ-RTyw, @paid-search-podcast)
The corpus leans native-tag-primary (L6), but the GA4 route is not universally condemned — treat GA4-linked tracking as acceptable for measurement, inferior only as the bidding primary.

Calls-from-ads as an optimization goal: one window treats calls from ads as a legitimate primary conversion to bid toward, another points out that Google's "calls from ads" counter can report phone calls for clicks where the phone never rang.
> "You'll want to make sure that calls from ads or calls from your website are set as the primary conversion action and that everything else is set to secondary." (4Cgc9PsCWrY, @jyll-saskin-gales)
> "if you've ever wondered why I you have 16 phone calls according to google but your phone never ring" (IBaaVMfiHvA, @paid-search-podcast)

The dossier is thin on direct GCLID-vs-EC4L head-to-head trials; the two windows that discuss both (ARR-wcgFC1s, oWSHR2_8uE0) are complementary rather than contradictory, so the point is settled as L9 rather than contested.

## Dated advice

RBvD5Z0ucTk (@growmyads) is framed in a 2023 auto-apply-recommendations context, advising that the "upgrade your conversion tracking" recommendation is a yes because it switches the account to data-driven attribution:
> "data driven attribution should absolutely be the attribution model you have set for your conversion tracking" (RBvD5Z0ucTk, @growmyads)
Changed since: data-driven attribution is now the standard default and the auto-apply recommendations list has been revised; re-check what that toggle actually applies in the current interface.

Gu-seS8didI (@paid-search-podcast) explicitly notes older attribution menus (first-click, linear, time-decay, position-based) are gone for most accounts, leaving only two choices:
> "you probably only have two options you have last click attribution or you have data driven attribution" (Gu-seS8didI, @paid-search-podcast)
Changed since: any advice referencing the four legacy non-data-driven models pre-dates the current account defaults; verify which models your account still exposes.

17wfLxcRLdE (@paid-search-podcast) describes GA4 as brand-new and clunky in the same window — a snapshot of the early GA4 era. The GA4-vs-native-tag attribution gap it cites may have shifted; re-measure rather than assuming the old magnitude.

## Creator result claims

- Native Google Ads purchase tag yields up to roughly 10-15% more attributed conversions than a GA4 primary import (@growmyads, zMDsA7h8uGo) UNVERIFIED
- Around 80% of accounts the creator audits have incorrect tracking, stated as a personal feeling, not a measured sample (@growmyads, WhaVp5efaFs) UNVERIFIED
- A client account appeared to hold a 93% conversion rate, later found to be page views counted as conversions (@jyll-saskin-gales, 6JI0fjrV1Io) UNVERIFIED
- Better and more accurate attribution observed inside Google Ads when running the Google Ads purchase tag versus a GA4 import (@growmyads, i_YMgSCUSBo) UNVERIFIED

## Platform mechanics

- Enhanced conversions for leads is enabled in conversion settings, then chooses between Google tag and Google tag manager as the installation method (4FPgR9a_3c4, @solutions8) — re-verify in the live product.
- Offline import rows require the gclid, the conversion name, and an event time that falls after the click; value and currency are optional and default to 1 USD (4FPgR9a_3c4, @solutions8) — re-verify in the live product.
- Count setting (one vs every), 30-day click-through window, and data-driven attribution are the defaults walked through during conversion-action setup (azlz9DqcALU, @growmyads; 1gcjYJLUyf8, @ben-heath) — re-verify in the live product.
- Per-action reporting is exposed via the all-conversions column plus Segments → Conversions → Conversion action (7twmzrtQdpo, @jyll-saskin-gales; ZoQ30fw4Q5s, @solutions8) — re-verify in the live product.
- Consent mode status appears under the measurement diagnostics tab with a good/excellent rating (ShUDhQpmyds, @jyll-saskin-gales) — re-verify in the live product.
- The free Google Tag Assistant Chrome extension lists the Google Ads tag, Google tag, and GTM container installed on a site (r3rv1qugGYw, @surfsideppc) — re-verify in the live product.

## RIG application

- Gate-D on spend doubles as a tracking receipt: no campaign launches until Tag Assistant shows the tags live and a test form submission lands in the conversions summary — proof before budget, same pattern as every RIG outward-action gate.
- RIG's local B2B setup is the L3/L4/L5 combo by default: thank-you-page form conversion with count = one, plus a phone conversion whose duration equals a real qualified call (a few minutes, not 10-60 seconds), since calls + forms are the only truth in a small account.
- Keep one primary goal per campaign (L7) — booked appointments primary, everything else secondary — so a small daily budget has a single learning signal instead of splitting across five actions.
- Segment by conversion action weekly (L13) so call leads and form leads are read separately; a campaign totals 12 conversions while producing 10 junk chat clicks is invisible without the segment.
- GA4 stays linked but secondary; the native Google Ads tag with enhanced conversions is the bidding primary (L6, Contested).
- When a CRM or call log exists, start importing offline conversions on gclid for closed-won only (L8/L9) — EC4L is the cheap first step, GCLID the upgrade once lead quality data is trustworthy; consent mode on for any non-US traffic (L11).
