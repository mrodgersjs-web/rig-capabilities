# Case: FAANG engineer on salaries, interviews and hedge funds

Source: https://www.youtube.com/watch?v=v4Dt4FalMOA (video id v4Dt4FalMOA). Paraphrased distillation; every line cites a CLAIM(<videoId>@mm:ss) timestamp in video v4Dt4FalMOA against the local transcript.

- published 2026-07-10 / duration ~77 min (4636s) / problem type: career
- Russian-language podcast (channel: Даниил Лаптев | ДЕВ РОЙ). Guest: Evgenii Ray (Front-End Engineer channel), then WhatsApp/Meta staff engineer in London. Interviewer/host: Daniil Laptev. Notes below are English paraphrase; only Evgenii's statements are recorded as laws.

## Author's framework as used
The interview-prep and career path Evgenii actually followed, reconstructed in order:
1. Set a relocation target early and treat English as the enabling skill (inspired by a US trip at 20; decided learning English matters for comfort abroad), CLAIM(v4Dt4FalMOA@02:41).
2. Build CV credibility through recognizable employers (JetBrains; top names get resumes read by big tech), CLAIM(v4Dt4FalMOA@04:32).
3. Use referrals purely to break through the applicant pool into an interview, CLAIM(v4Dt4FalMOA@12:21).
4. Rebuild CS fundamentals deliberately (Princeton algorithms course over ~3 months), CLAIM(v4Dt4FalMOA@18:03).
5. Map the actual loop before preparing: ask people inside the company what rounds ask, because recruiters give an unreliable map, CLAIM(v4Dt4FalMOA@19:42).
6. Match prep to the role: UI tasks and front-end system design for UI loops, LeetCode only where it is actually asked, CLAIM(v4Dt4FalMOA@19:18).
7. Practice by recording yourself and explaining out loud, doubly so in a non-native language, CLAIM(v4Dt4FalMOA@22:05).
8. Build a behavioral story bank: write out your work stories against the common behavioral question list and memorize them if English is weak, CLAIM(v4Dt4FalMOA@16:08).
9. Budget a long campaign (his run took 267 days from prep start to Meta offer, per the host's count, which he confirms in shape) while working a full-time job, CLAIM(v4Dt4FalMOA@00:44).

## Worked design
This is a career/interview video, so the "case" material is the loops and roles he describes rather than a product design.

Hedge fund interview loops (Jane Street, Citadel, Two Sigma):
- Motivation: career growth plus money; hedge funds are among London's best-paying employers, CLAIM(v4Dt4FalMOA@34:15).
- Interesting UI work exists because trading terminals are being rewritten from old Windows stacks to fast web, CLAIM(v4Dt4FalMOA@34:53).
- Jane Street: passed the front-end round, failed a generic programming round built on non-standard thinking tasks rather than standard LeetCode, CLAIM(v4Dt4FalMOA@35:46).
- Citadel: rounds went fine except one interviewer where there was no connection, CLAIM(v4Dt4FalMOA@35:23).
- Two Sigma: an earlier offer barely beat Meta; a later loop failed on one of three coding rounds because he did not finish one UI task, CLAIM(v4Dt4FalMOA@36:13).
- Structure he observed: recruiter described an algorithm round plus one front-end round; the actual loop was five front-end rounds and no system design, CLAIM(v4Dt4FalMOA@19:54).

Meta tech-lead project (launching a new product):
- Team scaled from ~6 to 15 engineers; he absorbed management duties when no manager was available, CLAIM(v4Dt4FalMOA@24:56).
- Value came from people/psychology handling, not engineering difficulty; the team was non-toxic and helpful, CLAIM(v4Dt4FalMOA@26:01).
- This project plus WhatsApp work led to promotion to staff (E6), CLAIM(v4Dt4FalMOA@26:30).

Meta internal LLM tools team (his move off WhatsApp):
- Company-wide push to build internal LLM tooling, staffing it with high-performing staff+ engineers, CLAIM(v4Dt4FalMOA@54:10).
- Team of ~32 with several senior principal staff; first time in a company-priority direction where there are no blockers, CLAIM(v4Dt4FalMOA@54:41).
- Work centers on context optimization, memory management, filesystem read speed, token minimization, prompt tuning; onboarding meant weeks of reading agent/tooling engineering material, CLAIM(v4Dt4FalMOA@55:48).
- In this team staff write the code and senior staff act as leads; roughly 90% of code is AI-assisted, which is why output volume is high, CLAIM(v4Dt4FalMOA@57:36).

Privacy as product constraint (WhatsApp):
- End-to-end encryption caps group size (2048) and narrows the solution space for features because of performance impact, CLAIM(v4Dt4FalMOA@31:26).
- Feature velocity suffers versus Telegram, which he says wins on product functionality and stores data server-side, CLAIM(v4Dt4FalMOA@32:07).
- The same privacy model is why WhatsApp is hard to monetize (no user context for ads), CLAIM(v4Dt4FalMOA@33:32).

## Trade-offs he names
- LeetCode-heavy prep vs role-specific UI prep -> for UI/front-end loops spend the time on components and front-end system design; for generic SWE/backend roles LeetCode is still required and actively asked, CLAIM(v4Dt4FalMOA@19:18), CLAIM(v4Dt4FalMOA@20:17).
- Course-based system design prep vs real scaling experience -> courses suffice up to senior; for staff+ only hands-on large-system experience survives the interview, CLAIM(v4Dt4FalMOA@13:22), CLAIM(v4Dt4FalMOA@13:28).
- B2 vs B1 English -> B2 for a low-stress pass, a good B1 only when the move is urgent, CLAIM(v4Dt4FalMOA@17:16).
- Fast silent solving vs narrated solving -> always narrate: an explained partial pass beats a silent perfect solve the candidate cannot defend, CLAIM(v4Dt4FalMOA@22:21), CLAIM(v4Dt4FalMOA@23:07).
- Big tech vs hedge funds vs mid-market London -> the same work can pay 20-30x differently across employers; funds pay most, work-life balance is team-dependent, CLAIM(v4Dt4FalMOA@37:22).
- Employer-sponsored visa vs talent visa -> talent visa for layoff security and faster settlement/citizenship; sponsored visas leave a 2-month scramble if fired, CLAIM(v4Dt4FalMOA@01:02:27), CLAIM(v4Dt4FalMOA@01:03:36).
- Comfortable role vs priority team -> he left a role where he could coast on four-hour days for a harder, interesting, blocker-free priority team, CLAIM(v4Dt4FalMOA@56:42), CLAIM(v4Dt4FalMOA@55:20).
- Privacy vs feature velocity (product trade-off he defends) -> accept slower features when encryption is the product promise; WhatsApp's encryption is real and messages cannot be bulk-downloaded, CLAIM(v4Dt4FalMOA@32:26).
- Buy vs rent in London (personal, his case) -> he bought when mortgage payments were ~2.5x cheaper than rent and built equity; rents later rose sharply, CLAIM(v4Dt4FalMOA@59:38).

## Anti-patterns he warns about
- Memorizing solutions without understanding: a candidate solved a task in three minutes, then failed when probed for 30 minutes because he had memorized code in a language he did not know, CLAIM(v4Dt4FalMOA@23:35).
- Practicing only by solving silently; the spoken explanation degrades while your mind is on coding and the interviewer hears noise, CLAIM(v4Dt4FalMOA@21:21).
- Trusting a recruiter's description of the loop; his actual rounds differed completely from what he was told, CLAIM(v4Dt4FalMOA@19:54).
- Spending eight weeks on LeetCode for a UI-role process that never asks it (his own self-diagnosed mistake), CLAIM(v4Dt4FalMOA@19:18).
- "Vibe monkey" prompting: demanding AI to just do it well without engineering context or a spec, CLAIM(v4Dt4FalMOA@41:31).
- Non-engineers (PMs, designers) generating piles of unmaintainable code that looks fine visually, CLAIM(v4Dt4FalMOA@40:14).
- Pushing AI features into every product surface regardless of user value (his critique of AI-everywhere at Meta), CLAIM(v4Dt4FalMOA@42:25).
- Org incentive trap: shipping fast zero-to-one projects and jumping on, leaving unmaintainable code behind (his explanation for weak code quality at Meta), CLAIM(v4Dt4FalMOA@29:03).
- Instructing engineers to burn more AI tokens as a goal: it manufactures usage, not value, CLAIM(v4Dt4FalMOA@43:21).

## Dated / contestable
- Claim that model progress has slowed and Claude Opus 4.6/4.7/4.8 feel identical while costs nearly doubled, a 2026 snapshot; model families turn over quickly, CLAIM(v4Dt4FalMOA@46:12).
- Company-specific claims (Google capping developer AI usage, Microsoft dropping Claude Code for Copilot, Uber resisting) are his industry read, not verified reporting, CLAIM(v4Dt4FalMOA@46:38).
- Compensation figures (Jane Street offers of 3-4 million for ex-colleagues, interns starting at 300k, 20-30x London pay spread) are self-reported hearsay and unverified, CLAIM(v4Dt4FalMOA@34:36), CLAIM(v4Dt4FalMOA@38:27).
- Assertions about Telegram's lack of privacy and about Durov's marketing claims come from inside WhatsApp and are contested; treat as one-sided, CLAIM(v4Dt4FalMOA@32:44), CLAIM(v4Dt4FalMOA@33:46).
- Rhetorical estimate that 95% of big-tech engineers write ordinary code for multiples of the pay is not measured, CLAIM(v4Dt4FalMOA@11:40).
- "Basic layout is already almost automated" is a fast-moving claim about tooling, CLAIM(v4Dt4FalMOA@44:31).
- UK visa details (settlement in 3 years, citizenship in 5) are policy-dependent and can change, CLAIM(v4Dt4FalMOA@01:02:52).
- B1-English sufficiency is anecdotal (observed cases, not a rule), CLAIM(v4Dt4FalMOA@17:23).
