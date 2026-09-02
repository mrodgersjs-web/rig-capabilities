#!/usr/bin/env python3
"""Enforce the forged-evaluator contract mechanically.

A rubric is only worth what the exemplars it came from can prove: the forge
claims to have derived scoring dimensions from a curated exemplar plus degraded
negatives, so the derived rubric MUST rank the real exemplar strictly above its
degraded twin. If it cannot, the rubric is self-scoring theater — it scores the
adjectives, not the specifics.

Two files:

  rubric          — the derived rubric (strict YAML subset): `version`,
                    `margin`, and a `dimensions` list where each dimension has
                    a `name` and a numeric `weight`; weights sum to 100.
  scores.jsonl    — the scoring record. `artifact` rows name the real exemplar
                    and the degraded negatives (each negative names its `twin`,
                    the exemplar it was degraded from). `finding` rows give one
                    per artifact x dimension: `met` plus, when RED, a
                    localized `finding` naming the artifact node and the check
                    that goes RED — never a bare adjective.

The scoring total is RECOMPUTED here from the rubric weights and the per-
dimension `met` flags; the forge never reports a number this checker cannot
derive itself. The load-bearing verdict: for every negative, its twin's total
minus the negative's total must be >= the declared `margin`. Equality with the
twin, an inverted ranking, or a gap below the margin is exit 2.

Exit codes (the honesty contract):
  0  rubric well-formed, every artifact path resolves, every negative actually
     differs from its twin, every RED finding is localized, and every twin
     outranks its degraded copy by at least the margin
  1  usage / file-not-found (a refusal to judge, not a verdict)
  2  a contract violation: a dimension without a weight, weights that do not
     sum to 100, an exemplar path that does not resolve, a negative identical
     to its twin (not actually degraded), an unlocalized RED finding, or a
     rubric that fails to rank a real exemplar above its degraded twin

Stdlib only. Reads only the paths it is given. Writes nothing.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WEIGHT_SUM = 100.0
ROLES = {"exemplar", "negative"}


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def parse_rubric(text: str, violations: list):
    """Parse the strict YAML subset the rubric is allowed to use.

    Returns (version, margin, dimensions) with whatever was parseable; every
    problem is appended to violations.
    """
    version = margin = None
    dimensions: list = []
    current = None       # dimension dict being extended
    in_dims = False
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw.startswith((" ", "\t")):
            key, _, rest = raw.partition(":")
            key, rest = key.strip(), rest.strip()
            in_dims = key == "dimensions"
            if key == "version":
                v = _num(rest)
                if v is None:
                    violations.append(f"rubric: `version` is not an integer ({rest!r})")
                else:
                    version = int(v)
            elif key == "margin":
                margin = _num(rest)
                if margin is None:
                    violations.append(f"rubric: `margin` is not numeric ({rest!r})")
            elif key != "dimensions":
                violations.append(f"rubric: unknown top-level key {key!r}")
            elif rest:
                violations.append("rubric: `dimensions` must be followed by an indented list")
            current = None
            continue
        if not in_dims:
            violations.append(f"rubric: indented line outside `dimensions`: {raw.strip()!r}")
            continue
        stripped = raw.strip()
        if stripped.startswith("- "):
            body = stripped[2:]
            k, _, v = body.partition(":")
            if k.strip() != "name":
                violations.append(f"rubric: dimension item must start with `name:` ({body!r})")
                current = None
                continue
            current = {"name": v.strip(), "weight": None, "origin": body}
            dimensions.append(current)
            continue
        k, _, v = stripped.partition(":")
        if current is None or not k.strip():
            violations.append(f"rubric: malformed dimension line: {stripped!r}")
            continue
        if k.strip() != "weight":
            violations.append(f"rubric: unknown dimension key {k.strip()!r}")
            continue
        current["weight"] = _num(v.strip())
        if current["weight"] is None:
            violations.append(
                f"rubric: dimension {current['name']!r} weight is not numeric ({v.strip()!r})")
    if version is None:
        violations.append("rubric: `version` missing — an unversioned rubric cannot be cited by a promotion")
    if margin is None:
        violations.append("rubric: `margin` missing — the required twin-gap must be declared, not implied")
    if not dimensions:
        violations.append("rubric: no dimensions — a rubric that scores nothing ranks nothing")
    seen = set()
    total = 0.0
    for d in dimensions:
        if not d["name"]:
            violations.append(f"rubric: a dimension has no name ({d['origin']!r})")
        elif d["name"] in seen:
            violations.append(f"rubric: duplicate dimension name {d['name']!r}")
        seen.add(d["name"])
        if d["weight"] is None:
            violations.append(f"rubric: dimension {d['name']!r} has no weight — an unweighted criterion moves no score")
        else:
            total += d["weight"]
    if dimensions and abs(total - WEIGHT_SUM) > 1e-9:
        violations.append(f"rubric: weights sum to {total:g}, not {WEIGHT_SUM:g}")
    return version, margin, dimensions


def _rows(path: Path, violations: list):
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            violations.append(f"{path.name}:{i}: invalid JSON ({e.msg})")
            continue
        if not isinstance(obj, dict):
            violations.append(f"{path.name}:{i}: row is not an object")
            continue
        obj["_origin"] = f"{path.name}:{i}"
        rows.append(obj)
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="validate a forged rubric + scoring record")
    ap.add_argument("rubric", help="derived rubric (strict YAML subset)")
    ap.add_argument("scores", help="scoring record (JSONL)")
    args = ap.parse_args(argv)

    for name in ("rubric", "scores"):
        p = Path(getattr(args, name))
        if not p.is_file():
            print(f"REFUSING: {name} not found: {p}", file=sys.stderr)
            return 1

    violations: list = []
    try:
        rubric_text = Path(args.rubric).read_text(encoding="utf-8")
        rows = _rows(Path(args.scores), violations)
    except OSError as e:
        print(f"REFUSING: cannot read: {e}", file=sys.stderr)
        return 1

    version, margin, dimensions = parse_rubric(rubric_text, violations)
    if violations:
        for v in violations:
            print(f"VIOLATION: {v}", file=sys.stderr)
        return 2
    dim_weights = {d["name"]: d["weight"] for d in dimensions}

    artifacts: dict = {}
    findings: dict = {}
    for row in rows:
        origin = row["_origin"]
        kind = row.get("kind")
        if kind == "artifact":
            path = row.get("path")
            role = row.get("role")
            if not isinstance(path, str) or not path.strip():
                violations.append(f"{origin}: artifact row has no `path`")
                continue
            if path in artifacts:
                violations.append(f"{origin}: duplicate artifact row for {path!r}")
                continue
            if role not in ROLES:
                violations.append(f"{origin}: artifact role {role!r} is not exemplar|negative")
                continue
            twin = row.get("twin")
            if role == "negative" and (not isinstance(twin, str) or not twin.strip()):
                violations.append(f"{origin}: negative has no `twin` — nothing to compare it against")
                twin = None
            artifacts[path] = {"role": role, "twin": twin if role == "negative" else None,
                               "origin": origin}
        elif kind == "finding":
            path, dim = row.get("path"), row.get("dimension")
            met = row.get("met")
            finding = row.get("finding", "")
            if not isinstance(path, str) or not isinstance(dim, str):
                violations.append(f"{origin}: finding missing `path`/`dimension`")
                continue
            if dim not in dim_weights:
                violations.append(f"{origin}: finding cites dimension {dim!r} not in the rubric")
                continue
            if not isinstance(met, bool):
                violations.append(f"{origin}: finding for {dim!r} has non-boolean `met`")
                continue
            if not met and (not isinstance(finding, str) or not finding.strip()):
                violations.append(
                    f"{origin}: RED finding on {dim!r} for {path!r} is not localized — "
                    "name the artifact node and the check that goes RED, never an adjective")
            findings[(path, dim)] = met
        else:
            violations.append(f"{origin}: unknown row kind {kind!r}")

    exemplars = [p for p, a in artifacts.items() if a["role"] == "exemplar"]
    negatives = [(p, a) for p, a in artifacts.items() if a["role"] == "negative"]
    if not exemplars:
        violations.append("record scores no exemplar — a rubric with no positive anchor ranks nothing")

    for path, art in artifacts.items():
        if not Path(path).is_file():
            violations.append(f"{art['origin']}: exemplar/artifact path does not resolve: {path!r}")
        if art["twin"] is not None:
            if art["twin"] not in artifacts:
                violations.append(f"{art['origin']}: negative's twin {art['twin']!r} is not a scored artifact")
            elif Path(art["twin"]).is_file() and Path(path).is_file():
                if Path(path).read_bytes() == Path(art["twin"]).read_bytes():
                    violations.append(
                        f"{art['origin']}: negative {path!r} is byte-identical to its twin "
                        f"{art['twin']!r} — it is not actually degraded")

    for path in artifacts:
        for dim in dim_weights:
            if (path, dim) not in findings:
                violations.append(f"{artifacts[path]['origin']}: no finding for {path!r} on {dim!r}")

    if violations:
        for v in violations:
            print(f"VIOLATION: {v}", file=sys.stderr)
        return 2

    totals = {path: sum(w for d, w in dim_weights.items() if findings[(path, d)])
              for path in artifacts}

    ranking_bad = False
    for path, art in negatives:
        twin = art["twin"]
        gap = totals.get(twin, 0.0) - totals[path]
        if gap <= 0:
            ranking_bad = True
            print(f"VIOLATION: rubric fails to rank — twin {twin!r} scored {totals.get(twin, 0.0):g} "
                  f"vs degraded copy {path!r} at {totals[path]:g}; the rubric cannot tell a real "
                  "exemplar from a hollowed-out one", file=sys.stderr)
        elif gap < margin:
            ranking_bad = True
            print(f"VIOLATION: twin {twin!r} beats its degraded copy {path!r} by {gap:g}, "
                  f"below the declared margin {margin:g}", file=sys.stderr)
    if ranking_bad:
        return 2

    print(f"CLEAN: rubric v{version} · {len(dim_weights)} dimensions · "
          f"{len(exemplars)} exemplar(s), {len(negatives)} negative(s)")
    for path in sorted(totals):
        print(f"  {totals[path]:6.2f}  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
