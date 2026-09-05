---
name: great-hd-02-icp-research-yaml
lane: revenue-gtm
exemplar_of: hD-02-icp-research.yaml
description: "Reference exemplar — a falsifiable ICP derived from won, lost, and churned accounts with scripted firmographics, measured outcome deltas, exclusions, and kill criteria."
---

# hD-02 ICP research — multi-site dental groups

## Input

Test whether US dental groups with 5–25 locations, a centralized operations lead, and fragmented scheduling systems close more reliably than smaller practices. The decision is whether this segment receives the next outbound allocation.

## Output

`artifacts/icp/dental-groups-2026-09/` contains the decision question, three-source inventory, a 64-account cohort spanning won/lost/churned outcomes, scripted `firmographics.csv`, quote-anchored trigger evidence, `anti_icp.md`, per-attribute win-rate deltas, a runnable Twenty segment query, refutation verdicts, and `icp.md` with evidence anchors and measurable kill criteria.

## Acceptance

```console
$ curl -sf http://localhost:3000/healthz
# expected: exit 0 before cohort work
$ python3 scripts/extract_firmographics.py --cohort artifacts/icp/dental-groups-2026-09/cohort.json --out artifacts/icp/dental-groups-2026-09/firmographics.csv
# expected: exit 0 with industry, size band, geography, and tech-stack columns
$ jq -e '[.accounts[].outcome | select(. != null and . != "")] | unique | length >= 2' artifacts/icp/dental-groups-2026-09/cohort.json
# expected: true; the cohort is not winners-only
$ ./bin/rig-capabilities goal-spec --stem hD-02-icp-research
# expected: verdict OK
```

Every top ICP attribute cites a CRM query, file line, or source URL and shows its won-versus-lost delta. At least two anti-ICP exclusions carry churn, win-rate, or sales-cycle evidence. The independent pass marks each of the top three attributes confirmed, weakened, or rejected; the final verdict is `validated` only if the kill criteria remain unfired.