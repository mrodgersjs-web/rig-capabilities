---
name: great-hB-10-lead-magnet-session-yaml
lane: revenue-gtm
exemplar_of: hB-10-lead-magnet-session.yaml
description: Reference exemplar for a useful-in-ten-minutes lead magnet with reusable machinery, a low-friction gate, hash-identical delivery, nurture, and tracking.
---

# hB-10-lead-magnet-session.yaml — great example

## Input

Create a checklist/template for one named job-to-be-done, promising a result achievable in ten minutes. The asset contains fillable fields, decision rules, and a worked example rather than repackaged prose. `jtbd.yaml` names the nurture sequence; the opt-in gate and delivery events are declared before rendering.

## Output

The completed Markdown asset renders to a branded PDF below 10 MB with cover, page numbers, and footer CTA. The gate asks at most three fields, says what will arrive and when, links privacy terms, and delivers the exact sealed file to a test address. Nurture and ESP tag mappings agree.

```console
$ python3 scripts/promise_map.py "$SESS/title.txt" "$SESS/asset.md"
# expected: every title-promise term maps to a delivered asset section

$ python3 scripts/form_audit.py "$SESS/gate.html" --max-fields 3
# expected: exit 0 with clear labels and privacy link

$ python3 scripts/delivery_e2e.py --form "$SESS/gate.html" --expect-sha "$(sha256sum "$SESS/asset.pdf" | cut -d' ' -f1)"
# expected: submit, receive, and download succeed with hash-identical PDF
```

## Acceptance

- Utility scan finds at least three reusable fields, checklist items, formulas, or equivalent cells.
- Every section is specific enough to name a tool, number, step, example, or decision criterion.
- `magnet_view`, `magnet_submit`, and `magnet_download` fire in the probe.
- Asset, gate, delivery, and event evidence pass the packet checksum; no production send occurs.
