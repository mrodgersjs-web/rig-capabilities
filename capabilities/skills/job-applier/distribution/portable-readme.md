# Job Applier for Aside v1.1.0

This package installs five skills: Job Applier, Lucy skills, lucyskills, Lucy executive evidence, and Lucy resume evidence. It prepares a full executive working resume, guides factual review, checks quality, and stops before a specific application submission.

The first five applications are hand-held. Review each resume first, then separately approve that exact application. The count starts at zero and advances only from approval-linked employer/ATS receipts. No application, message, or recurring job runs during installation.

## What changed

Job Applier now loads eight linked step skills. Every role starts with a full ideal-candidate persona and an atomic requirement inventory. The workflow maps ideal achievements to your real evidence, preserves your original Word template, produces a red UNCONFIRMED review copy and separate clean copy, then asks focused questions. A local validator checks required artifacts, step order and current hashes. It does not establish that a claim is true or authorize submission.

## Requirements

- Aside with local user skills under your home directory's `.aside/u/0/skills/user`.
- Python 3.10 or newer for the included helpers.
- Your own configured model and browser/document tools in Aside. You supply your own resume and target posting.
- Your own TypeSafe Jev credentials in the `TYPESAFE_API_KEY` environment variable inherited by the helper process. Use your existing secret manager or provider setup. Do not place the key in a skill, command argument, receipt, or shared chat.
- For the included render helper, installed LibreOffice `soffice` and Poppler `pdftoppm` and `pdfinfo`. It checks PATH first, then existing executables in supported macOS installation locations and the current user's Codex runtime. It records the exact programs used and never installs them. See the quality API reference for the lookup paths. Another trusted renderer is acceptable only if it produces actual page images bound to the final DOCX.
- Read the quality API reference for the image and typed response contract. Missing credentials, unavailable tools, or an invalid response blocks the affected step. There is no silent no-Jev mode.

The package includes reusable resume and executive interview guidance. It does not include a full Lucy video corpus, broader LinkedIn/salary automation, a separate Work application, model weights, credentials, or another person's career material.

## Install

Extract the ZIP. Open a terminal in the extracted `Job-Applier-Aside` folder. Verify and install:

```sh
python3 install.py verify
python3 install.py install
```

The installer makes no network requests. It checks every packaged file against `MANIFEST.json` before writing. Existing identical skills stay unchanged. If an existing skill differs, installation stops before writing any skill. To back up and replace those five package names, run:

```sh
python3 install.py install --replace
```

Keep the printed receipt path. Backups and the receipt live in `.job-applier-installs` inside your home directory. The installer does not touch other skills, provider settings, browser sessions, resumes, or automation status.

If installation is interrupted, use the receipt in the newest `.job-applier-installs` subdirectory to run the uninstall command below before trying again. The installer writes that receipt before changing skill files. Rollback preserves partial copies and restores prior skills, including after an interrupted rollback.

Start a fresh Aside chat or use its supported skill refresh. Ask it to read `job-applier/SKILL.md` from your user skill directory. Confirm that it can read all eight `steps/<name>/SKILL.md` files linked from Job Applier and resolve the linked Lucy skills. Updating files does not refresh an existing chat automatically. If the host uses another profile or skill root, stop and identify that root before copying anything. This installer targets profile `u/0` only.

## Run one application

Tell Aside:

> Use the updated Job Applier meta-skill for this official posting: [URL]. Load each of its eight step skills in order. Use my attached Word resume as the immutable template. Build the full ideal-candidate persona, map every requirement, then give me the complete tailored Word review copy with unconfirmed examples in actual red text and a separate clean version. Ask focused factual questions, review the rendered pages with me, and stop before submission.

The process is in `skills/job-applier/references/process.md`. The executable quality and render procedures are in `skills/job-applier/references/quality.md`. Read those from the installed copy when running. The skill name does not guarantee a bare slash-command registration.

A full current source and a valid live identity check are required first. Later quality findings stay visible and guide a clearly marked provisional draft, so you can review useful work while resolving questions. Failed or unknown checks keep their original receipts and block final documents, application readiness, and submission.

For working-draft reviews, the helper sends the full posting and draft with every historical evidence row referenced by the draft. Unused history is omitted from that hosted request; referenced rows are never truncated. The receipt still binds the full local packet. A request the provider cannot accept remains a hold, with its error recorded; a technically successful request does not mean its quality review passed.

The Jev image review uses an experimental image API and provides advisory evidence. `NEEDS_HUMAN_REVIEW` pauses an uncertain image check; it is not a formatting-failure verdict or permission to advance. You must review the actual rendered pages yourself. Your factual approval and your separate submission approval cannot be replaced by a model score. Missing or ambiguous submission confirmation stays unknown; never blindly submit again.

## Optional offline package checks

From the extracted package folder:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/job-applier/tests -v
```

These use synthetic fixtures and make no provider calls. For a real saved workflow packet, run `python3 skills/job-applier/scripts/validate_packet.py /path/to/packet.json`. Read the packet contract before preparing that record. A passing synthetic test is not proof of a completed application.

## Uninstall or roll back

Use the receipt printed by the install command:

```sh
python3 install.py uninstall --receipt /absolute/path/to/receipt.json
```

The uninstaller preserves the removed package files beside the receipt and restores any pre-install backups. Skills that were already identical before installation remain untouched. If you changed an installed file, uninstall refuses until you choose to preserve those edits:

```sh
python3 install.py uninstall --receipt /absolute/path/to/receipt.json --preserve-edits
```

This archives the changed copy before restoring the prior skill. Do not manually remove the receipt or backups until you no longer need rollback.

## Limits of the checks

A clean temporary-home install and uninstall can prove file placement, hashes, collision handling, and rollback. They do not prove that your Aside build discovers the skills or that your provider and browser work. Verify those on your own machine before a real application. The installer never uploads files or sends an application.

The offline pilot helper validates saved file hashes and record links. It cannot authenticate the human or employer behind a saved record. Inspect the original approval and actual employer/ATS confirmation before counting a submission.
