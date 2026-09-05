"""A pointer to a section must land on a section that exists.

Deduplicating the docs replaced inline copies with pointers: the workflow says
`Follow "Method 1: Autobuild" in .../build-database.md` instead of restating the
command, and build-database.md links back to SKILL.md for the fresh-shell rule
rather than repeating it. That trade is only worth making if the pointers are real.

The repo validator resolves file paths, not section anchors, so a heading renamed by one
character leaves a pointer aimed at nothing and every check still green:

    [text](../SKILL.md#each-bash-call-is-a-fresh-shell)   markdown anchor

An earlier lane also parsed prose pointers (`Follow "Method 1" in x.md`) out of a build
workflow that was never committed. Across the 106 tracked docs that form matched once, and
the one match was a path inside backticks — a false positive. Dead code is worse than no
code here: it makes the file look like it checks more than it does.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPTS_DIR.parent
PLUGIN_ROOT = SKILL_ROOT.parent.parent
SKIP_DIRS = {".pytest_cache", "__pycache__", ".venv", ".ruff_cache"}



RUNTIME_ROOT_VAR = "SKILL_DIR"

HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
# [label](path.md#anchor) — only links carrying an anchor.
ANCHOR_LINK = re.compile(r"\[[^\]]*\]\(([^)#\s]+\.md)#([A-Za-z0-9_-]+)\)")



def _doc_files() -> list[Path]:
    return sorted(
        p
        for p in PLUGIN_ROOT.rglob("*")
        if p.suffix in {".md", ".js"}
        and not SKIP_DIRS.intersection(p.parts)
        and not p.name.startswith("test_")
    )


def _shipped_files() -> list[Path]:
    """Everything that ships and gets read by a machine, not just docs.

    The marketplace-path hazard lives in executable payloads — a `.py` script or `.sh` helper
    with a hardcoded `SKILL_DIR` breaks exactly like the workflow that started this. Scanning
    only `.md`/`.js` would let a bad literal land in the scripts themselves.
    """
    return sorted(
        p
        for p in PLUGIN_ROOT.rglob("*")
        if p.suffix in {".md", ".js", ".py", ".sh"}
        and not SKIP_DIRS.intersection(p.parts)
        and not p.name.startswith("test_")
    )


def _slug(heading: str) -> str:
    """GitHub's anchor rule: lowercase, drop punctuation, spaces to hyphens."""
    text = heading.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", "-", text).strip("-")


def _headings(path: Path) -> list[str]:
    return HEADING.findall(path.read_text(encoding="utf-8"))


def _resolve(target: str, source_file: Path) -> Path | None:
    """Turn a pointer's path into a real file, or None if it is not one we can check."""
    if "${" in target or "{baseDir}" in target:
        return None
    candidates = [Path(target), PLUGIN_ROOT.parent.parent / target]
    if not target.startswith("/"):
        candidates.insert(0, (source_file.parent / target).resolve())
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _collect() -> list[tuple[Path, str, Path, str]]:
    anchors: list[tuple[Path, str, Path, str]] = []
    for path in _doc_files():
        for target, anchor in ANCHOR_LINK.findall(path.read_text(encoding="utf-8")):
            resolved = _resolve(target, path)
            if resolved is not None:
                anchors.append((path, anchor, resolved, target))
    return anchors


ANCHORS = _collect()


def test_pointers_were_found() -> None:
    """Guard the guard: a scanner matching nothing would pass this file in silence."""
    assert ANCHORS, f"no anchored markdown links found under {PLUGIN_ROOT} — the scanner broke"


def test_no_shipped_file_hardcodes_a_marketplace_path() -> None:
    """A marketplace-relative skill path resolves only inside a checkout of the marketplace.

    A shipped build workflow once carried `SKILL_DIR = 'plugins/static-analysis/skills/codeql'`.
    Installed elsewhere, its first block sourced a `build_log.sh` that was not there, exited
    127, and every rung reported a build failure for a project that builds. Nothing else in this
    suite would notice it being written back down, because CI runs from the one repo where the
    literal does resolve. The file that shipped it was never committed; the hazard is not
    file-specific, so it is checked across every tracked markdown, workflow, script and helper.
    """
    offenders = []
    for path in _shipped_files():
        if path == Path(__file__).resolve():
            continue        # this check's own prose names the literal
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if "plugins/static-analysis" in line and not line.lstrip().startswith(("//", "#")):
                offenders.append(f"{path.relative_to(PLUGIN_ROOT)}: {line.strip()}")
    assert not offenders, (
        "shipped files name their own path inside a marketplace checkout, which only resolves "
        "when the run starts there:\n  " + "\n  ".join(offenders)
    )


@pytest.mark.parametrize(
    ("source", "anchor", "target", "raw"),
    ANCHORS,
    ids=[f"{s.relative_to(PLUGIN_ROOT)}->{raw}#{a}" for s, a, _, raw in ANCHORS],
)
def test_anchor_link_lands_on_a_heading(source: Path, anchor: str, target: Path, raw: str) -> None:
    slugs = {_slug(h) for h in _headings(target)}
    assert anchor in slugs, (
        f"{source.relative_to(PLUGIN_ROOT)} links to {raw}#{anchor}, but that file has no "
        f"heading with that anchor. Available: {', '.join(sorted(slugs))}"
    )



