---
name: great-gap-pe_cfo-data-analytics.yaml
lane: data-analytics
source: canonical-curated
exemplar_of: gap-pe_cfo-data-analytics.yaml
description: Measured pe_cfo × data-analytics gap fill — have=0 need=3 gap=3; token Working-capital is load-bearing
---

# gap-pe_cfo-data-analytics.yaml — reference

Canonical harness `capabilities/harnesses/gap-pe_cfo-data-analytics.yaml`. Draft until a round graduates it. Coverage have=0 need=3 gap=3.

## Input

Quote the requests.jsonl cell before any other artifact:

    vertical=pe_cfo lane=data-analytics have=0 need=3 gap=3

Startup phrase required: "I am filling a measured gap, not inventing coverage."

## Output

A list of `need-have` concrete next assets under `capabilities/` whose `done_when` can go RED. The produced artifact must contain the load-bearing token `Working-capital`. Silence on that token is a finding (G2 halt).

## Acceptance

```
grep -n 'Working-capital' capabilities/harnesses/gap-pe_cfo-data-analytics.yaml
# must match; deleting the token must redden:
#   grep:capabilities/harnesses/gap-pe_cfo-data-analytics.yaml:Working-capital
python3 -c "from pathlib import Path; t=Path('capabilities/harnesses/gap-pe_cfo-data-analytics.yaml').read_text(); assert 'Working-capital' in t"
```

G1–G3 halt-green. This file stays draft. A gap harness that cannot fail is not a fill.
