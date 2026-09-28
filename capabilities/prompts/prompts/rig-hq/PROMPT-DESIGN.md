# PROMPT-DESIGN — RIG HQ three-tier prompt templates

Design document for the `prompts/rig-hq/` tree: `meta/<department>.md` (7),
`prompts/<agent>.md` (one per agent named in team-plan.json), and
`sub/<department>-<task>.md` (one per recurring task type and one per Reese
interrupt). Every template field below is justified by at least one citation.

Evidence base (read 2026-09-28):
- `~/.rig/jake/aos/prompt-research/omp-chat-patterns.md` — how Mike instructs (4,410 distinct typed instructions, 2026-08-03..2026-09-28). Cited `[OMP §n]`.
- `~/.rig/jake/aos/prompt-research/github-prompt-patterns.md` — 16 public prompt repos, tiering + fields + licenses. Cited `[GH#n]` with repo URL.
- `~/.rig/jake/aos/prompt-research/youtube-prompt-lessons.md` — 13 practitioner how-tos with timestamps. Cited `[YT channel @mm:ss]` with video URL.
- `~/.rig/jake/aos/maps/aside-links/team-plan.json` — 7 departments, meta-agents, agents.
- `~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json` — J1–J13 x 9 layers, 25 interrupts.
- `~/.rig/jake/aos/paperclip-build/prompt-gaps.json` — gap slugs this pass fills.

Citation key for OMP session quotes: session files under `~/.omp/agent/sessions/`;
the exact file per quote is recorded in `omp-chat-patterns.md` §2–§5 and reused here
by section reference only.

---

## 0. Laws before templates

1. **Reuse before write.** `capabilities/prompts/` is the first-party library; a new
   prompt is written only when `node tools/route.mjs "<job>"` finds no stored prompt
   that earns the place (`README.md`; `capabilities/skills/prompt-router/SKILL.md`).
2. **License law.** No text is copied from a repo without a permissive license.
   Structure may be learned from unlicensed repos (`contains-studio/agents`,
   `crewAIInc/crewAI-examples`, `disler/big-3-super-agent` — all no-license) and from
   GPL-3.0 `x1xhlol/system-prompts-and-models-of-ai-tools` (describe only, never
   quote). Everything in this tree is written in RIG's own words
   (`github-prompt-patterns.md` quoting policy; [GH#6][GH#10][GH#12][GH#16]).
3. **Jacob's lane (J9) is draft-only.** No auto-run agent, no auto-schedule, no
   auto-publish; Mike approves every artifact (team-plan.json `lane_c`;
   [OMP §3] "Everything past 40 seconds needs to be completely deleted").
4. **Nothing here is calibrated.** All files enter `status: draft`, `score: null`
   (`README.md` honesty contract). Scores come only from AutoPrompt + `tools/promote.mjs`.
5. **Paperclip is out of scope for this pass.** Jake attaches prompts after verifying
   (brief, deliverable 5).

## 1. Why three tiers

Composition direction is stable across every multi-tier repo inspected: task prompts
sit below role prompts, role prompts below routing/orchestration; nobody inverts it,
and task prompts are the most reused and most templated artifact
([GH tiering #4], e.g. Fabric's 261 task patterns `danielmiessler/fabric` MIT,
https://github.com/danielmiessler/fabric). The meta/orchestrator tier routes and
delegates, it does not do domain work ([GH tiering #1]: `ayush-that/sub-agents.directory`
`content/09-meta-orchestration/` MIT, https://github.com/ayush-that/sub-agents.directory;
`contains-studio/agents` department dirs; langgraph supervisor nodes,
https://github.com/langchain-ai/langgraph MIT). Corroborated on video:
"Orchestrator decides and delegates; specialists do one job"
[YT Brennan Wells @11:42](https://www.youtube.com/watch?v=twuZ5t-5O94),
[YT CrewAI crash course @07:42](https://www.youtube.com/watch?v=1op0cVFZj0Q)
("one step does not earn a crew"), [YT Anthropic tips @03:08](https://www.youtube.com/watch?v=LP5OCa20Zpg)
(workflow vs agent prompt are different shapes).

The separation of **output contract from procedure** is the newest pattern
(pydantic-ai typed `output_type`, https://github.com/pydantic/pydantic-ai MIT;
promptflow `outputs`/`sample`, https://github.com/microsoft/promptflow MIT; disler
output-styles): "what a good answer looks like" lives apart from "how to do the work"
[GH tiering #6].

## 2. Meta-prompt template — `meta/<department>.md`

One per department. Fields, each justified:

| # | Field | Why (citation) |
|---|---|---|
| M1 | IDENTITY AND MANDATE (department, meta-agent, jobs owned J-list) | Role/identity is table stakes (12/16 repos, [GH fields]); department scope = its JTBD jobs named literally [OMP implications meta-1]. |
| M2 | SCOPE / OUT-OF-SCOPE ("not yours" list) | Mike's scope fences are typed in the same breath as the ask ("do ONLY this sub-slice… Stop after writing the receipt", "This is Mike Rodgers' job search, not James") [OMP §2a-3, §2b]; `repowise-dev/claude-code-prompts` `patterns/01-system-prompt-architecture.md` MIT, https://github.com/repowise-dev/claude-code-prompts (ROLE AND SCOPE, NON-NEGOTIABLE RULES). |
| M3 | AGENT ROSTER (name, one-line role, prompt file, when to invoke) | contains-studio department dirs over role prompts [GH#10]; sub-agents.directory meta-orchestration roster [GH#15]; 8 of 16 repos carry goal/mission [GH fields]. |
| M4 | ROUTING RULES (task -> agent, delegation order, one task per prompt) | "One task per prompt; chain the rest" [YT Brennan @05:20]; classifier sub-prompt picks the next specialist prompt [YT Anthropic tips @03:46]; crewAI `tasks.yaml` agent assignment + context chaining [GH#12]. |
| M5 | THE BAR (numeric, externally anchored) | Mike's correction: "wouldn't 0.9 be something else that's gone viral by a top influencer" — never rate against his own corpus [OMP §3]; accepted runs all carry a numeric bar (0.9 Jev, median-of-3 >= 90, "print HM DONE") [OMP §4]; "replace adjectives with budgets and heuristics" [YT Anthropic agents @08:17](https://www.youtube.com/watch?v=XSZP9GhhuAc). |
| M6 | INTAKE TRANSLATION (homophone table + rule) | 183 homophone-corrected instructions; "Kobe"=Coby, "Quinn38"=Qwen 3.8, "open bot rig"=OpenRouter [OMP §5]; Reese J10 interrupt "A dictated name matches nothing -> Sense tests homophones before filing" (reese-jtbd.json). |
| M7 | RECEIPT RULE (named artifact or it did not happen) | "two runs ended without a receipt" [OMP §3]; accepted runs close on REPORT.md first line / commit sha / printed token [OMP §4]; only 3/16 repos carry done-criteria — the field that separates governance from prompt piles [GH fields]. |
| M8 | GATE (outward actions, batch APPROVE gd_*) | "I approve all gate d", "APPROVE gd_…" bulk tokens [OMP §2a-4]; escalation as a tool call, humans contacted with tools [GH#7] `humanlayer/12-factor-agents` `content/factor-07-contact-humans-with-tools.md` Apache-2.0, https://github.com/humanlayer/12-factor-agents. |
| M9 | LOOP HYGIENE (kill switch, fail-loud, deadline stop, budget cap) | "so codex session … just went into loops" [OMP §3]; "Add a stop, because absolute instructions loop" [YT Anthropic agents @12:50]; run length is always stated ("1000x turns until tuesday at 8am") [OMP §2a-7]; Reese governance_gap: budget cap inside the approval layer — every job gets one (reese-jtbd.json). |
| M10 | REESE LAYERS + INTERRUPTS owned (table: trigger -> response -> owner) | reese-jtbd.json layers 01–09 (Orchestrator, Sense, Make, Your approval, Craft, Ship, People, Learn, Identity files) and the department's interrupts; each interrupt has a `sub/` file. |
| M11 | DONE CRITERIA FOR THE DEPARTMENT + ESCALATION | done criteria 3/16 repos, escalation 3/16 — the two rarest, most valuable governance fields [GH fields]; repowise verification habits [GH#14]. |
| M12 | RESUME SEMANTICS ("Resume, do not restart: read git log first"; never overwrite completed work) | "I don't want override anything else that's been done" [OMP §3]; resume-not-restart is in the must list [OMP implications meta/global]. |

## 3. Agent prompt template — `prompts/<agent>.md`

One per agent (team-plan.json `agents` + `meta_agent` names; Jacob's lane as a
draft-only prompt). YAML frontmatter then body.

| # | Field | Why (citation) |
|---|---|---|
| A1 | frontmatter: id, tier, department, agent, parent, task, triggers, sources, provenance | Typed frontmatter is the richest field schema observed (promptflow `.prompty` `name`, typed `inputs`, `outputs`) [GH#9]; contains-studio frontmatter name/description/tools [GH#10]; registry requirement (registry.json entries; README.md layout). |
| A2 | ROLE AND IDENTITY (job sentence: what you do, for whom, what you will not do) | "Open with identity and goal" [YT ZazenCodes @10:12](https://www.youtube.com/watch?v=MO3U1X8-NNQ); "Name the job, not a generic expert" agreement 5 [YT Tyler @03:48](https://www.youtube.com/watch?v=Fwv_klMgOJ4); role costume counterpoint resolved as a job sentence, not "world-class" flavor [YT contradictions #3]; "make the role as specific as the job" [YT Tyler @03:48]. |
| A3 | MODEL ROUTE (pinned) + WORKTREE/CWD boundary | "Model route (fixed): mimo-plan/mimo-v2.6-pro" in TAC builder briefs — zero follow-up corrections [OMP §4]; Mike pins "/model mimo-plan/mimo-v2.6-pro" [OMP §2a-5]; fallback chain mimo -> xai-oauth/grok-4.7 -> anthropic/claude-opus-5-5, never Flash [brief; OMP §2a-5 homophones]. |
| A4 | READ-FIRST list (rules file, task file, addendum) | Corrections arrive as "read the ADDENDUM at the bottom of…" [OMP §2c]; context map plus an exclusive read list so the agent does not search what you know [YT IndyDevDan agentic @11:41](https://www.youtube.com/watch?v=luqKnexhpFs). |
| A5 | GOAL (measurable) | goal/mission 8/16 repos [GH fields]; crewAI agents.yaml role/goal split [GH#12]; "Scope the ask to a concrete job, not a generic assistant" [YT Google Cloud @01:22](https://www.youtube.com/watch?v=6xv6prtGNiE). |
| A6 | INPUTS IT EXPECTS | typed inputs 6/16 repos [GH fields]; pydantic-ai `deps_type` dynamic context [GH#8]; "inject date, preferences, and session facts at runtime" [YT Zazen @13:55]. |
| A7 | OUTPUT FORMAT (fixed schema / expected_output) | output contract 7/16 repos [GH fields]; "Every task has a description and an expected_output … the part most people skip" [YT CrewAI @03:50]; "expected_output is the handoff contract" [YT CrewAI @05:58]; "Return JSON when another system has to parse it" [YT Tyler @04:59]. |
| A8 | TOOL POLICY (when to use which tool; what it cannot do) | tool allowlist 6/16 repos [GH fields]; "Write when-to-use-which-tool rules … six similar search tools confuse the model" [YT Anthropic agents @10:34]; "A polished system prompt cannot rescue a bare tool" [YT Anthropic tips @06:16]. |
| A9 | CONSTRAINTS: Mike's must/never + redaction | must/never list [OMP global rules]; never print credentials (pasted "gh token -" incident) [OMP implications sub-6]. |
| A10 | DONE CRITERIA (one-line checkable: token, threshold, or STATUS: BLOCKED <reason>) | accepted runs share "a named artifact, a numeric bar, a bounded scope, and a receipt" [OMP §4]; "Assert the field or the final state; prove the check can fail" [YT Ebbelaar @46:01](https://www.youtube.com/watch?v=a3SMraZWNNs). |
| A11 | RESUME + REPORT FORMAT (what is left to do, what did we learn, what broke) | "Za need to be done out … what's left to do I don't want override anything else" [OMP §3]; his own words "what broke, what did we learn" [OMP implications prompt-6]. |
| A12 | ESCALATION TRIGGERS (where blocked/out-of-scope goes) | escalation implicit in 13/16 repos — a governance hole [GH anti-pattern 6]; factor-07 contact humans with tools [GH#7]; "Give an escape hatch or the format becomes a hallucination" [YT YC @09:25](https://www.youtube.com/watch?v=DL82mGde6wo). |
| A13 | FEW-SHOT (optional, 1–3, examples of a miss, marked never to emit verbatim) | "Bake the failure you just saw into an example" [YT Anthropic 101 @13:11](https://www.youtube.com/watch?v=ysPbXH0LpIE); "Mark examples as not to be spoken" [YT Zazen @15:51]; resolved contradiction: examples of the output contract or a failure, never a scripted trajectory [YT contradictions #1]. |

## 4. Sub-prompt template — `sub/<department>-<task>.md`

One per recurring task type and one per Reese interrupt.

| # | Field | Why (citation) |
|---|---|---|
| S1 | NAME + TRIGGER ("run when…") | crewAI `tasks.yaml` description triggers [GH#12]; Fabric patterns are one atomic transformation unit each (`data/patterns/*/system.md`) [GH#1]; slash-command file name is the command [YT Net Ninja @02:16](https://www.youtube.com/watch?v=52KBhQqqHuc). |
| S2 | TYPED INPUTS (name, type, example; bind to the exact supplied bytes) | "when he supplies an asset … bind to those bytes, not a lookalike" [OMP implications sub-1]; promptflow typed `inputs` with sample values [GH#9]; `$ARGUMENTS` parsed into named fields [YT Net Ninja @07:11]. |
| S3 | STEPS (numbered, imperative; exclusive read list) | Fabric STEPS [GH#1]; disler commands Run/Read/Report sections [GH#16]; "Fixed order for a one-shot task prompt" [YT Anthropic 101 @04:24]; read order stated "exclusively" [YT IndyDevDan agentic @11:41]. |
| S4 | OUTPUT FORMAT (exact sections/schema; repeat the critical constraint at the end) | "Repeat the output contract at the end … the closing block carries more weight" [YT Zazen @13:18]; section the prompt with markdown or XML [YT Anthropic 101 @10:17]. |
| S5 | EXPECTED_OUTPUT (one sentence the result must satisfy) | expected_output is the handoff contract [YT CrewAI @05:58]; countable output verified from the source of truth ("build out 100 cards", "at least 15 subagents") [OMP implications sub-2]. |
| S6 | DONE TEST (check that proves it; verification inside the task) | "prove this is done, visually verify it" [OMP §2]; independent critique on a different model family [OMP implications sub-3]; "no prompt change without a check that can go red" [YT Ebbelaar @46:01]. |
| S7 | FAILURE HANDLING + FIX-FORWARD (max rounds, then STATUS: BLOCKED) | "Keep iterating until you get there" with a named stop ("if the Jev 0.90 bar is not met after 3 rounds… 'STATUS: BLOCKED bar-not-met'") [OMP §3, implications sub-4]; compact errors to re-prompt [GH#7 factor-09]; guardrail re-prompts the same builder max 3 then Windshield (reese-jtbd.json J12 interrupt). |
| S8 | PERSISTENCE (where the result lands: report file + rig memory os) | "save, commit, and push to rig memory os" [OMP §2a-6]; next session must find it [OMP implications sub-5]. |
| S9 | REDACTION (keychain item names, never values) | pasted "gh token -" incident [OMP implications sub-6]; secrets never in repo (README.md rules). |
| S10 | STOP / ESCAPE HATCH (ask instead of inventing) | "Give an escape hatch or the format becomes a hallucination" [YT YC @09:25]; a `debug_info` field lets the model complain [YT YC @10:00]. |

## 5. Global must / never (from 4,410 typed instructions)

**Must** [OMP global rules]: pin the model route + fallback; state the numeric bar;
state the scope fence and non-goals; ask for a receipt; resume rather than restart;
translate dictation homophones before declaring an entity unknown; report "what is
left to do" honestly.

**Never** [OMP global rules]: claim done without an artifact; push to a repo/outward
target that was not named and verified; overwrite prior completed work; rate quality
against his own corpus when an external bar exists; run unbounded loops; auto-publish
anything in the Jacob/minor lane; print credentials.

Additional standing rules:
- Activity is not completion (cloned websites, "we've done no market research") [OMP §3].
- Build the deliverable, not meta-tooling ("Stop building gate tooling infrastructure") [OMP §3].
- Choose a stack that can run here ("the marimo dashboards did not work … set these up in docker") [OMP §3].
- Visual output is checked before it is claimed (horse's-head render) [OMP §3].
- Fail-loud: a silent failure rate is a defect ("so we are failing most runs") [OMP §3].

## 6. Homophone intake table (verbatim from [OMP §5])

| Heard | Means | | Heard | Means |
|---|---|---|---|---|
| Kobe | Coby (Skonord) | | open bot rig | OpenRouter |
| Quinn38 / "Quinn 3.8" | Qwen 3.8 (Blackwell) | | workflowz | workflows |
| gemini 3.8 flash | Qwen 3.8 Flash on Blackwell | | traject | trajectory / the Traject app |
| memo v 2.6 / Mimo | MiMo v2.6 | | Pewakie Pirate | Pewaukee Pirates |
| chat GBT | ChatGPT | | All My Pie | all my PAI |
| soul id | Sol (model family) | | AV IS | Avis (James Loehr's search) |
| adn / buidl / untip | and / build / until | | | |

Not homophones (never "correct"): Blackwell, GrokBot, OpenBot, MiMo, Jev, ApplyPilot,
Birch, Hudl, marimo, Prefect [OMP §5].

## 7. Quality bar for these files themselves

Per [YT top-12 rules]: every task prompt ends in a contract (rule 7); examples are for
misses and marked as examples (rule 10); every prompt carries an escape hatch and a
stop (rule 8); no prompt change without a check that can go red (rule 12) — which is
why this pass ships a planted-failure proof against `tools/route.mjs --selftest`.
Start short; add a line only when a real run fails (rule 2) — these are v1 drafts and
are expected to grow from observed failures, not from taste.
