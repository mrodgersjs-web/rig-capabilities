"""RIG Deviator™ v3 — strict criteria-based auditor.

Replaces v2's loose heuristic scorers with deterministic boolean criteria
packs per engine. Each pack has 5-10 yes/no questions, each detectable via
regex, count threshold, predicate function, or LLM-as-judge (3-vote majority).

Audit pipeline:
  text + criteria pack → per-question {pass: bool, evidence: str|None}
                       → audit score = sum(weight × pass)
                       → ratio = score / max_score
                       → σ from calibration ladder

Output per engine:
  {
    slug, codename, layer, axis,
    score: int, max: int, ratio: float,
    sigma: float, sigma_label: str, status: str,
    questions: [{id, question, mode, pass, weight, evidence, why}],
    failed_required: [question_ids],
  }
"""
from __future__ import annotations
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib import request as ur

from rig_lattice._paths import CALIBRATION_FILE as _CALIBRATION_YAML
from rig_lattice._paths import CRITERIA_DIR as _CRITERIA_DIR

try:
    import yaml
except ImportError:
    yaml = None  # optional: the runtime reads compiled JSON, not YAML

BASE = _CRITERIA_DIR.parent
CRITERIA_DIR = _CRITERIA_DIR
CALIBRATION_FILE = _CALIBRATION_YAML

# Host-neutral LLM endpoint. Only the llm_judge detection mode reaches it; the
# deterministic A1 audit path never does. RIG_DV_LLM_URL is the deprecated
# alias and is read first so existing environments keep working.
LLM_URL = (
    os.environ.get("RIG_DV_LLM_URL")
    or os.environ.get("RIG_LATTICE_LLM_URL")
    or "http://127.0.0.1:11434/v1/chat/completions"
)
LLM_MODEL = os.environ.get("RIG_LATTICE_LLM_MODEL", "llama3.3:70b")

_STALE_JSON_WARNED = False


# ── Criteria / calibration loader (JSON first — stdlib only) ────────────────
def _load_criteria(stem: str) -> dict:
    """Load a criteria pack (or the calibration ladder) by file stem.

    Prefers ``<stem>.json``, which ``scripts/compile_criteria.py`` generates
    from the YAML source of truth. This is what makes the 40-engine audit
    path stdlib-only.

    Two distinct failures, two distinct exceptions:

    ``FileNotFoundError``  no pack of that name exists in either format
    ``RuntimeError``       the pack exists as YAML but the JSON compile is
                           missing and PyYAML is not installed to read it
    """
    global _STALE_JSON_WARNED
    base = CRITERIA_DIR if stem != "calibration" else CALIBRATION_FILE.parent
    as_json = base / f"{stem}.json"
    if as_json.exists():
        return json.loads(as_json.read_text())

    as_yaml = base / f"{stem}.yaml"
    if not as_yaml.exists():
        raise FileNotFoundError(
            f"criteria pack not found: {as_json} (no .json and no .yaml)"
        )

    if yaml is None:
        raise RuntimeError(
            f"criteria/{stem}.json missing — run scripts/compile_criteria.py"
        )
    if not _STALE_JSON_WARNED:
        _STALE_JSON_WARNED = True
        print(
            f"warning: {stem}.json missing; falling back to PyYAML. "
            "Run scripts/compile_criteria.py to refresh the compile.",
            file=sys.stderr,
        )
    return yaml.safe_load(as_yaml.read_text())


def _load_yaml(path: Path) -> dict:
    """Back-compat shim: load by path, preferring the compiled JSON twin."""
    path = Path(path)
    as_json = path.with_suffix(".json")
    if as_json.exists():
        return json.loads(as_json.read_text())
    if yaml is not None:
        return yaml.safe_load(path.read_text())
    raise RuntimeError(
        f"{as_json.name} missing — run scripts/compile_criteria.py"
    )


# ── Calibration ─────────────────────────────────────────────────────────────
@dataclass
class Calibration:
    direction: str  # right | left | gate
    ladder: list[dict] = field(default_factory=list)
    hard_block_sigma: float = -30.0
    pass_sigma: float = 10.0
    per_optional_bonus: float = 2.0
    max_sigma: float = 25.0

    @classmethod
    def from_dict(cls, d: dict, default: "Calibration | None" = None) -> "Calibration":
        if default is None:
            return cls(
                direction=d.get("direction", "right"),
                ladder=d.get("ladder", []),
                hard_block_sigma=d.get("hard_block_sigma", -30.0),
                pass_sigma=d.get("pass_sigma", 10.0),
                per_optional_bonus=d.get("per_optional_bonus", 2.0),
                max_sigma=d.get("max_sigma", 25.0),
            )
        return cls(
            direction=d.get("direction", default.direction),
            ladder=d.get("ladder", default.ladder),
            hard_block_sigma=d.get("hard_block_sigma", default.hard_block_sigma),
            pass_sigma=d.get("pass_sigma", default.pass_sigma),
            per_optional_bonus=d.get("per_optional_bonus", default.per_optional_bonus),
            max_sigma=d.get("max_sigma", default.max_sigma),
        )


def _sigma_for_ratio(ratio: float, ladder: list[dict]) -> tuple[float, str]:
    """Walk the ladder from highest min downward, return first row that matches."""
    for row in sorted(ladder, key=lambda r: -r["min"]):
        if ratio >= row["min"]:
            return float(row["sigma"]), str(row.get("label", ""))
    return -20.0, "below floor"


# ── Detection modes ─────────────────────────────────────────────────────────
def _detect_regex(text: str, pattern: str, min_count: int = 1,
                   max_count: int | None = None, flags: str = "i") -> tuple[bool, str | None]:
    """Return (passed, first_match_quote). passed if min_count <= count <= max_count."""
    re_flags = 0
    if "i" in flags: re_flags |= re.IGNORECASE
    if "m" in flags: re_flags |= re.MULTILINE
    if "s" in flags: re_flags |= re.DOTALL
    matches = list(re.finditer(pattern, text, re_flags))
    count = len(matches)
    passed = count >= min_count and (max_count is None or count <= max_count)
    evidence = None
    if matches:
        m = matches[0]
        snippet = text[max(0, m.start()-40):m.end()+40].replace("\n", " ").strip()
        evidence = f"...{snippet}..." if snippet else m.group(0)
    return passed, evidence


def _detect_count(text: str, pattern: str, min_count: int = 1,
                   max_count: int | None = None, flags: str = "i") -> tuple[bool, str | None]:
    """Same as regex but used when caller cares about count semantics."""
    return _detect_regex(text, pattern, min_count, max_count, flags)


def _detect_absent(text: str, patterns: list[str], flags: str = "i") -> tuple[bool, str | None]:
    """Pass iff NONE of the patterns appear. Evidence is the FOUND violator."""
    re_flags = re.IGNORECASE if "i" in flags else 0
    for p in patterns:
        m = re.search(p, text, re_flags)
        if m:
            snippet = text[max(0, m.start()-40):m.end()+40].replace("\n", " ").strip()
            return False, f"found banned pattern '{m.group(0)}': ...{snippet}..."
    return True, None


def _detect_proximity(text: str, anchor_pattern: str, target_pattern: str,
                       window_chars: int = 800, flags: str = "i") -> tuple[bool, str | None]:
    """Pass if EVERY occurrence of anchor has target within window_chars."""
    re_flags = re.IGNORECASE if "i" in flags else 0
    anchors = list(re.finditer(anchor_pattern, text, re_flags))
    if not anchors:
        return False, "no anchor matches found"
    for a in anchors:
        local = text[a.start():a.start() + window_chars]
        if not re.search(target_pattern, local, re_flags):
            snippet = text[max(0, a.start()-40):a.end()+40].replace("\n", " ").strip()
            return False, f"anchor without nearby target: ...{snippet}..."
    return True, f"all {len(anchors)} anchors have target within {window_chars} chars"


# ── LLM judge ──────────────────────────────────────────────────────────────
def _llm_judge_once(text: str, question: str, timeout: int = 60) -> tuple[bool | None, str]:
    """One vote. Returns (yes/no/None, reason)."""
    prompt = (
        f"You are auditing a strategic document against a strict doctrine criterion.\n\n"
        f"DOCUMENT (truncated to first 4000 chars):\n---\n{text[:4000]}\n---\n\n"
        f"CRITERION (yes/no question):\n{question}\n\n"
        f"Answer in this exact format on TWO LINES:\n"
        f"VERDICT: YES   (or NO)\n"
        f"WHY: <one sentence pointing to specific text>\n\n"
        f"Be strict. If the criterion is partially met, answer NO. Only YES if fully and unambiguously met."
    )
    payload = {"model": LLM_MODEL, "messages": [{"role": "user", "content": prompt}],
               "temperature": 0.0, "max_tokens": 120}
    try:
        req = ur.Request(LLM_URL, data=json.dumps(payload).encode("utf-8"),
                         headers={"Content-Type": "application/json"}, method="POST")
        with ur.urlopen(req, timeout=timeout) as r:
            body = json.loads(r.read().decode("utf-8"))
        out = body["choices"][0]["message"]
        content = (out.get("content") or out.get("reasoning") or "").strip()
        m = re.search(r"VERDICT:\s*(YES|NO)", content, re.IGNORECASE)
        if not m:
            return None, f"unparseable: {content[:120]}"
        verdict = m.group(1).upper() == "YES"
        why_m = re.search(r"WHY:\s*(.+)", content, re.IGNORECASE | re.DOTALL)
        why = why_m.group(1).strip()[:200] if why_m else content[:200]
        return verdict, why
    except Exception as ex:
        return None, f"LLM error: {ex}"


def _llm_judge_majority(text: str, question: str, votes: int = 3) -> tuple[bool, str]:
    """N-vote majority. Returns (pass, reason_string)."""
    results = []
    with ThreadPoolExecutor(max_workers=votes) as ex:
        futs = [ex.submit(_llm_judge_once, text, question) for _ in range(votes)]
        for f in as_completed(futs):
            results.append(f.result())
    valid = [(v, w) for v, w in results if v is not None]
    if not valid:
        return False, "no valid LLM votes"
    yes_count = sum(1 for v, _ in valid if v)
    no_count = len(valid) - yes_count
    passed = yes_count > no_count
    reasons = " | ".join(w for _, w in valid[:2])
    return passed, f"{yes_count}/{len(valid)} YES · {reasons}"


# ── Question runner ─────────────────────────────────────────────────────────
def _run_question(text: str, q: dict, llm_enabled: bool = True) -> dict:
    """Execute one criterion question and return its result row."""
    mode = q.get("mode", "regex")
    qid = q["id"]
    question = q["question"]
    weight = float(q.get("weight", 1.0))
    required = bool(q.get("required", False))

    if mode == "regex":
        passed, ev = _detect_regex(
            text, q["pattern"],
            min_count=q.get("min_count", 1),
            max_count=q.get("max_count"),
            flags=q.get("flags", "i"),
        )
    elif mode == "absent":
        passed, ev = _detect_absent(text, q["patterns"], flags=q.get("flags", "i"))
    elif mode == "proximity":
        passed, ev = _detect_proximity(
            text, q["anchor"], q["target"],
            window_chars=q.get("window_chars", 800),
            flags=q.get("flags", "i"),
        )
    elif mode == "count_min":
        # Pass if number of pattern matches >= threshold
        matches = re.findall(q["pattern"], text, re.IGNORECASE)
        n = len(matches)
        threshold = int(q.get("threshold", 1))
        passed = n >= threshold
        ev = f"{n} matches (need ≥{threshold})"
    elif mode == "ratio_min":
        # Pass if (matches / total_words / 1000) >= threshold
        matches = re.findall(q["pattern"], text, re.IGNORECASE)
        words = max(len(text.split()), 1)
        density = len(matches) / words * 1000
        threshold = float(q.get("threshold", 1.0))
        passed = density >= threshold
        ev = f"density {density:.1f}/kw (need ≥{threshold})"
    elif mode == "llm_judge":
        if not llm_enabled:
            return {"id": qid, "question": question, "mode": mode, "weight": weight,
                    "required": required, "pass": False, "evidence": "LLM disabled",
                    "skipped": True}
        passed, ev = _llm_judge_majority(text, question, votes=q.get("votes", 3))
    else:
        return {"id": qid, "question": question, "mode": mode, "weight": weight,
                "required": required, "pass": False, "evidence": f"unknown mode {mode}",
                "skipped": True}

    return {"id": qid, "question": question, "mode": mode, "weight": weight,
            "required": required, "pass": bool(passed), "evidence": ev,
            "skipped": False}


# ── Engine audit ────────────────────────────────────────────────────────────
def audit_engine(text: str, criteria_path: Path,
                  default_cal: Calibration,
                  llm_enabled: bool = True) -> dict:
    """Run one engine's criteria pack against text. Returns audit dict."""
    pack = _load_yaml(criteria_path)
    cal = Calibration.from_dict(pack.get("calibration", {}), default_cal)

    questions = pack["questions"]
    results = [_run_question(text, q, llm_enabled) for q in questions]

    # Compute weighted score
    total_weight = sum(float(q.get("weight", 1.0)) for q in questions)
    earned = sum(r["weight"] for r in results if r["pass"])
    ratio = earned / total_weight if total_weight else 0.0

    # Gate logic
    failed_required = [r["id"] for r in results
                       if r.get("required") and not r["pass"] and not r.get("skipped")]

    if cal.direction == "gate":
        if failed_required:
            sigma = cal.hard_block_sigma
            label = f"HARD_BLOCK ({len(failed_required)} required failed)"
            status = "HARD_BLOCK"
        else:
            optional_passes = sum(1 for r in results
                                   if not r.get("required") and r["pass"])
            sigma = min(cal.pass_sigma + cal.per_optional_bonus * optional_passes,
                        cal.max_sigma)
            label = f"PASS (+{optional_passes} optional)"
            status = "PASS"
    else:
        sigma, label = _sigma_for_ratio(ratio, cal.ladder)
        if cal.direction == "left":
            sigma = -sigma
        # status thresholds
        if failed_required:
            status = "HARD_BLOCK"
            sigma = min(sigma, cal.hard_block_sigma)
        elif sigma <= -10:
            status = "HARD_BLOCK"
        elif sigma <= -3:
            status = "BLOCK"
        else:
            status = "PASS"

    return {
        "slug": pack["slug"],
        "codename": pack["codename"],
        "layer": pack["layer"],
        "axis": pack.get("axis", ""),
        "score": round(earned, 2),
        "max": round(total_weight, 2),
        "ratio": round(ratio, 3),
        "sigma": round(sigma, 2),
        "sigma_label": label,
        "status": status,
        "questions": results,
        "failed_required": failed_required,
    }


# ── Bulk auditor ────────────────────────────────────────────────────────────
def audit_all(text: str, llm_enabled: bool = True,
              engines: list[str] | None = None) -> dict:
    """Run audit across all criteria packs in CRITERIA_DIR (or filtered list)."""
    default_cal_full = _load_yaml(CALIBRATION_FILE)
    default_cal = Calibration.from_dict(default_cal_full.get("default", {}))
    # Gate-specific default override available too
    gate_cal = Calibration.from_dict(default_cal_full.get("gate", {}), default_cal)

    packs = sorted(CRITERIA_DIR.glob("*.yaml"))
    results: dict[str, dict] = {}
    for p in packs:
        slug = p.stem
        if engines and slug not in engines:
            continue
        # Peek at layer to pick gate vs default cal
        meta = _load_yaml(p)
        layer = meta.get("layer", "cognitive")
        cal = gate_cal if layer == "physics" else default_cal
        results[slug] = audit_engine(text, p, cal, llm_enabled=llm_enabled)

    # Composite RIG-L: top-6 |σ| pulls × (1 − risk penalty)
    non_gate = [r for r in results.values() if r["layer"] != "physics"]
    sorted_pulls = sorted(non_gate, key=lambda r: -abs(r["sigma"]))[:6]
    pulls = [r["sigma"] for r in sorted_pulls]
    hard_blocks = sum(1 for r in results.values() if r["status"] == "HARD_BLOCK")
    risk = min(0.9, hard_blocks * 0.3)
    rig_l = round(sum(pulls) / max(len(pulls), 1) * (1 - risk), 2) if pulls else 0.0
    bdf = round(sum(r["sigma"] for r in results.values()) / max(len(results), 1), 2)

    weakest = min(results.values(), key=lambda r: r["sigma"]) if results else None
    strongest = max(results.values(), key=lambda r: r["sigma"]) if results else None

    return {
        "rig_l": rig_l,
        "bdf": bdf,
        "hard_blocks": hard_blocks,
        "status": ("HARD_BLOCK" if hard_blocks > 0
                   else "PASS" if rig_l >= 5
                   else "BLOCK" if rig_l < 0 else "MARGINAL"),
        "weakest": {"codename": weakest["codename"], "sigma": weakest["sigma"]} if weakest else None,
        "strongest": {"codename": strongest["codename"], "sigma": strongest["sigma"]} if strongest else None,
        "engines": results,
    }


if __name__ == "__main__":
    import sys
    text_path = Path(sys.argv[1])
    llm = "--no-llm" not in sys.argv
    out = audit_all(text_path.read_text(), llm_enabled=llm)
    print(f"RIG-L: {out['rig_l']:+.2f}  BDF: {out['bdf']:+.2f}  "
          f"status: {out['status']}  hard_blocks: {out['hard_blocks']}")
    print(f"strongest: {out['strongest']['codename']} {out['strongest']['sigma']:+.2f}σ")
    print(f"weakest: {out['weakest']['codename']} {out['weakest']['sigma']:+.2f}σ")
    print()
    print(f"{'codename':12} {'slug':32} {'σ':>7}  {'ratio':>6}  {'status':12}")
    print("-" * 76)
    for slug, r in sorted(out['engines'].items(), key=lambda x: -x[1]['sigma']):
        print(f"{r['codename']:12} {slug:32} {r['sigma']:+7.2f}  "
              f"{r['ratio']:>5.2f}  {r['status']:12}")
