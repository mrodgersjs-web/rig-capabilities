# What good looks like: a paired run, and the negatives that stay in the ledger

Source asset: `capabilities/harnesses/mh-01-skill-genesis-session.yaml`
(gates 3.5 and 3.6, both halt-tier)
Adjudicator: `rig_capabilities/paired_runs.py` — `check <ledger> [--baseline <ledger>]`,
opens every file read-only and never rewrites the ledger.
Attribution: Discover AI videos `TA5QzGTQU_U`, `5S9NemR7Fwo`; arXiv 2608.11888,
arXiv 2608.13951, arXiv 2602.12670; repos `benchflow-ai/skillsbench`,
`HKUDS/HELIX`. Outputs below are real runs of the fixtures in
`examples/fixtures/paired-runs/`.

A genesis session that reports "the skill improved correctness" has claimed a
causal fact. Gate 3.5 makes it pay for the claim in a ledger: two runs of the
same task under exactly one differing config key, with the config hashes and
both cost axes written down. Gate 3.6 then refuses to let the ledger be
forgetful: a negative that was recorded and is now gone is a finding.

## 1. A pair that earns its claim

```
$ python3 rig_capabilities/paired_runs.py check examples/fixtures/paired-runs/valid_pair.jsonl
PAIR P-77 (T-42): correctness false->true delta=improved | tokens 48200->51800 x1.07 | wall_ms 185000->172000 x0.93 | differs_in=skill   rc=0
```

Four things had to be true for that line to be legal: the task id is shared, the
config hashes differ, exactly one config key differs, and `differs_in` names
that key. Tokens went up 7% and wall time went down — the checker reports the
multipliers rather than grading them silently, because the reader is allowed to
decide whether +7% tokens for a correctness flip is worth it.

## 2. The four ways a pair is illegal

```
$ python3 rig_capabilities/paired_runs.py check .../two_variables.jsonl
PAIRED-RUNS RED: ledger:2: two_variables_differ: pair 'P-21' varies model, skill — a pair with >1 free
variable proves nothing about any single change and is rejected outright                          rc=1

$ python3 rig_capabilities/paired_runs.py check .../same_config.jsonl
PAIRED-RUNS RED: ledger:2: identical_config: pair 'P-33' ran the same configuration twice and calls
the second run an improvement                                                                     rc=1

$ python3 rig_capabilities/paired_runs.py check .../cost_regression.jsonl
PAIR P-55 (T-55): correctness true->true delta=unchanged | tokens 40000->100000 x2.50 | ...        rc=1
```

The last one is the rule that catches honest people. Same correctness, 2.5x the
tokens: the ledger calls it a **cost regression** even though the run passed. A
skill that only ever gets graded on pass/fail will be paid for in tokens forever,
and "it still works" will keep being the argument. Two variables is worse than
zero information — it is information with a false attribution attached, so it is
rejected outright rather than discounted.

Also red: `config_hash_mismatch` (the declared hash is not the canonical hash of
the config as written — checked by recomputation, not by trust),
`differs_in_mismatch` (claims `skill`, configs actually differ in `model`),
`missing_cost_delta` (a claimed improvement with no numeric tokens/wall pair).

## 3. Retained negatives (gate 3.6)

```
$ python3 rig_capabilities/paired_runs.py check ledger_dropped_negative.jsonl --baseline baseline_ledger.jsonl
... retained_negative_missing ...                                                                   rc=1
$ python3 rig_capabilities/paired_runs.py check ledger_keeps_negative.jsonl --baseline baseline_ledger.jsonl
                                                                                                    rc=0
```

An id-set diff against a prior ledger, not a count. A session that "cleaned up"
its ledger by deleting the rows it failed to fix is the same act as a test suite
that deletes failing tests, and the archive-diff makes it visible.

## 4. Falsifiability

`tests/test_paired_runs.py` (14 tests) covers each verdict class, both CLI exit
codes, the tampered hash, the cost multiplier, and one test that asserts the
ledger's bytes are untouched after a check. Planting the diff-count guard
(`if len(diff) > 1:` → `if False:`) turns the suite RED:

```
FAIL: test_cli_red_exit_one
```

One honesty note about the fixture corpus: `two_variables.jsonl` carries a second
independent violation (`differs_in_mismatch`), so disabling only the >1-variable
rule still exits 1 on that file. The rule is isolated at unit level, not by that
fixture alone. Anyone tightening the corpus should split it.
