"""Six-slot skill contract: the SKILL.md contract made checkable, not descriptive.

Mechanism (arXiv:2608.29596 — "Towards a Systems Foundation for Agentic Skills",
Badhe/Shah/Tiwari/Kathrotia, video Kbxg-_CXs78; boundary-condition leg from
arXiv:2608.11888 — "Agent Skills Can Be Harmful", video TA5QzGTQU_U): a skill is a
six-tuple s = <A activation, I instruction, C applicability, P permitted tools,
pi control flow, E expected effects> — an interface specification, not prose.
A SKILL.md is a lossy compression of ONE successful run; the boundary conditions
dropped by that compression (environment, runtime, dependency set, tuned
parameters, budget, data scale) are exactly what silently invalidates reuse in a
new configuration, so the applicability slot must carry them and the asset must
name what falls OUT of scope.

Declared fork (RISK row, matrix 2026-09-02): these required keys are ADDITIVE on
top of the de-facto anthropics/skills SKILL.md format and on top of RIG's quality
contract (outcome/done_when/great_example/quality_floor). `done_when` already is
the E slot; `allowed-tools` on commands already is the P slot. This module is the
first place A, C, a named P, pi and the boundary conditions become machine-check
rather than convention.

Three verdicts per violated slot — not one:
  ABSENT      the key is not in the frontmatter at all
  EMPTY       the key is present with no value (`key:`, `key: []`, `key: null`)
  MALFORMED   the key has content with the wrong shape (scalar where a list
              belongs, a boundary map missing fields, a one-step control flow)
Collapsing ABSENT and EMPTY into one word would hide the most common authoring
bug — the key typed and the value never filled in — behind the fiction of a key
nobody ever wrote. Unit tests pin the distinction; the asset's done_when greps
the two single-slot fixtures for the two different words.

Loader gate: `loadable(path)` returns False unless the A and C slots are
complete — the paper's rule that only alpha(x_t, g)=1-evaluable and
applicability-bounded skills may be loaded. A loader elsewhere may call it; this
module edits nothing.

Exit codes: 0 = zero findings across everything scanned; 1 = any finding (every
one named); 2 = usage/IO error (a named path does not exist or is not a
supported asset kind). stdlib only.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# --- verdicts -----------------------------------------------------------------
ABSENT = "ABSENT"
EMPTY = "EMPTY"
MALFORMED = "MALFORMED"
OK = "OK"

# The run boundary a SKILL.md silently compresses away (arXiv:2608.11888,
# capability 10): environment, runtime, dependency set, tuned parameters,
# budget, data scale. Each missing field maps to a named failure class there.
BOUNDARY_FIELDS = ("env", "runtime", "deps", "params", "budget", "scale")

SUPPORTED_SUFFIXES = (".md", ".markdown", ".yaml", ".yml")

_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_\-]*)\s*:(.*)$")


# --- parsed nodes -------------------------------------------------------------
class _Empty:
    """Present-but-valueless marker. Absence is a missing dict key, never this."""

    __slots__ = ()


EMPTY_NODE = _Empty()


class Scalar:
    __slots__ = ("text",)

    def __init__(self, text: str):
        self.text = text


class Items:
    __slots__ = ("items",)

    def __init__(self, items: list):
        self.items = items


class Fields:
    __slots__ = ("children",)

    def __init__(self, children: dict):
        self.children = children


def _kind_name(node) -> str:
    if isinstance(node, Scalar):
        return "scalar"
    if isinstance(node, Items):
        return "list"
    if isinstance(node, Fields):
        return "mapping"
    return "empty"


# --- minimal indentation-aware block parser (stdlib only) ----------------------
def _indent_of(raw: str) -> int:
    return len(raw) - len(raw.lstrip(" "))


def _unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def _parse_block(lines: list, i: int, indent: int):
    """Parse a block at column `indent`. Returns (node, next_index)."""
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines):
        return Fields({}), i
    if lines[i].strip().startswith("- "):
        items: list = []
        while i < len(lines):
            raw = lines[i]
            if not raw.strip():
                i += 1
                continue
            s = raw.strip()
            if _indent_of(raw) < indent or not s.startswith("- "):
                break
            items.append(_unquote(s[2:]))
            i += 1
            # deeper lines under an item fold into it (lists of small maps)
            while (i < len(lines) and lines[i].strip()
                   and _indent_of(lines[i]) > indent
                   and not lines[i].strip().startswith("- ")):
                items[-1] = items[-1] + " " + _unquote(lines[i].strip())
                i += 1
        return Items(items), i
    children: dict = {}
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.strip().startswith("#"):
            i += 1
            continue
        ind = _indent_of(raw)
        if ind < indent:
            break
        if ind > indent:  # orphan deep line — already-unknown nesting, skip
            i += 1
            continue
        m = _KEY.match(raw.strip())
        if not m:
            i += 1
            continue
        key, rest = m.group(1), m.group(2).strip()
        i += 1
        if rest in (">-", ">", "|", "|-", ">+"):
            parts: list = []
            while i < len(lines) and (not lines[i].strip()
                                      or _indent_of(lines[i]) > indent):
                if lines[i].strip():
                    parts.append(_unquote(lines[i].strip()))
                i += 1
            children[key] = Scalar(" ".join(parts)) if parts else EMPTY_NODE
        elif rest == "":
            j = i
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and _indent_of(lines[j]) > indent:
                child, i = _parse_block(lines, j, _indent_of(lines[j]))
                children[key] = child
            else:
                children[key] = EMPTY_NODE
        elif rest in ("~", "null", "Null", "NULL"):
            children[key] = EMPTY_NODE
        elif rest.startswith("[") and rest.endswith("]"):
            inner = rest[1:-1].strip()
            children[key] = (EMPTY_NODE if not inner
                             else Items([_unquote(t) for t in inner.split(",")
                                         if t.strip()]))
        elif rest.startswith("{") and rest.endswith("}"):
            inner = rest[1:-1].strip()
            if not inner:
                children[key] = EMPTY_NODE
            else:
                kids = {}
                for pair in inner.split(","):
                    if ":" in pair:
                        k2, v2 = pair.split(":", 1)
                        kids[k2.strip()] = Scalar(_unquote(v2))
                children[key] = Fields(kids)
        else:
            children[key] = Scalar(_unquote(rest))
    return Fields(children), i


def parse_doc(text: str, name: str = "asset.md") -> Fields:
    """Parse one asset body into a top-level Fields node.

    `.md`/`.markdown`: the leading --- fence block; no fence ⇒ no slots
    (every slot reports ABSENT — an unfrontmattered file is not lighter, it is
    silent). `.yaml`/`.yml`: the whole document.
    """
    low = name.lower()
    if low.endswith(".yaml") or low.endswith(".yml"):
        node, _ = _parse_block(text.splitlines(), 0, 0)
        return node if isinstance(node, Fields) else Fields({})
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return Fields({})
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            end = i
            break
    if end is None:
        return Fields({})
    node, _ = _parse_block(lines[1:end], 0, 0)
    return node if isinstance(node, Fields) else Fields({})


# --- the six slots + boundary list, with required shapes -----------------------
def _scalar_rule(node):
    if isinstance(node, Scalar):
        return OK, "predicate present"
    return MALFORMED, f"must be one non-null string, found {_kind_name(node)}"


def _boundary_map_rule(node):
    if not isinstance(node, Fields):
        return MALFORMED, ("must be a mapping carrying the run boundary fields "
                           f"({', '.join(BOUNDARY_FIELDS)}), found {_kind_name(node)}")
    missing = [f for f in BOUNDARY_FIELDS
               if f not in node.children
               or not isinstance(node.children[f], Scalar)
               or not node.children[f].text.strip()]
    if missing:
        return MALFORMED, ("incomplete boundary fields: "
                           + ", ".join(missing))
    return OK, "run boundary declared"


def _list_rule(what: str, min_items: int = 1):
    def rule(node):
        if not isinstance(node, Items):
            return MALFORMED, f"must be a block list of {what}, found {_kind_name(node)}"
        blank = [t for t in node.items if not t.strip()]
        if blank:
            return MALFORMED, f"list of {what} contains a blank item"
        if len(node.items) < min_items:
            if min_items == 2:
                return MALFORMED, "one step is not a control flow"
            return MALFORMED, f"list of {what} has no items"
        return OK, "declared"
    return rule


SLOTS = (
    ("activation", "A", "activation condition: when state+goal make this skill fire",
     _scalar_rule),
    ("instruction", "I", "instruction: what to do when it fires", _scalar_rule),
    ("applies_when", "C", "applicability precondition carrying the run boundary fields",
     _boundary_map_rule),
    ("permissions", "P", "permitted tools the skill may use", _list_rule("tool tokens")),
    ("flow", "pi", "control flow: the ordered steps between pre- and post-state",
     _list_rule("steps", min_items=2)),
    ("done_when", "E", "expected effects: the machine-checkable post-state",
     _list_rule("effect checks")),
    ("out_of_scope", "OUT", "boundary: what this skill must NOT do / what falls outside it",
     _list_rule("out-of-scope statements")),
)


def slot_verdicts(node: Fields) -> list:
    """One verdict row per contract slot for a parsed asset."""
    children = node.children if isinstance(node, Fields) else {}
    rows = []
    for slot, letter, _desc, rule in SLOTS:
        present = slot in children
        if not present:
            verdict, detail = ABSENT, "key not in frontmatter"
        else:
            value = children[slot]
            if isinstance(value, _Empty):
                verdict, detail = EMPTY, "key present with no value"
            else:
                verdict, detail = rule(value)
        rows.append({"slot": slot, "letter": letter,
                     "verdict": verdict, "detail": detail})
    return rows


def findings_for_text(name: str, text: str) -> list:
    bad = [r for r in slot_verdicts(parse_doc(text, name)) if r["verdict"] != OK]
    return [{"path": name, **r} for r in bad]


def findings_for_path(path) -> list:
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="replace")
    return findings_for_text(str(p), text)


def _iter_assets(root: Path):
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES \
                and not any(part.startswith(".") for part in p.parts):
            yield p


def findings_for_tree(root) -> list:
    out = []
    for p in _iter_assets(Path(root)):
        out.extend(findings_for_path(p))
    return out


def loadable(path) -> tuple:
    """Loader gate: an asset is loadable only when A and C are complete.

    Returns (ok, blockers) with blockers like ["activation:ABSENT",
    "applies_when:MALFORMED"]. The paper's loading rule: a skill without an
    evaluable activation predicate or without declared applicability may not be
    loaded, because neither the router nor the reader can tell it apart from one
    that silently does the wrong thing here.
    """
    verdicts = {r["slot"]: r["verdict"] for r in slot_verdicts(parse_doc(
        Path(path).read_text(encoding="utf-8", errors="replace"), str(path)))}
    blockers = [f"{s}:{verdicts[s]}" for s in ("activation", "applies_when")
                if verdicts.get(s) != OK]
    return (not blockers, blockers)


# --- CLI ------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="python3 -m rig_capabilities.skill_contract",
        description="Check the six-slot skill contract (A, I, C, P, pi, E) plus "
                    "the boundary list (out_of_scope) on SKILL.md / harness YAML "
                    "assets. Verdicts: ABSENT / EMPTY / MALFORMED. "
                    "Exit 0 only at zero findings.")
    ap.add_argument("paths", nargs="+",
                    help="asset files or directories (dirs scanned recursively)")
    ap.add_argument("--json", action="store_true", help="emit findings as JSON")
    args = ap.parse_args(argv)

    files: list = []
    for raw in args.paths:
        p = Path(raw)
        if p.is_dir():
            files.extend(_iter_assets(p))
            continue
        if not p.exists():
            print(f"skill_contract: no such path: {raw}", file=sys.stderr)
            return 2
        if p.suffix.lower() not in SUPPORTED_SUFFIXES:
            print(f"skill_contract: unsupported asset kind: {raw}", file=sys.stderr)
            return 2
        files.append(p)

    findings: list = []
    for f in files:
        findings.extend(findings_for_path(f))

    if args.json:
        import json
        print(json.dumps(findings, indent=1))
    else:
        for x in findings:
            print(f"{x['path']}: {x['slot']} ({x['letter']}): "
                  f"{x['verdict']}: {x['detail']}")
        n_files = len(files)
        verdict_of = {}
        for x in findings:
            verdict_of[x["verdict"]] = verdict_of.get(x["verdict"], 0) + 1
        tally = ", ".join(f"{k}={v}" for k, v in sorted(verdict_of.items())) or "none"
        print(f"skill_contract: {len(findings)} finding(s) across {n_files} "
              f"file(s) [{tally}]")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
