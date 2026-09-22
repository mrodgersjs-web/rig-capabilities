from __future__ import annotations

import plistlib
import sys
from pathlib import Path

from harness.components import apply_mutation, render_template, report, validate_python
from harness.packet import DesignPacket, Proposal, Report

_COMPONENT = "runtime"


def render(packet: DesignPacket, out: Path) -> list[Path]:
    root = out / _COMPONENT
    worker = render_template(
        "worker.py.j2",
        root / "worker.py",
        task_queue_repr=repr(packet.runtime.task_queue),
        carrier_repr=repr(packet.runtime.carrier),
        lanes_repr=repr(tuple(lane.slug for lane in packet.lanes)),
    )
    schedules = render_template(
        "schedule.py.j2",
        root / "schedules.py",
        task_queue_repr=repr(packet.runtime.task_queue),
        schedules_repr=repr(tuple({
            "slug": lane.slug,
            "cron": lane.schedule_cron,
            "timezone": lane.tz,
            "overlap": "SKIP",
        } for lane in packet.lanes)),
    )
    plist = render_template(
        "launchd.plist.j2",
        root / "launchd" / packet.runtime.worker_plist,
        worker_plist=packet.runtime.worker_plist,
        python_path=sys.executable,
        working_directory=str(root),
    )
    return [worker, schedules, plist]


def validate(files: list[Path]) -> Report:
    findings: list[str] = []
    by_name = {path.name: path for path in files if path.exists()}
    for name in ("worker.py", "schedules.py"):
        if name not in by_name:
            findings.append(f"{name}:missing:file")
        else:
            validate_python(by_name[name], findings)
    plists = [path for path in files if path.suffix == ".worker" or path.name.endswith(".worker") or "launchd" in path.parts]
    if not plists:
        findings.append("launchd:missing:plist")
    for plist in plists:
        try:
            data = plistlib.loads(plist.read_bytes())
            for key in ("Label", "ProgramArguments", "WorkingDirectory"):
                if key not in data:
                    findings.append(f"{plist.name}:missing:{key}")
        except (OSError, plistlib.InvalidFileException) as exc:
            findings.append(f"{plist.name}:plist:{exc}")
    return report(findings)


def mutate(files: list[Path], proposal: Proposal) -> list[Path]:
    return apply_mutation(files, proposal, _COMPONENT)
