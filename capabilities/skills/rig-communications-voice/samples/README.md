# Writing samples per surface (v5.9)

Extraction procedure — real writing only, no fabricated samples:
- linkedin: rig-linkedin-scrape (read-only CDP) of Mike's own recent posts -> samples/linkedin/
- substack: public archive export of mikerodgers/Substack -> samples/substack/
- emails: mailbox export, work-context only, redact recipients -> samples/emails/
- film-scripts/novels: existing drafts in JakeStudio / rig-film-studio projects
- songs: SUNO lyric exports
- resumes: current resume + last 3 targeted variants (job cockpit packet)
- specs/code: rig-capabilities commits + one RFC
Floor: >= 2,000 words per surface before per-surface distributions are locked.
Then run the fingerprint-extractor procedure (sentence stats, >=10 signature
entries, 5-sentence calibration) and store fingerprint JSON in data/comms/.

DATA GAP: no samples exported yet — base fingerprint (references/fingerprint-v2.md)
is active for all surfaces until per-surface stats exist. Do not invent per-surface
distributions before the floor is met.
