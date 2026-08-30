"""rig-capabilities MCP surface: tool definitions + handlers."""
from __future__ import annotations

import os
from pathlib import Path

from .catalog import KINDS, Repo
from .live import live_status
from .mcp_stdio import McpStdioServer, ToolError

NAME = "rig-capabilities"
VERSION = "0.1.0"


def default_repo() -> Repo:
    env = os.environ.get("RIG_CAP_REPO")
    if env:
        return Repo(Path(env))
    return Repo(Path(__file__).resolve().parent.parent)


TOOLS = [
    {
        "name": "capabilities_search",
        "description": (
            "Search EVERY capability across the canonical rig-capabilities repo and all "
            "installed harness roots (~/.claude, ~/.codex, ~/.hermes, ~/.agents: skills, "
            "agents, hooks, goal harnesses, loops, commands). USE THIS BEFORE authoring a "
            "new skill/agent/hook or recommending an install — canonical repo entries rank "
            "above installed ones. Returns id, kind, source location, description, score."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "capability keywords"},
                "kind": {"type": "string", "enum": list(KINDS),
                         "description": "restrict to one kind"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100,
                          "description": "max results (default 20)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "capabilities_get",
        "description": (
            "Fetch one capability by id: metadata (source, path, sha, installable) plus "
            "its content (first ~40KB). If the id exists in several sources, all copies "
            "are listed and the canonical one is preferred."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "string"}},
            "required": ["id"],
        },
    },
    {
        "name": "capabilities_list",
        "description": ("List capabilities filtered by kind and/or source. "
                        "source='canonical' lists only this repo's governed assets."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "kind": {"type": "string", "enum": list(KINDS)},
                "source": {"type": "string", "description": "repo label, e.g. canonical"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 500},
            },
        },
    },
    {
        "name": "capability_install",
        "description": (
            "Install a CANONICAL capability from this repo into a harness root "
            "(claude|codex|hermes|agents|omp). Copies the asset and records a ledger entry. "
            "Refuses if the target exists and differs unless force=true (old copy is "
            "backed up as <name>.bak-<ts>). External assets must be canonicalized with "
            "capability_add first."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "harness": {"type": "string",
                            "enum": ["claude", "codex", "hermes", "agents", "omp"]},
                "force": {"type": "boolean", "description": "overwrite differing target"},
            },
            "required": ["id", "harness"],
        },
    },
    {
        "name": "capability_add",
        "description": (
            "Canonicalize an asset into this repo (git-version it): copy any file or "
            "directory (e.g. a skill/agent/hook already installed in a harness root, or a "
            "vendored OSS skill) into capabilities/<kind>/ and rebuild the index. This is "
            "how a capability becomes installable, deduped (canonical shadows same-id "
            "externals), and under version control."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "canonical id (slug)"},
                "kind": {"type": "string", "enum": list(KINDS)},
                "source_path": {"type": "string",
                                "description": "file or directory to import (~ expanded)"},
                "overwrite": {"type": "boolean"},
            },
            "required": ["id", "kind", "source_path"],
        },
    },
    {
        "name": "capabilities_stats",
        "description": ("Counts by kind and source, index freshness, and the install "
                        "ledger — the fleet-overview call."),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "capabilities_reindex",
        "description": ("Force a rescan of the repo and every external root (picks up "
                        "manual additions). Returns new counts."),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "capabilities_live_status",
        "description": (
            "Runtime evidence for canonical capabilities and named infra "
            "services — the answer to 'is it actually wired/running', not "
            "'does a file exist'. Hooks: registered in live settings.json? "
            "Skills/agents/harnesses: installed into a live harness root? "
            "Commands: on PATH? Services: port bound AND identity-matched "
            "(port open but owned by a different process reports 'hijacked'). "
            "States: wired | dormant | absent | down | hijacked | unknown. "
            "Call with no args for the fleet report, or pass an id for one asset."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "capability id (omit for fleet report)"},
                "services": {"type": "boolean", "description": "include infra port probes (default true)"},
            },
        },
    },
    {
        "name": "capabilities_outcomes",
        "description": (
            "Outcome lanes across the whole estate (security-review, "
            "revenue-gtm, content-publishing, design-ux, media-production, "
            "docs-knowledge, research-intel, data-analytics, infra-ops, "
            "code-engineering, business-ops, agent-engineering, misc) with "
            "per-kind counts. The browse map for the generated tree/ view."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "capabilities_route",
        "description": (
            "Intent router: give a natural-language outcome ('cold email "
            "outreach for dentists', 'add a failing test harness') and get "
            "ranked outcome lanes each with the top matching capabilities "
            "(id/kind/source). Use before search when the task is 'what do "
            "I have for X?' rather than 'find the string X'."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "the outcome you want"},
                "per": {"type": "integer", "description": "capabilities per lane (default 5)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "capabilities_context_pack",
        "description": (
            "CONTEXT FABRIC — the default entry point for any task that "
            "needs ecosystem knowledge. Fuses BM25 + ollama nomic-embed "
            "dense + outcome-lane routing + graph expansion into a "
            "task-minimal, trust- and freshness-filtered context pack with "
            "per-bundle provenance (source, path, sha, trust, freshness). "
            "Assembles a runtime context graph and persists it under "
            ".context/ for feedback (capability_rate_pack). Use instead of "
            "raw search when the agent should not scavenge the filesystem."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "intent": {"type": "string", "description": "what the agent is about to do"},
                "budget_tokens": {"type": "integer", "description": "max context tokens (default 1500)"},
                "max_nodes": {"type": "integer", "description": "max capability nodes (default 12)"},
                "min_trust": {"type": "number", "description": "okf trust floor 0..1 (default 0.5)"},
            },
            "required": ["intent"],
        },
    },
    {
        "name": "capabilities_graph",
        "description": (
            "Capability graph adjacency (declared relates_to + shared-token "
            "edges) expanded to depth 1-2 from one id. Use to widen or "
            "verify context around a specific asset."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "depth": {"type": "integer", "description": "1 or 2 (default 1)"},
            },
            "required": ["id"],
        },
    },
    {
        "name": "capabilities_concepts",
        "description": "Concept index lookup: normalized tag/term -> capability ids.",
        "inputSchema": {
            "type": "object",
            "properties": {"concept": {"type": "string"},
                           "limit": {"type": "integer"}},
            "required": ["concept"],
        },
    },
]


def _fmt_row(a: dict) -> dict:
    return {"id": a["id"], "kind": a["kind"], "source": a["source"],
            "name": a["name"], "description": a["description"][:180],
            "path": a["path"]}


def build_server(repo: Repo | None = None) -> McpStdioServer:
    repo = repo or default_repo()

    def search(args: dict):
        rows = repo.search(str(args.get("query", "")),
                           kind=args.get("kind"),
                           limit=int(args.get("limit", 20)))
        return {"count": len(rows), "results": [
            {"score": r["score"], **_fmt_row(r)} for r in rows]}

    def get(args: dict):
        matches = repo.resolve(str(args.get("id", "")))
        if not matches:
            raise ToolError("no capability named '%s'. Try capabilities_search first."
                            % args.get("id"))
        pick = next((m for m in matches if m["source"] == "canonical"), matches[0])
        out = {"matches": [_fmt_row(m) for m in matches], "chosen": _fmt_row(pick),
               "installable": pick["installable"], "sha": pick["sha"],
               "content": repo.content(pick["abs_path"])}
        return out

    def lst(args: dict):
        doc = repo.load_index()
        rows = [a for a in doc["assets"]
                if (not args.get("kind") or a["kind"] == args["kind"])
                and (not args.get("source") or a["source"] == args["source"])]
        lim = int(args.get("limit", 100))
        return {"count": len(rows), "shown": min(len(rows), lim),
                "results": [_fmt_row(a) for a in rows[:lim]]}

    def install(args: dict):
        try:
            return repo.install(str(args.get("id", "")), str(args.get("harness", "")),
                                force=bool(args.get("force")))
        except ValueError as exc:
            raise ToolError(str(exc))

    def add(args: dict):
        try:
            return repo.add(str(args.get("id", "")), str(args.get("kind", "")),
                            str(args.get("source_path", "")),
                            overwrite=bool(args.get("overwrite")))
        except ValueError as exc:
            raise ToolError(str(exc))

    def stats(args: dict):
        return repo.stats()

    def reindex(args: dict):
        doc = repo.build_index()
        return {"generated_at": doc["generated_at"], "total": doc["count"]}

    def live(args: dict):
        return live_status(repo, id=args.get("id"),
                           services=bool(args.get("services", True)))

    def outcomes(args: dict):
        from .taxonomy import dedupe, outcome_counts
        return {"lanes": outcome_counts(dedupe(repo.load_index()["assets"]))}

    def route(args: dict):
        from .taxonomy import route as _route
        return _route(repo, str(args.get("query", "")),
                      per=int(args.get("per", 5)))
    def context_pack(args: dict):
        from .fabric import context_pack as _pack
        return _pack(repo, str(args.get("intent", "")),
                     budget_tokens=int(args.get("budget_tokens", 1500)),
                     max_nodes=int(args.get("max_nodes", 12)),
                     min_trust=float(args.get("min_trust", 0.5)),
                     requester_acl=args.get("requester_acl"))

    def graph(args: dict):
        from .fabric import expand
        return expand(repo, [str(args.get("id", ""))],
                      depth=int(args.get("depth", 1)))

    def concepts(args: dict):
        from .fabric import lookup_concept
        return {"concept": args.get("concept"),
                "ids": lookup_concept(repo, str(args.get("concept", "")),
                                      int(args.get("limit", 20)))}

    handlers = {
        "capabilities_search": search,
        "capabilities_get": get,
        "capabilities_list": lst,
        "capability_install": install,
        "capability_add": add,
        "capabilities_stats": stats,
        "capabilities_reindex": reindex,
        "capabilities_live_status": live,
        "capabilities_outcomes": outcomes,
        "capabilities_route": route,
        "capabilities_context_pack": context_pack,
        "capabilities_graph": graph,
        "capabilities_concepts": concepts,
    }
    return McpStdioServer(NAME, VERSION, TOOLS, handlers)
