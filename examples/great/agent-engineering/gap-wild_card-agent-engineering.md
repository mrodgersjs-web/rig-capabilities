---
name: great-gap-wild_card-agent-engineering.yaml
lane: agent-engineering
source: canonical-curated
exemplar_of: gap-wild_card-agent-engineering.yaml
description: Measured wild_card × agent-engineering gap fill — have=0 need=3 gap=3; token prove it wrong is load-bearing
---

# gap-wild_card-agent-engineering.yaml — reference

Canonical harness `capabilities/harnesses/gap-wild_card-agent-engineering.yaml`. Draft until a round graduates it. Coverage have=0 need=3 gap=3.

## Input

Quote the requests.jsonl cell before any other artifact:

    vertical=wild_card lane=agent-engineering have=0 need=3 gap=3

Startup phrase required: "I am filling a measured gap, not inventing coverage."

## Output

A list of `need-have` concrete next assets under `capabilities/` whose `done_when` can go RED. The produced artifact must contain the load-bearing token `prove it wrong`. Silence on that token is a finding (G2 halt).

## Acceptance

```
grep -n 'prove it wrong' capabilities/harnesses/gap-wild_card-agent-engineering.yaml
# must match; deleting the token must redden:
#   grep:capabilities/harnesses/gap-wild_card-agent-engineering.yaml:prove it wrong
python3 -c "from pathlib import Path; t=Path('capabilities/harnesses/gap-wild_card-agent-engineering.yaml').read_text(); assert 'prove it wrong' in t"
```

G1–G3 halt-green. This file stays draft. A gap harness that cannot fail is not a fill.
