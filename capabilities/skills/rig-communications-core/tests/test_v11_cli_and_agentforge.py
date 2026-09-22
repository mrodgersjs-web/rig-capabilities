from pathlib import Path

from rig_comm.agentforge.runner import run_workflow
from rig_comm.cli import main


def test_cli_doctrine_check():
    code = main(["doctrine-check"])
    assert code == 0


def test_agentforge_single_message_guard_runs():
    root = Path(__file__).resolve().parents[1]
    wf = root / "agentforge" / "single-message-guard.workflow"
    run = run_workflow(str(wf), inputs={"draft": "Your team has a measurable cost pattern. If this is not useful, ignore this.", "approved": True})
    assert run.status == "ok"
    assert run.steps
