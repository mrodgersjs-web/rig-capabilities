# EMBED runbook — daily-scorecard-loop (human step; every action below is OUTWARD-adjacent and stays un-applied)

Drafts for all SEVEN surfaces are compiled under `out/daily-scorecard-loop/`. Nothing below has been done.

## 1. Aside routine
- Review `out/daily-scorecard-loop/aside/routine.json` (prompt, rrule, session_config).
- Insert via the Aside routine surface with a minted id, `status='active'`, real `memoryPath` created.
- Quiet-hours / routine rules still bind; a paused routine is never auto-unpaused.

## 2. grokbot behavior
- Merge `out/daily-scorecard-loop/grokbot/lanes.fragment.yaml` into ~/rig-builds/grokbot-allmodels/lanes.yaml (append-only).
- Run gen.py -> candidate litellm.yaml; review out/report.json + coverage.md; promote on approval.
- Place `out/daily-scorecard-loop/grokbot/config-model-block.toml` into ~/.grok/config.toml ([model.rig-scorecard-daily] -> router alias rig-local-first).

## 3. Jake harness/brain loop
- Review `out/daily-scorecard-loop/jake/loop-card.md`; or arm the heartbeat with `out/daily-scorecard-loop/jake/heartbeat.json`.
- Stays `state: DORMANT` until a human flips it (Gate-D on the recurring job).

## 4. Temporal always-on schedule
- Review `out/daily-scorecard-loop/temporal/schedule-spec.py` + `schedule.json`; register with paused=True via the runner's own env.
- Unpausing is a Gate-D action.

## 5. goal-harness spec
- Review `out/daily-scorecard-loop/goalspec/harness-goalspec.draft.json`; promote into out/harness-goalspecs via the owner's compile flow.

## 6. jake-brain loop card
- Hand `out/daily-scorecard-loop/jake-brain/loop-card.md` + `COORD.md` to the app/jake_brain owner. This studio writes nothing there.

## 7. Aside chat brief
- Open the chat yourself with `out/daily-scorecard-loop/aside-chat/brief.md` via aside_chat_new when you want it live.

Route bindings resolved at compile time: aside=mimo-plan/mimo-v2.6-pro, lane=rig-scorecard-daily, router_model=rig-local-first.
