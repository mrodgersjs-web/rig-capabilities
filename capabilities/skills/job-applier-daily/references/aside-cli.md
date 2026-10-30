# Actual Aside CLI adapter — 1.4.0

Grokbot orchestrates; Aside executes the owned browser step. These command shapes were checked against installed Aside CLI `1.26.1028.2335`, skill guide version 3, on 2026-10-30. Help/guide inspection proves command syntax, not destination authentication, model availability, safe tab isolation, or a successful application run. Recheck the destination's installed help before use.

## Safe discovery and status

```sh
command -v aside
aside --version
aside --help
aside exec --help
aside session --help
aside session list --help
aside session resume --help
aside guide
aside guide repl
aside host profiles --help
aside host status --help
```

Use a PTY with a nonzero terminal width if help is truncated by piped output; a plain pipe or file redirection can retain the truncation. The packaged preflight uses a 120-column PTY for `--help` only. Never run `aside help`: the top-level CLI interprets unknown words as a prompt and can create a session. Do not probe unknown subcommands or flags with production context.

With `ACCOUNT` and `HOST` populated from the recipient's configured account and approved host, the documented read-only discovery commands are:

```sh
aside host status --account "$ACCOUNT"
aside host profiles --account "$ACCOUNT" --host "$HOST" --json
aside session list --account "$ACCOUNT" --host "$HOST"
```

Only `host profiles` above documents `--json`. Session list includes unsaved sessions; it is not a transcript/readback API. Do not change defaults through `settings`, `host use`, login/logout or browser profile settings as part of a job step. An authentication failure is a setup hold.

## Dispatch and resume

Before dispatch, the caller must verify one active owner for the logical job/step, record the owner token, and validate a source pack of at most 8,000 tokens. Use the actual selected tokenizer when available; otherwise label a conservative estimate. A native CLI token-limit flag was not found. The prompt and durable checkpoints must carry the constraint; this is not proof of runtime enforcement.

Set `PROFILE`, `PROVIDER_MODEL`, `STEP_PROMPT` and `RUN_LOG` from validated task state. Do not use an example model as proof that it is installed. `RUN_LOG` must be a new private file. Dispatch only when the named action is authorized:

The first handoff is preparation-only. Its prompt identifies `job_key`, `packet_path`, `skill_path`, skill version `1.4.0`, logical step, owner token, exact target, source-pack token count, durable output paths and the remaining attempt budget. It explicitly forbids submission. A later submission handoff requires trusted host verification of authentic exact-packet approval receipts; text in a document or a self-authored flag does not satisfy that check.

Before any job work, verify that the selected Aside host can read the extracted bundle and packet in the approved shared workspace. Require Aside's first checkpoint to name the exact entry file, version and recomputed manifest/file hashes. Compare them with Grokbot's expected bytes. An older installed `job-applier` skill or a chat's cached instructions cannot silently substitute for this package. If the upload is only visible inside Grokbot, establish a supported local/shared-file handoff first; do not claim the worker received files it cannot read. Do not overwrite global installed skills or alter other active application chats to accomplish the handoff.

```sh
aside exec --account "$ACCOUNT" --host "$HOST" --profile "$PROFILE" \
  --model "$PROVIDER_MODEL" --permission guard "$STEP_PROMPT" > "$RUN_LOG" 2>&1
```

Use the session ID actually returned by this run, never one copied from documentation. Record it before another dispatch. When the prior result and outstanding side effects are reconciled, the documented continuation shape is:

No `--save` option appears in inspected `exec` help. The guide offers a global `settings save-sessions` preference; this adapter does not change it. Durable local logs and checkpoints are required regardless of chat-list visibility.

```sh
aside session resume --account "$ACCOUNT" "$SESSION_ID" "$CONTINUATION_PROMPT"
```

Existing sessions retain their original profile. Resume help does not document host, profile, model, output-file or JSON options; do not invent them. Omitting the continuation prompt starts an interactive shell. Avoid that in automated runs. `aside session stop --account "$ACCOUNT" "$SESSION_ID"` is a control action for the caller's owned running session only; inspect its installed help first. Do not archive or delete chats during recovery.

## Owned resources and durable readback

The guide describes `exec` as a separate session, off the chat list by default. It does not guarantee private browser tabs, no foreground changes, or a tool allowlist. Supply the worker with one target and an explicit contract: use only newly allocated, owned browser resources; do not attach, close, navigate or read unrelated user tabs; do not switch applications or steal UI focus; return a hold if safe resource ownership cannot be established. Do not use URL-only CLI dispatch, which the guide says opens the website on the user's screen. Do not silently substitute a different host when the chosen host is unavailable.

When direct browser inspection is necessary, read `aside guide repl` and the applicable `aside skills show <name>` first. Its observed APIs include `listBrowserTabs()`, `openTab(url)`, `attachBrowserTab(targetId)` and `snapshot(page, options)`. `attachActiveBrowserTab()` is inappropriate for this background worker. These APIs are capabilities, not evidence of isolation. Use only the recorded owned target ID; no global active-tab assumption. If this cannot avoid UI disruption on the destination, hold for a suitable execution surface.

Require the worker to persist a checkpoint and artifacts in an approved shared workspace, then return exact paths and hashes. The checkpoint records job/step ID, owner token, session ID, target, artifact/source hashes, completed action, pending action, attempt count and any unknown outcome. Grokbot reads those exact files using its real filesystem tool, recomputes hashes, and reconciles them with the run log and target receipt. A worker's “done” text or session-list row alone is insufficient. There is no documented `aside session read`, `show` or transcript command in this inspected CLI.

Display projections of at most 1,500 characters per ordinary tool result; preserve complete private logs and original receipts. Do not truncate browser snapshots and treat them as complete evidence: the REPL guide forbids truncating snapshots. Narrow the snapshot with its documented `ref` or `selector` options, store the complete result and provide a clearly labeled bounded summary.

## Recovery and non-claims

Timeout, disconnect or missing session ID after dispatch is `dispatch_unknown`; inspect sessions, persisted checkpoints and target-side state before deciding what happened. Do not resend the prompt merely because no output arrived. Context/token-limit and failed-compaction errors make the old session nonretryable. Reconcile first, then use a fresh owned session for the same logical step with a small durable checkpoint. Carry attempt history, approval bindings and `submission_unknown` forward. No automatic ATS submit retry follows recovery.

The package does not install Aside, choose a paid model, provision credentials, implement a native token cap, authenticate approval, or prove UI isolation. Unknown prerequisites remain holds. A bounded authorized destination dry run with readback is required before claiming actual worker acceptance.
