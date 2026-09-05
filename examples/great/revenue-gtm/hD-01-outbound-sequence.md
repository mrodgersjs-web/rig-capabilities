---
name: great-hd-01-outbound-sequence-yaml
lane: revenue-gtm
exemplar_of: hD-01-outbound-sequence.yaml
description: "Reference exemplar — a provenance-bound outbound batch deduped and suppressed before personalized copy, with an 8-of-8 safety queue that remains inert without Gate-D."
---

# hD-01 outbound sequence — dental operations batch

## Input

Build a draft-only three-step email/LinkedIn sequence for 42 dental operations leaders from an approved conference export. Use CRM facts or public conference facts for personalization. Sending and sequence enrollment are out of scope without `APPROVE dental-ops-2026-09`.

## Output

`artifacts/outbound/dental-ops-2026-09/` contains source provenance, `raw.csv`, CRM-deduped recipients, suppression counts by rule, bounded ICP scores, fact-to-source personalization records, cadence config, claim anchors, per-recipient safety results, inert queue metadata, and a sealed manifest. Every removal carries a reason code.

## Acceptance

```console
$ python3 scripts/dedupe_crm.py --list artifacts/outbound/dental-ops-2026-09/raw.csv --crm http://localhost:3000 --out artifacts/outbound/dental-ops-2026-09/deduped.csv
# expected: report records removed_count and the 10-row spot check has zero collisions
$ python3 scripts/validate_sequence.py artifacts/outbound/dental-ops-2026-09/sequence.yaml
# expected: exit 0; cadence includes delays, channels, and stop-on-reply
$ jq -s -e 'length > 0 and all(.[]; .passed >= 8)' artifacts/outbound/dental-ops-2026-09/safety_gate.jsonl
# expected: 0 for the final queue
$ shasum -a 256 -c artifacts/outbound/dental-ops-2026-09/manifest.sha256
# expected: all queue inputs report OK
```

`gate_d.log` is absent and queue `arm` is `false`, so the correct verdict is `drafted`, not sent. Each retained recipient has provenance, dedupe, suppression, grounded personalization, and all eight safety checks; `./bin/rig-capabilities goal-spec --stem hD-01-outbound-sequence` returns verdict OK.