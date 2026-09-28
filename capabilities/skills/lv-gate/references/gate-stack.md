# Gate stack: the ordered pre-publish gate and its verdict

## The stack, in order

1. Freeze the artifact (path + sha256). That hash is the gate subject in every downstream call.
2. Jev rubric first, per the stage mandate. Decision id recorded from `~/.rig/s1gate/decisions.db`.
3. Executable post gate (`li_post_gate.py`): selftest, then run with the crowding count. Rewrite on the
   named ACTION until clean. Exit 0 pass, 1 blocked, 2 usage error. Every finding carries a verb; a
   finding without a verb is a dashboard [li-post-gate].
4. Harness gates from the hB-04 session contract, in order, each recorded PASS / FAIL / SKIPPED.
5. Independent critic: scorecard, named failing criteria, hard blocks, ship / rewrite / kill
   [lg-critique, scorecard].
6. Anti-slop pass and the Eden voice-law-checker (see `voice-law-and-slop.md`).
7. Publish gate record from `rig-revenue-publish-gate`: six checklist cells, then REQUEST-APPROVAL or
   BLOCK. It never approves [rig-revenue-publish-gate].

## Fail-closed rules (each one is a stop, not a note)

- Jev errors, rubric absent from the criteria file, or the classifier CLI missing: DEFER. Do not
  substitute a different rubric and do not invent a JEV model [hB-04].
- `li_post_gate.py --selftest` fails: the gate is broken. Say so; do not publish on its verdict and do
  not treat the missing gate as a pass [hB-04].
- A proof command that cannot run is reported SKIPPED, never PASS [hB-04].
- The critic shares a session or model family with the drafter: refuse to score, report blocked
  [lg-critique].
- Two rewrite iterations reached: ESCALATE to Mike instead of grinding [lg-critique].
- Any step that could not run turns the final verdict into DEFERRED.

## Verdict vocabulary

One verdict per artifact, and only these four words:

| verdict | meaning | evidence required |
|---|---|---|
| PASS | every runnable gate passed | Jev decision id, gate exit codes, critic score, voice-law PASS |
| ESCALATE | fixable failures or a judgment only Mike can settle | named failing criteria and the exact question for Mike |
| BLOCK | a hard block or a halt-tier finding | the blocking rule and the finding text |
| DEFERRED | a classifier or gate could not run | which one, and the exact error |

An advisory PASS never authorizes publishing, sending, boosting or spend. Publishing and scheduling are
Gate-D items with Mike's explicit yes for that item; Eden remains the only publisher of record
[viral-core, hB-04].

## Rewrite loop

A rewrite goes back to the drafter with the failing criteria only, never the praise. Max 2 iterations.
Then escalate with the score history rather than averaging away disagreement [lg-critique].

## Gate output shape

```
artifact: <path> sha256:<hash>
jev:      PASS|DEFERRED  (rubric, decision id or error)
postgate: exit 0|1|2     (selftest: PASS)
harness:  CG-xx: PASS|FAIL|SKIPPED ...
critic:   n/10  failing: ...
voice:    anti-slop clean | voice-law-checker PASS|FAIL
publish:  REQUEST-APPROVAL | BLOCK
verdict:  PASS | ESCALATE | BLOCK | DEFERRED
```

Absorbed from: lg-critique; tool contracts cited: li-post-gate, hB-04-linkedin-post-session,
rig-revenue-publish-gate, viral-core.
