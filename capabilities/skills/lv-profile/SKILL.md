---
name: lv-profile
description: >-
  The LinkedIn profile as a landing page: headline formulas and keyword extraction, About and Featured, banner and button, company page, profile audits and read-only probes, classifier sync, and the job-search profile lane. Use for "optimize my profile", "fix my LinkedIn", "rewrite my headline", "profile audit", "company page", "profile for recruiters". JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage (audit row pass/fail, headline option ranking, claim admissibility, classifier verdict) goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, profile, headline, job-search, company-page]
outcome: "content-publishing: the profile converts the right stranger and classifies cleanly for the feed, with every edit proposed as exact before/after values and applied only after Mike approves"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-profile
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  absorbed: "11"
---

# lv-profile (the profile as a landing page)

## JEV-first mandate (read first)

The typed judgments this stage forces: does an audit row pass or fail, which headline option ranks first, is a claim in profile copy admissible (who measured it), and is the classifier verdict actually measured rather than vibed. Route each to Jev before any frontier LLM call.

- Command: `rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`. Stored rubrics: `post.linkedin` (Lane B), `post.viral`, `post.eden`, `comment.linkedin`, `doctrine.surface`. Profile copy and audit verdicts have no stored rubric: their verdict is DEFERRED to Mike, and the artifact stays a proposal.
- Fail closed: classifier down, erroring, or rubric missing means DEFERRED. Never a guessed verdict, never a frontier substitute.
- An advisory PASS is not permission to edit a profile. Every profile edit is a Gate-D item [viral-core].

## When to use / when not to

Use for: auditing a profile, rewriting headline or About, Featured and banner decisions, company page work, reading profile viewers as a classifier check, and running the job-search profile lane. Not for: drafting posts (lv-draft), comments (lv-engage), DMs or applications (lv-outreach and the job-search campaign runner), or measurement (lv-measure).

## Procedure

1. Read the live profile first and record every current field value verbatim. A proposal with no before-value is not reviewable, and the render may be partial [step-8-profile].
2. Run the audit and the 60-second classifier check before editing anything: who viewed the profile, and does the title set look like the buyer. Report a ratio with a denominator ("7 of the last 20 visitor titles sit in the ICP"), never a vibe [profile-audit, classifier-sync].
3. Decide who the profile must be about (classifier sync) before touching copy: content, messaging, and profile are three inputs to one classification [classifier-sync].
4. Extract the keyword set: take 10 real targets (profiles or postings in the buyer's world), pull the common skills and keywords, and place them in headline, About, Skills and the custom button so they read as prose [headline-formulas].
5. Write the headline as job title plus who Mike helps plus how (see `references/headline-and-keywords.md`). Lane B carries the governance positioning; the job lane serves recruiter search. They are different artifacts; do not average them [headline-formulas].
6. Draft About, Featured, banner and button per `references/about-featured-banner.md`. Photo, banner and copy are one artifact; assets come from the designated generator (Eden), not an agent hand-authoring one [lg-profile].
7. Company page only when the target is a Page: `references/company-page.md`.
8. Produce a field-by-field change list: field, current value, proposed value, why, which reader it serves. Never a rewritten profile blob [step-8-profile].
9. Show Mike the exact before and after values. He approves; then a human types. No agent submits a profile or Page-admin form on this account [lg-profile, step-8-profile].
10. Re-check the classifier in weeks (a few weeks to a month), not days; headline churn resets what the classifier is learning [classifier-sync, step-8-profile].

## Quality bar

- Every proposed change carries its observed current value; the verifier re-reads at least two fields independently [step-8-profile].
- Every figure in the copy answers "who measured that and what did they look at" or it is cut. No metric of any kind in a headline unless RIG measured it [headline-formulas, profile-audit].
- The audit passes: follow mode on, headline beyond a bare title, current professional photo, banner that sells what is posted about, reader-addressed About, best trophies Featured, custom URL, one explicit next step, keywords woven naturally, classifier verdict recorded with a denominator [profile-audit].
- Keyword placement reads as prose, not a search string [headline-formulas, about-and-featured].
- Before/after values exact and applied only after Mike approves [viral-core].

## Lanes

- **Lane B (RIG B2B):** the headline's value clause carries governance positioning; claims stay sourced; no mascots.
- **Lane A (personal brand):** profile supports the themed stream; the followers-vs-connections toggle is a Lane A/B decision because it reads as vanity to a sophisticated buyer [about-and-featured].
- **Ideawake client lane:** a client's profile is another person's surface; proposals only, nothing fires without Mike's explicit client approval [viral-core].
- **Job-search lane:** the profile is recruiter-facing: `references/job-search-profile.md` covers the Lucy routine, Open-to-Work set deliberately, share-resume-with-hirers, and human-pace editing. Edits still come to Mike as before/after values [lucy-skills, rig-job-search-campaign].

## Tools and runners

| name | kind | path | when to call |
|---|---|---|---|
| lucy-skills | runner | `~/.aside/u/0/skills/user/lucy-skills/SKILL.md` | job-lane runner: /lucy-skills profile audit, positioning, activity routine |
| jobs-assisted | runner | `~/Developer/rig-gtm-studio-v2/skills/jobs-assisted/SKILL.md` | job-search lane runner: find roles and draft outreach; the human clicks Submit |
| jobs-assisted@eden | runner | Eden skill `jobs-assisted` (eden://settings/skills/jobs-assisted) | Eden-resident job lane runner; cite by name, call through eden-mcp |

## Sub-skills

| file | covers |
|---|---|
| `references/headline-and-keywords.md` | headline formulas, the two readers, keyword extraction and placement, claim rules |
| `references/about-featured-banner.md` | About structure, Featured strategy, photo and banner specs, button and toggles (third-party synthesis) |
| `references/profile-audit-and-probes.md` | the 10-row audit, executor/verifier pair, read-only probe mechanics, hard stops |
| `references/classifier-sync.md` | the machine's half: three inputs one classification, the 60-second audit, re-check cadence |
| `references/company-page.md` | company page from zero, employee amplification, page commenting |
| `references/job-search-profile.md` | job lane: 20-10-5 activity, be-first job search, human-pace editing, campaign gates |

## Hard rules carried forward

- Profile edits are shown as exact before and after values and applied only after Mike approves [viral-core, lg-profile].
- No agent submits a profile-edit or Page-admin form on this account; a human types it [lg-profile, step-8-profile].
- Never submit into a partial render: probe the specific overlay route and observe the dialog first; an unhydrated contact-info save can blank real emails and phone numbers [lg-profile, profile-probe].
- Never navigate to edit, contact-info overlay, or a Page-admin route during a read probe [profile-probe].
- Company Page admin has been observed redirecting to an unavailable state; probe, do not assume [company-page, lg-profile].
- Headline churn resets the classifier's learning: one change set per month unless the measured audit says otherwise [step-8-profile, classifier-sync].
- Re-check the classifier in weeks to a month, never weekly [classifier-sync].
- No metric in a headline unless RIG measured it; results claims belong in the body with a source [headline-formulas].
- A visitor verdict is a ratio with a denominator, never an impression [classifier-sync, step-8-profile].
- Photo, banner and copy are one artifact; assets come from the designated generator, not hand-authored by an agent [lg-profile].
- The "40 times more likely" optimization figure is an uncited platform claim: a reason to do the work, never a number to publish [lg-profile].
- Identity asserted before any read is attributed; on mismatch return blocked and never click through an account chooser [profile-probe].
- A missing About or follower count from the API is recorded as unknown, never zero and never "absent" [profile-probe].
- Human-pace editing in the job lane: one tab, identity guard first, notify-network off, 12-30 ms typing, at most 7 saves per session, reload and read back after each save, hard stop on login redirect, checkpoint, CAPTCHA or unusual-activity warnings [rig-job-search-campaign].
- Never publish the client's address, birthday, or compensation anywhere outward; secrets by keychain item name only [rig-job-search-campaign].
- A frozen platform stays frozen: no reads, no scrapes through it [rig-job-search-campaign].
- Lane C is out of scope for this stage; refuse the envelope if the lane is C [profile-probe].

## Done-test

`python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-profile` verifies the frontmatter and JEV mandate, six sub-skills at size, a named ledger action for every stage-map row assigned to this stage, that every backticked path resolves, and that no sub-skill copies a 12-word run from a third-party merge source. GREEN means all of that holds.
