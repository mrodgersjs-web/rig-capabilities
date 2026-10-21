# ns-automation-builds stage doctrine

Distilled from Nick Saraev's videos for this stage (paraphrased; tags validated against video ids and lengths on 2026-10-21; 0 malformed tags removed, 135 kept). Source notes are local only: ~/rig-knowledge-raw/nick-saraev/notes.

## Core laws

1.  **Prioritize distribution and revenue systems over raw technology.** Selling AI alone does not generate wealth; building operational pipelines and distribution channels creates enterprise value.CLAIM(oUpC98ueWn8@0m)CLAIM(oUpC98ueWn8@8m)[consensus]
2.  **Automate back-end processes, not high-ticket sales conversations.** Chatbots fail in high-value deals where human rapport is required; automation belongs in data enrichment, routing, and high-volume low-value tasks.CLAIM(oUpC98ueWn8@5m)CLAIM(oUpC98ueWn8@7m)CLAIM(oUpC98ueWn8@9m)[consensus]
3.  **Sell guaranteed business outcomes, not technical workflows.** Positioning as an equity partner with performance guarantees commands higher pricing than selling commodity automation scripts.CLAIM(Al5I8tPlgU0@15m)CLAIM(Td8ymV1Cc_8@1m)CLAIM(Td8ymV1Cc_8@4m)[consensus]
4.  **Use event-driven triggers over polling to save operations.** Polling consumes excessive API operations; use webhooks, custom mail hooks, or instant triggers to reduce costs and latency.CLAIM(Qbi41HouOiI@16m)CLAIM(Qbi41HouOiI@20m)CLAIM(sGyj2HYZIEQ@3m)[consensus]
5.  **Save and version control frequently.** Save scenarios after every major change to enable fast rollbacks, and use the workflow history panel to restore earlier revisions.CLAIM(Qbi41HouOiI@0m)CLAIM(r6uX3btBgvw@7m)[consensus]
6.  **Test modules in isolation.** Run individual modules to create a two-second feedback loop rather than waiting for full scenario execution, which wastes time and operations.CLAIM(Qbi41HouOiI@1m)CLAIM(942qTUO2Nds@2m)CLAIM(942qTUO2Nds@26m)[consensus]
7.  **Use Set/Get Variable patterns to flatten canvases.** Declare variables early and retrieve them late to avoid dragging wires across the entire canvas, improving readability and vertical layout.CLAIM(Qbi41HouOiI@3m)CLAIM(Qbi41HouOiI@7m)[consensus]
8.  **Prefer Switch modules over Routers for maintainability.** Switches cover all inputs in a single node and are easier to maintain than multiple router branches with filters.CLAIM(Qbi41HouOiI@30m)CLAIM(vHJH3TShGks@25m)CLAIM(fBCpD4rIm5I@34m)[consensus]
9.  **Add delays between sequential API calls.** Insert sleep modules (1–3 seconds) between create-and-fetch sequences or email sends to prevent race conditions and spam filtering.CLAIM(Qbi41HouOiI@10m)CLAIM(942qTUO2Nds@7m)CLAIM(hQ5WyIZglx8@27m)[consensus]
10. **Use generic HTTP modules for custom integrations.** The generic HTTP module is more reliable than flaky native connectors (like Gmail filters) and allows access to any API via curl import.CLAIM(Qbi41HouOiI@15m)CLAIM(JdKC8TOPfJE@0m)CLAIM(y-eEbmNeFZo@23m)[consensus]
11. **Convert HTML to text or Markdown before AI processing.** Raw HTML is noisy and token-expensive; strip tags or convert to Markdown to reduce costs and improve model parsing.CLAIM(xs10RZU0Gp0@17m)CLAIM(y-eEbmNeFZo@5m)CLAIM(Ksr_H30Oris@30m)[consensus]
12. **Validate JSON syntax strictly.** Missing commas, trailing commas, or unescaped characters cause 400 errors; use AI or validators to repair malformed payloads.CLAIM(JdKC8TOPfJE@24m)CLAIM(6b442bN0CyI@46m)CLAIM(898WpSTxbFU@10m)[consensus]
13. **Treat all inputs and outputs as arrays.** Even single items are wrapped in arrays; use `.length` or index access carefully, and flatten nested arrays when necessary.CLAIM(6b442bN0CyI@49m)CLAIM(2GZ2SNXWK-c@120m)CLAIM(Ksr_H30Oris@9m)[consensus]
14. **Use regex for simple extraction, AI for complex parsing.** Regex is free and fast for emails or URLs; use AI for unstructured data where regex is brittle.CLAIM(sOSrsYmo0pM@22m)CLAIM(xs10RZU0Gp0@23m)CLAIM(o9AvKxLuCRU@5m)[consensus]
15. **Split large scenarios into child workflows.** Break flows exceeding 15–20 modules or those with variable runtimes into separate scenarios connected by webhooks to avoid timeouts.CLAIM(QqE6tsHpr3U@0m)CLAIM(QqE6tsHpr3U@5m)CLAIM(QqE6tsHpr3U@11m)[consensus]
16. **Implement error handling with break handlers.** Place break handlers on every third-party API call and enable storing incomplete executions to allow manual retries.CLAIM(TtvSHo003UI@2m)CLAIM(TtvSHo003UI@3m)CLAIM(5w6Bf5pponE@69m)[consensus]
17. **Use bulk API endpoints for high-volume writes.** Replace single-row append modules with bulk JSON array posts to reduce operation counts from hundreds to one.CLAIM(898WpSTxbFU@2m)CLAIM(898WpSTxbFU@13m)[consensus]
18. **Map dropdowns using internal IDs, not labels.** Use switch modules to map human-readable labels to system-specific internal IDs to ensure accurate record creation.CLAIM(vHJH3TShGks@25m)CLAIM(fBCpD4rIm5I@40m)CLAIM(hQ5WyIZglx8@14m)[consensus]
19. **Design proposals as diagnostic audits.** Translate bottlenecks into annualized dollar waste and present solutions as a fraction of recovered capital, not just technical specs.CLAIM(jyFqnQqkS64@1m)CLAIM(jyFqnQqkS64@3m)[consensus]
20. **Standardize delivery with templates and blueprints.** Reuse prebuilt workflows so new clients require only 20% customization, creating leverage on fulfillment time.CLAIM(4gGWba-6nOk@12m)CLAIM(fIWUAodAgJw@12m)[consensus]
21. **Use webhooks for cross-platform glue.** Webhooks connect services lacking native integrations and allow modular orchestration between workflows.CLAIM(lK3veuZAg0c@0m)CLAIM(lK3veuZAg0c@15m)CLAIM(sGyj2HYZIEQ@3m)[consensus]
22. **Self-host for cost control and data privacy.** n8n self-hosting eliminates per-execution fees, while Make.com charges per operation; choose based on devops capability and volume.CLAIM(JNI1kdkxaLo@4m)CLAIM(JNI1kdkxaLo@3m)CLAIM(kq5bmrjPPAY@1m)[consensus]
23. **Prioritize speed in lead response.** Respond to inbound leads within minutes; delays significantly hurt conversion rates and perceived value.CLAIM(tev9BPwb3tM@0m)CLAIM(LbDTsMDLU4c@1m)CLAIM(gsPGdq2C97c@71m)[consensus]
24. **Use AI for filtering before expensive processing.** Filter scraped or inbound data with AI to discard irrelevant items before triggering costly downstream actions or human review.CLAIM(ntSbFUQZHJ0@5m)CLAIM(dMcIhQ2v8lE@10m)[consensus]
25. **Maintain a single source of truth.** Keep all applicant, lead, or content data in one system (CRM or Sheet) to prevent silo confusion and ensure data integrity.CLAIM(vHJH3TShGks@2m)CLAIM(QJ7Kinz7wgk@2m)[consensus]

## Procedures

### 1. Iterative Module Testing
1.  Insert a Watch trigger and add a Sleep of ~3 seconds to allow data persistenceCLAIM(942qTUO2Nds@7m).
2.  Add a List module with a limit of 1 to fetch only the test recordCLAIM(942qTUO2Nds@7m).
3.  Right-click the module and select "Run This Module Only" to verify outputCLAIM(Qbi41HouOiI@1m).
4.  Use Set Variable to cache API outputs for subsequent tests to avoid burning operationsCLAIM(942qTUO2Nds@14m).
5.  Repeat for each new module, fixing field references immediately upon failureCLAIM(942qTUO2Nds@2m).

### 2. Bulk Google Sheets Append
1.  Replace the standard Add Row module with an HTTP Make a Request moduleCLAIM(898WpSTxbFU@2m).
2.  Set method to POST and use the `values.append` endpoint with `valueInputOption=USER_ENTERED`CLAIM(898WpSTxbFU@2m)CLAIM(898WpSTxbFU@4m).
3.  Use a Text Aggregator to build a JSON array of arrays from upstream bundlesCLAIM(898WpSTxbFU@10m).
4.  Map the aggregated JSON string into the request body under the `values` keyCLAIM(898WpSTxbFU@11m).

### 3. Static Website Scraping to JSON
1.  Add an HTTP GET module with "Parse Response" enabled to fetch raw HTMLCLAIM(Qbi41HouOiI@26m).
2.  Pipe the HTML through an HTML to Text or HTML to Markdown module to reduce tokensCLAIM(xs10RZU0Gp0@17m)CLAIM(y-eEbmNeFZo@5m).
3.  Send the cleaned text to an LLM with a system prompt demanding strict JSON outputCLAIM(xs10RZU0Gp0@18m).
4.  Use a Parse JSON module to convert the LLM response string into draggable variablesCLAIM(JdKC8TOPfJE@22m).

### 4. AI Voice Agent Booking Flow
1.  Configure a Vapi assistant with a system prompt limiting steps to 3–4 for memory retentionCLAIM(SOHwpaceIDw@11m).
2.  Define tool parameters forcing date inputs to ISO 8601 format to prevent parsing errorsCLAIM(SOHwpaceIDw@19m).
3.  Create a Make.com webhook scenario to receive the tool callCLAIM(SOHwpaceIDw@5m).
4.  Query the calendar for availability and return a JSON response matching Vapi’s required `{toolCallId, results}` shapeCLAIM(SOHwpaceIDw@23m).

### 5. LinkedIn Parasite Content System
1.  Scrape top-performing posts using Apify, filtering for engagement floors (e.g., >200 reactions)CLAIM(roTg7kyw8X4@16m).
2.  Extract hook structures and outlines using a reasoning modelCLAIM(roTg7kyw8X4@56m).
3.  Draft new content using few-shot examples of the creator’s tone in the system promptCLAIM(roTg7kyw8X4@64m).
4.  Stage drafts in Airtable with status flags for scheduled publishingCLAIM(roTg7kyw8X4@80m).

### 6. Proposal Generation Pipeline
1.  Trigger on a form submission capturing raw notes and client detailsCLAIM(viN9gX030T4@41m).
2.  Use an LLM to transform rough notes into polished problem/solution statements in JSON formatCLAIM(UVLeX600irk@2m).
3.  Copy a master Google Slides template to a new fileCLAIM(viN9gX030T4@27m).
4.  Use the Replace Text action to map JSON fields to `[[placeholder]]` variables in the slide deckCLAIM(viN9gX030T4@11m).
5.  Send the proposal link via email with a payment link attachedCLAIM(UVLeX600irk@7m).

### 7. Error Handling Setup
1.  Enable "Store incomplete executions" in scenario settings to allow manual retriesCLAIM(TtvSHo003UI@3m).
2.  Attach a Break handler to every third-party API moduleCLAIM(TtvSHo003UI@2m).
3.  Configure retry attempts (e.g., 3) with exponential backoff intervals for rate-limited APIsCLAIM(TtvSHo003UI@17m).
4.  Test the error path by deliberately passing a bad ID to confirm the break triggersCLAIM(TtvSHo003UI@5m).

## Decision rules

*   **If** the business model is high-ticket sales, **then** avoid chatbot automation for closing; use it only for back-end enrichmentCLAIM(oUpC98ueWn8@5m).
*   **If** the corpus fits within the model's context window, **then** skip RAG and paste the document directly into the promptCLAIM(LqVo5dasBh0@34m).
*   **If** you need to route based on multiple conditions, **then** use a Switch module instead of a Router for easier maintenanceCLAIM(Qbi41HouOiI@30m)CLAIM(fBCpD4rIm5I@34m).
*   **If** the target website is dynamic (JavaScript-rendered), **then** escalate from HTTP GET to a headless browser or Apify scraperCLAIM(y-eEbmNeFZo@1m)CLAIM(xs10RZU0Gp0@8m).
*   **If** you are a beginner with no capital, **then** choose a service business model over a product business to learn while earningCLAIM(4gGWba-6nOk@5m).
*   **If** you require devops control and high volume, **then** self-host n8n; **if** you prefer ease of use and error handling, **then** use Make.comCLAIM(JNI1kdkxaLo@4m)CLAIM(PjKHs-L6Sn4@11m).
*   **If** an API lacks a native connector, **then** use the generic HTTP module with a curl import rather than abandoning the integrationCLAIM(JdKC8TOPfJE@17m)CLAIM(y-eEbmNeFZo@23m).
*   **If** the scenario exceeds 15–20 modules, **then** split it into child scenarios connected by webhooks to maintain readability and avoid timeoutsCLAIM(QqE6tsHpr3U@0m).
*   **If** sending multiple emails in one flow, **then** insert sleep delays between sends to prevent spam filteringCLAIM(hQ5WyIZglx8@27m).
*   **If** scraping at scale, **then** use bulk append endpoints instead of row-by-row additions to save operationsCLAIM(898WpSTxbFU@13m).

## Failure modes

*   **Eliminating human rapport in high-ticket sales:** Crude chatbots cause conversion drops that wipe out labor savingsCLAIM(oUpC98ueWn8@5m).
*   **Ignoring array structures:** Assuming single items are not arrays leads to indexing errors in n8n and MakeCLAIM(6b442bN0CyI@49m)CLAIM(2GZ2SNXWK-c@120m).
*   **JSON syntax errors:** Missing commas, trailing commas, or unescaped characters cause 400 parse errorsCLAIM(JdKC8TOPfJE@24m)CLAIM(6b442bN0CyI@46m).
*   **Polling triggers:** Using polling instead of webhooks consumes excessive operations and adds latencyCLAIM(Qbi41HouOiI@16m).
*   **Monolithic scenarios:** Building flows with too many modules makes debugging difficult and risks execution timeoutsCLAIM(QqE6tsHpr3U@0m).
*   **Hardcoding credentials:** Pasting API keys directly into the canvas exposes them in blueprint exports; use variables or secretsCLAIM(JdKC8TOPfJE@16m).
*   **Skipping error handlers:** Failing to use break handlers on API calls causes scenarios to stop abruptly on transient errorsCLAIM(TtvSHo003UI@2m).
*   **Premature expansion:** Scaling an agency without robust delivery controls leads to churn and reputational damageCLAIM(XE6VcwCBSqA@6m).
*   **Over-polishing content:** Spending too much time on production quality delays feedback loops; prioritize volume and iterationCLAIM(NKX6cdLIH80@4m).
*   **Ignoring data types:** Sending strings where numbers are expected (or vice versa) causes API rejections; verify types in the pickerCLAIM(JdKC8TOPfJE@25m).

## Changed views

*   **Platform Preference:** Initially focused on Make.com for its visual ease, he later adopted n8n for self-hosting capabilities and lower costs at scale, acknowledging n8n's steeper learning curve but greater flexibilityCLAIM(JNI1kdkxaLo@4m)CLAIM(PjKHs-L6Sn4@11m).
*   **AI Agents:** Moved from simple linear workflows to agentic workflows where the LLM decides tool usage, but cautioned that agents should be constrained and small rather than complex nested waterfallsCLAIM(c2kaOwkkhpo@0m)CLAIM(2GZ2SNXWK-c@145m).
*   **RAG vs. Long Context:** Previously advocated for RAG (Retrieval-Augmented Generation) for knowledge bases, but now notes that long-context models often make RAG unnecessary for smaller corporaCLAIM(LqVo5dasBh0@7m)CLAIM(LqVo5dasBh0@34m).
*   **Sales Strategy:** Shifted from selling technical workflow setups to selling guaranteed business outcomes and revenue results to command higher pricingCLAIM(Td8ymV1Cc_8@1m)CLAIM(Al5I8tPlgU0@15m).
*   **Content Production:** Changed from heavily edited videos to single-take, low-friction recordings to maintain consistency and reduce production overheadCLAIM(XIBEPpN0VV8@29m)CLAIM(NKX6cdLIH80@12m).

