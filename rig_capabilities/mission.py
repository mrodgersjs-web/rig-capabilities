"""Read-only, evidence-bound composition of agents, skills, prompts and Memory OS.

This module creates a *proposal*, not a dispatch. No selected file, model score,
or memory record authorizes execution. Runtime adapters and outcome receipts are
separate future gates.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sqlite3
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Callable

from .catalog import Repo
from .s1gate import DB_PATH

SCHEMA = "rig.mission.v1"
RUNTIME_SOURCES = {
    "codex": "codex-agents",
    "claude": "claude-agents",
    "hermes": "hermes-agents",
    "omp": "omp-agents",
    "prime": "prime-agents",
}
ROUTABLE_RUNTIMES = {"codex", "claude"}  # other roots are inventoried, not live-smoked
STOP = {"a", "an", "the", "this", "that", "i", "we", "my", "our", "for",
        "and", "or", "to", "of", "in", "on", "with", "want", "need", "please",
        "agent", "agents", "skill", "skills", "prompt", "prompts", "use", "using",
        "fix", "bug", "verify", "regression", "do", "thing"}
GENERIC_TASK_TERMS = {"add", "write", "refactor", "investigate", "review", "audit",
                      "implement", "trace", "explain", "tests", "test", "run",
                      "design", "make", "improve", "handle", "check", "better",
                      "build", "useful"}
TECH_TERMS = {"python", "sql", "react", "kubernetes", "node", "javascript",
              "typescript", "postgres", "rust", "golang", "expo", "native", "api"}
DOMAIN_GUARDS = {"solidity", "blockchain", "smart", "ethereum", "employment"}
ROLE_WORDS = {"agency", "voltagent", "codex", "rig", "pro", "expert",
              "specialist", "engineer", "patterns", "skill"}
META_HINTS = {
    "when-building-or-fixing-agents": {"agent", "subagent", "prompt", "harness", "skill", "mcp"},
    "when-shipping-code": {"code", "coding", "python", "api", "bug", "fix", "test", "debug", "refactor", "build", "kubernetes", "node"},
    "when-working-with-data": {"data", "etl", "pipeline", "database", "sql", "warehouse", "postgres", "postgresql"},
    "when-securing-the-estate": {"security", "vulnerability", "secret", "auth", "authentication", "incident"},
    "when-designing-interfaces": {"ui", "ux", "interface", "accessibility", "react", "keyboard"},
    "when-researching-or-deciding": {"research", "compare", "decide", "evaluate", "evidence"},
    "when-selling-or-running-gtm": {"sales", "gtm", "lead", "campaign", "pricing"},
    "when-writing-content": {"article", "content", "copy", "newsletter", "writing"},
}
JEV_ENDPOINT = "https://api.typesafe.ai/v1/systemone"
PRIVATE_INTENT = re.compile(r"""(
    \bjacob\b | \bnil\b | pewaukee | \bjames\b | \bjennifer\b | \bcoby\b | \bkobe\b | skonord | ideawake | ideaweek | \bkyle\b | puckhaber | \bluca\b
  | \bfamily\b | \b(?:son|daughter|wife|husband)\b | \bclient\s+(?:source|data|records?|contacts?)\b
  | \bsk-[A-Za-z0-9_-]{16,} | \b(?:ghp|gho|ghs|xox[bapr])[-_][A-Za-z0-9-]{10,} | \bAKIA[0-9A-Z]{16}\b
  | -----BEGIN | \b[A-Fa-f0-9]{32,}\b | \b[A-Za-z0-9+/]{40,}={0,2}
  | \bpass(?:word|code)\s*[:=] | \bssn\b | social\s+security | routing\s+number | account\s+number
  | credit\s+card | \biban\b | [\w.+-]+@[\w-]+\.[A-Za-z]{2,}
  | (?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}
  | \$\s?\d[\d,.]*\s?[kKmM]?\b | \b\d{2,3}\s?[kK]\b
  | diagnos | prescription | medical\s+record | \bpatient
)""", re.I | re.X)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(doc: dict) -> bytes:
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _tokens(value: str) -> set[str]:
    tokens = {t for t in re.split(r"[^a-z0-9]+", value.lower()) if len(t) > 1 and t not in STOP}
    # Catalog names and task prose often use different surface forms for one technology.
    if "postgresql" in tokens:
        tokens.remove("postgresql")
        tokens.add("postgres")
    if "postgres" in tokens:
        tokens.add("database")
    if "openapi" in tokens:
        tokens.add("api")
    for plural, singular in (("indexes", "index"), ("migrations", "migration"),
                             ("rollbacks", "rollback")):
        if plural in tokens:
            tokens.remove(plural)
            tokens.add(singular)
    if tokens & {"authentication", "authorization", "privilege"}:
        tokens.add("security")
    if "middleware" in tokens:
        tokens.add("application")
    return tokens


def _path(asset: dict, root: Path) -> Path:
    path = Path(asset.get("abs_path") or root / asset["path"]).expanduser()
    return path / "SKILL.md" if path.is_dir() and asset.get("kind") == "skill" else path


def _ref(asset: dict, root: Path) -> dict | None:
    path = _path(asset, root)
    if not path.is_file():
        return None
    return {"id": asset["id"], "kind": asset["kind"], "source": asset["source"],
            "path": str(path.resolve()), "sha256": _sha(path.read_bytes())}


def _score(query: str, asset: dict, weights: dict[str, float] | None = None) -> float:
    q = _tokens(query) - GENERIC_TASK_TERMS
    if not q:
        return 0.0
    name = _tokens(str(asset.get("name") or asset["id"]))
    desc = _tokens(str(asset.get("description") or ""))
    weights = weights or {}
    score = sum(3.0 * weights.get(t, 1.0) for t in q & name)
    score += sum(0.5 * weights.get(t, 1.0) for t in (q & desc) - name)
    score += 3.0 * len(q & name & TECH_TERMS)
    score -= 1.5 * len((name & TECH_TERMS) - q)
    # A broad overlap must not turn an unrelated specialist into the primary.
    score -= 3.0 * len((name & DOMAIN_GUARDS) - q)
    score -= 1.0 * len(name - q - ROLE_WORDS)
    # "add tests" is a task signal for a tester, but not a standalone domain route.
    if re.search(r"\btests?\b", query.lower()) and name & {"tester", "testing"}:
        score += 2.0
    exact_name = str(asset.get("name") or Path(asset["id"]).stem).lower()
    if exact_name and exact_name in query.lower():
        score += 5.0
    return score


def _rank(query: str, assets: list[dict], *, exclude: set[str] | None = None) -> list[tuple[float, dict]]:
    excluded = exclude or set()
    query_terms = _tokens(query) - GENERIC_TASK_TERMS
    docs = [(_tokens(str(a.get("name") or a["id"])) |
             _tokens(str(a.get("description") or ""))) for a in assets]
    n = len(docs)
    weights = {t: math.log(1 + (n + 1) / (1 + sum(t in d for d in docs)))
               for t in query_terms}
    rows = [(_score(query, a, weights), a) for a in assets if a["id"] not in excluded]
    return sorted((r for r in rows if r[0] > 0), key=lambda r: (-r[0], r[1]["id"], r[1]["source"]))


def _choose(rows: list[tuple[float, dict]], minimum: float = 2.0, margin: float = 1.0) -> tuple[dict | None, str | None]:
    if not rows or rows[0][0] < minimum:
        return None, "low_match"
    if len(rows) > 1 and rows[0][0] - rows[1][0] < margin:
        return None, "ambiguous_match"
    return rows[0][1], None


def live_assets(root: Path) -> tuple[list[dict], dict]:
    """Use the existing catalog; add OMP/Prime agent roots it does not index."""
    repo = Repo(root)
    assets = list(repo.load_index()["assets"])
    sources = Counter(a["source"] for a in assets if a["kind"] == "agent")
    unsupported: list[str] = []
    added = 0
    for runtime, source in (("omp", "omp-agents"), ("prime-agent", "prime-agents")):
        raw_root = repo.config().get("install_roots", {}).get("agent", {}).get(runtime)
        if not raw_root:
            continue
        folder = Path(raw_root).expanduser()
        if not folder.is_dir():
            continue
        for path in sorted(folder.iterdir()):
            if not path.is_file():
                continue
            if path.suffix not in {".md", ".toml", ".json"}:
                unsupported.append(str(path))
                continue
            assets.append({"id": path.name, "kind": "agent", "source": source,
                           "path": path.name, "abs_path": str(path), "name": path.stem,
                           "description": path.stem.replace("-", " ")})
            sources[source] += 1
            added += 1
    return assets, {"agents_indexed": sum(sources.values()), "by_source": dict(sorted(sources.items())),
                    "unindexed_added": added, "unsupported": unsupported}


def memory_os_loader(request: dict) -> dict:
    """Authenticated front door only. Never read Memory OS backend directly."""
    command = ["/Users/rig128gb/bin/rig-memory-os", "call", "memory.get_context_package",
               "--input", json.dumps(request, sort_keys=True)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=15, check=False)
    if result.returncode:
        raise RuntimeError(f"memory_os_exit_{result.returncode}")
    package = json.loads(result.stdout)
    if not isinstance(package, dict) or not package.get("package_hash"):
        raise ValueError("memory_os_missing_package_hash")
    return package


def _safe_jev_intent(intent: str, root: Path) -> str:
    redactor = root / "capabilities/hooks/redact_state.py"
    if not redactor.is_file():
        raise ValueError("jev_redactor_unavailable")
    result = subprocess.run([sys.executable, str(redactor)], input=intent,
                            capture_output=True, text=True, timeout=5, check=True)
    if not result.stdout.strip() or PRIVATE_INTENT.search(result.stdout):
        raise ValueError("jev_private_intent_deferred")
    return result.stdout


def _jev_subject(intent: str) -> str:
    return f"mission.route hosted-jev {JEV_ENDPOINT} intent-sha256:{_sha(intent.encode('utf-8'))}"


def hosted_jev_loader(intent: str, root: Path) -> dict:
    """Shadow-classify sanitized intent on hosted JEV without local inference or previews."""
    sanitized = _safe_jev_intent(intent, root)
    state_sha = _sha(sanitized.encode("utf-8"))
    env = os.environ.copy()
    env.update({"S1GATE_JEV_ENDPOINT": JEV_ENDPOINT, "S1GATE_JEV_MODEL": "jev-latest",
                "S1GATE_STATE_PREVIEW": "0", "S1GATE_CACHE": "0"})
    if env.get("TYPESAFE_API_KEY") == "local":
        env.pop("TYPESAFE_API_KEY")
    result = subprocess.run(
        [sys.executable, str(root / "bin/rig-s1gate"), "check", "mission.route", "--stdin", "--json",
         "--subject", _jev_subject(intent)],
        input=sanitized, capture_output=True, text=True, timeout=15, check=False, env=env, cwd=root)
    if result.returncode not in (0, 2):
        raise RuntimeError("jev_gate_exit_" + str(result.returncode))
    doc = json.loads(result.stdout)
    if doc.get("error") or doc.get("verdict") not in ("PASS", "ESCALATE"):
        raise RuntimeError("jev_gate_unavailable")
    answer = doc.get("answers", {}).get("lane", {})
    if not isinstance(answer, dict) or answer.get("choice") not in (*META_HINTS, "no_match"):
        raise ValueError("jev_choice_missing")
    confidence = answer.get("confidence")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        raise ValueError("jev_confidence_invalid")
    if (not isinstance(doc.get("decision_id"), int) or isinstance(doc["decision_id"], bool)
            or doc["decision_id"] <= 0 or not str(doc.get("model") or "").startswith("jev-")
            or doc.get("state_sha256") != state_sha):
        raise ValueError("jev_provenance_invalid")
    return {"status": "observed" if doc["verdict"] == "PASS" else "uncertain",
            "choice": answer["choice"], "confidence": confidence,
            "decision_id": doc.get("decision_id"), "model": doc.get("model"),
            "latency_ms": doc.get("latency_ms"), "advisory": True,
            "provider": "hosted-jev", "endpoint": JEV_ENDPOINT, "state_sha256": state_sha,
            "intent_sha256": _sha(intent.encode("utf-8")), "enforced": False}


def _jev(intent: str, root: Path, loader: Callable[[str, Path], dict] | None) -> dict:
    if loader is None:
        return {"status": "not_evaluated", "advisory": True, "enforced": False}
    try:
        result = loader(intent, root)
        if result.get("status") not in ("observed", "uncertain") or result.get("advisory") is not True:
            raise ValueError("jev_result_invalid")
        return result
    except (OSError, RuntimeError, ValueError, TimeoutError, subprocess.SubprocessError) as exc:
        return {"status": "degraded", "reason": type(exc).__name__,
                "advisory": True, "enforced": False}


def _memory(intent: str, loader: Callable[[dict], dict] | None) -> dict:
    if loader is None:
        return {"status": "unavailable", "package_hash": None, "references": [],
                "reference_only": True, "fallback_used": False, "reason": "offline_eval"}
    request = {"query": intent, "purpose": "coding-startup", "hierarchy": ["RIG"],
               "token_budget": 600, "sensitivity_ceiling": "internal"}
    try:
        package = loader(request)
        if not isinstance(package, dict) or not package.get("package_hash"):
            raise ValueError("missing_package_hash")
        if package.get("hierarchy") not in (None, ["RIG"]):
            raise ValueError("scope_mismatch")
        refs = [{"id": item.get("id"), "status": item.get("status"),
                 "content_ref": item.get("content_ref"), "sensitivity": item.get("sensitivity")}
                for item in package.get("retrieved_items", []) if isinstance(item, dict)]
        return {"status": "ok", "package_hash": package["package_hash"],
                "references": refs, "reference_only": True, "fallback_used": False}
    except (OSError, ValueError, RuntimeError, TimeoutError, subprocess.TimeoutExpired) as exc:
        return {"status": "degraded", "package_hash": None, "references": [],
                "reference_only": True, "fallback_used": False,
                "reason": type(exc).__name__}


def _prompt(intent: str, registry: dict, root: Path) -> dict:
    rows = []
    for p in registry.get("prompts", []):
        a = {"id": p.get("id", ""), "name": p.get("id", ""),
             "description": " ".join([p.get("task", ""), p.get("category", ""),
                                         " ".join(p.get("triggers", []))])}
        score = _score(intent, a)
        if any(t.lower() in intent.lower() for t in p.get("triggers", []) if t):
            score += 4.0
        if score:
            rows.append((score, p))
    rows.sort(key=lambda row: (-row[0], row[1].get("id", "")))
    if not rows or rows[0][0] < 3 or (len(rows) > 1 and rows[0][0] - rows[1][0] < 1):
        return {"id": None, "status": "missing", "reason": "no_unambiguous_stored_prompt"}
    p = rows[0][1]
    path = root / "capabilities" / "prompts" / p.get("path", "")
    if not path.is_file():
        path = root / p.get("path", "")  # test fixtures and explicit overlays
    if not path.is_file():
        return {"id": p.get("id"), "status": "missing", "reason": "prompt_file_missing"}
    return {"id": p["id"], "version": p.get("version"), "status": p.get("status", "draft"),
            "path": str(path.resolve()), "sha256": _sha(path.read_bytes()),
            "provenance": p.get("provenance") or p.get("source"), "score": rows[0][0]}


def _template(root: Path, name: str) -> dict:
    path = root / "capabilities" / "prompts" / "composition" / name
    if not path.is_file():
        return {"id": name, "status": "missing"}
    return {"id": name, "status": "draft", "path": str(path.resolve()),
            "sha256": _sha(path.read_bytes())}


def _binding(asset: dict, root: Path, role: str, read_only: bool) -> dict | None:
    ref = _ref(asset, root)
    if ref is None:
        return None
    return {"asset": ref, "role": role, "read_only": read_only,
            "quality_profile": "agent_outcome_evaluation_v0"}


def _fingerprint(assets: list[dict]) -> str:
    rows = [{"id": a.get("id"), "kind": a.get("kind"), "source": a.get("source"),
             "sha": a.get("sha")} for a in assets]
    rows.sort(key=lambda x: (str(x["kind"]), str(x["source"]), str(x["id"])))
    return _sha(_canonical({"assets": rows}))


def _jev_receipt_valid(jev: dict, intent: str, root: Path) -> bool:
    """Bind an observed answer to the local decision log, not packet prose."""
    try:
        state_sha = _sha(_safe_jev_intent(intent, root).encode("utf-8"))
        if (jev.get("provider") != "hosted-jev" or jev.get("endpoint") != JEV_ENDPOINT
                or jev.get("intent_sha256") != _sha(intent.encode("utf-8"))
                or jev.get("state_sha256") != state_sha
                or not str(jev.get("model") or "").startswith("jev-")):
            return False
        db = Path(DB_PATH).resolve()
        with sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=1) as connection:
            row = connection.execute(
                "SELECT rubric, state_sha256, verdict, advisory, answers_json, model, subject, error "
                "FROM decisions WHERE id=?", (jev["decision_id"],)).fetchone()
        if not row or row[0] != "mission.route" or row[1] != state_sha or \
                row[2] != "PASS" or row[3] != 1 or row[5] != jev.get("model") or \
                row[6] != _jev_subject(intent) or row[7] is not None:
            return False
        answer = json.loads(row[4]).get("lane", {})
        return answer.get("choice") == jev.get("choice") and \
            answer.get("confidence") == jev.get("confidence")
    except (OSError, sqlite3.Error, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        return False


def _child_skill(intent: str, meta_skill: dict | None, assets: list[dict], root: Path) -> dict | None:
    if meta_skill is None:
        return None
    name = meta_skill.get("id") or _path(meta_skill, root).parent.name
    table = root / "capabilities" / "skills" / name / "references" / "routing.md"
    if not table.is_file():
        return None
    allowed = set()
    for line in table.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) >= 4 and cells[1] and cells[1] not in ("Skill", "---"):
            allowed.add(cells[1])
    lower = intent.lower()
    if name == "when-shipping-code":
        if "python" in lower and "test" in lower:
            selected = "python-testing"
        elif any(word in lower for word in ("fix", "bug", "debug", "trace", "leak", "investigate")):
            selected = "debug-like-expert"
        else:
            selected = None
    else:
        selected = None
    available: dict[str, dict] = {}
    for asset in assets:
        skill_id = asset.get("id")
        if asset.get("kind") != "skill" or skill_id not in allowed:
            continue
        if skill_id not in available or asset.get("source") == "canonical":
            available[skill_id] = asset
    if selected in available:
        return available[selected]
    ranked = _rank(intent, list(available.values()))
    child, _reason = _choose(ranked, minimum=1.5)
    return child


def compose(intent: str, runtime: str, root: Path | str, assets: list[dict],
            prompt_registry: dict, memory_loader: Callable[[dict], dict] | None = memory_os_loader,
            inventory: dict | None = None,
            jev_loader: Callable[[str, Path], dict] | None = None) -> dict:
    """Compose a hash-bound, non-executable candidate packet; abstain on ties."""
    root = Path(root).resolve()
    blocks: list[str] = []
    runtime_source = RUNTIME_SOURCES.get(runtime)
    if runtime not in ROUTABLE_RUNTIMES:
        blocks.append("unsupported_runtime")
    agents = [a for a in assets if a.get("kind") == "agent" and a.get("source") == runtime_source]
    meta = next((a for a in agents if Path(a["id"]).stem == "rig-agent"), None)
    if meta is None:
        blocks.append("meta_agent_missing")
    primary_pool = [a for a in agents if a is not meta and not any(
        word in Path(a["id"]).stem.lower() for word in ("reviewer", "verifier", "orchestrator", "director"))]
    ranked = _rank(intent, primary_pool)
    primary, reason = _choose(ranked)
    if reason:
        blocks.append(f"agent_{reason}")
    reviewers = [a for a in agents if any(word in Path(a["id"]).stem.lower()
                                        for word in ("code-reviewer", "verifier"))]
    reviewer = next((a for a in reviewers if "code-reviewer" in a["id"]), None)
    if reviewer is None and reviewers:
        reviewer = reviewers[0]
    if reviewer is None:
        blocks.append("independent_verifier_missing")
    q = _tokens(intent)
    hinted = [(len(q & hints), name) for name, hints in META_HINTS.items()]
    hinted.sort(key=lambda row: (-row[0], row[1]))
    meta_skill_name = hinted[0][1] if hinted and hinted[0][0] > 0 and (
        len(hinted) == 1 or hinted[0][0] > hinted[1][0]) else None
    if meta_skill_name is None:
        # An unspecific task cannot justify a named agent from incidental word overlap.
        primary = None
        ranked = []
    skills = [a for a in assets if a.get("kind") == "skill"]
    meta_skill = next((a for a in skills if a.get("id") == meta_skill_name or
                       (Path(a.get("abs_path") or a["path"]).parent.name == meta_skill_name)), None)
    if meta_skill is None:
        blocks.append("meta_skill_unresolved")
    child_skill = _child_skill(intent, meta_skill, assets, root)
    if child_skill is None:
        blocks.append("child_skill_unresolved")
    task_prompt = _prompt(intent, prompt_registry, root)
    if task_prompt["status"] == "draft":
        blocks.append("draft_prompt")
    elif task_prompt["status"] == "missing":
        blocks.append("task_prompt_missing")
    memory = _memory(intent, memory_loader)
    if memory["status"] != "ok":
        blocks.append("memory_" + memory["status"])
    jev = _jev(intent, root, jev_loader)
    if jev["status"] != "observed":
        blocks.append("jev_" + jev["status"])
    elif jev["choice"] != meta_skill_name:
        blocks.append("jev_route_disagreement")
    agent_stack = {
        "meta": _binding(meta, root, "meta", True) if meta else None,
        "agent": _binding(primary, root, "agent", False) if primary else None,
        "subagents": [_binding(reviewer, root, "verifier", True)] if reviewer else [],
    }
    if any(x is None for x in [agent_stack["meta"], agent_stack["agent"]]):
        blocks.append("agent_asset_unresolved")
    if reviewer and agent_stack["subagents"][0] is None:
        blocks.append("verifier_asset_unresolved")
        agent_stack["subagents"] = []
    skill_refs = [ref for ref in [(_ref(a, root) if a else None)
                                  for a in (meta_skill, child_skill)] if ref]
    if meta_skill and not skill_refs:
        blocks.append("meta_skill_asset_unresolved")
    if child_skill and not any(ref["id"] == child_skill["id"] for ref in skill_refs):
        blocks.append("child_skill_asset_unresolved")
    catalog_fingerprint = _fingerprint(assets)
    route_ok = not any(b in blocks for b in ("unsupported_runtime", "meta_agent_missing",
                                             "agent_low_match", "agent_ambiguous_match",
                                             "agent_asset_unresolved", "meta_skill_unresolved",
                                             "meta_skill_asset_unresolved", "child_skill_unresolved",
                                             "child_skill_asset_unresolved"))
    packet = {"schema": SCHEMA, "intent": intent, "intent_sha256": _sha(intent.encode("utf-8")),
              "runtime": runtime, "status": "candidate" if route_ok else "abstain",
              "catalog_fingerprint": catalog_fingerprint,
              "agent_stack": agent_stack, "skills": skill_refs,
              "prompt_stack": {"meta": _template(root, "meta.md"), "task": task_prompt,
                               "subprompts": [_template(root, "verify.md")]},
              "memory": memory, "eval": {"suite": "mission-router-v1",
                                        "config": "capabilities/evals/mission-router/promptfooconfig.yaml",
                                        "grader_provider": None, "promotion_ready": False},
              "jev": jev,
              "execution": {"authorized": False, "one_writer": True,
                            "outward_actions_authorized": False},
              "inventory": inventory or {"agents_indexed": sum(a.get("kind") == "agent" for a in assets)},
              "candidates": [{"id": a["id"], "score": score} for score, a in ranked[:5]],
              "blocks": sorted(set(blocks))}
    packet["packet_sha256"] = _sha(_canonical(packet))
    return packet


def validate_packet(packet: dict, root: Path | str, assets: list[dict],
                    prompt_registry: dict | None = None) -> list[str]:
    """Validate structure and provenance against *trusted current* inputs.

    A packet hash detects accidental mutation only; it is never authority.
    The caller supplies the canonical repo and fresh catalog, not paths from
    the untrusted packet. Malformed input returns verdicts, never exceptions.
    """
    if not isinstance(packet, dict):
        return ["packet_not_object"]
    root = Path(root).resolve()
    errors: list[str] = []
    if packet.get("schema") != SCHEMA:
        errors.append("schema_invalid")
    if packet.get("status") not in ("candidate", "abstain"):
        errors.append("status_invalid")
    if packet.get("runtime") not in ROUTABLE_RUNTIMES:
        errors.append("runtime_not_routable")
    if not isinstance(packet.get("intent"), str) or not packet["intent"].strip():
        errors.append("intent_invalid")
    elif packet.get("intent_sha256") != _sha(packet["intent"].encode("utf-8")):
        errors.append("intent_hash_mismatch")
    copy = dict(packet)
    claimed = copy.pop("packet_sha256", None)
    try:
        if claimed != _sha(_canonical(copy)):
            errors.append("packet_hash_mismatch")
    except (TypeError, ValueError):
        errors.append("packet_not_json")
    if packet.get("catalog_fingerprint") != _fingerprint(assets):
        errors.append("catalog_drift")
    execution = packet.get("execution")
    if not isinstance(execution, dict) or execution.get("authorized") is not False or \
            execution.get("outward_actions_authorized") is not False or \
            execution.get("one_writer") is not True:
        errors.append("execution_boundary_invalid")
    stack = packet.get("agent_stack")
    if not isinstance(stack, dict) or not isinstance(stack.get("subagents"), list):
        errors.append("agent_stack_invalid")
        stack = {"meta": None, "agent": None, "subagents": []}
    bindings = [("meta", stack.get("meta")), ("agent", stack.get("agent"))]
    bindings.extend(("subagent", b) for b in stack["subagents"])
    trusted = {(a.get("id"), a.get("kind"), a.get("source")): _path(a, root).resolve()
               for a in assets if isinstance(a, dict) and a.get("id") and a.get("kind") and a.get("source")}
    refs: list[dict] = []
    agent_ids: list[str] = []
    writers = 0
    for role, binding in bindings:
        if binding is None:
            continue
        if not isinstance(binding, dict) or not isinstance(binding.get("asset"), dict):
            errors.append("agent_binding_invalid")
            continue
        ref = binding["asset"]
        refs.append(ref)
        agent_ids.append(str(ref.get("id")))
        if ref.get("kind") != "agent" or ref.get("source") != RUNTIME_SOURCES.get(packet.get("runtime")):
            errors.append("agent_runtime_or_kind_invalid")
        if role == "meta" and Path(str(ref.get("id", ""))).stem != "rig-agent":
            errors.append("meta_agent_invalid")
        if binding.get("read_only") is False:
            writers += 1
        if role == "meta" and (binding.get("read_only") is not True or binding.get("role") != "meta"):
            errors.append("meta_role_invalid")
        if role == "agent" and (binding.get("read_only") is not False or binding.get("role") != "agent"):
            errors.append("primary_role_invalid")
        if role == "subagent" and (binding.get("read_only") is not True or binding.get("role") != "verifier"):
            errors.append("subagent_role_invalid")
    if len(agent_ids) != len(set(agent_ids)):
        errors.append("duplicate_agent_role")
    if writers != (1 if stack.get("agent") is not None else 0):
        errors.append("writer_count_invalid")
    skills = packet.get("skills")
    if not isinstance(skills, list):
        errors.append("skills_invalid")
        skills = []
    if any(not isinstance(skill, dict) or skill.get("kind") != "skill" for skill in skills):
        errors.append("skill_kind_invalid")
    if skills:
        first = skills[0] if isinstance(skills[0], dict) else {}
        meta_name = str(first.get("id", ""))
        if meta_name == "SKILL.md":
            meta_name = Path(str(first.get("path", ""))).parent.name
        if not meta_name.startswith("when-"):
            errors.append("meta_skill_invalid")
    refs.extend(skills)
    for ref in refs:
        if not isinstance(ref, dict) or not all(isinstance(ref.get(k), str) and ref[k]
                                                for k in ("id", "kind", "source", "path", "sha256")):
            errors.append("asset_ref_invalid")
            continue
        key = (ref["id"], ref["kind"], ref["source"])
        expected = trusted.get(key)
        if expected is None or Path(ref["path"]).resolve() != expected:
            errors.append("asset_not_catalogued:" + ref["id"])
            continue
        if not expected.is_file() or _sha(expected.read_bytes()) != ref["sha256"]:
            errors.append("asset_drift:" + ref["id"])
    prompts = packet.get("prompt_stack")
    if not isinstance(prompts, dict) or not isinstance(prompts.get("subprompts"), list):
        errors.append("prompt_stack_invalid")
        prompts = {"meta": None, "task": None, "subprompts": []}
    task = prompts.get("task")
    blocks = packet.get("blocks")
    if not isinstance(blocks, list) or any(not isinstance(x, str) for x in blocks):
        errors.append("blocks_invalid")
        blocks = []
    if not isinstance(task, dict) or task.get("status") not in ("draft", "calibrated", "missing"):
        errors.append("task_prompt_invalid")
    elif task["status"] == "draft" and "draft_prompt" not in blocks:
        errors.append("draft_prompt_block_missing")
    elif task["status"] == "missing" and "task_prompt_missing" not in blocks:
        errors.append("missing_prompt_block_missing")
    memory = packet.get("memory")
    if not isinstance(memory, dict) or memory.get("fallback_used") is not False or \
            memory.get("reference_only") is not True or memory.get("status") not in ("ok", "degraded", "unavailable"):
        errors.append("memory_boundary_invalid")
    elif memory["status"] != "ok" and "memory_" + memory["status"] not in blocks:
        errors.append("memory_block_missing")
    jev = packet.get("jev")
    if not isinstance(jev, dict) or jev.get("status") not in (
            "observed", "uncertain", "degraded", "not_evaluated") or \
            jev.get("advisory") is not True or jev.get("enforced") is not False:
        errors.append("jev_boundary_invalid")
    elif jev["status"] != "observed" and "jev_" + jev["status"] not in blocks:
        errors.append("jev_block_missing")
    elif jev["status"] == "observed":
        if jev.get("choice") not in (*META_HINTS.keys(), "no_match") or \
                not isinstance(jev.get("confidence"), (int, float)) or \
                not 0 <= jev["confidence"] <= 1 or \
                not isinstance(jev.get("decision_id"), int) or \
                isinstance(jev.get("decision_id"), bool) or \
                jev.get("provider") != "hosted-jev" or jev.get("endpoint") != JEV_ENDPOINT:
            errors.append("jev_evidence_invalid")
        elif not _jev_receipt_valid(jev, packet["intent"] if isinstance(packet.get("intent"), str) else "", root):
            errors.append("jev_receipt_unverified")
        if isinstance(skills, list) and skills:
            selected = skills[0].get("id") if isinstance(skills[0], dict) else None
            if selected == "SKILL.md":
                selected = Path(str(skills[0].get("path", ""))).parent.name
            if (jev.get("choice") != selected) != ("jev_route_disagreement" in blocks):
                errors.append("jev_disagreement_block_invalid")
    if packet.get("status") == "candidate":
        if stack.get("meta") is None or stack.get("agent") is None or not skills:
            errors.append("candidate_incomplete")
        if any(b in blocks for b in ("unsupported_runtime", "agent_low_match", "agent_ambiguous_match",
                                     "meta_agent_missing", "meta_skill_unresolved", "agent_asset_unresolved")):
            errors.append("candidate_status_inconsistent")
    registry = prompt_registry or {"prompts": []}
    prompt_lookup = {p.get("id"): p for p in registry.get("prompts", []) if isinstance(p, dict)}
    expected_prompts = [
        (prompts.get("meta"), root / "capabilities/prompts/composition/meta.md"),
        *[(p, root / "capabilities/prompts/composition/verify.md") for p in prompts["subprompts"]],
    ]
    if isinstance(task, dict) and task.get("status") != "missing":
        entry = prompt_lookup.get(task.get("id"))
        if entry is None or task.get("status") != entry.get("status") or task.get("version") != entry.get("version"):
            errors.append("prompt_registry_mismatch")
        else:
            rel = entry.get("path", "")
            expected = root / "capabilities/prompts" / rel
            if not expected.is_file():
                expected = root / rel
            expected_prompts.append((task, expected))
    for layer, expected in expected_prompts:
        if not isinstance(layer, dict) or layer.get("status") == "missing":
            continue
        if not isinstance(layer.get("path"), str) or Path(layer["path"]).resolve() != expected.resolve():
            errors.append("prompt_path_invalid")
        elif not expected.is_file() or _sha(expected.read_bytes()) != layer.get("sha256"):
            errors.append("prompt_drift:" + str(layer.get("id")))
    # Packet SHA is not a signature. Recompute the deterministic route from
    # current trusted catalog/registry and compare every route-critical field.
    if isinstance(packet.get("intent"), str) and packet["intent"].strip() and \
            packet.get("runtime") in ROUTABLE_RUNTIMES:
        expected_route = compose(packet["intent"], packet["runtime"], root, assets,
                                 registry, memory_loader=None, jev_loader=None)
        for key in ("status", "agent_stack", "skills", "prompt_stack", "candidates"):
            if packet.get(key) != expected_route.get(key):
                errors.append("route_mismatch:" + key)
        expected_blocks = {b for b in expected_route["blocks"] if not b.startswith(("memory_", "jev_"))}
        actual_blocks = {b for b in blocks if not b.startswith(("memory_", "jev_"))}
        if expected_blocks != actual_blocks:
            errors.append("route_mismatch:blocks")
    return sorted(set(errors))
