---
name: great-hB-12-case-study-session-yaml
lane: content-publishing
exemplar_of: hB-12-case-study-session.yaml
description: Reference exemplar for a customer-led case study with reproducible metrics, quote provenance, bounded claims, approval status, and number-parity twins.
---

# hB-12-case-study-session.yaml — great example

## Input

Draft a case study for a named buyer persona from an evidence locker containing the interview transcript, metric export, and before/after screenshots. The headline metric is defined in `metric.yaml` with its source and computation. Customer approval is recorded; otherwise the draft is name-scrubbed and visibly pending approval.

## Output

The narrative covers context, problem, failed alternatives, solution, outcome, and quote. Two quantified before/after pairs include timeframes. Every quotation resolves to a timestamp or email reference, and the headline computation can be rerun. A 150-word-or-less sales snippet preserves every number exactly.

```console
$ python3 scripts/verify_metric.py "$SESS/metric.yaml" "$SESS/evidence/"
# expected: exit 0 and proof/metric.json reproduces the headline result

$ python3 scripts/quote_provenance.py "$SESS/draft.md" "$SESS/evidence/"
# expected: every quoted sentence resolves; paraphrases remain unquoted

$ python3 scripts/number_parity.py "$SESS/draft.md" "$SESS/snippet.txt"
# expected: exit 0 with identical metrics in long and short formats
```

## Acceptance

- The evidence locker contains at least three hashed files.
- Required narrative sections, two before/after pairs, and persona criteria are present.
- Unsupported superlatives are absent; real names appear only with approval evidence.
- Draft, snippet, evidence hashes, metric proof, and approval status pass `sha256sum -c $SESS/proof/packet.sha256`.
