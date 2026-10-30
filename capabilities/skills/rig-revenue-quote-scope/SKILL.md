---
name: "rig-revenue-quote-scope"
description: "Scope, price, and quote a RIG revenue engagement for a professional-service firm: diagnostic entry offer, build pack, retainer ladder, exclusions, and an evidence-based proposal. Use when the trigger is 'quote this', 'price this', 'scope an engagement', or 'proposal for this firm'."
done_when:
  - 'grep:capabilities/skills/rig-revenue-quote-scope/SKILL.md:[Q]ualify .say no when it fails.'
  - 'grep:capabilities/skills/rig-revenue-quote-scope/SKILL.md:[t]he gate is the product'
---

# Quote and scope an engagement

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta — especially claim hygiene: corpus price figures are CLAIM
ladder calibration, never market data. `[AWAITING]` external rate cards remain open.

## Inputs

- Buyer: firm type (law/CPA/clinic/consulting), size, service lines, cities, current visibility,
  internal capacity (who reviews content — a YMYL firm must name the reviewing professional)
- RIG cost base: delivery tooling (~$100-150/mo stack per CLAIM: KqGWtb5U1Xc, q0wr137QFEk),
  review time, professional-review time billed to the client or the firm
- Corpus economics (all CLAIM — use only as band checks, each tagged): agency band
  $2,000-$10,000/mo (KBoBMHLsGjI, D8tVa_kalbg, 9tlew1lQy18); one-owner local-service retainer
  $500-$800/mo (nlVw5vOBogA); delivery stack ~$100-150/mo (q0wr137QFEk)

## Outputs

- Fixed-fee diagnostic scope (the entry offer), optional build pack, optional governed retainer
- Written exclusions (excluded tactics listed as out-of-scope, per rig-revenue-meta)
- Proof section: only verifiable RIG evidence — never corpus CLAIM figures dressed as results

## Step 1. Qualify (say no when it fails)

ROI legible? Repeatability? Measurable success defined (what number moves, by when, measured
where)? Data availability (the firm's own cases/figures for forced variables)? Error tolerance and
human escalation named? If any is missing, quote the diagnostic only — or decline.

## Step 2. Shape the ladder

1. Fixed-fee diagnostic/audit (entry): visibility + citation-gap + local + content audit with a
   prioritized 30-day plan. Fixed price, fixed duration, deliverable list written before quoting.
2. Governed build pack (project): the actual install — local visibility, answer/citation pages,
   content engine, lead capture. Priced on scope pages/sprints, not "more traffic".
3. Governed retainer (monthly): cadence content + citation monitoring + monthly report, with the
   human approval gate and professional review included as line items — the gate is the product.

## Step 3. Price it

1. Price from scope and cost base (hours × rate + tooling + review overhead), then sanity-check
   against the CLAIM bands above. Never anchor a quote on a corpus revenue claim.
2. Write the exclusions verbatim: no link buying, no SERP flooding, no unattended publishing, no
   fake profile data, no AI-detection evasion, no protected-title publishing without verified
   credentials.
3. Name the client's obligations: review turnaround, expert time, approved data for variables.

## Step 4. Evidence and honesty in the proposal

1. Every claim in the proposal carries a source or is deleted. Corpus-derived tool
   recommendations carry PAID ENDORSEMENT labels (Arvow, Blotato, Journalist AI).
2. No ranking guarantees, no timeline promises beyond what RIG controls (cadence, pages shipped,
   reviews requested). "Anyone telling you that otherwise is selling something" (CLAIM:
   PXThfLN-OHQ).
3. State the `[AWAITING]` market research openly if the buyer asks for market benchmarks.

## Step 5. Hand off

Accepted quote → rig-revenue-new-client-sprint. Declined/qualified-out → log the reason for the
next pricing iteration.

## done_when

- file:capabilities/skills/rig-revenue-quote-scope/SKILL.md
- grep:capabilities/skills/rig-revenue-quote-scope/SKILL.md:^## Step 3. Price it
- grep:capabilities/skills/rig-revenue-quote-scope/SKILL.md:PAID ENDORSEMENT
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-quote-scope/SKILL.md

## Provenance (videoIds)

KBoBMHLsGjI, nlVw5vOBogA, PXThfLN-OHQ, 86bRah0t_Ko, x288PvvQ4zk, q0wr137QFEk, KqGWtb5U1Xc,
oLt6QwcXZgA, Eg-_fH5oIVk, IwxQnVAJgFc, D8tVa_kalbg. All corpus figures are unverified creator
claims (CLAIM: per rig-revenue-meta).
