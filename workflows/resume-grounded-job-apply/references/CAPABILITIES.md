# Hermes capabilities and launch

## Required for this workflow

| Capability | Existing surface | How it is used / current limit |
|---|---|---|
| Workflow rules | `resume-grounded-job-apply` | This package, installed under `~/.hermes/skills/resume-grounded-job-apply/`. |
| Skill discovery | Hermes `skills_list` / `skill_view`; local `hermes --skills` | Names and CLI support verified. Start a fresh Hermes session to load a newly installed skill. |
| Files and terminal | Hermes file tools and terminal, Python 3 standard library | Read/hash résumé, extract DOCX XML, create local packets and run `scripts/check_answers.py`. No extra Python package is required by the checker. |
| Job research | Hermes `web_search` / `web_extract`, or an existing authenticated browser | Read current employer/ATS pages. Tool credentials and provider readiness must be checked in the actual session. No paid prospecting product is required. |
| Browser forms and uploads | Hermes native browser/computer tools, or installed `browser-skill` | Use current tool schemas for snapshots, input/select/click, file upload and confirmation. Skill presence is not a live application test. |
| Durable source and tracking | Private JakeStudio job-search note; provided CSV template | Store source citations, reviewed answers, receipts and next-review dates. Do not expose application data through the public website. |
| Independent claim review | Second bounded agent when available, otherwise a separate review pass with explicit limitation | Compare answers/materials to résumé and current form. A style score or synthetic checker test cannot replace it. |

## Browser path verified locally

The installed `~/.hermes/skills/browser-skill/SKILL.md` documents `bsk` for a real Chromium browser with an isolated Agent Window. Mechanics:

1. `bsk status --json` / `bsk browsers` to inspect readiness.
2. `bsk session start --browser <verified-instance-id>` and capture the returned session ID.
3. `bsk navigate <exact-job-url> --session <id>` and `bsk snapshot --session <id>`.
4. Use refs from that snapshot for `fill`, `select`, `click` and `press`. Refresh after each navigation. Inspect `bsk <command> --help` for exact parameters and upload support before using it.
5. End only the session this task created: `bsk session stop <id>`. Do not stop all sessions or close unrelated user tabs.

Observed September 7: a Chrome extension was connected, but daemon 0.1.7/protocol 1.0 and extension 0.2.0/protocol 1.1 reported version skew. No application form or upload was tested. Hermes must pass an ordinary read-only snapshot in its selected browser before filling anything. If incompatible, report the specific blocker or use an already working authorized native browser tool; do not silently change browser/credential settings. CAPTCHA/2FA/identity checks go to Mike.

## Existing skills to use selectively

- `browser-skill`: browser mechanics above; installed.
- `rig-write-resumes`: optional résumé writing mechanics; installed. Its persona/corpus and mandatory-metric suggestions may not add claims. This task's résumé-only rule controls the content.
- `job-application-cockpit` / `rig-job-cockpit`: optional read-only discovery of existing queue, deduplication and receipts. Installed documentation contains legacy paths/assumptions; verify files and schema before use. Do not run its bulk scrapers, generated personas, sends or stale deployment procedures blindly.
- `application-packet-builder`: do **not** load its static candidate persona or infer missing job requirements. Its packet structure is optional; this focused skill already provides the needed workflow.
- Existing Memory OS / Obsidian bridge: retrieve bounded context; memories are references, not authority to invent employment.

No Apollo, Instantly, Clay, Higgsfield or Google Ads capability is needed to apply for jobs. No additional plugin purchase or account creation was performed.

## Start Hermes

The local wrapper requires a task label for managed work. Verified help recognizes `--rig-task` at the wrapper and `--skills` at Hermes:

```sh
hermes --rig-task "Prepare truthful job applications from Mike's resume" --skills resume-grounded-job-apply
```

Then paste `PROMPT.md` and replace the job-link placeholder. Natural-language invocation also works: “Use the resume-grounded-job-apply skill.” If skill discovery has not refreshed, explicitly ask Hermes to read `~/.hermes/skills/resume-grounded-job-apply/SKILL.md`.

Public primary references checked September 7: [Hermes skills](https://hermes-agent.nousresearch.com/docs/guides/work-with-skills), [tools and toolsets](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools). Local CLI/help is authoritative for this installed wrapper. No inference job was launched to test installation.
