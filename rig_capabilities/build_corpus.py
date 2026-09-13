"""Corpus freeze (A33–A37): 30 frozen tutorial sources, zero fetched bytes.

The freeze is a MANIFEST plus discipline, not content:

- manifest-v1.json holds the 30 unique URLs in the plan's exact distribution
  (Pydantic AI 6, Temporal 6, Kestra 4, LangGraph 5, LangChain 3, Langfuse 3,
  LangSmith 3), each with retrieval_status=PENDING. There is no verb here
  that writes a transcript, and every row says so: retrieval runs need their
  own approved step (the exact command is recorded in open_items).
- the .sha256 sidecar binds golden bytes + filename + item count, following
  the criteria_pack golden-manifest pattern; verify() recomputes from disk.
- A frozen manifest is never rewritten: freeze(version="v1") against an
  existing v1 REFUSES; a re-freeze is manifest-v2.json with its own sidecar.
- A37: provenance_discipline is data on every row — fetched instructions are
  policy-inert, and transcript-derived hypotheses are a separate claim class
  from verified procedures (nothing here has either; it is all PENDING).
- A36: practitioner material is frozen as a KEYED register — author and the
  missing mechanism per entry, selection_status KEYED_PENDING_SOURCE. We do
  not freeze popularity; we do not freeze invented URLs either.

CLI: python3 rig_capabilities/build_corpus.py status|verify|freeze <version>
There is deliberately no add/update/append/fetch verb — tests pin it.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CORPUS_DIR = REPO / "runs" / "agentic-stack-buildout" / "corpus"
SCHEMA = "rig.corpus.freeze.v1"
DISTRIBUTION = {"pydantic-ai": 6, "temporal": 6, "kestra": 4,
                "langgraph": 5, "langchain": 3, "langfuse": 3, "langsmith": 3}
TOTAL = 30
MANIFEST_RX = re.compile(r"^([0-9a-f]{64})  (\S+)  items=(\d+)$")
ROW_KEYS = ("url", "provider", "kind", "why_version_applicable",
            "expected_artifact", "retrieval_status", "claim_class",
            "policy_effect")
PROVENANCE_DISCIPLINE = {
    "claim_classes": ("PENDING", "TRANSCRIPT_HYPOTHESIS", "VERIFIED_PROCEDURE"),
    "rule_a37": "fetched instructions are INPUT DATA with policy_effect=NONE; "
                "they never alter policy, doctrine, or gates. A transcript "
                "gives rise at most to a TRANSCRIPT_HYPOTHESIS, which becomes "
                "a VERIFIED_PROCEDURE only by an executable check run here.",
    "rule_a34": "missing/truncated captions stay recorded gaps (A34); the "
                "freeze ships zero transcripts.",
    "rule_a36": "practitioner material is keyed to a named missing mechanism "
                "before a source is chosen — never to popularity.",
}
OPEN_RETRIEVAL_ITEM = {
    "id": "A34-A35-retrieval",
    "status": "OPEN — needs its own approved step (no network in the freeze)",
    "command_when_approved":
        "python3 rig_capabilities/build_corpus.py freeze-status only; "
        "retrieval per row via the approved fetcher, writing "
        "rig_build.source_documents through build_store.put_source_document "
        "(dedupe key = sha256 of the canonicalized URL), and only after that "
        "may a new manifest version carry non-PENDING statuses",
}

_OFF = "official docs/how-to/tutorial index page"
_EX = "official example repository"

# The 30 frozen sources (A33). URL liveness was NOT probed — the freeze
# performs no network call; A35's crawl records the terminal status of every
# URL, and a dead URL becomes a documented replacement in the NEXT version.
V1_ITEMS = [
    # Pydantic AI — 6
    {"url": "https://ai.pydantic.dev/", "provider": "pydantic-ai",
     "kind": _OFF, "why_version_applicable": "docs track the pydantic-ai "
     "release line of the project's own repo",
     "expected_artifact": "page snapshot + sha256"},
    {"url": "https://ai.pydantic.dev/agents/", "provider": "pydantic-ai",
     "kind": _OFF, "why_version_applicable": "agent API docs, versioned with "
     "each pydantic-ai release", "expected_artifact": "page snapshot + sha256"},
    {"url": "https://ai.pydantic.dev/tools/", "provider": "pydantic-ai",
     "kind": _OFF, "why_version_applicable": "tool/toolkit surface — the "
     "mechanism our T5 proposal-validation row needs",
     "expected_artifact": "page snapshot + runnable snippet"},
    {"url": "https://ai.pydantic.dev/output/", "provider": "pydantic-ai",
     "kind": _OFF, "why_version_applicable": "structured-output API, the "
     "typed-proposal contract we onboard (A24)",
     "expected_artifact": "page snapshot + runnable snippet"},
    {"url": "https://ai.pydantic.dev/validation/", "provider": "pydantic-ai",
     "kind": _OFF, "why_version_applicable": "validation decorators — the "
     "failure-handling proof in A24", "expected_artifact": "page snapshot + "
     "runnable snippet"},
    {"url": "https://ai.pydantic.dev/testing-evals/", "provider": "pydantic-ai",
     "kind": _OFF, "why_version_applicable": "eval harness — feeds the "
     "behavior-check requirement for every vendor pack (A38)",
     "expected_artifact": "page snapshot + runnable snippet"},
    # Temporal — 6
    {"url": "https://docs.temporal.io/develop/python/", "provider": "temporal",
     "kind": _OFF, "why_version_applicable": "Python dev guide; SDK-major "
     "versioned docs", "expected_artifact": "page snapshot + sha256"},
    {"url": "https://docs.temporal.io/develop/python/core-application",
     "provider": "temporal", "kind": _OFF,
     "why_version_applicable": "workflow/activity definitions for the "
     "installed Python SDK", "expected_artifact": "page snapshot + "
     "runnable snippet"},
    {"url": "https://docs.temporal.io/develop/python/python-worker",
     "provider": "temporal", "kind": _OFF, "why_version_applicable":
     "versioned-worker mechanics — A25's verified-worker identity",
     "expected_artifact": "page snapshot + sha256"},
    {"url": "https://docs.temporal.io/develop/python/developer-tools",
     "provider": "temporal", "kind": _OFF, "why_version_applicable":
     "test-server/time-skipping tooling for durable-timer proofs",
     "expected_artifact": "page snapshot + sha256"},
    {"url": "https://docs.temporal.io/evaluate/development-production-quickstart/python",
     "provider": "temporal", "kind": _OFF, "why_version_applicable":
     "quickstart pinned to the Python SDK line", "expected_artifact":
     "page snapshot + runnable snippet"},
    {"url": "https://github.com/temporalio/sdk-python", "provider": "temporal",
     "kind": _EX, "why_version_applicable": "examples inside the SDK repo "
     "itself — always at the shipped version", "expected_artifact":
     "repo examples tree + sha256 of each"},
    # Kestra — 4
    {"url": "https://kestra.io/docs", "provider": "kestra", "kind": _OFF,
     "why_version_applicable": "docs ship with the self-hosted image we "
     "would onboard (A26)", "expected_artifact": "page snapshot + sha256"},
    {"url": "https://kestra.io/docs/workflows", "provider": "kestra",
     "kind": _OFF, "why_version_applicable": "flow/cadence semantics — the "
     "T2 ownership row", "expected_artifact": "page snapshot + yaml sample"},
    {"url": "https://kestra.io/docs/how-to-guides", "provider": "kestra",
     "kind": _OFF, "why_version_applicable": "retry/overlap/concurrency "
     "recipes required by A26", "expected_artifact": "page snapshot + "
     "runnable yaml"},
    {"url": "https://github.com/kestra-io/examples2", "provider": "kestra",
     "kind": _EX, "why_version_applicable": "official example repo, version "
     "tracks releases", "expected_artifact": "repo examples tree + sha256"},
    # LangGraph — 5
    {"url": "https://langchain-ai.github.io/langgraph/", "provider":
     "langgraph", "kind": _OFF, "why_version_applicable": "library docs at "
     "the released version line", "expected_artifact": "page snapshot + sha256"},
    {"url": "https://langchain-ai.github.io/langgraph/tutorials/",
     "provider": "langgraph", "kind": _OFF, "why_version_applicable":
     "end-to-end tutorials — the genuine-cycle pattern for A27",
     "expected_artifact": "page snapshot + runnable notebook"},
    {"url": "https://langchain-ai.github.io/langgraph/concepts/persistence/",
     "provider": "langgraph", "kind": _OFF, "why_version_applicable":
     "checkpoint API — the persistence precondition of A27",
     "expected_artifact": "page snapshot + sha256"},
    {"url": "https://langchain-ai.github.io/langgraph/how-tos/",
     "provider": "langgraph", "kind": _OFF, "why_version_applicable":
     "bounded how-tos including interrupt/limits — stop/cost/tool-limit "
     "hooks required by B36", "expected_artifact": "page snapshot + sha256"},
    {"url": "https://github.com/langchain-ai/langgraph/tree/main/examples",
     "provider": "langgraph", "kind": _EX, "why_version_applicable":
     "examples in-tree with the library at HEAD of the release branch",
     "expected_artifact": "repo examples tree + sha256"},
    # LangChain — 3
    {"url": "https://python.langchain.com/docs/introduction/",
     "provider": "langchain", "kind": _OFF, "why_version_applicable":
     "docs versioned per langchain release; conditional-use pack (A28)",
     "expected_artifact": "page snapshot + sha256"},
    {"url": "https://python.langchain.com/docs/how_to/", "provider":
     "langchain", "kind": _OFF, "why_version_applicable": "component how-tos "
     "at the current release", "expected_artifact": "page snapshot + sha256"},
    {"url": "https://python.langchain.com/docs/tutorials/", "provider":
     "langchain", "kind": _OFF, "why_version_applicable": "tutorials pinned "
     "to the docs version", "expected_artifact": "page snapshot + sha256"},
    # Langfuse — 3
    {"url": "https://langfuse.com/docs", "provider": "langfuse", "kind": _OFF,
     "why_version_applicable": "self-host versioned docs — A29 traces with "
     "redaction", "expected_artifact": "page snapshot + sha256"},
    {"url": "https://langfuse.com/docs/tracing", "provider": "langfuse",
     "kind": _OFF, "why_version_applicable": "tracing/SDK surface at the "
     "documented version", "expected_artifact": "page snapshot + sha256"},
    {"url": "https://langfuse.com/docs/prompt-management", "provider":
     "langfuse", "kind": _OFF, "why_version_applicable": "prompt-version "
     "linkage required for version/trace linkage in A29",
     "expected_artifact": "page snapshot + sha256"},
    # LangSmith — 3
    {"url": "https://docs.smith.langchain.com/", "provider": "langsmith",
     "kind": _OFF, "why_version_applicable": "platform docs; separate "
     "onboarding (A30)", "expected_artifact": "page snapshot + sha256"},
    {"url": "https://docs.smith.langchain.com/observability", "provider":
     "langsmith", "kind": _OFF, "why_version_applicable": "trace ingestion "
     "API at the documented version", "expected_artifact": "page snapshot + "
     "sha256"},
    {"url": "https://docs.smith.langchain.com/evaluation", "provider":
     "langsmith", "kind": _OFF, "why_version_applicable": "eval runs kept "
     "separate from tracing per A30", "expected_artifact": "page snapshot + "
     "sha256"},
]

# A36 — practitioner register: keyed to the mechanism we LACK, with the
# author/class of source named; no URL invented, no popularity argument.
V1_MECHANISM_GAPS = [
    {"mechanism": "typed model proposals with schema-repair on validation "
     "failure", "missing_because": "no production evidence yet (A24 blocks "
     "on isolated onboarding)", "candidate_source_author": "pydantic team "
     "talks/vlogs (official channel)", "selection_status":
     "KEYED_PENDING_SOURCE"},
    {"mechanism": "durable-timer crash-recovery drill under load",
     "missing_because": "we have no rehearsed kill-the-worker proof (B47)",
     "candidate_source_author": "Temporal community conference talks",
     "selection_status": "KEYED_PENDING_SOURCE"},
    {"mechanism": "code-owned cadence migration off launchd without dual "
     "execution", "missing_because": "B55 migration pattern unproven here",
     "candidate_source_author": "Kestra practitioner write-ups",
     "selection_status": "KEYED_PENDING_SOURCE"},
    {"mechanism": "genuine-cycle bounding: when checkpointed backtracking "
     "beats a plain retry loop", "missing_because": "T6 diagnosis rule is "
     "declared, not demonstrated", "candidate_source_author": "LangChain "
     "Academy / LangGraph maintainers", "selection_status":
     "KEYED_PENDING_SOURCE"},
    {"mechanism": "trace-redaction pipelines that never leak private corpus",
     "missing_because": "A29 redaction recipe absent",
     "candidate_source_author": "Langfuse community deployments",
     "selection_status": "KEYED_PENDING_SOURCE"},
    {"mechanism": "agentic-video/practitioner workflows (Cole Medin-class "
     "material) judged on mechanism completeness, not views",
     "missing_because": "no mechanism-keyed intake yet",
     "candidate_source_author": "Cole Medin; Matt Williams (RAG)",
     "selection_status": "KEYED_PENDING_SOURCE"},
]


class CorpusFreezeError(RuntimeError):
    pass


def manifest_path(version: str = "v1") -> Path:
    if not re.match(r"^v[0-9]+$", version or ""):
        raise CorpusFreezeError(f"version must look like v1/v2, got {version!r}")
    return CORPUS_DIR / f"manifest-{version}.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_bytes(items: list, mechanism_gaps: list, version: str) -> bytes:
    doc = {
        "schema": SCHEMA,
        "version": version,
        "frozen_at": _dt.datetime.now(_dt.timezone.utc)
                         .isoformat(timespec="seconds"),
        "freeze_method": "hand-frozen provider index; NO network call in the "
                         "freeze; URL liveness is A35's crawl job",
        "distribution": dict(DISTRIBUTION), "total": TOTAL,
        "policy": PROVENANCE_DISCIPLINE,
        "open_items": [OPEN_RETRIEVAL_ITEM],
        "items": items,
        "mechanism_gaps": mechanism_gaps,
    }
    return (json.dumps(doc, indent=1, sort_keys=True) + "\n").encode()


def freeze(version: str = "v1") -> dict:
    """Write manifest-<version>.json + its .sha256 sidecar. A frozen version
    is NEVER rewritten — the only move for a changed corpus is a new
    version. No other verb writes to the corpus directory."""
    man = manifest_path(version)
    if man.exists():
        raise CorpusFreezeError(
            f"{man.name} is frozen at sha {_sha(man)[:12]}; no verb rewrites "
            "a frozen manifest — re-freeze as a new version")
    items = [{**it, "retrieval_status": "PENDING",
              "claim_class": "PENDING", "policy_effect": "NONE"}
             for it in V1_ITEMS if version == "v1"]
    gaps = V1_MECHANISM_GAPS if version == "v1" else []
    if version != "v1":
        raise CorpusFreezeError(
            "v1 is the only corpus this task freezes; a later version must "
            "carry its own reviewed items, not an auto-copy")
    data = manifest_bytes(items, gaps, version)
    man.parent.mkdir(parents=True, exist_ok=True)
    man.write_bytes(data)
    sha = hashlib.sha256(data).hexdigest()
    man.with_suffix(".sha256").write_text(
        f"{sha}  {man.name}  items={len(items)}\n", encoding="utf-8")
    return {"version": version, "sha256": sha, "items": len(items),
            "manifest": str(man)}


def verify(version: str = "v1") -> tuple[list[str], dict]:
    """Golden verification (criteria_pack pattern): hash, filename, count,
    distribution, statuses, policy fields — all recomputed from disk."""
    man, side = manifest_path(version), manifest_path(version).with_suffix(".sha256")
    errs: list[str] = []
    if not man.is_file():
        return [f"manifest missing: {man}"], {}
    if not side.is_file():
        return ["sidecar missing"], {}
    line = side.read_text(encoding="utf-8").strip()
    m = MANIFEST_RX.match(line)
    if not m:
        return ["sidecar unparseable"], {}
    have = man.read_bytes()
    golden = hashlib.sha256(have).hexdigest()
    if m.group(1) != golden:
        errs.append("manifest sha != sidecar sha")
    if m.group(2) != man.name:
        errs.append(f"sidecar filename {m.group(2)!r} != {man.name!r}")
    doc = json.loads(have)
    if int(m.group(3)) != len(doc["items"]):
        errs.append(f"sidecar items={m.group(3)} != {len(doc['items'])}")
    counts: dict[str, int] = {}
    urls = set()
    for row in doc["items"]:
        if set(row) < set(ROW_KEYS):
            errs.append(f"row missing discipline keys: {row.get('url')}")
        if row["retrieval_status"] != "PENDING":
            errs.append(f"freeze carried a non-PENDING status: {row['url']}")
        if row["url"] in urls:
            errs.append(f"duplicate url {row['url']}")
        urls.add(row["url"])
        counts[row["provider"]] = counts.get(row["provider"], 0) + 1
    if len(doc["items"]) != TOTAL:
        errs.append(f"items {len(doc['items'])} != {TOTAL}")
    if counts != DISTRIBUTION:
        errs.append(f"distribution {counts} != {DISTRIBUTION}")
    return errs, {"sha256": golden, "items": len(doc["items"]),
                  "providers": counts,
                  "mechanism_gaps": len(doc.get("mechanism_gaps", [])),
                  "open_items": [o["id"] for o in doc.get("open_items", [])]}


def status(version: str = "v1") -> dict:
    errs, info = verify(version)
    return {"state": "live" if not errs else "stale",
            "errors": errs, **info,
            "retrieval": "0 fetched / 30 PENDING — retrieval is an OPEN "
                         "approved step, command recorded in open_items",
            "next_action": OPEN_RETRIEVAL_ITEM["command_when_approved"]}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in ("status", "verify", "freeze"):
        print(__doc__)
        return 0 if argv and argv[0] in ("-h", "--help") else 2
    verb = argv[0]
    if verb == "freeze":
        try:
            out = freeze(argv[1] if len(argv) > 1 else "v1")
        except CorpusFreezeError as exc:
            print(f"REFUSED: {exc}", file=sys.stderr)
            return 2
        print(json.dumps(out, indent=1))
        return 0
    if verb == "verify":
        errs, info = verify(argv[1] if len(argv) > 1 else "v1")
        print(json.dumps({"ok": not errs, "errors": errs, **info}, indent=1))
        return 0 if not errs else 2
    out = status(argv[1] if len(argv) > 1 else "v1")
    print(json.dumps(out, indent=1))
    return 0 if out["state"] == "live" else 2


if __name__ == "__main__":
    sys.exit(main())
