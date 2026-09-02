#!/usr/bin/env python3
"""Enforce the immutable-surface contract mechanically.

A self-improving harness declares, in a YAML manifest, the exact surface an
optimizer may mutate (`mutable_surface`: its memory/config files) and the
machinery that is fixed by declaration (`immutable`: its own checker, gate,
patching procedure, validation loop). Any score delta after an improvement run
is only attributable to the mutable layer if nothing outside it moved. The
failure mode this closes is the improver that edits its own gate: the loop that
"passes" because it rewrote what passing means.

Two files, both given as argv:

  MANIFEST  — flat YAML subset: `harness_id:`, optional `root:`, a
              `mutable_surface:` list of globs, and an `immutable:` list of
              paths (files or directory prefixes) fixed by declaration.
  WRITES    — JSONL; one proposed write per line: {"path": "<path>"}.
              Paths are harness-relative, or root-prefixed when the manifest
              declares `root:`. Globs match across `/` (deny-by-default).

Verdict per write, in this order (the order is load-bearing):
  SELF_TOUCH     the write targets an immutable path — even when the declared
                 allowlist would also cover it. An optimizer widening its own
                 surface must not be able to swallow the gate: the immutable
                 declaration overrides the allowlist, always.
  PATH_ESCAPE    the RAW string matches an allowlist glob but the normalized
                 path does not (`memory/../runs/x.py`): traversal must not be
                 a side door into (or out of) the surface.
  OUTSIDE_SURFACE every other path no glob covers.

Exit codes (the honesty contract):
  0  every proposed write is inside the declared mutable surface
  1  usage / manifest-or-writes file not found (a refusal to judge)
  2  a contract violation: SURFACE_MISSING (no allowlist key — a missing
     allowlist is denial, not licence), SURFACE_EMPTY (allowlist declared with
     zero entries), MANIFEST_MALFORMED, WRITE_MALFORMED, SELF_TOUCH,
     PATH_ESCAPE, or OUTSIDE_SURFACE

Stdlib only. Reads only the two paths it is given. Writes nothing.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import posixpath
import re
import sys
from pathlib import Path


class _Usage(Exception):
    pass


class _Parser(argparse.ArgumentParser):
    """Usage errors are refusals (exit 1), never verdicts (exit 2)."""

    def error(self, message: str):  # pragma: no cover - argparse hook
        raise _Usage(message)



_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):(.*)$")
_ITEM_RE = re.compile(r"^\s+-\s+(.*)$")


def _unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1].strip()
    return v


def parse_manifest(path: Path):
    """Return (globs, immutables, root, problems). Structure errors are problems.

    Problems are tagged: ('MANIFEST_MALFORMED', msg) for structure errors,
    ('SURFACE_MISSING'|'SURFACE_EMPTY', msg) for allowlist-declaration errors.
    """
    problems: list = []
    lists: dict = {}
    scalars: dict = {}
    current = None
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].rstrip() if raw.lstrip().startswith("#") else raw.rstrip()
        if not line.strip():
            continue  # blank line: a list may continue after it
        m = _KEY_RE.match(line)
        if m and not line.startswith((" ", "\t")):
            key, val = m.group(1), _unquote(m.group(2))
            if val == "":
                current = key
                lists.setdefault(key, [])
            elif key in ("mutable_surface", "immutable"):
                if val == "[]":
                    lists.setdefault(key, [])
                    current = None
                else:
                    problems.append(("MANIFEST_MALFORMED",
                                     f"line {lineno}: '{key}' must be a list, not scalar {val!r}"))
                    current = None
            else:
                scalars[key] = val
                current = None
            continue
        m = _ITEM_RE.match(line)
        if m:
            if current is None:
                problems.append(("MANIFEST_MALFORMED",
                                 f"line {lineno}: list item outside any list key"))
            else:
                lists[current].append(_unquote(m.group(1)))
            continue
        problems.append(("MANIFEST_MALFORMED", f"line {lineno}: unparseable line {raw!r}"))

    if any(t == "MANIFEST_MALFORMED" for t, _ in problems):
        return [], [], "", problems

    if "mutable_surface" not in lists:
        problems.append(("SURFACE_MISSING",
                         "manifest declares no mutable_surface allowlist — "
                         "a missing allowlist denies everything, it is not a licence"))
        return [], [], "", problems
    globs = [posixpath.normpath(g) for g in lists["mutable_surface"] if g.strip()]
    if not globs:
        problems.append(("SURFACE_EMPTY",
                         "mutable_surface allowlist has zero entries — nothing is mutable"))
        return [], [], "", problems
    immutables = [posixpath.normpath(p) for p in lists.get("immutable", []) if p.strip()]
    root = posixpath.normpath(scalars.get("root", "")) if scalars.get("root") else ""
    return globs, immutables, root, problems


def _relativize(p: str, root: str):
    """Strip the declared root from a proposed path. Returns (rel, absolute_outside)."""
    p = p.replace("\\", "/")
    if p.startswith("/"):
        if root and p.startswith(root.rstrip("/") + "/"):
            return p[len(root.rstrip("/")) + 1:], False
        return None, True  # absolute path outside the harness root
    if root and (p == root or p.startswith(root.rstrip("/") + "/")):
        return p[len(root.rstrip("/")) + 1:] if p != root else "", False
    return p, False


def check_write(raw_path: str, globs, immutables, root: str):
    """Return None (allowed) or a (tag, detail) violation for one write."""
    naive_rel, abs_outside = _relativize(raw_path, root)
    if naive_rel is None or naive_rel == "":
        return ("OUTSIDE_SURFACE", f"{raw_path!r} is not inside the harness root {root!r}")
    candidate = posixpath.normpath(naive_rel)
    if candidate == ".." or candidate.startswith("../"):
        if any(fnmatch.fnmatchcase(naive_rel, g) for g in globs):
            return ("PATH_ESCAPE",
                    f"{raw_path!r} normalizes to {candidate!r}, outside the harness")
        return ("OUTSIDE_SURFACE", f"{raw_path!r} resolves outside the harness root")

    # 1. immutable machinery wins over any allowlist match
    for imp in immutables:
        if candidate == imp or candidate.startswith(imp + "/"):
            return ("SELF_TOUCH",
                    f"{raw_path!r} targets declared-immutable machinery {imp!r} "
                    f"(immutable overrides the allowlist)")
    # 2. allowlist membership, on the NORMALIZED path
    if any(fnmatch.fnmatchcase(candidate, g) for g in globs):
        return None
    # 3. normalized misses but the raw string matched a glob: traversal side door
    if any(fnmatch.fnmatchcase(naive_rel, g) for g in globs):
        return ("PATH_ESCAPE",
                f"{raw_path!r} matches the allowlist only before normalization "
                f"(normalized: {candidate!r})")
    return ("OUTSIDE_SURFACE", f"{raw_path!r} is under no mutable_surface glob")


def load_writes(path: Path):
    """Return (rows, problems). Each row is (lineno, path_str); problems are tagged."""
    rows, problems = [], []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            problems.append(("WRITE_MALFORMED", f"line {lineno}: not JSON ({exc.msg})"))
            continue
        if not isinstance(obj, dict):
            problems.append(("WRITE_MALFORMED", f"line {lineno}: not an object"))
            continue
        p = obj.get("path")
        if not isinstance(p, str) or not p.strip():
            problems.append(("WRITE_MALFORMED",
                             f"line {lineno}: missing or empty 'path'"))
            continue
        rows.append((lineno, p.strip()))
    return rows, problems


def main(argv=None) -> int:
    ap = _Parser(description="check proposed writes against a declared mutable surface")
    ap.add_argument("manifest", help="surface manifest YAML (mutable_surface allowlist)")
    ap.add_argument("writes", help="writes.jsonl — one {\"path\": ...} per proposed write")
    try:
        args = ap.parse_args(argv)
    except (_Usage, SystemExit) as exc:
        code = getattr(exc, "code", 2)
        print(f"usage: {exc}", file=sys.stderr)
        return 1 if isinstance(exc, _Usage) or code == 2 else code

    mp, wp = Path(args.manifest), Path(args.writes)
    for p, what in ((mp, "manifest"), (wp, "writes")):
        if not p.is_file():
            print(f"{what} file not found: {p}", file=sys.stderr)
            return 1

    violations: list = []
    globs, immutables, root, problems = parse_manifest(mp)
    violations.extend(problems)
    if violations:  # an untrustworthy allowlist cannot pass any write through
        for tag, msg in violations:
            print(f"VIOLATION {tag}: {msg}")
        print(f"\nsurface: {len(violations)} violation(s) — manifest rejected, "
              f"no write is judged")
        return 2

    writes, problems = load_writes(wp)
    violations.extend(problems)
    allowed = 0
    for lineno, raw in writes:
        found = check_write(raw, globs, immutables, root)
        if found:
            tag, detail = found
            violations.append((tag, f"line {lineno}: {detail}"))
        else:
            allowed += 1
            print(f"ALLOW {raw}")

    if violations:
        for tag, msg in violations:
            print(f"VIOLATION {tag}: {msg}")
        print(f"\nsurface: {len(violations)} violation(s); {allowed} of {len(writes)} "
              f"write(s) allowed")
        return 2
    print(f"OK {mp.name}: {allowed} write(s) inside the declared mutable surface")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
