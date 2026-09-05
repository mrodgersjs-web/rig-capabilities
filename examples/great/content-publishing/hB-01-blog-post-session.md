---
name: great-hB-01-blog-post-session-yaml
lane: content-publishing
exemplar_of: hB-01-blog-post-session.yaml
description: Reference exemplar for a voice-true long-form post whose thesis, SERP research, claims, word band, originality, and CTA are proven.
---

# hB-01-blog-post-session.yaml — great example

## Input

Create one 1,800-word practitioner post from a locked brief naming the thesis, reader pain, keyword, word budget, and single CTA. A publication voice profile exists before drafting. Research captures five competing pages and at least eight claim-level sources, with current sources for statistics.

## Output

The run writes `brief.md`, `research/serp.json`, `research/sources.yaml`, an approved outline, the complete draft, SEO-surface proof, and a sealed packet. Each statistic, quote, or dated claim resolves to a source entry.

```console
$ python3 -c "import json; d=json.load(open('$SESS/research/serp.json')); assert len(d['competitors']) >= 5"
# expected: exit 0 with search intent and five heading structures captured

$ python3 scripts/bind_claims.py "$SESS/draft.md" "$SESS/research/sources.yaml"
# expected: exit 0; an unbound claim would exit 3

$ python3 scripts/wordband.py "$SESS/brief.md" "$SESS/draft.md"
# expected: draft falls within ±15% of the locked word budget
```

## Acceptance

- The brief hash is recorded before research closes and is unchanged afterward.
- All outline H2s appear in the draft; banned-phrase, voice, overlap, and readability checks are clean or explicitly waived where the harness permits.
- SEO title, description, slug, and internal links meet the declared bounds.
- The one reachable CTA is in the final 15%, and `sha256sum -c $SESS/proof/packet.sha256` exits 0.
