"""Calibration harness for the RIG System-1 Gate.

Why this file exists
--------------------
A System One answer is a probability. A gate is a threshold. The gap between
them is where every naive deployment dies: someone writes ``if p > 0.85`` and
ships it. 0.85 of *what*? Measured against *which* labelled examples? At what
false-block rate?

RIG law: **no eval ladder, no production claim.** A rubric stays advisory until
its threshold has been swept against labelled ground truth and the resulting
operating point is recorded in the rubric file itself.

The asymmetry that matters
--------------------------
A gate that lets a bad artifact through costs one bad artifact.
A gate that blocks good work gets switched off, and then you have no gate.
So the default objective here is **precision on the BLOCK class** with a
hard ceiling on the false-block rate, not raw accuracy.

Labels
------
Two labels per signal for multi-question or multi-rule rubrics:
  ``bad``  -- the artifact genuinely should not have passed
  ``good`` -- the artifact was fine
Whole-decision labels remain a legacy input only for one-question, one-rule
rubrics. MCP-agent labels are advisory until reviewed on the human side.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .s1gate import (DecisionLog, Rubric, _rule_signal, load_rubric, resolve,
                     rubric_canonical_sha, rule_canonical_sha)


def _rubric_body_sha(body: Dict[str, Any]) -> str:
    import hashlib
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False, default=str)
                          .encode("utf-8")).hexdigest()

__all__ = ["Point", "sweep", "choose_operating_point", "calibrate_rubric", "report"]

MIN_LABELLED = 30  # below this, refuse to certify: the estimate is noise.


@dataclass
class Point:
    threshold: float
    tp: int   # correctly flagged bad
    fp: int   # good work wrongly flagged  <-- the expensive error
    tn: int
    fn: int   # bad work let through

    @property
    def precision(self) -> float:
        d = self.tp + self.fp
        return self.tp / d if d else 0.0

    @property
    def recall(self) -> float:
        d = self.tp + self.fn
        return self.tp / d if d else 0.0

    @property
    def false_block_rate(self) -> float:
        """Share of GOOD artifacts this threshold would have blocked."""
        d = self.fp + self.tn
        return self.fp / d if d else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.update(
            precision=round(self.precision, 4),
            recall=round(self.recall, 4),
            false_block_rate=round(self.false_block_rate, 4),
            f1=round(self.f1, 4),
        )
        return d


def _extract(rows: Iterable[Any], qname: str, attr: str) -> List[Tuple[float, str]]:
    """Pull (value, label) pairs for one answer field out of logged decisions."""
    out: List[Tuple[float, str]] = []
    for r in rows:
        label = (r["signal_label"] if "signal_label" in r.keys() else r["label"] or "").strip().lower()
        if label not in ("good", "bad"):
            continue
        try:
            answers = json.loads(r["answers_json"])
        except (ValueError, TypeError):
            continue
        val = resolve(answers, qname, attr)
        if val is None:
            continue
        try:
            out.append((float(val), label))
        except (TypeError, ValueError):
            continue
    return out


def sweep(
    pairs: Sequence[Tuple[float, str]],
    *,
    steps: int = 101,
    direction: str = "above",
) -> List[Point]:
    """Sweep every threshold and score it.

    ``direction='above'`` means "a HIGH value indicates bad" (e.g. a
    ``weakened_test`` probability). ``'below'`` means a LOW value indicates bad
    (e.g. a quality score).
    """
    if not pairs:
        return []
    lo = min(v for v, _ in pairs)
    hi = max(v for v, _ in pairs)
    if hi == lo:
        hi = lo + 1e-9
    points: List[Point] = []
    for i in range(steps):
        t = lo + (hi - lo) * i / (steps - 1)
        tp = fp = tn = fn = 0
        for val, label in pairs:
            flagged = val >= t if direction == "above" else val <= t
            if flagged and label == "bad":
                tp += 1
            elif flagged and label == "good":
                fp += 1
            elif not flagged and label == "good":
                tn += 1
            else:
                fn += 1
        points.append(Point(round(t, 6), tp, fp, tn, fn))
    return points


def choose_operating_point(
    points: Sequence[Point],
    *,
    max_false_block_rate: float = 0.05,
    min_recall: float = 0.50,
    tie: str = "low",
    declared: Optional[float] = None,
) -> Optional[Point]:
    """Pick the threshold that catches the most bad work while staying under
    the false-block ceiling. Returns None when no threshold qualifies -- which
    is a real and honest answer meaning *this rubric is not ready to enforce*.

    ``tie='middle'`` (opt-in) picks the middle of the band of equally-good
    thresholds: maximum margin from both classes. The default ``'low'`` keeps
    the historical choice, which for ``direction='above'`` is the HARSHEST
    tied threshold (it hugs the good class and false-blocks near-misses).
    """
    eligible = [
        p
        for p in points
        if p.false_block_rate <= max_false_block_rate and p.recall >= min_recall
    ]
    if not eligible:
        return None
    # Maximise recall, break ties on precision, then on the lower threshold.
    ranked = sorted(eligible, key=lambda p: (-p.recall, -p.precision, p.threshold))
    if tie == "middle":
        band = [p for p in ranked if (p.recall, p.precision) == (ranked[0].recall, ranked[0].precision)]
        return band[len(band) // 2]
    if tie == "declared" and declared is not None:
        # Keep the threshold the rule already states when the data cannot tell the
        # tied options apart; move only as far as the measured band requires.
        band = [p for p in ranked if (p.recall, p.precision) == (ranked[0].recall, ranked[0].precision)]
        return min(band, key=lambda p: (abs(p.threshold - declared), p.threshold))
    return ranked[0]


def _labeled_hash(rows, signal: str) -> str:
    import hashlib
    question, attr = signal.split(".", 1)
    evidence = []
    for row in rows:
        signal_scoped = "signal_label" in row.keys()
        evidence.append({
            "decision_id": row["id"], "rubric": row["rubric"],
            "state_sha256": row["state_sha256"], "signal": signal,
            "value": resolve(json.loads(row["answers_json"]), question, attr),
            "label": row["signal_label"] if signal_scoped else row["label"],
            "model": row["model"],
            "labelled_by": row["signal_labelled_by"] if signal_scoped else row["labelled_by"],
            "labelled_at": row["signal_labelled_at"] if signal_scoped else row["labelled_at"],
        })
    body = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _split(pairs: Sequence[Tuple[float, str]]) -> Tuple[List, List]:
    """Deterministic stratified split: every 5th labelled point, taken per class,
    is held out. Same data always yields the same split -- calibration is rerunnable."""
    train: List = []
    hold: List = []
    counters: Dict[str, int] = {}
    for v, lab in pairs:
        i = counters.get(lab, 0)
        counters[lab] = i + 1
        (hold if i % 5 < 2 else train).append((v, lab))
    return train, hold


def _metrics(pairs: Sequence[Tuple[float, str]], t: float, direction: str) -> Dict[str, float]:
    tp = fp = tn = fn = 0
    for val, lab in pairs:
        flagged = val >= t if direction == "above" else val <= t
        if flagged and lab == "bad":
            tp += 1
        elif flagged:
            fp += 1
        elif lab == "good":
            tn += 1
        else:
            fn += 1
    p = Point(t, tp, fp, tn, fn)
    return {"threshold": t, "precision": p.precision, "recall": p.recall,
            "false_block_rate": p.false_block_rate}


def _declared_threshold(rule: Dict[str, Any]) -> Optional[float]:
    """'lane.confidence <= 0.90' -> 0.9. None when the rule has no numeric bound."""
    import re as _re
    m = _re.search(r"(>=|<=|>|<)\s*([0-9]*\.?[0-9]+)\s*$", str(rule.get("when", "")))
    return float(m.group(2)) if m else None


def calibrate_rubric(
    rubric_name: str,
    signal: Tuple[str, str],
    *,
    direction: str = "above",
    max_false_block_rate: float = 0.05,
    min_recall: float = 0.50,
    tie: str = "low",
    db_path: Optional[Path] = None,
    rubric_dir: Optional[Path] = None,
    write: bool = False,
) -> Dict[str, Any]:
    """Measure ONE signal and, optionally, certify THAT RULE only.

    Certification is per rule: a rubric becomes whole-rubric `calibrated` only when
    every rule signal has its own certified entry. The chosen threshold must hold
    on train, holdout, AND combined -- a rule that only works in-sample does not
    ship. A signal with no matching rule in the rubric is refused WITHOUT writing
    anything: calibration that cannot bind to a rule is decoration.
    """
    rb: Rubric = load_rubric(rubric_name, rubric_dir)
    qname, attr = signal
    sig = "%s.%s" % (qname, attr)

    # Bind first or refuse: exactly one rule must carry this signal.
    matching = [r for r in rb.rules if _rule_signal(r) == sig]
    if len(matching) != 1:
        raise ValueError(
            "refusing to calibrate %s.%s: %d rules match signal %r "
            "(need exactly 1); nothing written" % (rubric_name, attr, len(matching), sig))
    rule = matching[0]

    log = DecisionLog(db_path)
    try:
        needs_signal_labels = (len(rb.questions) > 1
                               or len({_rule_signal(r) for r in rb.rules}) > 1)
        rows = (log.labelled_signal(rubric_name, sig) if needs_signal_labels
                else log.labelled(rubric_name))
        models = sorted({r["model"] or "" for r in rows})
    finally:
        log.close()

    pairs = _extract(rows, qname, attr)
    n_bad = sum(1 for _, l in pairs if l == "bad")
    n_good = len(pairs) - n_bad
    result: Dict[str, Any] = {
        "rubric": rubric_name, "signal": sig, "direction": direction,
        "label_scope": "signal" if needs_signal_labels else "decision",
        "n_labelled": len(pairs), "n_good": n_good, "n_bad": n_bad, "certified": False, "reason": "",
    }
    if len(pairs) < MIN_LABELLED:
        result["reason"] = (
            "only %d labelled decisions; need >= %d before any threshold is "
            "trustworthy. Gate stays advisory." % (len(pairs), MIN_LABELLED))
        return result
    if len(models) != 1 or not models[0]:
        result["reason"] = "mixed or missing judge models; calibrate each model separately"
        return result
    if n_bad < 5 or n_good < 5:
        result["reason"] = "class imbalance: %d good / %d bad. Need >= 5 of each." % (n_good, n_bad)
        return result

    train, holdout = _split(pairs)
    points = sweep(train, direction=direction)
    chosen = choose_operating_point(points, max_false_block_rate=max_false_block_rate,
                                    min_recall=min_recall, tie=tie,
                                    declared=_declared_threshold(rule))
    result["separation"] = round(
        abs(statistics.fmean([v for v, l in pairs if l == "bad"])
            - statistics.fmean([v for v, l in pairs if l == "good"])), 4)
    if chosen is None:
        result["reason"] = (
            "no threshold satisfies false_block_rate <= %.2f and recall >= %.2f on TRAIN. "
            "The signal does not separate good from bad on this data. Fix the "
            "rubric wording or drop the gate -- do not ship it." % (max_false_block_rate, min_recall))
        return result
    t = chosen.threshold
    dec = _declared_threshold(rule)
    if tie == "declared" and dec is not None:
        # Use the stated value itself when it scores exactly like the chosen point on TRAIN.
        m_c, m_d = _metrics(train, t, direction), _metrics(train, dec, direction)
        if all(m_c[k] == m_d[k] for k in ("precision", "recall", "false_block_rate")):
            t = dec
            chosen = Point(dec, chosen.tp, chosen.fp, chosen.tn, chosen.fn)
    m_train = _metrics(train, t, direction)
    m_hold = _metrics(holdout, t, direction)
    m_all = _metrics(list(pairs), t, direction)
    result["operating_point"] = chosen.to_dict()
    result["train"], result["holdout"], result["combined"] = m_train, m_hold, m_all

    def meets(m: Dict[str, float]) -> bool:
        return m["false_block_rate"] <= max_false_block_rate and m["recall"] >= min_recall

    if not (meets(m_hold) and meets(m_all)):
        result["reason"] = (
            "threshold %.4f holds on train but fails holdout (fbr=%.2f recall=%.2f) or "
            "combined (fbr=%.2f recall=%.2f): in-sample fit is not calibration. "
            "Gate stays advisory." % (t, m_hold["false_block_rate"], m_hold["recall"],
                                      m_all["false_block_rate"], m_all["recall"]))
        return result

    result["reason"] = "threshold %.4f meets the ceiling on train, holdout, and combined" % t

    if write:
        path = Path(rb.path)  # type: ignore[arg-type]
        raw = json.loads(path.read_text(encoding="utf-8"))
        import re as _re
        # Edit the SHIPPED text first, then hash what a later reader will load:
        # the binding must survive the write, not describe the pre-write state.
        for r in raw.get("rules", []):
            if _rule_signal(r) == sig:
                r["when"] = "%s %s %.4f" % (sig, ">=" if direction == "above" else "<=", round(t, 4))
                edited = r
        fields = {f for f in Rubric.__dataclass_fields__ if f != "path"}
        rb_after = Rubric(**{k: v for k, v in raw.items() if k in fields})
        edited = next(r for r in raw["rules"] if _rule_signal(r) == sig)
        entry = {
            "direction": direction, "threshold": round(t, 4),
            "label_scope": result["label_scope"],
            "train": m_train, "holdout": m_hold, "combined": m_all,
            "n_labelled": len(pairs), "n_good": n_good, "n_bad": n_bad,
            "labeled_set_sha256": _labeled_hash(rows, sig),
            "model": models[0],
            "models_seen": models,
            "rule_sha256": rule_canonical_sha(edited),
            "rubric_sha256": rubric_canonical_sha(rb_after),
            "max_false_block_rate": max_false_block_rate, "min_recall": min_recall,
            "tie": tie,
        }
        cal = raw.setdefault("calibration", {})
        cal.setdefault("rules", {})[sig] = entry
        all_sigs = []
        for r in raw.get("rules", []):
            m = _re.match(r"^\s*(\w+\.(?:p\.[\w\-]+|\w+))", str(r.get("when", "")))
            if m and m.group(1) not in all_sigs:
                all_sigs.append(m.group(1))
        raw["calibrated"] = bool(all_sigs) and all(
            s in cal["rules"] and (not needs_signal_labels
                                   or cal["rules"][s].get("label_scope") == "signal")
            for s in all_sigs)
        path.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
        result["certified"] = True
        result["rubric_calibrated"] = raw["calibrated"]
        result["written_to"] = str(path)

    return result


def report(result: Dict[str, Any]) -> str:
    lines = [
        "s1gate calibration: %s" % result["rubric"],
        "  signal        : %s (%s = bad)" % (result["signal"], result["direction"]),
        "  labelled      : %d  (good=%d bad=%d)"
        % (result["n_labelled"], result["n_good"], result["n_bad"]),
    ]
    if "separation" in result:
        lines.append("  separation    : %.4f mean gap" % result["separation"])
    op = result.get("operating_point")
    if op:
        lines += [
            "  threshold     : %.4f" % op["threshold"],
            "  precision     : %.3f" % op["precision"],
            "  recall        : %.3f" % op["recall"],
            "  false-block   : %.3f  <- the expensive error" % op["false_block_rate"],
        ]
    lines.append("  certified     : %s" % ("YES" if result["certified"] else "no"))
    lines.append("  %s" % result["reason"])
    return "\n".join(lines)
