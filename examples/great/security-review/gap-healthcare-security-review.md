---
name: great-gap-healthcare-security-review.yaml
lane: security-review
source: canonical-curated
exemplar_of: gap-healthcare-security-review.yaml
description: Measured healthcare × security-review gap fill — have=0 need=3 gap=3; token PHI is load-bearing
---

# gap-healthcare-security-review.yaml — reference

Canonical harness `capabilities/harnesses/gap-healthcare-security-review.yaml`. Draft until a round graduates it. Coverage have=0 need=3 gap=3.

## Input

Quote the requests.jsonl cell before any other artifact:

    vertical=healthcare lane=security-review have=0 need=3 gap=3

Startup phrase required: "I am filling a measured gap, not inventing coverage."

## Output

A list of `need-have` concrete next assets under `capabilities/` whose `done_when` can go RED. The produced artifact must contain the load-bearing token `PHI`. Silence on that token is a finding (G2 halt).

## Acceptance

```
grep -n 'PHI' capabilities/harnesses/gap-healthcare-security-review.yaml
# must match; deleting the token must redden:
#   grep:capabilities/harnesses/gap-healthcare-security-review.yaml:PHI
python3 -c "from pathlib import Path; t=Path('capabilities/harnesses/gap-healthcare-security-review.yaml').read_text(); assert 'PHI' in t"
```

G1–G3 halt-green. This file stays draft. A gap harness that cannot fail is not a fill.
