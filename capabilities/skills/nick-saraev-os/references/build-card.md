# Recall Chat build card: nick-saraev-os

Generated in Recall Chat (Claude Opus 5.5, source = Recall only) over cards NS-00 to NS-06, saved as Recall card 3e0eb98f. Some currency amounts were mangled by the chat page's math rendering; the skills restate them in words.

# Recall Chat answer (chat https://app.recall.it/chat/8df0759c-f6e7-4c8d-b929-b0869a375911)

ought
for 1m 34s
Build Card: nick-saraev-os (v0.1, stages NS-01 to NS-03)

What this card authors: an operator can turn Nick's 255 hours of video into governed, checkable procedures. Nobody has to rewatch the videos. Every rule carries a citation, and every skill has a test it can fail. This draft uses only the four attached cards 
.

Data problems to fix before install. The NS-03 lead-gen card has corrupted spots:

A broken DMs-vs-email rule. Its second tag is 5E580yoD4eo@@9m (two @ signs), and the line then loops for a long stretch 
. The distiller broke here; this rule needs to be regenerated.
Tags with no minute: CLAIM(AKNKI9uXjdQ), CLAIM(v9f87-aHbzE) and CLAIM(oAWeFwHlo) 
. The last one looks like a damaged copy of oAWe5wFwHlo.
A malformed tag: CLAIm(ZaEvUAkI).
Changed-views entries with no tags at all 
.
Mixed tag casing. Procedure steps use Claim( instead of CLAIM(.

The agentic card has CLAIM(nsFliqg8Dro@13), which is missing its "m" 
. None of these broken tags are used as support for any law below.

Meta-skill: nick-saraev-os (routes only)

Purpose: pick the right stage skill and pass the request along. It never does the work itself 
.

Trigger phrases: "how would Nick build this", "Saraev method", "agency playbook", "Nick Saraev".

Routing rules (first match wins):

Agent, Claude Code, Codex, directive, SOP-to-agent, sub-agents → ns-agentic-workflows
n8n, Make, scenario, webhook, HTTP module, JSON mapping → ns-automation-builds
Leads, scraping, enrichment, cold email, icebreaker → ns-lead-gen-outbound
Offer, price, sales call, scaling, career or content → the NS-04 to NS-06 skills. These aren't built yet, so the router should say so and stop rather than guess.

Tie-break when a request could be either a canvas scenario or an agent: use the agentic card's rule. Repeatable, deterministic work goes into scripts or canvas flows; judgment and routing go to the LLM 
.

Done-test (can fail): run a labeled routing set of about 30 requests. The skill fails if accuracy is below a threshold Mike sets, or if the meta-skill calls any execution tool even once.

Skill 1: ns-agentic-workflows 

Purpose: turn a business SOP into an agent built in three layers (directive, orchestration, execution) that a separate checker can verify.

Trigger phrases: "build an agent for", "turn this SOP into an agent", "directive", "agents.md", "sub-agents", "routine on a schedule".

Laws
Keep the three layers separate. Goals live in plain-language directives. The LLM only routes. Deterministic scripts do the actions. CLAIM(bA-WmidVSGo@15m), CLAIM(MxyRjL7NG18@62m), CLAIM(Uj-1we7Rew4@1m), CLAIM(hwTz4s_IqgE@2m), CLAIM(c7DKk9xHaaU@0m)
Code handles anything repeatable or logical. Sorting, math and API calls go in code. The model is reserved for judgment and synthesis. CLAIM(bA-WmidVSGo@19m), CLAIM(MxyRjL7NG18@66m), CLAIM(sduaTkhIm_w@35m), CLAIM(QufcrM79snw@9m)
Break work into small units, each checked on its own. This stops context contamination and regressions. CLAIM(oCuttuCQmZg@3m), CLAIM(UPtmKh1vMN8@28m), CLAIM(45K3zHckCnQ@8m)
Unattended runs need stricter SOPs than chat sessions. With no operator steering, errors compound. CLAIM(j3aXJNu9804@1m), CLAIM(Uj-1we7Rew4@29m), CLAIM(Ob5Vu-gD3mo@9m)
Nothing is accepted without verification. Use tests, compilers or screenshot checks, and score on binary criteria rather than impressions. CLAIM(oCuttuCQmZg@15m), CLAIM(UPtmKh1vMN8@45m), CLAIM(QoQBzR1NIqI@39m), CLAIM(lNum1UFDYn0@12m), CLAIM(qKU-e0x2EmE@3m), CLAIM(qKU-e0x2EmE@7m)
Keep state in files and prune context. Pasting raw history into the prompt lowers quality and raises cost. CLAIM(oCuttuCQmZg@8m), CLAIM(EsTrWCV0Ph4@103m), CLAIM(aif87UYCxOo@10m), CLAIM(LP7bfT4vOlo@1m), CLAIM(yulWjh3rq28@40m)
Run each worker in an isolated, short-lived container. This gives every run the same starting point and limits who can see credentials. CLAIM(j3aXJNu9804@5m), CLAIM(NF10evwkefM@7m), CLAIM(Ob5Vu-gD3mo@7m), CLAIM(oCuttuCQmZg@33m)
Anything outward-facing waits for a human. Publishing or sending needs approval; internal steps can run on their own. CLAIM(8rVQuZlRaqo@4m), CLAIM(rvkjS3YoVio@4m)
Procedure: Three-Layer Workflow Setup 
Create a directives/ folder for goals and an executions/ folder for scripts. CLAIM(bA-WmidVSGo@53m), CLAIM(MxyRjL7NG18@96m), CLAIM(c7DKk9xHaaU@8m)
Write agents.md with the layer rules and how the agent should correct itself. CLAIM(bA-WmidVSGo@47m), CLAIM(MxyRjL7NG18@76m), CLAIM(c7DKk9xHaaU@8m)
Write the business logic as bullet points in the directives. CLAIM(MxyRjL7NG18@12m), CLAIM(Uj-1we7Rew4@29m)
Have the agent generate a deterministic script for each action. CLAIM(bA-WmidVSGo@55m), CLAIM(MxyRjL7NG18@96m)
Have directives call scripts by name. CLAIM(MxyRjL7NG18@97m)
RIG addition: test the routine with synthetic payloads before turning on any live schedule. CLAIM(j3aXJNu9804@12m)
Sub-skills (changed from the plan)
ns-directive-writer (kept, now larger): turns an SOP into a directive with no ambiguity. It also takes over the file-based context layout from the old context-evals sub-skill.
ns-execution-scripts (kept): one deterministic script per tool action. GUI automation becomes a branch inside this sub-skill, used only when no API exists. CLAIM(2u93VTYvG5U@0m)
ns-agent-evals-verifier (renamed from ns-agent-context-evals): binary pass/fail evals, run by a verifier that holds sole authority to declare done. It also enforces the output schema. CLAIM(NF10evwkefM@12m), CLAIM(Xkrfm1VfETA@1m)
ns-agent-security (kept): reviews secrets, open ports, tool permissions and sandbox boundaries.

The split matters for your generator/evaluator/verifier separation. The original plan put context layout (a builder's job) and evals (a checker's job) in one sub-skill, which mixes the two roles.

Done-test (can fail)

Feed in a sealed SOP. The build fails if any of these is true:

The orchestration layer makes even one direct API call that isn't through a script in executions/.
Any eval is phrased as a judgment instead of a yes/no check.
The independent verifier's pass rate on held-out cases is below a threshold you set.
Any outward action has no approval gate.
A secrets scan of the repo finds anything.
What does NOT fit RIG
Self-healing as written. The agent reads its own errors and rewrites its own directives. CLAIM(bA-WmidVSGo@43m), CLAIM(Uj-1we7Rew4@23m), CLAIM(c7DKk9xHaaU@15m), CLAIM(sduaTkhIm_w@20m) That breaks "no agent reviews its own output." Keep the idea, but change the route: the agent proposes a patch, an evaluator scores it, and the verifier merges it.
The skill-creation loop where the agent writes a skill, runs it once and patches it 
. It has the same self-review problem. It's fine for drafting at your L1 level; it doesn't qualify for L4 promotion.
Rendering long prompts as images to save tokens. CLAIM(dzfFN0RgPlI@0m) This is single-source, can't be audited, and doesn't belong in a signed harness.
Screen-coordinate GUI automation as a default 
. It's single-source and fragile. Use it only as a last resort.
Skill 2: ns-automation-builds 
NS-02-automation-bui…

Purpose: build n8n or Make flows that keep working when an API fails, a payload is malformed, or volume grows.

Trigger phrases: "n8n workflow", "Make scenario", "webhook", "HTTP module", "map this JSON", "automation keeps breaking".

Laws
Split flows over 15 to 20 modules into child scenarios connected by webhooks. Large flows are hard to debug and time out. CLAIM(QqE6tsHpr3U@0m) CLAIM(QqE6tsHpr3U@5m) CLAIM(QqE6tsHpr3U@11m)
Every third-party call gets an error handler, and incomplete runs are stored so they can be retried by hand. CLAIM(TtvSHo003UI@2m) CLAIM(TtvSHo003UI@3m) CLAIM(5w6Bf5pponE@69m)
Trigger with webhooks, not polling. Polling burns operations and adds delay. CLAIM(lK3veuZAg0c@0m) CLAIM(lK3veuZAg0c@15m) CLAIM(sGyj2HYZIEQ@3m) CLAIM(Qbi41HouOiI@16m)
Assume every input and output is an array, even when it holds one item. CLAIM(6b442bN0CyI@49m) CLAIM(2GZ2SNXWK-c@120m) CLAIM(Ksr_H30Oris@9m)
Check JSON syntax and data types strictly. Commas, escaping and string-versus-number mistakes cause most 400 errors. CLAIM(JdKC8TOPfJE@24m) CLAIM(6b442bN0CyI@46m) CLAIM(898WpSTxbFU@10m) CLAIM(JdKC8TOPfJE@25m)
Never paste credentials into the canvas. Blueprint exports leak them. CLAIM(JdKC8TOPfJE@16m)
Build from templates so a new client needs about 20% custom work. CLAIM(4gGWba-6nOk@12m) CLAIM(fIWUAodAgJw@12m)
Automate the back office, not high-value sales conversations, where human rapport decides the deal. CLAIM(oUpC98ueWn8@5m) CLAIM(oUpC98ueWn8@7m) CLAIM(oUpC98ueWn8@9m)
Procedure: Iterative Module Testing 
NS-02-automation-bui…
Add a watch trigger, then a sleep of about 3 seconds so the data persists. CLAIM(942qTUO2Nds@7m)
Add a list module limited to 1 record. CLAIM(942qTUO2Nds@7m)
Run that module alone and check its output. CLAIM(Qbi41HouOiI@1m)
Cache API outputs in variables so retests don't burn operations. CLAIM(942qTUO2Nds@14m)
Repeat for each module, fixing field references as soon as one fails. CLAIM(942qTUO2Nds@2m)
RIG addition: finish with an end-to-end run using a payload shaped like a real client's. The lead-gen card warns that testing modules only in isolation misses integration errors 
. That warning's tag has no minute, so it's noted here without a CLAIM tag.
Sub-skills (plan confirmed)
ns-api-http-integration: raw HTTP calls, auth, parsing, and mapping dropdowns to internal IDs rather than labels. CLAIM(vHJH3TShGks@25m)
ns-scenario-architecture: scenario splitting, webhooks between scenarios, error handlers, bulk endpoints, and one source of truth. CLAIM(898WpSTxbFU@2m) CLAIM(vHJH3TShGks@2m)
ns-data-transformation: regex for simple extraction, AI for messy text, reshaping arrays and JSON. CLAIM(sOSrsYmo0pM@22m) CLAIM(xs10RZU0Gp0@23m) CLAIM(o9AvKxLuCRU@5m)

One change: move "sell guaranteed outcomes" and "proposals as diagnostic audits" out of this skill and into ns-offer-and-sales. CLAIM(Al5I8tPlgU0@15m) CLAIM(jyFqnQqkS64@1m) They are sales laws that ended up in a build doctrine.

Done-test (can fail)

A scenario set fails if any of these is true:

Any scenario has more than 20 modules.
Any third-party call has no handler.
An exported blueprint contains a key.
Any trigger polls.
An injected 4xx or 5xx error doesn't land in the incomplete-executions store.
What does NOT fit RIG
Make-specific operation-count tuning as a main design goal. It belongs to a vendor's pricing model, not to a governed system.
The LinkedIn "parasite" content system, which scrapes other creators' top posts and copies their hook structures. CLAIM(roTg7kyw8X4@16m) CLAIM(roTg7kyw8X4@56m) Its output is exactly what any competitor could publish unnoticed.
Tool-level Vapi detail 
NS-02-automation-bui…
. It's useful as a recipe card but too tied to one vendor to be a law.
Skill 3: ns-lead-gen-outbound 

Purpose: build a list of verified contacts keyed by company domain, and draft personalized outreach that only sends after approval.

Trigger phrases: "scrape leads", "find emails", "enrich this list", "cold email campaign", "icebreakers".

Laws
The company domain is the unit everything else hangs on. Get domains first and drop leads without one before spending credits. CLAIM(2XHgJXX49Jk@3m) CLAIM(eElnA0mCzXw@8m)
Look up emails by name plus domain. This works about 70% of the time, versus 55 to 60% using company name alone. CLAIM(2XHgJXX49Jk@1m) CLAIM(AKNKI9uXjdQ@21m)
Remove duplicates before any paid lookup. Duplicates quietly burn credits and distort cost per lead. CLAIM(2XHgJXX49Jk@18m)
For enterprises, search one domain at a time. One credit returns about 40 emails. CLAIM(2XHgJXX49Jk@9m)
Scraping niche directories beats buying marketplace lists, because those leads haven't been flooded with outreach yet. CLAIM(2XHgJXX49Jk@29m)
Personalization depth comes from scraping many pages of a site, not one. The card links this to 5 to 10% reply rates. CLAIM(oAWe5wFwHlo@10m)
AI fills slots in a script a human wrote and tested; it doesn't write the message from scratch. CLAIM(5E580yoD4eo@6m) CLAIM(5E580yoD4eo@34m)
The guarantee matters more than the list or the tools. Frame it as pay-for-performance, not as a refund. CLAIM(IJBp8MAAMGQ@3m) CLAIM(v9f87-aHbzE@3m)
Procedure: AirScape to Anymail Finder Pipeline, with a dedupe gate added 
In AirScape, set location, company size and keyword, then preview. CLAIM(2XHgJXX49Jk@2m)
Load the results into a table. Expect names without domains. CLAIM(2XHgJXX49Jk@3m)
Resolve domains from the company-name field. CLAIM(2XHgJXX49Jk@3m)
Export only the selected rows to CSV. CLAIM(2XHgJXX49Jk@4m)
RIG addition: remove duplicate domains and drop rows with no domain. CLAIM(2XHgJXX49Jk@18m)
Run a bulk decision-maker search in Anymail Finder. CLAIM(2XHgJXX49Jk@4m)
Review the valid flag on each result. You're only charged for emails it finds. CLAIM(2XHgJXX49Jk@5m)
Sub-skills (plan confirmed, with one boundary change)
ns-lead-scraping: Apify, Maps and site scraping into a list keyed by domain. Direct HTTP requests plus parsing replace paid APIs where that's allowed. CLAIM(OroDNJl-pyc@2m)
ns-email-enrichment: names to verified emails, dedupe first, and the bulk-versus-single-domain choice. CLAIM(2XHgJXX49Jk@9m)
ns-cold-email-personalization: two LLM calls. The first pulls structured facts into JSON (Claim(yYVfcfa7n5A@18m)); the second writes against a style example (Claim(yYVfcfa7n5A@15m)) 
. This split already matches your generator separation.

Boundary change: move invoice recovery (CLAIM(h-pQz4E1p3o@12m)) to ns-automation-builds, and productization (CLAIM(itA4M364nd8@1m)) to ns-agency-scale. Neither is lead generation.

Done-test (can fail)

A batch fails if any of these is true:

Any row has no domain.
Any duplicate domain reached a paid call (check the credits log).
The verified-email rate is far below the ~70% benchmark without a logged reason.
Any icebreaker contains generic praise, or none of its details come from a page other than the homepage.
Anything sends without your approval. Sending is external, so it falls under your approval rule regardless of score.
What does NOT fit RIG
The deliverability tricks: all-lowercase subject lines, a fake "sent from my iPhone" signature, plain text made to look handwritten. CLAIM(v9f87-aHbzE@10m) These are signals designed to mislead the reader. They're also single-source.
Getting around Google Maps bot detection with proxies, and scraping LinkedIn with session cookies. CLAIM(OroDNJl-pyc@19m) CLAIM(2XHgJXX49Jk@6m) Both are terms-of-service risks a governed build can't take on.
Cheap-offer volume plays: about 1,000 emails a day, hyper-narrow micro-niches, and posing as a freelancer 
. These fit Nick's agency model; they don't fit an operating-system offer.
The plan's open questions (for these three stages)

1. Is 6 skills the right cut? Should outbound and offer/sales merge? Keep them separate, but clean up the boundaries. Sales laws show up in two cards outside NS-04:

In NS-03: risk reversal, freelancer framing, putting proof first, and niching down 
.
In NS-02: selling outcomes, and proposals as audits 
NS-02-automation-bui…
.

Merging the skills would make that mixing permanent. Instead, ns-offer-and-sales should produce a typed offer packet (guarantee, proof, niche) that ns-lead-gen-outbound takes as a required input. That gives you a hash-chained hand-off rather than two copies of the same laws. The NS-04 card isn't in this context, so I'd treat this as provisional.

2. Which laws conflict across time (Make, then n8n, then agentic)?

Platform: he started on Make, then moved to n8n for self-hosting and cost at scale. CLAIM(JNI1kdkxaLo@4m) CLAIM(PjKHs-L6Sn4@11m) The agentic card goes further: Python scripts called from directives replace the canvas for deterministic work 
. Treat this as a ladder: Make for simple linear flows, n8n for volume or custom code, scripts for anything an agent orchestrates.
Agents: NS-02 says to keep agents small and constrained rather than building nested chains. CLAIM(c2kaOwkkhpo@0m) CLAIM(2GZ2SNXWK-c@145m) NS-01 describes fleets of sub-agents with heartbeat monitoring. CLAIM(NF10evwkefM@10m) That fleet method is single-source, so the "small and constrained" stance should be the default.
RAG: NS-01 still recommends retrieval for context 
. NS-02 records a later view that long-context models often make RAG unnecessary for small corpora. CLAIM(LqVo5dasBh0@7m) CLAIM(LqVo5dasBh0@34m) Settle it with a size threshold you choose, not by preference.
Cold email: he moved from "it's saturated" to "it rewards whoever keeps going" 
. This change has no citation; leave it out until it's tagged.

3. Which parts fit RIG? See each skill's "does not fit" section. The pattern: data hygiene, layer separation, error handling and approval gates fit; growth tricks, ways around terms of service, and agents checking their own work don't.

Laws that contradict each other
Tension	Side A	Side B	Resolution
How long prompts should be	Keep core instructions short; accuracy falls past about 250 tokens. CLAIM(CxbHw93oWP0@2m)	Unattended routines need detailed runbooks with filters and output formats. CLAIM(j3aXJNu9804@10m)	A short core directive, with detail kept in files that load on demand
Who writes the message	AI only fills slots in a human script. CLAIM(5E580yoD4eo@6m)	The second LLM call generates a whole newsletter. Claim(yYVfcfa7n5A@15m)	The slot-filling law wins; the newsletter is a single-video variant
What happens on errors	Set HTTP nodes to continue on error. CLAIM(OroDNJl-pyc@15m)	Use break handlers and store incomplete runs. CLAIM(TtvSHo003UI@2m)	Continue-on-error only if failures go to a dead-letter log. Otherwise it's a hidden retry, which your rules ban.
How to test	Test each module alone first 
NS-02-automation-bui…
	Isolated tests miss integration errors 
	Both: module tests first, end-to-end as the final gate
How fast to answer replies	Reply within minutes. CLAIM(tev9BPwb3tM@0m)	Within 60 seconds, for up to +396% conversion. CLAIM(IJBp8MAAMGQ@2m)	Same direction, but the +396% figure is single-source. Don't treat it as an SLA until you've tested it.
Agent autonomy	Agents fix and patch themselves (law in NS-01)	Outward actions need a human (also NS-01)	Self-patching becomes a proposal the evaluator scores and the verifier approves

The pattern across all three cards is consistent. Nick's most reliable material (marked "consensus" in the cards) is about structure: layers, splitting, handlers, domains, dedupe. Those carry over to RIG with almost no repair. The parts with only one source are mostly the growth tactics, and those are also the parts that don't fit. The reliable laws and the RIG-compatible laws are largely the same set, so the first install should promote only those and park the single-source tactics.

N
N
Sources
Add to card

Compare agentic workflow laws with lead-gen laws

Search for the missing NS-04 to NS-06 stage cards

Fix corrupted tags in the NS-03 lead-gen card

﻿

Ask anything... type @ to add context
Context
Upload
Recall
Claude Opus 5.5

# Recall Chat answer (chat https://app.recall.it/chat/ca8a82e5-9da7-430d-afe5-1f2b0ca5e922)

ght
for 1m 28s
nick-saraev-os: build card, part 2

Scope: the stage skills for offers and sales (NS-04), agency scale (NS-05) and AI career and content (NS-06). Everything comes from the four attached cards. CLAIM tags are copied exactly, including the broken ones. I fix them only in the audit section.

One finding changes the cut. The three stage cards don't stay in their lanes. NS-04 includes outbound procedures. NS-05 includes cold-email setup, a sales call framework and a tool-choice rule. About half of NS-06 is build craft: Tailwind, curl import, JSON parsing and agent design. So each skill below keeps only the laws for its own stage, and I've marked what should move elsewhere 
+2
.

Skill 1: ns-offer-and-sales 

Purpose: Turn a qualified conversation into a priced, scoped first project that is built to become a retainer.

Trigger phrases: "price this," "write the proposal," "how do I structure the offer," "prep the sales call," "convert to retainer," "what niche," "they want a discount."

Entry condition: A conversation already exists. Finding leads belongs to ns-lead-gen-outbound.

Laws
Charge more the closer the work is to revenue. Buyers fund revenue-side systems more readily than savings-side ones. The card says front-end systems command about 350% more. CLAIM(T5-RXi-Zk_g@1-2m)
Pitch outcomes, not models or specs. Buyers pay to have a problem solved and to reduce risk. Talking about technology confuses non-technical buyers. CLAIM(Fw8NGGnEchs@0m), CLAIM(Y54kp53gi_M@2m), CLAIM(LQMAnCIIPgM@111-112m)
Sell relief for the single tightest constraint. Find the one bottleneck (usually lead gen), sell the fix for it, and price against it. CLAIM(Gz8tbgZTdpI@4m), CLAIM(OLwEtOEF36A@29m)
Price as a share of impact, not hours. Hourly billing penalizes you for being efficient. The fee should be a cut of the money saved or earned. CLAIM(owdN96DwdT4@7m), CLAIM(NsQWWnu7vzI@6m), CLAIM(Y54kp53gi_M@15m)
Make the first project fast, cheap to deliver and low-risk, with an obvious next step. Choose a first project that naturally creates the need for the next service. CLAIM(ArNmQRpctIc@3m), CLAIM(eLqveVYFWc4@10m), CLAIM(ArNmQRpctIc@22m), CLAIM(RmYTguzXrVM@9m)
Recurring revenue beats one-off revenue. A smaller monthly client out-earns a larger one-off within a year, and margins improve as the workflow gets familiar. CLAIM(T5-RXi-Zk_g@4m), CLAIM(RmYTguzXrVM@4m), CLAIM(kChb6HrYOeE@2-3m)
Sell rigid, deterministic tasks, not all-in-one agents. Systems that try to run a whole operation aren't reliable enough to sell. CLAIM(whXs1RaQIDA@26m), CLAIM(cZuvJxmjdxU@12m)
Fix the success criteria up front and keep client input to one intake. This is the defense against scope creep. CLAIM(ArNmQRpctIc@9m), CLAIM(hRBL6ISvB3s@29)
Procedure: Call-to-Retainer Path 
+1
Build rapport briefly, then ask why the prospect replied to your outreach. [CLAIM(rQcXmY6rSVY@67)] [CLAIM(PRxtWdI3xvA@16)]
Have them walk through their customer journey or pain points to find the bottleneck. [CLAIM(PRxtWdI3xvA@17)] [CLAIM(QTWBgFLuNvY@5)]
Put a number on the cost of doing nothing: direct savings plus lost opportunity. [CLAIM(rQcXmY6rSVY@67)] [CLAIM(ite9u07MhsM@7)]
Present the fix as recovering that amount. [CLAIM(L4Qbx8OM9l4@93)] [CLAIM(QTWBgFLuNvY@5)]
Say on the call that you intend a long-term partnership. CLAIM(RmYTguzXrVM@7m)
Send the proposal quickly after the call. The cards disagree on 30 vs 60 minutes; see the conflicts section.
During delivery, send a proactive update every 1–2 days. CLAIM(RmYTguzXrVM@11m)
Sub-skills (confirmed, with one change)
ns-niche-and-offer: choose the niche and design the first project plus its upsell path.
ns-value-pricing: turn a quantified impact into a fee. This is the only owner of pricing. NS-05 and NS-06 both list a pricing sub-skill; delete those and reference this one.
ns-sales-call-and-proposal: run the discovery call, quantify the pain and send a fast proposal.
ns-retainer-conversion: move from one-off to recurring revenue. Change: fold client onboarding in here, because NS-04 treats onboarding as a sales tool that reduces churn. CLAIM(hRBL6ISvB3s@3)
Done-test (an independent Verifier decides)

Fail if any of these is true:

The proposal has no cost-of-inaction number.
The fee can't be traced to that number by a stated percentage band.
The proposal doesn't name the follow-up service the first project leads to.
The success criteria aren't written down.
The deal is marked closed before the money arrives. Taken from NS-05: CLAIM(36xOZ1e6tuM@0m) CLAIM(m4yA2A-gPwk@31m) CLAIM(PRxtWdI3xvA@21m)

Sending a price or proposal is an external action, so it stays at A3 and needs your approval.

What doesn't fit RIG
Lead-count guarantees ("X leads in Y days," said to lift conversion about 300%) are built for selling volume 
. For fractional CAIO work, guarantee a proof obligation instead: a passing eval, a governance packet, or a named metric moving.
The low-price ramp: start low and raise 30% per client, with a roughly $1,500 entry offer 
. This is a price-discovery play for commodity work. A CAIO engagement should start at a value-priced diagnostic.
Digital-first niches that avoid healthcare and finance 
+1
. This flips for RIG. Compliance friction is a cost for Nick's model, but it's where governed builds are worth paying for.
Zero-capital outreach (15 Loom videos a day, Apify/Apollo scraping) and the coaches-chatbot vs SaaS lead-gen rule 
. These belong in the outbound skill, and both are volume plays.
The pricing ladder that includes hourly as a step 
. It conflicts with law 4; drop the hourly rung.
Skill 2: ns-agency-scale 
+1

Purpose: Find the one constraint limiting throughput, widen it, measure again, and productize whatever repeats.

Trigger phrases: "we're stuck," "where's the bottleneck," "should I hire," "productize this," "delivery is taking too long," "next stage of growth."

Laws
The slowest stage sets total output, no matter how fast the other stages are. CLAIM(8HQb8aji_xs@4m) CLAIM(wamAXd1V5C8@4m) CLAIM(miM6LCX08VQ@1m) CLAIM(XhRJiAG4s5U@0m)
The bottleneck moves with revenue: lead gen under 
10
𝑘
𝑎
𝑚
𝑜
𝑛
𝑡
ℎ
,
𝑓
𝑢
𝑙
𝑓
𝑖
𝑙
𝑙
𝑚
𝑒
𝑛
𝑡
𝑓
𝑟
𝑜
𝑚
10kamonth,fulfillmentfrom10k to 
25
𝑘
,
ℎ
𝑖
𝑟
𝑖
𝑛
𝑔
𝑎
𝑏
𝑜
𝑣
𝑒
25k,hiringabove25k. CLAIM(8HQb8aji_xs@11m) CLAIM(T11bzHVsdMQ@5m)
Gains at the bottleneck flow straight to output. A 10% gain there lifts revenue about 10%. Gains anywhere else are wasted. CLAIM(8HQb8aji_xs@20m) CLAIM(8HQb8aji_xs@11m)
Choosing the right task matters more than doing tasks fast. Fast work off the bottleneck produces no growth. CLAIM(8HQb8aji_xs@21m) CLAIM(cWYnMhu3AFg@2m) CLAIM(4WpmacKbTK0@3m) CLAIM(gjW084ll5T8@4m) CLAIM(vanIpwGcFT4@2m)
Fixing one bottleneck exposes the next, so the work is a loop, not a one-time project. CLAIM(8HQb8aji_xs@8m) CLAIM(wamAXd1V5C8@9m) CLAIM(miM6LCX08VQ@10m)
Start custom, then productize. Custom projects pay down skill gaps and prove demand. Templates come after. CLAIM(g1iiirHCEbM@17m) CLAIM(L4Qbx8OM9l4@51m) CLAIM(52yOx4nAGM8@19m) CLAIM(2i2tPQKcQ4Y@33m) CLAIM(eex1XkQwoMc@0m)
Run AI as a normal B2B service business. Lead gen, sales and retention matter more than how clever the build is. CLAIM(L4Qbx8OM9l4@4m) CLAIM(52yOx4nAGM8@0m) CLAIM(2i2tPQKcQ4Y@2m) CLAIM(r0c7RhMFcww@2m) CLAIM(On_DVAjnkRY@0m)
Don't add headcount before fixing operations, and hire on paid work tests, not résumés. These two laws are filed in NS-04 but belong here. CLAIM(zAMoAWA_BOE@0m), CLAIM(YLg8HTafhlk@3m), CLAIM(zAMoAWA_BOE@3m), CLAIM(gGo7M4cvPxQ@8m)
Procedure: Bottleneck Cycle, then Crystallize 
Map the whole pipeline from lead intake to completion. [CLAIM(8HQb8aji_xs@1m)] [CLAIM(wamAXd1V5C8@2m)]
Name the stage with the lowest throughput. [CLAIM(wamAXd1V5C8@4m)] [CLAIM(miM6LCX08VQ@7m)]
Pick the type of fix. If the stage works but is slow, widen its inputs. If it's failing, do R&D. Otherwise make a structural change (hiring or SOPs). [CLAIM(8HQb8aji_xs@14m)] [CLAIM(wamAXd1V5C8@7m)]
Widen the bottleneck. [CLAIM(wamAXd1V5C8@8m)]
Measure again and name the new bottleneck. [CLAIM(8HQb8aji_xs@9m)] [CLAIM(wamAXd1V5C8@9m)]
Crystallize step: go through finished projects for repeated deliverables. [CLAIM(g1iiirHCEbM@17)] [CLAIM(m4yA2A-gPwk@16)] Turn them into templates; the card cites delivery dropping from about 40 hours to about 5. [CLAIM(g1iiirHCEbM@21)] [CLAIM(gjW084ll5T8@19)]
Sub-skills (with changes)
ns-bottleneck-diagnosis: measure each stage's throughput, name the single constraint, pick the fix type. Confirmed.
ns-productization: mine project logs for repeated blocks and turn them into templates and SOPs. Confirmed. In RIG terms this is the step where proven work becomes reusable procedure.
ns-hiring-and-delegation → rename to ns-delegation. The purpose becomes delegating the bottleneck to a new agent harness or a contractor, gated by a paid work test. For a solo operator, "hiring" means minting a new harness when a pattern has repeated three or more times.
Add or move: the Client Onboarding & Delivery procedure 
 goes to ns-retainer-conversion. Cold Email Infrastructure 
 and the "asynchronous-outreach" candidate 
 go to NS-03.
Done-test

Fail if any of these is true:

The pipeline map is missing a measured throughput number for any stage.
More than one bottleneck is named.
The fix targets a stage that isn't the bottleneck.
There's no before-and-after measurement of the bottleneck stage.
The new bottleneck isn't named.

For productization, it fails if a template is promoted without at least two finished projects behind it.

What doesn't fit RIG
**The revenue bands and the 
20
𝑘
ℎ
𝑖
𝑟
𝑖
𝑛
𝑔
𝑡
ℎ
𝑟
𝑒
𝑠
ℎ
𝑜
𝑙
𝑑
∗
∗
<
𝑠
𝑝
𝑎
𝑛
>
<
𝑠
𝑜
𝑢
𝑟
𝑐
𝑒
−
𝑔
𝑟
𝑜
𝑢
𝑝
𝑟
𝑒
𝑓
𝑠
=
"
7
,
9
"
/
>
<
/
𝑠
𝑝
𝑎
𝑛
>
𝑎
𝑠
𝑠
𝑢
𝑚
𝑒
𝑎
𝑛
𝑎
𝑔
𝑒
𝑛
𝑐
𝑦
𝑤
𝑖
𝑡
ℎ
𝑠
𝑡
𝑎
𝑓
𝑓
.
𝐼
𝑛
𝑎
𝑓
𝑟
𝑎
𝑐
𝑡
𝑖
𝑜
𝑛
𝑎
𝑙
𝐶
𝐴
𝐼
𝑂
𝑝
𝑟
𝑎
𝑐
𝑡
𝑖
𝑐
𝑒
,
𝑦
𝑜
𝑢
𝑟
𝑜
𝑤
𝑛
ℎ
𝑜
𝑢
𝑟
𝑠
𝑎
𝑟
𝑒
𝑡
ℎ
𝑒
𝑓
𝑢
𝑙
𝑓
𝑖
𝑙
𝑙
𝑚
𝑒
𝑛
𝑡
𝑙
𝑖
𝑚
𝑖
𝑡
𝑙
𝑜
𝑛
𝑔
𝑏
𝑒
𝑓
𝑜
𝑟
𝑒
20khiringthreshold∗∗<span><source−grouprefs="7,9"/></span>assumeanagencywithstaff.InafractionalCAIOpractice,yourownhoursarethefulfillmentlimitlongbefore25k. Expect fulfillment to be the bottleneck early, and treat delegating to agents as the fix.
Affiliate signups during onboarding 
: it's a conflict of interest when you're advising the client on which vendors to use. Drop it.
The Make vs n8n tool rule 
 belongs to NS-02 and has nothing to do with scaling.
Skill 3: ns-ai-career-and-content 

Purpose: Keep your value rooted in business judgment as AI absorbs execution, and run content as a governed engine for building authority.

Trigger phrases: "what should I learn," "is this model release worth testing," "write my LinkedIn post," "content pipeline," "should I post or do outreach," "repurpose this video."

Laws
Content builds a long-term brand. It doesn't bring cash soon. Early revenue comes from Upwork or cold email. CLAIM(FdJuDZ6OVOY@1m, FdJuDZ6OVOY@17m-19m, yR9enwhUkp8@2m-3m)
The edge has moved from knowing tools to business judgment, because agents can now research tools. This is a changed view. CLAIM(S3kdxriOESk@13m, npCSNPN3F1o@18m-19m)
If you can't name the business formula a system moves (profit, growth or value), don't build it. CLAIM(Ozp3k4qzmHo@13m)
Find leverage with a driver tree: set a goal as metric, amount and period, then work backward to its drivers. Single source. CLAIM(Ozp3k4qzmHo@2m-5m)
Skip minor model bumps; test new classes of capability. Chasing every release is a failure mode. CLAIM(x55Fj_syFcI@0m-1m), CLAIM(x55Fj_syFcI@3m)
Learn a task by hand before handing it to AI, or the underlying skill fades. CLAIM(iqfA2vfbKUY@3m)
Match the message to the buyer's awareness: do they know the problem, know the type of solution, or know you fit? Single source. CLAIM(nmal1JTOrWI@0m)
A human reviews before anything is published. Fully automatic publishing damages quality and the brand. CLAIM(jBF48jNWPJE@18m), CLAIM(XlYQa0GgfaU@32m), CLAIM(r3tAJ8Oj4J4@18m-19m)
Procedure: Governed Content Pipeline 
Pull source text (transcripts), using existing subtitles before paying for transcription. CLAIM(G3LuGcAeiOU@26m, DNfp1XKC15k@9m)
Run an LLM with a role prompt and require JSON output. CLAIM(G3LuGcAeiOU@9m, DNfp1XKC15k@20m)
Parse it with escaped newlines. CLAIM(jp_GEYNC7jo@19m, DNfp1XKC15k@51m)
Map the output to each platform, with a human review gate before publishing. CLAIM(jp_GEYNC7jo@41m, G3LuGcAeiOU@30m)
Write a "posted on" timestamp back to the record so nothing gets published twice. CLAIM(DNfp1XKC15k@82m)

This maps directly onto your LinkedIn Studio. Your own Build Cards are the source corpus.

Sub-skills (changed from one to two)
ns-content-engine: source to draft to review gate to publish to write-back, tagged by awareness stage. Confirmed.
Add ns-career-positioning: triage model releases, run the formula test, and check which skills you've mastered by hand before automating them.
Remove these NS-06 candidates: api-integration, prompt-engineering and workflow-architecture 
. They duplicate NS-01 and NS-02. Also move few-shot prompting 
 to NS-01, and the reliability-vs-agents laws 
 to NS-01.
Done-test

Fail if any of these is true:

Something is published without a logged human review.
A duplicate post happens.
A piece can't be traced to an awareness stage and a business formula.
A model release gets tested without first being logged as either a minor bump or a new class.
What doesn't fit RIG
Thumbnail rules (1280x720, cutouts, a single font) are for YouTube and come from one source 
.
Lighting and audio 
 is fine, but it's production hygiene, not a law.
Tailwind component builds and curl import 
 are build craft that ended up in this card.
"Sell to revenue impact" 
 repeats NS-04 law 1; delete the copy here.
Open questions from the plan 

1. Is 6 skills the right cut, or should outbound and offer/sales merge? Keep six, but make the boundaries strict. The cards show the problem isn't too many skills; it's procedures filed in the wrong place. NS-04 carries outbound procedures and NS-05 carries cold-email setup 
+1
. Draw the line at "a conversation exists": before it is outbound, after it is offer and sales. Also, the plan's sub-skill list adds up to 18 as I count it (4+3+3+4+3+1), not the stated 16 
. With my changes it's still 18 (+1 career-positioning, −1 pricing duplicate avoided). Either change the target or merge ns-email-enrichment into ns-lead-scraping.

2. Which laws conflict across time? Covered in the next section.

3. What fits RIG and what doesn't? Fits: bottleneck diagnosis, value pricing, outcomes-first selling, the preference for deterministic builds, productization, the human review gate and the formula test. Doesn't fit: the low-price ramp, lead-count guarantees, high-volume Loom outreach, avoiding regulated niches (this one flips) and affiliate onboarding. The common thread: Nick's playbook shrinks risk for buyers of cheap work. For RIG, the governance proof is what reduces the buyer's risk, so it should replace the guarantee.

Conflicts and changed views
#	Conflict	Side A	Side B	Resolution for the build
1	Value-pricing bands	10–25% of savings, 10–30% of revenue 
	50% of savings, 30% of revenue impact 
	Encode as a range of 10–50% of savings and 10–30% of revenue. Flag which videos are newer before choosing.
2	Proposal speed	Within 30 minutes 
	Within 60 minutes 
	Set a ceiling of 60 minutes and a target of 30.
3	Hourly billing	A ladder step from free to hourly to fixed to retainer 
	Hourly penalizes efficiency 
	Drop the hourly rung.
4	When to hire	Hiring becomes the bottleneck above $25k 
	Hire at about $20k a month (broken tag) 
	Go with the bottleneck test, not a revenue number.
5	Make → n8n	Switch at $5–15k a month for polish and AI features 
	Switched for curl import and lower API cost 
	Same move, different reasons. NS-02 owns it.
6	Agents	Don't sell all-in-one agents 
	Agents are a coming layer on top of deterministic flows 
; the business shifts to selling outcomes as agents gain autonomy 
	Current rule: deterministic builds plus a governed agent layer. This is RIG's thesis.
7	Content	Content was the best lead source	Content is a long-term asset; do outreach first 
	Use the newer view. It matches the 90% outreach rule 
.
8	Outreach method	Cold calling	Asynchronous Loom across several channels 
	NS-03 owns it.
CLAIM tag audit

Unusable (ID damaged and minute lost): all in NS-05 

claim(h PI YRP Xj Vo @ m) → probably hPIYRPXj_Vo, minute unknown
claim(l Zc El ZH no @ m) (twice) → lZcElZHO5no, minute unknown
claim(Na M ACq mmu E @ m) → NaM0ACqmmuE
claim(gj W ll T @ m) → gjW084ll5T8
claim(r Qc Xm Y r SVY @ m) → rQcXmY6rSVY
claim(e ex Xk Qwo Mc @ m) → eex1XkQwoMc

The "Lead Channel Priority" rule is contaminated 
. It has about 26 tags with spaces in them, stripped digits (wamAXdVVC should be wamAXd1V5C8; YfYv_TEJg should be YfYv0_TEJ3g) and duplicates. The distiller's own reasoning also leaked into the card ("Correction," "Wait," "Actually"). Rebuild this rule from source.

Placeholders and missing numbers 
: "under 
𝑘
/
𝑚
𝑜
"
ℎ
𝑎
𝑠
𝑛
𝑜
𝑛
𝑢
𝑚
𝑏
𝑒
𝑟
.
"
𝐼
𝑛
𝑐
𝑟
𝑒
𝑎
𝑠
𝑒
𝑏
𝑦
 
k/mo"hasnonumber."Increaseby X or %" is a template that was never filled in.

Laws with no CLAIM at all: Ignoring Bottlenecks, both NS-05 changed views (Platform Migration, Outreach Method), Business Model Evolution, and Role Focus 
.

Missing the m unit: examples include CLAIM(XhRJiAG4s5U@1), CLAIM(rQcXmY6rSVY@17), CLAIM(hRBL6ISvB3s@3), CLAIM(hRBL6ISvB3s@29), and most NS-05 procedure tags, which are also wrapped in [ ] 
+1
.

Format drift:

NS-04 writes ranges as @1-2m; NS-06 writes @10m-12m.
NS-06 puts several locators inside one CLAIM(a, b, c) instead of one tag per locator 
.
The parser should normalize all of these before checking that each locator resolves.

Labeling error: Revenue Proximity is tagged [consensus] but has only one citation 
. Downgrade it to single-source.

Typos (not tags): "Appify" should be Apify 
. The bold markup is broken in "Custom** Tailwind Configs" and "Make.com to** n8n" 
.

Before this ships: the NS-05 card's tags are the weakest in the set. Re-extract that card from its source videos (8HQb8aji_xs, wamAXd1V5C8, NaM0ACqmmuE, F0bUCu6pZlI and the others listed above) before any law that cites it is promoted to autonomous. Until then, those laws should stay at A3 or below.

N
N
Sources
Add to card

Compare pricing laws across NS-04 and NS-05

List all malformed CLAIM tags in these cards

Synthesize the retainer strategy from NS-04 and NS-06

﻿

Ask anything... type @ to add context
Context
Upload
Recall
Claude Opus 5.5

