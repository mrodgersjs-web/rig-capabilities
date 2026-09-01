"""rig-capabilities — versioned capability store with MCP surface.

v16: 1000x round engine — deterministic upgrades graduated only by green done-tests.
Stdlib only.
"""
__version__ = "16.0.0"
VERSION_LADDER = {
    "2": "catalog + MCP + 4-tier context fabric",
    "3": "drift auto-refresh + observation-decay + ACL policy",
    "4": "local federation + ratings→trust + per-agent workspaces",
    "5": "HMAC signing + public catalog + analytics + SQL/API connectors + HTTP federation + traces",
    "6": "org-IdP HMAC requester tokens + Bearer-authenticated serve + federation auth",
    "7": "skill quality contract (outcome/done_when/great_example/quality_floor)",
    "8": "/skill-upgrades command installed in all 5 harnesses",
    "9": "frontier research corpus ingested as intel assets",
    "10": "great-examples corpus + reference-implementation injection",
    "11": "misc lane burn-down via embedding overlay (898 -> 298)",
    "12": "coverage matrix + per-agent skill packs + capability requests",
    "13": "session-start boot pack + hook comment-metadata contract",
    "14": "Supabase schema + db-sync",
    "15": "runnable done-tests + quality-run scorecards",
    "16": "1000x round engine (graduate-on-green)",
}
