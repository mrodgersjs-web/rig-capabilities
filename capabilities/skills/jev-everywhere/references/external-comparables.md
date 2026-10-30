# External comparables: how other people built the same thing

Distilled synthesis with sources. Primary index: yibie/awesome-jev
(https://github.com/yibie/awesome-jev, 1.5k stars, observed 2026-09-23) and its
Classification & Routing category file. These are leads and pattern sources, not
endorsements: the list itself says inclusion is not a quality review, and its
adopter checklist below is worth more than any single entry.

## Transferable patterns (with the project that demonstrates each)

1. **Route the model/effort per task, after deterministic pre-filtering.**
   Jevonian (https://github.com/xinyao27/jevonian) picks model route AND thinking
   level in one call from session state and quota health, while pinned models,
   explicit requests and `routing.mode: "off"` skip Jev entirely; low confidence is
   marked in the ledger rather than accepted. Switchboard
   (https://github.com/ruban-24/switchboard) matches Claude Code / Codex tasks to
   model + reasoning effort and then keeps the choice stable for the conversation to
   protect prompt-cache continuity.
2. **Skill selection is a typed decision, run in shadow first.** jev-skill-router
   (https://github.com/shimo4228/jev-skill-router) is a Claude Code plugin whose
   UserPromptSubmit hook asks one Choice over the installed skill roster plus
   boolean gates on whether any skill is needed, suggests only above a 0.30 fit
   floor, and defaults to shadow mode that logs the decision without injecting it.
   pi-jev-skill-picker (https://github.com/safzanpirani/pi-jev-skill-picker) ranks
   installed skills before any of them run; langchain-skill-router
   (https://github.com/deyna256/langchain-skill-router) keeps every non-picked
   skill's instructions out of the prompt.
3. **One call per batch, answers mapped to actions by code.** jev-logtriage
   (https://github.com/jyatesdotdev/jev-logtriage) batches collapsed Loki logs into
   ONE call of Noul + Score + Choice and maps answers in code to
   suppress/watch/review/notify/page, low confidence to review, nothing executed.
   jev-oncall (https://github.com/mingleiw/jev-oncall) asks 4 typed questions per
   alert in one call, pages on P(SEV1)+P(SEV2) >= 0.80, routes the middle band to a
   human with a 15-minute ack before it pages anyway, and falls back to configured
   severity on any error or timeout. Published run: p50 418 ms, p95 1477 ms,
   $0.04 per 1,000 alerts.
4. **Code first, Jev second, never guess.** jev-table-import-mapper
   (https://github.com/DuvInc/jev-table-import-mapper) does a strict deterministic
   name-equality pass first, then one Noul per remaining (source, destination) pair
   plus a guard Noul per incoming column (253 questions in one call, 915 ms,
   $0.0012), leaving unmapped fields visible above a 0.75 threshold rather than
   guessing.
5. **Ask the disqualifying question first.** jev-resume-disqualifier
   (https://github.com/AiPersonacademy/jev-resume-disqualifier) knocks a resume out
   in under 25 ms so only survivors reach full evaluation. Same shape as our S3.
6. **The meta-route is itself a typed decision.** jev-fit (https://jev-fit.com)
   sends an idea plus a fixed typed rubric where a Choice picks plain code, Jev, or
   a reasoning LLM, behind a Noul gate for non-tasks; code vetoes Jev when the idea
   needs images; low confidence returns "not sure". This is S12 in executable form.
7. **Judgment without side effects.** JevBystander
   (https://github.com/Nisaka520/JevBystander) answers one batched request of typed
   questions about a visible chat and then shows three toasts and does nothing else:
   no generated reply, no input injection, no screenshot. The judgment path never
   acts.
8. **Flag-gated migration from LLM to Jev.** Notra
   (https://github.com/usenotra/notra) routes brand-visibility classifiers off an
   LLM and onto Jev Booleans at a 0.5 threshold behind `NOTRA_JEV_CLASSIFIERS`,
   targeting 300 ms p50. Shadow first, flip when traces are clean.
9. **Documents and browser surfaces are in scope.** DocJev
   (https://github.com/jerryjliu/docjev, LlamaIndex) classifies documents against
   natural-language category rules and finds sub-document boundaries, 40/40
   originals at about 182 ms decision p50. Tab Sorter
   (https://github.com/AstonyCat/jev-tab-grouper) groups browser tabs from one
   parallel call with a fixed fallback bucket and untouched manual groups; Feed Lens
   (https://github.com/SkywalkerDarren/feed-lens) annotates social posts in a Chrome
   extension with per-platform Noul labels.
10. **Honest counter-evidence on cost.** AI-decision-maker
    (https://github.com/zlZayn/AI-decision-maker) measured Jev at 6.6-12.7x an LLM's
    token cost for CSV typing, because the answer is one character while per-question
    criteria repeat. Jev wins on latency, determinism of the answer set, and
    classification volume, not automatically on tokens. Measure before claiming.

## The adopter checklist (steal this as a "bad looks like" list)

From awesome-jev's "Curation is not endorsement", run before adopting any Jev
project, and equally before claiming your own embedding works:

- Does the code actually call the Jev API? Look for a real request carrying typed
  questions, and a parsed answer coming back. (This is also the proof standard for
  our own "Jev was used" claims: a decision-log row or a request/response pair.)
- Is there a runnable check? A test, an example with expected output, or a public
  demo. No check means no evidence it works.
- Do the numbers have a source? Any accuracy, latency, cost or volume figure should
  be traceable to the linked page.
- How much of the repository is code? Prompt-document projects can be legitimate;
  know which one you are getting.
- Is there a license?

Two more warnings the list makes that map onto our own estate: same-day bulk
submissions sharing one scaffold (same AGENTS.md / CLAUDE.md / STATE.md /
CHANGELOG.md, one or two commits each, more prose than code) are unproven leads,
not validated tools; and removal is as valid a contribution as addition, so a
pattern that fails refutation gets cut rather than archived.

## Where our estate already goes further than these

- Confidence floors as a second axis and false-block-first optimization (s1gate
  laws 2 and 4), and no uncalibrated enforcement (law 3).
- A calibration corpus that converts advisory gates into enforcing ones via
  `rig-s1gate label` + `rig-s1gate calibrate` over `~/.rig/s1gate/decisions.db`.
- A never-auto lane for content about a minor, where even a clean PASS downgrades to
  ESCALATE (law 6).

## Retired local System One comparison, 2026-09-23

Mike retired OpenJev on 2026-09-30. Use hosted JEV only, redact first, and defer if
private details remain. This list is historical comparison evidence and does not
authorize installing or restarting any local classifier.

- razorback16/openjev (https://github.com/razorback16/openjev) was the selected historical candidate:
  DiffusionGemma 26B-A4B reads answer-slot probabilities in one read-only pass (no generation, so
  answers cannot go off-schema), Jev-compatible wire API and error shapes, Apache-2.0, measured
  latency tables, Docker (vLLM / NVIDIA) and in-process MLX (Apple silicon) backends. Kept caveat:
  answer quality is whatever DiffusionGemma gives in this mode. The retired MLX deployment
  observations are preserved in ../references/embedding.md section 4.
- Other same-name historical candidates were SiliconLabAI/OpenJev
  (playground; parallel/oneshot modes parse LLM prose; useful part is Mapika/decider-2b),
  zhihz/openjev (frozen Qwen3-4B, no score primitive, sequential reads), xingwudao/OpenJev
  (deterministic mock only, "real inference planned", no license), nico-martin/open-jev (in-browser
  Transformers.js scope). A listing here is a lead, not an endorsement.
