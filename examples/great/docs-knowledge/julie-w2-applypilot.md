# julie-w2-applypilot — what a green run looks like

Gate-green end state for one application cycle (the contract this skill must
reproduce every run, never narrate after the fact):

1. **Posting is official and current** — verified on the employer's own careers
   page, not an aggregator; posting id + fetch timestamp in the run log.
2. **Resume is hash-reviewed full-history** — a reviewer outside the drafting
   agent has hash-reviewed the complete resume artifact; the review hash is
   recorded before any submission.
3. **Receipt is typed and employer-side** — the ATS confirmation number was
   typed by the operator after the submission event; no inferred or scraped
   receipts count.
4. **Outreach evidence is post-reload only** — follow-up evidence collected
   after a verified page reload; pre-reload state never enters the ledger.
5. **No duplicates** — dedupe check against `~/.applypilot` state passed before
   submit; a match stops the run and resumes the existing application instead.

Anything missing one of the five is an honest BLOCKED, not a completion.
