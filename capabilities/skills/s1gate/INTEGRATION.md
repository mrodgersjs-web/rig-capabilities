# s1gate integration plan: making the number do something

**The defect this fixes:** Jev returns a score, the score gets read, nothing changes.
A score that only informs is a dashboard. A score that drives a rewrite is a loop.

## Three verbs, in order of how much trust they need

| Verb | What it does | Calibration needed | Use it today? |
|---|---|---|---|
| `rank` | N candidates in, best-first out | **None.** Relative order is meaningful even when an absolute threshold is not | Yes |
| `improve` | Score, rewrite against the findings, rescore, up to N times. Returns the best version and the trajectory | **None** for advisory; the findings are the input to the rewriter, not a verdict | Yes |
| `check` (block) | Hard-stop on a calibrated threshold | **Measured operating point** at false-block <= 5% | Only once certified |

Every routine below uses `improve` and `rank`. None of them block. That is deliberate:
rewrite-until-clean gets 90% of the value with 0% of the false-block risk.

Verified 2026-09-18: `improve post.linkedin` took a draft with 4 findings (Lane A cast leak,
invented "87%" stat, banned vocabulary, peer-not-buyer) to 1 finding in **8.1s on a local
27B model**, replacing the fake stat with the author's real audit numbers from the context.

## The one pattern, everywhere

Wherever a routine currently says *"draft X and hand it to Mike"*, it now says:

```
1. Draft X as before.
2. Run:  rig-s1gate improve <rubric> --stdin --context "<who/what/why>" --max 3 --json
3. Hand Mike the BEST version, plus the trajectory line
   (e.g. "ESCALATE(4) -> ESCALATE(1)"), plus any finding that remained.
4. If the loop did NOT clear, say so in one line. Never hide a remaining finding.
```

Where a routine produces **several** candidates (post variants, comment targets, leads,
prospects), it runs `rank` first and only `improve`s the top one or two.

The rubric never sees Gate-D. `improve` on Lane C (`nil.jacob`) is `never_auto`: it
returns a cleaner draft and still ESCALATEs, because a human decides on a minor's lane.

## Routine-by-routine map

| Routine | Rubric | Verb | What changes in the prompt |
|---|---|---|---|
| Daily LinkedIn post package | `post.linkedin` | improve | Score Eden's draft; improve up to 3x; deliver best + trajectory |
| LinkedIn daily engagement sweep | `comment.linkedin` | rank, then improve | Rank comment targets; improve every comment before it is posted |
| LinkedIn post launch responder | `comment.linkedin` | improve | Improve each reply; positive-only rule is enforced by the rubric |
| Wednesday LinkedIn follow pass | `gtm.lead` | rank | Rank follow targets by fit band; top band first |
| Instagram daily content package | `post.instagram` | improve | Improve caption; unsourced health claims get rewritten out |
| Instagram daily engagement prep | `comment.linkedin` (adapted) | rank | Rank outward targets before Mike fires them |
| Instagram daily sponsor prospect | `gtm.lead` | rank | Rank prospects by fit band + `fit` choice |
| Instagram weekly collab prospects | `gtm.lead` | rank | Same |
| Instagram daily metrics log | `signal.performance` | check (advisory) | Classify each item's outcome so "what worked" is a counted claim |
| Instagram monthly monetization audit | `signal.performance` | check (advisory) | Same, monthly roll-up |
| RIG Client Growth: Research, Drafts & Review | `post.linkedin`, `email.outreach` | improve | Improve article draft and email drafts |
| Nightly copy gate sweep | `post.linkedin` / `post.eden` per lane | rank + improve | Rank the library; improve the bottom quartile |
| Jacob X Sunday content batch | `nil.jacob` | improve (never_auto) | Improve, then ESCALATE to Mike. Never auto-publish |
| Jacob X daily peer & reply scout | `nil.jacob` | improve (never_auto) | Same for reply drafts |
| Jacob X daily executor | `nil.jacob` | check (advisory) | Final pre-send annotation; a finding halts and reports |
| Friday end-of-day measurement log | `signal.performance` | check (advisory) | Counted outcomes, not vibes |
| Model route watchdog | none | | Unchanged |

## Coding agents

Wired via `capabilities/hooks/s1gate-stage-gate.sh` as a Stop hook, warn-only.
The rubric is `code.diff`; the verb is `improve` on the agent's own summary+diff when
the gate escalates. The loop is *the agent fixes its own findings in the same session*,
not a restart.

Plan gate: `plan.readiness` before any unattended build. A plan that scores
`readiness <= 1.2` gets one `improve` pass, and if it still does not clear, the build
does not start. This is the cheapest gate in the system because the artifact it protects
is the most expensive.

## GTM: the loop closes on outcomes, not drafts

`signal.performance` is the piece that makes this compound. Every published item gets
classified: business_outcome / audience_signal / vanity_only / no_signal, with
`attributable` and `sample_too_small` as guards. That log is what a System 2 review
reads monthly to retune the *rubrics* -- so the gate learns what actually converted,
not what looked good.

## What this costs

Jev usage observed across ~430 decisions today: **~1 cent total** at the provider's
billed rate. The rewriter runs on the LAN fleet (loopback tunnel first, Blackwell
second) at zero marginal cost. The `improve` loop's ceiling is 3 rewrites, so the
worst case per artifact is ~4 Jev calls plus 3 local generations: seconds, not dollars.

## What still needs a human

- Enforcing (hard BLOCK) on any rubric: needs question-matched labels. See
  `code.diff`'s calibration block for the refused attempt and the diagnosis.
- Gate-D: unchanged. `improve` makes a draft better; it never publishes it.
- Lane C: `never_auto` is structural, not a setting.
