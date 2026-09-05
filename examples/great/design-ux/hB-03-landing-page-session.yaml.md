---
name: great-hB-03-landing-page-session-yaml
lane: design-ux
exemplar_of: hB-03-landing-page-session.yaml
description: Reference exemplar for a one-offer landing page with message match, one CTA destination, measured events, mobile proof, and accessibility.
---

# hB-03-landing-page-session.yaml — great example

## Input

Build a booking page for one traffic source. `offer.yaml` locks who, offer, outcome, timeframe, risk reversal, and three objections; `source_message.txt` contains the upstream promise. The only conversion is a booking form, and view, CTA-click, and submit event names are declared before implementation.

## Output

The page has one unique CTA destination above the fold and at the end, at least three proof elements in the first two viewports, no more than five labeled fields, and concrete answers to the three locked objections. Performance, events, accessibility, and a 390×844 capture are saved under `proof/`.

```console
$ python3 scripts/message_match.py --source "$SESS/source_message.txt" --page "$SESS/page.html"
# expected: headline token overlap is at least 0.8

$ python3 scripts/form_audit.py "$SESS/page.html" --max-fields 5
# expected: exit 0; every field has a real label

$ python3 scripts/events_probe.py "$SESS/page.html" --expect view,cta_click,form_submit
# expected: all three exact events fire and proof/events.json is written
```

## Acceptance

- A DOM check proves one CTA destination and both required placements.
- Total payload is at most 1.5 MB, throttled LCP at most 2.5 seconds, and the 390px viewport has no horizontal overflow.
- Critical accessibility violations are zero and form errors are announced.
- HTML, offer, performance, event, and mobile artifacts pass `sha256sum -c $SESS/proof/packet.sha256`.
