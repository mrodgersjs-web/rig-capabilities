---
name: email-campaign-operator
description: Builds evidence-led email campaign drafts, dispatch banks, repurposed assets and independent review packets. Use for weekly opt-in nurture or the manually reviewed first 20 cold emails.
version: 1.0.0
status: candidate
---

<objective>
Turn an offer, audience, supplied proof and operator voice into a coherent draft package. Reuse the canonical rig-write-emails surface engine. This companion orchestrates content and review; it never sends, schedules, imports recipients or configures provider automations.
</objective>

<quick_start>
Read /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-write-emails/SKILL.md and follow its packet assembly and scoring instructions. Record source paths, timestamps and command evidence in the run directory. If that dependency fails, preserve the error and keep the package blocked; do not simulate its results.

Classify the request as cold_first20 or warm_opt_in before drafting. Use the workflow below. For review-only requests, inspect the supplied artifact version and run the evaluator or verifier role without rewriting it.
</quick_start>

<boundaries>
- cold_first20 means at most 20 distinct prospects, one initial individualized message each. Mike personally reviews and sends every message. No automated outreach, follow-up, enrollment or nurture. Unsent or rejected drafts do not count as sent.
- warm_opt_in means the five-email nurture package only for recipients with recorded permission for that purpose. A public address, prior cold email, reply or general relationship alone is not nurture consent. Missing consent allows sample drafts only.
- All current services, prices, scope and availability need sources. Future concepts must say proposed/not available and stay out of live-offer CTAs. Agree scope and quote before build.
- Never invent proof, personal observations, voice samples, prices, urgency, scarcity, results, conversion likelihood or percentages. A checklist is educational guidance, not a recorded demonstration. Missing proof or voice keeps full verification blocked; useful educational drafts may still be delivered with explicit limitations.
- Generator, evaluator and verifier must be distinct real actors or independently executed review sessions with evidence of identity and input hashes. Renaming the same writer inside one conversation does not create independence. Verifier reads final files and source evidence and does not rewrite them.
- A draft-quality result cannot authorize external actions. Leave send_status BLOCKED_MANUAL_ONLY for cold_first20, and NOT_AUTHORIZED for warm drafts unless a separate scoped release is established. This skill never executes that release.
</boundaries>

<inputs>
Record offer_name, audience, audience_problem, intended_transformation, weekly_theme, campaign_goal, primary_cta, proof_assets and operator_voice_samples. Each source gets an ID, path or URL, inspection time, permitted claims and limits. Record missing inputs explicitly; do not fill them with fiction.

Also record mode, run_id, operator, audience/list provenance, consent evidence where applicable, contact suppression status, approved sender identity, reply mailbox verification, postal address, opt-out method and source of any deadline. Do not copy secrets or raw private transcripts into the package.
</inputs>

<templates>
Copy the CSV headers from templates/ into the run directory. Use templates/review_record.yaml for actual actor evidence; null fields stay missing. Read acceptance-scenarios.md when validating this workflow.
</templates>

<workflow>
1. Write campaign_brief.md with one audience, offer, transformation, theme and CTA. Distinguish reader intent from guaranteed results. Use current source evidence; mark segment selection as a test hypothesis when unvalidated.
2. Write angle_map.yaml with Problem, Proof, Philosophy and Plan. Proof grades are A measured artifact, B contextualized case, C supplied observation, D unsupported/prohibited. Seek three Problem angles, three legitimate proof assets, two Philosophy contrasts and one ordered Plan. Report shortfalls. Empty proof inventories cannot pass as evidence.
3. In warm_opt_in mode draft five_email_campaign.md with announcement, problem, proof, philosophy and plan emails. Every non-announcement uses Hook, Build, Payoff and Invitation and remains useful with the CTA removed. If proof is absent, replace the proof email with labeled educational guidance and mark the proof requirement unmet. Do not advertise a launch, deadline or opening unless factual.
4. In cold_first20 mode write first20.csv and first20_drafts.md. Each usable row needs verified business name, geography/category, legitimate public contact source, exact reproducible website observation with URL/date/evidence, one relevant offer and one question. No fabricated personal relationship or inferred revenue loss. Exclude uncertain contacts; keep fewer than 20 when evidence runs out. If the website was already inspected, do not ask the recipient to send that URL. Suitable question: Is reviewing that part of the site a priority for you?
5. Write daily_dispatch_bank.md using See, Make, Say. Attach the genuine observation, its source, audience connection, one payoff and CTA. Without observations, provide topic prompts labeled unobserved rather than first-person stories.
6. Write claim_ledger.csv and cta_ledger.csv. Trace each material claim to its evidence and limitations. Each email has one primary action. Check destinations and reply behavior; a successful HTTP response alone does not prove that an application or mailbox works. Missing checks remain unknown. Include approved sender identity, postal address and usable opt-out/suppression instructions in final email bodies. Placeholders are draft-only blockers.
7. Produce repurposed_assets.md. For every warm email, derive a LinkedIn post, carousel outline, short-video script and reply starter with the same supported payoff. They are drafts, not permission to post or message.
8. Send the actual artifact version to the evaluator for three real question/response revision cycles on material issues. Record exact questions, cited defects, generator changes, before/after hashes, unresolved defects and actor/session IDs. Do not manufacture defects or invent cycles. If three meaningful cycles cannot be evidenced, report the shortfall instead of a completed card.
9. Score every email from 0–2 for relevance, hook, build, payoff, proof, personality, CTA and future-open value. Require at least 13/16 on every email, plus hard truth, CTA and compliance gates. Scores are evaluator judgments, not measured purchase probabilities. Keep raw dimension scores and explanations. No score overrules unsupported proof, fake scarcity, broken CTA or missing controls.
10. Have the independent verifier inspect final files, source/link checks and evaluator records. Write verification_report.md with draft_quality PASS/FAIL/INCOMPLETE, each gate and evidence, actor identity, final artifact hashes, unresolved inputs and separate send status. A generator-authored PASS or a templated empty report is invalid.
11. Initialize measurement_log.csv without invented outcomes. Keep cold and warm cohorts separate. Record sent, delivered, unique opens, clicks, replies, qualified conversations, conversions, unsubscribes, complaints and defensibly attributable revenue only from actual evidence. Treat privacy-distorted opens cautiously; zero denominator yields undefined, not zero. Never turn draft forecasts into actual performance.
12. Deliver paths, actual checks and missing inputs. Preserve failed reviews. Any later source/content change invalidates the bound review until rechecked. Do not call a draft complete when the card's proof, voice or review requirements remain unmet.
</workflow>

<success_criteria>
The draft package contains its brief, angle map, mode-specific emails, dispatch bank, claim/CTA ledgers, repurposed assets, measurement log and real independent review evidence. Three material revision cycles, per-email scores and hard gates are evidenced against final hashes. If any requirement is missing, deliver an explicitly incomplete draft with the missing evidence named. Installation proves availability only; it does not prove campaign quality, live sending, provider integration or D85 certification.
</success_criteria>

<provenance>
Adapted from Mike's BUILD CARD — Email Campaign Operator Skill Personality-Led Weekly Demand Engine.md, supplied 2026-09-14. Card attributes frequency, value, invitation, personality, 4P, See → Make → Say and HBPI to https://www.youtube.com/watch?v=1dcReMz3ajQ. The video has not been independently watched by this skill author; attribution is through the supplied card. Role separation, scorecard, evidence obligations and first-20 restrictions are RIG/user adaptations.
</provenance>
