# linkedin-viral: full routing table

Generated 2026-09-27 from a read-only inventory of every LinkedIn capability on this Mac: 174 entries (161 routable, 7 retired, 6 broken or empty). Machine-readable copy: `inventory.json` in this folder.

Rules: pick by the SKILL.md quick index first; use this table when nothing there fits. Load exactly ONE child per task step and at most one of its sub-skills. Retired rows are never routed. Broken rows are reported to Mike, never improvised. Paths are canonical; other install locations are in inventory.json.

Kinds: M meta-skill, S skill, s sub-skill, C command, L loop, A agent, H harness. Lanes: A personal brand, B RIG B2B, client Ideawake, job search, all.

## Routers and end-to-end systems (9)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| /alfred | C |  | all | `~/.hermes/commands/alfred.md` | Load the alfred Prime Agent skill and execute the requested task. |
| /hermes-linkedin | C |  | all | `~/.hermes/commands/hermes-linkedin.md` | Activate the Hermes LinkedIn JTBD pack. |
| /rig-linkedin-studio | C |  | B | `~/.hermes/commands/rig-linkedin-studio.md` | Plan, draft, score and route LinkedIn content for RIG with evidence and brand memory. |
| linkedin-growth-os | M |  | all | `~/.aside/u/0/skills/user/linkedin-growth-os/SKILL.md` | Meta router for Mike's LinkedIn growth: source->plan->draft->critique->publish->amplify->measure. Routes to child skills; never publishes. |
| linkedin-influencer-os | M |  | all | `~/.aside/u/0/skills/user/linkedin-influencer-os/SKILL.md` | Meta-skill router for the 1% influencer build: routes hook design, visuals, growth tactics and the daily execution loop to corpus-derived families. |
| linkedin-optimizer | M |  | all | `~/.aside/u/0/skills/user/linkedin-optimizer/SKILL.md` | Meta skill over 13 skills / 42 sub-skills + meta agent + mega harness. Whole LinkedIn funnel: profile, qualify, engage, convert, monetize. |
| rig-linkedin-virality | M |  | A | `~/.hermes/skills/rig-linkedin-virality/SKILL.md` | META-SKILL LinkedIn go-viral OS: orchestrates content (P1), distribution (P2), measurement (P3) into a daily unattended run targeting 10k impressions/post. |
| when-growing-social-accounts | M |  | all | `~/.aside/u/0/skills/user/when-growing-social-accounts/SKILL.md` | Routes drafting, scheduling, engaging and measuring on LinkedIn/Instagram/X to the correct lane skill (71 skills). |
| when-writing-content | M |  | all | `~/.aside/u/0/skills/user/when-writing-content/SKILL.md` | Routes articles, newsletters, copy, hooks and long-form deliverables to the right writing skill (69 skills). |

## Strategy, positioning, doctrine (10)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| content-matrix | S |  | all | `~/.aside/u/0/skills/user/content-matrix/SKILL.md` | Generate 32+ LinkedIn post ideas in one table by pairing content pillars with 8 proven formats (Justin Welsh content matrix). |
| content-pillar-architect | S |  | all | `~/.aside/u/0/skills/user/content-pillar-architect/SKILL.md` | Design a content pillar system: 3-5 load-bearing pillars with formats, cadence and proof sources per pillar. |
| linkedin-growth-engine | M |  | all | `~/.aside/u/0/skills/user/linkedin-growth-engine/SKILL.md` | Cross-account LinkedIn growth doctrine and multi-channel amplification framework; universal rules shared by account-specific child skills. |
| rig-linkedin-studio-engine-builder | S |  | all | `~/Developer/rig-skills/studios/rig-linkedin-studio-engine-builder/SKILL.md` | Build LinkedIn Studio A1A3A4 engines (commenting, engagement, DM and related engines). |
| rig-linkedin-taki | S |  | B | `~/.aside/u/0/skills/user/rig-linkedin-taki/SKILL.md` | Apply Taki Moore's content, Hot Button Map and Cash Campaign rules to Mike's LinkedIn activity for Rodgers Intelligence. |
| rig-top100-linkedin-content | S |  | all | `~/.aside/u/0/skills/user/rig-top100-linkedin-content/SKILL.md` | RIG Top 100 capability #21: LinkedIn Content Generation. Mike's LinkedIn is RIG's #1 growth channel. |
| algorithm-2026 | s | li-growth | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/li-growth/sub-skills/algorithm-2026.md` | algorithm-2026.md — what the corpus claims about the 2026 LinkedIn feed |
| format-mix | s | lg-plan | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-plan/sub/format-mix.md` | Format mix |
| li-growth | S | linkedin-influencer-os | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/li-growth/SKILL.md` | Growth, algorithm, cadence, engagement and measurement doctrine for RIG's LinkedIn lanes. USE WHEN planning a posting week, running the golden-hour loop, run... |
| tommy-clark-doctrine | S | linkedin-viral | all | `~/Developer/rig-capabilities/capabilities/skills/tommy-clark-doctrine/SKILL.md` | Tommy Clark's founder-led B2B LinkedIn doctrine from all 79 videos (2024-2026): positioning, content system, hooks, algorithm, outbound, rule ledger. |

## Hooks (7)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| content-headline-a-b-generator | S |  | all | `~/.aside/u/0/skills/user/content-headline-a-b-generator/SKILL.md` | Generate headline A/B variant pairs with explicit hypotheses, ready for structured testing. |
| content-hook-generator | S |  | all | `~/.aside/u/0/skills/user/content-hook-generator/SKILL.md` | Generate scroll-stopping hooks from a post's core claim across proven hook families, scored by pattern-interrupt strength. |
| hook-generator | S |  | all | `~/.hermes/skills/hook-generator/SKILL.md` | Generate 6 clickbait-style LinkedIn hook variations for any topic: 40-char opening + 40-char bold contrast line. |
| hook-families | s | li-hooks | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/li-hooks/sub-skills/hook-families.md` | Hook families — the corpus taxonomy |
| hook-lab | s | lg-draft | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-draft/sub/hook-lab.md` | Hook lab |
| hook-selection | s | li-hooks | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/li-hooks/sub-skills/hook-selection.md` | Hook selection — gates, tie-breakers, and the receipts rule |
| li-hooks | S | linkedin-influencer-os | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/li-hooks/SKILL.md` | Select and brief LinkedIn hooks from the corpus-derived hook taxonomy. USE WHEN picking a hook family for a post, generating hook variants for Eden, deciding... |

## Drafting (15)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| /rig-ae-linkedin-run | C |  | A | `~/.hermes/commands/rig-ae-linkedin-run.md` | Belief-shift LinkedIn post with friction valley + first comment (full LinkedIn Studio harness). |
| /rig-collider | C |  | A | `~/.hermes/commands/rig-collider.md` | Deterministic Python entrypoint for the Collision Engine article generator. |
| content-cta-optimizer | S |  | all | `~/.aside/u/0/skills/user/content-cta-optimizer/SKILL.md` | Rewrite calls-to-action to match reader intent stage, with friction analysis and variant generation. |
| content-newsletter-curator | S |  | all | `~/.aside/u/0/skills/user/content-newsletter-curator/SKILL.md` | Curate and structure newsletter issues from a source pile: selection, ordering, commentary and consistent sections. |
| content-thread-structurer | S |  | all | `~/.aside/u/0/skills/user/content-thread-structurer/SKILL.md` | Structure long-form ideas into platform-native threads with per-post payload, pacing and recap architecture. |
| post-formatter | S |  | all | `~/.hermes/skills/post-formatter/SKILL.md` | Turn a topic into a ready-to-publish LinkedIn post using PAS, AIDA, BAB, STAR or SLAY: 200-250 words, 20 lines, mobile-formatted. |
| post-writer | S |  | all | `~/.hermes/skills/post-writer/SKILL.md` | Write LinkedIn posts that match the user's voice system (about-me.md and voice.md); outputs the final post in a code block. |
| rig-collision-engine | S |  | A | `~/.aside/u/0/skills/user/rig-collision-engine/SKILL.md` | V10 LinkedIn Studio article generator: pop-culture x decades-deep veteran worldview skeleton, scored by BlendValue with no-commodity/no-preach floors. |
| rig-comms-drafting-loop | L |  | all | `~/Developer/rig-capabilities/capabilities/loops/rig-comms-drafting-loop.md` | Communications drafting loop for RIG written surfaces (draft -> gate -> revise), covering LinkedIn among the comms surfaces. |
| rig-daily-linkedin-post | S |  | B | `~/.aside/u/0/skills/user/rig-daily-linkedin-post/SKILL.md` | Run or plan Mike's daily LinkedIn post for Rodgers Intelligence Group (Lane B RIG B2B); drafts, scheduling, queue, reporting. |
| rig-linkedin-agency | S |  | all | `~/.hermes/skills/rig-linkedin-agency/SKILL.md` | RIG LinkedIn Agency - full content factory with 10 specialized subagents (posts, carousels, articles, strategy, scheduling). |
| rig-write-linkedin | S |  | all | `~/Developer/rig-capabilities/capabilities/skills/rig-write-linkedin/SKILL.md` | Communications OS v6 surface engine for LinkedIn: assembles the write packet (voice v2 + wounds + corpus + persona) and gate-scores the artifact. |
| body-craft | s | lg-draft | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-draft/sub/body-craft.md` | Body craft |
| lg-draft | S | linkedin-optimizer | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-draft/SKILL.md` | Draft one LinkedIn post for Mike Rodgers - classify the reader, run a hook lab, write for dwell and saves, choose a format. USE WHEN asked to write, rewrite,... |
| post-architecture | s | li-hooks | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/li-hooks/sub-skills/post-architecture.md` | Post architecture — body structures behind the hook |

## Visuals, carousels, video (10)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| gemini-carousel | S |  | all | `~/.hermes/skills/gemini-carousel/SKILL.md` | Generate a branded slide-by-slide LinkedIn carousel using Gemini: design brief, approval gate, then per-slide image prompts at 1080x1350. |
| graphic-designer | S |  | all | `~/.hermes/skills/graphic-designer/SKILL.md` | Create LinkedIn post graphics: chooses between an HTML/CSS structured graphic and an AI-generated infographic. |
| quote-post | S |  | all | `~/.hermes/skills/quote-post/SKILL.md` | Two-step LinkedIn quote-post workflow: generate a viral motivational quote, then a Gemini prompt that recreates a reference image with it baked in. |
| rig-linkedin-image-harness | S |  | B | `~/.hermes/skills/rig-linkedin-image-harness/SKILL.md` | Goal-harness driving Higgsfield for LinkedIn Lane-B authored portraits until a frame clears the SIGNATURE v1 HERO-MAX gate stack; then human-approved. |
| carousel-architecture | s | li-visuals | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/li-visuals/sub-skills/carousel-architecture.md` | carousel-architecture — the document/carousel system |
| carousel-html | s | lg-draft | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-draft/sub/carousel-html.md` | Carousel from HTML/CSS/JS |
| eden-brief-templates | s | li-visuals | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/li-visuals/sub-skills/eden-brief-templates.md` | eden-brief-templates — what Eden receives |
| image-system | s | li-visuals | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/li-visuals/sub-skills/image-system.md` | image-system — single images, graphics, GIFs, and the banner |
| li-visuals | S | linkedin-influencer-os | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/li-visuals/SKILL.md` | RIG LinkedIn visual strategy: choose the format, architect the carousel/image/video, and write the exact brief eden.so executes. USE WHEN a LinkedIn post nee... |
| video-shorts | s | li-visuals | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/li-visuals/sub-skills/video-shorts.md` | video-shorts — LinkedIn video and vertical shorts playbook |

## Voice and anti-slop (5)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| anti-slop | S |  | all | `~/.aside/u/0/skills/user/anti-slop/SKILL.md` | Turn AI-written copy into copy a human would ship: lint AI tells, rewrite, cleanse with a rival model, lint again (SlopMonster). |
| content-voice-fingerprint-extractor | S |  | all | `~/.aside/u/0/skills/user/content-voice-fingerprint-extractor/SKILL.md` | Extract a quantified voice fingerprint from writing samples: sentence rhythm, vocabulary signature, banned-word profile, hook style. |
| rig-communications-voice | S |  | all | `~/Developer/rig-capabilities/capabilities/skills/rig-communications-voice/SKILL.md` | Voice Fingerprint v2 for the Communications OS: locked fingerprint, 12-surface register map, drift detector and sample-extraction procedure. |
| rig-top100-brand-voice | S |  | all | `~/.aside/u/0/skills/user/rig-top100-brand-voice/SKILL.md` | RIG Top 100 capability #27: Brand Voice Consistency. RIG brand must be recognizable everywhere. |
| slopmonster | S |  | all | `~/.aside/u/0/skills/user/slopmonster/SKILL.md` | Turn AI-written copy into copy a human would ship: lint for AI tells, rewrite, cleanse with a rival model, lint again. |

## Scoring and gates (6)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| hB-04-linkedin-post-session | H |  | all | `~/Developer/rig-capabilities/capabilities/harnesses/hB-04-linkedin-post-session.yaml` | Canonical RIG harness for linkedin-post-session: JEV gate before drafting, pre-publish gate, quality floor 0.6. |
| post-scorer | S |  | all | `~/.hermes/skills/post-scorer/SKILL.md` | Score a LinkedIn post against real performance data pulled from the user's own post history via Apify, not generic advice. |
| rig-revenue-publish-gate | A |  | B | `~/Developer/rig-capabilities/capabilities/agents/rig-revenue-publish-gate.md` | Sub-agent running the pre-publish gate on one artifact: sourced claims, disclosure labels, professional review where YMYL, typed human approval. |
| lg-critique | S | linkedin-optimizer | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-critique/SKILL.md` | Independently score a LinkedIn draft out of 10 before it is shown to Mike or sent to Eden. USE WHEN asked to review, score, critique or 'is this good enough'... |
| li-post-gate | H | hB-04-linkedin-post-session | all | `~/Developer/rig-capabilities/capabilities/harnesses/linkedin-post-gates/li_post_gate.py` | Executable LinkedIn pre-publish gate (li_post_gate.py) with --selftest, CITATIONS.md and postflight checks. |
| scorecard | s | lg-critique | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-critique/sub/scorecard.md` | Scorecard |

## Planning, scheduling, publishing (8)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| alfred-content-planning-cron | S |  | A | `~/.aside/u/0/skills/user/alfred-content-planning-cron/SKILL.md` | Use when planning cron fires. Builds tomorrow.json for the Alfred content pipeline. |
| eden-mcp | S |  | all | `~/.aside/u/0/skills/user/eden-mcp/SKILL.md` | Drive the Eden Canvas MCP server (boards, notes, social intelligence and the post scheduler) correctly from any MCP client. |
| linkedin-weekly-rhythm | S |  | A | `~/.aside/u/0/skills/user/linkedin-weekly-rhythm/SKILL.md` | Mike's themed daily LinkedIn post system (Mon Ted Lasso ... Sat Be More Birch) for Lane A personal brand; Eden brief + image render. |
| rig-revenue-publish-ramp | S |  | B | `~/Developer/rig-capabilities/capabilities/skills/rig-revenue-publish-ramp/SKILL.md` | Set and hold the publishing ramp: 1 to 5 to 10 items per week over time, never a velocity spike, drafts-first human approval. |
| rig-top100-content-calendar | S |  | all | `~/.aside/u/0/skills/user/rig-top100-content-calendar/SKILL.md` | RIG Top 100 capability #22: Content Calendar & Scheduling. Consistency compounds. |
| cadence-ritual | s | li-growth | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/li-growth/sub-skills/cadence-ritual.md` | cadence-ritual.md — the daily/weekly operating rhythm |
| lg-plan | S | linkedin-optimizer | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-plan/SKILL.md` | Plan Mike Rodgers' LinkedIn week - slots, formats, targets and what to cut. USE WHEN asked to plan, schedule or fill a content week, when asked how to hit an... |
| lg-publish | S | linkedin-optimizer | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-publish/SKILL.md` | Move an approved LinkedIn draft into Eden and hand it to Mike to publish. USE WHEN a draft has passed lg-critique, when asked to schedule or queue a LinkedIn... |

## Post-launch and golden hour (4)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| linkedin-post-launch | S |  | all | `~/.aside/u/0/skills/user/linkedin-post-launch/SKILL.md` | Run the LinkedIn post launch and engagement playbook: boost a new post, reply to comments, drive traffic, daily engagement sweep. |
| golden-hour | s | lg-amplify | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-amplify/sub/golden-hour.md` | Golden hour, 60-90 minutes |
| lg-amplify | S | linkedin-optimizer | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-amplify/SKILL.md` | Amplify a published LinkedIn post legitimately - golden hour replies, a reference comment, borrowed attention on other people's threads, company-page presenc... |
| save-asset | s | lg-amplify | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-amplify/sub/save-asset.md` | The reference comment |

## Comments and engagement (6)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| /comment-engine | C |  | B | `~/.hermes/commands/comment-engine.md` | Run / resume / audit RIG's 85%-deterministic LinkedIn commenting engine (PREP != FIRE, human-approved). |
| alfred-comment-engagement | S |  | A | `~/.hermes/skills/alfred-comment-engagement/SKILL.md` | Monitor LinkedIn comments on Mike's recent posts and reply with value-add responses under a <2 hour SLA (inbound engagement lane). |
| pinned-comment | S |  | client | `~/.hermes/skills/pinned-comment/SKILL.md` | Write LinkedIn pinned comments AND image-generation prompts in Charlie Hills' signature style; image prompt first, then the 4-line comment. |
| rig-linkedin-desktop | A |  | B | `~/Developer/rig-capabilities/capabilities/agents/rig-linkedin-desktop.md` | Dedicated Hermes operator for Mike and RIG: grow relevant followers, evidence-backed AI credibility, high-ICP relationships, comment suggestions. |
| borrowed-attention | s | lg-amplify | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-amplify/sub/borrowed-attention.md` | Borrowed attention |
| engagement-comment-led | s | li-growth | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/li-growth/sub-skills/engagement-comment-led.md` | engagement-comment-led.md — comment-led growth under lane caps |

## DMs and outreach (23)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| /linkedin-outreach | C |  | all | `~/.hermes/commands/linkedin-outreach.md` | LinkedIn follower outreach overview/manual command for the luca-studio outreach engine. |
| /outreach-arm | C |  | all | `~/.hermes/commands/outreach-arm.md` | GATE-D ARM the live LinkedIn DM send (CDP transport) - the only path that turns the engine LIVE. |
| /outreach-daily | C |  | all | `~/.hermes/commands/outreach-daily.md` | RIG LinkedIn outreach DAILY DRY-RUN; manual sister of the 7am rig-linkedin-outreach-daily routine. |
| /outreach-replies | C |  | all | `~/.hermes/commands/outreach-replies.md` | Reply loop: detect LinkedIn prospect replies, forward to Mike, pause nudges. Never auto-answers. |
| /outreach-send | C |  | all | `~/.hermes/commands/outreach-send.md` | GATE-D LIVE path: sends real LinkedIn DMs on Mike's account; refuses to run without approval. |
| cold-outreach-sequence | S |  | all | `~/.hermes/skills/cold-outreach-sequence/SKILL.md` | Build multi-touch cold outreach sequences - research-driven personalization, 4-6 step cadences, reply-focused copy for email and LinkedIn. |
| darius-linkedin-outreach-agent | S |  | all | `~/.hermes/skills/darius-linkedin-outreach-agent/SKILL.md` | Darius GTM sub-agent for LinkedIn DM campaigns - conference outreach, cold DMs, follow-up sequences (Dykema 2026, 20/20 sent). |
| dykema-dm-campaign-learnings | S |  | all | `~/.hermes/skills/dykema-dm-campaign-learnings/SKILL.md` | Battle-tested learnings from the Dykema 2026 DSO Conference LinkedIn DM campaign - 20/20 sent, 27 errors overcome. |
| gtm-outreach-sequence-architect | S |  | all | `~/.aside/u/0/skills/user/gtm-outreach-sequence-architect/SKILL.md` | Design multi-touch outreach sequences with spacing, escalation logic and exit conditions per segment (email + LinkedIn). |
| linkedin-dm-batch-sender | S |  | all | `~/.hermes/skills/linkedin-dm-batch-sender/SKILL.md` | Reusable LinkedIn DM batch sender - sends pre-approved DMs to a target list via patchright (battle-tested Dykema 2026, 20/20 sent). |
| linkedin-followup-sequence | S |  | all | `~/.hermes/skills/linkedin-followup-sequence/SKILL.md` | Automated LinkedIn follow-up sequences - Day 0 initial DM, Day 3 follow-up, Day 7 final nudge, auto-pauses on reply. |
| abcd-method | s | lg-convert | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-convert/sub/abcd-method.md` | The ABCD close |
| comment-to-dm | s | lg-amplify | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-amplify/sub/comment-to-dm.md` | Comment to DM — the bridge between engage and convert |
| dm-copy-craft | s | lg-convert | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-convert/sub/dm-copy-craft.md` | DM copy craft — the line-level rules |
| dm-sequences | s | lg-convert | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-convert/sub/dm-sequences.md` | DM sequences, spacing and ceilings |
| followup-cadence | s | lg-convert | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-convert/sub/followup-cadence.md` | Follow-up cadence — math, value-add, breakup, model split |
| inbox-triage | s | lg-convert | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-convert/sub/inbox-triage.md` | Inbox triage |
| lg-convert | S | linkedin-optimizer | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-convert/SKILL.md` | Run the LinkedIn DM conversion sequence end to end - draft, gate, route, and follow up. Covers sourcing (via lg-qualify), opener copy craft, sequence shape, ... |
| no-reply-ladder | s | lg-convert | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-convert/sub/no-reply-ladder.md` | The no-reply ladder |
| opener-recipes | s | lg-convert | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-convert/sub/opener-recipes.md` | Opener recipes — pick a model, then a recipe |
| pre-call-nurture | s | lg-convert | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-convert/sub/pre-call-nurture.md` | Pre-call nurture — the "manifest" stage |
| reply-handling | s | lg-convert | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-convert/sub/reply-handling.md` | Reply handling — beyond the letter |
| voice-video-dms | s | lg-convert | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-convert/sub/voice-video-dms.md` | Voice notes and permission-gated videos |

## Lead qualification and monetization (15)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| timyakubson-linkedin-sales-navigator | S |  | all | `~/.pi/skills/timyakubson-linkedin-sales-navigator/SKILL.md` | Extract leads from LinkedIn Sales Navigator into Clay or another tool (unofficial-but-allowed workflow). |
| call-prep | s | lg-monetize | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-monetize/sub/call-prep.md` | Pre-call briefing |
| contract-terms | s | lg-monetize | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-monetize/sub/contract-terms.md` | Contract and billing terms as revenue instruments |
| hot-signals | s | lg-qualify | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-qualify/sub/hot-signals.md` | Hot signals — the timing half of fit |
| icp-fit-card | s | lg-qualify | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-qualify/sub/icp-fit-card.md` | ICP fit card |
| intent-tracking | s | lg-qualify | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-qualify/sub/intent-tracking.md` | Intent tracking — the recurring watch |
| lg-client-engine | S | linkedin-optimizer | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-client-engine/SKILL.md` | Run the client-getting loop on LinkedIn end to end - draft and write posts that pull, source and qualify prospects, draft DMs and follow up until they reply ... |
| lg-monetize | S | linkedin-optimizer | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-monetize/SKILL.md` | Convert attention into revenue - offer construction, quiz and assessment lead magnets, pre-call briefing, and the contract terms that are revenue instruments... |
| lg-qualify | S | linkedin-optimizer | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-qualify/SKILL.md` | Qualify a LinkedIn prospect before anyone messages them - ICP fit card, hot-intent signals, sourcing channels (existing 1st-degree network, content-driven in... |
| offer-construction | s | lg-monetize | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-monetize/sub/offer-construction.md` | Offer construction |
| owned-audience | s | lg-monetize | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-monetize/sub/owned-audience.md` | Owned audience — the "own" in rent, borrow, own |
| quiz-funnel | s | lg-monetize | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-monetize/sub/quiz-funnel.md` | Quiz / assessment funnels |
| relevance-bridge | s | lg-qualify | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-qualify/sub/relevance-bridge.md` | Relevance bridge — what the message is anchored to |
| sourcing-channels | s | lg-qualify | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-qualify/sub/sourcing-channels.md` | Sourcing channels — where the prospects come from |
| sourcing-without-salesnav | s | lg-qualify | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-qualify/sub/sourcing-without-salesnav.md` | Sourcing without Sales Navigator |

## Profile (7)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| profile-optimizer | S |  | all | `~/.hermes/skills/profile-optimizer/SKILL.md` | Rebuild a LinkedIn profile for conversions: headline options, about, experience, featured strategy + 4 image generation prompts. |
| about-and-featured | s | lg-profile | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-profile/sub/about-and-featured.md` | About, featured, banner, button, toggles |
| classifier-sync | s | lg-profile | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-profile/sub/classifier-sync.md` | Classifier sync — the machine's half of the profile |
| company-page | s | lg-profile | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-profile/sub/company-page.md` | Company page from zero |
| headline-formulas | s | lg-profile | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-profile/sub/headline-formulas.md` | Headline formulas |
| lg-profile | S | linkedin-optimizer | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-profile/SKILL.md` | Audit and rebuild a LinkedIn profile as a conversion asset and a classifier input - headline, about, featured, banner, custom button, settings toggles, compa... |
| profile-audit | s | lg-draft | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-draft/sub/profile-audit.md` | Profile audit — profile as landing page |

## Measurement (9)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| /linkedin-operate | L |  | all | `~/.hermes/commands/linkedin-operate.md` | Run one verified daily cycle of the live LinkedIn OS (Loop ID GL-LO-01): score goals, verify floors, seal packet. |
| /outreach-status | C |  | all | `~/.hermes/commands/outreach-status.md` | Outreach status: queue, proof, funnel and Routine. Read-only, touches no state, sends nothing. |
| analytics-dashboard | S |  | all | `~/.hermes/skills/analytics-dashboard/SKILL.md` | Turn a LinkedIn Analytics export into an interactive dark-themed React dashboard plus 5 data-backed content recommendations. |
| linkedin-analytics-tracker | S |  | all | `~/.aside/u/0/skills/user/linkedin-analytics-tracker/SKILL.md` | Daily cross-channel measurement for LinkedIn growth: impressions, reactions, comments, profile views, website clicks, group reach, Reddit, trade pub. |
| rig-top100-analytics-content | S |  | all | `~/.aside/u/0/skills/user/rig-top100-analytics-content/SKILL.md` | RIG Top 100 capability #28: Content Analytics & Performance. Data drives content decisions. |
| analytics-surface | s | lg-measure | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-measure/sub/analytics-surface.md` | Where each number actually lives |
| lg-measure | S | linkedin-optimizer | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-measure/SKILL.md` | Read LinkedIn analytics honestly and turn last week into next week's plan. USE WHEN asked how a post or a week performed, when reporting impressions or reach... |
| measurement-kpi-loop | s | li-growth | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/li-growth/sub-skills/measurement-kpi-loop.md` | measurement-kpi-loop.md — read the numbers, pick next week's winners |
| reach-math | s | lg-plan | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-plan/sub/reach-math.md` | Reach math |

## Scraping and research (9)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| /scrape | C |  | all | `~/.hermes/commands/scrape.md` | Intelligent multi-engine web scraping - discover, extract and organize information from the web. |
| /scraper | C |  | all | `~/.hermes/commands/scraper.md` | Alias of /scrapers - fleet scrapers on 36/96/256. |
| /scrapers | C |  | all | `~/.hermes/commands/scrapers.md` | Global multi-engine scraper OS - all open scrapers + Browse AI fallback, fleet LLMs on RIG 36/96/256. |
| alfred-trend-pipeline | S |  | A | `~/.hermes/skills/alfred-trend-pipeline/SKILL.md` | Daily competitor and industry trend analysis for the Alfred content cron: Exa MCP + multi-provider fallback, JSON trend report. |
| rig-linkedin-scrape | S |  | all | `~/.hermes/skills/rig-linkedin-scrape/SKILL.md` | Read-only LinkedIn engagement scraper (PROVEN): a creator's posts + engagement, the logged-in feed, or a post's engagers. Never writes. |
| scrapers | S |  | all | `~/.aside/u/0/skills/user/scrapers/SKILL.md` | Global multi-engine scraper OS (18 engines) plus the canonical-session LinkedIn read path and a working Instagram read path. |
| claim-ledger | s | lg-source | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-source/sub/claim-ledger.md` | Claim ledger |
| corpus-map | s | lg-source | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-source/sub/corpus-map.md` | Corpus map |
| lg-source | S | linkedin-optimizer | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-source/SKILL.md` | Answer a LinkedIn question from RIG's scraped creator corpus with evidence classes attached. USE WHEN asked what a creator taught about X, whether a LinkedIn... |

## Cross-platform distribution (8)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| content-cross-platform-repurposer | S |  | all | `~/.aside/u/0/skills/user/content-cross-platform-repurposer/SKILL.md` | Repurpose one canonical piece across platforms while holding voice constant and respecting each platform's native grammar. |
| linkedin-cross-platform | S |  | all | `~/.aside/u/0/skills/user/linkedin-cross-platform/SKILL.md` | Amplify LinkedIn posts across Reddit, X, Substack, trade publications, podcasts, email and LinkedIn Groups, with the per-channel route-back map. |
| rig-top100-content-repurposing | S |  | all | `~/.aside/u/0/skills/user/rig-top100-content-repurposing/SKILL.md` | RIG Top 100 capability #26: Content Repurposing. 1 video to 10 posts, 5 articles, 3 threads. |
| distribution-pipeline | s | li-growth | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/li-growth/sub-skills/distribution-pipeline.md` | distribution-pipeline.md — attention → profile → pipeline |
| lg-distribute | S | linkedin-optimizer | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-distribute/SKILL.md` | Stage 12 of the LinkedIn Optimizer: take one LinkedIn asset out to the surfaces a RIG buyer actually reads - LinkedIn Groups, Reddit, X, Substack, email, and... |
| reddit-and-groups | s | lg-distribute | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-distribute/sub/reddit-and-groups.md` | Reddit and LinkedIn Groups - the two channels where a shortcut costs the account |
| substack-and-x | s | lg-distribute | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-distribute/sub/substack-and-x.md` | Substack and X - the two channels that fail for carrier reasons, not writing reasons |
| trade-publications | s | lg-distribute | all | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/skills/lg-distribute/sub/trade-publications.md` | Trade publications - the 2-4 week lane |

## Events and conferences (2)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| conference-outreach-playbook | S |  | all | `~/.hermes/skills/conference-outreach-playbook/SKILL.md` | Reusable conference outreach playbook - from attendee list to booked meetings (Dykema 2026). |
| linkedin-event-engagement | S |  | all | `~/.aside/u/0/skills/user/linkedin-event-engagement/SKILL.md` | Conference surge playbook (LinkedIn + X): discover events, build recognition T-21, surge T-5, hourly live loop on the hashtag, follow up after. |

## Client lane (Ideawake) (1)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| ideawake-linkedin-weekly | S |  | client | `~/.aside/u/0/skills/user/ideawake-linkedin-weekly/SKILL.md` | Run Coby Skonord's weekly LinkedIn engine for Ideawake: Mon/Wed/Fri publish+amplify, Tue/Thu engagement-only, plus a new-channel sweep. |

## Job-search lane (1)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| lucy-skills | M |  | job | `~/.aside/u/0/skills/user/lucy-skills/SKILL.md` | Meta skill + /lucy-skills from 527 Career Growth With Lucy videos: positioning, LinkedIn profile section-by-section, activity 20-10-5, resume, interviews. |

## Browser mechanics and automation (6)

| id | kind | parent | lane | path | what it does |
|---|---|---|---|---|---|
| /linkedin-machine | L |  | all | `~/.hermes/commands/linkedin-machine.md` | Build complete LinkedIn operation (Loop ID GL-BD-02): content pipeline, engagement engine, DM outreach, analytics dashboard, scheduling. |
| /ralph | C |  | all | `~/.hermes/commands/ralph.md` | Load the ralph Prime Agent skill and execute the requested task. |
| linkedin-automation | S |  | all | `~/.hermes/skills/linkedin-automation/SKILL.md` | Browser automation for LinkedIn via patchright + cookie vault: DM outreach, comment engagement, smart follows, profile views, endorsements, analytics. |
| linkedin-site-mechanics | S |  | all | `~/.aside/u/0/skills/user/linkedin-site-mechanics/SKILL.md` | Hard-won linkedin.com automation mechanics: searching/scraping posts, resolving post URLs, posting comments and replies, following, throttle detection. |
| patchright-linkedin-proofer | S |  | all | `~/.hermes/skills/patchright-linkedin-proofer/SKILL.md` | 4-phase safe patchright run against Mike's LinkedIn: read-only cookie probe, 5-name roster pre-warm, per-line APPROVE gate before send, post-action audit. |
| ralph | S |  | all | `~/.hermes/skills/ralph/SKILL.md` | Self-referential loop until task completion with architect verification (Ralph + Ultrawork iteration). |

## Retired: never route (7)

Postiz is retired; Eden (eden-mcp) is the single publisher of record. These still exist on disk for history only.

| id | kind | path | why retired |
|---|---|---|---|
| /jake-linkedin | C | `~/.hermes/commands/jake-linkedin.md` | core mechanism is Postiz |
| alfred-linkedin-chaos-pipeline | S | `~/.hermes/skills/alfred-linkedin-chaos-pipeline/SKILL.md` | core mechanism is Postiz |
| alfred-post-publisher | S | `~/.aside/u/0/skills/user/alfred-post-publisher/SKILL.md` | core mechanism is Postiz |
| linkedin-content-automation | S | `~/.hermes/skills/linkedin-content-automation/SKILL.md` | core mechanism is Postiz |
| linkedin-engagement-automation | S | `~/.hermes/skills/linkedin-engagement-automation/SKILL.md` | core mechanism is Postiz |
| postiz | S | `~/.hermes/skills/postiz/SKILL.md` | core mechanism is Postiz |
| ralph-postiz-pipeline | S | `~/.hermes/skills/ralph-postiz-pipeline/SKILL.md` | core mechanism is Postiz |

## Broken or empty routes: report, do not improvise (6)

These names appear in harness folders but have no readable SKILL.md or command file. If a task needs one, tell Mike the route is broken and stop.

- /timyakubson-linkedin-sales-navigator (command): expected at ~/.hermes/commands/timyakubson-linkedin-sales-navigator.md; status active
- linkedin-agency (skill): expected at ~/.hermes/skills/linkedin-agency/SKILL.md; status unknown
- linkedin-studio (skill): expected at ~/.hermes/skills/linkedin-studio/SKILL.md; status unknown
- rig-virality-predictor (skill): expected at ~/.hermes/skills/rig-virality-predictor/SKILL.md; status unknown
- rig-voice-engineering (skill): expected at ~/.hermes/skills/rig-voice-engineering/SKILL.md; status unknown
- ralph-l8 (sub-skill): expected at ~/.hermes/skills/ralph-l8/SKILL.md; status unknown

## Adjacent lanes: never route LinkedIn work here

| id | why | path |
|---|---|---|
| jacob-x-growth | content about a minor (Jacob, X account); never auto-scheduled, per-post approval | `~/.aside/u/0/skills/user/jacob-x-growth/SKILL.md` |
| rig-instagram-growth | Instagram lane (@rodgemd1) | `~/.aside/u/0/skills/user/rig-instagram-growth/SKILL.md` |
