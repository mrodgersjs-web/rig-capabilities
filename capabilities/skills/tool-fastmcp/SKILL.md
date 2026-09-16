---
name: tool-fastmcp
description: Build typed MCP Python servers for Design Harness tool adapters using the installed MCP SDK 2.x API.
outcome: "code-engineering: Tools component adapters expose narrow typed actions through MCPServer with version-correct tools and resources"
done_when:
  - cmd:/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "import importlib.metadata as m; assert m.version('mcp') == '2.2.0'; from mcp.server.mcpserver import MCPServer; assert MCPServer('check').name == 'check'"
great_example: "A Tools component exposes one MCPServer tool per deterministic action, with resource reads separate from mutations and no model call hidden inside the server."
quality_floor: 0.7
relates_to: rig-design-harness
provenance: "local:/Users/rig128gb/.claude/skills/zazen-fastmcp-server + authored-2026-09-16 (mcp 2.x update)"
---

# tool-fastmcp

## Role in our stack

The harness uses MCP Python SDK 2.2.0 in the **Tools** component. In v2, `FastMCP` was renamed to `MCPServer`; the local `zazen-fastmcp-server` source is mcp<2-era and is retained for feature concepts only. All executable guidance here uses `mcp.server.mcpserver.MCPServer`.

## Verified snippets

### 1. Construct a server

```python
from mcp.server.mcpserver import MCPServer
server = MCPServer("rig-server")
assert server.name == "rig-server"
```

Verified against harness mcp 2.2.0: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/fastmcp/verify.py 1` → exit 0.

### 2. Register a tool

```python
from mcp.server.mcpserver import MCPServer
server = MCPServer("rig-tools")

@server.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

assert add(2, 3) == 5
```

Verified: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/fastmcp/verify.py 2` → exit 0.

### 3. Register a resource

```python
server = MCPServer("rig-resources")

@server.resource("config://status")
def status() -> str:
    return "green"
```

Verified: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/fastmcp/verify.py 3` → exit 0.

## Pitfalls

- `from mcp.server.fastmcp import FastMCP` is a v1 import and fails on mcp 2.x.
- Transport options moved from the constructor to `run_*` methods in v2.
- Sync handlers execute on a worker thread; do not assume an event loop exists inside `def` handlers.
- Keep sampling out of deterministic tools unless an explicit runtime decision needs a model.

## Planted failure

The obsolete v1 import is the permanent migration canary:

```bash
/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "from mcp.server.fastmcp import FastMCP"
```

Expected: non-zero `ModuleNotFoundError` pointing to the v2 migration guide.
