---
outcome: code-engineering:
done_when:
  - file:capabilities/loops/scraping-harness.md
  - the loop file parses and declares a termination test
great_example: examples/great/code-engineering/scraping-harness.md.md
quality_floor: 0.6
---

# Scraping Harness — GL-SI Gate Loop

**Owner:** Jake PAI
**Scope:** GL-SI (Scraping / Ingestion loops)
**Status:** RUNTIME GATE LOOP
**Signed:** 2026-07-10

This harness governs every GL-SI cycle. No scraped data is written to the knowledge base until all gates pass. The loop is: SOURCE → SCRAPE → VALIDATE → STORE → VERIFY.

---

## Gate 0 — Identity Lock

Every GL-SI session must confirm identity before any scraping executes.

- G0.1 ❏ Load `jake-active-goal.json` and confirm `status == "ACTIVE"`
- G0.2 ❏ State the current GL-SI cycle number and target source (URL, API, platform)
- G0.3 ❏ Confirm scraper identity: state scraper module name + version from `~/.rig/scrapers/registry.json`
- G0.4 ❏ Confirm storage target: which knowledge store receives this data

**Evidence:** Goal JSON + scraper module path + storage target path
**On-fail:** HALT. Write `G0-FAIL-{timestamp}` to `~/.rig/state/scraping-failures.log`. No scraping proceeds.

---

## Gate 1 — Source Legitimacy

Before scraping, verify the source is authorized and safe.

- G1.1 ❏ Source URL is in the approved source registry: `~/.rig/scrapers/approved-sources.json`
- G1.2 ❏ Source is not blocklisted: check against `~/.rig/scrapers/blocklist.json` (HED, IdeaWake, known-scam domains)
- G1.3 ❏ robots.txt honored: `curl -s {source}/robots.txt` — confirm path is not disallowed
- G1.4 ❏ Rate limit respected: confirm last scrape of this source was > `min_interval_s` (default 3600s) from `~/.rig/state/scrape-timestamps.json`
- G1.5 ❏ Source is reachable: `curl -sI -o /dev/null -w '%{http_code}' {url}` returns 2xx or 3xx

**Evidence:** Approved source entry + blocklist check + robots.txt content + last-scrape timestamp + HTTP status
**On-fail:** If source not approved → HALT + alert Jake. If blocklisted → HALT + log CRITICAL. If rate-limited → DEFER (write new timestamp, skip cycle). If unreachable → retry once after 60s, then DEFER.

---

## Gate 2 — Data Quality

Raw scraped data must pass quality checks before further processing.

- G2.1 ❏ Response is non-empty: `wc -c {raw_file}` > 100 bytes
- G2.2 ❏ Response is parseable: JSON parses (`jq . {file}` exit 0) or HTML is well-formed (`xmllint --html {file}` exit 0 or equivalent)
- G2.3 ❏ No honeypot content detected: response does not contain known trap strings (`"honeypot"`, `"bot detected"`, `"captcha required"` in body)
- G2.4 ❏ Content-to-noise ratio ≥ 30%: extracted text / raw bytes ≥ 0.30
- G2.5 ❏ No empty or placeholder records: if array, `jq 'map(select(.title != null and .title != "")) | length'` > 0

**Evidence:** Byte count + parse exit code + honeypot scan + ratio calculation + record count
**On-fail:** If empty/unparseable → log source + skip cycle. If honeypot → HALT + blacklist source temporarily (24h). If low ratio → log WARNING but continue with extracted subset.

---

## Gate 3 — Deduplication

No duplicate data enters the knowledge base.

- G3.1 ❏ Compute content hash for each scraped record: `shasum -a 256 {record}` or `jq -c '.' {record} | shasum -a 256`
- G3.2 ❏ Check hash against existing knowledge base: `grep {hash} ~/.rig/state/content-hashes.jsonl`
- G3.3 ❏ Check URL + date combination against existing: `grep '{url}|{date}' ~/.rig/state/scrape-log.jsonl`
- G3.4 ❏ If near-duplicate detected (URL match, >80% content overlap), merge rather than insert
- G3.5 ❏ Record all new hashes to content-hashes.jsonl: `echo '{hash}|{source}|{timestamp}' >> ~/.rig/state/content-hashes.jsonl`

**Evidence:** Hash computation output + grep results (0 matches = no dups) + merge decision if applicable
**On-fail:** If exact duplicate → SKIP record silently (log count). If near-duplicate merge fails → log WARNING, insert as new with `duplicate_of: {existing_hash}` field. Never silently overwrite.

---

## Gate 4 — Storage Verification

Data must be written to storage and verified readable.

- G4.1 ❏ Write data to target store: `~/.rig/knowledge/{domain}/{source-slug}-{date}.json`
- G4.2 ❏ Verify write succeeded: file exists and is non-empty
- G4.3 ❏ Verify data is re-readable: `cat {file} | jq '.records | length'` returns expected count
- G4.4 ❏ Verify no data corruption: re-hash stored file, compare to pre-write hash
- G4.5 ❏ Update scrape registry: `~/.rig/state/scrape-log.jsonl` entry with `{source, timestamp, record_count, file_path, hash}`
- G4.6 ❏ **ENFORCED: Local-first storage** — data goes to local disk FIRST. Cloud/object storage is secondary and must not replace local copy.

**Evidence:** File path + byte size + record count + re-read hash + registry entry
**On-fail:** If write fails → retry once. If re-read fails → delete corrupt file, retry. If hash mismatch → delete file, log CRITICAL, alert Jake. If local write fails → HALT (never write to cloud only).

---

## Gate 5 — Freshness Check

Scraped data must be fresh relative to its domain.

- G5.1 ❏ Record timestamp of source data (not scrape time): extract `{published_at}` or `{last_modified}` from content
- G5.2 ❏ Verify freshness: `{now} - {published_at}` < `max_age` per source config (default: 7 days)
- G5.3 ❏ If stale, mark record with `stale: true, stale_reason: "published {age} ago"` but still store
- G5.4 ❏ Update freshness score in knowledge store: `freshness: {1.0 if < 1 day, 0.5 if < 7 days, 0.1 if > 30 days}`
- G5.5 ❏ If >50% of cycle's records are stale → log WARNING to `~/.rig/state/scraping-failures.log`

**Evidence:** Published timestamp + age calculation + freshness score + stale count
**On-fail:** If timestamp missing → mark `freshness: null`, log WARNING. Stale data is stored but flagged — never silently discarded unless explicitly expired (>90 days).

---

## ENFORCED INVARIANTS

| ID | Invariant | Enforcement |
|---|---|---|
| INV-SI-1 | No duplicate data in knowledge base | Gate 3 must produce 0 exact-dup insertions |
| INV-SI-2 | Source-per-claim | Every stored record carries `{source_url, scraped_at, hash}` — no unsourced claims |
| INV-SI-3 | Local-first storage | Gate 4.6 — local disk write before any cloud sync |
| INV-SI-4 | Blocklist is absolute | Gate 1.2 — blocklisted sources are never scraped, no override |
| INV-SI-5 | Rate limits are absolute | Gate 1.4 — minimum interval enforced, no skip |
| INV-SI-6 | Honeypot = permanent blacklist | Gate 2.3 — honeypot detection blacklists source for 7 days minimum |

---

## PROOF PACKET

Each GL-SI cycle produces:

```json
{
  "schema": "rig.scraping.proof.v1",
  "cycle": 0,
  "timestamp": "ISO-8601",
  "source": { "url": "...", "type": "web|api|file", "approved": true },
  "gates": {
    "G0_identity": { "pass": true, "scraper": "...", "version": "..." },
    "G1_source_legitimacy": { "pass": true, "robots_ok": true, "rate_ok": true },
    "G2_data_quality": { "pass": true, "bytes": 0, "records": 0, "noise_ratio": 0.0 },
    "G3_dedup": { "pass": true, "new": 0, "duplicates_skipped": 0, "merged": 0 },
    "G4_storage": { "pass": true, "path": "...", "hash": "...", "local_first": true },
    "G5_freshness": { "pass": true, "avg_freshness": 0.0, "stale_count": 0 }
  },
  "records_stored": 0,
  "records_skipped": 0,
  "verdict": "PASS | FAIL | CRITICAL"
}
```

---

## FAILURE SEVERITY

| Severity | Trigger | Action |
|---|---|---|
| LOW | Low noise ratio, missing timestamp | Log only |
| MEDIUM | Near-duplicate detected, >50% stale, source unreachable | Log + flag in proof packet |
| HIGH | Source not approved, parse failure, honeypot detected | Log + HALT cycle + alert Jake |
| CRITICAL | Blocklist violation, storage corruption, cloud-only write | Log + HALT all GL-SI + alert Mike Telegram |

---

*Signed: Jake PAI, 2026-07-10*
*Governs: GL-SI loops (scraping, ingestion, knowledge intake)*

## What Great Looks Like (WGLL)

Amazing scraping output from this harness:

- **Data is real** — every row verifiable against source URL
- **Rate limits respected** — no 429s, exponential backoff on failures
- **Schema is typed** — Pydantic model validates every scraped record
- **Deduplication works** — no duplicate records in output
- **Anti-detection active** — user-agent rotation, proxy rotation, request jitter
- **Error recovery graceful** — partial results saved, failed URLs logged for retry
- **Output format documented** — schema, field descriptions, example records

