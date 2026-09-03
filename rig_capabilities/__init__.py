"""rig-capabilities — versioned capability store with MCP surface.

v52: the 2031 capability increment set, realigned onto main's published ladder.
VERSION_LADDER 1–52.

The 2031 rungs were authored as 41–50 while main independently published
Loop-Skill Contract v11 and IQRSQPI v20 as 41/42. Realignment keeps main's
published numbers and shifts the 2031 rungs to 43–51; docs/ROADMAP.md, the
ladder below and `tests.test_version_coherence` are pinned in a cycle.
Stdlib only.
"""
__version__ = "47.0.0"
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
    "36": "proofchain 16/16 prefixes found",
    "37": "MCP gaps/overlay_status/proofchain/release",
    "38": "stats public_assets + gate_d_cases",
    "39": "ROADMAP V28 ARMED + Wave 4 rows",
    "40": "Wave 4 close",
    "41": "Loop-Skill Contract v11: rig-loop engine, IQRSQPI v11 + 6 core doctrine loop-skills, hooks wired in 5 harnesses",
    "42": "IQRSQPI v20: done-tests executed, Q<->R dryness gate, child slice runs, cross-family verifier dispatch, calibration ledger, handoff; /iqrsqpi in 5 harnesses",
    # The 2031 rungs shipped on the fable-2031 branch numbered 41–50, colliding
    # with the two rungs main had already published. Realignment keeps main's
    # numbers; the branch's rungs shift +2.
    "43": "P0/P1 intent + question layer: DONE-CONTRACT-2031, TRUNCATED-SOURCES, CONFLICT-RESOLUTIONS, ASSUMPTIONS",
    "44": "P2 deterministic corpus scanner + source inventory + classify rules",
    "45": "P3 M0–M5 capability register + C_t/A_t/RobustMADZ + weekly gate",
    "46": "P3b Known Expert OS phase harness + claim-typed evidence ledger",
    "47": "P4 worktree leases, rotating canary, dispatcher packet, mechanical denial",
    "48": "P5 E_stage promotion gate + golden replay corpus",
    "49": "P5b dormant-by-default Fable 5.1 model route",
    "50": "P6 IQRSQPI v10 executable stage machine + anti-fabrication proof layer",
    "51": "P7/P8 certify-gate wiring (12 gates), 14 CLI verbs, 5 read-only tools",
    "52": "Discover AI increment: frontmatter-visibility gate (canonical + external), "
          "directory assets need SKILL.md, round exit_code -> CLI rc + MCP isError, "
          "done_when ran/unrunnable accounting, exemplar-resolution ratchet, "
          "paired-run/skill-contract/acceptance-identity/lifecycle/topology surfaces",
}
