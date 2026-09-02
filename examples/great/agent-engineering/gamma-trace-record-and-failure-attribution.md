---
name: great-gamma-trace-record-and-failure-attribution
lane: agent-engineering
source: canonical-curated
exemplar_of: gamma-trace-record-and-failure-attribution
description: Reference exemplar — the gamma validator GREEN on a complete trace with an evidenced one-class attribution, RED (exit 2) on each of the four planted failure classes, and loudly honest on the legitimate UNATTRIBUTED state
---

# gamma-trace-record-and-failure-attribution — reference

Canonical asset `gamma-trace-record-and-failure-attribution` (skill). Path:
`capabilities/skills/gamma-trace-record-and-failure-attribution`.

> Every consequential step appends a seven-field γ row (believed state, skills
> delivered, action, observation, proposed change, checker verdict, resulting
> state) plus one terminal outcome per attempt; a RED attempt is attributed to
> exactly one of four fixed components citing its own γ rows; attribution
> without evidence is UNATTRIBUTED — never guessed. `validate_gamma.py`
> enforces every clause; the planted fixtures are permanent regression cases.

All transcripts below are real command output from this repo, 2026-09-02,
run with `cwd = repo root` (exactly how `done_tests.py` executes `cmd:`).
`V=capabilities/skills/gamma-trace-record-and-failure-attribution`.

## GREEN — a complete trace with an evidenced attribution

`fixtures/gamma_valid.jsonl`: 5 step rows across 2 attempts — r-17 GREEN, r-18
RED — plus the single attribution row for r-18. Note `g-18-1` carries `e_t: []`
(no card for the unknown scheduler API) and `g-18-2` carries the blanket-retry
card against a deterministic schema error; the attribution names
`skill_missing_or_wrong`, cites exactly those two rows, and exonerates W and C
*by their rows*:

```console
$ python3 $V/validate_gamma.py $V/fixtures/gamma_valid.jsonl --genesis $V/fixtures/genesis_valid.md
SUMMARY gamma_rows=5 attempts=2 red=1 unattributed=0 violations=0
$ echo $?
0
```

## RED 1 — a seven-field row with a hole

Same trace, `o_t: null` on `g-18-1`. A row missing the observation is not a
lighter record; it deletes the only link between action and proposal, so the
file is refused by line number:

```console
$ python3 $V/validate_gamma.py $V/fixtures/gamma_missing_field.jsonl
VIOLATION .../fixtures/gamma_missing_field.jsonl:2: step g-18-1: field o_t missing/null
SUMMARY gamma_rows=2 attempts=1 red=1 unattributed=0 violations=1
$ echo $?
2
```

## RED 2/3 — two classes and zero classes

The same failed run attributed to `skill_missing_or_wrong` **and**
`verifier_missed`, then to nothing but "it just failed, basically":

```console
$ python3 $V/validate_gamma.py $V/fixtures/gamma_attr_two_classes.jsonl
VIOLATION .../fixtures/gamma_attr_two_classes.jsonl:4: attribution_class_count: got 2 classes ['skill_missing_or_wrong', 'verifier_missed'], exactly one required
SUMMARY gamma_rows=2 attempts=1 red=1 unattributed=0 violations=1
$ echo $?
2

$ python3 $V/validate_gamma.py $V/fixtures/gamma_attr_zero_classes.jsonl
VIOLATION .../fixtures/gamma_attr_zero_classes.jsonl:4: attribution_class_count: got 0 classes [], exactly one required
SUMMARY gamma_rows=2 attempts=1 red=1 unattributed=0 violations=1
$ echo $?
2
```

Two classes is "rewrite everything" wearing a class label; zero is the
unattributed failure this skill exists to make illegal. Both die at exit 2.

## RED 4 — a guess dressed as an attribution

A named class citing **no** rows ("felt like the retrieval policy was the
problem"). This is the mechanical teeth of the never-guess rule: a class
without evidence is rejected with its own remedy named:

```console
$ python3 $V/validate_gamma.py $V/fixtures/gamma_attr_without_evidence.jsonl
VIOLATION .../fixtures/gamma_attr_without_evidence.jsonl:4: attribution_without_evidence: class 'retrieval_policy_inadequate' cites no gamma rows — attribution without evidence must be recorded as UNATTRIBUTED, never guessed
SUMMARY gamma_rows=2 attempts=1 red=1 unattributed=0 violations=1
$ echo $?
2
```

## GREEN — the honest UNATTRIBUTED state (exit 0, no cover-up)

`fixtures/gamma_unattributed_honest.jsonl`: all four components exonerated by
the rows, so the truth is "the trace does not discriminate a cause". Legal —
cites empty, evidence names the gap — and echoed so nobody mistakes the green
exit for an answer:

```console
$ python3 $V/validate_gamma.py $V/fixtures/gamma_unattributed_honest.jsonl
SUMMARY gamma_rows=2 attempts=1 red=1 unattributed=1 violations=0
UNATTRIBUTED run r-19: rows are internally coherent: delivered card matches the task (E not implicated), state stayed aligned with observations (W not implicated), the delivered card is the one the policy should pick (rho not implicated), and the checker rejected correctly (C not implicated). Nothing in g-19-1..g-19-2 discriminates a cause; naming one would be a guess.  (honest gap — improvement work goes to the evidence, not to a guess)
$ echo $?
0
```

## RED 5 — a genesis skill that cannot cite its motivating rows

`fixtures/genesis_missing_provenance.md` is a plausible migration procedure
with a `source:` but no `gamma_provenance:` — exactly the mh-01 failure mode
(genesis from a declared need). Refused even though the prose is good:

```console
$ python3 $V/validate_gamma.py $V/fixtures/gamma_valid.jsonl --genesis $V/fixtures/genesis_missing_provenance.md
VIOLATION .../fixtures/genesis_missing_provenance.md: genesis_missing_gamma_provenance: `gamma_provenance:` must cite the gamma rows that motivated this skill
SUMMARY gamma_rows=5 attempts=2 red=1 unattributed=0 violations=1
$ echo $?
2
```

The provenanced sibling (`fixtures/genesis_valid.md`,
`gamma_provenance: [g-18-1, g-18-2]`) exits 0 — and its citations are
cross-checked against the trace: a dangling row-id is
`genesis_provenance_dangling`.

**Why this is the exemplar:** every clause of the law has a violation code and
a planted fixture that proves the gate goes RED — field holes, class-count
both directions, evidence-less guesses, provenance-less genesis — while the
one state prose-only skills never admit (UNATTRIBUTED) passes, visibly, so the
skill is honest about the difference between *no answer* and *a fake answer*.
