"""rig-capabilities MCP surface: tool definitions + handlers."""
from __future__ import annotations
import json
import os
from pathlib import Path

from .catalog import KINDS, Repo
from .live import live_status
from .mcp_stdio import McpStdioServer, ToolError

NAME = "rig-capabilities"
VERSION = "40.0.0"


# The default corpus scope for `capabilities_converge`. The live corpus roots are
# (~/Downloads, ~/mnt/RIGLake) and ~/mnt/RIGLake is a stale mount — `is_dir()`
# answers True and the walk then dies with TimeoutError around 160 s — so a tool
# that must answer an empty call cannot default to them. This is the committed
# 20-card fixture corpus, and the tool labels its answer `fixture_snapshot`.
FIXTURE_CORPUS_ROOT = "tests/fixtures/fable2031/corpus"
# Four of the five shipped handoff fixtures are bad packets the prefilter must
# REJECT (the CLI exits 2 on each). The fifth, `handoff-honest.json`, is the
# well-formed packet whose offline prefilter passes (CLI exit 0) and which still
# may not be called PASS — that verdict belongs only to the full ladder over a
# git-archive tree at the claimed commit.
DISPATCH_FIXTURES = ("handoff-fabricated.json", "handoff-phantom.json",
                     "handoff-tampered.json", "handoff-isolation.json")
DISPATCH_FIXTURE_HONEST = "handoff-honest.json"


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
                "requester": {"type": "string", "description": "agent id for ACL policy (jake=* )"},
                "token": {"type": "string", "description": "signed requester token; overrides requester when valid"},
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
    {
        "name": "capabilities_refresh",
        "description": (
            "v3 drift report. Compares configured root mtimes to "
            ".last_seen.json. Pass apply=true to rebuild the index if stale."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"apply": {"type": "boolean"}},
        },
    },
    {
        "name": "capabilities_analytics",
        "description": "v5 per-asset pack/rating analytics (writes .context/analytics.json).",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "capabilities_public_catalog",
        "description": "v5 public catalog: assets whose okf.acl contains 'public'.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "capabilities_connectors",
        "description": "SQL/API connector status (configured labels/types + last error).",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "capabilities_observe",
        "description": "Local traces + Langfuse reachability. langfuse=false when unconfigured.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "capabilities_db_sync",
        "description": "Upsert the capability index (+packs/ratings) into Postgres (rig-dev-db). Optional dsn override.",
        "inputSchema": {"type": "object",
                        "properties": {"dsn": {"type": "string"}}},
    },
    {
        "name": "capabilities_test",
        "description": "Run an asset's executable done_when checks (cmd/file/grep/mcp). pass=true only when every runnable check succeeds.",
        "inputSchema": {"type": "object",
                        "properties": {"id": {"type": "string"}},
                        "required": ["id"]},
    },
    {
        "name": "capabilities_round",
        "description": "Run a 1000x improvement round in a lane: canonical assets get deterministic contract upgrades, applied only with green done-tests. Default strategy is informative-first (need x Bernoulli variance), so evaluations go where a change can be observed; strategy='weakest' restores the old score-ascending order. budget caps done-test evaluations and is enforced; skipped candidates come back in 'deferred'. dry=true reports without writing.",
        "inputSchema": {"type": "object",
                        "properties": {"lane": {"type": "string"},
                                       "n": {"type": "integer"},
                                       "dry": {"type": "boolean"},
                                       "budget": {"type": "integer"},
                                       "strategy": {"type": "string",
                                                    "enum": ["informative",
                                                             "weakest"]}}},
    },
    {
        "name": "capabilities_issue_token",
        "description": "Issue an HMAC requester token (org IdP). Requires a signing key.",
        "inputSchema": {
            "type": "object",
            "properties": {"agent": {"type": "string"},
                           "ttl": {"type": "integer", "description": "seconds (default 3600)"}},
            "required": ["agent"],
        },
    },
    {
        "name": "capabilities_certify",
        "description": "Run the deterministic certification gates (suite/index_fresh/done_tests/idp_integrity/acl_jake). plant=true proves each gate fires via copy-tree plant-failure.",
        "inputSchema": {"type": "object",
                        "properties": {"plant": {"type": "boolean"}}},
    },
    {
        "name": "capabilities_agent_pack",
        "description": "Agent packs (24 agents): resolved entries against the live index; boot=true adds live state + done-test verdict per entry; intent= matches agent-shaped queries.",
        "inputSchema": {"type": "object",
                        "properties": {"agent": {"type": "string"},
                                       "boot": {"type": "boolean"},
                                       "intent": {"type": "string"}}},
    },
    {
        "name": "capabilities_gaps",
        "description": "Rank coverage-gap cells and optionally write draft harnesses. apply=false is dry.",
        "inputSchema": {"type": "object",
                        "properties": {"n": {"type": "integer"},
                                       "apply": {"type": "boolean"}}},
    },
    {
        "name": "capabilities_overlay_status",
        "description": "LLM overlay coverage (tagged/target/ollama). Never claims complete on a short file.",
        "inputSchema": {"type": "object",
                        "properties": {"target": {"type": "integer"}}},
    },
    {
        "name": "capabilities_proofchain",
        "description": "Verify ROADMAP packet prefixes against ~/.rig/proof hashes.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "capabilities_goal_spec",
        "description": (
            "Pull the compiled goal spec — the engine-loadable form of a harness. "
            "No args: every goal with gate counts and staleness. stem: one goal. "
            "session_type: resolve by what the session is ('code-review'). "
            "verdict STALE means the harness changed since it was compiled: "
            "recompile before executing the gates it names."
        ),
        "inputSchema": {"type": "object",
                        "properties": {"stem": {"type": "string"},
                                       "session_type": {"type": "string"}}},
    },
    {
        "name": "capabilities_release",
        "description": "Build the public-catalog zip locally. apply=false dry. Does not git-tag or GitHub-release.",
        "inputSchema": {"type": "object",
                        "properties": {"apply": {"type": "boolean"}}},
    },
    {
        "name": "capabilities_quality_report",
        "description": "Skill quality-contract coverage: outcome/done_when/great_example/quality_floor per canonical asset, weakest first.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "capabilities_fabrication",
        "description": (
            "Read-only anti-fabrication report: the fabrication ledger "
            "aggregated over a trailing window (total, fabricated, by_agent, "
            "by_verdict, fabrication_rate — null when the ledger is absent, "
            "never a rate invented from nothing) plus the verdict ladder as "
            "data: who may say what, and that only dispatcher.admit run by a "
            "different-family verifier may ever emit PASS. Seals nothing, "
            "writes nothing, logs nothing."
        ),
        "inputSchema": {"type": "object",
                        "properties": {
                            "since_days": {"type": "integer", "minimum": 1,
                                           "maximum": 3650,
                                           "description": "trailing window (default 30)"}},
                        },
    },
    {
        "name": "capabilities_register",
        "description": (
            "Read-only M0-M5 capability register report: row count, every "
            "validation failure with its reason, the convergence scoreboard "
            "(e_cap / C_t / A_t as exact decimal strings, active vs scored "
            "rows, degenerate targets named), the booked_qualified_conversations "
            "row status with the week's qualified-booking count exactly as "
            "register.load_bookings resolves it (an unresolved qualification "
            "evidence path counts zero and says why), and dC_t versus the "
            "newest sealed week under .context/realign/ — null, never zero, "
            "when no prior week is sealed. Writes no register, runs no week."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "capabilities_evidence",
        "description": (
            "Read-only Evidence Ledger report: every claim with the reasons "
            "this ledger can give it (unknown type/use, confidence out of "
            "range, evidence path that does not resolve) and the ids rule 3 "
            "permits on a resume — computed by evidence_ledger.resume_claims, "
            "so an inferred or planned claim can never be reported resumable. "
            "Writes no ledger rows."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "capabilities_converge",
        "description": (
            "Read-only weekly convergence report: the five-condition weekly "
            "gate verdict for one week (defaults to the current ISO week) with "
            "every failing cause named, the corpus unclassified_rate the gate "
            "refused or accepted, dC_t against the newest sealed week, and the "
            "sealed series. `prev is None` yields BASELINE_ONLY — a first "
            "measurement is never reported as a PASS. Scores through "
            "convergence.score_week, which raises rather than scoring on a "
            "register the classifier cannot place; that refusal is returned as "
            "data, not raised. Runs no week driver, writes no sealed artifact."
        ),
        "inputSchema": {"type": "object", "properties": {
            "week": {"type": "string",
                     "description": "ISO week id (default: the current week)"},
            "bookings_path": {"type": "string",
                              "description": "score against this bookings "
                                             "artifact instead of the week's "
                                             "own path"}},
        },
    },
    {
        "name": "capabilities_dispatch_verify",
        "description": (
            "Read-only handoff-packet prefilter: given a packet path, returns "
            "dispatcher.admit in offline mode — PREFILTER_CLEAR / FABRICATED / "
            "BLOCKED / ISOLATION_BREACH with reasons, checks and the packet "
            "hash — plus the verdict ladder as data. Offline mode NEVER returns "
            "PASS: it re-executes nothing, so it can only fail a packet, never "
            "clear one. With no arguments it returns the ladder, the rules, and "
            "the shipped fixtures with their expected CLI exit codes, so a "
            "done-test can call it empty. It NEVER materialises a checkout and "
            "NEVER mints or rotates a canary; only a different-family verifier "
            "running the full ladder over a git-archive tree at the claimed "
            "commit may emit PASS. An unparseable or missing packet is "
            "returned as data."
        ),
        "inputSchema": {"type": "object", "properties": {
            "packet": {"type": "string",
                       "description": "handoff packet JSON path (repo-relative "
                                      "or absolute)"},
            "verifier_family": {"type": "string",
                                "description": "family of the verifying model "
                                               "(default gpt)"},
            "dispatcher_family": {"type": "string",
                                  "description": "family that ran the work "
                                                 "(default claude)"}},
        },
    },
    {
        "name": "capabilities_wire_mcp",
        "description": (
            "Wire the rig-capabilities MCP server into the four harnesses that "
            "lack it (cursor, gemini, opencode, goose): one entry, in each "
            "config dialect, from one spec. action='plan' (default) returns "
            "per-target states and unified diffs and writes nothing; "
            "action='verify' is the idempotency proof. action='apply' writes "
            "only what the plan changed AND only under a Gate-D approval that "
            "names this action and every target written: without a non-empty "
            "gate_d_run_id it returns gate_d_required and writes nothing; a "
            "gate refusal (missing file, wrong action, target not approved) "
            "comes back as {ok: false, reason}. Already-wired targets are "
            "skipped, so the call is idempotent by construction."
        ),
        "inputSchema": {"type": "object", "properties": {
            "action": {"type": "string", "enum": ["plan", "verify", "apply"],
                       "description": "default plan; apply is dormant without "
                                      "gate_d_run_id"},
            "gate_d_run_id": {"type": "string",
                              "description": "approved Gate-D run naming "
                                             "action mcp-wire (apply only)"},
            "targets": {"type": "array", "items": {"type": "string"},
                        "description": "restrict the write to these targets "
                                       "(cursor, gemini, opencode, goose)"}},
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
                     requester_acl=args.get("requester_acl"),
                     requester=args.get("requester"),
                     token=args.get("token"))

    def graph(args: dict):
        from .fabric import expand
        return expand(repo, [str(args.get("id", ""))],
                      depth=int(args.get("depth", 1)))

    def concepts(args: dict):
        from .fabric import lookup_concept
        res = lookup_concept(repo, str(args.get("concept", "")),
                             int(args.get("limit", 20)))
        return {"concept": args.get("concept"), **res}

    def refresh(args: dict):
        from .refresh import auto_refresh, drift_report
        if args.get("apply"):
            return auto_refresh(repo)
        return drift_report(repo)

    def analytics(_args: dict):
        from .surface import write_analytics
        return write_analytics(repo)

    def public_catalog(_args: dict):
        from .surface import write_public_catalog
        return write_public_catalog(repo)

    def issue_token(args: dict):
        from .idp import issue_token as _issue
        return _issue(repo, str(args.get("agent", "")), ttl=int(args.get("ttl", 3600)))


    def connectors(_args: dict):
        from .connectors import connector_status
        return connector_status(repo)

    def observe(_args: dict):
        from .observe import status as obs_status
        return obs_status(repo)

    def quality_report(_args: dict):
        from .quality import quality_report as _qr
        return _qr(repo)

    def db_sync(args: dict):
        from .sync import sync as _sync
        return _sync(repo, dsn=args.get("dsn") or None)
    def test_asset(args: dict):
        from .done_tests import run_asset
        return run_asset(repo, str(args.get("id", "")))
    def round_lane(args: dict):
        from .rounds import run_round
        return run_round(repo, str(args.get("lane", "misc")),
                         n=int(args.get("n") or 5), dry=bool(args.get("dry")),
                         budget=(int(args["budget"]) if args.get("budget")
                                 is not None else None),
                         strategy=str(args.get("strategy") or "informative"))



    def certify(args: dict):
        from .certify import certify as _certify
        from .certify import self_test
        # self_test copies the tree once per gate and `suite` runs the whole
        # unittest module per copy (law L3): pass `only` through so a caller
        # can plant-failure-prove the gates it means to break.
        return (self_test(repo, only=args.get("only")) if args.get("plant")
                else _certify(repo))

    def agent_pack(args: dict):
        from .packs import boot_pack, match_agent, resolve_pack
        if args.get("intent"):
            return {"matches": match_agent(repo, str(args["intent"]))}
        agent = str(args.get("agent", ""))
        return boot_pack(repo, agent) if args.get("boot") else resolve_pack(repo, agent)

    def gaps(args: dict):
        from .gaps import write_gap_harnesses
        return write_gap_harnesses(repo, n=int(args.get("n") or 8),
                                   apply=bool(args.get("apply")))

    def overlay_status(args: dict):
        from .concepts_llm import overlay_status as _st
        return _st(repo, target=int(args.get("target") or 300))

    def proofchain(_args: dict):
        from .proofchain import verify_roadmap
        return verify_roadmap(repo)

    def release_zip(args: dict):
        from .release import build_public_zip
        return build_public_zip(repo, apply=bool(args.get("apply")))

    # ---- fable2031 read-only surface (P7) --------------------------------
    # These three handlers are literally read-only: no seal_packet, no
    # write_sentinel_evidence, no log_fabrication, no realign.run_week, no
    # model_route.apply. tests/fable2031_tools.py monkeypatches those to
    # raise, so wiring a writer in here fails a test instead of mutating
    # live state from an MCP call.

    def fabrication(args: dict):
        from .afproof import fabrication_rates, verdict_ladder
        days = int(args.get("since_days") or 30)
        return {"read_only": True,
                "rates": fabrication_rates(since_days=days),
                "verdict_ladder": verdict_ladder()}

    def register_state(_args: dict):
        from .convergence import delta, metrics, sealed_series
        from .realign import week_id
        from .register import (BOOKED_ID, RegisterError, bookings_path,
                               load_bookings, load_register, require_booked_row,
                               row_errors)
        rows = load_register(repo)
        try:
            require_booked_row(rows)
            booked = {"id": BOOKED_ID, "row_present": True, "error": None}
        except RegisterError as exc:
            booked = {"id": BOOKED_ID, "row_present": False, "error": str(exc)}
        week = week_id()
        booked["week"] = week
        booked["artifact"] = str(bookings_path(repo, week))
        try:
            doc = load_bookings(bookings_path(repo, week))
            booked["qualified"] = doc["count"]
            booked["records_total"] = doc["total"]
            booked["invalid"] = doc["invalid"]
        except RegisterError as exc:
            booked["qualified"] = None
            booked["error"] = booked["error"] or str(exc)
        board = metrics(rows)
        prior = sealed_series(repo)
        step = None if not prior else delta(prior[-1].get("c_t"), board["c_t"])
        return {"read_only": True,
                "rows_total": len(rows),
                "row_errors": row_errors(rows),
                "metrics": board,
                "booked_qualified_conversations": booked,
                "sealed_weeks": [w.get("week") for w in prior],
                "delta_c_t": None if step is None else
                {"previous": step["prev"], "current": step["cur"],
                 "delta": None if step["delta"] is None else str(step["delta"])}}

    def evidence_state(_args: dict):
        from .evidence_ledger import (LEDGER_PATH, load_ledger, resume_claims,
                                      validate_claim)
        rows = load_ledger(repo)
        resumable = {r.get("id") for r in resume_claims(rows, root=repo.root)}
        return {"read_only": True,
                "ledger": str(repo.root / LEDGER_PATH),
                "rows_total": len(rows),
                "resume_eligible": sorted(i for i in resumable if i),
                "claims": [{"id": r.get("id"), "type": r.get("type"),
                            "confidence": r.get("confidence"),
                            "allowed_use": r.get("allowed_use"),
                            "resume": bool(r.get("id") in resumable),
                            "errors": validate_claim(r, root=repo.root)}
                           for r in rows]}
    def converge_state(args: dict):
        """The weekly gate as data. Never raises, never walks a dead mount.

        `convergence.score_week` recomputes the corpus report over
        `corpus.CORPUS_ROOTS` = (~/Downloads, ~/mnt/RIGLake). ~/mnt/RIGLake is a
        stale mount: `is_dir()` returns True and the walk then dies with
        TimeoutError after ~160 s. An MCP tool called with `{}` must answer, so
        the default scope is the committed fixture corpus and says so; an
        operator who wants the live corpus passes `roots` and gets a refusal as
        data if the mount eats it.
        """
        from . import corpus as corpus_mod
        from .convergence import score_week
        # `CorpusRefusal` lives in corpus; convergence only reaches it through a
        # function-level seam, so importing the real class must go to corpus.
        try:
            from .corpus import CorpusRefusal
        except ImportError:                       # pragma: no cover - P2 absent
            CorpusRefusal = Exception
        from .realign import week_id
        roots = [str(r) for r in (args.get("roots") or [])]
        scope = "operator_supplied" if roots else "fixture_snapshot"
        if not roots:
            roots = [str(FIXTURE_CORPUS_ROOT)]
        week = str(args.get("week") or "") or None
        week = week or week_id()
        try:
            report = corpus_mod.corpus_report(roots=roots)
        except BaseException as exc:            # noqa: BLE001 - reported, not raised
            return {"read_only": True, "week": week, "corpus_scope": scope,
                    "live_corpus_scanned": scope != "fixture_snapshot",
                    "error": f"corpus_scan_failed:{type(exc).__name__}: {exc}",
                    "hint": "pass roots explicitly; ~/mnt/RIGLake is a stale mount"}
        try:
            scored = score_week(repo, report=report, week=week,
                                bookings_path=args.get("bookings_path"))
        except CorpusRefusal as exc:
            return {"read_only": True, "week": week, "corpus_scope": scope,
                    "live_corpus_scanned": scope != "fixture_snapshot",
                    "corpus": {"ok": report.get("ok"), "reason": report.get("reason"),
                               "unclassified_rate": report.get("unclassified_rate")},
                    "refusal": f"corpus_refusal:{exc}",
                    "verdict": None,
                    "note": "no week is scored on a register the classifier cannot place"}
        except Exception as exc:                    # noqa: BLE001 - reported, not raised
            return {"read_only": True, "week": week, "corpus_scope": scope,
                    "error": f"{type(exc).__name__}: {exc}"}
        gate = scored.get("gate", {})
        return {"read_only": True,
                "corpus_scope": scope,
                "live_corpus_scanned": scope != "fixture_snapshot",
                "verdict": gate.get("verdict"),
                "note": ("fixture corpus: verdict is computed on the committed "
                         "20-card snapshot, not the live corpus"
                         if scope == "fixture_snapshot" else None),
                "gate": gate,
                "score": {k: v for k, v in scored.items() if k != "gate"}}

    def dispatch_verify(args: dict):
        """Offline prefilter only: no checkout, no re-execution, no canary turn."""
        from . import dispatcher
        fixtures = repo.root / "tests" / "fixtures" / "fable2031"
        ladder = {
            "prefilter": ("this tool — mechanical packet checks; emits "
                          "FABRICATED / BLOCKED / FAIL, never PASS"),
            "full_ladder": ("dispatcher.admit(verify=True) run by a "
                            "different-family verifier over a git-archive tree "
                            "at the claimed commit — the ONLY emitter of PASS"),
            "fleet_status": ("Sentinel Prime is specification-only, so fleet "
                             "status stays BLOCKED_PENDING_SENTINEL"),
        }
        src = str(args.get("packet") or "").strip()
        if not src:
            return {"read_only": True, "mode": "no_packet",
                    "verdict": None, "ladder": ladder,
                    "rules": ["claim_locked_violation: a packet may only claim "
                              "SUBMITTED_FOR_VERIFICATION",
                              "a truthful canary non-zero is admission evidence "
                              "and is never fed to TAC",
                              "PASS requires verifier family != dispatcher family"],
                    "fixtures": ([{"packet": str(fixtures / n), "expected_exit": 2}
                                  for n in DISPATCH_FIXTURES]
                                 + [{"packet": str(fixtures / DISPATCH_FIXTURE_HONEST),
                                     "expected_exit": 3,
                                     "note": "the prefilter declines to refute it; "
                                             "PASS still requires the full ladder"}]),
                    "hint": "pass packet for the offline prefilter verdict"}
        path = Path(src)
        if not path.is_absolute():
            path = repo.root / src
        if not path.is_file():
            return {"read_only": True, "mode": "offline_prefilter", "packet": src,
                    "error": "packet_missing", "verdict": None, "expected_exit": 2}
        try:
            packet = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return {"read_only": True, "mode": "offline_prefilter", "packet": src,
                    "error": f"packet_not_json:{exc}", "verdict": None,
                    "expected_exit": 2}
        try:
            out = dispatcher.admit(
                packet, None,
                family_of_verifier=str(args.get("verifier_family") or "gpt"),
                family_of_dispatcher=str(args.get("dispatcher_family") or "claude"),
                reexec=None, offline=True)
        except dispatcher.AdmissionError as exc:
            return {"read_only": True, "mode": "offline_prefilter", "packet": src,
                    "error": str(exc), "verdict": None, "expected_exit": 2}
        out["read_only"] = True
        out["mode"] = "offline_prefilter"
        out["checkout_performed"] = False
        out["reexecution_performed"] = False
        out["ladder"] = ladder
        if out.get("verdict") == "PASS":
            # Unreachable while `admit` holds its invariant, and deliberately not
            # silent if that ever changes: an offline PASS is the exact defect this
            # rung exists to prevent, so it is surfaced rather than forwarded.
            out["invariant_violation"] = "offline_pass_emitted"
            out["verdict"] = "BLOCKED"
        return out


    def goal_spec_tool(args: dict):
        """Serve compiled goals. Read-only, repo-rooted, staleness-aware.

        Exposing a goal without a staleness verdict would let an agent run gates
        that the harness no longer declares, so the source hash pinned at compile
        time is checked against the live file on every read.
        """
        from . import goal_spec
        return goal_spec.serve(Path(repo.root),
                               stem=str(args.get("stem") or ""),
                               session_type=str(args.get("session_type") or ""))

    def wire_mcp(args: dict):
        """Project the server entry into four harness configs.

        Dormant-by-default: apply needs a Gate-D run id naming this action,
        and the refusal mirrors the CLI shape so neither surface can drift
        into silently writing a config.
        """
        from . import mcp_wire
        action = str(args.get("action") or "plan")
        run_id = str(args.get("gate_d_run_id") or "").strip()
        if run_id.startswith("APPROVE "):
            # Accept the literal approval phrase as well as the bare run_id.
            run_id = run_id[len("APPROVE "):].strip()
        if action == "apply":
            if not run_id:
                return {"ok": False, "writes": 0, "action": "mcp-wire",
                        "reason": "gate_d_required",
                        "hint": "re-run with gate_d_run_id naming an approved "
                                "Gate-D run that lists the targets to write"}
            targets = [str(t) for t in (args.get("targets") or [])] or None
            try:
                return mcp_wire.apply(run_id, targets_only=targets)
            except mcp_wire.WireGateError as exc:
                return {"ok": False, "writes": 0, "reason": str(exc)}
        if action == "verify":
            return mcp_wire.verify()
        return mcp_wire.plan()


    handlers = {
        "capabilities_search": search,
        "capabilities_get": get,
        "capabilities_list": lst,
        "capability_install": install,
        "capability_add": add,
        "capabilities_stats": stats,
        "capabilities_reindex": reindex,
        "capabilities_certify": certify,
        "capabilities_agent_pack": agent_pack,
        "capabilities_live_status": live,
        "capabilities_outcomes": outcomes,
        "capabilities_route": route,
        "capabilities_context_pack": context_pack,
        "capabilities_graph": graph,
        "capabilities_concepts": concepts,
        "capabilities_refresh": refresh,
        "capabilities_analytics": analytics,
        "capabilities_public_catalog": public_catalog,
        "capabilities_connectors": connectors,
        "capabilities_observe": observe,
        "capabilities_test": test_asset,
        "capabilities_round": round_lane,
        "capabilities_db_sync": db_sync,
        "capabilities_issue_token": issue_token,
        "capabilities_quality_report": quality_report,
        "capabilities_gaps": gaps,
        "capabilities_overlay_status": overlay_status,
        "capabilities_proofchain": proofchain,
        "capabilities_release": release_zip,
        "capabilities_fabrication": fabrication,
        "capabilities_register": register_state,
        "capabilities_evidence": evidence_state,
        "capabilities_converge": converge_state,
        "capabilities_dispatch_verify": dispatch_verify,
        "capabilities_goal_spec": goal_spec_tool,
        "capabilities_wire_mcp": wire_mcp,
    }
    return McpStdioServer(NAME, VERSION, TOOLS, handlers)
