"""The two verbs that make a score actionable.

``rank``    -- N candidates in, best-first out. Needs NO calibration: relative
               order is meaningful even when an absolute BLOCK threshold is not.
``improve`` -- one draft in, a better draft out. Score, hand the specific
               failing reasons to a System 2 rewriter, rescore, repeat until the
               gate clears or the budget runs out. Returns the best version seen
               and the full score trajectory, so the improvement is a receipt
               and not a claim.

Both consume the number. Neither merely reports it.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional

from .s1gate import BLOCK, ESCALATE, PASS, DecisionLog, GateResult, Rubric, evaluate, load_rubric

__all__ = ["rank", "improve", "ImproveResult", "claude_rewriter", "local_rewriter",
           "default_rewriter", "Rewriter"]

Rewriter = Callable[[str, str, List[str], Rubric], str]
_SEV = {PASS: 0, ESCALATE: 1, BLOCK: 2}


# --------------------------------------------------------------------------
# Scoring a result so candidates can be ordered
# --------------------------------------------------------------------------


def _badness(res: GateResult) -> tuple:
    """Lower is better. Verdict first, then how many rules tripped, then how
    hard the worst one tripped (distance past its threshold, when parseable)."""
    tripped = [r for r in res.reasons if r.startswith(("BLOCK:", "ESCALATE:"))]
    return (_SEV.get(res.verdict, 3), len(tripped))


def rank(
    rubric: Rubric | str,
    candidates: List[str],
    *,
    subject: Optional[str] = None,
    log: Optional[DecisionLog] = None,
) -> List[Dict[str, Any]]:
    """Score every candidate and return them best-first.

    Output rows: ``{"index", "verdict", "tripped", "reasons", "text"}``.
    """
    rb = load_rubric(rubric) if isinstance(rubric, str) else rubric
    rows = []
    for i, text in enumerate(candidates):
        res = evaluate(rb, text, subject="%s#%d" % (subject or "rank", i), log=log)
        rows.append({
            "index": i,
            "verdict": res.verdict,
            "tripped": _badness(res)[1],
            "reasons": [r for r in res.reasons if not r.startswith("downgraded")],
            "text": text,
            "_key": _badness(res),
        })
    rows.sort(key=lambda r: r["_key"])
    for r in rows:
        r.pop("_key", None)
    return rows


# --------------------------------------------------------------------------
# Rewriters
# --------------------------------------------------------------------------

_REWRITE_PROMPT = """You are revising a draft so it clears a quality gate. The gate scored the draft and these are the exact findings that failed:

{findings}

The gate's questions, so you know what it measures:
{questions}

Rules for the rewrite:
- Fix ONLY what the findings name. Do not change voice, length, structure, or claims that were not flagged.
- Never invent a source, number, or credential to satisfy a finding. If a claim cannot be sourced, remove or soften it.
- Preserve every fact, name, and figure that was not flagged, exactly as written.
- Output the revised draft only. No preamble, no explanation, no quotes around it.

Context about this draft: {context}

DRAFT:
{draft}"""


def claude_rewriter(draft: str, context: str, findings: List[str], rb: Rubric) -> str:
    """Rewrite via the local ``claude`` CLI in non-interactive mode."""
    bin_ = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
    if not os.path.exists(bin_):
        raise RuntimeError("claude CLI not found; supply a different rewriter")
    qs = "\n".join("- %s: %s" % (k, v.get("instructions", "")) for k, v in rb.questions.items())
    prompt = _REWRITE_PROMPT.format(
        findings="\n".join("- " + f for f in findings) or "- (none)",
        questions=qs, context=context or rb.description, draft=draft,
    )
    # Host runtimes (Aside, meta-harness) export PYTHONHOME/PYTHONPATH that break
    # any child python the CLI spawns. Hand it a clean interpreter environment.
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTHON", "VIRTUAL_ENV"))}
    out = subprocess.run(
        [bin_, "-p", prompt, "--output-format", "text"],
        capture_output=True, text=True, timeout=180, env=env,
    )
    text = (out.stdout or "").strip()
    if out.returncode != 0 or not text:
        raise RuntimeError("rewriter failed rc=%s: %s" % (out.returncode, (out.stderr or "")[:200]))
    return text


# Local-first ladder. Each entry is (base_url, model). Loopback tunnels are
# preferred over LAN IPs because the LAN labels drift. Override with
# S1GATE_REWRITER_LADDER="url|model,url|model".
_DEFAULT_LADDER = [
    ("http://127.0.0.1:8771", "qwen3.8-27b-oq6:instruct"),
    ("http://192.168.68.90:8011", "blackwell-qwen38-flash"),
]


def _ladder() -> List[tuple]:
    raw = os.environ.get("S1GATE_REWRITER_LADDER", "").strip()
    if not raw:
        return list(_DEFAULT_LADDER)
    out = []
    for item in raw.split(","):
        if "|" in item:
            u, m = item.split("|", 1)
            out.append((u.strip().rstrip("/"), m.strip()))
    return out or list(_DEFAULT_LADDER)


def local_rewriter(draft: str, context: str, findings: List[str], rb: Rubric) -> str:
    """Rewrite via any OpenAI-compatible local endpoint, walking the ladder."""
    import urllib.error
    import urllib.request

    qs = "\n".join("- %s: %s" % (k, v.get("instructions", "")) for k, v in rb.questions.items())
    prompt = _REWRITE_PROMPT.format(
        findings="\n".join("- " + f for f in findings) or "- (none)",
        questions=qs, context=context or rb.description, draft=draft,
    )
    body = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
        "max_tokens": max(600, len(draft) // 2),
        "stream": False,
    }
    errors = []
    for base, model in _ladder():
        body["model"] = model
        req = urllib.request.Request(
            base + "/v1/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            text = (data["choices"][0]["message"]["content"] or "").strip()
            # Strip a thinking block or code fence if the model emitted one.
            if "</think>" in text:
                text = text.split("</think>", 1)[1].strip()
            if text.startswith("```"):
                text = text.strip("`").split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            if text:
                return text
            errors.append("%s returned empty" % model)
        except (urllib.error.URLError, OSError, KeyError, ValueError, TimeoutError) as exc:
            errors.append("%s@%s: %s" % (model, base, str(exc)[:80]))
    raise RuntimeError("every rung of the local ladder failed: " + "; ".join(errors))


def default_rewriter(draft: str, context: str, findings: List[str], rb: Rubric) -> str:
    """Local first; the claude CLI only if every local rung is down."""
    try:
        return local_rewriter(draft, context, findings, rb)
    except RuntimeError as local_exc:
        try:
            return claude_rewriter(draft, context, findings, rb)
        except RuntimeError as cli_exc:
            raise RuntimeError("%s | claude fallback: %s" % (local_exc, cli_exc))


# --------------------------------------------------------------------------
# The loop
# --------------------------------------------------------------------------


@dataclass
class ImproveResult:
    rubric: str
    original: str
    best: str
    best_verdict: str
    iterations: int
    cleared: bool
    trajectory: List[Dict[str, Any]] = field(default_factory=list)
    stopped_because: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def summary(self) -> str:
        path = " -> ".join("%s(%d)" % (t["verdict"], t["tripped"]) for t in self.trajectory)
        head = "[s1gate improve:%s] %s after %d iteration(s): %s" % (
            self.rubric, "CLEARED" if self.cleared else "NOT CLEARED", self.iterations, path)
        return head + ("\n  stopped: " + self.stopped_because if self.stopped_because else "")


def improve(
    rubric: Rubric | str,
    draft: str,
    *,
    context: str = "",
    rewriter: Rewriter = default_rewriter,
    max_iterations: int = 3,
    accept: str = PASS,
    subject: Optional[str] = None,
    log: Optional[DecisionLog] = None,
) -> ImproveResult:
    """Score -> rewrite against the findings -> rescore, until ``accept`` or budget.

    ``accept`` is the verdict that counts as done: ``PASS`` (default) or
    ``ESCALATE`` when a human will read it anyway and you only want BLOCK-class
    defects removed. Never returns a version worse than the best seen.
    """
    rb = load_rubric(rubric) if isinstance(rubric, str) else rubric
    target = _SEV[accept]

    current = draft
    res = evaluate(rb, current, subject="%s#0" % (subject or "improve"), log=log)
    best_text, best_res = current, res
    traj = [{"iteration": 0, "verdict": res.verdict, "tripped": _badness(res)[1], "reasons": res.reasons}]
    stopped = ""
    n = 0

    while _SEV[res.verdict] > target and n < max_iterations:
        n += 1
        findings = [r for r in res.reasons if r.startswith(("BLOCK:", "ESCALATE:"))]
        try:
            candidate = rewriter(current, context, findings, rb)
        except Exception as exc:  # noqa: BLE001
            stopped = "rewriter failed on iteration %d: %s" % (n, exc)
            break
        if candidate.strip() == current.strip():
            stopped = "rewriter returned an unchanged draft on iteration %d" % n
            break
        res = evaluate(rb, candidate, subject="%s#%d" % (subject or "improve", n), log=log)
        traj.append({"iteration": n, "verdict": res.verdict, "tripped": _badness(res)[1], "reasons": res.reasons})
        if _badness(res) < _badness(best_res):
            best_text, best_res = candidate, res
        current = candidate

    cleared = _SEV[best_res.verdict] <= target
    if not stopped and not cleared:
        stopped = "budget of %d iterations exhausted" % max_iterations
    if rb.never_auto:
        stopped = (stopped + "; " if stopped else "") + "rubric is never_auto: a human still decides"

    return ImproveResult(
        rubric=rb.name, original=draft, best=best_text, best_verdict=best_res.verdict,
        iterations=n, cleared=cleared, trajectory=traj, stopped_because=stopped,
    )
