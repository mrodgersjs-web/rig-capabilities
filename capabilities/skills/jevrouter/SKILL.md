---
name: jevrouter
description: Use Jev to choose the next tool, model, or subagent when a task has competing capability choices, the user asks for routing, or the next step is uncertain. Use the real current task and available candidates.
---

# JevRouter

Announce “JevRouter: routing the next step” when starting. A past setup check is not a routing decision for the current task.

At the first meaningful capability choice, and again when an observation changes the next step, gather the tools/models/subagents actually available to this host. Submit the current task and at least two plausible choices; exclude JevRouter itself. Keep exact host tool names. Never reuse a GitHub example catalog for an unrelated task or invent unavailable model/subagent IDs. Skip trivial chat and steps whose sole permitted operation the user has already specified.

In Aside, prefer the registered native MCP tool `mcp__jevrouter__jev_route`. Pass one object with `request`, `context`, and `candidates`. `candidates` is an array of capability objects, not a JSON string. Each MCP candidate requires `id`, `name`, and `type`. The exact `type` enum is `skill`, `mcp_tool`, `cli`, `dsh`, `model`, or `subagent`. Use the current task and the exact available capability names. The native MCP server runs the canonical helper with `serve-mcp` and returns the routing decision to Aside.

This payload uses the observed Aside host tools `read_file` and `bash`. `mcp_tool` is their routing category. Replace the request and candidates with the current task and tools available in the current host.

```json
{
  "request": "Read a known local startup file without changing it",
  "context": {"next_step": "Read the known local startup file"},
  "candidates": [
    {
      "id": "read_file",
      "name": "read_file",
      "type": "mcp_tool",
      "description": "Read the known local file directly"
    },
    {
      "id": "bash",
      "name": "bash",
      "type": "mcp_tool",
      "description": "Run a read-only shell check of the file"
    }
  ]
}
```

If the MCP tool is unavailable, report the missing connection and defer routing. Do not assume sandbox Node can access the native JevRouter distribution or credentials. An SSH bridge is optional only when that session has verified native SSH access, including host trust and authentication. Reading an installed skill does not prove either access path works.

In OMP's native runtime, use the canonical CLI helper with the same request object on stdin.

```sh
node '/Users/rig128gb/Developer/rig-capabilities/capabilities/skills/jevrouter/scripts/route.mjs' route --stdin <<'JEV_INPUT'
{
  "request": "Find the latest interview and retrieve its original source",
  "context": {"next_step": "Find the source before summarizing it"},
  "candidates": [
    {"name": "web_search", "description": "Find current web sources"},
    {"name": "summarize", "description": "Summarize sources already retrieved"}
  ]
}
JEV_INPUT
```

The native helper uses an inherited `JEV_API_KEY` or `TYPESAFE_API_KEY`, then the native macOS Keychain service `com.rig.env.TYPESAFE_API_KEY`, then `~/.rig/s1gate/env`. `S1GATE_ENV_FILE` overrides the fallback file path. The file must be a regular file owned by the current user with no group or other access. Symlinks are rejected. The helper reads credential assignments without shell evaluation and supplies the credential only through the native CLI's environment. Missing credentials fail closed. There is no automatic demo fallback. Never print keys or put them in arguments.

The names above illustrate the shape: replace the task and candidates with this turn's real capabilities. Model/subagent candidates use `{id,name,type,description}` with `type: model` or `subagent`. CLI also accepts `--request` with `--candidates-file` for JSON/YAML, and SDK users can call `route({request,candidates})`.

Read the MCP tool result or the CLI JSON on stdout. CLI progress is on stderr. State the returned `decision_id`, `status`, `decision.selected`, and whether the provider was live or demo. If `status=selected`, execute only that available capability through the host's own permission checks. If confirmation is required, obtain it first. On `no_decision`, invalid input, missing credentials, or network error, explain the fallback and gather better inputs; never describe a failed or demo call as live Jev routing. CLI exit codes: 0 selected, 2 review/no-decision, 1 error.

After execution, include the observation in the next routing request when needed. Routing is `decision_only`. It does not authorize execution, call `setModel`, switch the host's underlying model, spawn agents, or execute returned IDs automatically. Do not recurse into routing the router or run routing again just to make status green.

Always respect project instructions and host authorization.
