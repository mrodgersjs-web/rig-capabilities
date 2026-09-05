---
name: great-gap-dental-revenue-gtm.yaml
lane: revenue-gtm
source: canonical-curated
exemplar_of: gap-dental-revenue-gtm.yaml
description: Measured dental × revenue-gtm gap fill — have=1 need=3 gap=2; token claim-denial is load-bearing
---

# gap-dental-revenue-gtm.yaml — reference

Canonical harness `capabilities/harnesses/gap-dental-revenue-gtm.yaml`. Draft until a round graduates it. Coverage have=1 need=3 gap=2.

## Input

Quote the requests.jsonl cell before any other artifact:

    vertical=dental lane=revenue-gtm have=1 need=3 gap=2

Startup phrase required: "I am filling a measured gap, not inventing coverage."

## Output

A list of `need-have` concrete next assets under `capabilities/` whose `done_when` can go RED. The produced artifact must contain the load-bearing token `claim-denial`. Silence on that token is a finding (G2 halt).

## Acceptance

```
grep -n 'claim-denial' capabilities/harnesses/gap-dental-revenue-gtm.yaml
# must match; deleting the token must redden:
#   grep:capabilities/harnesses/gap-dental-revenue-gtm.yaml:claim-denial
python3 -c "from pathlib import Path; t=Path('capabilities/harnesses/gap-dental-revenue-gtm.yaml').read_text(); assert 'claim-denial' in t"
```

G1–G3 halt-green. This file stays draft. A gap harness that cannot fail is not a fill.
