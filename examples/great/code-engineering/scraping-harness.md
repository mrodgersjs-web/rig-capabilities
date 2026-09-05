---
name: great-scraping-harness
lane: code-engineering
source: canonical-curated
exemplar_of: scraping-harness
description: "Reference exemplar for approved, rate-respecting ingestion with parse checks, content hashes, deduplication, local-first storage, and freshness evidence."
---

# Scraping loop: approved release feed

## Input

Choose a URL already present in `approved-sources.json`, confirm it is absent from the blocklist, honor robots.txt and the source's minimum interval, then capture raw data locally before extraction. Each record must carry source URL, publication time, scrape time, and content hash.

```console
$ python3 scripts/assert_loop_termination.py capabilities/loops/scraping-harness.md
$ curl -sI -o /dev/null -w '%{http_code}' "$URL"
$ wc -c "$RAW_FILE"
$ jq . "$RAW_FILE"
$ jq -c '.' "$RECORD" | shasum -a 256
```

## Output

The loop contract validates. The source returns 2xx/3xx, raw content exceeds 100 bytes, parses, contains no trap marker, and meets the content-to-noise floor. Exact hashes already present in the knowledge base are skipped; near-duplicates are merged or explicitly linked. New data is written under `~/.rig/knowledge/` before any secondary sync, re-read with the expected record count, and hash-verified. Freshness is calculated from source publication time, with stale records retained and labeled.

## Acceptance

- The validator and parse commands exit 0; HTTP status is 2xx/3xx.
- Stored record count equals the re-read count and pre/post-write hashes match.
- Every inserted record has provenance; exact duplicate insertions and blocklist violations are zero.
- Rate-limit or reachability failures defer safely, while honeypot or storage-corruption evidence halts the cycle.
