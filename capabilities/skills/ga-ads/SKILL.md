---
name: ga-ads
description: >-
  Ad creation for Google Ads: responsive search ads, headlines and descriptions from theme and offer, pinning policy, asset coverage (sitelinks, callouts, structured snippets, call, image, price, promotion), ad strength and policy safety. USE WHEN writing or rewriting ads, before launch, or when ad strength or disapprovals block delivery. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of google-ads-os.
owner: rig-intelligence
domain: Marketing
status: Stable
acl: internal
tags: [google-ads, google-ads-os, google-ads, ads]
outcome: "revenue-gtm: every ad group carries an RSA whose headlines match the theme and the landing page, with full asset coverage and zero policy risk"
done_when:
  - cmd:python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-ads/SKILL.md
  - cmd:python3 capabilities/skills/google-ads-os/scripts/check_family.py ga-ads
quality_floor: 0.6
metadata:
  parent: "google-ads-os"
  laws: "14"
  corpus: "data/corpora/google-ads (1052 transcripts, 8 channels)"
---

# ga-ads: ad copy and assets that match the query and the page

## JEV-first mandate (read first)

**Findability anchor - this is an always-loaded instruction surface, not a deep reference.** This block sits in this stage's description, which every harness (Claude Code, Codex, Hermes, OMP, Prime Agent, Aside) loads into every session at start, and in the front door `google-ads-os` and Mike's always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"). The text reaches the agent before any task in this stage begins; an agent whose only context is this excerpt still routes to Jev first.

**JEV FIRST - before any frontier LLM call, on every task.** Inventory the decisions the task forces and route each one, first match wins: CODE (deterministic rule) -> JEV (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`, decision id recorded) -> SYSTEM 2 (frontier LLM for generation) -> HUMAN (Gate-D: outward, paid, destructive). Semantic triage, routing and classification go to the rig-s1gate Jev path BEFORE any frontier LLM call. Re-run the inventory when scope shifts.

Typed judgments this stage forces: which ad copy wins, does this ad pass. Each goes to Jev (TypeSafe System One) before any frontier model opinion.

- Command: `~/.rig/bin/rig-s1gate check ad.search --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. No Google-Ads-specific rubric exists for this judgment; `ad.search` is the nearest existing one and is advisory until calibrated.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to spend, enable a campaign, raise a budget or publish. Ad spend is Gate-D: only Mike approves, and only the parent operator acts.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use for every ad before launch and at each creative refresh. Not for landing pages (ga-landing) or keyword themes (ga-keywords).

## Procedure

1. **Write from the theme and the offer**: headlines cover the theme (query language), the outcome, the proof or differentiator, and the CTA. Descriptions expand the promise and prequalify.
2. **Message match is the spine**: ad headline ≈ landing page H1 ≈ keyword meaning. The `ad.search` rubric exists exactly for this (query match, named pain, finished outcome, specificity, trust, differentiation, CTA prequalification, message match).
3. **Pinning policy**: pin only where a message MUST appear (e.g. regulatory or offer name); over-pinning strangles rotation and drops effective coverage. Prefer strength through variety.
4. **Asset coverage is part of the ad**: sitelinks (with descriptions), callouts, structured snippets, call asset for lead gen, images, price/promotion where real. Assets are free SERP real estate and a trust surface.
5. **Ad strength is a compass, not a law**: do not stuff junk headlines to chase "Excellent"; do not ignore "Poor" where the theme is narrow.
6. **Policy safety**: no unprovable claims, no trademark misuse, no prohibited content; financial/health claims need substantiation (pmm ads for local B2B: policy safety is a scored axis).
7. **Jev**: every new ad through `ad.search` with the full input set; iterate until it clears or record DEFERRED.

## Checklist (before this stage is called done)

- [ ] Headlines cover theme, outcome, proof, CTA
- [ ] Message match verified ad-to-page (H1 alignment)
- [ ] Pinning minimal and justified
- [ ] Asset coverage complete for the campaign type
- [ ] Every ad number true on the landing page today
- [ ] Policy check passed (claims, trademarks, prohibited content)
- [ ] Jev `ad.search` run per new ad; decision id recorded

## Hands the next stage

`ad-sets.md`: per theme - RSA headlines/descriptions, pinning decisions, asset inventory, Jev verdict ids. ga-landing mirrors the winning message; ga-reporting reads the results.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/google-ads/notes/ga-ads.md` (local corpus, not republished).

- L1. Stock each responsive search ad to its full complement of headlines and descriptions rather than the minimum, so the system has a real pool of combinations to test. CLAIM(0W1mR6b3WwM, UOQK73bobyM, jnAYabeKSag) | channels: 3 | status: consensus
- L2. Every headline slot must carry a distinct claim; two headlines saying the same thing waste a slot and the machine's testing capacity. CLAIM(YdWyP7IuG-0, UOQK73bobyM, w0clPy63ya8) | channels: 2 | status: consensus
- L3. Ad strength is an editing-stage suggestion score, not a serving or auction input; judge the ad on click-through and conversions instead. CLAIM(bA5EMJSa4Co, bjRR-yfaBlI, jnAYabeKSag, -yOy5uGwIRI) | channels: 4 | status: consensus
- L4. Excessive pinning narrows the combinations Google can serve and can cost impressions and click-through rate, and it drags the ad-strength rating down. CLAIM(kw2EEFjjzh8, 5GkO2fzQYxk, Ib_-lRg2xrw, O3QZLz21V3k) | channels: 3 | status: consensus
- L5. Deliberately pin the clearest, most aggressive message (or several variants of it) into position one so the core claim always shows, accepting the ad-strength hit. CLAIM(-yOy5uGwIRI, RCRPj2JmqCY, LoyJP3qxJyY, YdWyP7IuG-0) | channels: 4 | status: consensus
- L6. Judge each asset on its own metrics and keep the pool fresh: pull low-labelled or bottom-impression headlines and descriptions and replace them with new variants to test. CLAIM(YdWyP7IuG-0, jQr_UYNIZ_E, eFL6_qo7g10, eH45cy67gGc) | channels: 3 | status: consensus
- L7. High click-through rate does not prove the copy converts; with too little conversion data the system optimises toward whatever earns clicks, so read copy quality off conversions rather than CTR alone. CLAIM(fNRvEj9jf3w, 5uKLr1rZeyY) | channels: 2 | status: consensus
- L8. A fully stocked RSA spans thousands of headline/description combinations and every extra asset lengthens the learning cycle, so small accounts should expect slow and partial testing, never exhaustive testing. CLAIM(bA5EMJSa4Co, z6hF9AlfXBM) | channels: 2 | status: consensus
- L9. Seasonal and promotional copy should be shipped as scheduled assets (headline and description assets, plus promotion assets with start and end dates) instead of hand-editing every ad when a sale starts and ends. CLAIM(HfPj1Uk6ve8, XuJyaQwXiqc, qPKq784aP34, dLhH7fICDzc) | channels: 3 | status: consensus
- L10. Add every asset type that genuinely fits the business — sitelinks, callouts, structured snippets, promotions, calls — because they are cheap coverage even though they are not the main performance lever. CLAIM(3UO1VcidoMk, Yaniuwsxd60, fxbYM-y9ZDk, i3-Dvy4Wjb4) | channels: 2 | status: consensus
- L11. Treat disapproved ads, headlines and assets as work to fix rather than ignoring them, so the ad keeps the largest possible pool of live elements for Google to test. CLAIM(0W1mR6b3WwM, 4uGrZIy7-GQ) | channels: 2 | status: consensus
- L12. Pressure-test every headline against the competition: if a rival could run the identical line, the copy — and possibly the offer behind it — is too generic to earn the click. CLAIM(6rfn9UdT4lg, bjRR-yfaBlI, -yOy5uGwIRI) | channels: 3 | status: consensus
- L13. When testing ad copy changes, change one variable at a time — for example pin versus no-pin on otherwise identical RSAs — so any result change can be attributed. CLAIM(RCRPj2JmqCY, YdWyP7IuG-0) | channels: 2 | status: consensus
- L14. A promotion's advertised price must match what the landing page shows: running a compare-at-price setup together with a promotion asset triggers disapproval, so pick one mechanism per offer. CLAIM(Gu-seS8didI) | channels: 1 | status: single-source

## Where the creators disagree

Pinning is the clearest disagreement in the dossier. One side argues for aggressive pinning of the key message: [quote in corpus notes] (-yOy5uGwIRI, @paid-search-podcast). The other side warns against it: [quote in corpus notes] (5GkO2fzQYxk, @jyll-saskin-gales). One practitioner sits on the fence: [quote in corpus notes] (O3QZLz21V3k, @surfsideppc).

Ad strength also splits the corpus. Most creators discard it — [quote in corpus notes] (bjRR-yfaBlI, @aaron-young) — while one optimiser keeps it in his evaluation checklist: [quote in corpus notes] (4uGrZIy7-GQ, @optmyzr), and a third treats it as guidance rather than auction signal: [quote in corpus notes] (jnAYabeKSag, @surfsideppc).

How many headlines to run: fill everything versus keep it lean. One camp says stock the ad fully (0W1mR6b3WwM, @ben-heath; UOQK73bobyM, @growmyads, [quote in corpus notes]), while another prefers fewer assets for faster learning — [quote in corpus notes] (z6hF9AlfXBM, @jyll-saskin-gales) — a window whose five-headline limits are about Gmail ads, so the context is narrower than search RSAs.

Automatically created assets: presented as a performance benefit by one creator — [quote in corpus notes] (e98ndUDcjmA, @ben-heath) — but switched off by default by others: [quote in corpus notes] (uyXOzCXO5KY, @growmyads) and [quote in corpus notes] (iTKl8OSCsRg, @surfsideppc).

## Dated advice (platform mechanics change; re-verify before relying)

[quote in corpus notes] (iTKl8OSCsRg, @surfsideppc) — any advice or UI walkthrough using the word "extensions[quote in corpus notes]assets[quote in corpus notes]what were formerly called extensions, but now it's all called assets").

[quote in corpus notes] (XuJyaQwXiqc, @paid-search-podcast) — describes the pre-scheduled-asset workflow; scheduled headline/description and promotion assets replaced it.

[quote in corpus notes] (BHQEJAU5NG8, @growmyads) — advice written for the fixed-combo expanded-text-ad era; RSA rotation is now the only search ad mode, so [quote in corpus notes] testing expectations are obsolete.

[quote in corpus notes] (-yOy5uGwIRI, @paid-search-podcast) — [quote in corpus notes] vocabulary in older RSA advice maps to headline 1/2/3 today; some windows still mix the two.

sVGZKSEpqvU (@optmyzr, [quote in corpus notes]) and the Black Friday masterclasses dLhH7fICDzc (@growmyads, 2024) and hanrZznTlVA (@growmyads, 2025) carry season- and year-specific promotion advice; re-check current-year promotion asset requirements before reusing them.

## Creator result claims (UNVERIFIED, never repeat as fact)

Ben Heath claims adding the obvious ad assets can lift return on ad spend by roughly a fifth: [quote in corpus notes] (Yaniuwsxd60, @ben-heath) — UNVERIFIED

The Shopping feed video's title promises "10X Growth" from feed optimizations (y3cO7_QuVHg, @growmyads) — UNVERIFIED

An optimiser recounts clients' promotions that [quote in corpus notes] (QYV_8Kv7u9k, @growmyads), an anecdote with no measurement attached — UNVERIFIED

## Platform mechanics notes

RSA limits: 15 headlines and 4 descriptions per ad, with up to three additional headline assets and two additional description assets beyond those limits; AI-generated copy from automatically created assets does not count toward the limit (HfPj1Uk6ve8, @jyll-saskin-gales) — re-verify in the live product.

Google typically serves about two headlines and two descriptions, sometimes three headlines (h7xOSw1i7Jw, @aaron-young), and up to three RSAs may run per ad group (jnAYabeKSag, @surfsideppc) — re-verify in the live product.

Ad strength officially [quote in corpus notes] per the Google support text quoted on screen (bA5EMJSa4Co, @growmyads) — re-verify in the live product.

Automatically created assets are an opt-in campaign-level setting that builds headlines and descriptions from the landing page, existing ads and ad-group keywords (e98ndUDcjmA, @ben-heath); one window claims opting in also opts the campaign into AI Max for search (iTKl8OSCsRg, @surfsideppc) — re-verify in the live product.

Headline and description assets can be set at account level and scheduled; promotion assets take start and end dates and render beneath the ad, but cannot be served with Shopping ads — Shopping promotions go through Google Merchant Center instead (XuJyaQwXiqc, qPKq784aP34, @paid-search-podcast; HfPj1Uk6ve8, @jyll-saskin-gales) — re-verify in the live product.

RSA headlines and descriptions can be pulled into sitelink slots unless you pin headline 1, headline 2 or description 1; dynamic sitelinks are an account-level automated asset; sitelinks created at account, campaign, ad group and asset group levels can all serve together and support scheduling (HfPj1Uk6ve8, @jyll-saskin-gales) — re-verify in the live product.

Per-asset metrics live under the ad via "view asset details[quote in corpus notes]Low" performance label marks assets flagged for replacement (YdWyP7IuG-0, @growmyads; dcPh57jpjXE, @optmyzr) — re-verify in the live product.

Comparing a promotion asset against a compare-at-price setup produces a price-mismatch disapproval (Gu-seS8didI, @paid-search-podcast), and disapproved ads are surfaced with their reason and editable in place in third-party tooling (eDCiBtuiohQ, @optmyzr — an Optmyzr dashboard feature, not a Google UI) — re-verify in the live product.

## RIG application (RIG synthesis, not corpus claims)

Write ad copy per query theme: each ad group gets one RSA whose headlines each say something a competitor could not say verbatim, carrying the real offer (free 20-minute assessment, call today) and matching the landing page claim exactly.
Pin only the compliance-critical line — the booked-assessment CTA — into headline 1; leave the rest unpinned, and run pin-versus-unpin as a one-variable test per ad group rather than a blanket rule.
Ignore the ad-strength colour entirely; judge copy on qualified calls and form fills against spend, and keep a testing sheet so which headlines were tested and which won survives account changes.
Small budgets mean small data: run 6-8 strong headlines and 2-3 descriptions, review asset-level performance monthly, replace low or zero-impression assets with fresh variants, and never wait for exhaustive combination testing.
Use scheduled headline/description and promotion assets for any seasonal offer instead of editing live ads, and re-check for disapprovals after every edit or page change.
Keep automatically created assets off by default so Google never writes a claim the offer cannot back, and keep every spend change behind Gate-D approval.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/rsa-blueprint.md` | building a responsive search ad that can actually rotate |
| `references/asset-and-extension-checklist.md` | the asset inventory every campaign should carry |

## Hard rules

- Every number in an ad (prices, discounts, counts) is true on the landing page the day it serves.
- Never promise what the landing page does not deliver; message match is a hard gate, not a style preference.
- Disapprovals are fixed the day they appear; a disapproved ad is a hole in the account.
- New ads enter through experiments or clear rotation logic, never wholesale replacement on a live learning campaign.
- Ad copy decisions are drafts; publishing/serving remains Gate-D through Mike.

## Done-test

`python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-ads/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ga-ads` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
