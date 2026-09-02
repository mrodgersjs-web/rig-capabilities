---
name: great-iqrsqpi-v10
lane: agent-engineering
source: canonical-curated
exemplar_of: iqrsqpi-v10
description: Reference exemplar — the IQRSQPI v10 stdlib runtime deciding stage order, artifacts, sources, and Builder≠Checker from real command output, including the refusal that proves the artifact law works
---

# iqrsqpi-v10 — reference

Canonical asset `iqrsqpi-v10` (skill). Path: `capabilities/skills/iqrsqpi-v10`.

> The seven canonical stages validated by code: `normalize_stage` collapses every
> harness vocabulary onto the canonical order, `run_pass` refuses a pass whose
> verifier is its generator, refuses any reached stage whose required artifact is
> not on disk, and refuses any number stated without a source.

All transcripts below are real command output from this repo, 2026-09-01.

## The alias law, in one assertion (the skill's own done-test)

```console
$ python3 -c "from rig_capabilities.iqrsqpi_v10 import normalize_stage as n; assert n('I')=='Intent' and n('I2')=='Integrate' and n('I5')=='Integrate' and n('Q2')=='Quality'"
$ echo $?
0
```

`I` → Intent while `I2`/`I5` → Integrate: whole-token exact lookup, so a
longest alias is never swallowed by its own prefix. An unknown token names
itself as unknown rather than landing on a guess:

```console
$ python3 -c "from rig_capabilities.iqrsqpi_v10 import normalize_stage; normalize_stage('Q3')"
StageError: unknown_stage_token:'Q3'
```

## Builder ≠ Checker, in one call

```python
from rig_capabilities.iqrsqpi_v10 import run_pass
from rig_capabilities.catalog import Repo
run_pass(Repo('.'), 'fable-2031', ['I', 'Q'], verifier='x', generator='x')
```

```console
StageError: verifier_is_generator
```

The entity that walked the stages holds no authority to certify them. There is
no flag that relaxes this.

## The artifact law refusing a real walk (the honest live state)

The live walk `.context/iqrsqpi/fable-2031/` records only `00-intake`. Asking
the runtime to bless two reached stages:

```python
run_pass(Repo('.'), 'fable-2031', ['I', 'Q'],
         verifier='gpt-56', generator='claude-fable-5-1')
```

```console
StageError: artifact_missing:01-reality
```


Question demands the reality document; it does not exist; the pass does not
exist. The fix is to do the Research and record `01-reality` — never to touch
up the error.

## The hermetic gate and its plant-failure proof

```console
$ ./bin/rig-capabilities certify --only stage_order ; echo $?
{"gates": {"stage_order": {"ok": true, ...}}, "verdict": true}
0
$ ./bin/rig-capabilities self-test --only stage_order   # green -> planted RED -> restored green
```

The gate reads one committed fixture (`tests/fixtures/fable2031/iqrsqpi-run.json`,
stages written in the two vocabularies real harnesses use: `I, question, R,
synthesize, …`) and nothing else — law L1. The plant reorders two fixture stages
and the gate must go RED; a green that cannot fail is theater.

**Why this is the exemplar:** every load-bearing sentence in the skill maps to
a command above with captured output; the runtime's refusals are shown firing
on real repo state, and the one honest limitation (the partial live walk) is
reported as the law working rather than papered over.
