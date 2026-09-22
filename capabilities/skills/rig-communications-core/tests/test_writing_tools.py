import json

from rig_comm.integrations import writing_tools as wt


# Real captured output from the three linters (see references/WRITING_TOOLS.md).
ALEX_STDERR = """<stdin>
   1:5-1:11  warning  `master` may be insensitive, use `primary`, `lead`, `hub`, `reference` instead                   master     retext-equality
  1:12-1:21  warning  `whitelist` may be insensitive, use `passlist`, `alrightlist`, `safelist`, `allow list` instead  whitelist  retext-equality

\u26a0 2 warnings
"""

WRITE_GOOD_STDOUT = """In /tmp/x.txt
=============
So the report was written by John. There are many issues that are very important
^^
"So" adds no meaning on line 1 at column 0
-------------
"was written" may be passive voice on line 1 at column 14
-------------
"There are" is unnecessary verbiage on line 1 at column 35
-------------
"many" is a weasel word and can weaken meaning on line 1 at column 45
-------------
"very" is a weasel word and can weaken meaning on line 1 at column 66
"""

MARKDOWNLINT_STDERR = """/tmp/x.md:1 error MD022/blanks-around-headings Headings should be surrounded by blank lines [Expected: 1; Actual: 0; Below] [Context: "# Title"]
/tmp/x.md:2:1 error MD018/no-missing-space-atx No space after hash on atx style heading [Context: "#Bad heading"]
/tmp/x.md:4:31 error MD009/no-trailing-spaces Trailing spaces [Expected: 0 or 2; Actual: 3]
"""


# --- catalog --------------------------------------------------------------- #
EXPECTED_NAMES = {
    "Alex.js", "Atomic Reach", "The Chicago Manual of Style", "Chisel Editor",
    "CiteMe", "Cliche Finder", "Contributor Covenant", "Danger", "Grammarly",
    "The Hemingway Editor", "Inkwell", "JigSaw", "Kindling", "LanguageCheck",
    "Markdownlint", "Markdownlint-cli", "Perspective API", "ProWritingAid",
    "Readable.io", "Taskade", "toprank", "Weallbehave", "Write Good",
}


def test_catalog_covers_every_awesome_tool():
    names = {t.name for t in wt.TOOLS}
    assert names == EXPECTED_NAMES
    assert len(wt.TOOLS) == len(EXPECTED_NAMES)  # no duplicate rows


def test_catalog_entries_well_formed():
    for t in wt.TOOLS:
        assert t.name and t.url.startswith(("http://", "https://"))
        assert t.category and t.kind and t.checks
        assert isinstance(t.runnable, bool)
        assert t.audit, f"{t.name} missing link-audit evidence"
        if t.wired:
            assert t.runnable, f"{t.name} wired but not runnable"
            assert t.package and t.install


def test_catalog_is_json_serializable():
    json.dumps(wt.catalog())  # CLI --list path


def test_wired_tools_match_runners():
    assert wt.WIRED_TOOLS == ("alex", "write-good", "markdownlint")


# --- parsers (against real tool output) ------------------------------------ #
def test_parse_alex():
    findings = wt._parse_alex(ALEX_STDERR)
    assert len(findings) == 2
    first = findings[0]
    assert first.tool == "alex"
    assert first.severity == "warning"
    assert first.line == 1 and first.column == 5
    assert first.rule == "retext-equality"
    assert "master" in first.message
    assert "may be insensitive" in first.message
    # summary line "2 warnings" must NOT parse as a finding
    assert all("warnings" not in f.message.split(" ", 1)[0] for f in findings)


def test_parse_write_good():
    findings = wt._parse_write_good(WRITE_GOOD_STDOUT)
    assert len(findings) == 5
    passive = [f for f in findings if "passive voice" in f.message]
    assert passive and passive[0].line == 1 and passive[0].column == 14
    assert all(f.tool == "write-good" for f in findings)


def test_parse_markdownlint():
    findings = wt._parse_markdownlint(MARKDOWNLINT_STDERR)
    assert len(findings) == 3
    rules = {f.rule for f in findings}
    assert {"MD022/blanks-around-headings", "MD018/no-missing-space-atx",
            "MD009/no-trailing-spaces"} == rules
    md018 = [f for f in findings if f.rule == "MD018/no-missing-space-atx"][0]
    assert md018.line == 2 and md018.column == 1 and md018.severity == "error"


def test_parsers_ignore_noise():
    assert wt._parse_alex("npm warn deprecated foo\nrandom text\n") == []
    assert wt._parse_write_good("=============\nheader only\n") == []
    assert wt._parse_markdownlint("no findings here\n") == []


# --- graceful degradation (no subprocess) ---------------------------------- #
def test_analyze_degrades_when_nothing_on_path(monkeypatch):
    monkeypatch.setattr(wt.shutil, "which", lambda _name: None)
    results = wt.analyze("The master whitelist.")
    assert set(results) == set(wt.WIRED_TOOLS)
    for res in results.values():
        assert res.available is False
        assert res.ran is False
        assert res.findings == []
        assert res.error  # explains why


def test_analyze_unknown_tool_is_reported_not_raised():
    results = wt.analyze("hi", tools=["bogus"])
    assert results["bogus"].available is False
    assert "no wired wrapper" in results["bogus"].error


def test_npx_failure_marks_not_ran(monkeypatch):
    # simulate npx bootstrap failure: non-zero rc, no findings, npm error text
    monkeypatch.setattr(wt, "_resolve_argv", lambda _b, _p: ["npx", "--yes", "alex", "--stdin"])
    monkeypatch.setattr(wt, "_invoke",
                        lambda _argv, _input, _timeout: (1, "", "npm error could not determine executable to run"))
    res = wt.run_alex("text")
    assert res.available is True
    assert res.ran is False
    assert res.findings == []
    assert res.error


def test_every_tool_carries_audit_evidence():
    assert all(t.audit for t in wt.TOOLS)
    assert all("audit" in d for d in wt.catalog())


def test_resolver_prefers_binary_then_pinned_npx(monkeypatch):
    # global binary present -> use it directly (markdownlint binary != package name)
    monkeypatch.setattr(wt.shutil, "which",
                        lambda n: "/usr/local/bin/markdownlint" if n == "markdownlint" else None)
    assert wt._resolve_argv("markdownlint", "markdownlint-cli") == ["/usr/local/bin/markdownlint"]
    # binary absent, npx present -> pinned PACKAGE, not the binary name
    monkeypatch.setattr(wt.shutil, "which",
                        lambda n: "/usr/bin/npx" if n == "npx" else None)
    argv = wt._resolve_argv("markdownlint", "markdownlint-cli")
    assert argv == ["npx", "--yes", wt._PINNED["markdownlint-cli"]]
    assert "@" in argv[-1]  # version-pinned for determinism


def test_no_npx_env_forbids_autoinstall(monkeypatch):
    monkeypatch.setattr(wt.shutil, "which",
                        lambda n: "/usr/bin/npx" if n == "npx" else None)
    monkeypatch.setenv("RIG_WRITING_TOOLS_NO_NPX", "1")
    assert wt._resolve_argv("markdownlint", "markdownlint-cli") is None


def test_run_failed_semantics():
    assert wt._run_failed(124, has_findings=False) is True   # timeout
    assert wt._run_failed(1, has_findings=False) is True     # crash / bootstrap fail
    assert wt._run_failed(0, has_findings=False) is False    # clean input, no issues
    assert wt._run_failed(1, has_findings=True) is False     # markdownlint: findings + rc 1
    # timeout is unconditional: even partial findings mean the analysis was truncated
    assert wt._run_failed(124, has_findings=True) is True
