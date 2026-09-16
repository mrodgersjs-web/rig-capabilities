"""chunk.py — decompose a mission into chunks, keep the critical ones with Mike, fan the rest
through NVIDIA PAIR, and PROVE where each one actually ran.

Why this module exists (evidence, 2026-09-15):

  * PAIR (127.0.0.1:11435, bundled `ollama-proxy` 0.26.2) routes one request to one
    model-owning node. NVIDIA's own split is "Hermes decomposes / PAIR routes / Ollama
    executes" — PAIR has no queue, no max-concurrency, and no decomposition. Backpressure
    is therefore OUR job: it forwards immediately and only retries upstream 429s.
  * PAIR persists every routed request to `workloads-history.json` with `originatedFrom`
    and `scheduledOn` node UUIDs. That makes offload PROVABLE after the fact instead of
    merely claimed. `verify()` is built on it.
  * Carrier selection is NOT invented here. `/Users/rig128gb/.rig/bin/rig-owner-router` is
    the executable form of RIG_OWNER_ROUTING_DOCTRINE.md and owns that verdict.
    `/Users/rig128gb/.rig/node-ops/fleet-routing/fleet_routing_v1.py` already owns
    inference-plane priority (P1 PAIR/Ollama -> P2 Blackwell -> P3 oMLX -> P4 paid).

The criticality gate is fail-closed toward Mike: anything that looks like design, a control
plane, an outward effect, or an unverifiable chunk stays LOCAL. A chunk missing the fields
needed to judge it is REFUSED, never quietly fanned out.

Stdlib only (house rule: the hermes venv has no PyYAML/requests).
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal

SCHEMA = "rig.chunk.plan.v1"

PAIR_BASE = "http://127.0.0.1:11435"
PAIR_SUPPORT = Path.home() / "Library/Application Support/Nvidia Corporation/Personal AI Router"
PAIR_MEMBERS = PAIR_SUPPORT / "cluster/members.json"
PAIR_HISTORY = PAIR_SUPPORT / "workloads-history.json"
OWNER_ROUTER = Path("/Users/rig128gb/.rig/bin/rig-owner-router")
RUN_ROOT = Path.home() / ".rig/state/chunk-runs"

Lane = Literal["local", "fanout", "refused"]

# A chunk touching any of these stays with Mike: design authority, control plane, outward
# effect, security boundary, instruction surface.
#
# `scope` matters. Design intent lives in what the work IS (title + prompt); the acceptance
# text only describes how the result gets checked, so scanning it for design words produces
# false holds — "acceptance: single word naming a color" is not an API-naming decision, and a
# gate that trips on it keeps everything local and defeats the point. Effects, controls,
# secrets and doctrine ARE scanned in acceptance too, because an outward action hidden in a
# check ("acceptance: the post is published") is exactly what must not be delegated.
CRITICAL_PATTERNS: tuple[tuple[str, str, str], ...] = (
    (
        "design",
        r"\b(design(s|ed|ing)?|architect(s|ed|ing|ure|ural)?)\b"
        r"|\b(api|public|interface|abi) (surface|contract|shape)\b"
        r"|\b(data model|schema|migration|db migration)\b"
        r"|\brenam(e|es|ed|ing)\b"
        r"|\bnaming (convention|scheme|decision|standard)\b"
        r"|\bname the (api|interface|type|module|endpoint|table|column|command|flag)\b",
        "work",
    ),
    ("control", r"\b(approval|permission|budget|quota|retry polic(y|ies)|idempotenc(y|e)|rate limit|kill switch|gate-?d)\b", "all"),
    ("effect", r"\b(publish(ed|es|ing)?|deploy(ed|s|ing)?|release[ds]?|push(ed|es|ing)?|merge[ds]?|send|sent|email|dm|payment|charge[ds]?|invoice|refund|delete[ds]?|drop|destroy|revoke|rotate)\b", "all"),
    ("security", r"\b(credential|secret|api key|password|private key|pii|phi)\b|"
                 r"\b(auth|access|bearer|refresh|session|api|secret|oauth|jwt) token\b|"
                 r"\btoken (secret|credential|rotation|value)\b", "all"),
    ("doctrine", r"\b(doctrine|instruction surface|agents\.md|claude\.md|system prompt|policy file)\b", "all"),
)

# Work class -> models to prefer, best first. Availability is checked against live PAIR, so a
# model still downloading onto a node is skipped until it lands.
#
# Capability-first policy, grounded in the official Hugging Face cards:
#   * Qwen3.8-Flash-Next (125B / 6B active + 51B n-gram + 4B MTP) is the strongest
#     open-weight candidate: DeepSWE 58.7, SWE-bench Pro 62.5, Toolathlon 73.5. Its GGUF is
#     129–161GB (Q2–Q4), so only the 256GB node can host it.
#   * Qwen3.8-27B is the best practical model for the 36/96GB tier: Terminal Bench 73.0,
#     SWE-bench Pro 61.7, QwenSWEBench 79.0, native 262K context.
#   * qwen3.5:9b is the small-node quality floor. There is NO official Qwen3.8-9B model.
#   * qwen3:4b is triage-only. It exists for cheap routing/smoke/probes, never coding,
#     reasoning, summarization, extraction, or long-context work.
#
# Target fleet matrix (Blackwell 192.168.68.90 EXCLUDED by operator instruction):
#   .52 36GB    Qwen3.8-27B + qwen3.5:9b + triage:4b + embeddings
#   .53 256GB   Qwen3.8-Flash-Next Q4 + Qwen3.8-27B + coder/reasoning fallbacks
#   .60 24GB    qwen3.5:9b + triage:4b + embeddings
#   .64 28GB    qwen3.5:9b + 30/32B fallbacks already resident + triage:4b
#   .74 96GB    Qwen3.8-27B + qwen3:32b + coder/longctx fallbacks
#   local 128GB embeddings only, deliberately bare so work does not land here
FLASH_NEXT = "hf.co/unsloth/Qwen3.8-Flash-Next-GGUF:UD-Q4_K_XL"

WORK_CLASS_MODELS: dict[str, tuple[str, ...]] = {
    "code": (FLASH_NEXT, "qwen3.8:27b", "qwen3-coder:30b", "deepseek-r1:32b"),
    "reason": (FLASH_NEXT, "qwen3.8:27b", "qwen3:32b", "deepseek-r1:32b", "qwen3.6:35b-a3b", "ornith:35b"),
    "summarize": ("qwen3.8:27b", "qwen3.5:9b", "qwen3:32b"),
    "extract": ("qwen3.5:9b", "qwen3.8:27b"),
    "longctx": (FLASH_NEXT, "qwen3.8:27b", "laguna-262k:latest", "rig-96gb-laguna:latest", "qwen3:32b"),
    "triage": ("qwen3:4b", "qwen3.5:9b"),
    "embed": ("nomic-embed-text:latest",),
}
DEFAULT_WORK_CLASS = "summarize"


class ChunkError(Exception):
    """Refusal or contract violation. Carries the reason the caller must show a human."""


@dataclass(frozen=True)
class Chunk:
    """One unit of work. `acceptance` is mandatory for fan-out: a chunk nobody can check
    cannot be delegated, so it stays local by construction."""

    id: str
    title: str
    prompt: str
    work_class: str = DEFAULT_WORK_CLASS
    acceptance: str = ""
    reversible: bool = True
    failure_cost: float = 0.0
    est_tokens: int = 0

    @staticmethod
    def from_obj(obj: dict[str, Any]) -> "Chunk":
        missing = [k for k in ("id", "title", "prompt") if not str(obj.get(k, "")).strip()]
        if missing:
            raise ChunkError(f"chunk missing required field(s): {', '.join(missing)}")
        cost = obj.get("failure_cost", 0.0)
        if not isinstance(cost, (int, float)) or isinstance(cost, bool) or not 0.0 <= float(cost) <= 1.0:
            raise ChunkError(f"chunk {obj['id']}: failure_cost must be a number in [0,1], got {cost!r}")
        reversible = obj.get("reversible", True)
        if not isinstance(reversible, bool):
            raise ChunkError(f"chunk {obj['id']}: reversible must be a bool, got {reversible!r}")
        work_class = str(obj.get("work_class", DEFAULT_WORK_CLASS))
        if work_class not in WORK_CLASS_MODELS:
            raise ChunkError(f"chunk {obj['id']}: unknown work_class {work_class!r}; known: {sorted(WORK_CLASS_MODELS)}")
        return Chunk(
            id=str(obj["id"]),
            title=str(obj["title"]),
            prompt=str(obj["prompt"]),
            work_class=work_class,
            acceptance=str(obj.get("acceptance", "")),
            reversible=reversible,
            failure_cost=float(cost),
            est_tokens=int(obj.get("est_tokens", 0) or 0),
        )

    def key(self, mission_id: str) -> str:
        raw = f"{mission_id}\x00{self.id}\x00{self.prompt}".encode()
        return hashlib.sha256(raw).hexdigest()[:16]


@dataclass
class Verdict:
    chunk_id: str
    lane: Lane
    reasons: list[str] = field(default_factory=list)
    owner: str = ""
    model: str = ""
    placement: str = "unproven"


def classify(chunk: Chunk) -> Verdict:
    """Fail-closed criticality gate. LOCAL wins over FANOUT whenever either fires."""
    reasons: list[str] = []
    work_text = f"{chunk.title}\n{chunk.prompt}".lower()
    full_text = f"{work_text}\n{chunk.acceptance}".lower()
    for label, pattern, scope in CRITICAL_PATTERNS:
        hit = re.search(pattern, work_text if scope == "work" else full_text)
        if hit:
            reasons.append(f"critical:{label}:{hit.group(0)}")
    if not chunk.reversible:
        reasons.append("critical:irreversible")
    if chunk.failure_cost >= 0.5:
        reasons.append(f"critical:failure_cost={chunk.failure_cost}")
    if not chunk.acceptance.strip():
        reasons.append("critical:no-acceptance-check")
    if reasons:
        return Verdict(chunk_id=chunk.id, lane="local", reasons=reasons)
    return Verdict(chunk_id=chunk.id, lane="fanout", reasons=["delegable"])


def owner_for(text: str, *, router: Path = OWNER_ROUTER) -> str:
    """Carrier verdict from the doctrine's own executable. Never re-implemented here.
    An unavailable router is reported as `review-required`, never guessed green."""
    if not router.exists():
        return "review-required:router-missing"
    try:
        out = subprocess.run([str(router), "route", text], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        return f"review-required:router-error:{type(exc).__name__}"
    if out.returncode != 0:
        return f"review-required:exit{out.returncode}"
    try:
        return str(json.loads(out.stdout).get("owner", "review-required:no-owner"))
    except json.JSONDecodeError:
        return "review-required:unparseable"


def _get_json(url: str, timeout: int = 15) -> Any:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read())


def pair_models(*, base: str = PAIR_BASE) -> list[str]:
    """Live model inventory. PAIR gates each request on exact model availability, so a model
    absent here can never be routed."""
    payload = _get_json(f"{base}/v1/models")
    return [str(m["id"]) for m in payload.get("data", []) if m.get("id")]


def local_node_uuid(*, members: Path = PAIR_MEMBERS) -> str:
    """This machine's PAIR node UUID — the thing offloaded work must NOT be scheduled on.
    Identified by the loopback address PAIR records for the local member."""
    if not members.exists():
        raise ChunkError(f"PAIR cluster members not found at {members}")
    rows = json.loads(members.read_text())
    for row in rows:
        if str(row.get("ipAddress", "")) in {"127.0.0.1", "::1", "localhost"}:
            return str(row["nodeUuid"])
    raise ChunkError("no loopback member in PAIR cluster file; cannot identify the local node")


def observed_placements(*, history: Path = PAIR_HISTORY) -> dict[str, set[str]]:
    """model -> set of node UUIDs PAIR has actually scheduled it on. Evidence, not config."""
    if not history.exists():
        return {}
    seen: dict[str, set[str]] = {}
    for row in json.loads(history.read_text()):
        model, node = row.get("model"), row.get("scheduledOn")
        if model and node:
            seen.setdefault(str(model), set()).add(str(node))
    return seen


def pick_model(chunk: Chunk, available: Iterable[str], placements: dict[str, set[str]], local_uuid: str) -> tuple[str, str]:
    """(model, placement) for a chunk. `placement` states what the EVIDENCE supports:
      offload-proven  — PAIR has scheduled this model on a remote node before
      local-only      — every observation ran here; offloading it would be a lie
      unproven        — never observed; verify() decides after the run
    """
    ready = set(available)
    for model in WORK_CLASS_MODELS.get(chunk.work_class, ()):
        if model not in ready:
            continue
        nodes = placements.get(model, set())
        remote = nodes - {local_uuid}
        if remote:
            return model, "offload-proven"
        if nodes:
            return model, "local-only"
        return model, "unproven"
    raise ChunkError(
        f"chunk {chunk.id}: no model for work_class {chunk.work_class!r} is available on PAIR "
        f"(wanted one of {WORK_CLASS_MODELS.get(chunk.work_class, ())})"
    )


def plan(mission: dict[str, Any], *, base: str = PAIR_BASE, allow_local_only: bool = False) -> dict[str, Any]:
    """Split a mission into local / fanout / refused lanes. Pure classification: dispatches
    nothing, mutates nothing outward."""
    mission_id = str(mission.get("mission_id") or "").strip()
    if not mission_id:
        raise ChunkError("mission missing mission_id")
    raw_chunks = mission.get("chunks")
    if not isinstance(raw_chunks, list) or not raw_chunks:
        raise ChunkError("mission has no chunks[]")

    available = pair_models(base=base)
    local_uuid = local_node_uuid()
    placements = observed_placements()

    lanes: dict[str, list[dict[str, Any]]] = {"local": [], "fanout": [], "refused": []}
    for obj in raw_chunks:
        try:
            chunk = Chunk.from_obj(obj if isinstance(obj, dict) else {})
        except ChunkError as exc:
            lanes["refused"].append({"chunk": obj, "reason": str(exc)})
            continue
        verdict = classify(chunk)
        verdict.owner = owner_for(f"{chunk.title}: {chunk.prompt}"[:400])
        row: dict[str, Any] = {"chunk": asdict(chunk), "verdict": asdict(verdict), "key": chunk.key(mission_id)}
        if verdict.lane == "local":
            lanes["local"].append(row)
            continue
        try:
            model, placement = pick_model(chunk, available, placements, local_uuid)
        except ChunkError as exc:
            lanes["refused"].append({"chunk": asdict(chunk), "reason": str(exc)})
            continue
        if placement == "local-only" and not allow_local_only:
            lanes["refused"].append({
                "chunk": asdict(chunk),
                "reason": f"model {model} has only ever been scheduled on this box; "
                          "fanning it out would not free the 128GB (pass allow_local_only to override)",
            })
            continue
        verdict.model, verdict.placement = model, placement
        row["verdict"] = asdict(verdict)
        lanes["fanout"].append(row)

    return {
        "schema": SCHEMA,
        "mission_id": mission_id,
        "goal": str(mission.get("goal", "")),
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pair": {"base": base, "local_node_uuid": local_uuid, "models_available": len(available)},
        "counts": {lane: len(rows) for lane, rows in lanes.items()},
        "lanes": lanes,
    }


def _post_chat(base: str, model: str, prompt: str, *, max_tokens: int, timeout: int) -> tuple[int, str]:
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "stream": False,
    }).encode()
    req = urllib.request.Request(f"{base}/v1/chat/completions", data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read())
        choices = payload.get("choices") or [{}]
        return 200, str(choices[0].get("message", {}).get("content", ""))
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()[:400].decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return 0, f"{type(exc).__name__}: {exc}"


def dispatch(
    plan_obj: dict[str, Any],
    *,
    base: str = PAIR_BASE,
    max_inflight: int = 4,
    attempts: int = 3,
    max_tokens: int = 1024,
    timeout: int = 300,
    run_root: Path = RUN_ROOT,
) -> dict[str, Any]:
    """Fan out the `fanout` lane through PAIR with OUR backpressure (PAIR has none).

    Retries 429/5xx/transport with exponential backoff. Idempotent per chunk key: an existing
    artifact is reused unless deleted. Touches no chunk in the local or refused lanes, and
    performs no outward effect of any kind.
    """
    if plan_obj.get("schema") != SCHEMA:
        raise ChunkError(f"not a {SCHEMA} plan")
    run_id = f"{plan_obj['mission_id']}-{int(time.time())}"
    run_dir = run_root / run_id
    (run_dir / "chunks").mkdir(parents=True, exist_ok=True)
    (run_dir / "plan.json").write_text(json.dumps(plan_obj, indent=2))
    ledger = run_dir / "ledger.jsonl"

    def one(row: dict[str, Any]) -> dict[str, Any]:
        chunk, verdict = row["chunk"], row["verdict"]
        artifact = run_dir / "chunks" / f"{row['key']}.json"
        if artifact.exists():
            return {"chunk_id": chunk["id"], "state": "reused", "artifact": str(artifact)}
        started = time.time()
        status, text = 0, ""
        for attempt in range(1, attempts + 1):
            status, text = _post_chat(base, verdict["model"], chunk["prompt"], max_tokens=max_tokens, timeout=timeout)
            if status == 200:
                break
            if attempt < attempts:
                time.sleep(min(2 ** attempt, 8))
        record = {
            "chunk_id": chunk["id"],
            "key": row["key"],
            "model": verdict["model"],
            "status": status,
            "state": "completed" if status == 200 else "failed",
            "started_ms": int(started * 1000),
            "finished_ms": int(time.time() * 1000),
            "output": text,
        }
        artifact.write_text(json.dumps(record, indent=2))
        with ledger.open("a") as fh:
            fh.write(json.dumps({k: v for k, v in record.items() if k != "output"}) + "\n")
        return {k: v for k, v in record.items() if k != "output"} | {"artifact": str(artifact)}

    rows = plan_obj["lanes"]["fanout"]
    with ThreadPoolExecutor(max_workers=max(1, max_inflight)) as pool:
        results = list(pool.map(one, rows))

    return {
        "schema": "rig.chunk.dispatch.v1",
        "run_id": run_id,
        "run_dir": str(run_dir),
        "dispatched": len(results),
        "completed": sum(1 for r in results if r.get("state") in {"completed", "reused"}),
        "failed": sum(1 for r in results if r.get("state") == "failed"),
        "kept_local": len(plan_obj["lanes"]["local"]),
        "refused": len(plan_obj["lanes"]["refused"]),
        "results": results,
    }


def _history_rows(history: Path) -> list[dict[str, Any]]:
    if not history.exists():
        return []
    try:
        return json.loads(history.read_text())
    except json.JSONDecodeError:
        return []  # mid-write by PAIR; the settle loop retries


def _matches(rows: list[dict[str, Any]], model: str, started: int, finished: int, window_ms: int) -> list[dict[str, Any]]:
    return [
        r for r in rows
        if str(r.get("model")) == model
        and started - window_ms <= int(r.get("startedAt") or 0) <= finished + window_ms
    ]


def verify(
    dispatch_obj: dict[str, Any],
    *,
    history: Path = PAIR_HISTORY,
    members: Path = PAIR_MEMBERS,
    window_ms: int = 5000,
    settle_s: float = 15.0,
) -> dict[str, Any]:
    """Prove where the work RAN, from PAIR's own ledger.

    Matches each dispatched chunk to `workloads-history.json` rows by model plus a start-time
    window, then checks `scheduledOn`. Verdicts:
      OFFLOAD_PROVEN    — every matched row ran on a node that is not this box
      OFFLOAD_VIOLATION — at least one matched row ran here (the offload claim is false)
      UNPROVEN          — no matching row; absence of evidence is never a pass

    PAIR's workload manager flushes history AFTER the HTTP response returns, so reading once
    immediately after dispatch races the writer and reports a false UNPROVEN. We poll until
    every dispatched chunk has a row or `settle_s` expires — a bounded wait, never an assumption.
    """
    local_uuid = local_node_uuid(members=members)
    pending = [r for r in dispatch_obj.get("results", []) if r.get("state") != "reused"]
    deadline = time.time() + max(0.0, settle_s)
    rows = _history_rows(history)
    while pending and time.time() < deadline:
        if all(_matches(rows, str(r.get("model")), r.get("started_ms", 0), r.get("finished_ms", 0), window_ms) for r in pending):
            break
        time.sleep(0.5)
        rows = _history_rows(history)
    checks: list[dict[str, Any]] = []
    for result in dispatch_obj.get("results", []):
        if result.get("state") == "reused":
            checks.append({"chunk_id": result.get("chunk_id"), "verdict": "UNPROVEN", "reason": "artifact reused; no new routing"})
            continue
        started, finished = result.get("started_ms", 0), result.get("finished_ms", 0)
        matched = _matches(rows, str(result.get("model")), started, finished, window_ms)
        if not matched:
            checks.append({"chunk_id": result.get("chunk_id"), "verdict": "UNPROVEN", "reason": "no PAIR history row matched"})
            continue
        nodes = {str(r.get("scheduledOn")) for r in matched}
        local_hits = sorted(n for n in nodes if n == local_uuid)
        checks.append({
            "chunk_id": result.get("chunk_id"),
            "verdict": "OFFLOAD_VIOLATION" if local_hits else "OFFLOAD_PROVEN",
            "nodes": sorted(nodes),
            "matched_rows": len(matched),
        })
    verdicts = {c["verdict"] for c in checks}
    overall = "OFFLOAD_VIOLATION" if "OFFLOAD_VIOLATION" in verdicts else (
        "UNPROVEN" if ("UNPROVEN" in verdicts or not checks) else "OFFLOAD_PROVEN"
    )
    return {
        "schema": "rig.chunk.verify.v1",
        "run_id": dispatch_obj.get("run_id"),
        "local_node_uuid": local_uuid,
        "overall": overall,
        "proven": sum(1 for c in checks if c["verdict"] == "OFFLOAD_PROVEN"),
        "violations": sum(1 for c in checks if c["verdict"] == "OFFLOAD_VIOLATION"),
        "unproven": sum(1 for c in checks if c["verdict"] == "UNPROVEN"),
        "checks": checks,
    }


def doctor(*, base: str = PAIR_BASE) -> dict[str, Any]:
    """What is actually reachable right now. Every field is a probe, not a config claim."""
    report: dict[str, Any] = {"schema": "rig.chunk.doctor.v1", "pair_base": base}
    try:
        report["models"] = sorted(pair_models(base=base))
        report["pair"] = "reachable"
    except (urllib.error.URLError, OSError, TimeoutError, json.JSONDecodeError) as exc:
        report["pair"] = f"unreachable: {type(exc).__name__}: {exc}"
        report["models"] = []
    try:
        report["local_node_uuid"] = local_node_uuid()
    except ChunkError as exc:
        report["local_node_uuid"] = f"unknown: {exc}"
    placements = observed_placements()
    local = report.get("local_node_uuid", "")
    report["offload_proven_models"] = sorted(m for m, nodes in placements.items() if nodes - {local})
    report["local_only_models"] = sorted(m for m, nodes in placements.items() if nodes and not (nodes - {local}))
    report["owner_router"] = "present" if OWNER_ROUTER.exists() else "missing"
    report["history_rows"] = len(json.loads(PAIR_HISTORY.read_text())) if PAIR_HISTORY.exists() else 0
    return report
