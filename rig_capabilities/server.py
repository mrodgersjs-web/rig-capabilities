"""rig-capabilities MCP surface: tool definitions + handlers."""
from __future__ import annotations
import getpass
import hashlib
import json
import os
from pathlib import Path
from . import __version__
from . import surface_tools
from .catalog import KINDS, Repo
from .live import live_status
from . import comms_bridge
from .mcp_stdio import McpStdioServer, ToolError

NAME = "rig-capabilities"
# One source. This constant duplicated `rig_capabilities.__version__` and then
# went stale by nine shipped rungs, so every MCP `initialize` handshake
# advertised 40.0.0. `tests.test_version_coherence` pins the equality.
VERSION = __version__


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
        "name": "capabilities_build_store",
        "description": "Read-only rig_build status: both planes (record, measure) probed for "
                       "configuration/reachability, outbox total+pending, effective role. "
                       "configured=false is honest UNCONFIGURED, never a fabricated pass.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "capabilities_measure_quorum",
        "description": "Qualification evidence for one lattice cell: attempt count, durable "
                       "count, span hours, and the stored qualification record if any.",
        "inputSchema": {"type": "object",
                        "properties": {"cell": {"type": "string"}},
                        "required": ["cell"]},
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
            "action": {"type": "string",
                       "enum": ["plan", "verify", "selftest", "apply"],
                       "description": "default plan; selftest is a dry per-target "
                                      "capability-pull proof; apply is dormant "
                                      "without gate_d_run_id"},
            "gate_d_run_id": {"type": "string",
                              "description": "approved Gate-D run naming "
                                             "action mcp-wire (apply only)"},
            "targets": {"type": "array", "items": {"type": "string"},
                        "description": "restrict the write to these targets "
                                       "(cursor, gemini, opencode, goose)"}},
        },
    },
    {
        "name": "capabilities_asset_hygiene",
        "description": (
            "What the estate cannot see about itself, in one call. Runs three "
            "committed scanners through their own main() and reports: every "
            "declared great_example path that does not resolve (with "
            "declared/resolved/dangling), any asset whose frontmatter is longer "
            "than catalog.HEAD_BYTES and therefore invisible to the loader "
            "(clean/other_unloaded/truncation_hidden), and the six-slot skill "
            "contract tally over `scope` (default `capabilities`). "
            "`ran` means all three reported; `clean` means none of them found "
            "debt. Debt is named in `debt`, never folded into a pass and never "
            "into a refusal. Read-only: no writes, no network, no model."
        ),
        "inputSchema": {"type": "object", "properties": {
            "scope": {"type": "string",
                      "description": "repo-relative subtree for the contract "
                                     "scan; default capabilities. Anything "
                                     "outside the repo is refused."}},
        },
    },
    {
        "name": "capabilities_verdict",
        "description": (
            "One verdict from one verdict module, through that module's own CLI "
            "path, so the answer cannot disagree with `./bin/rig-capabilities`. "
            "check: paired_runs (adjudicate a paired-run ledger: argv = [ledger]; "
            "verdicts CORRELATED/DETERMINISTIC/MIXED/INCONCLUSIVE), skill_contract "
            "(argv = [path...]; six-slot A/I/C/P/pi/E declarations), "
            "acceptance_identity (argv = [record]; stamps who ran and who "
            "verified, and refuses self-verification — it never writes the stamp "
            "here), lifecycle (argv = [plan, --example|--assets F, --now D, "
            "[--plant P]]), topology (argv = [validate, path, [--mutate M, "
            "[--expect PREFIX]] | [dispatch, path, src, dst, payload]). "
            "Relative paths are repo-relative. `ran` is not `clean`: exit 1 "
            "means it ran and found debt, exit >=2 means it refused. Read-only."
        ),
        "inputSchema": {"type": "object", "properties": {
            "check": {"type": "string",
                      "enum": ["paired_runs", "skill_contract",
                               "acceptance_identity", "lifecycle", "topology"]},
            "argv": {"type": "array", "items": {"type": "string"},
                     "description": "tokens the named module expects, minus the "
                                    "program name; repo-relative paths only"}},
            "required": ["check"],
        },
    },
    # --- Communications OS (rig_comms runtime, deterministic, no LLM) ---
    {
        "name": "capabilities_comms_surfaces",
        "description": "surface registry: lanes, engines, deviation budgets, AGF floors",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "capabilities_comms_route",
        "description": "route a natural-language writing intent to a ranked surface list",
        "inputSchema": {"type": "object", "properties": {
            "intent": {"type": "string"}}, "required": ["intent"]},
    },
    {
        "name": "capabilities_comms_packet",
        "description": "assemble the deterministic drafting context packet for a surface; "
                       "private lane refuses without human:true (PRIVACY_LOCK)",
        "inputSchema": {"type": "object", "properties": {
            "surface": {"type": "string"}, "brief": {"type": "string"},
            "persona": {"type": "string"},
            "human": {"type": "boolean",
                      "description": "assert human-directed write (private lane only)"}},
            "required": ["surface", "brief"]},
    },
    {
        "name": "capabilities_comms_score",
        "description": "run the deterministic gate stack (voice, fingerprint, gates) over an "
                       "artifact; can_ship=false lists the blocking reasons",
        "inputSchema": {"type": "object", "properties": {
            "surface": {"type": "string"}, "artifact": {"type": "string"}},
            "required": ["surface", "artifact"]},
    },
    {
        "name": "capabilities_comms_voice_check",
        "description": "voice fingerprint score + corpus drift report for an artifact",
        "inputSchema": {"type": "object", "properties": {
            "artifact": {"type": "string"}}, "required": ["artifact"]},
    },
    {
        "name": "capabilities_comms_ledger_report",
        "description": "loop events, drafted-vs-shipped funnel, and calibration (Brier) report",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "capabilities_comms_doctor",
        "description": "harness drift check: every installed comms skill hash-matched against "
                       "canonical (exit 2 = drift)",
        "inputSchema": {"type": "object", "properties": {}},
    },
    # -- build backend (Section IV B23–B28). Eight additions ONLY: every
    # schema is closed (additionalProperties=false), NONE carries a caller-
    # authored identity or a PASS/admitted/qualified field — by construction
    # there is no argument slot such a flag could arrive in, and the handlers
    # additionally re-refuse any stray key. Identity is bound at this server
    # process (RIG_CAP_CALLER from the wrapper, else the OS user).
    {
        "name": "capabilities_build_diagnose",
        "description": (
            "Validate a build diagnosis packet against the 588-cell authority "
            "and bind it to the CURRENT criteria pack sha. Same validator as "
            "bin/rig-build-standard diagnose — the tool cannot disagree with "
            "the CLI. Read-only: returns the normalized packet or the named "
            "refusal; a missing field is a rejection, never a default."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "minLength": 1},
                "cell_id": {"type": "string"},
                "done_test": {"type": "array", "items": {"type": "string"},
                              "minItems": 1},
                "out_of_scope": {"type": "array", "items": {"type": "string"}},
                "effort_budget": {"type": "object", "properties": {
                    "cpu_minutes": {"type": "number", "exclusiveMinimum": 0},
                    "usd": {"type": "number", "exclusiveMinimum": 0},
                    "wallclock_seconds": {"type": "number",
                                          "exclusiveMinimum": 0}},
                    "required": ["cpu_minutes", "usd", "wallclock_seconds"],
                    "additionalProperties": False},
                "evidence_refs": {"type": "array", "minItems": 1,
                                  "items": {"type": "string"}},
            },
            "required": ["goal", "cell_id", "done_test", "out_of_scope",
                         "effort_budget", "evidence_refs"],
            "additionalProperties": False,
        },
    },
    {
        "name": "capabilities_build_index",
        "description": (
            "Read the cell->build index bound to the verified golden pack "
            "(588-cell authority). Bounded rows + cursor; explicit state: "
            "live | empty | unknown(stale/corrupt). Never writes; a handle "
            "older than the current golden manifest answers stale, never "
            "answers for the new generation."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description":
                         "index file inside the repo (default "
                         "runs/agentic-stack-buildout/index/build-index.jsonl)"},
                "cursor": {"type": "integer", "minimum": 0},
                "limit": {"type": "integer", "minimum": 1, "maximum": 200},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "capabilities_build_gaps",
        "description": (
            "Cells of the 588 authority with NO build-index record under the "
            "current pack generation. Read-only, bounded + cursor; when the "
            "index is unreadable the state is 'unknown' and no gap list is "
            "fabricated from assumptions."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "cursor": {"type": "integer", "minimum": 0},
                "limit": {"type": "integer", "minimum": 1, "maximum": 200},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "capabilities_build_run_start",
        "description": (
            "Register a durable run from a VALID diagnosis packet (same "
            "validator as the CLI). Idempotent on the packet hash; the "
            "caller cannot choose state, identity, or any PASS field — "
            "started_by is this server process's identity. Without an "
            "approved rig_build target the answer is an explicit blocked "
            "state naming the reason, never a fake run."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "minLength": 1},
                "cell_id": {"type": "string"},
                "done_test": {"type": "array", "items": {"type": "string"},
                              "minItems": 1},
                "out_of_scope": {"type": "array", "items": {"type": "string"}},
                "effort_budget": {"type": "object", "properties": {
                    "cpu_minutes": {"type": "number", "exclusiveMinimum": 0},
                    "usd": {"type": "number", "exclusiveMinimum": 0},
                    "wallclock_seconds": {"type": "number",
                                          "exclusiveMinimum": 0}},
                    "required": ["cpu_minutes", "usd", "wallclock_seconds"],
                    "additionalProperties": False},
                "evidence_refs": {"type": "array", "minItems": 1,
                                  "items": {"type": "string"}},
                "process_key": {"type": "string"},
                "process_version": {"type": "string"},
            },
            "required": ["goal", "cell_id", "done_test", "out_of_scope",
                         "effort_budget", "evidence_refs"],
            "additionalProperties": False,
        },
    },
    {
        "name": "capabilities_build_run_get",
        "description": (
            "Read one run plus its most recent events from the durable "
            "store. Read-only; unknown run answers state=unknown; events "
            "bounded by limit/cursor. Unreachable storage is state=unknown "
            "with the named reason, never an empty success."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {"type": "string"},
                "cursor": {"type": "integer", "minimum": 0},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
            },
            "required": ["run_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "capabilities_build_evidence_add",
        "description": (
            "Worker-scoped evidence ingestion: register a repo-contained "
            "artifact (sha256 RECOMPUTED from bytes; declared-hash mismatch "
            "refused) and append a receipt event under the caller's fencing "
            "token (stale token -> refused, B47). There is no verdict/"
            "outcome/qualified argument that can be submitted here; "
            "qualification is recomputed, never accepted."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {"type": "string"},
                "path": {"type": "string", "description":
                         "artifact file inside the repo"},
                "uri": {"type": "string"},
                "kind": {"type": "string", "enum":
                         ["receipt", "checkpoint", "report", "log"]},
                "sequence": {"type": "integer", "minimum": 1},
                "fencing_token": {"type": "integer", "minimum": 1},
            },
            "required": ["run_id", "path", "kind", "sequence",
                         "fencing_token"],
            "additionalProperties": False,
        },
    },
    {
        "name": "capabilities_build_omission_request",
        "description": (
            "Stage an exact-cell omission PROPOSAL (cell + reason + evidence "
            "refs) as a DORMANT request file carrying the server-bound "
            "caller identity. This tool can stage and never approve: no "
            "argument approves, waives, or qualifies — that is Gate-D/human "
            "authority and the pending request stays open until then."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "cell_id": {"type": "string"},
                "reason": {"type": "string", "minLength": 1},
                "evidence_refs": {"type": "array", "minItems": 1,
                                  "items": {"type": "string"}},
            },
            "required": ["cell_id", "reason", "evidence_refs"],
            "additionalProperties": False,
        },
    },
    {
        "name": "capabilities_build_qualify",
        "description": (
            "Recompute build qualification for a commit from the four-"
            "receipt manifest through the SAME commit_gate.check the CLI "
            "runs, plus the live index generation for the cell. The input is "
            "only (cell_id, sha, manifest path): there is no admitted/pass/"
            "verdict field, and the answer is recomputed fresh, never "
            "accepted from the caller. Read-only and non-consuming."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "cell_id": {"type": "string"},
                "sha": {"type": "string"},
                "manifest_path": {"type": "string", "description":
                                  "receipt manifest JSON inside the repo"},
            },
            "required": ["cell_id", "sha", "manifest_path"],
            "additionalProperties": False,
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

    def build_store_status(_args: dict):
        from . import build_store as _bs, measure_store as _ms
        return {"record": _bs.status(), "measure": _ms.status()}

    def measure_quorum(args: dict):
        from . import measure_store as _ms
        cell = str(args.get("cell", ""))
        out = {"cell": cell, "configured": False}
        try:
            conn = _ms.connect()
        except Exception as exc:  # noqa: BLE001 — honest UNCONFIGURED, not a crash
            out["detail"] = str(exc)[:160]
            return out
        out["configured"] = True
        try:
            out["quorum"] = _ms.assess_quorum(conn, cell)
            out["qualification"] = _ms.qualification(conn, cell)
        except Exception as exc:  # noqa: BLE001
            out["detail"] = str(exc)[:160]
        finally:
            conn.close()
        return out

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
        rep = run_round(repo, str(args.get("lane", "misc")),
                        n=int(args.get("n") or 5), dry=bool(args.get("dry")),
                        budget=(int(args["budget"]) if args.get("budget")
                                is not None else None),
                        strategy=str(args.get("strategy") or "informative"))
        code = int(rep.get("exit_code") or 0)
        if code:
            # A refused round (replay guard, blocked lane, red gate) must not come
            # back as `isError: false`. The whole report is serialised into the
            # error text so the caller still sees the verdict, the diff-hash and
            # the record line that refused it.
            raise ToolError(f"round refused (exit_code={code}): "
                            + json.dumps(rep, ensure_ascii=False, default=str))
        return rep



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
        if action == "selftest":
            return mcp_wire.selftest()
        return mcp_wire.plan()


    def asset_hygiene(args: dict):
        out = surface_tools.asset_hygiene(repo, args)
        if not out.get("ran"):
            # A scanner that refused is not a clean estate. Same rule as `round`:
            # the refusal has to reach the surface that a cron reads.
            raise ToolError(f"asset_hygiene refused: {out.get('reason')}")
        return out

    def verdict(args: dict):
        out = surface_tools.verdict(repo, args)
        if not out.get("ran"):
            raise ToolError(
                f"{out.get('check') or 'verdict'} refused "
                f"(exit_code={out.get('exit_code')}): {out.get('reason')}")
        return out


    # -- build backend (B23–B28): bound to the SAME modules that
    # bin/rig-build-standard runs (build_diagnose / build_index / commit_gate)
    # so a tool answer can never disagree with the CLI. Identity is taken
    # from this server process (wrapper env, else OS user) — never from a
    # caller-authored field; every schema is closed and every handler below
    # also re-refuses keys outside its allow-list. There is deliberately no
    # argument slot named pass/admitted/qualified/verdict.

    def _build_caller() -> str:
        return os.environ.get("RIG_CAP_CALLER") or getpass.getuser()

    def _build_inside(rel: str) -> Path:
        root = Path(repo.root).resolve()
        p = (root / str(rel)).resolve()
        if not str(p).startswith(str(root) + "/"):
            raise ToolError(f"path escapes the repo: {rel!r}")
        return p

    def _build_closed(args: dict, allowed: tuple, tool: str) -> None:
        extra = set(args) - set(allowed)
        if extra:
            raise ToolError(f"{tool}: unknown keys {sorted(extra)} refused "
                            "(closed schema; identity/verdict fields are "
                            "never accepted from callers)")

    def _build_store():
        """Connect or return the named blocker — a missing target is an
        explicit blocked/unknown state, never a fabricated success."""
        from . import build_store
        try:
            return build_store, build_store.connect()
        except build_store.StoreError as exc:
            return build_store, None, str(exc)

    _DIAG_KEYS = ("goal", "cell_id", "done_test", "out_of_scope",
                  "effort_budget", "evidence_refs")

    def build_diagnose_tool(args: dict):
        from . import build_diagnose as bd
        from .build_index import current_pack_sha
        _build_closed(args, _DIAG_KEYS, "capabilities_build_diagnose")
        try:
            packet = bd.diagnose({k: args[k] for k in _DIAG_KEYS})
        except bd.DiagnoseError as exc:
            raise ToolError(f"diagnosis refused: {exc}")
        return {"read_only": True, "state": "validated", "packet": packet,
                "criteria_pack_sha256": current_pack_sha(Path(repo.root))}

    def _build_index_read(args: dict):
        from .build_index import open_live, IndexError_
        rel = args.get("path") or \
            "runs/agentic-stack-buildout/index/build-index.jsonl"
        path = _build_inside(rel)
        try:
            ix = open_live(Path(repo.root), str(path))
            gen, recs = ix._load()
        except IndexError_ as exc:
            return None, None, "unknown", str(exc)
        if gen is None:
            # No _meta header: the file is absent or never written. The
            # handle still carries the verified pack sha, but there is no
            # generation to answer for.
            return None, None, "empty", f"no index generation at {rel}"
        return ix, recs, "live", None

    def build_index_tool(args: dict):
        _build_closed(args, ("path", "cursor", "limit"),
                      "capabilities_build_index")
        ix, recs, state, reason = _build_index_read(args)
        cur = int(args.get("cursor") or 0)
        lim = min(int(args.get("limit") or 50), 200)
        out = {"read_only": True, "state": state}
        if state != "live":
            out["reason"] = reason
            return out
        cells = sorted(recs)
        out.update({"pack_sha": ix.pack_sha, "index_generation": ix.pack_sha,
                    "total": len(cells), "shown": len(cells[cur:cur + lim]),
                    "records": [recs[c] for c in cells[cur:cur + lim]],
                    "next_cursor": cur + lim if cur + lim < len(cells)
                    else None})
        return out

    def build_gaps_tool(args: dict):
        from .build_diagnose import _cell_ids
        _build_closed(args, ("path", "cursor", "limit"),
                      "capabilities_build_gaps")
        ix, recs, state, reason = _build_index_read(args)
        cur = int(args.get("cursor") or 0)
        lim = min(int(args.get("limit") or 50), 200)
        if state == "unknown":
            return {"read_only": True, "state": "unknown", "reason": reason,
                    "gaps": None}
        authority = set(_cell_ids())
        gaps = sorted(authority - set(recs or {}))
        out = {"read_only": True,
               "state": "empty" if state == "empty" else "live",
               "authority_cells": len(authority), "recorded": len(recs or {}),
               "gap_total": len(gaps), "gaps": gaps[cur:cur + lim],
               "next_cursor": cur + lim if cur + lim < len(gaps) else None}
        if state == "empty":
            out["reason"] = reason
        return out

    def build_run_start_tool(args: dict):
        from . import build_diagnose as bd, build_store
        _build_closed(args, _DIAG_KEYS + ("process_key", "process_version"),
                      "capabilities_build_run_start")
        try:
            packet = bd.diagnose({k: args[k] for k in _DIAG_KEYS})
        except bd.DiagnoseError as exc:
            raise ToolError(f"run refused — diagnosis invalid: {exc}")
        caller = _build_caller()
        key = "mcp:" + hashlib.sha256(
            json.dumps(packet, sort_keys=True).encode()).hexdigest()[:24]
        res = _build_store()
        store, conn = res[0], res[1]
        if conn is None:
            return {"state": "blocked",
                    "reason": f"no rig_build target: {res[2]}",
                    "idempotency_key": key,
                    "next_action": "apply scripts/ddl_rig_build.sql via "
                                   "build_migrate after B11/B12 approval"}
        try:
            if not (args.get("process_key") and args.get("process_version")):
                return {"state": "blocked",
                        "reason": "no owner binding supplied for this cell — "
                                  "run bind_cell first; the store never "
                                  "invents a default owner",
                        "idempotency_key": key}
            from .build_index import current_pack_sha
            out = store.start_run(
                conn, cell_id=packet["cell_id"],
                criteria_version=current_pack_sha(Path(repo.root)),
                process_key=args["process_key"],
                process_version=args["process_version"],
                idempotency_key=key, started_by=caller)
            return {"state": out["status"], "run": out["row"],
                    "started_by": caller, "idempotency_key": key}
        except store.StoreError as exc:
            return {"state": "blocked", "reason": str(exc)}
        finally:
            conn.close()

    def build_run_get_tool(args: dict):
        from . import build_store
        _build_closed(args, ("run_id", "cursor", "limit"),
                      "capabilities_build_run_get")
        cur = int(args.get("cursor") or 0)
        lim = min(int(args.get("limit") or 25), 100)
        res = _build_store()
        store, conn = res[0], res[1]
        if conn is None:
            return {"read_only": True, "state": "unknown",
                    "reason": f"storage unreachable: {res[2]}"}
        try:
            c = conn.cursor()
            c.execute("SELECT * FROM rig_build.runs WHERE run_id=%s",
                      (args["run_id"],))
            cols = [d[0] for d in c.description]
            row = c.fetchone()
            if row is None:
                return {"read_only": True, "state": "unknown",
                        "run_id": args["run_id"]}
            run = dict(zip(cols, row))
            c.execute("""SELECT sequence, kind, payload, fencing_token,
                                occurred_at FROM rig_build.run_events
                         WHERE run_id=%s ORDER BY sequence DESC
                         LIMIT %s""", (args["run_id"], lim))
            ecols = [d[0] for d in c.description]
            events = [dict(zip(ecols, r)) for r in c.fetchall()]
            return {"read_only": True, "state": "live", "run": run,
                    "events_newest_first": events, "cursor": cur,
                    "next_cursor": cur + lim}
        except Exception as exc:  # fail closed, named
            return {"read_only": True, "state": "unknown",
                    "reason": f"{type(exc).__name__}: {exc}"}
        finally:
            conn.close()

    def build_evidence_add_tool(args: dict):
        from . import build_store
        _build_closed(args, ("run_id", "path", "uri", "kind", "sequence",
                             "fencing_token"),
                      "capabilities_build_evidence_add")
        p = _build_inside(args["path"])
        if not p.is_file():
            raise ToolError(f"evidence file not found: {args['path']}")
        res = _build_store()
        store, conn = res[0], res[1]
        if conn is None:
            return {"state": "blocked",
                    "reason": f"no rig_build target: {res[2]}"}
        caller = _build_caller()
        try:
            art = store.add_artifact(
                conn, run_id=args["run_id"], uri=args.get("uri")
                or f"local://{args['path']}", kind=args["kind"],
                recorded_by=caller, path=str(p))
            ev = store.append_event(
                conn, run_id=args["run_id"], sequence=args["sequence"],
                kind="receipt", fencing_token=args["fencing_token"],
                payload={"content_sha256": art["content_sha256"],
                         "path": args["path"], "artifact": art["status"]})
            return {"state": "recorded", "artifact": art["status"],
                    "event": ev["status"], "recorded_by": caller}
        except store.StoreError as exc:
            return {"state": "refused", "reason": str(exc),
                    "note": "hash mismatch, stale fencing token, or "
                            "sequence violation — nothing was stored"}
        finally:
            conn.close()

    def build_omission_request_tool(args: dict):
        from .build_diagnose import _cell_ids
        _build_closed(args, ("cell_id", "reason", "evidence_refs"),
                      "capabilities_build_omission_request")
        if args["cell_id"] not in _cell_ids():
            raise ToolError("cell_id not in the 588-cell authority")
        caller = _build_caller()
        doc = {"state": "PENDING_HUMAN_REVIEW", "cell_id": args["cell_id"],
               "reason": args["reason"].strip(),
               "evidence_refs": list(args["evidence_refs"]),
               "requested_by": caller,
               "approval": "NOT POSSIBLE HERE — this tool stages only; "
                           "consent is Gate-D/human and this file records "
                           "that the request is OPEN, never that it is "
                           "granted"}
        body = json.dumps(doc, indent=1, sort_keys=True) + "\n"
        digest = hashlib.sha256(
            json.dumps({k: doc[k] for k in
                        ("state", "cell_id", "reason", "evidence_refs",
                         "requested_by")},
                       sort_keys=True).encode()).hexdigest()[:16]
        out_path = Path(repo.root) / "runs" / "agentic-stack-buildout" \
            / "omissions" / f"omission-{digest}.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if out_path.exists():
            return {"state": "already_staged", "path": str(out_path),
                    "requested_by": caller}
        out_path.write_text(body, encoding="utf-8")
        return {"state": "staged_dormant", "path": str(out_path),
                "requested_by": caller,
                "next_action": "human/Gate-D review; pending stays open"}

    def build_qualify_tool(args: dict):
        from . import commit_gate
        from .build_index import open_live, current_pack_sha, IndexError_
        from .build_diagnose import _cell_ids
        _build_closed(args, ("cell_id", "sha", "manifest_path"),
                      "capabilities_build_qualify")
        if args["cell_id"] not in _cell_ids():
            raise ToolError("cell_id not in the 588-cell authority")
        manifest_file = _build_inside(args["manifest_path"])
        try:
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ToolError(f"manifest unreadable: {exc}")
        # RECOMPUTED — the verdict is produced here from live authorities;
        # no submitted flag is consulted (the schema has no such slot).
        live_sha = current_pack_sha(Path(repo.root))
        try:
            ix = open_live(Path(repo.root), str(_build_inside(
                "runs/agentic-stack-buildout/index/build-index.jsonl")))
            _, recs = ix._load()
            cell_record = recs.get(args["cell_id"])
        except FileNotFoundError:
            cell_record = None
        except IndexError_ as exc:
            return {"read_only": True, "state": "stale",
                    "admitted": False, "reason": str(exc)}
        gate = commit_gate.check(Path(repo.root), args["sha"], manifest)
        blockers = list(gate["refusals"])
        if cell_record is None:
            blockers.append("index: no build record for this cell under the "
                            f"current pack {live_sha[:12]} (UNKNOWN blocks)")
        return {"read_only": True, "state": "recomputed",
                "admitted": gate["admitted"] and not blockers,
                "refusals": blockers, "criteria_pack_sha256": live_sha,
                "index_generation": live_sha,
                "checked_by": _build_caller()}

    handlers = {
        "capabilities_asset_hygiene": asset_hygiene,
        "capabilities_verdict": verdict,
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
        "capabilities_build_store": build_store_status,
        "capabilities_measure_quorum": measure_quorum,
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
        # Communications OS — thin passthrough to the rig_comms runtime.
        "capabilities_comms_surfaces": comms_bridge.surfaces_catalog,
        "capabilities_comms_route": comms_bridge.route,
        "capabilities_comms_packet": comms_bridge.packet,
        "capabilities_comms_score": comms_bridge.score,
        "capabilities_comms_voice_check": comms_bridge.voice_check,
        "capabilities_comms_ledger_report": comms_bridge.ledger_report,
        "capabilities_comms_doctor": comms_bridge.doctor,
        # Build backend (B23–B28) — eight additions, nothing renamed or
        # removed. Read tools return {"read_only": True, ...} per house
        # convention; every handler re-checks its closed schema.
        "capabilities_build_diagnose": build_diagnose_tool,
        "capabilities_build_index": build_index_tool,
        "capabilities_build_gaps": build_gaps_tool,
        "capabilities_build_run_start": build_run_start_tool,
        "capabilities_build_run_get": build_run_get_tool,
        "capabilities_build_evidence_add": build_evidence_add_tool,
        "capabilities_build_omission_request": build_omission_request_tool,
        "capabilities_build_qualify": build_qualify_tool,
    }

    # -- resources: an exact-match URI map, never a path join (no traversal) --
    skills_dir = comms_bridge.COMMS_HOME.parent
    RESOURCES = [
        {"uri": "comms://surfaces", "name": "Surface registry",
         "description": "lanes, engines, deviation budgets, AGF floors (live)",
         "mimeType": "application/json"},
        {"uri": "comms://fingerprint", "name": "Voice fingerprint v2",
         "description": "banned phrases, signature vocab, sentence bands (live)",
         "mimeType": "application/json"},
        {"uri": "comms://doctrine", "name": "Communications doctrine",
         "description": "the routing doctrine every comms tool obeys",
         "mimeType": "text/markdown"},
        {"uri": "comms://rejected-patterns", "name": "Rejected patterns",
         "description": "phrases and shapes the machine refuses to emit",
         "mimeType": "text/markdown"},
        {"uri": "capabilities://stats", "name": "Catalog stats",
         "description": "asset counts by kind and source (live)",
         "mimeType": "application/json"},
    ]

    def read_resource(uri: str) -> str:
        if uri == "comms://surfaces":
            return json.dumps(comms_bridge.surfaces_catalog({}), indent=1, default=str)
        if uri == "comms://fingerprint":
            return json.dumps(comms_bridge._load()["voice"].FINGERPRINT, indent=1)
        if uri == "comms://doctrine":
            p = skills_dir / "rig-communications-doctrine" / "SKILL.md"
            if not p.is_file():
                raise ToolError(f"doctrine skill missing at {p}")
            return p.read_text(encoding="utf-8")
        if uri == "comms://rejected-patterns":
            p = (comms_bridge._load()["ledger"].data_root()
                 / "rejected-patterns" / "banned-phrases.md")
            if not p.is_file():
                raise ToolError(f"no rejected-patterns corpus at {p}")
            return p.read_text(encoding="utf-8")
        if uri == "capabilities://stats":
            return json.dumps(repo.stats(), indent=1, default=str)
        raise ToolError(f"unknown resource uri: {uri}")

    # -- prompts: the /write loop as a first-class MCP primitive --
    PROMPTS = [
        {"name": "write", "description":
            "Communications OS write packet: doctrine, voice, gates and surface "
            "card assembled for one brief; draft must then pass "
            "capabilities_comms_score before shipping.",
         "arguments": [{"name": "surface", "required": True},
                       {"name": "brief", "required": True},
                       {"name": "persona", "required": False},
                       {"name": "human", "required": False}]},
        {"name": "review", "description":
            "Verifier prompt: score an artifact through the deterministic gate "
            "stack and report blocks — never rewrite silently.",
         "arguments": [{"name": "surface", "required": True},
                       {"name": "artifact", "required": True}]},
    ]

    def get_prompt(name: str, args: dict) -> dict:
        if name == "write":
            m = comms_bridge._load()
            surf = m["surfaces"].resolve(args.get("surface") or "")
            if surf is None:
                raise ToolError(f"unknown surface '{args.get('surface')}'")
            comms_bridge._private_guard(surf, bool(args.get("human")),
                                        "the write prompt")
            brief = (args.get("brief") or "").strip()
            if not brief:
                raise ToolError("brief required")
            packet = m["packets"].build_packet(
                surf.id, brief, args.get("persona", ""))
            return {
                "description": f"Communications OS write packet for {surf.id}",
                "messages": [
                    {"role": "system", "content": packet + (
                        "\n\n---\nHARD RULES: draft only from this packet; before "
                        "shipping run capabilities_comms_score with surface='"
                        + surf.id + "' and the draft as artifact; can_ship=false means "
                        "revise (max 3 corrections, then escalate), never ship; never "
                        "claim metrics the packet did not supply.")},
                    {"role": "user", "content": brief},
                ],
            }
        if name == "review":
            surf = args.get("surface") or ""
            artifact = args.get("artifact") or ""
            if not artifact.strip():
                raise ToolError("artifact required")
            return {
                "description": "Gate-stack review of a comms artifact",
                "messages": [
                    {"role": "system", "content":
                        "You are the independent Verifier (Builder/Verifier split). "
                        "Run capabilities_comms_score with surface='" + surf + "' "
                        "and capabilities_comms_voice_check on this artifact. Report "
                        "can_ship, every blocking reason, and voice drift deltas. "
                        "Do NOT rewrite the artifact yourself; return the verdict."},
                    {"role": "user", "content": artifact},
                ],
            }
        raise ToolError(f"unknown prompt: {name}")

    return McpStdioServer(
        NAME, VERSION, TOOLS, handlers,
        resources=RESOURCES, read_resource=read_resource,
        prompts=PROMPTS, get_prompt=get_prompt,
        instructions=(
            "rig-capabilities: search before you author; canonicalize with "
            "capability_add; distribute with capability_install. Communications OS "
            "loop: capabilities_comms_route -> capabilities_comms_packet (or the "
            "`write` prompt) -> draft -> capabilities_comms_score (can_ship=true or "
            "revise, max 3) -> capabilities_comms_doctor before any harness ships. "
            "The private lane (love-notes) refuses machine drafting without "
            "human:true and machine scoring always — a PRIVACY_LOCK error is a "
            "lock, not a bug."))
