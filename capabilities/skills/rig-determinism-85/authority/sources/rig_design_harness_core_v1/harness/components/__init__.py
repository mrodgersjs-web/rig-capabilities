from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from harness.packet import Proposal, Report

_TEMPLATE_DIR = Path(__file__).resolve().parents[2] / "templates"
_ENV = Environment(
    loader=FileSystemLoader(_TEMPLATE_DIR),
    undefined=StrictUndefined,
    autoescape=False,
    keep_trailing_newline=True,
)
_HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
_COMPONENTS = {"context", "tools", "runtime", "orchestration", "evaluation"}


def render_template(name: str, destination: Path, **values: Any) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(_ENV.get_template(name).render(**values))
    return destination


def report(findings: list[str]) -> Report:
    return Report(ok=not findings, findings=findings)


def validate_python(path: Path, findings: list[str]) -> None:
    try:
        ast.parse(path.read_text(), filename=str(path))
    except (OSError, SyntaxError) as exc:
        findings.append(f"{path.name}:python:{exc}")


def _component_root(files: list[Path], component: str) -> Path:
    for parent in files[0].parents:
        if parent.name == component:
            return parent
    raise ValueError(f"files are not inside a {component} component")


def _diff_path(raw: str) -> str:
    path = raw.split("\t", 1)[0].strip()
    if path == "/dev/null":
        raise ValueError("component mutation cannot create or delete files")
    return path[2:] if path.startswith(("a/", "b/")) else path


def _relative_target(raw: str, component: str) -> Path:
    path = Path(_diff_path(raw))
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"diff touches file outside {component} component: {raw}")
    if path.parts and path.parts[0] in _COMPONENTS:
        if path.parts[0] != component:
            raise ValueError(f"diff touches file outside {component} component: {raw}")
        path = Path(*path.parts[1:])
    return path


def _apply_hunks(original: str, diff_lines: list[str]) -> str:
    source = original.splitlines(keepends=True)
    output: list[str] = []
    source_index = 0
    index = 0
    while index < len(diff_lines):
        match = _HUNK.match(diff_lines[index])
        if not match:
            raise ValueError(f"invalid unified diff hunk: {diff_lines[index].rstrip()}")
        old_start = int(match.group(1))
        target_index = old_start - 1
        if target_index < source_index:
            raise ValueError("overlapping unified diff hunks")
        output.extend(source[source_index:target_index])
        source_index = target_index
        index += 1
        while index < len(diff_lines) and not diff_lines[index].startswith("@@ "):
            line = diff_lines[index]
            if line.startswith("\\ No newline at end of file"):
                index += 1
                continue
            if not line or line[0] not in " +-":
                raise ValueError(f"invalid unified diff line: {line.rstrip()}")
            body = line[1:]
            if line[0] == " ":
                if source_index >= len(source) or source[source_index] != body:
                    raise ValueError("unified diff context does not match target")
                output.append(source[source_index])
                source_index += 1
            elif line[0] == "-":
                if source_index >= len(source) or source[source_index] != body:
                    raise ValueError("unified diff deletion does not match target")
                source_index += 1
            else:
                output.append(body)
            index += 1
    output.extend(source[source_index:])
    return "".join(output)


def apply_mutation(files: list[Path], proposal: Proposal, component: str) -> list[Path]:
    if proposal.component != component:
        raise ValueError(f"proposal component {proposal.component!r} does not match {component!r}")
    if not files:
        raise ValueError("cannot mutate an empty component")
    root = _component_root(files, component)
    allowed = {path.resolve() for path in files}
    lines = proposal.diff.splitlines(keepends=True)
    changes: list[tuple[Path, list[str]]] = []
    index = 0
    while index < len(lines):
        if not lines[index].startswith("--- "):
            index += 1
            continue
        old_path = _relative_target(lines[index][4:], component)
        index += 1
        if index >= len(lines) or not lines[index].startswith("+++ "):
            raise ValueError("unified diff is missing +++ path")
        new_path = _relative_target(lines[index][4:], component)
        if old_path != new_path:
            raise ValueError("component mutation cannot rename files")
        target = (root / new_path).resolve()
        if target not in allowed:
            raise ValueError(f"diff touches file outside {component} component: {new_path}")
        index += 1
        hunks: list[str] = []
        while index < len(lines) and not lines[index].startswith("--- "):
            hunks.append(lines[index])
            index += 1
        changes.append((target, hunks))
    if not changes:
        raise ValueError("proposal.diff contains no unified diff file changes")
    rendered = [(target, _apply_hunks(target.read_text(), hunks)) for target, hunks in changes]
    for target, content in rendered:
        target.write_text(content)
    return files
