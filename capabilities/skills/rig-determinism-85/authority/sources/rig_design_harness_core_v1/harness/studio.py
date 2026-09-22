from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Literal

RUNS_ROOT = Path.home() / ".rig" / "systems-studio" / "runs"

# Exact artifact and heading contract from systems-thinking-studio/processes/phases.md.
_REQUIRED_HEADINGS: dict[str, tuple[str, ...]] = {
    "brief.md": ("## Problem", "## Success looks like"),
    "frame.md": (),
    "diagnosis.md": ("## Suspect", "## Evidence", "## Counterintuitive"),
    "leverage.md": ("## Chosen", "## Rejected"),
    "grounding.md": ("## Citations", "## Gaps"),
    "polymath.md": ("## Target structure", "## Top imports", "## Rejected (metaphor-only)"),
    "DELIVERABLE.md": ("## What is happening", "## What to do", "## Falsifier", "## Rejected"),
}

_PHASE_ARTIFACTS = (
    ("01", "brief.md"),
    ("02", "frame.md"),
    ("03", "diagnosis.md"),
    ("04", "leverage.md"),
    ("05", "grounding.md"),
    ("06", "polymath.md"),
    ("07", "DELIVERABLE.md"),
)




class StudioRed(RuntimeError):
    pass


def _new_run(before: set[Path], output: str) -> Path:
    matches = re.findall(r"^run dir:\s*(.+)$", output, re.MULTILINE)
    if matches:
        return Path(matches[-1]).expanduser().resolve()
    created = [path for path in RUNS_ROOT.glob("*") if path.is_dir() and path not in before]
    if created:
        return max(created, key=lambda path: path.stat().st_mtime_ns)
    raise RuntimeError("systems studio did not report or create a run directory")


def _run(command: list[str]) -> Path:
    before = {path.resolve() for path in RUNS_ROOT.glob("*") if path.is_dir()}
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
    try:
        return _new_run(before, output)
    except RuntimeError:
        raise RuntimeError(f"{' '.join(command)} failed ({result.returncode}): {output.strip()}") from None


def run_det(problem: str, domain: str, context: str) -> Path:
    doctor = subprocess.run(["studio", "doctor"], capture_output=True, text=True, check=False)
    if doctor.returncode:
        output = (doctor.stdout or "") + ("\n" + doctor.stderr if doctor.stderr else "")
        raise RuntimeError(f"studio doctor failed ({doctor.returncode}): {output.strip()}")
    return _run(["studio", "run", problem, "--domain", domain, "--context", context])


def run_agent(problem: str) -> Path:
    return _run(["systems-studio", problem])


def _contract_failure(run_dir: Path) -> str | None:
    if not run_dir.is_dir():
        return f"run directory missing: {run_dir}"
    for name, required in _REQUIRED_HEADINGS.items():
        path = run_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            return f"{name} missing/empty"
        headings = {line.strip() for line in path.read_text(errors="replace").splitlines() if line.startswith("## ")}
        missing = [heading for heading in required if heading not in headings]
        if missing:
            return f"{name} missing required headings: {', '.join(missing)}"
    return None


def _red_reason(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    for pattern in (r"^FAIL\b", r"\bphase\s+\d+\s+RED\b", r"\bDEGRADED\b", r"^RUN\s+RED\b", r"\bRED\b"):
        for line in reversed(lines):
            if re.search(pattern, line, re.IGNORECASE):
                return line
    return "studio verification reported RED"


def phase_states(run_dir: Path) -> list[str]:
    run_dir = Path(run_dir)
    logs = "\n".join(
        path.read_text(errors="replace")
        for path in (run_dir / "harness.log", run_dir / "verify.log")
        if path.is_file()
    )
    states: list[str] = []
    for number, artifact in _PHASE_ARTIFACTS:
        path = run_dir / artifact
        required = _REQUIRED_HEADINGS[artifact]
        headings = (
            {line.strip() for line in path.read_text(errors="replace").splitlines() if line.startswith("## ")}
            if path.is_file() and path.stat().st_size
            else set()
        )
        if path.is_file() and path.stat().st_size and all(heading in headings for heading in required):
            state = "GREEN"
        elif re.search(rf"\bphase\s+0?{int(number)}\b.*\b(?:RED|DEGRADED)\b", logs, re.IGNORECASE):
            state = "RED"
        else:
            state = "RUNNING"
        states.append(f"{number}:{state}")

    final = verdict(run_dir)
    states.append(f"08:{final}")
    return states


def verdict(run_dir: Path) -> Literal["GREEN", "RED", "RUNNING"]:
    run_dir = Path(run_dir)
    failure = _contract_failure(run_dir)
    if failure:
        return "RED"

    verify_log = run_dir / "verify.log"
    verify_text = verify_log.read_text(errors="replace") if verify_log.is_file() else ""
    terminal = re.findall(r"^RUN (GREEN|RED)(?:\s|$)", verify_text, re.MULTILINE)
    if terminal:
        return terminal[-1]
    if re.search(r"(?:\bphase\s+\d+\s+RED\b|^FAIL\b)", verify_text, re.MULTILINE | re.IGNORECASE):
        return "RED"

    harness_log = run_dir / "harness.log"
    harness_text = harness_log.read_text(errors="replace") if harness_log.is_file() else ""
    if re.search(r"\bRED\b", harness_text, re.IGNORECASE):
        return "RED"
    return "RUNNING"


def require_green(run_dir: Path) -> None:
    state = verdict(run_dir)
    if state == "GREEN":
        return
    failure = _contract_failure(Path(run_dir))
    if failure:
        raise StudioRed(failure)
    logs = []
    for name in ("verify.log", "harness.log"):
        path = Path(run_dir) / name
        if path.is_file():
            logs.append(path.read_text(errors="replace"))
    reason = _red_reason("\n".join(logs)) if state == "RED" else "studio run is still RUNNING"
    raise StudioRed(reason)
