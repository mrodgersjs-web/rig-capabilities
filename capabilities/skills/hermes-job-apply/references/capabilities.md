# Capabilities and existing integrations

This workflow has no new Python/npm dependencies or service. Hermes provides reasoning and calls the tools available in its active session. Presence on disk is not proof of live browser connectivity or account authorization.

| Capability | Existing surface | How this workflow uses it |
|---|---|---|
| Skill discovery | Hermes `skills_list`, `skill_view` | Load `hermes-job-apply` and its referenced files; installed loader verified separately in the build proof. |
| Local files and checkpointing | Hermes file tools and terminal | Read the source resume, keep private answers, write per-application files atomically. |
| Resume extraction | Local DOCX parser or macOS `textutil`; installed PDF reader when present | Preserve tables and employment headings. `pdftotext` was absent on this Mac at inspection; don't invoke it blindly. |
| Browser forms | Installed `browser-skill` and `bsk`; alternatively Hermes native browser tools when offered | Inspect current tools, then navigate, snapshot, fill, select, and read back. Load that browser's skill/docs before operating. |
| File upload | Installed `agent-browser upload <selector> <files...> --session <name>`, or a human-assisted upload | CLI help confirms upload support. It must be connected to the authorized application session. `bsk` and native Hermes browser tools did not expose upload at inspection. Never move sessions or switch tools to evade a restriction. |
| Live job research | Hermes web search/extraction or browser reading | Verify employer page, requisition, and current description. No fixed paid search provider required. |
| Existing job inventory | `job-application-cockpit` skill, canonical studio data | Reuse verified queue/status files; see paths below. Do not execute deployment or scraping scripts merely to fill an application. |
| Resume writing | `rig-write-resumes`, `rig-communications-core` | Optional drafting/style checks. Resume evidence remains authoritative; a style score is not factual verification. |
| Dossier/letter structure | `application-packet-builder` | Optional formatting reference only. Its hardcoded biography, example metrics, and old Desktop paths must not supply facts or destinations. |
| Memory | Private JakeStudio policy and answer bank; RIG Memory OS retrieval if available | User-verified answer reuse. Retrieved records are references, not new authorization or verified career facts. |

Inspected on 2026-09-07: the listed skills, Hermes launcher, `bsk`, `agent-browser`, and `textutil` exist locally. Runtime browser login, upload support, live ATS submission, and profile-specific tool grants must be checked during an application run. No browser was opened or application sent by this installation.

## Current workspace references

Canonical LinkedIn studio input root:
`/Users/rig128gb/Developer/rig-gtm-studio-v2/studios/linkedin/`

Resume candidates:
- `/Users/rig128gb/Downloads/MikeRodgersResume.docx` (original-file candidate, outside repository; read-only)
- `luca/job-search/Mike_Rodgers_Resume.docx`
- `luca/job-search/Mike_Rodgers_Resume.txt`
- `luca/job-search/resume_current.txt`

Potential existing tracker/packet surfaces, whose current schema must be inspected before use:
- `luca/job-search/apply-ops/`
- `luca/job-search/packets/`
- `data/engagement.db` (read-only inspection until its writer contract is verified)
- `cockpit-v2/public/data/jobs.json`
- `luca/Luca_Job_Tracker.xlsx` (213 Jobs and 213 Applications rows at inspection; row count alone does not prove submissions)

The older `luca/excel/` workbook and installed Hermes workbook differ from the canonical studio workbook. Reconcile job IDs and actual statuses; don't overwrite one with another. Apply-ops `OPERATOR_PROGRESS.md` contains staged work, and latest-plan says the status store was not modified. A staged packet is not proof that Mike applied.

The private source registry records the inspected resume binding. Prefer an explicit new user-supplied resume over these candidates; do not choose the newest timestamp among generated variants. Legacy `job-application-cockpit` instructions point to Desktop copies. Those paths do not override current repository placement or the source registry.

## Future maintenance

Canonical owner: `/Users/rig128gb/Developer/rig-capabilities/capabilities/skills/hermes-job-apply/`.
Hermes installed copy: `/Users/rig128gb/.hermes/skills/hermes-job-apply/`.

Change the canonical asset, validate the requested behavior, then register with `capability_add` using the canonical path and install via `capability_install` for Hermes. Inspect an existing differing installation before replacing it; the installer preserves a backup. Do not maintain separate independently edited workflow copies.
