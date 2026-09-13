# Corpus freeze A33–A37 — retrieval manifest (agentic-stack-buildout)

Run from this directory (`runs/agentic-stack-buildout/corpus/`).
Ingest status: **every manifest row is `claim_class=PENDING`,
`ingest_label=not_ingested_local_only`** — there is no authorized `rig_build`
database this session (plan item NB-02 unapproved), so
`build_store.put_source_document` was never called and no row claims
ingestion. Per `rig_capabilities/build_corpus.py` (OPEN_RETRIEVAL_ITEM and the
module docstring: "every row says so: retrieval runs need their own approved
step"), a row may only leave PENDING after its bytes are in
`rig_build.source_documents`; bytes here sit in `raw/` awaiting that step.
Row keys mirror `ROW_KEYS` (url, provider, kind, why_version_applicable,
expected_artifact, retrieval_status, claim_class, policy_effect) plus the A33
fields (canonical_url, fetched_at, http_status, content_sha256, title,
product_version_or_doc_date, quota_slot) so a later ingest needs no converter.

The frozen URL set is `manifest-v1.json` (immutable, verified, copy in
`frozen/`). A34 retrieval hit 8 dead frozen URLs (404); per the A33 rule those
rows are kept with `retrieval_status=REPLACED(...)` + `replaced_by`, and the
replacements carry `replaces=<old url>`. `manifest.jsonl` therefore holds 30
quota rows + 8 immutable history rows = 38 lines.

## Count table (each reproducible by the printed one-liner; outputs pasted below)

| # | Count | Command | Result |
|---|-------|---------|--------|
| C1 | frozen quota rows | `python3 -c "import json;print(sum(1 for l in open('manifest.jsonl') if json.loads(l).get('quota_slot')))"` | 30 |
| C2 | per-provider quota | `python3 -c "import json,collections;print(dict(collections.Counter(json.loads(l)['provider'] for l in open('manifest.jsonl') if json.loads(l).get('quota_slot'))))"` | pydantic-ai 6, temporal 6, kestra 4, langgraph 5, langchain 3, langfuse 3, langsmith 3 |
| C3 | retrieval status histogram (quota rows) | `python3 -c "import json,collections;print(dict(collections.Counter(json.loads(l)['retrieval_status'].split('(')[0] for l in open('manifest.jsonl') if json.loads(l).get('quota_slot'))))"` | REDIRECT 14, RETRIEVED_FULL 14, RETRIEVED_PARTIAL 2 |
| C4 | discovered URLs per provider | `wc -l discovered/*.jsonl` | 1143 total (see block) |
| C5 | practitioner items per missing mechanism | `python3 -c "import json,collections;print(dict(collections.Counter(json.loads(l)['mechanism'] for l in open('practitioner/register.jsonl'))))"` | 9 items over the 6 named mechanisms |
| C6 | manifest hashes == bytes on disk | hash-recompute script below | 60 files, 0 mismatches |
| C7 | REPLACED history rows | `python3 -c "import json;print(sum(1 for l in open('manifest.jsonl') if not json.loads(l).get('quota_slot')))"` | 8 |
| C8 | cleaned text present and hash-true | `python3 -c "import json,hashlib,pathlib;C=pathlib.Path('.');rs=[json.loads(l) for l in open('manifest.jsonl')];q=[r for r in rs if r.get('cleaned_file')];bad=[r['url'] for r in q if hashlib.sha256((C/r['cleaned_file']).read_bytes()).hexdigest()!=r['cleaned_sha256']];print(len(q),'bad',len(bad))"` | 30 cleaned rows, 0 bad (min 29 / median 7,871 / max 102,870 bytes) |

## Verbatim outputs (captured 2026-09-12, this directory)

```
C1: 30
C2: {'pydantic-ai': 6, 'temporal': 6, 'kestra': 4, 'langgraph': 5, 'langchain': 3, 'langfuse': 3, 'langsmith': 3}
C3: {'REDIRECT': 14, 'RETRIEVED_FULL': 14, 'RETRIEVED_PARTIAL': 2}
C4:    574 discovered/kestra.jsonl
      27 discovered/langchain.jsonl
      87 discovered/langfuse.jsonl
      65 discovered/langgraph.jsonl
      44 discovered/langsmith.jsonl
     299 discovered/pydantic-ai.jsonl
      47 discovered/temporal.jsonl
    1143 total
C5: {'durable workflow replay safety and versioned workers': 2, 'transactional outbox + claim/fencing': 2, 'resumable checkpoints with bounded cycles': 1, 'Postgres role-scoped isolation with RLS': 1, 'closed-schema MCP tool design that cannot mint authority': 1, 'migration idempotency and grant-vs-function execution-context bugs': 2}
C6: files 60 mismatches 0
C7: 8
```

C6 script (run here, not in a temp dir — read-only over this tree):

```
python3 -c "
import json,hashlib,pathlib;C=pathlib.Path('.');n=b=0
for l in open('manifest.jsonl'):
    r=json.loads(l)
    for f,h in ((r.get('raw_file'),r.get('content_sha256')),(r.get('cleaned_file'),r.get('cleaned_sha256'))):
        if f:n+=1;b+=hashlib.sha256((C/f).read_bytes()).hexdigest()!=h
print('files',n,'mismatches',b)"
```

A37 string-verification outputs (against fetched bytes, same directory):

```
pg_try_advisory_xact_lock present: True
SECURITY DEFINER present: True
```

## Status vocabulary actually used

`RETRIEVED_FULL` · `REDIRECT(final url)` · `RETRIEVED_PARTIAL(reason)` ·
`BLOCKED(status)` (the 8 original 404s, now REPLACED) · `NOT_ATTEMPTED`
(discovered map). `MISSING_CAPTIONS`: zero rows — no video source entered the
frozen set (`transcripts/GAP-NOTES.md`). `UNREACHABLE`: zero rows.

## Known gaps / honest limits

- 2 quota rows are RETRIEVED_PARTIAL: `langchain-ai.github.io/langgraph/` and
  `.../concepts/persistence/` still return 200 but only as JS-redirect shells;
  the live content is captured in the two docs.langchain.com replacement rows
  and the discovered map.
- The 3 langchain quota URLs all redirect to one canonical overview page
  (provider docs consolidation); distinct live pages are enumerated in
  `discovered/langchain.jsonl`.
- The 3 langsmith quota URLs share 2 canonical targets for the same reason.
- Discovered maps were built from links present in fetched official pages
  (nav/index extraction), not a full-site crawl; JS-only page trees (e.g.
  parts of docs.temporal.io, which exposes few static hrefs) are undercounted.
  Nothing discovered beyond the 30+8 was fetched — the point is the map.
- `product_version_or_doc_date` is best-effort extraction from page metadata;
  `null` means the page carried no machine-readable date/version. One
  implausible future date (2030-01-01 schema example on the Pydantic agents
  page) was nulled rather than recorded.
- Fetched pages embed install/approve instructions; per A37 they are inert
  data (`policy_effect=NONE`) and no command from fetched material was run.

## Corrected pass: cleaned bytes (2026-09-13)

The first pass left `cleaned_file` as zero-byte placeholders, so every
`cleaned_sha256` was the empty-string hash — literally true, and useless
downstream (A38 would have read nothing). Cleaned text was then generated from
the raw bytes already on disk (drop script/style/nav/form chrome, keep `<pre>`
blocks verbatim inside ``` fences, collapse whitespace), each `cleaned_sha256`
recomputed over the bytes actually written, and `manifest.jsonl` rewritten in
place (per-pid temp + atomic replace). `manifest-v1.json` and its sidecar were
not touched (sha `a98f4653…` verified before and after), and no page was
re-fetched, so `content_sha256` is unchanged on all 30 quota rows. C6 still
holds after the pass: 60 declared files, 0 mismatches.

The smallest cleaned row is 29 bytes: the two `RETRIEVED_PARTIAL` raw files are
JS-redirect shells, so their cleaned text is the shell's text. That is the raw
bytes speaking, not a lost fetch — live content for both sits in the
docs.langchain.com replacement rows.
