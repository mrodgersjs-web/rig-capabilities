---
name: capabilities-realign
description: Run the weekly Realign loop — score C_t/A_t on the committed register, honour the 10% corpus halt, demand a file-backed booking, and emit the five week artifacts, honestly dry and honestly BASELINE_ONLY.
argument-hint: "[--week YYYY-Www] [--root DIR] [--apply]"
allowed-tools: Read, Bash
category: meta
outcome: "meta: the week gets a verdict from code over files — zero bookings is a named cause, a first week is a baseline, and neither is allowed to read as an improvement"
done_when:
  - file:capabilities/commands/capabilities-realign.md
  - grep:capabilities/commands/capabilities-realign.md:BASELINE_ONLY
  - cmd:test 5 -eq $(python3 -c 'from rig_capabilities.realign import ARTIFACT_KINDS; print(len(ARTIFACT_KINDS))')
  - cmd:test 1 -eq $(python3 -c 'from rig_capabilities import convergence as C; g = C.weekly_gate(None, dict(c_t="0.5", a_t="0.5"), [], 0, unclassified_rate="0.05"); print(int("booked_qualified_conversations" in g["causes"]))')
  - cmd:test 0 -eq $(python3 -c 'from rig_capabilities.register import load_bookings as L; print(L("tests/fixtures/fable2031/bookings-zero.json")["count"])')
  - grep:capabilities/commands/capabilities-realign.md:state: DORMANT
  - grep:capabilities/commands/capabilities-realign.md:gate_d_required: true
state: DORMANT
gate_d_required: true
cadence: "0 17 * * 0"
great_example: capabilities/commands/capabilities-realign.md
acl: public
quality_floor: 0.7
---

# capabilities-realign

The weekly convergence driver: `rig_capabilities.realign.run_week` scores one ISO week
(`week_id()` → `%G-W%V`, never typed by hand) against `capability_register.csv` and the corpus,
and `convergence.weekly_gate` — not this conversation — issues the verdict.

1. Run dry first: `./bin/rig-capabilities realign` (add `--week YYYY-Www` to score a named week).
   Dry is the default: `--dry` is an explicit no-op and `--apply` is the only mode that writes.
2. Bound the corpus scan in interactive runs with `--root <dir>` (repeatable). The unbounded live
   roots take minutes; an unreported unclassified rate makes the week FAIL, never PASS — inheriting
   last week's rate is not a fallback.
3. Read the verdict as the five-condition node it is: PASS needs ΔC_t > 0, ΔA_t ≥ 0,
   unclassified_rate ≤ 0.10, bookings > 0, and no unresolved flag ≥ 5σ. Anything else prints
   named `causes` — quote them, do not paraphrase them away.
4. With no prior sealed week the verdict is **BASELINE_ONLY**: this week's C_t/A_t are a baseline,
   never a delta, and must never be described as an improvement. Today's honest first-week line is
   `verdict BASELINE_ONLY · causes [booked_qualified_conversations] · bookings 0 · sealed false`.
5. A zero-booking week against a real baseline is FAIL with its cause named — complete, never
   retried, never back-filled. Three FAIL weeks escalate to LOOP_REBUILD_REQUIRED; three weeks of
   rising C_t with zero bookings escalate to WEIGHTS_INVALID.
6. Quote the five artifact paths written under `.context/realign/<YYYY-Www>/` (register diff,
   convergence report, proof JSON, Doctrine Update Phrase, Operator's Weekly). Each carries
   `sealed: false` with a named seal reason until a real `proof_hash` exists.

Bookings are ZERO by evidence: a record counts only when its `qualification_evidence_path`
resolves to a file on disk. No output of this command may state or imply a booking, a meeting, a
revenue figure, or a convergence improvement that the proof JSON does not carry. Fleet status stays
BLOCKED_PENDING_SENTINEL while Sentinel Prime is specification-only. The weekly schedule is staged
dormant in `.context/realign/cron-job.json` (`enabled: false`); arming a recurring job is its own
Gate-D action.

The read-only `capabilities_converge` MCP tool is deliberately not used in `done_when`: `mcp:`
parses as a form, but it is only runnable once the handler answers `{}` without raising, while
every check above is a `cmd:` that runs now and fails honestly if the code behind it breaks.
