---
name: great-hB-05-seo-content-session-yaml
lane: content-publishing
exemplar_of: hB-05-seo-content-session.yaml
description: Reference exemplar for intent-matched SEO content with competitor gaps, entity coverage, valid hierarchy, links, schema, and cannibalization proof.
---

# hB-05-seo-content-session.yaml — great example

## Input

Create a guide for one primary query and four secondary queries, each mapped to intent and funnel stage. Audit the actual result-page format and features, compare the top five ranking pages, then lock three uncovered subtopics into the outline before drafting.

## Output

The draft has one H1, valid H2/H3 nesting, at least two snippet-eligible blocks, four descriptive internal links, two authoritative citations, byline credentials, a review date, and valid Article or FAQPage JSON-LD. It covers at least 70% of the salient related entity set.

```console
$ python3 scripts/gap_map.py "$SESS/gaps.yaml" "$SESS/outline.md"
# expected: all three or more gaps map to an H2

$ python3 scripts/entity_cover.py "$SESS/draft.md" "$SESS/cluster.yaml" --min 0.70
# expected: exit 0 with entity coverage at or above 0.70

$ python3 scripts/cannibal_check.py "$SESS/cluster.yaml" "$SESS/site_index.json" --max 0.6
# expected: no conflicting page above threshold; otherwise consolidate instead of publish
```

## Acceptance

- Query cluster, result-page features, and competitor gaps are captured before the draft.
- Heading lint, snippet checks, internal-link target checks, and schema validation all produce evidence.
- No keyword-stuffing target is accepted and no unanswered heading remains.
- Cluster, gaps, draft, schema, and link proofs pass `sha256sum -c $SESS/proof/packet.sha256`.
