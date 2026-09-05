---
name: great-mh-02-harness-forge-session
lane: agent-engineering
source: canonical-curated
exemplar_of: mh-02-harness-forge-session
description: Reference exemplar — the forge harness declaring what it may change (mutable_classes), sealing what it is (sha256 over a typed slot vector), and refusing to let an inner-loop session rewrite its own bytes, all proven RED as well as GREEN on real command output
---

# mh-02-harness-forge-session — reference

Canonical asset `mh-02-harness-forge-session` (harness). Path:
`capabilities/harnesses/mh-02-harness-forge-session.yaml`.

> A forge that can rewrite any harness, including its own, has no learnable
> surface — it has drift. So MH-02 declares the surface before the run
> (`mutable_classes`, with a `never` scope for the machinery it is scored
> against), seals its configuration as `sha256` over a typed slot vector so two
> runs of the same YAML can be told apart, and freezes its own bytes for any
> session that declares `loop: inner`. Every one of those three is a command
> that goes RED, not a paragraph.

All transcripts below are real command output from this repo, 2026-09-02, on
harness sha256 `41251057a729…` (the file's own `start=` / `end=` hashes below are
its first 12 hex chars, so the transcript is pinned to a byte state).

## The three checks are declared once, in the harness

```console
$ grep -n "^    config_identity:\|^    surface_admission:\|^    inner_loop_byte_freeze:" \
    capabilities/harnesses/mh-02-harness-forge-session.yaml | cut -c1-64
109:    config_identity: python3 -c 'import sys,hashlib;sys.path.insert(0,…
110:    surface_admission: python3 -c 'import sys;A=sys.argv;Y=A[1];P=list(A…
111:    inner_loop_byte_freeze: python3 -c 'import sys,os,hashlib;A=sys.argv;…
```

`mutable_surface.checks` is the single source of truth. The front-matter
`done_when` fixtures and gate 5.1-5.3 proofs do not copy the logic — they
extract it (`grep -m1 '^    <name>:' … | cut -f2- -d:`) and run it, so the
declaration cannot rot into decoration.

## 1. Configuration identity — the hash identifies the run

`config.slots` is a vector of `slot:name|type|value`; the sealed value is
`sha256` over those lines in declaration order, newline-terminated.

```console
$ <checks.config_identity> capabilities/harnesses/mh-02-harness-forge-session.yaml
CONFIG_IDENTITY slots=14 computed=3248135d7a1dcc74 sealed=3248135d7a1dcc74 verdict=PASS
rc=0

$ # one slot value edited (gate_count_band 8-15 -> 8-20), sealed hash left alone
$ <checks.config_identity> <edited copy>
CONFIG_IDENTITY slots=14 computed=aa0eef2b2f8db372 sealed=3248135d7a1dcc74 verdict=RED slot vector and sealed hash differ
rc=1
```

The RED case is the point. A harness that changed a knob without re-sealing is
now two different things wearing one name, and the check says so before anything
is scored. `fixtures.config_block` asserts `rc=1` and `fixtures.config_pass`
asserts `rc=0`, so an always-green seal cannot survive the done-test.

## 2. Surface admission — rejected before it is scored

`mutable_classes` names exact paths with a scope (`inner` / `outer` / `never`).
Longest declared match wins, which is what makes `capabilities/harnesses/`
(the artifact a forge session may rewrite) and
`capabilities/harnesses/mh-02-harness-forge-session.yaml` (its own bytes,
`outer`, Gate-D) different things.

```console
$ <checks.surface_admission> <yaml> capabilities/harnesses/hn-01-forged-session.yaml .rig/forge/gate-5.3.txt
SURFACE_ADMISSION loop=inner map=[('capabilities/harnesses/hn-01-forged-session.yaml', 'inner'), ('.rig/forge/gate-5.3.txt', 'inner')] rejected=[]
rc=0

$ <checks.surface_admission> <yaml> <own yaml> rig_capabilities/rounds.py scripts/compile_harnesses.py
SURFACE_ADMISSION loop=inner map=[('capabilities/harnesses/mh-02-harness-forge-session.yaml', 'outer'), ('rig_capabilities/rounds.py', 'never'), ('scripts/compile_harnesses.py', 'never')] rejected=[('capabilities/harnesses/mh-02-harness-forge-session.yaml', 'outer'), ('rig_capabilities/rounds.py', 'never'), ('scripts/compile_harnesses.py', 'never')]
rc=1
```

The same proposal under `loop: outer` is admitted for the `outer` class — which
is what proves the gate reads a real declaration rather than refusing
everything — while `never` still bites:

```console
$ <checks.surface_admission> <loop:outer copy> capabilities/harnesses/mh-02-harness-forge-session.yaml
SURFACE_ADMISSION loop=outer map=[('capabilities/harnesses/mh-02-harness-forge-session.yaml', 'outer')] rejected=[]
rc=0

$ <checks.surface_admission> <loop:outer copy> rig_capabilities/rounds.py
SURFACE_ADMISSION loop=outer map=[('rig_capabilities/rounds.py', 'never')] rejected=[('rig_capabilities/rounds.py', 'never')]
rc=1
```

## 3. Inner-loop byte freeze — the session cannot move its own ground

`record_before_first_write` pins `sha256sum` of the harness at start;
`inner_loop_byte_freeze` re-derives it at close. An undeclared loop is treated
as `inner`, so the freeze is fail-closed.

```console
$ <checks.inner_loop_byte_freeze> <untouched copy> <state dir>
BYTE_FREEZE loop=inner start=41251057a729 end=41251057a729 verdict=PASS
rc=0

$ <checks.inner_loop_byte_freeze> <copy the session edited> <state dir>
BYTE_FREEZE loop=inner start=41251057a729 end=b3ee1bef629f verdict=RED inner-loop session changed its own harness bytes
rc=1

$ # the loop declaration itself deleted -> defaults to inner, and bites anyway
$ <checks.inner_loop_byte_freeze> <copy with loop line deleted> <state dir>
BYTE_FREEZE loop=inner start=41251057a729 end=7bcddfcb21fa verdict=RED inner-loop session changed its own harness bytes
rc=1
```

The planted edit is a *valid* YAML change (`pattern_cadence 5 -> 9`), not
appended garbage: the file still parses, which is exactly why a byte hash is the
right guard. Editing `loop: inner` to `loop: outer` to escape the freeze changes
bytes too — that is the third transcript.

## The forge passes its own gates

MH-02 is a harness for forging harnesses, so it is scored by them:

```console
$ python3 scripts/compile_harnesses.py compile capabilities/harnesses/mh-02-harness-forge-session.yaml
OK  mh-02-harness-forge-session.yaml         gates= 20 blocking= 20 weighted= 0 no_proof=0

compiled 1/1 harness specs -> .../out/harness-goalspecs (gates: 20, without-proof: 0, skipped: 0)

$ ./bin/rig-capabilities goal-spec --stem mh-02-harness-forge-session
verdict OK | stale False | source_sha 41251057a729b9b2 == compiled 41251057a729b9b2
id GL-MH-02-HARNESS-FORGE-SESSION | gates 20 | approval_required True | anti_patterns 5
new gate ids present: ['0.5', '5.1', '5.2', '5.3']
```

15 capability gates (band 8-15), 5 identity gates (band 3-5), tier partition
green with `stop_gates: ["5.2","5.3"]` — the two boundaries a session may not
cross alone, which is why the served spec now reports
`approval_required: true`.

## What is honest about the shape, not hidden

- **The compiler drops the declaration.** `scripts/compile_harnesses.py`
  carries whitelisted keys plus gate `proof` strings into
  `out/harness-goalspecs/`; `mutable_surface` is not whitelisted
  (`_meta carries mutable_surface: False`). Enforcement survives because every
  gate command re-parses this file. Widening `mutable_classes` is therefore a
  change to machinery, not to a readable field — hence Gate-D.
- **Gate 4.2 flags gate 4.2.** The theater scan hits requirement `4.2` because
  that requirement *quotes* the banned adjectives it defines. Present at HEAD
  before this change; left alone rather than quietly reworded.
- **Nothing here depends on an unverified link.** Every arXiv id and repo slug
  in `mutable_surface.provenance` is present in the link verdict log with
  `exists: true`; two dossier links that failed verification are recorded as a
  limitation without repeating their identifiers.
