"""RIG System-1 Gate (s1gate).

A governed decision layer built on TypeSafe's System One model (Jev).

Doctrine
--------
Jev returns *calibrated probabilities over a fixed answer set*. It generates no
text. That makes it the missing rung between "deterministic" and "agentic": the
judgment is probabilistic, but it is consumed by an ``if`` statement that lives
in our code, not in a model's prose.

Hard rules encoded here (see capabilities/skills/s1gate/SKILL.md):

1. **Fail closed.** A provider error, a timeout, or an unparseable answer is a
   BLOCK, never a PASS. Silence is not consent.
2. **Confidence is a second axis.** A Score mean is meaningless when the
   distribution is bimodal. Every Score/Choice rule is also subject to a
   confidence floor; below the floor the verdict is ESCALATE, not PASS.
3. **No uncalibrated enforcement.** A rubric whose policy has not been measured
   against labelled ground truth runs in ADVISORY mode only. It may annotate;
   it may not block. ``s1gate_calibrate`` is what flips ``calibrated`` to true.
4. **Every decision is logged.** The decision log is both the ProofPacket and
   the training set that lets System 2 retune System 1 later.
5. **The gate never grades its own homework.** The artifact author does not
   receive the thresholds or the calibration set.

Stdlib only, per rig-capabilities packaging policy.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

__all__ = [
    "Verdict",
    "GateResult",
    "S1GateError",
    "ProviderError",
    "Rubric",
    "load_rubric",
    "list_rubrics",
    "evaluate",
    "ask",
    "DecisionLog",
]

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
RUBRIC_DIR = Path(
    os.environ.get("S1GATE_RUBRIC_DIR", REPO_ROOT / "capabilities" / "harnesses" / "s1gate" / "rubrics")
)
STATE_DIR = Path(os.environ.get("S1GATE_STATE_DIR", Path.home() / ".rig" / "s1gate"))
DB_PATH = Path(os.environ.get("S1GATE_DB", STATE_DIR / "decisions.db"))

JEV_ENDPOINT = os.environ.get("S1GATE_JEV_ENDPOINT", "https://api.typesafe.ai/v1/systemone")
JEV_MODEL = os.environ.get("S1GATE_JEV_MODEL", "jev-latest")
KEYCHAIN_ITEM = os.environ.get("S1GATE_KEYCHAIN_ITEM", "com.rig.env.TYPESAFE_API_KEY")

# Verdicts, most severe first. Precedence is resolved by this ordering.
BLOCK = "BLOCK"
ESCALATE = "ESCALATE"
PASS = "PASS"
_SEVERITY = {BLOCK: 3, ESCALATE: 2, PASS: 1}


class S1GateError(RuntimeError):
    """Base error."""


class ProviderError(S1GateError):
    """The System One provider could not be reached or returned garbage."""


# --------------------------------------------------------------------------
# Credentials -- value never returned to a caller, never logged.
# --------------------------------------------------------------------------


def _api_key() -> str:
    key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if key:
        return key
    try:
        out = subprocess.run(
            ["security", "find-generic-password", "-s", KEYCHAIN_ITEM, "-w"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:  # pragma: no cover
        raise ProviderError("keychain lookup failed: %s" % type(exc).__name__) from exc
    key = (out.stdout or "").strip()
    if not key:
        raise ProviderError(
            "no System One API key: set TYPESAFE_API_KEY or store keychain item %s" % KEYCHAIN_ITEM
        )
    return key


# --------------------------------------------------------------------------
# Provider call
# --------------------------------------------------------------------------


def ask(
    state: str,
    questions: Dict[str, Any],
    *,
    model: Optional[str] = None,
    timeout: float = 20.0,
    retries: int = 2,
) -> Dict[str, Any]:
    """POST one System One request. Returns the parsed response body.

    Raises ProviderError on any failure. Callers must treat that as BLOCK.
    """
    if not isinstance(state, str) or not state.strip():
        raise S1GateError("state must be a non-empty string")
    if not questions:
        raise S1GateError("at least one question is required")

    payload = json.dumps(
        {"state": state, "model": model or JEV_MODEL, "questions": questions}
    ).encode("utf-8")
    key = _api_key()

    last: Optional[Exception] = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(
            JEV_ENDPOINT,
            data=payload,
            method="POST",
            headers={
                "Authorization": "Bearer %s" % key,
                "Content-Type": "application/json",
                "User-Agent": "rig-s1gate/1.0",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            if "answers" not in body:
                raise ProviderError("response missing 'answers'")
            return body
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode("utf-8")[:300]
            except Exception:  # pragma: no cover
                pass
            last = ProviderError("HTTP %s: %s" % (exc.code, detail))
            # 4xx other than 429 will not fix themselves.
            if exc.code != 429 and 400 <= exc.code < 500:
                break
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
            last = ProviderError("%s: %s" % (type(exc).__name__, exc))
        if attempt < retries:
            time.sleep(0.4 * (2 ** attempt))
    raise last if last else ProviderError("unknown provider failure")


# --------------------------------------------------------------------------
# Answer access -- a tiny, safe path language. No eval().
# --------------------------------------------------------------------------

# Supported left-hand sides:
#   <q>.noul          probability the statement is true       (Noul)
#   <q>.score         the score mean                          (Score)
#   <q>.confidence    distribution concentration, 0..1        (Score/Choice)
#   <q>.choice        the selected option, string             (Choice)
#   <q>.p.<option>    probability of one option/level         (Choice/Score)
_OPS = {
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
}
_RULE_RE = re.compile(
    r"^\s*([A-Za-z_][\w]*)\.(noul|score|confidence|choice|p\.[\w\-]+)\s*"
    r"(>=|<=|==|!=|>|<)\s*(.+?)\s*$"
)


def resolve(answers: Dict[str, Any], qname: str, attr: str) -> Any:
    """Read one field out of a System One answer block. None if absent."""
    ans = answers.get(qname)
    if not isinstance(ans, dict):
        return None
    if attr.startswith("p."):
        return (ans.get("probabilities") or {}).get(attr[2:])
    if attr == "confidence":
        # Noul answers carry no confidence; absence must not read as 0.0.
        return ans.get("confidence")
    return ans.get(attr)


def eval_condition(answers: Dict[str, Any], expr: str) -> Tuple[Optional[bool], str]:
    """Evaluate one ``field op value`` condition.

    Returns ``(result, note)``. ``result`` is None when the field is missing or
    the comparison is not applicable -- an undecidable condition never passes.
    """
    m = _RULE_RE.match(expr or "")
    if not m:
        return None, "unparseable condition: %r" % expr
    qname, attr, op, raw = m.groups()
    left = resolve(answers, qname, attr)
    if left is None:
        return None, "missing field %s.%s" % (qname, attr)
    raw = raw.strip()
    if attr == "choice":
        right: Any = raw.strip("\"'")
        if op not in ("==", "!="):
            return None, "choice supports only == and !="
    else:
        try:
            right = float(raw)
        except ValueError:
            return None, "non-numeric threshold %r" % raw
        try:
            left = float(left)
        except (TypeError, ValueError):
            return None, "non-numeric answer for %s.%s" % (qname, attr)
    return _OPS[op](left, right), "%s.%s=%s %s %s" % (qname, attr, left, op, right)


# --------------------------------------------------------------------------
# Rubrics
# --------------------------------------------------------------------------


@dataclass
class Rubric:
    name: str
    stage: str
    lane: str
    description: str
    questions: Dict[str, Any]
    rules: List[Dict[str, Any]]
    confidence_floor: float = 0.35
    calibrated: bool = False
    calibration: Dict[str, Any] = field(default_factory=dict)
    # Free-text provenance per question: why a wording or threshold was changed.
    notes: Dict[str, Any] = field(default_factory=dict)
    # Lane C and other human-owned surfaces can never be auto-actioned.
    never_auto: bool = False
    path: Optional[str] = None

    @property
    def enforcing(self) -> bool:
        """Only a calibrated rubric may BLOCK. Others annotate."""
        return bool(self.calibrated)


def load_rubric(name: str, rubric_dir: Optional[Path] = None) -> Rubric:
    d = Path(rubric_dir or RUBRIC_DIR)
    p = d / ("%s.json" % name)
    if not p.exists():
        raise S1GateError("no rubric %r in %s" % (name, d))
    raw = json.loads(p.read_text(encoding="utf-8"))
    known = {f for f in Rubric.__dataclass_fields__ if f != "path"}
    unknown = set(raw) - known
    if unknown:
        raise S1GateError("rubric %s has unknown keys: %s" % (name, sorted(unknown)))
    return Rubric(path=str(p), **raw)


def list_rubrics(rubric_dir: Optional[Path] = None) -> List[str]:
    d = Path(rubric_dir or RUBRIC_DIR)
    if not d.exists():
        return []
    return sorted(p.stem for p in d.glob("*.json"))


# --------------------------------------------------------------------------
# Result
# --------------------------------------------------------------------------


@dataclass
class GateResult:
    rubric: str
    verdict: str
    enforced: bool
    reasons: List[str]
    answers: Dict[str, Any]
    model: str
    latency_ms: int
    advisory: bool = False
    state_sha256: str = ""
    error: Optional[str] = None
    decision_id: Optional[int] = None

    @property
    def ok(self) -> bool:
        """True only when the gate positively cleared the artifact."""
        return self.verdict == PASS

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def summary(self) -> str:
        tag = self.verdict + (" (advisory)" if self.advisory else "")
        head = "[s1gate:%s] %s" % (self.rubric, tag)
        if not self.reasons:
            return head
        return head + "\n" + "\n".join("  - " + r for r in self.reasons)


# --------------------------------------------------------------------------
# Decision log
# --------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS decisions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    ts           REAL NOT NULL,
    rubric       TEXT NOT NULL,
    subject      TEXT,
    state_sha256 TEXT NOT NULL,
    verdict      TEXT NOT NULL,
    advisory     INTEGER NOT NULL DEFAULT 0,
    answers_json TEXT NOT NULL,
    reasons_json TEXT NOT NULL,
    model        TEXT,
    latency_ms   INTEGER,
    error        TEXT,
    label        TEXT,
    labelled_at  REAL,
    labelled_by  TEXT
);
CREATE INDEX IF NOT EXISTS idx_decisions_rubric ON decisions(rubric);
CREATE INDEX IF NOT EXISTS idx_decisions_label ON decisions(rubric, label);
"""


class DecisionLog:
    """Append-only record of every gate decision.

    This is the ProofPacket *and* the calibration corpus: once a human (or a
    System 2 reviewer) fills in ``label``, the rows become the labelled set that
    ``s1gate_calibrate`` measures thresholds against.
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = Path(db_path or DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def record(self, result: GateResult, subject: Optional[str] = None) -> int:
        cur = self._conn.execute(
            "INSERT INTO decisions (ts, rubric, subject, state_sha256, verdict, advisory,"
            " answers_json, reasons_json, model, latency_ms, error)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                time.time(),
                result.rubric,
                subject,
                result.state_sha256,
                result.verdict,
                1 if result.advisory else 0,
                json.dumps(result.answers),
                json.dumps(result.reasons),
                result.model,
                result.latency_ms,
                result.error,
            ),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def label(self, decision_id: int, label: str, by: str = "human") -> None:
        self._conn.execute(
            "UPDATE decisions SET label=?, labelled_at=?, labelled_by=? WHERE id=?",
            (label, time.time(), by, decision_id),
        )
        self._conn.commit()

    def labelled(self, rubric: str) -> List[sqlite3.Row]:
        return list(
            self._conn.execute(
                "SELECT * FROM decisions WHERE rubric=? AND label IS NOT NULL ORDER BY id",
                (rubric,),
            )
        )

    def counts(self, rubric: Optional[str] = None) -> Dict[str, int]:
        q = "SELECT verdict, COUNT(*) c FROM decisions"
        args: Tuple[Any, ...] = ()
        if rubric:
            q += " WHERE rubric=?"
            args = (rubric,)
        q += " GROUP BY verdict"
        return {r["verdict"]: r["c"] for r in self._conn.execute(q, args)}

    def close(self) -> None:
        self._conn.close()


# --------------------------------------------------------------------------
# The gate
# --------------------------------------------------------------------------


def _confidence_check(rubric: Rubric, answers: Dict[str, Any]) -> List[str]:
    """Flag every Score/Choice answer whose distribution is too flat to act on.

    This is the lesson from the very first live probe: a Score can return a
    plausible mean (1.39) off a bimodal distribution (0.46 / 0.42 at opposite
    ends) with confidence 0.0. Acting on that mean would be acting on noise.
    """
    flagged = []
    for qname, ans in (answers or {}).items():
        if not isinstance(ans, dict):
            continue
        if ans.get("type") == "noul":
            continue  # Noul answers carry no confidence by design.
        conf = ans.get("confidence")
        if conf is None:
            continue
        if float(conf) < rubric.confidence_floor:
            flagged.append(
                "low confidence on %r (%.2f < floor %.2f) -- distribution too flat to act on"
                % (qname, float(conf), rubric.confidence_floor)
            )
    return flagged


def evaluate(
    rubric: Rubric | str,
    state: str,
    *,
    subject: Optional[str] = None,
    log: Optional[DecisionLog] = None,
    model: Optional[str] = None,
    timeout: float = 20.0,
) -> GateResult:
    """Score ``state`` against ``rubric`` and return a verdict.

    Verdict precedence is BLOCK > ESCALATE > PASS. An uncalibrated rubric is
    downgraded to advisory: its verdict is reported but ``enforced`` is False,
    so callers that honour the contract will not hard-fail on it.
    """
    rb = load_rubric(rubric) if isinstance(rubric, str) else rubric
    sha = hashlib.sha256(state.encode("utf-8")).hexdigest()
    t0 = time.time()

    try:
        body = ask(state, rb.questions, model=model, timeout=timeout)
    except (ProviderError, S1GateError) as exc:
        # Rule 1: fail closed.
        res = GateResult(
            rubric=rb.name,
            verdict=BLOCK,
            enforced=True,
            advisory=False,
            reasons=["System One unavailable, failing closed: %s" % exc],
            answers={},
            model="",
            latency_ms=int((time.time() - t0) * 1000),
            state_sha256=sha,
            error=str(exc),
        )
        if log:
            res.decision_id = log.record(res, subject)
        return res

    latency = int((time.time() - t0) * 1000)
    answers = body.get("answers") or {}
    verdict = PASS
    reasons: List[str] = []

    for rule in rb.rules:
        cond = rule.get("when", "")
        want = str(rule.get("verdict", ESCALATE)).upper()
        outcome, note = eval_condition(answers, cond)
        if outcome is None:
            # Rule 1 again: an undecidable rule is a reason to escalate, never
            # a reason to pass quietly.
            if _SEVERITY[ESCALATE] > _SEVERITY[verdict]:
                verdict = ESCALATE
            reasons.append("rule %r undecidable (%s)" % (cond, note))
            continue
        if outcome:
            if _SEVERITY.get(want, 2) > _SEVERITY[verdict]:
                verdict = want
            reasons.append("%s: %s [%s]" % (want, rule.get("reason", cond), note))

    for note in _confidence_check(rb, answers):
        if _SEVERITY[ESCALATE] > _SEVERITY[verdict]:
            verdict = ESCALATE
        reasons.append("ESCALATE: " + note)

    # Rule 3: an unmeasured rubric may not block.
    advisory = not rb.enforcing
    if advisory and verdict == BLOCK:
        verdict = ESCALATE
        reasons.append(
            "downgraded BLOCK->ESCALATE: rubric %r is not calibrated; "
            "run s1gate_calibrate before enforcing" % rb.name
        )
    if rb.never_auto and verdict == PASS:
        verdict = ESCALATE
        reasons.append(
            "ESCALATE: rubric %r is marked never_auto -- a machine PASS is a "
            "recommendation, a human still decides" % rb.name
        )

    if verdict == PASS and not reasons:
        reasons.append("no rule tripped; all confidences at or above floor")

    res = GateResult(
        rubric=rb.name,
        verdict=verdict,
        enforced=not advisory,
        advisory=advisory,
        reasons=reasons,
        answers=answers,
        model=str(body.get("model", "")),
        latency_ms=latency,
        state_sha256=sha,
    )
    if log:
        res.decision_id = log.record(res, subject)
    return res
