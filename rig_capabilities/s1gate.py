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

# Deterministic answer cache. The provider answer for (rubric, state, questions,
# model) is treated as reusable for CACHE_TTL_DAYS; the VERDICT is never cached --
# it is recomputed from the cached answers against the CURRENT rubric on every
# call, so rule edits, calibration changes and never_auto always apply fresh.
# Measured motivation (2026-09-30, decisions.db): the top-volume sites re-ask an
# identical state 36-96% of the time and pay 200-1900 ms each time.
# Disable entirely with S1GATE_CACHE=0.
CACHE_ENABLED = os.environ.get("S1GATE_CACHE", "1") != "0"
CACHE_TTL_DAYS = float(os.environ.get("S1GATE_CACHE_TTL_DAYS", "7"))

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


def _rule_signal(rule: Dict[str, Any]) -> Optional[str]:
    """'claim_atomic.noul <= 0.50' -> 'claim_atomic.noul'."""
    # 'risk.p.yes >= 0.5' -> 'risk.p.yes': a per-option probability is its own signal.
    m = re.match(r"^\s*(\w+\.(?:p\.[\w\-]+|\w+))", str(rule.get("when", "")))
    return m.group(1) if m else None


def rule_canonical_sha(rule: Dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(rule, sort_keys=True, ensure_ascii=False)
                          .encode("utf-8")).hexdigest()


def questions_sha(questions: Dict[str, Any]) -> str:
    """Canonical hash of the question set. The answers a provider returns are a
    function of the state AND the questions, so both belong in the cache key."""
    return hashlib.sha256(json.dumps(questions, sort_keys=True, ensure_ascii=False, default=str)
                          .encode("utf-8")).hexdigest()


def rubric_canonical_sha(rb: "Rubric") -> str:
    """Hash over everything that shapes judgement -- calibration data and the file
    path are excluded, or writing a certification would invalidate itself."""
    body = asdict(rb)
    # calibration, the derived whole-rubric flag, and the rules list are EXCLUDED:
    # rules bind through their own rule_sha256, so certifying rule B must not void
    # rule A's binding. What remains -- questions, stage, lane, wording, floor --
    # is exactly what shapes every answer from the judge.
    for k in ("calibration", "calibrated", "path", "rules"):
        body.pop(k, None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False, default=str)
                          .encode("utf-8")).hexdigest()


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
        """Report effective enforcement, not a legacy configuration flag."""
        return bool(self.rules) and all(self.rule_enforces(rule) for rule in self.rules)

    def rule_enforces(self, rule: Dict[str, Any], model: Optional[str] = None) -> bool:
        """A rule enforces only on its OWN certification whose hashes still match.

        Editing the rule, any part of the rubric, or switching the judging model
        voids the certification -- the rule drops back to advisory rather than
        enforcing on stale evidence. Multi-question and multi-rule rubrics also
        require signal-scoped ground truth; a whole-decision label cannot
        certify an individual question. Single-rule legacy packs retain the
        whole-rubric fallback.
        """
        sig = _rule_signal(rule)
        entries = (self.calibration or {}).get("rules") or {}
        entry = entries.get(sig) if sig else None
        needs_signal_labels = (len(self.questions) > 1
                               or len({_rule_signal(r) for r in self.rules}) > 1)
        if not entry:
            return bool(self.calibrated) and not needs_signal_labels
        if needs_signal_labels and entry.get("label_scope") != "signal":
            return False
        if entry.get("model") != (model or JEV_MODEL):
            return False
        return (entry.get("rule_sha256") == rule_canonical_sha(rule)
                and entry.get("rubric_sha256") == rubric_canonical_sha(self))


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
    state_preview: str = ""
    error: Optional[str] = None
    decision_id: Optional[int] = None
    cache_hit: bool = False

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
    excluded     INTEGER NOT NULL DEFAULT 0,
    exclusion_reason TEXT,
    label        TEXT,
    labelled_at  REAL,
    labelled_by  TEXT,
    state_preview TEXT
);
CREATE INDEX IF NOT EXISTS idx_decisions_rubric ON decisions(rubric);
CREATE INDEX IF NOT EXISTS idx_decisions_label ON decisions(rubric, label);
CREATE TABLE IF NOT EXISTS decision_signal_labels (
    decision_id INTEGER NOT NULL REFERENCES decisions(id),
    signal TEXT NOT NULL,
    label TEXT NOT NULL CHECK (label IN ('good', 'bad')),
    labelled_at REAL NOT NULL,
    labelled_by TEXT NOT NULL,
    PRIMARY KEY (decision_id, signal)
);
CREATE INDEX IF NOT EXISTS idx_signal_labels_signal ON decision_signal_labels(signal, label);
CREATE TABLE IF NOT EXISTS answer_cache (
    rubric        TEXT NOT NULL,
    state_sha256  TEXT NOT NULL,
    questions_sha TEXT NOT NULL,
    model_alias   TEXT NOT NULL,
    answers_json  TEXT NOT NULL,
    response_model TEXT,
    created_ts    REAL NOT NULL,
    last_hit_ts   REAL,
    hits          INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (rubric, state_sha256, questions_sha, model_alias)
);
"""


class DecisionLog:
    """Append-only record of every gate decision.

    This is the decision receipt and calibration corpus. Multi-question
    rubrics require a separate ground-truth label for each signal. A global
    decision label cannot certify those rules.
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = Path(db_path or DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), timeout=30)
        # Multiple lanes (advisor-plus, routines, hooks) write to this one file
        # from separate processes. sqlite's default is to fail immediately on a
        # lock; busy_timeout makes a writer WAIT instead of erroring. Reported
        # live 2026-09-30: database-is-locked errors across two LinkedIn lanes.
        self._conn.execute("PRAGMA busy_timeout = 30000")
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        # Migration for databases created before state previews existed. A busy
        # error means another writer just did the same ALTER; verify either way.
        for ddl in ("ALTER TABLE decisions ADD COLUMN state_preview TEXT",
                    "ALTER TABLE decisions ADD COLUMN excluded INTEGER NOT NULL DEFAULT 0",
                    "ALTER TABLE decisions ADD COLUMN exclusion_reason TEXT",
                    "ALTER TABLE decisions ADD COLUMN cache_hit INTEGER NOT NULL DEFAULT 0"):
            try:
                self._conn.execute(ddl)
            except sqlite3.OperationalError:
                pass
        cols = {r[1] for r in self._conn.execute("PRAGMA table_info(decisions)")}
        self.has_preview = "state_preview" in cols
        self.has_cache_hit = "cache_hit" in cols
        self._conn.commit()

    def record(self, result: GateResult, subject: Optional[str] = None) -> int:
        # A decision with no subject cannot be attributed to a caller or
        # artifact, so it can never be calibrated. Refuse loudly; never
        # silently default. Callers pass 'kind:id@sha12', e.g.
        # 'code.diff:pr-42@a1b2c3d4e5f6'.
        if subject is None or not str(subject).strip():
            raise ValueError(
                "refusing to log a decision without a subject: pass "
                "subject='kind:id@sha12' (e.g. 'code.diff:pr-42@a1b2c3d4e5f6'); "
                "an unattributable row poisons every aggregate on the table")
        preview = getattr(result, "state_preview", "") or None
        cache_hit = 1 if getattr(result, "cache_hit", False) else 0
        # A row that carries an error is a provider failure, not a judgment:
        # quarantine it out of the scoring path at birth (reversible flag,
        # nothing deleted).
        excluded = 1 if result.error else 0
        exclusion_reason = ("provider-error: %s" % result.error)[:200] if result.error else None
        if self.has_preview and self.has_cache_hit:
            cur = self._conn.execute(
                "INSERT INTO decisions (ts, rubric, subject, state_sha256, verdict, advisory,"
                " answers_json, reasons_json, model, latency_ms, error, state_preview,"
                " excluded, exclusion_reason, cache_hit)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
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
                    preview,
                    excluded,
                    exclusion_reason,
                    cache_hit,
                ),
            )
        elif self.has_preview:
            cur = self._conn.execute(
                "INSERT INTO decisions (ts, rubric, subject, state_sha256, verdict, advisory,"
                " answers_json, reasons_json, model, latency_ms, error, state_preview,"
                " excluded, exclusion_reason)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
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
                    preview,
                    excluded,
                    exclusion_reason,
                ),
            )
        else:
            cur = self._conn.execute(
                "INSERT INTO decisions (ts, rubric, subject, state_sha256, verdict, advisory,"
                " answers_json, reasons_json, model, latency_ms, error,"
                " excluded, exclusion_reason)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
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
                    excluded,
                    exclusion_reason,
                ),
            )
        self._conn.commit()
        return int(cur.lastrowid)

    def recent(self, rubric: Optional[str] = None, n: int = 20, unlabelled: bool = False) -> List[sqlite3.Row]:
        q = "SELECT * FROM decisions"
        cond, args = [], []
        if rubric:
            cond.append("rubric=?")
            args.append(rubric)
        if unlabelled:
            cond.append("label IS NULL")
        if cond:
            q += " WHERE " + " AND ".join(cond)
        q += " ORDER BY id DESC LIMIT ?"
        args.append(max(1, min(int(n), 500)))
        return list(self._conn.execute(q, args))

    def get(self, decision_id: int) -> Optional[sqlite3.Row]:
        return self._conn.execute("SELECT * FROM decisions WHERE id=?", (decision_id,)).fetchone()

    def label(self, decision_id: int, label: str, by: str = "human") -> None:
        if label not in ("good", "bad"):
            raise ValueError("label must be good or bad")
        self._conn.execute(
            "UPDATE decisions SET label=?, labelled_at=?, labelled_by=? WHERE id=?",
            (label, time.time(), by, decision_id),
        )
        self._conn.commit()

    def label_signal(self, decision_id: int, signal: str, label: str,
                     by: str = "human") -> None:
        """Label the defect represented by one question, not the whole artifact."""
        if label not in ("good", "bad"):
            raise ValueError("label must be good or bad")
        parts = signal.split(".", 1)
        if (len(parts) != 2 or not re.fullmatch(r"\w+", parts[0])
                or not re.fullmatch(r"\w+|p\.[\w\-]+", parts[1])):
            raise ValueError("signal must look like question.attr or question.p.option")
        decision = self.get(decision_id)
        if decision is None:
            raise ValueError("decision not found")
        answers = json.loads(decision["answers_json"])
        if resolve(answers, parts[0], parts[1]) is None:
            raise ValueError("decision has no answer for signal")
        self._conn.execute(
            "INSERT INTO decision_signal_labels"
            " (decision_id, signal, label, labelled_at, labelled_by)"
            " VALUES (?,?,?,?,?)"
            " ON CONFLICT(decision_id, signal) DO UPDATE SET"
            " label=excluded.label, labelled_at=excluded.labelled_at,"
            " labelled_by=excluded.labelled_by",
            (decision_id, signal, label, time.time(), by),
        )
        self._conn.commit()

    def labelled_signal(self, rubric: str, signal: str) -> List[sqlite3.Row]:
        return list(self._conn.execute(
            "SELECT d.*, l.label AS signal_label,"
            " l.labelled_by AS signal_labelled_by,"
            " l.labelled_at AS signal_labelled_at FROM decisions AS d"
            " JOIN decision_signal_labels AS l ON l.decision_id=d.id"
            " WHERE d.rubric=? AND l.signal=? AND l.labelled_by!='mcp-agent'"
            " AND COALESCE(d.excluded,0)=0"
            " ORDER BY d.id",
            (rubric, signal),
        ))

    def labelled(self, rubric: str) -> List[sqlite3.Row]:
        return list(
            self._conn.execute(
                "SELECT * FROM decisions WHERE rubric=? AND label IS NOT NULL"
                " AND COALESCE(excluded,0)=0"
                " AND COALESCE(labelled_by, '')!='mcp-agent' ORDER BY id",
                (rubric,),
            )
        )

    def counts(self, rubric: Optional[str] = None) -> Dict[str, int]:
        q = "SELECT verdict, COUNT(*) c FROM decisions WHERE COALESCE(excluded,0)=0"
        args: Tuple[Any, ...] = ()
        if rubric:
            q += " AND rubric=?"
            args = (rubric,)
        q += " GROUP BY verdict"
        return {r["verdict"]: r["c"] for r in self._conn.execute(q, args)}

    def hygiene(self, rubric: Optional[str] = None) -> Dict[str, int]:
        """Honest corpus totals: what is attributable, what is quarantined,
        and the pass rate over clean rows only (non-blank subject, no error)."""
        where, args = "1=1", ()
        if rubric:
            where, args = "rubric=?", (rubric,)
        row = self._conn.execute(
            "SELECT COUNT(*) total,"
            " SUM(subject IS NULL OR TRIM(subject)='') blank,"
            " SUM(COALESCE(excluded,0)!=0) excluded,"
            " SUM(COALESCE(excluded,0)=0 AND subject IS NOT NULL"
            "     AND TRIM(subject)!='') clean,"
            " SUM(COALESCE(excluded,0)=0 AND subject IS NOT NULL"
            "     AND TRIM(subject)!='' AND verdict='PASS') clean_pass"
            " FROM decisions WHERE " + where, args).fetchone()
        return {k: int(row[k] or 0) for k in ("total", "blank", "excluded", "clean", "clean_pass")}

    def close(self) -> None:
        self._conn.close()

    # ------------------------------------------------------------------
    # Deterministic answer cache. Caches the provider's ANSWERS only; the
    # verdict is always recomputed from current rubric logic in evaluate().
    # A cache hit therefore cannot launder a stale enforcement decision.
    # ------------------------------------------------------------------

    def cache_lookup(self, rubric: str, state_sha256: str, qsha: str,
                     model_alias: str) -> Optional[Dict[str, Any]]:
        """Return the cached body {'answers': ..., 'model': ...} or None.

        A row past CACHE_TTL_DAYS is a miss (and is pruned lazily). A hit bumps
        its own counters so `cache-stats` can prove the cache is earning.
        """
        if not CACHE_ENABLED:
            return None
        row = self._conn.execute(
            "SELECT answers_json, response_model, created_ts FROM answer_cache"
            " WHERE rubric=? AND state_sha256=? AND questions_sha=? AND model_alias=?",
            (rubric, state_sha256, qsha, model_alias),
        ).fetchone()
        if row is None:
            return None
        age = time.time() - float(row["created_ts"])
        if age > CACHE_TTL_DAYS * 86400:
            self._conn.execute(
                "DELETE FROM answer_cache WHERE rubric=? AND state_sha256=?"
                " AND questions_sha=? AND model_alias=?",
                (rubric, state_sha256, qsha, model_alias))
            self._conn.commit()
            return None
        self._conn.execute(
            "UPDATE answer_cache SET hits=hits+1, last_hit_ts=?"
            " WHERE rubric=? AND state_sha256=? AND questions_sha=? AND model_alias=?",
            (time.time(), rubric, state_sha256, qsha, model_alias))
        self._conn.commit()
        return {"answers": json.loads(row["answers_json"]),
                "model": row["response_model"] or "",
                "_cache_age_s": int(age)}

    def cache_store(self, rubric: str, state_sha256: str, qsha: str,
                    model_alias: str, answers: Dict[str, Any],
                    response_model: str) -> None:
        if not CACHE_ENABLED:
            return
        self._conn.execute(
            "INSERT INTO answer_cache (rubric, state_sha256, questions_sha, model_alias,"
            " answers_json, response_model, created_ts, hits) VALUES (?,?,?,?,?,?,?,0)"
            " ON CONFLICT(rubric, state_sha256, questions_sha, model_alias) DO UPDATE SET"
            " answers_json=excluded.answers_json, response_model=excluded.response_model,"
            " created_ts=excluded.created_ts, hits=0",
            (rubric, state_sha256, qsha, model_alias,
             json.dumps(answers), response_model, time.time()))
        self._conn.commit()

    def cache_stats(self, rubric: Optional[str] = None) -> Dict[str, Any]:
        where, args = ("WHERE rubric=?", (rubric,)) if rubric else ("", ())
        rows = list(self._conn.execute(
            "SELECT rubric, COUNT(*) entries, SUM(hits) hits,"
            " SUM(LENGTH(answers_json)) bytes FROM answer_cache " + where +
            " GROUP BY rubric ORDER BY hits DESC", args))
        out = {"enabled": CACHE_ENABLED, "ttl_days": CACHE_TTL_DAYS, "rubrics": []}
        total_hits = 0
        for r in rows:
            out["rubrics"].append({"rubric": r["rubric"], "entries": r["entries"],
                                   "hits": int(r["hits"] or 0), "bytes": int(r["bytes"] or 0)})
            total_hits += int(r["hits"] or 0)
        out["total_hits"] = total_hits
        out["total_hits"] = total_hits
        out["logged_cache_hits"] = int(self._conn.execute(
            "SELECT COUNT(*) FROM decisions WHERE cache_hit=1" +
            (" AND rubric=?" if rubric else ""), args).fetchone()[0] or 0)
        # Estimated avoided latency: cache-hit rows have ~0ms themselves, so the
        # honest estimate is hits x the average MISS latency for the same rubric.
        avg = self._conn.execute(
            "SELECT AVG(latency_ms) FROM decisions WHERE COALESCE(cache_hit,0)=0"
            " AND error IS NULL" + (" AND rubric=?" if rubric else ""), args).fetchone()[0]
        out["avg_miss_latency_ms"] = int(avg or 0)
        out["est_ms_saved"] = int((avg or 0) * out["logged_cache_hits"])
        return out

    def cache_clear(self, rubric: Optional[str] = None) -> int:
        if rubric:
            cur = self._conn.execute("DELETE FROM answer_cache WHERE rubric=?", (rubric,))
        else:
            cur = self._conn.execute("DELETE FROM answer_cache")
        self._conn.commit()
        return int(cur.rowcount or 0)


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
    # A short local preview is what makes a logged decision labelable later.
    # Disable entirely with S1GATE_STATE_PREVIEW=0.
    preview = "" if os.environ.get("S1GATE_STATE_PREVIEW") == "0" else state[:500]
    t0 = time.time()

    # Deterministic answer cache: same rubric + same state + same questions +
    # same model alias within TTL skips the network call. The verdict below is
    # still computed from live rubric logic, so a cached answer under a rubric
    # that has since been hardened will freshly BLOCK. A provider failure is
    # never cached.
    qsha = questions_sha(rb.questions)
    model_alias = model or JEV_MODEL
    cached = log.cache_lookup(rb.name, sha, qsha, model_alias) if log else None
    cache_hit = cached is not None

    if cache_hit:
        body = {"answers": cached["answers"], "model": cached["model"]}
    else:
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
                state_preview=preview,
                error=str(exc),
            )
            if log:
                res.decision_id = log.record(res, subject)
            return res
        if log:
            log.cache_store(rb.name, sha, qsha, model_alias,
                            body.get("answers") or {},
                            str(body.get("model") or ""))

    latency = int((time.time() - t0) * 1000)
    # Certification binds to the model that ANSWERED (e.g. jev-1.13.0), not the
    # requested alias (jev-latest): comparing to the alias meant no certified rule
    # ever enforced. A version change still voids the certification.
    judged = str(body.get("model") or "") or model or JEV_MODEL
    answers = body.get("answers") or {}
    verdict = PASS
    reasons: List[str] = []

    fired_enforce: List[bool] = []
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
            enforce = rb.rule_enforces(rule, judged)
            fired_enforce.append(enforce)
            if want == BLOCK and not enforce:
                # Rule 3, per rule: a signal nobody measured may annotate, not block.
                want = ESCALATE
                reasons.append(
                    "downgraded BLOCK->ESCALATE: rule %r is not calibrated (or its "
                    "certification is stale: rubric, rule, or model changed); "
                    "run s1gate_calibrate before enforcing" % (_rule_signal(rule) or cond))
            if _SEVERITY.get(want, 2) > _SEVERITY[verdict]:
                verdict = want
            reasons.append("%s: %s [%s]" % (want, rule.get("reason", cond), note))

    for note in _confidence_check(rb, answers):
        if _SEVERITY[ESCALATE] > _SEVERITY[verdict]:
            verdict = ESCALATE
        reasons.append("ESCALATE: " + note)

    # Rule 3: an unmeasured signal may not block. Enforcement is per rule: one
    # certified rule no longer launders its uncertified neighbours into hard power,
    # and a whole-rubric `calibrated: true` still means what it meant for legacy packs.
    # The pack enforces when at least one FIRED rule carries its own certification.
    # An enforceable BLOCK is not diluted by uncalibrated neighbours; a BLOCK from an
    # uncalibrated rule was already downgraded in the loop above.
    advisory = ((not any(fired_enforce)) if fired_enforce else
                not (bool(rb.rules) and all(rb.rule_enforces(r, judged) for r in rb.rules)))
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
        state_preview=preview,
        cache_hit=cache_hit,
    )
    if log:
        res.decision_id = log.record(res, subject)
    return res
