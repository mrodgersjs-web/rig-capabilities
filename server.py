#!/usr/bin/env python3
"""rig-capabilities MCP server — canonical capability store for every harness.

Transport: stdio (newline-delimited JSON-RPC 2.0). Stdlib only — no installs.
Spawned by Claude Code, Codex, OMP, Hermes, and Prime Agent configs; identical
process for all of them (same pattern as jake-pai-mcp).

Session rule the tools enforce: capabilities_search BEFORE authoring anything
new; canonicalize with capability_add, distribute with capability_install.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rig_capabilities.server import build_server  # noqa: E402

if __name__ == "__main__":
    build_server().serve_forever()
