"""rig-capabilities — versioned capability store with MCP surface.

v5: catalog + context fabric + drift/ACL/decay + federation + signed packs.
Stdlib only.
"""
__version__ = "5.0.0"
VERSION_LADDER = {
    "2": "catalog + MCP + 4-tier context fabric",
    "3": "drift auto-refresh + observation-decay + ACL policy",
    "4": "local federation + ratings→trust + per-agent workspaces",
    "5": "HMAC pack signing + public catalog + per-asset analytics",
}
