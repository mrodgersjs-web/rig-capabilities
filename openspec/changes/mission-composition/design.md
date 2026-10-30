# Design

The catalog remains asset authority. `rig_capabilities.mission` joins catalog
agent entries, current prompt registry entries, and actual file hashes for one
natural-language request. OMP/Prime agent install roots are inventoried as
unmanaged additions; unsupported files are reported. The packet is ephemeral
and content-addressed, so no permanent wrapper is generated per installed
agent.

The router proposes one meta-agent, one writer, and one read-only verifier.
Low scores and ties abstain. It selects a top-level `when-*` skill only when
deterministic hints resolve; specialist skill selection is constrained to the
meta-skill's routing contract. The meta/task/subprompt chain is explicitly
draft-aware. The task prompt is looked up in the versioned prompt registry.

The local OpenJev `mission.route` choice is a shadow check on the meta-skill
lane. Its decision ID, model, confidence, latency, and disagreement are recorded
without giving it dispatch or promotion authority. A degraded local Jev call
is visible and never silently falls back to hosted Jev. Promptfoo evaluates
offline deterministic routes; the Jev shadow needs separately labelled live
cases and calibration before it can determine routes. Jev cannot prove work
completion, source support, or safety by itself. See `JEV-PRACTICE-REVIEW.md`.

Memory is accessed only via the authenticated `memory.get_context_package`
front door. Packet output preserves source IDs and statuses but not memory
bodies. Memory cannot expand authority. A failed call yields `degraded` and
never falls back to the store.

The first Promptfoo suite is a local-provider route contract. It cannot prove
model-output quality. Weekly scouting retains URL/title/headings/hash only;
candidate practices must be converted into separately evaluated challengers.
No weekly job auto-promotes, installs, or executes anything.

## Next gates

1. Build and live-smoke each runtime adapter (Codex, Claude, Hermes, OMP,
   Prime, Aside where a native agent contract exists) with observed load and
   execution receipts.
2. Add real coding-task artifact fixtures and an explicit independent outcome
   evaluator to Promptfoo. Bind score to dataset, provider/model, and prompt
   hashes before a prompt can become calibrated.
3. Add batched Jev shadow choices for shortlisted agent, skill, prompt, and
   tool candidates, then label real cases and measure disagreement, false
   accept, abstention, p95 latency, and cost against deterministic routing.
4. Stage candidate prompt/agent edits weekly; promote only on verified gains
   and within existing Gate-D and repository-placement rules.
