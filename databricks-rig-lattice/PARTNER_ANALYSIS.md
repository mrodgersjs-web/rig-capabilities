# Databricks Partner Analysis — 2026-09-10
## Status: SOURCED DRAFT — pending remaining validation before remote publication

Evidence tiers: **A** = official page read directly this session (dates are page
publication dates); **B** = search-summary lead, page not yet read directly;
**C** = RIG hypothesis/recommendation, not evidence.

A-validated by direct read (exact publication dates): 2026 Global Partner Awards
blog (2026-06-15) · SAP Databricks PR (2025-02-13) · Salesforce expansion story
(2026-06-16) · Accenture Databricks Business Group PR (2026-03-17) · Deloitte
awards article (2026-06-15) · Microsoft expansion PR (2026-07-23) · Brickbuilder
Partner Network launch blog (2026-02-11).
Still pending direct read: Anthropic 2025 PR, Neon PR, Informatica IWM-2026 PR
(date from URL slug `20260520` only), Wipro partnership PR (URL 404 — claim
demoted to B), live partner-directory crawl (browser path D85-gated).

## Scoring (reproducible)
Components 0–10; **score = (0.5·signal + 0.3·overlap + 0.2·cost⁻¹) / 2**.
- signal: 10 = named in 2026 official partnership PR **or** 2026 award +
  co-marketing ≤6 mo · 8 = 2026 award winner (awards blog, A) · 6 = official
  partnership PR >12 mo old · 4 = official mention >18 mo · 2 = program-level only.
- overlap: with RIG ICP verticals (healthcare/medical/medspa, law,
  fractional-CPA/PE, manufacturing, construction, service-business):
  10 = award in matching vertical · 8 = named client/use-case matches ·
  5 = adjacent (finance ≈ PE/CPA; retail/consumer ≈ service-business) ·
  2 = enterprise-generic.
- cost⁻¹: 10 = self-service (Built-On registration/Marketplace) ·
  7 = small/mid SI teaming · 5 = large-SI teaming · 4 = ISV co-marketing ·
  3 = Tier-1 alliance gate.

## Ranked target matrix (each row = one relationship; A unless noted)

| # | target | category | joint motion (verbatim-grade evidence) | date (source) | sig | ovl | c⁻¹ | calc | score | RIG wedge (C) | next validation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Accenture/Avanade | SI | Global Partner of the Year 2026, 8th consecutive year (2019–2026); Healthcare PoY; Public Sector Federal PoY; Business Group w/ >25,000 trained (BG PR) | 2026-06-15 (awards) + 2026-03-17 (accenture.com) | 10 | 8 | 3 | (5.0+2.4+0.6)/2 | **4.0** | delivery-depth subcontract on healthcare workstreams | BG teaming terms/tier gates |
| 2 | Cognizant | SI | Manufacturing Partner of the Year 2026 — "18 manufacturing use cases" | 2026-06-15 (awards) | 8 | 10 | 5 | (4.0+3.0+1.0)/2 | **4.0** | RIG manufacturing vertical co-sell; only award in a core RIG ICP | alliance contact; directory tier |
| 3 | Salesforce | platform ISV | Expanded partnership: Zero Copy + Federated Auth/Search, MuleSoft Agent Scanners, Slack Genie; ISV Business App PoY | 2026-06-16 (salesforce.com) | 10 | 7 | 4 | (5.0+2.1+0.8)/2 | **3.95** | CRM-triangulation pitch | Databricks-side mirror + H2-2026 GA list |
| 4 | Deloitte | SI | NA PoY (2nd yr) + Banking PoY + SLED PoY | 2026-06-15 (both) | 10 | 5 | 3 | (5.0+1.5+0.6)/2 | **3.55** | regulated-vertical depth | teaming terms |
| 5 | SAP | platform | SAP Databricks in Business Data Cloud; "earmark $250M to help make customers and system integrator partners successful … across deployment and migrations"; also Manufacturing ISV PoY | 2025-02-13 (PR) + 2026-06-15 (awards) | 10 | 6 | 3 | (5.0+1.8+0.6)/2 | **3.7** | PE-portfolio finance/CFO plays on migration wave | fund eligibility terms |
| 6 | Health Catalyst | ISV | Healthcare Partner of the Year (ISV) 2026 | 2026-06-15 (awards) | 8 | 8 | 4 | (4.0+2.4+0.8)/2 | **3.6** | healthcare/medspa vertical adjacency | Marketplace co-listing scan |
| 7 | EY | SI | Customer Impact PoY + Financial Services PoY 2026 (6,900+ trained) | 2026-06-15 (awards) | 8 | 7 | 4 | (4.0+2.1+0.8)/2 | **3.45** | fractional-CPA/PE finance adjacency | directory + practice scan |
| 8 | Celebal Technologies | SI | APJ PoY + Migration & Modernization PoY — "pre-built migration accelerators, SAP data integration solutions" (awards text) | 2026-06-15 (awards) | 8 | 5 | 7 | (4.0+1.5+1.4)/2 | **3.45** | SAP-wave subcontract; small-SI speed | outreach experiment |
| 9 | Tredence | SI | Business Transformation PoY — "healthcare systems" named customer set | 2026-06-15 (awards) | 8 | 5 | 7 | (4.0+1.5+1.4)/2 | **3.45** | healthcare client base subcontract | outreach experiment |
| 10 | Microsoft | platform | Partnership extended "through the 2030s"; Genie/Unity AI Gateway across M365; Cobalt | 2026-07-23 (PR) | 10 | 3 | 4 | (5.0+0.9+0.8)/2 | **3.35** | Azure Databricks co-sell | own Azure partner status |
| 11 | Indicium AI | SI | Latin America PoY (Brazil-based) | 2026-06-15 (awards) | 8 | 3 | 8 | (4.0+0.9+1.6)/2 | **3.25** | fastest-terms subcontract test | directory + contact |
| 12 | Anthropic | ISV | AI Transformations PoY 2026; 5-yr Claude deal (2025-03 PR, pending direct read; $100M figure is Forbes) | 2026-06-15 (awards) + 2025-03 (pending) | 8 | 4 | 6 | (4.0+1.2+1.2)/2 | **3.2** | Claude-first co-build story | PR direct read + Marketplace scan |
| 13 | Wipro | SI | Innovation PoY 2026 (banking: Bill Pay, KYC, FDIC 370). NOTE: "new global partnership" PR URL 404s — that claim demoted to B | 2026-06-15 (awards) | 8 | 4 | 6 | (4.0+1.2+1.2)/2 | **3.2** | capacity practice white-label | find live PR via wipro.com |
| 14 | Tiger Analytics | SI | Retail/Consumer/Travel PoY — IDX accelerator | 2026-06-15 (awards) | 8 | 4 | 6 | (4.0+1.2+1.2)/2 | **3.2** | service-business vertical subcontract | directory |
| 15 | OpenAI | ISV | AI Agents Partner of the Year 2026 | 2026-06-15 (awards) | 8 | 4 | 5 | (4.0+1.2+1.0)/2 | **3.15** | model-adjacency content plays | — |
| 16 | Koantek | SI | Lakebase PoY — Ascend AI AppBase, FDE delivery model | 2026-06-15 (awards) | 8 | 3 | 7 | (4.0+0.9+1.4)/2 | **3.15** | Lakebase migration niche partner | koantek.com direct read |
| 17 | Slalom | SI | Data+AI Platform PoY + Insurance PoY (Insurance 360 Brickbuilder) | 2026-06-15 (awards) | 8 | 4 | 5 | (4.0+1.2+1.0)/2 | **3.1** | insurance/service adjacency | directory |
| 18 | NTT Data | SI | APJ Growth PoY (Japanese banks) | 2026-06-15 (awards) | 8 | 3 | 5 | (4.0+0.9+1.0)/2 | **2.95** | APJ subcontract | directory |
| 19 | Informatica (Salesforce-owned) | ISV/data | IWM 2026: IDMC headless + Agent Bricks via MCP, Lakebase connector, MDM golden records, UC tag extraction | 2026-05-20 per URL slug (page read pending) | 8 | 4 | 4 | (4.0+1.2+0.8)/2 | **3.0** | MCP-ecosystem legitimization | page direct read |
| 20 | Capgemini | SI | EMEA PoY (25k-table UC migration) + CME PoY | 2026-06-15 (awards) | 8 | 3 | 3 | (4.0+0.9+0.6)/2 | **2.75** | EMEA subcontract | directory |
| 21 | Infosys | SI | Visionary PoY + Governance PoY (UC migrations) | 2026-06-15 (awards) | 8 | 3 | 3 | (4.0+0.9+0.6)/2 | **2.75** | governance-workstream subcontract | directory |
| 22 | TCS | SI | Data Warehouse PoY + Talent Development PoY | 2026-06-15 (awards) | 8 | 3 | 3 | (4.0+0.9+0.6)/2 | **2.75** | capacity subcontract | directory |

Unscored A-context (from awards blog, single-source, no action yet): ZS (Life
Sciences), EPAM (AI), Entrada (Genie), Lovelytics (Energy + Brickbuilder PoY),
LTM (COE), Aimpoint Digital (Digital Native), v4c.ai (Emerging), NIIT MTS
(training); ISV: Sigma (BI), Qlik (integration), Collibra (governance), Datadog
(observability), MinIO (storage), NVIDIA (AI tools), Replit (app generation),
Epsilon/Celonis/Kythera (Built-On), S&P Global + Cotality (data), D&B, FactSet,
Trade Desk, IQVIA, Kraken, Acxiom, Palantir, Moody's, Fivetran, Glean, Omni.
Neon acquisition (serverless Postgres → Lakebase) confirmed by Reuters URL
2025-05-14; databricks.com PR direct read pending.

Program facts (A, BPN blog 2026-02-11): unified Bronze→Silver→Gold→Platinum
across Consulting&SI / Connected Tech / Data providers / Built-On; Velocity
incentives = Source/Activate/Grow (consumption rebates); MDF proposal-based at
Silver → strategic co-investment at Platinum; Specializations = 6 Core
Industries + 4 Core Products (GenAI, Lakeflow); Delivery Expert badges;
ecosystem "7,000+ partners", GSI practice growth "101% YoY" (blog figures).

Disambiguations (do not conflate):
- **Two $250M figures**: SAP-success earmark for customers+SI deployments/
  migrations (SAP PR 2025-02-13) vs Databricks India investment (linked from
  Accenture PR 2026-03-17).
- **Seven vs eight years**: Accenture PR (2026-03-17) says "Global SI Partner of
  the Year seven consecutive years"; awards blog (2026-06-15) says Global
  Partner of the Year "eighth consecutive year (2019–2026)". Both quoted as
  published; later-dated awards blog governs the ranking.

## Tier C — RIG targeting hypotheses (not evidence)
- H1 Tier-1 SIs under-staff RIG vertical depth (dental/legal/construction) →
  validate via RFP language + directory skill tags.
- H2 SAP $250M wave is the 12-month money event; Celebal/Infosys/Capgemini
  (SAP-integration award language) are the wave's operators → subcontract them,
  don't wait for the fund.
- H3 Built-On track = RIG's lowest-cost entry; D85 gates presented as PWAF
  evidence. (Program steps A; cost estimate C.)
- H4 small/mid awardees convert to subcontract faster than Tier-1. Run as
  scored outreach experiments (Indicium, Celebal, Tredence first).

## Remaining validation before remote publication
1. Direct-read pending PRs: Anthropic, Neon, Informatica, Koantek, Wipro-live URL.
2. Partner-directory crawl (tier + specialization per target) — browser-gated.
3. Marketplace scan for existing vertical-agent MCP listings (competition).
