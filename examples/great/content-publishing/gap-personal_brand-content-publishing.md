---
name: great-gap-personal_brand-content-publishing.yaml
lane: content-publishing
source: canonical-curated
exemplar_of: gap-personal_brand-content-publishing.yaml
description: Measured personal_brand × content-publishing gap fill — have=0 need=3 gap=3; token Anti-thirst is load-bearing
---

# gap-personal_brand-content-publishing.yaml — reference

Canonical harness `capabilities/harnesses/gap-personal_brand-content-publishing.yaml`. Draft until a round graduates it. Coverage have=0 need=3 gap=3.

## Input

Quote the requests.jsonl cell before any other artifact:

    vertical=personal_brand lane=content-publishing have=0 need=3 gap=3

Startup phrase required: "I am filling a measured gap, not inventing coverage."

## Output

A list of `need-have` concrete next assets under `capabilities/` whose `done_when` can go RED. The produced artifact must contain the load-bearing token `Anti-thirst`. Silence on that token is a finding (G2 halt).

## Acceptance

```
grep -n 'Anti-thirst' capabilities/harnesses/gap-personal_brand-content-publishing.yaml
# must match; deleting the token must redden:
#   grep:capabilities/harnesses/gap-personal_brand-content-publishing.yaml:Anti-thirst
python3 -c "from pathlib import Path; t=Path('capabilities/harnesses/gap-personal_brand-content-publishing.yaml').read_text(); assert 'Anti-thirst' in t"
```

G1–G3 halt-green. This file stays draft. A gap harness that cannot fail is not a fill.
