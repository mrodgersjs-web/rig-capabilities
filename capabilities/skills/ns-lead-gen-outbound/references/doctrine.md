# ns-lead-gen-outbound stage doctrine

Distilled from Nick Saraev's videos for this stage (paraphrased; tags validated against video ids and lengths on 2026-10-21; 47 malformed tags removed, 94 kept). Source notes are local only: ~/rig-knowledge-raw/nick-saraev/notes.

## Core laws

- **The domain is the atomic unit of lead gen.** Build every pipeline around a list of company domains first, regardless of the source (AirScape, Google Maps, LinkedIn). Domains are the critical input for all downstream enrichment tools, and filtering by domain presence before spending credits prevents wasted spend on leads without websites.CLAIM(2XHgJXX49Jk@3m)CLAIM(eElnA0mCzXw@8m)[consensus]
- **Brute-force email patterns via domain.** Take a person's name and company domain, then test plausible patterns (first@domain, first.last@domain) until one resolves. Domain-based lookups yield ~70% success rates compared to ~55-60% for company-name-only lookups, making them the most reliable method for surfacing correct addresses.CLAIM(2XHgJXX49Jk@1m)CLAIM(AKNKI9uXjdQ@21m)[consensus]
- **Scrape raw HTML and parse with regex/LLM.** Request page content via HTTP, convert to plain text or markdown to save tokens, and use regex or LLMs to extract structured fields (email, phone, pitch angles). This extracts contact data from virtually any webpage without dedicated scrapers and turns unstructured dumps into CRM rows.CLAIM(2XHgJXX49Jk@2m)CLAIM(yYVfcfa7n5A@12m)[consensus]
- **Target companies actively hiring in your niche.** Scrape LinkedIn Jobs or Indeed for firms posting roles related to your service. These listings represent companies with committed budget and stated pain points, making them the warmest possible cold-outreach targets compared to generic directories.CLAIM(2XHgJXX49Jk@26m)CLAIM(b83zwuCRQYw@1m)[consensus]
- **Deduplicate before enrichment.** Always deduplicate scraped domain lists before feeding them into paid tools like Anymail Finder. Duplicates silently consume credits and distort cost-per-lead metrics, making your unit economics look worse than they are.CLAIM(2XHgJXX49Jk@18m)[single-source]
- **Use single-domain searches for enterprise arbitrage.** When targeting large enterprises, run single-domain company searches rather than bulk searches. You pay one credit but extract roughly 40 publicly listed emails per domain, dramatically lowering the cost per contact for high-value targets.CLAIM(2XHgJXX49Jk@9m)[single-source]
- **Scrape niche directories for unsaturated leads.** Scraping specific platforms or directories directly produces leads that have not been saturated by mass cold outreach, yielding higher reply rates than data purchased from third-party marketplaces like Apollo.CLAIM(2XHgJXX49Jk@29m)[single-source]
- **Cold email remains the highest ROI channel.** Despite claims of its death, cold email returns ~$3 for every $1 spent initially, rising to $15-20 per dollar once mastered. It is the top-ranked acquisition channel for automation agencies due to low barrier to entry and scalable infrastructure.CLAIM(IJBp8MAAMGQ@1m)[single-source]
- **Reply speed drives conversion.** The send-time-to-reply window is critical; handling a reply within 60 seconds can raise downstream conversion by up to 396%. Speed signals professionalism and keeps the lead warm during the initial interest spike.CLAIM(IJBp8MAAMGQ@2m)[single-source]
- **Risk reversal is the biggest differentiator.** A strong guarantee matters more than list quality or tools. Without risk reversal (e.g., "or you don't pay"), reply rates stall at 2-3%. Refund language should be avoided; "no strings attached" or "or you don't pay" frames the offer as pay-for-performance rather than a refund of failure.CLAIM(IJBp8MAAMGQ@3m)CLAIM(v9f87-aHbzE@3m)[consensus]
- **Niche down hard for higher response rates.** The intersection of specific industries and technologies (e.g., "Shopify dog-food WordPress store owners") beats generic "marketing agencies." Hyper-specific targeting reduces competition and increases relevance, though some high-ticket buyers may prefer broader legitimacy signals.CLAIM(v9f87-aHbzE@5m)[single-source]
- **Freelancer positioning outperforms agency framing.** On first contact, positioning as a freelancer often yields better response rates than agency or marketplace framing because it implies direct access and lower overhead. Test this per industry, as some buyers require perceived corporate legitimacy.CLAIM(v9f87-aHbzE@5m)[single-source]
- **Front-load social proof with recent results.** Place your strongest case study (with a recent time marker like "last month") at the top of the email or in the subject line. Buried proof is wasted; recent, specific numbers (e.g., "$962.7M/yr") separate you from bot-farm senders and build immediate credibility.CLAIM(v9f87-aHbzE@12m)CLAIM(v9f87-aHbzE@16m)[single-source]
- **Micro-hacks improve deliverability and tone.** Use all-lowercase subject lines to read as handwritten, avoid HTML signatures to protect deliverability, and include "sent from my iPhone" to signal authenticity. These small tweaks can add ~0.5% to reply rates by reducing the "mass blast" perception.CLAIM(v9f87-aHbzE@10m)[single-source]
- **Deep personalization requires multi-page scraping.** Extract all internal links from a prospect's site, scrape each page, summarize them with AI, and combine into an icebreaker. This depth implies real research and drives 5-10% reply rates, whereas one-page scraping often misses context.CLAIM(oAWe5wFwHlo@10m)[single-source]
- **Use AI for structure, humans for tone in personalization.** AI can generate icebreakers from scraped data, but fully AI-generated messages often read flamboyant or hallucinated. Use AI to customize fields in a proven script rather than writing from scratch, ensuring the last 20% of personalization feels human.CLAIM(5E580yoD4eo@6m)CLAIM(5E580yoD4eo@34m)[consensus]
- **Replace paid APIs with direct HTTP requests + parsing.** Instead of paying for scraping APIs, send direct HTTP requests to search URLs (e.g., Google Maps) and parse the HTML yourself using regex. This eliminates per-request costs entirely, though it requires handling rate limits via proxies.CLAIM(OroDNJl-pyc@2m)[single-source]
- **Build automation from the inside out (core logic first).** Develop workflows by testing core logic modules first before wiring them together. Use limit nodes during development to cut execution time, and set HTTP nodes to "continue on error" so single failures do not halt entire batches.CLAIM(OroDNJl-pyc@1m)CLAIM(OroDNJl-pyc@15m)[consensus]
- **Automate invoice recovery for immediate cash flow gains.** Unpaid invoices are usually lost to neglect, not refusal. A simple automated nudge system (escalating copy at 7/14/21/28/35/42 days) can recover $5-20K/year for an average agency with minimal setup effort.CLAIM(h-pQz4E1p3o@12m)[single-source]
- **Productize services to decouple time from revenue.** Convert bespoke services into standardized packages with fixed deliverables and prices. This eliminates scope creep, reduces onboarding friction, and allows new engagements to start at ~80% completion, widening profit margins as volume grows.CLAIM(itA4M364nd8@1m)[single-source]

## Procedures

**AirScape → Anymail Finder Pipeline**
1. Go to airscape.ai, set location, company size, and keyword (e.g., "PPC agency"). Click "Preview companies."CLAIM(2XHgJXX49Jk@2m)2. Click "Load all companies to a table." Results include names and LinkedIn URLs but typically not domains.CLAIM(2XHgJXX49Jk@3m)3. Click "Company Domain" column, select company-name field as lookup source, add rows, and run built-in workflow to resolve domains.CLAIM(2XHgJXX49Jk@3m)4. Export enriched table as CSV (selected rows only).CLAIM(2XHgJXX49Jk@4m)5. In Anymail Finder, go to Bulk Search → New Bulk → upload CSV → select "Decision Maker Search" → map columns → Process.CLAIM(2XHgJXX49Jk@4m)6. Review results (name, role, email, valid flag). Download; credits charged only for found emails.CLAIM(2XHgJXX49Jk@5m)**LinkedIn Sales Navigator → Vain/PhantomBuster → Anymail Finder**
1. In Sales Navigator, filter by job titles (founder, CEO), geography, and headcount. Aim for 2,000–2,500 results.CLAIM(2XHgJXX49Jk@6m)2. Copy search URL. In Vain (or PhantomBuster), create order/scrape using your LinkedIn profile cookie token.CLAIM(2XHgJXX49Jk@6m)3. Download CSV (first name, last name, title, etc.).CLAIM(2XHgJXX49Jk@7m)4. In Anymail Finder, start New Bulk → "Person Name Search" → upload CSV. Tool resolves domains via search then applies enrichment.CLAIM(2XHgJXX49Jk@8m)**n8n Automated Scrape + AI Extraction Workflow**
1. In Apollo.io, build filtered list (Founder/Partner titles, location). Note search URL.CLAIM(yYVfcfa7n5A@5m)2. In Apify Store, use `code_crafter/apollo-io-scraper`. Paste Apollo URL, set record count, run actor. Export CSV.CLAIM(yYVfcfa7n5A@6m)3. In Make.com/n8n, filter leads where `website` AND `email` are non-empty.CLAIM(yYVfcfa7n5A@11m)4. HTTP GET each lead's website URL (follow redirects max 21). Convert HTML to plain text/markdown to save tokens.CLAIM(yYVfcfa7n5A@12m)CLAIM(oAWe5wFwHlo@17m)5. OpenAI Call 1: Extract structured context (`website_context`, `person_context`, `unique_angles`) into JSON from scraped text + Apollo fields.CLAIM(yYVfcfa7n5A@18m)6. OpenAI Call 2: Generate newsletter/icebreaker using JSON context + style example + humanizing rules (shorten names/locations, focus on small details).CLAIM(yYVfcfa7n5A@15m)CLAIM(oAWe5wFwHlo@24m)7. Create Google Doc titled "For {First Name} – Custom Newsletter" with generated content.CLAIM(yYVfcfa7n5A@22m)8. Push lead to Instantly via API POST, passing Google Doc link in `custom_variables`. Subject: "For {First Name}, I wrote you a newsletter."CLAIM(yYVfcfa7n5A@33m)**Invoice Recovery Automation**
1. Source invoices from Stripe/QuickBooks/Sheets where status=open/overdue.CLAIM(h-pQz4E1p3o@16m)2. Parse sent date (`yyyy-mm-dd`) into datetime object. Compute days since sent: `(now - sent)` / ms-per-day, rounded.CLAIM(h-pQz4E1p3o@6m)3. Route by day buckets: 7, 14, 21, 28, 35, 42 days since sent.CLAIM(h-pQz4E1p3o@16m)4. Send escalating follow-up email per bucket (gentle check-in -> firmer -> pressure). Vary copy slightly per week.CLAIM(h-pQz4E1p3o@11m)5. Watch for payment events (Stripe `payment_intent.succeeded`). Retrieve customer email -> Search sheet rows -> Update status cell to "paid".CLAIM(h-pQz4E1p3o@19m)## Decision rules

*   **If targeting large enterprises:** Use single-domain company searches in Anymail Finder instead of bulk searches to maximize emails per credit (~40 vs ~5-15). **CLAIM(2XHgJXX49Jk@9m)**
*   **If scraping Google Maps at scale:** Route traffic through a SER proxy after a few hundred requests to avoid rate-limiting and bot detection; otherwise use direct HTTP requests with delays for small batches. **CLAIM(OroDNJl-pyc@19m)** **CLAIM(OroDNJl-pyc@10m)**





## Failure modes









## Changed views



