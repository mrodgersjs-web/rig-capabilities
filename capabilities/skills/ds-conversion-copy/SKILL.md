---
name: ds-conversion-copy
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate
  (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict.
  Main skill of design-studio-os for conversion copy: Write the page: hero, proof and calls to action for one buyer and one ask, with the anti-slop lint clean. 63 laws, 41
  looks-like/does-not pairs distilled from the RIG design YouTube corpus (top-10 subscribed channels
  weighted), every law cited CLAIM(<videoId>@mm:ss). Use when a landing page, hero, headline, CTA or section copy needs writing or fixing.
tier: main
parent: design-studio-os
activation: "Load at the start of any task that decides conversion copy. Entered by the /design-studio command through design-studio-os, by ds-copywriter, or by the ds-gate-* harness that names this stage."
owner: rig-intelligence
status: Stable
acl: internal
outcome: "design-ux: copy.md: hero (who for, outcome, one ask), section copy, proof placements, CTA hierarchy; lint-clean per ds-slop-linter, with citations or labeled own reasoning on every judgment"
done_when:
  - cmd:python3 ../rig-design-studio-os/tools/claims_check.py capabilities/skills/ds-conversion-copy/SKILL.md
  - cmd:python3 ../rig-design-studio-os/tools/check_family.py
quality_floor: 0.6
---

# Conversion copy

JEV FIRST, and it binds every task under this skill: an agent whose only context is this excerpt
sends semantic triage, routing and classification to the rig-s1gate Jev path BEFORE any frontier LLM call
(`~/.rig/bin/rig-s1gate check ui.design --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`;
nearest existing rubric: ui.design, advisory until calibrated). When the classifier is unavailable: DEFERRED,
never a guessed verdict. A required signal passes only above 0.9.

## Load surface

Load this skill FIRST, before any design decision, whenever the job touches conversion copy. It is an
always-loaded task-start surface, not a deep reference an agent must already know about: the `/design-studio`
command loads `design-studio-os`, which names this skill in its stage routes table; `when-designing-interfaces`
and `when-designing-websites` route design work to that front door; and the meta agent `ds-director` dispatches
`ds-copywriter`, which loads this skill before its first action. The stage's gate harness
(`ds-gate-craft`, `ds-gate-brief`, `ds-gate-critique` or `ds-gate-ship`) names these requirements, so a session
running that harness loads this file to pass its gate. Paths are relative to `~/Developer/rig-design-studio-os`.

## When to use

Trigger words: "landing page copy", "headline", "CTA", "make it convert", "hero section". Inside a build this stage runs after the stage that feeds it and
before ds-build-ship, ds-critique.

## Inputs and output contract

Inputs: the buyer, the offer, the proof available (named results, testimonials, logos), the voice.
Output: copy.md: hero (who for, outcome, one ask), section copy, proof placements, CTA hierarchy; lint-clean per ds-slop-linter.

## Procedure

1. Hero offer: first screen value, audience, visual, proof, and one button (see references/hero-offer.md).
2. Proof system: testimonials, case studies, and off-site reuse without carousels or unapproved edits (see references/proof-system.md).
3. Objection close: benefits, FAQ, repeated single action, and the last ask (see references/objection-close.md).
4. Page edit: cut jargon, cut pages, restraint, real imagery, mobile-as-default, known header patterns (see references/page-edit.md).
5. Offer page: one offer per page, three benefits, three-step plan, feature check near the decision, about-page formula, homepage teases (see references/offer-page.md).
6. Check the decision tables below for the choices this stage forces.
7. Run the anti-patterns as a final sweep; each surviving one becomes a finding in `ds-critique`.
8. Cite every load-bearing choice (CLAIM copied from this file); label the rest own reasoning.

## Core laws (load-bearing subset)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 4 | Place a credibility cue beside the hero claim: buyer count, client logos, or years in business. Do not leave the claim unsupported. | Flux Academy, Sam Crawford | CLAIM(GTNgiTK-ic8@02:37), | consensus |
| 5 | Name the next step on the button (schedule the consultation, see the plans, buy). Do not label it Contact us. If they are not ready to buy, the named step can be a look at plans rather than a hard start. | Flux Academy, Wes McDowell, Mike Locke, Jesse Showalter | , CLAIM(Zxz-0r8G7KQ@02:02), CLAIM(7m8fdKIErPY@07:17), CLAIM(SI9Q7O8ZTpk@02:23) | consensus |
| 6 | Give the page one job. When contact, book, and learn-more are equally loud, the visitor does nothing. | Sam Crawford, Flux Academy, Jesse Showalter | , CLAIM(YkxGTwbRQ9w@00:29), CLAIM(mEWs_68-yL8@00:53), CLAIM(3hlrCSQSsWs@01:42) | consensus |
| 7 | Make the first screen answer, before the scroll: what this is, who it is for, how life gets better, and what to do next. If that is not clear in the opening seconds, they hit back. | Sam Crawford, Jesse Showalter, Wes McDowell, Paige Brunton | CLAIM(75xzeXRZrHQ@02:15), CLAIM(SI9Q7O8ZTpk@00:32), CLAIM(b0KQaZkDBKU@02:45), CLAIM(0m1TeQyNqW4@01:09) | consensus |
| 11 | After the hero promise, lead each block with the buyer outcome, not the technical spec. Use three benefits, each with a visual, a result title, and one line that names the feature and what it means in the buyer's life. | Flux Academy, Wes McDowell | CLAIM(GTNgiTK-ic8@04:28), CLAIM(b0KQaZkDBKU@03:29), CLAIM(mGbLhEY7nPE@11:08) | consensus |
| 13 | Treat the FAQ as the objection list. On a homepage, about six items is enough; turn known hesitations into questions (why not the cheaper option) and answer with the rebuttal. | Flux Academy, Sam Crawford, Wes McDowell | CLAIM(GTNgiTK-ic8@05:54), CLAIM(Zxz-0r8G7KQ@15:05) | consensus |
| 15 | Repeat the same primary action below the fold, not only in the hero. A hero button plus a footer button is not enough. Two entry methods are allowed only when both serve that one outcome and you have evidence both get used. Rank any extra buttons as secondary. | Sam Crawford, Jesse Showalter | CLAIM(OX0fnUrNVPo@04:36), CLAIM(3hlrCSQSsWs@02:47), CLAIM(SI9Q7O8ZTpk@04:00) | consensus |
| 16 | Put case studies ahead of bare quotes. Each project page walks the before, the work, the after, and a quote that matches the claim. A single homepage screenshot is not a portfolio. On the homepage, tease a few projects and link out. | Sam Crawford, Paige Brunton | CLAIM(OX0fnUrNVPo@01:14), CLAIM(0m1TeQyNqW4@06:43), CLAIM(0m1TeQyNqW4@07:25) | consensus |
| 1 | Write the hero headline as the value or outcome, not a generic category label such as the product type or the service name. | Flux Academy | CLAIM(GTNgiTK-ic8@01:05) | single-source |
| 2 | Put a subtitle under the headline that explains how the value is produced and who it is for. | Flux Academy | CLAIM(GTNgiTK-ic8@01:42) | single-source |
| 3 | Show a hero visual of the product in use, or of the person being hired, so the buyer can picture the purchase. | Flux Academy | CLAIM(GTNgiTK-ic8@02:09) | single-source |
| 8 | Pack the value proposition, the clearest call to action, and the strongest message above the fold. Do not save the best line for later. | Sam Crawford | CLAIM(OX0fnUrNVPo@00:19) | single-source |

The full set of 63 laws lives in the sub-skills, plus 15 ungrouped laws below.

## Sub-skills

| sub-skill | file | owns |
|---|---|---|
| hero-offer | references/hero-offer.md | 12 laws |
| proof-system | references/proof-system.md | 7 laws |
| objection-close | references/objection-close.md | 7 laws |
| page-edit | references/page-edit.md | 14 laws |
| offer-page | references/offer-page.md | 10 laws |

## Further laws (not yet grouped into a sub-skill)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 36 | When a client asks to copy a competitor layout, ask why, what the site must do, and who it is for before you match colors. | Sam Crawford | CLAIM(75xzeXRZrHQ@08:04) | single-source |
| 37 | Study a reference site for the action it causes: first eye stop, headline promise, where proof sits relative to the ask, and the one job. A screenshot of the hero is not the study. | Sam Crawford | CLAIM(75xzeXRZrHQ@09:21) | single-source |
| 38 | Do not expect a paid offer to convert on the first button. Build a flow: hero action, product in motion, benefits, who it is for, then proof. Each section keeps one focus. | Flux Academy, Jesse Showalter | CLAIM(YkxGTwbRQ9w@02:10), | consensus |
| 40 | Color the primary button so it contrasts with the background and with the hero image, and reserve that color for the action. Faces in a photo will steal the eye from a quiet button. | Flux Academy, Jesse Showalter | CLAIM(YkxGTwbRQ9w@05:31), CLAIM(SI9Q7O8ZTpk@03:28) | consensus |
| 41 | Cut the first step to the smallest ask: one email field and one button. A 10-field form, or a button that opens a second account page, is friction that kills the buy. | Flux Academy | CLAIM(YkxGTwbRQ9w@06:36) | single-source |
| 43 | Write the value block so it scans: a short title and one outcome line, in the buyer's job language, not a feature dump. | Jesse Showalter | CLAIM(mEWs_68-yL8@07:32) | single-source |
| 45 | Put one long block lower on the page for people doing due diligence and for search: desired change, external problem, how it feels, your belief, empathy, process, the action, and what failure versus success looks like. Do not make that block the hero. Structure and plain language help search; they are not opposed to the design. | Jesse Showalter, Sam Crawford | CLAIM(mEWs_68-yL8@10:17), | consensus |
| 46 | For visitors not ready to buy, offer one useful free item (a short guide, a kit, or a training) in exchange for an email. Do not let that second ask outrank the primary action. | Jesse Showalter | CLAIM(mEWs_68-yL8@12:34) | single-source |
| 47 | Park secondary links, maps, and policies in the footer so they stay available without competing with the page's one job. | Jesse Showalter, Flux Academy | CLAIM(mEWs_68-yL8@13:44), CLAIM(GTNgiTK-ic8@07:04) | consensus |
| 49 | Put a point of view, a process, and a personality on the page. A site that looks like every other firm in the category gets priced like one. | Sam Crawford | CLAIM(OX0fnUrNVPo@02:20), CLAIM(DuowDNn3TNc@03:20) | single-source |
| 50 | If proof is thin, add proof before you fund a redesign. Stacked quotes, video, screenshots, and logos can out-earn a prettier page because they answer whether this worked for someone like the visitor. | Sam Crawford | CLAIM(3hlrCSQSsWs@03:12), | single-source |
| 51 | Replace default form chrome and default badge icons with a small custom label that states what the user is doing. The care signal is in that detail, not in a full-screen video background. | Sam Crawford | CLAIM(3hlrCSQSsWs@05:59) | single-source |
| 53 | Decide what stays from visitor data: what they click, where they drop, and which pages they read. Owner taste and a founder story they care about are not the brief. | Sam Crawford | CLAIM(DuowDNn3TNc@05:09) | single-source |
| 54 | Judge the site by whether it helps the business sell. Likes on a design gallery are not the score. A beautiful photo with no price, no availability, and no action fails even for a visual business. | Jesse Showalter | CLAIM(mEWs_68-yL8@00:12), CLAIM(mEWs_68-yL8@01:31) | single-source |
| 63 | Show how-it-works as three visuals of the real objects (the thing they scan, the real app icon), and put the store buttons on this page instead of sending them to a second page. | Flux Academy | CLAIM(X1dIZ53O-8s@06:43), CLAIM(X1dIZ53O-8s@13:15) | single-source |

## Looks like / does not (strongest pairs)

| looks like | does not | why | citation |
|---|---|---|---|
| 1 | Headline states the outcome or the uniqueness ("more traffic for your business"). | Headline names the category ("we build websites", "we sell coffee"). | Category labels do not give a reason to stay. |
| 2 | Benefit line: what changes for the buyer (stay connected, immersive sound). | Spec line: speed or horsepower with no outcome. | Buyers act on the result, not the technical sheet. |
| 3 | One obvious action, everything else quieter. | Five equal buttons: contact, book, learn more. | Equal volume produces no action. |
| 4 | Headline names the thing and who it is for. | Headline only describes a product feature. | The visitor must see themselves in the first line. |
| 5 | Hero answers where, what, why, and next step at once. | Hero answers one or two of those and hopes they scroll. | Most visits die in the opening seconds. |
| 6 | Copy written first; layout serves the words. | Layout copied from a competitor while the words stay weaker. | You copied the part that does not sell. |

Full pair set: the ds-exemplars skill and studio-exemplars/pairs/conversion_copy/.

## Decision tables

| decision | option A | option B | pick when |
|---|---|---|---|
| How many actions | One primary action, repeated | Several different actions at equal weight | Always pick A on a conversion page. B only if the page truly has two audiences with two jobs, and even then separate the pages. CLAIM(75xzeXRZrHQ@00:44), CLAIM(OX0fnUrNVPo@04:22) |
| Where to repeat the button | Hero plus a close | Same button in nearly every section | Pick the repeated button once the page is longer than a hero. Hero-only fails mid-scroll conviction. CLAIM(OX0fnUrNVPo@04:36), CLAIM(GTNgiTK-ic8@06:48) |
| Proof format | Case study (problem, method, result) | Short quote | Use the case study when you need the sale. Use the short quote for scan points, with the long version on the case study page. CLAIM(OX0fnUrNVPo@01:14), CLAIM(Yz3pOF7D-bw@03:34) |
| Headline type | Outcome plus who it is for | Feature or category | Pick outcome unless the category is already the search term and the subtitle carries the outcome. CLAIM(GTNgiTK-ic8@01:05), CLAIM(75xzeXRZrHQ@01:49) |

## Anti-patterns

- Generic category headline with no value. CLAIM(GTNgiTK-ic8@01:10)
- Hero with no visual of the thing being bought. CLAIM(GTNgiTK-ic8@02:09)
- Unsupported claims with no logos, counts, or years. CLAIM(GTNgiTK-ic8@02:37)
- Specs without benefits. CLAIM(GTNgiTK-ic8@04:43)
- Page that ends without a last ask. CLAIM(GTNgiTK-ic8@06:48)
- Five competing calls to action. CLAIM(75xzeXRZrHQ@00:49)
- Designing before the words exist. CLAIM(75xzeXRZrHQ@03:01)
- Adding sections and motion to fake premium. CLAIM(75xzeXRZrHQ@03:52)
- plus 12 more in references/<sub-skill>.md files

## Creator disagreements (stated, not resolved)

- How often to show the button. Flux (2022) specifies a hero button and a last-call button before the footer. CLAIM(GTNgiTK-ic8@03:03), CLAIM(GTNgiTK-ic8@06:48). Sam Crawford (2026) says a hero button plus a footer button is not enough, and the same primary action should appear in almost every section. CLAIM(OX0fnUrNVPo@04:36). Same creator also says one job and one obvious action, with other buttons getting out of the way. CLAIM(75xzeXRZrHQ@00:44). Reconciliation used in the laws: one action, repeated, never several different actions at equal weight.
- What the hero headline must say. Flux allows either the problem solved or the uniqueness of the offer, and notes it need not name the activity. CLAIM(GTNgiTK-ic8@01:05). Sam Crawford wants the line to say exactly what it is and who it is for, and treats a pure feature line as the failure. CLAIM(75xzeXRZrHQ@01:49). Jesse wants very few words that name the offer and how life gets better. CLAIM(mEWs_68-yL8@02:51), CLAIM(mEWs_68-yL8@04:21). Prefer the short line that names both outcome and audience; do not ship a category label.
- Where proof sits. Flux puts a credibility cue in the hero and more proof later. CLAIM(GTNgiTK-ic8@02:37). Jesse calls placement debatable and prefers logos and reviews after the hero, the negative-stakes block, and the value block. CLAIM(mEWs_68-yL8@09:15). Sam Crawford (2026) will stack proof all the way down a plain page and would pick proof over a redesign if forced. CLAIM(3hlrCSQSsWs@03:35). Working rule: one proof cue near the claim, a full proof section after the value is clear, never a carousel.
- How long the copy may be. Sam Crawford says cut the draft in half, then in half again, and that walls of text lose the visit. CLAIM(DuowDNn3TNc@02:29), CLAIM(OX0fnUrNVPo@02:34). Jesse still wants one long, keyword-rich paragraph lower on the page so a careful reader can finish due diligence. CLAIM(mEWs_68-yL8@10:17). Working rule: scan layer up top, one long block below, not essays in every section.
- Two doors or one. Flux's Netflix example allows get-started or sign-in and calls that focus. CLAIM(YkxGTwbRQ9w@01:01). Sam Crawford's 2026 study allows a call and a contact form when both feed the same outcome and the split is real. CLAIM(3hlrCSQSsWs@02:47). Both reject a brochure, a newsletter, and a chat widget as extra jobs.
- Scarcity and timers. Only Flux (2022) teaches limited quantity and expiring offers as conversion tools. CLAIM(YkxGTwbRQ9w@07:42). Wes uses fear-of-missing-out via live signup popups, not a countdown. CLAIM(mGbLhEY7nPE@03:39). Treat timers as single-source. Do not invent a limit the offer does not have.
- Who is in the hero photo. Flux (2022) wants the product in use, or a photo of the freelancer so the buyer can picture who they are hiring. CLAIM(GTNgiTK-ic8@02:09). Wes (2025) wants the customer in the after state in the hero, and holds the founder photo for the solution block. CLAIM(Zxz-0r8G7KQ@03:31), CLAIM(Zxz-0r8G7KQ@06:37). For a product, show the product in use. For a service, Wes's split (buyer in the hero, guide photo later) is the more specific rule in this set; Flux's freelancer portrait is the older single example.
- How many benefits. Wes caps the set at three in both 2018 and 2025. CLAIM(Zxz-0r8G7KQ@08:26), CLAIM(b0KQaZkDBKU@04:58). Jesse shows icon stacks without a count cap. CLAIM(mEWs_68-yL8@07:49). Use three unless the offer truly has a fourth that would be a lie to omit.
- Comparison tables. Wes in 2025 allows a table where the rival still wins some rows, as long as you have more checks. CLAIM(Zxz-0r8G7KQ@14:44). The same creator in 2024 says a wall of red marks looks biased. CLAIM(mGbLhEY7nPE@09:24). Follow the 2024 caution: educate, do not stack failures.
- How hard the button may be. Wes (2025) rejects "contact us" and wants the label to name the next step, such as scheduling a consultation. CLAIM(Zxz-0r8G7KQ@02:07). Locke (2010) says "get started" is a hard sell and "see pricing" converts better for people who are not ready. CLAIM(7m8fdKIErPY@06:51). Working rule: name a real step at the commitment they can make. Vague contact is still wrong. A hard buy is wrong only when the offer needs a look first.
- Who appears, and how much biography. Locke (2010) wants a face, a name, and a story on the site so the guard drops. CLAIM(7m8fdKIErPY@02:24). Wes (2022) wants one real face and bans team bios, hobbies, and social links. CLAIM(bYZkDOwQxfg@07:21), CLAIM(bYZkDOwQxfg@07:13). Paige (2024) wants a founder photo on a personal brand, or a team or office photo on a traditional brand, as a homepage tease. CLAIM(0m1TeQyNqW4@05:09). Working rule: one real face, a short why, no hobby roster.
- How long the explainer video is. Wes (2018) says about 60 seconds, problem through the cost of doing nothing, ending on the same button. CLAIM(b0KQaZkDBKU@05:43). Locke (2010) wants about two minutes so they can skip reading. CLAIM(7m8fdKIErPY@06:11). Prefer the shorter cut unless the product cannot be grasped in a minute. Put a result line beside the player either way. CLAIM(mGbLhEY7nPE@07:45)
- Clever versus quiet luxury. Jesse (2025) says do not be cute; name the benefit in a few words. CLAIM(SI9Q7O8ZTpk@08:32). Sam Crawford (2026) says a luxury page can stay quiet and let the visitor lean in, after clarity is already established. CLAIM(3hlrCSQSsWs@05:20), CLAIM(3hlrCSQSsWs@05:20). Quiet is allowed. Cute that hides the offer is not.

## Creator claims (unverified)

- Most people are not scrolling past the hero. CLAIM(OX0fnUrNVPo@00:19)
- You have less than 3 seconds to earn attention. CLAIM(OX0fnUrNVPo@01:27)
- Most sites lose people in the first 5 seconds. CLAIM(75xzeXRZrHQ@02:26)
- Headlines do about 80% of the selling. CLAIM(OX0fnUrNVPo@02:04)
- Case studies outperform testimonials "by a mile." CLAIM(OX0fnUrNVPo@01:14)
- Nine times out of 10, copying the competitor is the wrong move. CLAIM(75xzeXRZrHQ@08:37)
- Moving a quote from $500 to $5,000 is mostly belief, and cheap prices attract cheap clients. CLAIM(75xzeXRZrHQ@12:04), CLAIM(75xzeXRZrHQ@12:43)
- AI can assemble a generic page faster and cheaper, and cannot make the strategic call. CLAIM(75xzeXRZrHQ@13:53)

## Tool-specific (dated)

- Figma landing-page template used as the demo canvas (Flux, 2022). The section order is the law; the file is not. CLAIM(GTNgiTK-ic8@00:38)
- Stripe homepage and a copywriter site used as 2022 hero examples: value line, who it is for, start button, product-in-use visual. CLAIM(GTNgiTK-ic8@03:22)
- Social Juice link for collecting written or video reviews at project end (Flux, 2023). The durable rule is: send prompts, accept video or text, then cut the video. CLAIM(Yz3pOF7D-bw@09:27)
- Unbounce link-count chart and the 4.39 average (Flux, 2022). The durable rule is fewer links in the section, not that average. CLAIM(YkxGTwbRQ9w@01:31)
- Google PageSpeed Insights as the 2022 check Flux names. Re-test on a current speed tool; the rule is still to design lighter assets. CLAIM(YkxGTwbRQ9w@09:26)
- Gobi countdown bar and PandaDoc / Campaign Monitor / Egghead / Netflix / Zola as 2022 screen examples. Section logic survives; those UIs may not. CLAIM(YkxGTwbRQ9w@02:41), CLAIM(YkxGTwbRQ9w@08:26)
- Spline and Rive named in 2026 as the reason every designer can add 3D and parallax. The law is still: do not let motion outrank the offer. CLAIM(DuowDNn3TNc@04:40)
- Squarespace default form and default circle-member badges replaced with a custom corner label and custom laurels (Sam Crawford, 2026). The law is: do not ship the platform default when a  small custom label can state the action. CLAIM(3hlrCSQSsWs@06:28)
- plus 10 more in the corpus law file studio-corpus/laws/conversion_copy.md

## Hand-off
- Next stage: ds-build-ship, ds-critique. Agent: `ds-copywriter` (sub: ds-slop-linter).
- Corpus source: studio-corpus/laws/conversion_copy.md (regenerate skills with tools/build_skills.py after a corpus refresh).
- Nothing outward (deploy, publish, push) without Gate-D: `ds-pre-publish-gate-d` enforces it once wired.
