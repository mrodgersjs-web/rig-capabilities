---
name: great-gap-manufacturing-infra-ops.yaml
lane: infra-ops
source: canonical-curated
exemplar_of: gap-manufacturing-infra-ops.yaml
description: Measured manufacturing × infra-ops gap fill — have=0 need=3 gap=3; token genealogy is load-bearing
---

# gap-manufacturing-infra-ops.yaml — reference

Canonical harness `capabilities/harnesses/gap-manufacturing-infra-ops.yaml`. Draft until a round graduates it. Coverage have=0 need=3 gap=3.

## Input

Quote the requests.jsonl cell before any other artifact:

    vertical=manufacturing lane=infra-ops have=0 need=3 gap=3

Startup phrase required: "I am filling a measured gap, not inventing coverage."

## Output

A list of `need-have` concrete next assets under `capabilities/` whose `done_when` can go RED. The produced artifact must contain the load-bearing token `genealogy`. Silence on that token is a finding (G2 halt).

## Acceptance

```
grep -n 'genealogy' capabilities/harnesses/gap-manufacturing-infra-ops.yaml
# must match; deleting the token must redden:
#   grep:capabilities/harnesses/gap-manufacturing-infra-ops.yaml:genealogy
python3 -c "from pathlib import Path; t=Path('capabilities/harnesses/gap-manufacturing-infra-ops.yaml').read_text(); assert 'genealogy' in t"
```

G1–G3 halt-green. This file stays draft. A gap harness that cannot fail is not a fill.
