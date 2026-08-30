# Headless lane: Gate-D as code, not convention

Proof that RIG's headless agent runs can enforce the Gate-D guard **inside the
agent loop** via the Anthropic Agent SDK's `can_use_tool` permission callback,
instead of relying on shell-wrapped CLI invocations plus external PreToolUse
hooks. When the agent runs headless (cron, CI, fleet workers), a callback in
the host process is enforced by construction; a hook only exists if the shell
wrapper remembered to wire it.

Everything below was run on 2026-08-30 on the M5 Max workstation. No network
LLM calls are involved in the proof.

## 1. Install evidence (MIT-licensed SDK)

```
$ export PATH="$HOME/.local/bin:$PATH"
$ cd ~/Developer/rig-capabilities
$ uv venv .venvs/claude-sdk --python 3.12
Using CPython 3.12.12
Creating virtual environment at: .venvs/claude-sdk
$ uv pip install --python .venvs/claude-sdk/bin/python claude-agent-sdk
...
$ .venvs/claude-sdk/bin/python -m pip show claude-agent-sdk
Name: claude-agent-sdk
Version: 0.2.148
Summary: Python SDK for Claude Code
Home-page: https://github.com/anthropics/claude-agent-sdk-python
$ .venvs/claude-sdk/bin/python -c "import claude_agent_sdk as m; print(m.__version__)"
__version__: 0.2.148
```

License: MIT (anthropics/claude-agent-sdk-python) — vendorable per RIG license
policy.

## 2. Verified API surface (imported, not remembered)

`dir(claude_agent_sdk)` exports 155 public symbols. The permission-callback
surface (filtered from the actual `dir()` output):

```
['BaseHookInput', 'CallToolResult', 'CanUseTool', 'CanUseToolShadowedWarning',
 'ClaudeAgentOptions', 'ClaudeSDKClient', 'DeferredToolUse', 'HookCallback',
 'HookContext', 'HookEventMessage', 'HookInput', 'HookJSONOutput',
 'HookMatcher', ..., 'PermissionMode', 'PermissionRequestHookInput',
 'PermissionRequestHookSpecificOutput', 'PermissionResult',
 'PermissionResultAllow', 'PermissionResultDeny', 'PermissionUpdate', ...,
 'PreToolUseHookInput', ...]
```

The permission callback type alias, printed via
`print(claude_agent_sdk.CanUseTool)`:

```
collections.abc.Callable[[str, dict[str, typing.Any],
claude_agent_sdk.types.ToolPermissionContext],
collections.abc.Awaitable[claude_agent_sdk.types.PermissionResultAllow |
claude_agent_sdk.types.PermissionResultDeny]]
```

Result dataclasses (`dataclasses.fields` + `inspect.signature`):

```
PermissionResultAllow fields: ['behavior', 'updated_input', 'updated_permissions']
  sig: (behavior: Literal['allow'] = 'allow',
        updated_input: dict[str, Any] | None = None,
        updated_permissions: list[PermissionUpdate] | None = None) -> None
PermissionResultDeny fields: ['behavior', 'message', 'interrupt']
  sig: (behavior: Literal['deny'] = 'deny', message: str = '',
        interrupt: bool = False) -> None
ToolPermissionContext fields: ['signal', 'suggestions', 'tool_use_id',
  'agent_id', 'blocked_path', 'decision_reason', 'title', 'display_name',
  'description']
```

`ClaudeAgentOptions` — 48 dataclass fields (full `dataclasses.fields` dump):

```
tools allowed_tools system_prompt mcp_servers strict_mcp_config
permission_mode continue_conversation resume session_id max_turns
max_budget_usd disallowed_tools model fallback_model betas
permission_prompt_tool_name cwd cli_path settings add_dirs env extra_args
max_buffer_size debug_stderr stderr can_use_tool hooks user
include_partial_messages include_hook_events forward_subagent_text
fork_session resume_session_at resume_drops_turn agents setting_sources
skills sandbox plugins max_thinking_tokens thinking effort output_format
enable_file_checkpointing session_store session_store_flush
load_timeout_ms task_budget
```

The field that matters for Gate-D: **`can_use_tool`**. Note that
`permission_mode` exists, but the gate logic below is ours regardless of mode.

## 3. The Gate-D-as-code pattern

`examples/gate_d_sdk_demo.py` registers an async callback with the exact
`CanUseTool` signature — `(tool_name: str, input_data: dict, context:
ToolPermissionContext) -> PermissionResultAllow | PermissionResultDeny` — and
mirrors, pattern-for-pattern, the decision semantics of the two house guard
hooks (`~/.claude/hooks/guard-dangerous-commands.sh`,
`guard-secret-write.sh`):

| Rule class | Denies |
| --- | --- |
| Dangerous commands (Bash) | `rm` recursive+force targeting `/`, `~`, `~/`, `$HOME`, or system paths; `sudo rm`; `mkfs`; `dd`/redirects to raw devices; force-push to `main`/`master`; `git reset --hard ~/`; `git clean -fx`; `chmod -R 777 /`; fork bombs |
| Credential leak (any tool) | `AKIA[0-9A-Z]{16}`, PEM `PRIVATE KEY` headers, `gh[pursr]_…` tokens, Slack `xox…` tokens, Stripe `sk-live/sk-proj`, Google `AIza…` keys — scanned across **every nested string value** of the tool input (generalizes the hook's four content fields) |

Unlike the shell hooks (which fail *open* on internal error to avoid bricking
the fleet), the callback returns an explicit `PermissionResultDeny` with a
message the model sees, and appends one JSON line per decision to
`examples/gate_d_ledger.jsonl` next to the script — credential matches are
masked (`[REDACTED-CREDENTIAL]`) before the ledger touches disk. Wiring is
proven in-process without spawning the CLI:
`ClaudeAgentOptions(can_use_tool=gate_d)` asserts the callback is stored.

Run + result (synthetic payloads, no LLM):

```
$ .venvs/claude-sdk/bin/python examples/gate_d_sdk_demo.py
[OK ] deny  Bash   rule=rm-rf-root-or-home
[OK ] deny  Bash   rule=rm-rf-root-or-home
[OK ] deny  Write  rule=aws-access-key-id
[OK ] deny  Write  rule=pem-private-key
[OK ] allow Bash   rule=no-rule-match
[OK ] allow Edit   rule=no-rule-match
ledger: .../examples/gate_d_ledger.jsonl (6 lines)
exit=0
```

Ledger lines (4 deny, 2 allow):

```json
{"decision": "deny", "rule": "rm-rf-root-or-home", "tool": "Bash", "tool_input": {"command": "rm -rf / --no-preserve-root"}, "tool_use_id": "toolu_synth_01", "ts": "..."}
{"decision": "deny", "rule": "rm-rf-root-or-home", "tool": "Bash", "tool_input": {"command": "mkdir out && rm -rf $HOME/Documents"}, "tool_use_id": "toolu_synth_02", "ts": "..."}
{"decision": "deny", "rule": "aws-access-key-id", "tool": "Write", "tool_input": {"content": "key: [REDACTED-CREDENTIAL]\n", "file_path": "notes/aws.md"}, "tool_use_id": "toolu_synth_03", "ts": "..."}
{"decision": "deny", "rule": "pem-private-key", "tool": "Write", "tool_input": {"content": "[REDACTED-CREDENTIAL]\nMIIE...\n", "file_path": "id.pem"}, "tool_use_id": "toolu_synth_04", "ts": "..."}
{"decision": "allow", "rule": "no-rule-match", "tool": "Bash", "tool_input": {"command": "rm -rf ./build && npm run build"}, "tool_use_id": "toolu_synth_05", "ts": "..."}
{"decision": "allow", "rule": "no-rule-match", "tool": "Edit", "tool_input": {"file_path": "README.md", "new_string": "Shipped 2026-08-30."}, "tool_use_id": "toolu_synth_06", "ts": "..."}
```

## 4. Migration recipe: `~/.rig/departments` onto the SDK (recipe only, no edits made)

Target state: dept runners call the SDK in-process with the gate attached,
instead of shelling out to the `claude` CLI and hoping the hook config fires.
(Reality note: no dept cron-spec on disk was found invoking the `claude` CLI
directly; the recipe applies to any subprocess/`shell=True` agent invocation
found in dept runners, e.g. under `~/.rig/departments/<dept>/`.)

1. **Inventory call sites.** `grep -rn "subprocess\|shell=True" ~/.rig/departments --include="*.py"`
   (and `*.sh`) and classify: agent-CLI invocations vs. ordinary tooling
   subprocess calls. Only the former migrate; the rest stay.
2. **Point runners at the pinned venv.** Each runner script switches from
   spawning the CLI binary to importing from
   `~/Developer/rig-capabilities/.venvs/claude-sdk` (add its `site-packages`
   to `sys.path`, or launch with that venv's interpreter). Pin the SDK version
   (`claude-agent-sdk==0.2.148`) in the runner's requirements header so cron
   drift is detectable.
3. **Attach the gate at construction.** Replace
   `subprocess.run(["claude", "-p", prompt, ...])` with
   `query(prompt=..., options=ClaudeAgentOptions(can_use_tool=gate_d, permission_mode="default", cwd=..., model=...))`
   where `gate_d` is the demo callback, promoted into a shared importable
   module (e.g. `rig_capabilities/gate_d.py`) so every dept shares one rule
   set — the same rules as the hooks, single source of truth.
4. **Keep the hooks during the overlap.** The hooks and the callback are
   idempotent mirrors of each other: hook blocks are a superset-safe subset of
   callback denies for identical payloads, so double enforcement cannot
   double-deny anything the callback allows. Run both for one cron cycle and
   diff the `gate_d_ledger.jsonl` decisions against hook stderr lines; a
   callback-allow + hook-deny row means the mirror drifted — fix the mirror
   before removing the hook for that runner.
5. **Cut over per-dept, keep the ledger as the audit trail.** Flip one low
   stakes dept's cron to the SDK path, let it run a full cadence, verify the
   ledger sealed every tool decision, then roll the pattern dept by dept. The
   hooks stay wired fleet-wide as defense-in-depth for interactive sessions;
   only the headless runners change. Gate-D rule: this migration itself is
   edit-side work under Mike's approval — nothing in this doc has been applied.

## 5. Companion: GitHub Actions lane

`docs/claude-code-action-workflow-example.yaml` mirrors the current documented
usage of `anthropics/claude-code-action` (fetched from the repo on 2026-08-30).
That runner-side surface has no `can_use_tool` equivalent — enforcement there
is `settings`/`claude_args` permission flags plus repo permissions — so the
Actions file is staged as a per-repo adoption candidate pending Gate-D, not
installed.
