"""External writing-tool integrations.

Pulled from the `awesome-writing-tools` list
(https://github.com/Guido1Alessandro1Trevisan/awesome-writing-tools).

Two surfaces:

1. ``TOOLS`` / ``catalog()`` — an honest registry of every tool on the list,
   classified by kind and whether it can run locally without credentials.
2. Live wrappers for the three open-source prose linters that *can* run
   headlessly — Alex.js, write-good and markdownlint — normalised into a
   common ``Finding`` shape and aggregated by ``analyze()``.

Design constraints (match the rest of ``rig_comm``):
- stdlib only; the linters are Node CLIs resolved at call time via ``npx``.
- Never raise on a missing/broken tool: return ``ToolResult(available/ran)``.
- The deterministic offline ``core.evaluate`` is untouched — these subprocess
  linters are an optional, advisory layer, not part of the ship gate.

SaaS / API-key / desktop-app tools on the list are catalogued honestly with
``runnable=False``; there is no fake wrapper that pretends to call Grammarly.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence

__all__ = [
    "WritingTool",
    "Finding",
    "ToolResult",
    "TOOLS",
    "WIRED_TOOLS",
    "catalog",
    "run_alex",
    "run_write_good",
    "run_markdownlint",
    "analyze",
]


# --------------------------------------------------------------------------- #
# Catalog
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class WritingTool:
    name: str
    url: str
    category: str            # readability | inclusivity | grammar | style | markdown | ...
    kind: str                # npm-cli | python-cli | saas | web-api | desktop-app | claude-plugin | reference
    runnable: bool           # can it run locally, headless, without credentials?
    checks: str              # one line: what it catches / does
    package: str = ""        # install target (npm/pip name) when runnable
    install: str = ""        # exact install command when runnable
    wired: bool = False      # True => this module ships a live wrapper
    audit: str = ""          # link-check result (HTTP status / redirect / rename), probed 2026-09-16

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "url": self.url,
            "category": self.category,
            "kind": self.kind,
            "runnable": self.runnable,
            "wired": self.wired,
            "checks": self.checks,
            "package": self.package,
            "install": self.install,
            "audit": self.audit,
        }


# Every entry on awesome-writing-tools (markdownlint-cli listed as its own row,
# as in the source). Order follows the source README.
TOOLS: List[WritingTool] = [
    WritingTool("Alex.js", "http://alexjs.com/", "inclusivity", "npm-cli", True,
                "Catches insensitive, inconsiderate phrasing (gender/race/religion/etc.)",
                package="alex", install="npm i -g alex", wired=True,
                audit="200; http->https to alexjs.com"),
    WritingTool("Atomic Reach", "https://www.atomicreach.com/", "content-optimization", "saas", False,
                "Was predictive audience-aware content SaaS; site now redirects to RAD Intel "
                "(radintel.ai) — original Atomic Reach product defunct/rebranded",
                audit="200 but REDIRECTS to https://www.radintel.ai/ (RAD Intel); original product gone"),
    WritingTool("The Chicago Manual of Style", "http://www.chicagomanualofstyle.org/home.html", "style-guide", "reference", False,
                "Authoritative style/usage/grammar reference (subscription)",
                audit="200"),
    WritingTool("Chisel Editor", "https://egonschiele.github.io/chisel-docs/", "editor", "desktop-app", False,
                "AI-powered book/story writing editor",
                audit="200"),
    WritingTool("CiteMe", "https://citeme.app/", "citation", "saas", False,
                "AI academic citation generator, 40+ styles (SaaS + extensions)",
                audit="200"),
    WritingTool("Cliche Finder", "http://cliche.theinfo.org/", "style", "web-api", False,
                "Highlights cliches in prose (hosted web app)",
                audit="200 (still live)"),
    WritingTool("Contributor Covenant", "https://www.contributor-covenant.org/", "code-of-conduct", "reference", False,
                "Open-source code-of-conduct pledge template",
                audit="200"),
    WritingTool("Danger", "https://github.com/danger/danger", "code-review", "npm-cli", False,
                "Formalises pull-request etiquette in CI (needs a repo + CI context)",
                package="danger", install="npm i -g danger",
                audit="200"),
    WritingTool("Grammarly", "https://www.grammarly.com/", "grammar", "saas", False,
                "Grammar/clarity/plagiarism checker (paid SaaS, no headless API)",
                audit="200"),
    WritingTool("The Hemingway Editor", "http://www.hemingwayapp.com/", "readability", "web-api", False,
                "Flags adverbs, passive voice, complex sentences (web/desktop app, no CLI)",
                audit="200; http->https to hemingwayapp.com"),
    WritingTool("Inkwell", "https://github.com/4worlds4w-svg/inkwell", "editor", "desktop-app", False,
                "Local Markdown editor (Rust/Tauri): split view, focus/typewriter modes",
                audit="200"),
    WritingTool("JigSaw", "https://jigsaw.google.com/projects/", "moderation", "reference", False,
                "Google incubator countering extremism/censorship (project hub)",
                audit="200; redirects to jigsaw.google"),
    WritingTool("Kindling", "https://kindlingwriter.com", "editor", "desktop-app", False,
                "Open-source novel writing app bridging outline and draft (Rust/Tauri)",
                audit="200"),
    WritingTool("LanguageCheck", "https://github.com/JohannesBuchner/languagecheck", "academic", "python-cli", False,
                "Analyses LaTeX scientific papers (tense, a/an, spelling); needs LaTeX source",
                package="languagecheck", install="pip install languagecheck",
                audit="200"),
    WritingTool("Markdownlint", "https://github.com/markdownlint/markdownlint", "markdown", "npm-cli", True,
                "Flags Markdown style issues (Ruby lib; run via markdownlint-cli)",
                package="markdownlint-cli", install="npm i -g markdownlint-cli", wired=True,
                audit="200"),
    WritingTool("Markdownlint-cli", "https://github.com/igorshubovych/markdownlint-cli", "markdown", "npm-cli", True,
                "Command-line interface for markdownlint",
                package="markdownlint-cli", install="npm i -g markdownlint-cli", wired=True,
                audit="200"),
    WritingTool("Perspective API", "https://www.perspectiveapi.com/", "moderation", "web-api", False,
                "ML toxicity/impact scoring for comments (needs Google API key)",
                package="", install="requires GOOGLE Perspective API key",
                audit="200"),
    WritingTool("ProWritingAid", "https://prowritingaid.com/", "style", "saas", False,
                "Style/grammar suggestions: repetition, vague wording, passive voice (paid SaaS)",
                audit="200"),
    WritingTool("Readable.io", "https://readable.io/", "readability", "saas", False,
                "Readability analysis and improvement suggestions (paid SaaS)",
                audit="200; redirects to readable.com"),
    WritingTool("Taskade", "https://taskade.com/", "collaboration", "saas", False,
                "Real-time collaborative outlines/task lists (SaaS)",
                audit="200; redirects to www.taskade.com"),
    WritingTool("toprank", "https://github.com/nowork-studio/toprank", "seo", "claude-plugin", False,
                "Claude Code plugin: E-E-A-T SEO writer, keyword research, CMS publish (needs GSC + CMS creds); "
                "repo renamed to nowork-studio/notfair-plugin",
                package="toprank", install="Claude Code plugin",
                audit="200 but repo renamed/redirects to nowork-studio/notfair-plugin"),
    WritingTool("Weallbehave", "https://github.com/wealljs/weallbehave", "code-of-conduct", "npm-cli", False,
                "CLI to generate/update CODE_OF_CONDUCT.md (project scaffolder, not a prose check)",
                package="weallbehave", install="npm i -g weallbehave",
                audit="200"),
    WritingTool("Write Good", "https://github.com/btford/write-good", "style", "npm-cli", True,
                "Prose linter: passive voice, weasel words, wordy phrases, cliches",
                package="write-good", install="npm i -g write-good", wired=True,
                audit="200"),
]


def catalog() -> List[Dict[str, object]]:
    """Return the full tool registry as plain dicts."""
    return [t.to_dict() for t in TOOLS]


# --------------------------------------------------------------------------- #
# Live linter wrappers
# --------------------------------------------------------------------------- #
@dataclass
class Finding:
    tool: str
    severity: str            # error | warning | info
    message: str
    rule: str = ""
    line: Optional[int] = None
    column: Optional[int] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "tool": self.tool,
            "severity": self.severity,
            "message": self.message,
            "rule": self.rule,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class ToolResult:
    tool: str
    available: bool          # a way to invoke the tool exists (binary or npx)
    ran: bool                # the subprocess executed and produced a parseable result
    findings: List[Finding] = field(default_factory=list)
    error: Optional[str] = None
    raw: str = ""

    def to_dict(self) -> Dict[str, object]:
        return {
            "tool": self.tool,
            "available": self.available,
            "ran": self.ran,
            "count": len(self.findings),
            "findings": [f.to_dict() for f in self.findings],
            "error": self.error,
        }


# Pinned npm versions for the ``npx`` fallback, so two machines resolve the same
# linter instead of whatever "latest" happens to be. Bump deliberately.
_PINNED = {
    "alex": "alex@11.0.1",
    "write-good": "write-good@1.0.8",
    "markdownlint-cli": "markdownlint-cli@0.49.1",
}


def _resolve_argv(binary: str, npx_pkg: str) -> Optional[List[str]]:
    """Prefer a globally installed binary, else a pinned ``npx`` fallback.

    ``binary`` is the executable name (e.g. ``markdownlint``); ``npx_pkg`` is the
    npm package (e.g. ``markdownlint-cli``) — the two differ. Set
    ``RIG_WRITING_TOOLS_NO_NPX=1`` to forbid the nondeterministic auto-install.
    """
    local = shutil.which(binary)
    if local:
        return [local]
    if os.environ.get("RIG_WRITING_TOOLS_NO_NPX"):
        return None
    if shutil.which("npx"):
        return ["npx", "--yes", _PINNED.get(npx_pkg, npx_pkg)]
    return None


def _invoke(argv: Sequence[str], input_text: Optional[str], timeout: float):
    """Run a subprocess. Returns (rc, stdout, stderr) or None if unlaunchable."""
    try:
        proc = subprocess.run(
            list(argv),
            input=input_text,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or ""
        err = (exc.stderr or "") + "\n[timeout]"
        if isinstance(out, bytes):
            out = out.decode("utf-8", "replace")
        if isinstance(err, bytes):
            err = err.decode("utf-8", "replace")
        return (124, out, err)
    return (proc.returncode, proc.stdout, proc.stderr)


_TIMEOUT_RC = 124


def _run_failed(rc: int, has_findings: bool) -> bool:
    """The tool did not produce a trustworthy complete result.

    A timeout (rc 124) is always a failure — even with partial findings, the
    analysis was truncated. Otherwise, a nonzero exit with no parseable findings
    (npx bootstrap failure, crash) is a failure. Clean input legitimately exits 0
    with no findings.
    """
    if rc == _TIMEOUT_RC:
        return True
    return (not has_findings) and rc != 0


def _result(tool: str, binary: str, npx_pkg: str, parser, input_text: Optional[str],
            file_arg: Optional[str], timeout: float) -> ToolResult:
    argv = _resolve_argv(binary, npx_pkg)
    if argv is None:
        return ToolResult(tool=tool, available=False, ran=False,
                          error=f"`{binary}` not found and npx fallback unavailable")
    if file_arg is not None:
        argv = list(argv) + [file_arg]
    res = _invoke(argv, input_text, timeout)
    if res is None:
        return ToolResult(tool=tool, available=False, ran=False,
                          error=f"failed to launch `{binary}`")
    rc, out, err = res
    combined = f"{out}\n{err}"
    findings = parser(combined)
    if _run_failed(rc, bool(findings)):
        return ToolResult(tool=tool, available=True, ran=False,
                          error=(combined.strip() or f"exit {rc}")[:800], raw=combined)
    return ToolResult(tool=tool, available=True, ran=True,
                      findings=findings, raw=combined)


# --- parsers (tested against real captured output) ------------------------- #
_ALEX_RE = re.compile(
    r"^\s*(?P<line>\d+):(?P<col>\d+)-\d+:\d+\s+(?P<sev>warning|error)\s+(?P<rest>.+\S)\s*$"
)


def _parse_alex(text: str) -> List[Finding]:
    findings: List[Finding] = []
    for line in text.splitlines():
        m = _ALEX_RE.match(line)
        if not m:
            continue
        parts = re.split(r"\s{2,}", m.group("rest").strip())
        message = parts[0]
        rule = parts[-1] if len(parts) > 1 and parts[-1].startswith("retext") else "alex"
        findings.append(Finding(
            tool="alex", severity=m.group("sev"), message=message, rule=rule,
            line=int(m.group("line")), column=int(m.group("col")),
        ))
    return findings


_WG_RE = re.compile(
    r'^"(?P<phrase>.+?)" (?P<reason>.+) on line (?P<line>\d+) at column (?P<col>\d+)$'
)


def _parse_write_good(text: str) -> List[Finding]:
    findings: List[Finding] = []
    for line in text.splitlines():
        m = _WG_RE.match(line.strip())
        if not m:
            continue
        findings.append(Finding(
            tool="write-good", severity="warning",
            message=f'"{m.group("phrase")}" {m.group("reason")}',
            rule="write-good",
            line=int(m.group("line")), column=int(m.group("col")),
        ))
    return findings


_ML_RE = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+)(?::(?P<col>\d+))?\s+(?P<sev>\w+)\s+"
    r"(?P<rule>MD\d+/\S+)\s+(?P<msg>.*)$"
)


def _parse_markdownlint(text: str) -> List[Finding]:
    findings: List[Finding] = []
    for line in text.splitlines():
        m = _ML_RE.match(line.strip())
        if not m:
            continue
        col = m.group("col")
        findings.append(Finding(
            tool="markdownlint", severity=m.group("sev"),
            message=m.group("msg").strip(), rule=m.group("rule"),
            line=int(m.group("line")), column=int(col) if col else None,
        ))
    return findings


def _write_temp(text: str, suffix: str) -> str:
    fd = tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8")
    try:
        fd.write(text)
    finally:
        fd.close()
    return fd.name


def run_alex(text: str, timeout: float = 90.0) -> ToolResult:
    """Run Alex.js over ``text`` via stdin."""
    return _result("alex", "alex", "alex", _parse_alex, input_text=text,
                   file_arg="--stdin", timeout=timeout)


def run_write_good(text: str, timeout: float = 90.0) -> ToolResult:
    """Run write-good over ``text`` (needs a file argument)."""
    path = _write_temp(text, ".txt")
    try:
        return _result("write-good", "write-good", "write-good", _parse_write_good,
                       input_text=None, file_arg=path, timeout=timeout)
    finally:
        _safe_unlink(path)


def run_markdownlint(text: str, timeout: float = 90.0) -> ToolResult:
    """Run markdownlint-cli over ``text`` (needs a .md file argument)."""
    path = _write_temp(text, ".md")
    try:
        return _result("markdownlint", "markdownlint", "markdownlint-cli", _parse_markdownlint,
                       input_text=None, file_arg=path, timeout=timeout)
    finally:
        _safe_unlink(path)


def _safe_unlink(path: str) -> None:
    try:
        Path(path).unlink()
    except OSError:
        pass


_RUNNERS = {
    "alex": run_alex,
    "write-good": run_write_good,
    "markdownlint": run_markdownlint,
}

# Names of tools that have a live wrapper in this module.
WIRED_TOOLS = tuple(_RUNNERS)


def analyze(text: str, tools: Optional[Sequence[str]] = None,
            timeout: float = 90.0) -> Dict[str, ToolResult]:
    """Run the wired linters over ``text`` and return {tool: ToolResult}.

    ``tools`` restricts the run to a subset of ``WIRED_TOOLS``. Missing tools
    degrade to ``ToolResult(available=False)`` — this never raises.
    """
    selected = list(tools) if tools else list(WIRED_TOOLS)
    out: Dict[str, ToolResult] = {}
    for name in selected:
        runner = _RUNNERS.get(name)
        if runner is None:
            out[name] = ToolResult(tool=name, available=False, ran=False,
                                   error=f"no wired wrapper for `{name}`")
            continue
        out[name] = runner(text, timeout=timeout)
    return out
