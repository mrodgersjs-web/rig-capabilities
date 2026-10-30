import importlib.machinery
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def labeler(monkeypatch, tmp_path):
    path = Path(__file__).resolve().parents[1] / "bin/skill-surface-label"
    loader = importlib.machinery.SourceFileLoader("surface_label_hosted", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    monkeypatch.setattr(module, "STOP", str(tmp_path / "stop"))
    monkeypatch.setattr(module, "SET", str(tmp_path / "set.jsonl"))
    monkeypatch.setattr(module, "OUT", str(tmp_path / "labels.jsonl"))
    manifest = {"metas": ["when-shipping-code"], "entries": {
        "when-shipping-code": {"role": "meta", "meta": "when-shipping-code"},
        "code-review": {"role": "skill", "meta": "when-shipping-code", "purpose": "Review Python code"},
    }}
    monkeypatch.setattr(module.ss, "load", lambda: manifest)
    monkeypatch.setattr(module, "route", lambda _: {
        "status": "ROUTED", "sensitive": False, "load": "code-review", "levels": [
            {"level": 1, "kind": "meta", "choice": "when-shipping-code", "confidence": 0.99,
             "verdict": "PASS", "decision_id": 1, "lane": "jev"},
            {"level": 2, "kind": "skill", "choice": "code-review", "confidence": 0.99,
             "verdict": "PASS", "decision_id": 2, "lane": "jev"},
        ],
    })
    return module


def hosted_evaluator(monkeypatch):
    from rig_capabilities import s1gate
    states = []

    def evaluate(rubric, state, **kwargs):
        states.append((state, kwargs))
        return SimpleNamespace(error=None, verdict="PASS", decision_id=333, model="jev-1.13.0", answers={
            "meta_choice": {"choice": "when-shipping-code", "confidence": 0.99},
            "meta_fit": {"noul": 0.99}, "skill_fit": {"noul": 0.99},
        })

    monkeypatch.setattr(s1gate, "evaluate", evaluate)
    monkeypatch.setattr(s1gate, "DecisionLog", lambda: SimpleNamespace(close=lambda: None))
    monkeypatch.setattr(s1gate, "JEV_ENDPOINT", "https://api.typesafe.ai/v1/systemone")
    return states


def test_redacted_hosted_agreement_never_becomes_independent_truth(labeler, monkeypatch):
    states = hosted_evaluator(monkeypatch)
    item = {"id": "sample", "title": "Code review", "text": "Review Python code using sk-" + "a" * 32}
    row = labeler.label_one(item, labeler.ss.Tree(labeler.ss.load()))
    assert row["router"] == "hosted-jev"
    assert row["labeler"] == "hosted-jev-verifier"
    assert row["independent"] is False
    assert row["label_meta"] == "good"
    assert row["label_decision_id"] == 333
    assert row["label_model"] == "jev-1.13.0"
    assert states[0][0] == "Request from Mike: Review Python code using [REDACTED-TOKEN]"
    assert states[0][1]["model"] == "jev-latest"
    assert row["sensitive"] is True


def test_private_details_defer_without_hosted_or_local_labeling(labeler, monkeypatch):
    states = hosted_evaluator(monkeypatch)
    item = {"id": "sample", "title": "Review", "text": "Review a patient medical record"}
    row = labeler.label_one(item, labeler.ss.Tree(labeler.ss.load()))
    assert row["labeler"] is None
    assert row["label_meta"] is None
    assert row["deferred"] == "private details remain after secret redaction; hosted routing deferred"
    assert states == []


def test_relabel_preserves_historical_rows_and_does_not_require_local_model(labeler, monkeypatch, capsys):
    states = hosted_evaluator(monkeypatch)
    old = {"id": "historical", "router": "openjev-local", "labeler": "laya", "independent": True}
    item = {"id": "new", "title": "Code review", "text": "Review Python code"}
    historical_bytes = json.dumps(old) + "\n"
    Path(labeler.OUT).write_text(historical_bytes)
    Path(labeler.SET).write_text(json.dumps(item) + "\n")
    assert labeler.run(1, relabel=True) == 0
    rows = Path(labeler.OUT).read_text()
    assert rows.startswith(historical_bytes)
    appended = json.loads(rows.splitlines()[-1])
    assert appended["id"] == "new"
    assert appended["labeler"] == "hosted-jev-verifier"
    assert appended["independent"] is False
    assert appended["label_decision_id"] == 333
    assert len(states) == 1


def test_local_endpoint_override_defers_labeling(labeler, monkeypatch):
    states = hosted_evaluator(monkeypatch)
    from rig_capabilities import s1gate
    monkeypatch.setattr(s1gate, "JEV_ENDPOINT", "http://127.0.0.1:8080/v1/systemone")
    item = {"id": "sample", "title": "Code review", "text": "Review Python code"}
    row = labeler.label_one(item, labeler.ss.Tree(labeler.ss.load()))
    assert row["labeler"] is None
    assert row["label_error"] == "RuntimeError: labeler requires the hosted JEV API endpoint"
    assert states == []
