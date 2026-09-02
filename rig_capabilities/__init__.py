"""rig-capabilities — versioned capability store with MCP surface.

v50: Discover AI capability increment — catalog truncation guard, phantom-asset
scanner fix, round verdict propagation, evidence/contract/identity/lifecycle/topology
surfaces. VERSION_LADDER 1–50.

50.1.0 adds the two read-only surface tools that put those verdicts where an
agent can actually call them: `capabilities_asset_hygiene` and
`capabilities_verdict` (`rig_capabilities/surface_tools.py`). Minor, not a new
ladder rung: no ROADMAP row or proof packet rides on it yet, so the major stays
pinned to rung 50 by `tests.test_version_coherence`.
Stdlib only.
"""
__version__ = "50.1.0"
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
    "17": "scraper-corpus intel root (mtime freshness)",
    "18": "live cross-node federation (token_file)",
    "19": "LLM concept overlay (honest tiers)",
    "20": "verified requesters (idp tokens in pack traces)",
    "21": "stats.json + dashboard panel",
    "22": "certify gates + plant-failure self-test",
    "23": "agent packs + boot packs + pack-first context",
    "24": "canonical commands + certify MCP tool + installer command delivery",
    "25": "OMP+Prime hook roots + installer hook delivery + live-on-presence",
    "26": "gap harness drafts from requests.jsonl",
    "27": "traces panel (aggregates, no payloads)",
    "28": "public zip builder (dormant, Gate-D gd_1788227314643)",
    "29": "Layer-Isolated certify in the unit suite (no nested suite)",
    "30": "ROADMAP evidence table + proof-chain",
    "31": "gate_d.evaluate library (no SDK)",
    "32": "canonical command/hook public ACL default",
    "33": "commands delivered to hermes/omp/agents/prime",
    "34": "overlay doctor (honest 62/300)",
    "35": "harness-install GoalSpecs (dry default)",
    "36": "proofchain ROADMAP prefixes vs ~/.rig/proof",
    "37": "MCP gaps/overlay_status/proofchain/release",
    "38": "stats public_assets + gate_d_cases",
    "39": "ROADMAP V28 ARMED + Wave 4 rows",
    "40": "Wave 4 close",
    # 41–49 were documented in docs/ROADMAP.md with their own proof packets but
    # never entered the ladder, so `/version`, `stats`, the release zip name and
    # the MCP `initialize` handshake all advertised 40.0.0 for nine shipped
    # increments. `tests.test_catalog.RoadmapTests` now pins the three in a
    # cycle, so the constant and the document cannot drift apart again.
    "41": "P0/P1 intent + question layer: DONE-CONTRACT-2031, TRUNCATED-SOURCES, CONFLICT-RESOLUTIONS, ASSUMPTIONS",
    "42": "P2 deterministic corpus scanner + source inventory + classify rules",
    "43": "P3 M0–M5 capability register + C_t/A_t/RobustMADZ + weekly gate",
    "44": "P3b Known Expert OS phase harness + claim-typed evidence ledger",
    "45": "P4 worktree leases, rotating canary, dispatcher packet, mechanical denial",
    "46": "P5 E_stage promotion gate + golden replay corpus",
    "47": "P5b dormant-by-default Fable 5.1 model route",
    "48": "P6 IQRSQPI v10 executable stage machine + anti-fabrication proof layer",
    "49": "P7/P8 certify-gate wiring (12 gates), 14 CLI verbs, 5 read-only tools",
    "50": "Discover AI increment: frontmatter-visibility gate (canonical + external), "
          "directory assets need SKILL.md, round exit_code -> CLI rc + MCP isError, "
          "done_when ran/unrunnable accounting, exemplar-resolution ratchet, "
          "paired-run/skill-contract/acceptance-identity/lifecycle/topology surfaces",
}
