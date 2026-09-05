---
name: great-gap-construction-docs-knowledge.yaml
lane: docs-knowledge
source: canonical-curated
exemplar_of: gap-construction-docs-knowledge.yaml
description: Measured construction × docs-knowledge gap fill — have=2 need=3 gap=1; token OSHA is load-bearing
---

# gap-construction-docs-knowledge.yaml — reference

Canonical harness `capabilities/harnesses/gap-construction-docs-knowledge.yaml`. Draft until a round graduates it. Coverage have=2 need=3 gap=1.

## Input

Quote the requests.jsonl cell before any other artifact:

    vertical=construction lane=docs-knowledge have=2 need=3 gap=1

Startup phrase required: "I am filling a measured gap, not inventing coverage."

## Output

A list of `need-have` concrete next assets under `capabilities/` whose `done_when` can go RED. The produced artifact must contain the load-bearing token `OSHA`. Silence on that token is a finding (G2 halt).

## Acceptance

```
grep -n 'OSHA' capabilities/harnesses/gap-construction-docs-knowledge.yaml
# must match; deleting the token must redden:
#   grep:capabilities/harnesses/gap-construction-docs-knowledge.yaml:OSHA
python3 -c "from pathlib import Path; t=Path('capabilities/harnesses/gap-construction-docs-knowledge.yaml').read_text(); assert 'OSHA' in t"
```

G1–G3 halt-green. This file stays draft. A gap harness that cannot fail is not a fill.
