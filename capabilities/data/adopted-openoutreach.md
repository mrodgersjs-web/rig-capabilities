# PROVENANCE — eracle/OpenOutreach

- Upstream: https://github.com/eracle/OpenOutreach @ 05ce1fa (2026-10-23)
- License: GPL-3.0 (read from LICENCE.md, not the badge) — stays a separate process, called over CLI/JSON, never vendored into MIT code
- Adopted: 2026-10-29 (clone for reference). The **runtime** is the pipx install `~/.local/bin/openoutreach` v6.1.2, not this clone.
- Already mounted: `~/Developer/clients-ai-jobs/server/sources.js:155 runOpenOutreach()` → `jf_people` with provenance `openoutreach`, logged in `source_runs`.
- Verdict: **installed and wired, but has never produced a lead.** `source_runs` shows openoutreach failed=3 (2026-10-28), detail: `onboarding_incomplete — set OPENOUTFIND_BETTERCONTACT_API_KEY`. `~/.openoutreach` holds the generated RIG ICP brief (mid-market 50–2,000 employees, AI-leadership buying roles, competitor/staffing exclusions) written 2026-10-29 by the local router (sglang `qwen3.8-flash-next-uncensored` on :18811), so the LLM leg is proven; only the data-provider key is missing.
- Walls: BetterContact API key. Free tier 40 credits, no card; discovery is billed nothing, a verified work email costs 1 credit (~$2/lead hosted). Key belongs in `EnvironmentVariables` of `~/Library/LaunchAgents/com.rig.clients-ai-jobs-app.plist` (currently only `PORT=3211`), then `launchctl kickstart -k gui/$UID/com.rig.clients-ai-jobs-app`.
- Dedupe: Oxygen (oxygen-agent.com, free plan, activation 4/4 complete, a sequence launched) already sends. OpenOutreach's job is discovery + written fit reason, not another sender. Nothing in this lane may send without Gate-D.
