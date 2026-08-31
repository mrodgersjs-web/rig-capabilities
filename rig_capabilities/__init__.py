"""rig-capabilities — versioned capability store with MCP surface.

v8: /skill-upgrades canonicalized and installed into all 5 harnesses.
Stdlib only.
"""
__version__ = "8.0.0"
VERSION_LADDER = {
    "2": "catalog + MCP + 4-tier context fabric",
    "3": "drift auto-refresh + observation-decay + ACL policy",
    "4": "local federation + ratings→trust + per-agent workspaces",
    "5": "HMAC signing + public catalog + analytics + SQL/API connectors + HTTP federation + traces",
}
