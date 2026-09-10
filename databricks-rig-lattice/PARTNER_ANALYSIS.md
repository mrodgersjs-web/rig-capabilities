# Databricks Partner Analysis — 2026-09-10
## Status: SOURCED DRAFT — pending remaining validation before remote publication

Evidence tiers: **A** = official page read directly this session (dates are page
publication dates); **B** = search-summary lead, page not yet read directly;
**C** = RIG hypothesis/recommendation, not evidence.

A-validated by direct read (exact publication dates): 2026 Global Partner Awards
blog (2026-06-15) · SAP Databricks PR (2025-02-13) · Databricks–Anthropic PR
(2025-03-26, "strategic, five-year partnership", 10,000+ customers) ·
Databricks–Neon PR (2025-05-14, "over 80 percent of the databases provisioned
on Neon were created automatically by AI agents") · Salesforce expansion story
(2026-06-16) · Accenture Databricks Business Group PR (2026-03-17) · Deloitte
awards article (2026-06-15) · Microsoft expansion PR (2026-07-23) · Brickbuilder
Partner Network launch blog (2026-02-11). Newsroom-page context (A): Databricks
>80% YoY growth / $7B+ run-rate (2026-08-13); $188B-valuation strategic round
(2026-07-16).
Official PR URLs that 404 on direct read — claims kept at B: Wipro partnership
PR; Informatica IWM-2026 PR (date slug 2026-05-20 unverified). Live
partner-directory crawl still pending (browser path D85-gated).

## Scoring (reproducible; applied to the 10 plan-relevant counterparties only)
**score = (0.5·signal + 0.3·overlap + 0.2·cost⁻¹) / 2**, components 0–10, every
level defined. Sort = score desc; **ties: higher overlap, then signal, then
alphabetical**.

signal: 10 named in 2026 official partnership PR or 2026 award + co-marketing
≤6 mo · 9 2026 award + co-marketing ≤12 mo · 8 2026 award winner (awards blog) ·
7 award-nominated/shortlisted official mention 2026 · 6 official partnership PR
>12 mo old · 5 dated partnership PR 24–30 mo · 4 official mention >18 mo ·
3 program page presence, no dated item · 2 program-level only · 1 incidental
official mention · 0 nothing official.

overlap (RIG ICPs: healthcare/dental/medspa, law, fractional-CPA/PE,
manufacturing, construction, service-business): 10 award in a matching vertical ·
9 awards in ≥2 matching verticals · 8 named clients/use-cases in a matching
vertical · 7 official partnership names an adjacent vertical (finance≈PE/CPA;
retail/consumer≈service-business) · 6 official materials reference an adjacent
vertical · 5 named customers in an adjacent vertical · 4 adjacent vertical
claimed without named evidence · 3 horizontal offer, adjacency implied only ·
2 enterprise-generic only · 1 no vertical language · 0 positioning conflicts
with RIG ICPs.

cost⁻¹ (inverse entry cost): 10 self-service (Built-On registration/Marketplace) ·
9 self-service with light editorial review · 8 small-SI teaming (hundreds of
staff) · 7 mid-SI teaming · 6 ISV co-build program application (no self-service
path) · 5 large-SI teaming · 4 ISV co-marketing · 3 Tier-1 alliance gate ·
2 enterprise-only procurement · 1 no partner motion · 0 closed program.

## Plan-relevant counterparties — sorted by score; each row = one relationship

| # | target | tier | why it can change RIG's plan | evidence (date) | sig | ovl | c⁻¹ | calc | score | RIG wedge (C) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Cognizant | A | **Manufacturing PoY 2026 — the only award in a core RIG ICP** ("18 manufacturing use cases") | awards blog 2026-06-15 | 8 | 10 | 5 | (4.0+3.0+1.0)/2 | **4.0** | manufacturing vertical co-sell |
| 2 | Accenture/Avanade | A | Global Partner of the Year 2026 (8th consecutive yr) **and Healthcare PoY**; BG >25,000 trained | awards 2026-06-15 + accenture.com PR 2026-03-17 | 10 | 8 | 3 | (5.0+2.4+0.6)/2 | **4.0** | subcontract into healthcare workstreams |
| 3 | Salesforce | A | Platform gravity: expanded partnership (Zero Copy, Federated Auth/Search, MuleSoft Agent Scanners, Slack Genie); owns Informatica; ISV Business App PoY | salesforce.com 2026-06-16 + awards 2026-06-15 | 10 | 7 | 4 | (5.0+2.1+0.8)/2 | **3.95** | CRM-triangulation pitch |
| 4 | SAP | A | The money: "earmark $250M to help make customers and system integrator partners successful … across deployment and migrations"; Manufacturing ISV PoY | SAP PR 2025-02-13 + awards 2026-06-15 | 10 | 6 | 3 | (5.0+1.8+0.6)/2 | **3.7** | PE-portfolio CFO plays on migration wave |
| 5 | Health Catalyst | A | **Healthcare PoY (ISV) 2026** — nearest-ISV adjacency to RIG's dental/medspa lane | awards 2026-06-15 | 8 | 8 | 4 | (4.0+2.4+0.8)/2 | **3.6** | Marketplace co-listing / referral path |
| 6 | Celebal Technologies | A | APJ PoY + Migration & Modernization PoY with "SAP data integration solutions" — small SI operating the SAP wave | awards 2026-06-15 | 8 | 5 | 7 | (4.0+1.5+1.4)/2 | **3.45** | SAP-wave subcontract (realistic terms) |
| 7 | Tredence | A | Business Transformation PoY; named customers include healthcare systems | awards 2026-06-15 | 8 | 5 | 7 | (4.0+1.5+1.4)/2 | **3.45** | healthcare-client subcontract |
| 8 | Indicium AI | A | Latin America PoY, Brazil-based — smallest named winner; fastest teaming test | awards 2026-06-15 | 8 | 3 | 8 | (4.0+0.9+1.6)/2 | **3.25** | cheapest subcontract experiment |
| 9 | Koantek | A (B for staff-size detail) | Lakebase PoY; Databricks-exclusive SI selling an "AppBase" starter-kit pattern — template for RIG's packaged play | awards 2026-06-15 | 8 | 3 | 7 | (4.0+0.9+1.4)/2 | **3.15** | competitive template for D85-branded app kit |
| 10 | Anthropic | A | AI Transformations PoY 2026 + "strategic, five-year partnership" PR bringing Claude natively to 10,000+ companies ($100M figure is Forbes-only, excluded from scoring) | awards 2026-06-15 + PR 2025-03-26 | 8 | 3 | 6 | (4.0+0.9+1.2)/2 | **3.05** | Claude-on-Databricks co-build content |

Note: Anthropic overlap re-scored to 3 under the explicit rubric (horizontal
offer, adjacency implied only), which drops it below Koantek and Indicium; its
PR is now direct-read A, so no B claim feeds its score.

Not scored (won't change RIG's plan near-term), appendix facts only:
Deloitte [A] (NA+Banking+SLED PoY, 2026-06-15), Microsoft [A] (partnership
"through the 2030s", 2026-07-23), EY [A] (Customer Impact + Financial Services
PoY, 6,900+ trained), Wipro [award A; partnership claim B, PR URL 404]
(Innovation PoY), Tiger Analytics [A] (Retail PoY), OpenAI [A] (AI Agents PoY),
Slalom [A] (Platform + Insurance PoY), NTT Data [A] (APJ Growth PoY),
Informatica [B] (IWM-2026 agentic/MCP expansion; PR URL 404, date slug
2026-05-20 unverified), Capgemini [A] (EMEA + CME PoY), Infosys [A] (Visionary
+ Governance PoY), TCS [A] (Data Warehouse + Talent PoY). Full 2026 roster (A,
awards blog 2026-06-15): also ZS (Life Sciences), EPAM (AI), Entrada (Genie),
Lovelytics (Energy + Brickbuilder), LTM (COE), Aimpoint Digital, v4c.ai
(Emerging), NIIT MTS (training); ISV: Sigma, Qlik, Collibra, Datadog, MinIO,
NVIDIA, Replit, SAP Manufacturing ISV, Epsilon/Celonis/Kythera (Built-On),
S&P Global, Cotality, D&B, FactSet, Trade Desk, IQVIA, Kraken, Acxiom,
Palantir, Moody's, Fivetran, Glean, Omni. Neon acquisition: A direct-read,
2025-05-14.

Program facts (A, BPN blog 2026-02-11): unified Bronze→Silver→Gold→Platinum
across Consulting&SI / Connected Tech / Data providers / Built-On; Velocity
incentives = Source/Activate/Grow (consumption rebates); MDF proposal-based at
Silver → strategic co-investment at Platinum; Specializations = 6 Core
Industries + 4 Core Products (GenAI, Lakeflow); ecosystem "7,000+ partners",
GSI practice growth "101% YoY" (blog figures).

Disambiguations (do not conflate):
- **Two $250M figures**: SAP-success earmark for customers+SI deployments/
  migrations (SAP PR 2025-02-13) vs Databricks India investment (linked from
  Accenture PR 2026-03-17).
- **Seven vs eight years**: Accenture PR (2026-03-17): "Global SI Partner of
  the Year seven consecutive years"; awards blog (2026-06-15): Global Partner
  of the Year "eighth consecutive year (2019–2026)". Both quoted as published;
  awards blog governs ranking.

## Tier C — RIG targeting hypotheses (not evidence)
- H1 Tier-1 SIs under-staff RIG verticals (dental/legal/construction) →
  validate via RFP language + directory skill tags.
- H2 SAP $250M wave is the 12-month money event; Celebal/Infosys/Capgemini
  (SAP-integration award language) operate it → subcontract them, don't wait
  for the fund.
- H3 Built-On track = RIG's lowest-cost entry; D85 gates presented as PWAF
  evidence. (Program steps A; cost estimate C.)
- H4 small/mid awardees (Indicium, Celebal, Tredence) convert to subcontract
  faster than Tier-1 → run as scored outreach experiments.

## Remaining validation before remote publication
1. Relocate live canonical pages for the two B claims: Wipro partnership PR,
   Informatica IWM-2026 PR (both 404 today).
2. Koantek own-site page for the staff-size/AppBase B detail (award itself is A).
3. Partner-directory crawl (tier + specialization) — browser-gated.
4. Marketplace scan for vertical-agent MCP listings (competition).
