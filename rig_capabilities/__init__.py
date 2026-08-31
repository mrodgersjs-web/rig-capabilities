"""rig-capabilities — versioned capability store with MCP surface.

v13: session-start boot pack on all harnesses; hook frontmatter bug fixed.
Stdlib only.
"""
__version__ = "13.0.0"
VERSION_LADDER = {
    "2": "catalog + MCP + 4-tier context fabric",
    "3": "drift auto-refresh + observation-decay + ACL policy",
    "4": "local federation + ratings→trust + per-agent workspaces",
    "5": "HMAC signing + public catalog + analytics + SQL/API connectors + HTTP federation + traces",
}
