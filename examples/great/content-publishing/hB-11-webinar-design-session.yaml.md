---
name: great-hB-11-webinar-design-session-yaml
lane: content-publishing
exemplar_of: hB-11-webinar-design-session.yaml
description: Reference exemplar for a 45-minute webinar whose teaching promise, timed arc, interaction cadence, offer bridge, registration parity, and rehearsal are proven.
---

# hB-11-webinar-design-session.yaml — great example

## Input

Design a live 45-minute webinar with one teaching promise and one bridged offer. `design.yaml` locks the promise, offer, runtime, and registration/show/close assumptions. The plan must teach before pitching and include registration, reminders, rehearsal, replay, and follow-up artifacts.

## Output

The arc budgets hook, credibility, three teaching blocks, bridge, offer, and Q&A to exactly the runtime. Each teaching block contains a framework, demonstration, or worked example; teaching blocks outnumber pitch blocks at least three to one. Four interactions are spaced no more than seven minutes apart.

```console
$ python3 scripts/arc_check.py "$SESS/arc.yaml" --runtime 45
# expected: stage minute budgets sum to 45

$ python3 scripts/teach_density.py "$SESS/arc.yaml" --min-ratio 3
# expected: exit 0 with teaching:pitch ratio at least 3:1

$ python3 scripts/engagement_map.py "$SESS/arc.yaml" --min 4 --max-gap 7
# expected: four or more designed interactions with no excessive gap
```

## Acceptance

- The offer bridge connects the promise's unresolved gap to the offer in no more than three minutes.
- Registration headline repeats the promise; its form has at most four fields and reminders include T−24h and T−1h.
- Slides are at most 60 with no more than 40 words each; fallback PDF, backup stream, and presenter sheet are documented.
- Design, arc, slides, registration page, and follow-up pass the packet checksum; no live event is launched.
