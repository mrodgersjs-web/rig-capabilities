# Asset quality behavior

## Inventory and readiness

The system SHALL inventory every top-level canonical skill and agent from
source, including newly added assets not yet in a TTL index. It SHALL report
missing metadata, exemplars and behavioral done-tests separately. A `file:`
or text-presence check alone SHALL NOT count as a behavioral done-test.

## Promotion

The system SHALL NOT turn a declared floor, a Jev confidence value, a
metadata-completeness score or a routing-test pass into an outcome score.
It SHALL BLOCK promotion when any canonical asset lacks independently
verified, source-bound, held-out task outcomes above 0.90 or has a hard block.
An empty inventory SHALL NOT pass the gate.

## Semantic checks

Jev SHALL receive redacted, bounded state for typed semantic checks. An
unavailable or uncalibrated Jev rubric SHALL defer or advise; it SHALL NOT
certify completion. A Promptfoo suite SHALL name which behavior it proves
and SHALL NOT extrapolate router fixtures into task outcomes.
