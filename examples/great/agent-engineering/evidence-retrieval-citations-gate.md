---
name: great-evidence-retrieval-citations-gate
lane: agent-engineering
source: canonical-curated
exemplar_of: evidence-retrieval-citations-gate
description: Reference exemplar — BM25 retrieval beats a keyword baseline on a measured probe set (MRR 0.8333 > 0.7130), the citations gate resolves against an INDEPENDENT registry (a planted fabricated id goes RED), and the beats-baseline clause is plant-proven not theater
---

# evidence-retrieval-citations-gate — reference

Canonical asset `evidence-retrieval-citations-gate` (skill). Path:
`capabilities/skills/evidence-retrieval-citations-gate`.

> Retrieved evidence is ranked (BM25), measured against a keyword baseline, and
> every returned claim's citation resolves in an INDEPENDENT registry — or it is
> refused. `retrieve.py` is the whole checker; the planted fixtures are
> permanent regression cases.

## The benchmark beats the baseline (measured, not asserted)

```
$ retrieve.py benchmark --matrix fixtures/corpus.json --probes fixtures/probes.json --hit-floor 0.6
{ "probes": 9, "bm25_mrr": 0.8333, "keyword_mrr": 0.713, "hit_at_1": 0.6667, "hit_floor": 0.6 }
OK benchmark: bm25 MRR 0.8333 > keyword 0.7130, hit@1 0.667 >= 0.6   # exit 0
```

The probes are short and ambiguous on purpose — `"harness state memory"`,
`"skill task context"`, `"tool call model"` — terms shared across many rows, so
raw keyword overlap ties several docs and loses on tie-break while BM25's IDF
weighting lifts the gold row. On trivially-separable queries both scorers hit
1.0 and the benchmark correctly REFUSES (a tie does not prove the ranker earns
its complexity); that refusal is why the probe set is built to discriminate.

## The citations gate cannot be self-vouched

The load-bearing correction: the registry is loaded from a SEPARATE file, never
from the corpus under test.

```
$ retrieve.py gate --matrix fixtures/corpus.json --registry fixtures/registry.json --query "harness state memory"
OK gate: 5 result(s), every citation resolves in an independent registry of 62   # exit 0

$ retrieve.py gate --matrix fixtures/corpus_bogus_citation.json --registry fixtures/registry.json --query "lesson trigger mandated check"
UNRESOLVED_CITATION experience-lesson-records: arXiv:9999.99999-FABRICATED       # exit 2
```

If the registry were built from the matrix (the first draft), the fabricated id
would be added to the registry and pass. It does not, because the registry is
independent.

## The five done-test forms

| form | exit | why |
|------|------|-----|
| benchmark corpus.json / probes.json | 0 | BM25 beats keyword MRR, hit@1 >= floor |
| gate corpus.json / registry.json | 0 | every returned citation resolves |
| gate corpus_bogus_citation.json | 2 | a fabricated arXiv id is caught |
| gate corpus_no_citation.json | 2 | an uncited returned row is refused |
| benchmark probes_bad_gold.json | 2 | a probe whose gold is not in the corpus |

## Not theater

Out-of-band plant: replace `if not (bm25_mrr > kw_mrr):` with `if False:` and
run a tie probe (bm25 == kw). The benchmark printed OK and exited 0 — gate
blind. Restored byte-identical; the real benchmark still exits 0 legitimately
(0.8333 > 0.7130) and a tie again exits 2. Blind rc=0, restored rc=2.

## Provenance

Corpus = RIG's derived capability analysis (id-only citations, not creator
text). Registry = the 62 real source ids (18 video / 24 arXiv / 20 oss) of the
Discover AI increment.
