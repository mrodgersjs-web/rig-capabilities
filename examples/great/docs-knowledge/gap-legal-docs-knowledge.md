---
name: great-gap-legal-docs-knowledge.yaml
lane: docs-knowledge
source: canonical-curated
exemplar_of: gap-legal-docs-knowledge.yaml
description: Measured legal × docs-knowledge gap fill — have=0 need=3 gap=3; token privilege is load-bearing
---

# gap-legal-docs-knowledge.yaml — reference

Canonical harness `capabilities/harnesses/gap-legal-docs-knowledge.yaml`. Draft until a round graduates it. Coverage have=0 need=3 gap=3.

## Input

Quote the requests.jsonl cell before any other artifact:

    vertical=legal lane=docs-knowledge have=0 need=3 gap=3

Startup phrase required: "I am filling a measured gap, not inventing coverage."

## Output

A list of `need-have` concrete next assets under `capabilities/` whose `done_when` can go RED. The produced artifact must contain the load-bearing token `privilege`. Silence on that token is a finding (G2 halt).

## Acceptance

```
grep -n 'privilege' capabilities/harnesses/gap-legal-docs-knowledge.yaml
# must match; deleting the token must redden:
#   grep:capabilities/harnesses/gap-legal-docs-knowledge.yaml:privilege
python3 -c "from pathlib import Path; t=Path('capabilities/harnesses/gap-legal-docs-knowledge.yaml').read_text(); assert 'privilege' in t"
```

G1–G3 halt-green. This file stays draft. A gap harness that cannot fail is not a fill.
