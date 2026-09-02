# Great example — capabilities-certify

Two halves, both earned. Run: `certify plant`, then a promotion review.

## 1. The gate matrix (`plant`)

`rig_capabilities/certify.py` runs its `GATES` table — twelve gates as of
2026-09-02 (suite, index_fresh, done_tests, idp_integrity, acl_jake, register,
corpus_refusal, canary_detection, lease_exclusivity, fable_dormant,
stage_order, evidence_ledger). The V22 five-gate plant (suite / index_fresh /
done_tests / idp_integrity / acl_jake, all RED-when-planted, all restored
GREEN) still holds inside that larger table; the table grew, the discipline
did not change. It once caught a live bug: `semgrep`'s done_when grepped
`SKILL.md:Semgrep` — the frontmatter itself carried the pattern, so the check
could never fail. A certification run that finds its own weakness is worth
more than five clean green runs.

## 2. The held-out promotion review

Every gate above scores the estate on the tasks the estate was written
against. So before a contract edit replaced the incumbent, its promotion
record went through `scripts/held_out_nonregression.py`. The overfitting
candidate (train 0.6667 → 0.9167, held-out 0.7500 → 0.3750) — real output:

```
$ python3 scripts/held_out_nonregression.py check examples/fixtures/held-out/heldout_regression
...
REFUSE heldout_regression: regressed cases (pass->fail): h1, h2, h3
REFUSE heldout_regression: held-out regression: 0.7500 -> 0.3750 (drop 0.3750 > band 0.0200) — tasks: h1, h2, h3
$ echo $?
1
```

Round's old rule — "applied only when done-tests stay green" — would have
promoted this: every seen done-test stayed green while unseen work lost 37.5
points. The mirrored candidate (train up, held-out improves too) exits 0; a
promotion record with no cost envelope, a candidate record that silently drops
a retained negative, and a run with no held-out set at all each exit 1 naming
its rule. The full planted estate decides as declared:

```
$ python3 scripts/held_out_nonregression.py selftest
ok   cost_overrun: verdict=refuse (expected refuse)
ok   good: verdict=promote (expected promote)
ok   heldout_regression: verdict=refuse (expected refuse)
ok   hidden_negative: verdict=refuse (expected refuse)
ok   missing_budget: verdict=refuse (expected refuse)
ok   seen_only: verdict=refuse (expected refuse)
6/6 fixture cases decide as declared
```

The RED this gate exists to catch is named in the fixture, not in prose:
`seen_only` — promotion decided on the seen set alone, overfitting invisible
to the gate. Noise band is `max(0.02, 2 × 1.4826·MAD)` over the sealed
held-out rates in `history.jsonl`, the same RobustMADZ primitive
`rig-realign` uses for week-over-week movement, finally guarding promotions.
