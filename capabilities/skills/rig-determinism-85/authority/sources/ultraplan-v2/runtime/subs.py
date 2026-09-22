"""W11 sub-level: the 24 shared primitives, by reference.

Every normal operation consumes these; none is duplicated into a studio. Where
a primitive already exists elsewhere in the runtime it is RE-EXPORTED here with
its source named -- the registry is the map, the source is the implementation.
The primitives that did not exist are implemented here, small and tested."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# -- re-exports (single implementation, referenced by name) -----------------
from runtime.ledger import Ledger as _Ledger          # schema validator lives in schemas/v1 + jsonschema
from runtime.approvals import consume as approval_consume, ApprovalError
from runtime.ledger import BudgetExceeded

def artifact_hash(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def receipt_verifier(receipt: dict) -> tuple[bool, str]:
    """A receipt is verified when its evidence hash matches the artifact bytes."""
    ev = receipt.get("evidence") or {}
    p, want = ev.get("path"), ev.get("sha256")
    if not p or not want:
        return False, "receipt names no artifact hash"
    if not Path(p).exists():
        return False, "artifact missing: %s" % p
    got = artifact_hash(p)
    return (got == want), ("hash match" if got == want else "hash mismatch %s != %s" % (got[:12], want[:12]))

def budget_checker(mission_id: str, ledger: _Ledger) -> dict:
    bud, owner = ledger._effective_budget(mission_id)
    if not bud:
        return {"ok": True, "why": "no budget declared"}
    spent = ledger._spent(owner)
    over = {k: spent[k] for k in spent if bud.get(k) is not None and spent[k] > float(bud[k])}
    return {"ok": not over, "over": over, "spent": spent, "budget": bud}

def writer_fence_validator(ledger: _Ledger, key: str, token: str) -> bool:
    try:
        ledger.check_fence(key, token)
        return True
    except Exception:
        return False

def sse_cursor_validator(last_event_id: str, earliest_available: int) -> dict:
    try:
        cur = int(last_event_id)
    except (TypeError, ValueError):
        return {"ok": False, "action": "full-replay"}
    if cur < earliest_available - 1:
        return {"ok": False, "action": "gap", "lost_before": earliest_available}
    return {"ok": True, "cursor": cur}

def route_resolver(root: str, call: str) -> str | None:
    """Resolve a route call to a directory under root, or None."""
    if call.startswith("studio:"):
        p = Path(root) / "studios" / call[len("studio:"):]
    else:
        p = (Path(root) / call).resolve()
        if not str(p).startswith(str(Path(root).resolve())):
            return None
    return str(p) if p.is_dir() else None

def plant_failure_runner(cell_path: str, slot: str = "routes.yaml") -> dict:
    from rig_capabilities.ultra_cell import plant_failure  # by reference
    return plant_failure(Path(cell_path), slot=slot)

# -- primitives that had no home --------------------------------------------
def normalize_dedup(items: list[str]) -> list[str]:
    seen, out = set(), []
    for it in items:
        k = " ".join(str(it).lower().split())
        if k not in seen:
            seen.add(k)
            out.append(it)
    return out


def wave_plan(deps: dict) -> list[list[str]]:
    """Topological waves: each wave is a set of cells that can run in parallel
    (disjoint, no intra-wave edges). A cycle is NAMED, not silently dropped."""
    import collections
    unknown = {d for lst in deps.values() for d in lst if d not in deps}
    if unknown:
        raise ValueError("dependency on unknown cell(s): %s" % sorted(unknown))
    indeg = {n: len(set(v)) for n, v in deps.items()}
    rev = collections.defaultdict(list)
    for n, ds in deps.items():
        for d in set(ds):
            rev[d].append(n)
    waves, placed = [], set()
    remaining = dict(indeg)
    while remaining:
        wave = sorted(n for n, k in remaining.items() if k == 0)
        if not wave:
            raise ValueError("cycle among: %s" % sorted(remaining))
        waves.append(wave)
        for n in wave:
            remaining.pop(n)
            for m in rev.get(n, []):
                if m in remaining:
                    remaining[m] -= 1
    return waves


def angle_generation(topic: str, classes: int = 14) -> list[str]:
    """Deterministic angle prompts: one per class, stable order."""
    return ["%s -- what does '%s' look like here?" % (c, topic) for c in ANGLE_CLASSES[:classes]]


def freshness_plan(recheck_days=(7, 30, 90), now=None):
    """Forecast/skill freshness: due dates for T+N re-checks. Positive offsets
    only, sorted, deduped -- a schedule that can never come due is refused."""
    import time as _t
    base = _t.time() if now is None else float(now)
    offs = [int(x) for x in recheck_days if int(x) > 0]   # non-positive offsets are noise, dropped
    if not offs:
        raise ValueError("freshness schedule needs at least one positive T+N offset")
    return sorted({base + o * 86400 for o in offs})


def informed_check(counts: dict, floor: float) -> dict:
    """Is the information sufficient to proceed? Every class must meet the floor
    ratio; names every shortfall (never a bare bool -- an action list, not a verdict)."""
    bad = []
    for k, v in sorted((counts or {}).items()):
        try:
            f = float(v)
        except (TypeError, ValueError):
            bad.append(k + " (not a number)")
            continue
        if f < floor:
            bad.append("%s (%.3f < %.3f)" % (k, f, floor))
    return {"sufficient": not bad, "shortfalls": bad}


ANGLE_CLASSES = ["customer/job", "buyer/money", "competitor/landscape", "technical feasibility",
             "distribution/channel", "timing/why-now", "legal/compliance", "people/capacity",
             "second-order effects", "failure modes", "exit/kill", "measurement",
             "dependencies/assumptions", "ethics/reputation"]


def lens_pack() -> list[str]:
    """The canonical lens pack: exactly the 14 angle classes, always."""
    return list(ANGLE_CLASSES)


def lens_instances(topic: str) -> list[dict]:
    """One instance per lens; count is structurally bounded by the pack."""
    return [{"lens": c, "prompt": "%s -- what does '%s' look like here?" % (c, topic)}
            for c in ANGLE_CLASSES]



def harvest_evidence(directory: str) -> dict:
    """W10 harvest: index JEX/audit/receipt JSON evidence on disk into a ledger-ready
    summary. Read-only; counts only what exists; a missing dir is zero, never an error
    the caller must guess around."""
    from pathlib import Path as _P
    p = _P(directory)
    files = sorted(p.glob("*.json")) if p.is_dir() else []
    parsed, broken = [], []
    for f in files:
        try:
            parsed.append((f.name, json.loads(f.read_text())))
        except Exception:
            broken.append(f.name)
    passed = [n for n, d in parsed if isinstance(d, dict) and (d.get("pass") or d.get("cleared"))]
    return {"files": len(files), "parsed": len(parsed), "broken": broken,
            "passed": len(passed), "source_dir": str(p)}


def scraper_instances(sources: list[dict]) -> list[dict]:
    """One instance per declared source, structurally capped at len(sources):
    never fans out per-query, per-page, or per-retry. Each instance inherits
    the source's politeness (min_interval_s) and MUST state what it stops on."""
    out = []
    for s in sources:
        if not isinstance(s, dict) or not s.get("url"):
            raise ValueError("scraper source needs at least a url")
        out.append({"url": s["url"], "kind": s.get("kind", "page"),
                    "min_interval_s": max(1.0, float(s.get("min_interval_s", 2.0))),
                    "stop_on": ["robots_disallow", "http_429", "http_403", "budget_exhausted"]})
    return out


def register_firstmate(name: str, capabilities: list[str], workspace: str, registry: dict) -> dict:
    """Registration is append-only and duplicate-owner-refusing, mirroring the
    lane contract: one firstmate name owns one workspace."""
    if not name or not capabilities or not workspace:
        raise ValueError("registration needs name, >=1 capability, workspace")
    if name in registry:
        raise ValueError("firstmate %s already registered (one owner per name)" % name)
    registry[name] = {"capabilities": sorted(capabilities), "workspace": workspace,
                      "registered_ts": time.time()}
    return registry[name]


def liveness_check(url_or_path: str, timeout: float = 4.0) -> dict:
    import urllib.request, urllib.error
    if url_or_path.startswith("http"):
        try:
            code = urllib.request.urlopen(url_or_path, timeout=timeout).status
            return {"live": 200 <= code < 400, "code": code}
        except urllib.error.HTTPError as e:
            return {"live": False, "code": e.code}
        except Exception as e:
            return {"live": False, "error": str(e)[:120]}
    return {"live": Path(url_or_path).exists()}

MODEL_FAMILY_LADDER = ["local/blackwell", "local/kimi", "openrouter/gemini", "openrouter/qwen"]

def model_family_ladder(model: str) -> int:
    """Index in the ladder; -1 when unknown (callers refuse, never guess)."""
    for i, fam in enumerate(MODEL_FAMILY_LADDER):
        if model.startswith(fam.split("/", 1)[1].split("-")[0]) or fam in model:
            return i
    return -1

def order_swap_check(seq: list) -> bool:
    """A monotonically increasing sequence with no swapped pair."""
    return all(a < b for a, b in zip(seq, seq[1:]))

def memory_append(path: str, record: dict) -> int:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps({"ts": time.time(), **record}, sort_keys=True)
    with open(p, "a") as fh:
        fh.write(line + "\n")
    with open(p) as fh:
        return sum(1 for _ in fh)

def variant_proposal(live: str, candidate: str, why: str) -> dict:
    """Staged, never applied: adoption is a separate calibrated decision."""
    return {"live_sha256": hashlib.sha256(live.encode()).hexdigest(),
            "candidate_sha256": hashlib.sha256(candidate.encode()).hexdigest(),
            "why": why, "state": "staged", "adopted": False}

def envelope_builder(kind: str, **fields) -> dict:
    base = {"schema_version": "1", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    env = {**base, **fields}
    from jsonschema import Draft7Validator
    schema = json.loads((Path(__file__).resolve().parent.parent /
                         "schemas" / "v1" / ("%s.v1.json" % kind)).read_text())
    errs = sorted(Draft7Validator(schema).iter_errors(env), key=lambda e: list(e.path))
    if errs:
        raise ValueError("envelope invalid: %s" % "; ".join(e.message[:120] for e in errs[:3]))
    return env


def _build_registry():
    skip = {"annotations"}
    out = {}
    for name, obj in list(globals().items()):
        if name.startswith("_") or name in skip:
            continue
        if callable(obj) or isinstance(obj, list):
            out[name] = obj
    return out


SUBS = _build_registry()


def persona_panel(topic: str) -> str:
    """Render the lens panel as markdown: one '- [lens:X]' line per structural
    angle-class instance. Empty topic refused -- a panel with no subject is theater."""
    if not topic or not topic.strip():
        raise ValueError("persona panel needs a topic")
    lines = ["## Panel"]
    for inst in lens_instances(topic.strip()):
        lines.append("- [lens:%s] %s" % (inst["lens"], inst["prompt"]))
    return "\n".join(lines) + "\n"


_BLOCKING = ("must", "block", "cannot", "without", "before we")
_ASSUMED = ("assume", "typically", "default", "presum")


def bank_quality(questions) -> str:
    """Tag each question [BLOCKING] / [ASSUMED] / [INFORMATIONAL] by rule and render
    a '## Questions' section. Deterministic: the tag comes from the text, not a model.
    Empty bank refused -- an empty question bank proves nothing."""
    qs = [q.strip() for q in questions if q and q.strip()]
    if not qs:
        raise ValueError("question bank is empty")
    lines = ["## Questions"]
    for q in qs:
        low = q.lower()
        if any(k in low for k in _BLOCKING):
            tag = "BLOCKING"
        elif any(k in low for k in _ASSUMED):
            tag = "ASSUMED"
        else:
            tag = "INFORMATIONAL"
        lines.append("- [%s] %s" % (tag, q))
    return "\n".join(lines) + "\n"
