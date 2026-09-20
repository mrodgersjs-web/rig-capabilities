#!/usr/bin/env python3
"""Generate the authoritative UltraPlan V2 build manifest.

The contract's per-track table is authoritative. Its rows total 904, while the
prose says 864; the emitted header records that discrepancy rather than hiding
it or dropping forty W11 hierarchy items.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

CONTRACT = Path("/Users/rig128gb/Desktop/ultraplan/ULTRAPLAN-V2-CONTRACT.md")
OUTPUT = Path(__file__).with_name("BUILD-MANIFEST.yaml")
GENERATED_AT = "2026-09-20T00:00:00Z"
CONTRACT_DECLARED_TOTAL = 864

TRACK_TOTALS = {
    "W00": 42,
    "W01": 78,
    "W02": 76,
    "W03": 64,
    "W04": 58,
    "W05": 28,
    "W06": 72,
    "W07": 86,
    "W08": 92,
    "W09": 58,
    "W10": 38,
    "W11": 76,
    "W12": 42,
    "W13": 50,
    "W14": 44,
}
ACTUAL_TOTAL = sum(TRACK_TOTALS.values())

RIG_CAPABILITIES_PLAN = "/Users/rig128gb/Developer/rig-capabilities/plans/ultraplan-v2"
ULTRAPLAN = "/Users/rig128gb/Developer/ultraplan"
ULTRA_MCP = "/Users/rig128gb/Developer/ultra-mcp"

TRACK_WRITES = {
    "W00": [RIG_CAPABILITIES_PLAN],
    "W01": [f"{ULTRAPLAN}/schemas", f"{ULTRAPLAN}/cells", RIG_CAPABILITIES_PLAN],
    "W02": [f"{ULTRAPLAN}/rig-loop", f"{ULTRAPLAN}/commands", RIG_CAPABILITIES_PLAN],
    "W03": [f"{ULTRAPLAN}/commands", f"{ULTRAPLAN}/ui", f"{ULTRA_MCP}/server.py"],
    "W04": [f"{ULTRAPLAN}/cells", f"{ULTRAPLAN}/rig-loop", RIG_CAPABILITIES_PLAN],
    "W05": [f"{ULTRAPLAN}/rig-loop", f"{ULTRAPLAN}/commands", RIG_CAPABILITIES_PLAN],
    "W06": [f"{ULTRAPLAN}/cells", f"{ULTRAPLAN}/commands", RIG_CAPABILITIES_PLAN],
    "W07": [f"{ULTRAPLAN}/cells", RIG_CAPABILITIES_PLAN],
    "W08": [f"{ULTRAPLAN}/cells", RIG_CAPABILITIES_PLAN],
    "W09": [f"{ULTRAPLAN}/cells", f"{ULTRAPLAN}/rig-loop", RIG_CAPABILITIES_PLAN],
    "W10": [f"{ULTRAPLAN}/cells", f"{ULTRAPLAN}/rig-loop", RIG_CAPABILITIES_PLAN],
    "W11": [f"{ULTRAPLAN}/cells", RIG_CAPABILITIES_PLAN],
    "W12": [f"{ULTRAPLAN}/ui", RIG_CAPABILITIES_PLAN],
    "W13": [f"{ULTRAPLAN}/rig-loop", f"{ULTRAPLAN}/commands", RIG_CAPABILITIES_PLAN],
    "W14": [RIG_CAPABILITIES_PLAN],
}

TRACK_REQUIREMENTS = {
    "W00": [
        "Record dirty state and preserve every unrelated edit",
        "Snapshot persisted console state, all 292 shape IDs, and current artifact hashes",
        "Record the current JEV route, model inventory, port inventory, and installed Fusion and Earendil surfaces",
        "Resolve registered writable roots for ultraplan and ultra-mcp",
        "Create a TAC source manifest covering all 14 lessons, timestamps, repositories, loot, and disposition",
        "Classify each imported course asset as reuse, adapt, reference_only, unnecessary, or pending_license_review",
        "Locate the four missing member repositories through the canonical registry before acquisition",
        "Record complete caption coverage and incomplete frame-by-frame video review",
        "Restore the baseline without losing any drawing, session, or user edit",
    ],
    "W01": [
        "Create versioned command, event, receipt, approval, projection, route, and cell schemas",
        "Make studio bundles discoverable and remove the validator studio skip",
        "Resolve every studio target to an existing implementation",
        "Reject missing slots, empty bindings, absent children, invalid route predicates, cycles, orphaned cells, and incompatible envelopes",
        "Replace prose-only checks with registered executable check IDs and parameters",
        "Add BDD feature files for every track and studio operation",
        "Plant invalid studio roots, missing routes, invalid envelopes, and vacuous hooks",
        "Separate phase, engine-stage, studio, cell, shape, and view identifiers",
        "Prevent the prior 26-of-26-valid blind spot from recurring",
    ],
    "W02": [
        "Consolidate every state transition under rig-loop",
        "Move authoritative state from JSON projections to transactional SQLite events and snapshots",
        "Add command IDs, idempotency keys, expected sequences, and writer fences",
        "Commit outbox entries transactionally and store effect receipts separately",
        "Add legal park, resume, cancel, abandon, retry_exhausted, and reconcile_uncertain states",
        "Enforce decision, cost, time, and tool budgets inherited by children",
        "Add replay, snapshot, rebuild, and recovery commands",
        "Exercise crash points before insert, after event insert, after outbox insert, after commit, and before response",
        "Prove an acknowledged command survives restart without duplicate effects",
    ],
    "W03": [
        "Implement execute(command, authenticated_actor) as the shared transport-neutral handler",
        "Make CLI import the shared handler directly",
        "Make MCP a thin stdio adapter over the shared handler",
        "Keep Node as a loopback UI and proxy rather than a second command authority",
        "Replace direct events.jsonl writes with commands through Python",
        "Add SSE cursor replay, Last-Event-ID, gap reporting, and bounded backpressure",
        "Add authenticated browser sessions",
        "Bind approval to actor, action, target, parameter hash, specification revision, expiration, and single-use nonce",
        "Keep backend credentials out of browser storage",
        "Preserve CLI exit semantics",
        "Preserve existing working UI routes",
        "Prove console, CLI, and MCP produce equivalent durable outcomes for the same command",
    ],
    "W04": [
        "Correct genuinely_different rubric polarity and explanatory reason",
        "Add high, low, and boundary fixtures",
        "Calibrate per rule and per signal instead of one rubric-wide flag",
        "Reject unmatched calibration rules without writing configuration",
        "Bind calibration to rubric, rule, model, and labeled-set hashes",
        "Require held-out and combined-policy evaluation",
        "Keep insufficiently measured rules advisory",
        "Use real chain verification and reject caller-supplied boolean assertions",
        "Require five surviving forecasts across three independent weight families",
        "Exclude the author family from independent forecasts",
        "Standardize aggregation on symmetric trimmed mean with trim=1",
        "Add asymmetric aggregation fixtures",
        "Require receipts before forecast registration, settlement, or score claims",
        "Block authoritative pass on malformed output, missing evidence, insufficient diversity, or false calibration",
    ],
    "W05": [
        "Create a bounded local fixture mission",
        "Enter the fixture mission through the console",
        "Produce intent, question bank, research evidence, alternatives, and an accepted specification",
        "Execute one architecture-to-build slice",
        "Run a fresh-context GLM review",
        "Plant a real failure and repair it through the normal workflow",
        "Restart the runtime mid-mission and prove safe resumption",
        "Seal one real ProofPacket",
        "Complete one ordinary-surface mission with observable inputs, outputs, failure evidence, and recovery",
    ],
    "W06": [
        "Implement Core Four contracts for context, model, prompt, and tools",
        "Implement through-agent leverage for stdout, types, docs, tests, architecture, plans, templates, and deterministic ADWs",
        "Implement setup, prime, start, plan, build, test, review, document, and repair commands",
        "Implement chore, bug, feature, and domain-specific planning templates",
        "Implement PITER adapters for Prompt Input, Trigger, Environment, and Review",
        "Implement typed planner-to-builder and builder-to-reviewer handoffs",
        "Provide isolated workspaces, port allocation, test fixtures, and run logs",
        "Implement ad hoc, workflow, control-flow, delegation, higher-order, template-meta, and expert-self-improvement prompt forms",
        "Enforce context budgets, tool allowlists, resume packets, and scoped worker reports",
        "Stage meta prompt, agent, and skill generators as candidates rather than activating them",
        "Check capability maturity at C1 grades 1-7, C2 grades 1-2, and C3 grades 1-3",
        "Repair native Codex Fusion behavior while preserving Earendil",
        "Probe each route before assignment and refuse silent metered fallback",
        "Give every reusable TAC pattern contracts, tests, admission rules, and a bounded runtime path",
    ],
    "W12": [
        "Map all 292 shapes to requirement, cell, artifact, projection, control, or decoration",
        "Preserve existing tldraw IDs and manual edits",
        "Render live phase, studio, worker, budget, artifact, approval, and proof state",
        "Show freshness timestamps and distinguish planned, built, connected, verified, and blocked",
        "Add readable Architecture and Cells views",
        "Bundle local frontend dependencies",
        "Preserve existing sessions on ports 61398, 61399, and 61400",
        "Test reconnect without duplicate mission creation",
        "Make the console a truthful projection of durable evidence",
    ],
    "W13": [
        "Snapshot database, artifacts, registry bindings, adapters, and drawings before migration",
        "Import legacy JSON with explicit provenance and uncertainty",
        "Rebuild projections from events",
        "Rehearse migration and rollback",
        "Exercise stale sequence, stale lease, stale approval, duplicate command, and uncertain-effect cases",
        "Run 100 fixture missions in the isolated soak",
        "Run 10000 commands in the isolated soak",
        "Inject 20 percent duplicate deliveries in the isolated soak",
        "Exercise 100 reconnects in the isolated soak",
        "Exercise 24 controlled restarts in the isolated soak",
        "Hold acknowledged-command loss at zero",
        "Hold duplicate effects at zero",
        "Hold illegal transitions at zero",
        "Hold accepted stale approvals at zero",
        "Hold recursive root missions at zero",
        "Recover the UI within 5 seconds",
        "Recover the Python service within 15 seconds",
        "Detect worker failure within 30 seconds",
        "Recover a full session within 120 seconds",
        "Rebuild 10000 events within 60 seconds with an identical hash",
        "Leave no idle worker process after 5 minutes",
    ],
    "W14": [
        "Validate all OpenSpec changes",
        "Validate all cells and planted failures",
        "Run unit, integration, browser, accessibility, visual, performance, and security suites",
        "Run independent GLM review from fresh context",
        "Complete requirement-to-source-to-cell-to-evidence traceability",
        "Run the D85 checklist and certificate verification against actual execution classification",
        "Generate a final ProofPacket with source hashes, model routes, tests, failure receipts, recovery evidence, and verifier verdict",
        "Block promotion when D85 cannot certify the actual classified scope",
    ],
}

FACETS = [
    ("contract", "Specify", "documentation", "astra"),
    ("implementation", "Implement", "runtime", "blackwell"),
    ("positive-invocation", "Exercise accepted path for", "test", "glm"),
    ("negative-invocation", "Exercise rejected path for", "test", "glm"),
    ("route-integration", "Connect the real caller for", "route", "blackwell"),
    ("restart-recovery", "Recover after interruption for", "test", "glm"),
    ("planted-failure", "Prove RED then GREEN for", "test", "glm"),
    ("independent-verification", "Independently verify", "test", "glm"),
    ("evidence-binding", "Bind artifact hashes and receipts for", "test", "glm"),
    ("traceability", "Trace source to evidence for", "documentation", "astra"),
]

STUDIO_OPERATIONS = {
    "W07": {
        "questioning": [
            "persona-panel", "bank-harvest", "tag-and-route", "value-rank",
            "card-assemble", "coverage-meter", "informed-check",
        ],
        "research": [
            "sufficiency-bar", "corpus-first", "wave-scout", "landscape-wave",
            "base-rate-scout", "source-grade", "gap-mining", "dry-check",
            "freshness-scheduler",
        ],
        "forecasting": [
            "forecast-brief", "swarm-fanout", "envelope-validate", "aggregate",
            "premortem", "ledger-register", "resolve-and-score",
        ],
    },
    "W08": {
        "architecture": [
            "system-context", "domain-boundaries", "frontend-architecture",
            "backend-api-architecture", "data-architecture", "security-architecture",
            "integration-contracts", "deployment-architecture", "quality-attributes",
            "tradeoff-records", "dependency-impact", "architecture-verification",
        ],
        "development-build": [
            "frontend-build", "backend-build", "data-migrations", "integration-build",
            "build-toolchain", "unit-contract-tests", "system-e2e-tests",
            "accessibility-visual", "performance", "security-validation",
            "release-package", "documentation",
        ],
    },
    "W09": {
        "execution": [
            "wave-planner", "lease", "dispatch", "worker", "verifier", "arbiter",
            "integrate", "receipts",
        ],
        "proof": [
            "done-test-register", "plant-failure", "attest", "chain", "sssf-gates",
            "seal", "proofpacket",
        ],
    },
    "W10": {
        "learning": [
            "harvest", "attribute", "write-back", "prompt-optimize",
            "rubric-recalibrate", "reweight", "realign-register",
        ],
    },
}

STUDIO_REQUIREMENTS = {
    "W07": [
        "Research researchable blockers before interrupting the user",
        "Deduplicate question and research banks together",
        "Register forecasts for measurable later resolution",
    ],
    "W08": [
        "Require accepted architecture contracts before Development and Build starts",
        "Reopen architecture review and affected BDD scenarios when a contract changes",
        "Traverse architecture, data, APIs, trust boundaries, implementation, visual checks, and documentation with a real fixture",
    ],
    "W09": [
        "Use Firstmate worker envelopes",
        "Enforce one writer lease and serialize shared-file writes",
        "Support explicit code, human, and outward slice kinds",
        "Require receipt-shaped done-tests for every slice",
        "Require per-slice approval for outward work",
        "Separate worker and verifier model families",
        "Plant a mission-level done-test failure",
        "Attest artifacts and seal proof",
        "Prevent a builder from certifying itself",
        "Reject file-existence hooks that pass with empty output",
        "Prevent competing workers from writing shared files",
    ],
    "W10": [
        "Require evidence-backed attribution",
        "Schedule T+N business outcome reads",
        "Stage prompt candidates outside live production",
        "Stage skill candidates outside live production",
        "Stage agent candidates outside live production",
        "Stage expertise candidates outside live production",
        "Require held-out evaluation before learning promotion",
        "Block learning promotion on regression",
        "Require independent promotion verdicts",
        "Represent no_change explicitly",
        "Represent insufficient_evidence explicitly",
        "Represent candidate_rejected explicitly",
        "Write Memory OS events through the authenticated interface",
        "Resolve forecasts through the authenticated interface",
        "Resolve each future outcome exactly once",
        "Prevent unsupported learning from overwriting a live capability",
    ],
}

META_COMPONENTS = [
    "ultraplan-root",
    "five-phases",
    "nine-engine-stages",
    "nine-studios",
    "cross-cutting-capability-registry",
    "model-routing",
    "approval-policy",
    "context-policy",
    "evidence-policy",
    "learning-admission",
]

SUB_PRIMITIVES = [
    "lens-instances",
    "normalize-dedup",
    "angle-generation",
    "scraper-instances",
    "liveness-check",
    "model-family-ladder",
    "lens-pack",
    "jev-noul-call",
    "jev-choice-call",
    "jev-score-call",
    "order-swap-check",
    "memory-append",
    "variant-proposal",
    "envelope-builder",
    "firstmate-registration",
    "schema-validator",
    "artifact-hasher",
    "receipt-verifier",
    "budget-checker",
    "approval-validator",
    "writer-fence-validator",
    "sse-cursor-validator",
    "route-resolver",
    "plant-failure-runner",
]

STUDIO_REQUIREMENT_KINDS = {
    "approval": "hook",
    "route": "route",
    "memory": "context",
    "forecast": "loop",
    "writer": "hook",
    "lease": "hook",
    "proof": "harness",
    "bdd": "test",
}

GUARD_TERMS = {
    "schema", "validator", "validate", "reject", "gate", "approval", "lease",
    "fence", "seal", "proof", "idempotency", "duplicate", "authority", "auth",
    "budget", "transition", "route", "receipt", "cycle", "hash", "freshness",
    "regression", "promotion", "recovery", "restart", "crash", "backpressure",
}
MANDATORY_COVERAGE = {f"H{number}" for number in range(1, 23)} | {
    f"Q-{letter}" for letter in "ABCDEFGHIJ"
}

REGULAR_COVERAGE = {
    ("W02", 0): ("H1",),
    ("W02", 2): ("H2",),
    ("W06", 12): ("H3", "H11"),
    ("W02", 4): ("H5", "H20"),
    ("W02", 5): ("H6", "H7"),
    ("W03", 7): ("H19",),
    ("W12", 3): ("H16",),
    ("W12", 0): ("H22",),
}

OPERATION_COVERAGE = {
    ("questioning", "persona-panel"): ("H12", "Q-A"),
    ("questioning", "bank-harvest"): ("H9",),
    ("questioning", "value-rank"): ("Q-D", "Q-E"),
    ("questioning", "informed-check"): ("H8",),
    ("research", "landscape-wave"): ("Q-C",),
    ("research", "dry-check"): ("H10",),
    ("forecasting", "forecast-brief"): ("H14",),
    ("forecasting", "swarm-fanout"): ("Q-F",),
    ("forecasting", "premortem"): ("Q-G",),
    ("architecture", "tradeoff-records"): ("Q-H",),
    ("architecture", "dependency-impact"): ("Q-B",),
    ("execution", "wave-planner"): ("Q-I",),
    ("execution", "dispatch"): ("H4",),
    ("learning", "harvest"): ("Q-J",),
}

STUDIO_REQUIREMENT_COVERAGE = {
    ("W09", 1): ("H15",),
    ("W09", 2): ("H13",),
    ("W09", 5): ("H18",),
    ("W09", 6): ("H17",),
    ("W10", 1): ("H21",),
}


def coverage_clause(tags: tuple[str, ...]) -> str:
    return "" if not tags else " Mandatory coverage: " + " ".join(f"[covers:{tag}]" for tag in tags) + "."




def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:56] or "item"


def infer_owner(requirement: str, default: str) -> str:
    text = requirement.lower()
    if any(word in text for word in ("firstmate", "worker", "dispatch", "writer lease", "writer-fence")):
        return "firstmate"
    if any(word in text for word in ("rig-loop", "transition", "sqlite", "ledger", "outbox", "replay", "snapshot", "idempotency", "park", "resume")):
        return "deterministic"
    return default


def infer_kind(text: str, default: str = "runtime") -> str:
    lowered = text.lower()
    for token, kind in STUDIO_REQUIREMENT_KINDS.items():
        if token in lowered:
            return kind
    if "schema" in lowered or "contract" in lowered:
        return "harness"
    if "ui" in lowered or "console" in lowered or "browser" in lowered or "visual" in lowered:
        return "ui"
    if "migration" in lowered or "rollback" in lowered or "legacy" in lowered:
        return "migration"
    if "prompt" in lowered:
        return "prompt"
    if "agent" in lowered or "worker" in lowered or "verifier" in lowered:
        return "agent"
    if "hook" in lowered:
        return "hook"
    if "loop" in lowered or "state" in lowered or "recovery" in lowered:
        return "loop"
    if "context" in lowered or "provenance" in lowered:
        return "context"
    if "test" in lowered or "fixture" in lowered or "verify" in lowered:
        return "test"
    return default


def authority_for(owner: str) -> str:
    return {
        "astra": "ULTRAPLAN-V2-CONTRACT.md and Astra acceptance ownership; rig-loop remains the only transition authority",
        "blackwell": "Astra-accepted contract implemented by Blackwell within a Firstmate writer lease",
        "glm": "Fresh-context GLM 5.3 verification over durable artifacts and rerunnable receipts",
        "firstmate": "Firstmate dispatch authority and exclusive file-boundary writer lease",
        "deterministic": "rig-loop legal-transition authority backed by the canonical SQLite event ledger",
    }[owner]


def executable_done_test(item_id: str, facet: str, operation: str | None = None) -> str:
    op = f" --operation {operation}" if operation else ""
    commands = {
        "contract": f"python3 -m ultraplan.contract_checks schema --item {item_id}{op}",
        "implementation": f"python3 -m ultraplan.contract_checks invoke --item {item_id}{op} --fixture positive",
        "positive-invocation": f"python3 -m ultraplan.contract_checks invoke --item {item_id}{op} --fixture positive --expect accepted",
        "negative-invocation": f"python3 -m ultraplan.contract_checks invoke --item {item_id}{op} --fixture invalid --expect blocked",
        "route-integration": f"python3 -m ultraplan.contract_checks route --item {item_id}{op} --surface real",
        "restart-recovery": f"python3 -m ultraplan.contract_checks recover --item {item_id}{op} --restart",
        "planted-failure": f"python3 -m ultraplan.contract_checks plant --item {item_id}{op} --expect red-green",
        "independent-verification": f"python3 -m ultraplan.contract_checks verify --item {item_id}{op} --family glm",
        "evidence-binding": f"python3 -m ultraplan.contract_checks evidence --item {item_id}{op} --require artifact-hash,receipt",
        "traceability": f"python3 -m ultraplan.contract_checks trace --item {item_id}{op} --require source,cell,evidence",
        "operation-cell": f"python3 -m ultraplan.cells validate --item {item_id}{op} --require-slots skill,agent,prompt,harness,hooks,loop,context,route",
        "studio-requirement": f"python3 -m ultraplan.contract_checks requirement --item {item_id} --expect enforced",
        "meta-governance": f"python3 -m ultraplan.cells validate --item {item_id} --tier meta --no-normal-duplication",
        "sub-primitive": f"python3 -m ultraplan.cells validate --item {item_id} --tier sub --shared-by-reference",
        "wiring-edge": f"python3 -m ultraplan.cells graph --item {item_id} --assert-resolved --assert-acyclic",
    }
    return f"Run `{commands[facet]}` and require exit 0 plus a receipt that names the asserted observable outcome."


def plant_failure(item_id: str, guarding: bool) -> dict[str, Any]:
    if not guarding:
        return {"procedure": None, "reason": "non-guarding"}
    return {
        "procedure": (
            f"Run `python3 -m ultraplan.contract_checks plant --item {item_id}`; "
            "require the guard to go RED, restore the fixture, then require GREEN."
        ),
        "reason": None,
    }


def is_guarding(text: str, facet: str) -> bool:
    if facet in {"negative-invocation", "planted-failure", "operation-cell", "meta-governance", "sub-primitive", "wiring-edge"}:
        return True
    lowered = text.lower()
    return any(term in lowered for term in GUARD_TERMS)


def make_item(
    track: str,
    number: int,
    component: str,
    title: str,
    kind: str,
    tier: str,
    owner: str,
    disposition: str,
    depends_on: list[str],
    writes_to: list[str],
    input_contract: str,
    output_contract: str,
    facet: str,
    operation: str | None = None,
) -> dict[str, Any]:
    item_id = f"UP.{track}.{slugify(component)}.{number:03d}"
    guarding = is_guarding(f"{title} {input_contract} {output_contract}", facet)
    return {
        "id": item_id,
        "title": title,
        "kind": kind,
        "tier": tier,
        "owner": owner,
        "disposition": disposition,
        "depends_on": list(dict.fromkeys(depends_on)),
        "writes_to": writes_to,
        "input_contract": input_contract,
        "output_contract": output_contract,
        "authority": authority_for(owner),
        "done_test": executable_done_test(item_id, facet, operation),
        "plant_failure": plant_failure(item_id, guarding),
        "independent_verifier": "GLM 5.3 in fresh context, with a model family different from the Blackwell builder",
        "evidence": {
            "required": ["command", "exit_code", "stdout", "artifact_sha256"],
            "receipts": [],
        },
        "status": "inventoried",
    }


def base_dependencies(track: str, anchors: dict[str, str]) -> list[str]:
    required_tracks = {
        "W00": [],
        "W01": ["W00"],
        "W02": ["W01"],
        "W03": ["W02"],
        "W04": ["W01"],
        "W05": ["W03", "W04"],
        "W06": ["W01", "W03"],
        "W07": ["W01", "W02", "W03"],
        "W08": ["W01", "W02", "W03"],
        "W09": ["W01", "W02", "W03"],
        "W10": ["W01", "W02", "W03"],
        "W11": ["W07", "W08", "W09", "W10"],
        "W12": ["W03"],
        "W13": ["W02", "W03", "W12"],
        "W14": list(TRACK_TOTALS)[:-1],
    }[track]
    return [anchors[name] for name in required_tracks]


def disposition_for(track: str, facet: str) -> str:
    if track in {"W00"}:
        return "reuse"
    if track in {"W04"}:
        return "repair"
    if track in {"W06", "W12", "W13"}:
        return "extend"
    if facet in {"positive-invocation", "independent-verification", "evidence-binding", "traceability"}:
        return "extend"
    return "create"


def build_regular_track(track: str, anchors: dict[str, str]) -> list[dict[str, Any]]:
    requirements = TRACK_REQUIREMENTS[track]
    target = TRACK_TOTALS[track]
    dependencies = base_dependencies(track, anchors)
    items: list[dict[str, Any]] = []
    contract_ids: dict[int, str] = {}
    for offset in range(target):
        facet_index, requirement_index = divmod(offset, len(requirements))
        facet, verb, kind, default_owner = FACETS[facet_index]
        requirement = requirements[requirement_index]
        coverage = coverage_clause(REGULAR_COVERAGE.get((track, requirement_index), ()))
        number = offset + 1
        owner = infer_owner(requirement, default_owner)
        actual_kind = infer_kind(requirement, kind) if facet == "implementation" else kind
        item_dependencies = dependencies if facet_index == 0 else dependencies + [contract_ids[requirement_index]]
        item = make_item(
            track=track,
            number=number,
            component=f"r{requirement_index + 1:02d}-{facet}",
            title=f"{verb} {requirement}",
            kind=actual_kind,
            tier="shared" if track in {"W00", "W06", "W13", "W14"} else "normal",
            owner=owner,
            disposition=disposition_for(track, facet),
            depends_on=item_dependencies,
            writes_to=TRACK_WRITES[track],
            input_contract=(
                f"Contract requirement: {requirement}. Facet: {facet}. Inputs must carry version, provenance, "
                f"actor identity, and the preceding dependency receipts.{coverage}"
            ),
            output_contract=(
                f"Durable {facet} result for '{requirement}' with observable state, artifact hash, "
                "command receipt, and invalidation metadata."
            ),
            facet=facet,
        )
        items.append(item)
        if facet_index == 0:
            contract_ids[requirement_index] = item["id"]
    return items


def flattened_operations(track: str) -> list[tuple[str, str]]:
    return [
        (studio, operation)
        for studio, operations in STUDIO_OPERATIONS[track].items()
        for operation in operations
    ]


def studio_operation_owner(studio: str, operation: str) -> str:
    if studio == "execution" and operation in {"lease", "dispatch", "worker", "integrate", "receipts"}:
        return "firstmate"
    if operation in {"done-test-register", "plant-failure", "chain", "sssf-gates", "seal", "proofpacket", "ledger-register", "resolve-and-score"}:
        return "deterministic"
    return "blackwell"


def build_studio_track(
    track: str,
    anchors: dict[str, str],
    operation_ids: dict[str, list[str]],
) -> list[dict[str, Any]]:
    dependencies = base_dependencies(track, anchors)
    operations = flattened_operations(track)
    items: list[dict[str, Any]] = []
    core_ids: list[str] = []

    for studio, operation in operations:
        number = len(items) + 1
        owner = studio_operation_owner(studio, operation)
        coverage = coverage_clause(OPERATION_COVERAGE.get((studio, operation), ()))
        item = make_item(
            track=track,
            number=number,
            component=f"{studio}-{operation}-cell",
            title=f"Assemble the {studio} {operation} normal operation cell",
            kind="harness",
            tier="normal",
            owner=owner,
            disposition="create",
            depends_on=dependencies,
            writes_to=[f"{ULTRAPLAN}/cells/{studio}", RIG_CAPABILITIES_PLAN],
            input_contract=(
                f"The {studio}.{operation} operation receives versioned evidence, budgets, actor identity, "
                "provenance, freshness limits, and dependency receipts. Its eight-slot cell declares: "
                "skill; agent contract; prompt template or deterministic-only declaration; harness with "
                "inputs, outputs, budgets, and done-test; pre-action, post-result, and completion hooks; "
                "bounded loop with repair, park, and exit behavior; context with provenance and freshness "
                f"policy; and route with consumers and dependencies.{coverage}"
            ),
            output_contract=(
                f"A bounded {studio}.{operation} result with typed artifacts, route and hook receipts, "
                "positive and negative behavior, repair or park exit, and independently rerunnable evidence."
            ),
            facet="operation-cell",
            operation=f"{studio}.{operation}",
        )
        items.append(item)
        core_ids.append(item["id"])
        operation_ids.setdefault(studio, []).append(item["id"])

    for requirement_index, requirement in enumerate(STUDIO_REQUIREMENTS[track], start=1):
        number = len(items) + 1
        default_owner = "astra" if any(word in requirement.lower() for word in ("require", "represent", "support")) else "blackwell"
        owner = infer_owner(requirement, default_owner)
        coverage = coverage_clause(STUDIO_REQUIREMENT_COVERAGE.get((track, requirement_index - 1), ()))
        item = make_item(
            track=track,
            number=number,
            component=f"studio-requirement-{requirement_index:02d}",
            title=requirement,
            kind=infer_kind(requirement, "harness"),
            tier="normal",
            owner=owner,
            disposition="create",
            depends_on=dependencies + core_ids,
            writes_to=TRACK_WRITES[track],
            input_contract=f"All affected operation-cell receipts plus the literal studio requirement: {requirement}.{coverage}",
            output_contract=f"An executable studio-level guard and receipt proving: {requirement}.",
            facet="studio-requirement",
        )
        items.append(item)

    remaining = TRACK_TOTALS[track] - len(items)
    evidence_modes = [
        ("positive-invocation", "Positive invocation evidence", "accepted"),
        ("negative-invocation", "Negative invocation evidence", "blocked"),
        ("independent-verification", "Independent GLM evidence", "verified"),
    ]
    candidates = [
        (studio, operation, core_ids[index], mode, label, outcome)
        for mode, label, outcome in evidence_modes
        for index, (studio, operation) in enumerate(operations)
    ]
    assert remaining <= len(candidates), (track, remaining, len(candidates))

    for studio, operation, core_id, mode, label, outcome in candidates[:remaining]:
        number = len(items) + 1
        item = make_item(
            track=track,
            number=number,
            component=f"{studio}-{operation}-{mode}",
            title=f"{label} for {studio} {operation}",
            kind="test",
            tier="normal",
            owner="glm",
            disposition="extend",
            depends_on=dependencies + [core_id],
            writes_to=[f"{ULTRAPLAN}/cells/{studio}", RIG_CAPABILITIES_PLAN],
            input_contract=(
                f"Invoke {studio}.{operation} through its registered real route using the {mode} fixture, "
                "with fixed inputs, budgets, freshness policy, and expected outcome '{outcome}'."
            ),
            output_contract=(
                f"Rerunnable {mode} receipt for {studio}.{operation}, including command, exit code, "
                "observable result, artifact hash, and verifier identity."
            ),
            facet=mode,
            operation=f"{studio}.{operation}",
        )
        items.append(item)

    assert len(items) == TRACK_TOTALS[track]
    return items


def build_w11(
    anchors: dict[str, str],
    operation_ids: dict[str, list[str]],
) -> list[dict[str, Any]]:
    dependencies = base_dependencies("W11", anchors)
    items: list[dict[str, Any]] = []
    meta_ids: dict[str, str] = {}
    primitive_ids: dict[str, str] = {}

    for component in META_COMPONENTS:
        number = len(items) + 1
        owner = "deterministic" if component in {"ultraplan-root", "five-phases", "nine-engine-stages"} else "astra"
        item = make_item(
            track="W11",
            number=number,
            component=f"meta-{component}",
            title=f"Govern the {component} meta component set without duplicating normal behavior",
            kind="harness",
            tier="meta",
            owner=owner,
            disposition="create",
            depends_on=dependencies,
            writes_to=TRACK_WRITES["W11"],
            input_contract=f"Resolved W07-W10 operation receipts and policy inputs for the {component} governing set.",
            output_contract=f"A bounded {component} selector, budget, route, and evaluation contract that only references normal cells.",
            facet="meta-governance",
        )
        items.append(item)
        meta_ids[component] = item["id"]

    for primitive in SUB_PRIMITIVES:
        number = len(items) + 1
        owner = infer_owner(primitive, "blackwell")
        item = make_item(
            track="W11",
            number=number,
            component=f"sub-{primitive}",
            title=f"Share the {primitive} subcomponent by reference",
            kind=infer_kind(primitive, "runtime"),
            tier="sub",
            owner=owner,
            disposition="reuse" if primitive.startswith("jev-") else "create",
            depends_on=dependencies + [meta_ids["cross-cutting-capability-registry"]],
            writes_to=TRACK_WRITES["W11"],
            input_contract=f"Typed callers, envelopes, and policy constraints for the reusable {primitive} primitive.",
            output_contract=f"One versioned {primitive} implementation referenced by normal cells, with no per-operation copy.",
            facet="sub-primitive",
        )
        items.append(item)
        primitive_ids[primitive] = item["id"]

    studios = list(operation_ids)
    edge_specs = [
        ("meta-selection", "model-routing", "model-family-ladder"),
        ("schema-validation", "cross-cutting-capability-registry", "schema-validator"),
        ("route-resolution", "nine-studios", "route-resolver"),
        ("context-provenance-freshness", "context-policy", "liveness-check"),
        ("evidence-hash-receipt", "evidence-policy", "artifact-hasher"),
    ]
    for edge_name, meta_name, primitive_name in edge_specs:
        for studio in studios:
            number = len(items) + 1
            refs = operation_ids[studio]
            item = make_item(
                track="W11",
                number=number,
                component=f"edge-{studio}-{edge_name}",
                title=f"Resolve the {studio} {edge_name} meta-to-normal-to-sub wiring edge",
                kind="route",
                tier="normal",
                owner="deterministic" if edge_name in {"schema-validation", "route-resolution"} else "astra",
                disposition="create",
                depends_on=dependencies + refs + [meta_ids[meta_name], primitive_ids[primitive_name]],
                writes_to=TRACK_WRITES["W11"],
                input_contract=(
                    f"The {studio} operation-cell IDs {', '.join(refs)} plus meta component {meta_name} "
                    f"and shared primitive {primitive_name}."
                ),
                output_contract=(
                    f"A resolved, acyclic {studio} {edge_name} edge whose referenced cells and primitive "
                    "versions remain hash-bound and freshness-checked."
                ),
                facet="wiring-edge",
            )
            items.append(item)

    global_edges = [
        (
            "recursive-child-expansion-guard",
            "Guard every meta, normal, and sub child expansion against cycles and unbounded recursion",
            "schema-validator",
        ),
        (
            "shared-primitive-reference-guard",
            "Guard every normal cell against copying a shared subcomponent implementation",
            "receipt-verifier",
        ),
    ]
    all_operation_refs = [item_id for refs in operation_ids.values() for item_id in refs]
    for component, title, primitive in global_edges:
        number = len(items) + 1
        item = make_item(
            track="W11",
            number=number,
            component=f"edge-{component}",
            title=title,
            kind="test",
            tier="normal",
            owner="deterministic",
            disposition="create",
            depends_on=dependencies + all_operation_refs + [primitive_ids[primitive]],
            writes_to=TRACK_WRITES["W11"],
            input_contract="The complete W07-W10 operation graph, all meta roots, and all referenced subcomponent versions.",
            output_contract=f"A distinct {component} receipt proving the hierarchy is finite, resolved, and shared by reference.",
            facet="wiring-edge",
        )
        items.append(item)

    assert len(META_COMPONENTS) == 10
    assert len(SUB_PRIMITIVES) == 24
    assert len(items) == TRACK_TOTALS["W11"], len(items)
    return items


def generate_items() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    anchors: dict[str, str] = {}
    operation_ids: dict[str, list[str]] = {}

    for track in TRACK_TOTALS:
        if track in STUDIO_OPERATIONS:
            track_items = build_studio_track(track, anchors, operation_ids)
        elif track == "W11":
            track_items = build_w11(anchors, operation_ids)
        else:
            track_items = build_regular_track(track, anchors)
        items.extend(track_items)
        anchors[track] = track_items[-1]["id"]
    return items


def validate_items(items: list[dict[str, Any]]) -> Counter[str]:
    required_fields = {
        "id", "title", "kind", "tier", "owner", "disposition", "depends_on",
        "writes_to", "input_contract", "output_contract", "authority", "done_test",
        "plant_failure", "independent_verifier", "evidence", "status",
    }
    allowed_kinds = {
        "prompt", "agent", "skill", "harness", "hook", "loop", "context", "route",
        "runtime", "ui", "test", "migration", "documentation",
    }
    allowed_tiers = {"meta", "normal", "sub", "shared"}
    allowed_owners = {"astra", "blackwell", "glm", "firstmate", "deterministic"}
    allowed_dispositions = {"reuse", "repair", "extend", "create"}
    id_pattern = re.compile(r"^UP\.(W\d{2})\.[a-z0-9-]+\.\d{3}$")

    assert len(items) == ACTUAL_TOTAL, (len(items), ACTUAL_TOTAL)
    ids = [item["id"] for item in items]
    assert len(ids) == len(set(ids)), "duplicate manifest IDs"
    id_set = set(ids)
    positions = {item_id: index for index, item_id in enumerate(ids)}
    counts: Counter[str] = Counter()

    for item in items:
        assert set(item) == required_fields, (item["id"], set(item) ^ required_fields)
        match = id_pattern.fullmatch(item["id"])
        assert match, item["id"]
        track = match.group(1)
        counts[track] += 1
        for field in ("title", "kind", "tier", "owner", "disposition", "done_test", "status"):
            assert isinstance(item[field], str) and item[field].strip(), (item["id"], field)
        assert item["kind"] in allowed_kinds, item["id"]
        assert item["tier"] in allowed_tiers, item["id"]
        assert item["owner"] in allowed_owners, item["id"]
        assert item["disposition"] in allowed_dispositions, item["id"]
        assert item["status"] == "inventoried", item["id"]
        assert item["writes_to"], item["id"]
        assert item["input_contract"].strip() and item["output_contract"].strip(), item["id"]
        assert item["authority"].strip() and item["independent_verifier"].strip(), item["id"]
        assert item["plant_failure"]["procedure"] or item["plant_failure"]["reason"] == "non-guarding", item["id"]
        for dependency in item["depends_on"]:
            assert dependency in id_set, (item["id"], dependency)
            assert positions[dependency] < positions[item["id"]], (item["id"], dependency)

    assert dict(counts) == TRACK_TOTALS, (dict(counts), TRACK_TOTALS)
    assert sum(counts.values()) == ACTUAL_TOTAL
    serialized_items = json.dumps(items, sort_keys=True)
    for coverage_id in MANDATORY_COVERAGE:
        assert f"[covers:{coverage_id}]" in serialized_items, f"unmapped mandatory coverage {coverage_id}"
    w11_components = [item["id"].split(".")[2] for item in items if item["id"].startswith("UP.W11.")]
    assert len(w11_components) == len(set(w11_components)), "duplicate W11 primitive or wiring edge"
    return counts


def validate_serialized_document(document: dict[str, Any]) -> None:
    text = OUTPUT.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        loaded = json.loads(text)
        parser = "stdlib json"
    else:
        loaded = yaml.safe_load(text)
        parser = "PyYAML"
    assert loaded == document, f"serialized manifest changed when loaded through {parser}"
    assert len(loaded["items"]) == ACTUAL_TOTAL
    print(f"ASSERT parse_round_trip OK ({parser})")


def main() -> None:
    contract_bytes = CONTRACT.read_bytes()
    contract_sha256 = hashlib.sha256(contract_bytes).hexdigest()
    items = generate_items()
    counts = validate_items(items)
    document = {
        "generated_by": "plans/ultraplan-v2/gen_manifest.py",
        "contract_sha256": contract_sha256,
        "generated_at": GENERATED_AT,
        "totals": {
            "contract_declared_total": CONTRACT_DECLARED_TOTAL,
            "actual_total": ACTUAL_TOTAL,
            "track_counts_sum": sum(TRACK_TOTALS.values()),
            "by_track": TRACK_TOTALS,
            "discrepancy_note": (
                "The contract declares 864 total items, but its fifteen authoritative per-track "
                "counts sum to 904. Captain ruling on 2026-09-20 preserves every per-track count, "
                "including W11=76, and records rather than conceals the 40-item discrepancy."
            ),
        },
        "items": items,
    }
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    validate_serialized_document(document)
    print(f"ASSERT total OK {len(items)}")
    print("ASSERT unique_ids OK")
    print("ASSERT dependencies OK")
    print("ASSERT required_fields OK")
    print(f"OK {len(items)}")
    print(" ".join(f"{track} {counts[track]}" for track in TRACK_TOTALS))


if __name__ == "__main__":
    main()
