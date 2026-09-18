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
Two labels per rubric, on the decision rows:
  ``bad``  -- the artifact genuinely should not have passed
  ``good`` -- the artifact was fine
Anything else is ignored.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .s1gate import DecisionLog, Rubric, load_rubric, resolve

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
        label = (r["label"] or "").strip().lower()
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
) -> Optional[Point]:
    """Pick the threshold that catches the most bad work while staying under
    the false-block ceiling. Returns None when no threshold qualifies -- which
    is a real and honest answer meaning *this rubric is not ready to enforce*.
    """
    eligible = [
        p
        for p in points
        if p.false_block_rate <= max_false_block_rate and p.recall >= min_recall
    ]
    if not eligible:
        return None
    # Maximise recall, break ties on precision, then on the gentler threshold.
    return sorted(eligible, key=lambda p: (-p.recall, -p.precision, p.threshold))[0]


def calibrate_rubric(
    rubric_name: str,
    signal: Tuple[str, str],
    *,
    direction: str = "above",
    max_false_block_rate: float = 0.05,
    min_recall: float = 0.50,
    db_path: Optional[Path] = None,
    rubric_dir: Optional[Path] = None,
    write: bool = False,
) -> Dict[str, Any]:
    """Measure one rubric's primary signal and, optionally, certify it.

    ``signal`` is ``(question_name, attribute)`` e.g. ``("weakened_test", "noul")``.
    Certification (``write=True``) rewrites the rubric JSON with the measured
    threshold, the metrics, and ``calibrated: true``.
    """
    rb: Rubric = load_rubric(rubric_name, rubric_dir)
    log = DecisionLog(db_path)
    try:
        rows = log.labelled(rubric_name)
    finally:
        log.close()

    qname, attr = signal
    pairs = _extract(rows, qname, attr)
    n_bad = sum(1 for _, l in pairs if l == "bad")
    n_good = len(pairs) - n_bad

    result: Dict[str, Any] = {
        "rubric": rubric_name,
        "signal": "%s.%s" % (qname, attr),
        "direction": direction,
        "n_labelled": len(pairs),
        "n_good": n_good,
        "n_bad": n_bad,
        "certified": False,
        "reason": "",
    }

    if len(pairs) < MIN_LABELLED:
        result["reason"] = (
            "only %d labelled decisions; need >= %d before any threshold is "
            "trustworthy. Gate stays advisory." % (len(pairs), MIN_LABELLED)
        )
        return result
    if n_bad < 5 or n_good < 5:
        result["reason"] = (
            "class imbalance: %d good / %d bad. Need >= 5 of each." % (n_good, n_bad)
        )
        return result

    points = sweep(pairs, direction=direction)
    chosen = choose_operating_point(
        points, max_false_block_rate=max_false_block_rate, min_recall=min_recall
    )
    result["curve"] = [p.to_dict() for p in points[:: max(1, len(points) // 20)]]
    result["separation"] = round(
        abs(
            statistics.fmean([v for v, l in pairs if l == "bad"])
            - statistics.fmean([v for v, l in pairs if l == "good"])
        ),
        4,
    )

    if chosen is None:
        result["reason"] = (
            "no threshold satisfies false_block_rate <= %.2f and recall >= %.2f. "
            "The signal does not separate good from bad on this data. Fix the "
            "rubric wording or drop the gate -- do not ship it."
            % (max_false_block_rate, min_recall)
        )
        return result

    result["operating_point"] = chosen.to_dict()
    result["reason"] = "threshold %.4f meets the ceiling" % chosen.threshold

    if write:
        path = Path(rb.path)  # type: ignore[arg-type]
        raw = json.loads(path.read_text(encoding="utf-8"))
        updated = False
        for rule in raw.get("rules", []):
            if rule.get("when", "").startswith("%s.%s" % (qname, attr)):
                op = ">=" if direction == "above" else "<="
                rule["when"] = "%s.%s %s %.4f" % (qname, attr, op, chosen.threshold)
                updated = True
        if not updated:
            result["reason"] += " (WARNING: no matching rule to update)"
        raw["calibrated"] = True
        raw["calibration"] = {
            "signal": result["signal"],
            "direction": direction,
            "n_labelled": len(pairs),
            "n_good": n_good,
            "n_bad": n_bad,
            "operating_point": chosen.to_dict(),
            "max_false_block_rate": max_false_block_rate,
            "min_recall": min_recall,
        }
        path.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
        result["certified"] = True
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
