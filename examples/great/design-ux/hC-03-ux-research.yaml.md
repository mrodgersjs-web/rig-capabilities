---
name: great-hC-03-ux-research-yaml
lane: design-ux
exemplar_of: hC-03-ux-research.yaml
description: Reference exemplar for ethical UX research with falsifiable hypotheses, consent, coded observations, saturation evidence, and recommendation traceability.
---

# hC-03-ux-research.yaml — great example

## Input

Study why qualified users abandon a configuration flow. Before contact, `plan.md` states the research question, three falsifiable hypotheses, method, analysis plan, and PII handling. `screener.md` defines inclusion/exclusion criteria and recruitment source. Every participant has a consent record before capture begins.

## Output

Each session file includes date, duration, modality, and timestamped raw notes. A declared `codebook.yaml` drives the coded-observation CSV. `themes.csv` connects each theme to at least two observations from at least two participants; the saturation table states new themes per session. Insights and recommendations form a complete traceability chain.

```console
$ test "$(find artifacts/uxr/config-dropoff/consent -type f | wc -l)" -eq "$(find artifacts/uxr/config-dropoff/sessions -type f | wc -l)"
# expected: one consent record per participant session

$ python3 -c "import csv; r=list(csv.DictReader(open('artifacts/uxr/config-dropoff/themes.csv'))); assert all(row['theme_id'] and row['observation_id'] for row in r)"
# expected: every theme row resolves to coded evidence

$ ./bin/rig-capabilities goal-spec --stem hC-03-ux-research
# expected: canonical research gates resolve before the readout is accepted
```

## Acceptance

- Research question, hypotheses, screener, consent, provenance, and PII policy are complete.
- Raw capture, coded observations, themes, and saturation counts remain distinct evidence layers.
- Each insight cites theme IDs and each recommendation cites an insight; orphan count is zero.
- Readout assigns confidence from evidence density, and persona/journey updates are delivered as a diff rather than overwrite.
