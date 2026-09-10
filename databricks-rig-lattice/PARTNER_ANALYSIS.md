# Databricks Partner Analysis — 2026-09-10

Method: web search sweep 2026-09-10; rows kept only where the evidence is an
official press release / official partner page / major wire. Partner directory
was NOT crawled live (JS-rendered; browser path currently D85-gated) — that
crawl is the top validation step below. Confidence = source authority × recency.

Status legend:
- **A-verified** — official source, relationship exists, dated URL below.
- **B-lead** — third-party/summary source or inference from A facts; not a claim
  of relationship.
- **C-hypothesis** — RIG targeting statement / recommendation; explicitly not
  evidence.

Likelihood-to-work-with-RIG score (0–5): 0.5×co-sell/Marketplace/PWAF signal +
0.3×RIG vertical-buyer overlap + 0.2×inverse entry cost. Verified co-program
signals (awards, Business Group, new partnership PRs) outrank brand adjacency.

## Tier A — verified relationships (official, dated)

| target | cat | joint motion (evidence) | buyer/use case | evidence (date, URL) | conf | RIG wedge (C) | next validation | score |
|---|---|---|---|---|---|---|---|---|
| SAP | platform | SAP Databricks in Business Data Cloud; $250M pledged for customer+SI migrations | ERP customers, PE-portfolio finance/CFO | 2025-02 databricks.com: https://www.databricks.com/company/newsroom/press-releases/databricks-announces-launch-sap-databricks | high | migration-wave subcontract; fractional-CPA/PE vertical depth | confirm $250M fund status + partner eligibility terms | 4.6 |
| Salesforce | platform | expanded 2026 partnership: Data 360 Zero Copy, Federated Auth/Search, MuleSoft Agent Scanners, Slack; ISV Business App Partner of Year DAIS '26 | Agentforce buyers, CRM-centric ops | 2026-07 salesforce.com: https://www.salesforce.com/news/stories/salesforce-databricks-shared-foundation-of-human-agent-work-announcement/ | high | one-pitch triangulation with RIG CRM plays | check Databricks-side PR mirror + integration cert list | 4.2 |
| Accenture/Avanade | SI | Global Partner of the Year 2026 (8th yr); Accenture Databricks Business Group launched | global enterprise agentic AI | 2026-07 databricks.com awards: https://www.databricks.com/blog/databricks-announces-2026-global-partner-awards · 2026 accenture.com newsroom: https://newsroom.accenture.com/news/2026/accenture-and-databricks-accelerate-enterprise-adoption-of-ai-applications-and-agents-at-scale | high | delivery-depth subcontract on vertical workstreams | probe BG partner/teaming terms (tier gates likely) | 4.0 |
| Deloitte | SI | NA Partner of Year 2026 (2nd yr) + Banking + Public Sector SLED (3 awards) | regulated finance, government | 2026-07 deloitte.com: https://www.deloitte.com/us/en/alliances/articles/databricks-partner-award.html | high | regulated-vertical depth (healthcare/legal) | same teaming-terms probe | 3.8 |
| Microsoft | platform | expanded strategic partnership "through the 2030s"; Databricks runs own ops on Azure | Azure-centric enterprises | 2026-08 databricks.com: https://www.databricks.com/company/newsroom/press-releases/databricks-and-microsoft-expand-partnership-help-enterprises-bring | high | Azure Databricks co-sell path | map to existing Azure partner status (none yet) | 3.5 |
| Wipro | SI | new/enhanced global partnership; "self-contained Databricks practice" | modernization at scale | 2026-08 wipro.com: https://www.wipro.com/newsroom/press-releases/2026/wipro-partners-with-databricks-to-enable-enterprises-modernize-data-and-deploy-ai-at-scale/ | high | capacity-hungry practice → white-label vertical accelerators | contact alliance via Built-On/MDF route | 3.9 |
| Anthropic | model ISV | 5-year partnership; Claude native on platform (Forbes reports ~$100M) | enterprise agent builders | 2025-03 databricks.com: https://www.databricks.com/company/newsroom/press-releases/databricks-and-anthropic-sign-landmark-deal-bring-claude-models · 2025-03 Forbes: https://www.forbes.com/sites/richardnieva/2025/03/26/anthropic-databricks/ | high (relationship) / med ($ figure is Forbes) | RIG is already Claude-first; co-build story | Marketplace listing co-brand possibility | 3.4 |
| Capgemini | SI | EMEA Partner of the Year 2026 | EMEA enterprise | 2026-07 databricks.com awards (URL above) | high | EMEA subcontract | directory skills tags | 3.2 |
| Celebal Technologies | SI | APJ Growth Partner of the Year 2026 | APJ mid-market | 2026-07 databricks.com awards (URL above) | high | faster subcontract than Tier-1 (hypothesis) | outreach experiment | 3.6 |
| NTT Data | SI | APJ Growth Partner of the Year 2026 | APJ | 2026-07 databricks.com awards (URL above) | high | subcontract | directory | 3.0 |
| Indicium AI | SI | Latin America Partner of the Year 2026 | LatAm | 2026-07 databricks.com awards (URL above) | med | niche subcontract | directory | 2.6 |
| Koantek | SI | Lakebase category recognition 2026 | Lakebase early adopters | 2026-07 databricks.com awards (URL above) | med | Neon/Lakebase migration niche | skills page | 2.9 |
| Informatica (Salesforce-owned) | ISV/data | expanded Databricks capabilities at IWM 2026: IDMC headless + Agent Bricks via MCP, Lakebase connector, MDM golden records, UC tag extraction | governed-data buyers | 2026-05-20 informatica.com: https://www.informatica.com/about-us/news/news-releases/2026/05/20260520-informatica-brings-headless-data-management-lakebase-connectivity-golden-record-publishing-and-unity-catalog-tag-extraction-to-the-databricks-platform.html · close: 2025-11-18 salesforce.com: https://www.salesforce.com/uk/news/press-releases/2025-11-18/salesforce-completes-acquisition-of-informatica/ | high | MCP-ecosystem adjacency (their MCP presence legitimizes RIG MCP route) | none needed for adjacency claim | 3.1 |
| EY / Infosys / TCS / Slalom / EMEA regional winners | SI | category/POY wins 2026 (banking, governance, DW, platform) | per-category | 2026-07 databricks.com awards (URL above) | high (per award row) | subcontract candidates | directory per firm | 2.8–3.4 |
| Neon | internal product | $1B acquisition; serverless Postgres for agents → Lakebase | agent-dev teams | 2025-05 databricks.com: https://www.databricks.com/company/newsroom/press-releases/databricks-agrees-acquire-neon-help-developers-deliver-ai-systems · Reuters: https://www.reuters.com/technology/databricks-buy-startup-neon-1-billion-wsj-reports-2025-05-14/ | high | build on Lakebase = riding their integration wave | architecture decision, not partnership | — |

Program facts (A, official): Brickbuilder Partner Network Bronze→Platinum, PWAF
promotion paths (Connected/Data/Built-on), Source/Activate/Grow incentives, MDF,
6 Core Industries + 4 Core Products specializations (GenAI, Lakeflow) —
2026-02 blog https://www.databricks.com/blog/building-whats-next-together-introducing-brickbuilder-partner-network-agentic-ai-era +
2026-05 guide https://www.databricks.com/sites/default/files/2026-05/partner-program-guides-2026.pdf.
Agent-product integration surface (PWAF guidance): Managed MCP, Genie APIs via
MCP, Marketplace MCP publishing — official partner-architecture docs
https://databrickslabs.github.io/partner-architecture/isv-partners/product-categories/ai-ml (undated doc; treat requirements as current-but-uncertain).

## Tier B — leads (not evidence-backed relationships)

- Quantiphi, Thoughtworks, "Slalom elite status" per dataconsultingfirms.com
  ranking (2026-05, third-party): https://dataconsultingfirms.com/insights/databricks-consulting-partners-2026 —
  low authority; Slalom's award IS in Tier A, Quantiphi/Thoughtworks are B until
  directory-verified.
- "Cross-Industry Partner Accelerators (Agentic AI/GenAI/LLMOps)" — databricks.com
  blog 2025-11: https://www.databricks.com/blog/introducing-databricks-cross-industry-partner-accelerators-agentic-ai-genai-and-llmops —
  program exists (A) but RIG eligibility/benefit = B.
- Search result "Claude Fable 5 available on Databricks" — UNVERIFIED model-name
  claim on a databricks.com URL; excluded pending direct check.

## Tier C — RIG targeting statements (hypotheses, all)

- H1: Tier-1 SIs under-staff dental/legal/construction vertical depth →
  subcontract demand. UNVERIFIED; validate via RFP language + directory skills
  tags.
- H2: SAP $250M migration wave + PE-portfolio CFO use cases = 12-month revenue
  event. Money-event claim is inference; fund existence is A.
- H3: Built-On track (Marketplace MCP server + PWAF Built-on validation) is
  RIG's lowest-cost legitimate entry; D85 gates presented as PWAF evidence.
  Entry-cost estimate = hypothesis; program steps are A.
- H4: mid-tier awardees (Celebal, Tredence, Indicium) convert to subcontract
  faster than Accenture/Deloitte. Inference from size, untested; run as
  scored outreach experiments.

## Top-ranked RIG entry list (by score, C-adjusted)

1. SAP-migration wave plays (4.6) — via whoever wins migration pods; validate fund terms.
2. Salesforce/Databricks triangulation (4.2) — existing RIG CRM assets.
3. Wipro practice (3.9) — newest, capacity-hungry, A-dated PR.
4. Deloitte regulated verticals (3.8) / Accenture BG (4.0, gated teaming).
5. Celebal APJ experiment (3.6) — cheap subcontract test.

Next validation (one batch, when browser path unlocks): crawl
databricks.com/partners/partner-directory for each target's tier +
specializations; confirm DAIS '26 award pages; check Marketplace for existing
vertical-agent MCP listings (competition scan).
