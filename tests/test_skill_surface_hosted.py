import importlib.machinery
import importlib.util
import json
from pathlib import Path

import pytest


@pytest.fixture
def surface(monkeypatch, tmp_path):
    path = Path(__file__).resolve().parents[1] / "bin" / "skill-surface"
    loader = importlib.machinery.SourceFileLoader("skill_surface_hosted", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    manifest = {
        "metas": ["when-shipping-code"],
        "entries": {
            "when-shipping-code": {
                "role": "meta", "meta": "when-shipping-code", "load": "/skills/code/SKILL.md",
            },
            "code-review": {
                "role": "skill", "meta": "when-shipping-code",
                "purpose": "Review a Python code change", "load": "/skills/code-review/SKILL.md",
            },
        },
    }
    monkeypatch.setattr(module, "load", lambda: manifest)
    monkeypatch.setattr(module, "ROUTES", str(tmp_path / "routes.jsonl"))
    return module


def answer(q, *args, **kwargs):
    choice = {"meta": "when-shipping-code", "skill": "code-review"}[q]
    return {
        "ok": True, "lane": "jev", "choice": choice, "confidence": 0.99,
        "probs": {choice: 0.99}, "verdict": "PASS", "decision_id": 321, "model": "jev-test",
    }


def forbid_local(monkeypatch, surface):
    def unexpected(*args, **kwargs):
        pytest.fail("Local inference was invoked")
    for name in ("openjev_choice", "laya_choice"):
        monkeypatch.setattr(surface, name, unexpected, raising=False)


def test_hosted_failure_defers_without_local_inference(surface, monkeypatch, capsys):
    forbid_local(monkeypatch, surface)
    monkeypatch.setattr(surface, "jev_choice", lambda *a, **k: {
        "ok": False, "error": "hosted API unavailable", "decision_id": 322,
    })
    assert surface.cmd_route("Review a Python code change", as_json=True) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "DEFERRED"
    assert result["load"] is None
    assert result["levels"][0]["decision_id"] == 322


def test_retired_local_flag_routes_through_hosted_api(surface, monkeypatch, capsys):
    forbid_local(monkeypatch, surface)
    monkeypatch.setattr(surface, "jev_choice", answer)
    assert surface.cmd_route("Review a Python code change", local=True, as_json=True) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "ROUTED"
    assert result["load"] == "code-review"
    assert [level["lane"] for level in result["levels"]] == ["jev", "jev"]


def test_token_is_redacted_before_hosted_routing(surface, monkeypatch, capsys):
    forbid_local(monkeypatch, surface)
    states = []

    def hosted(q, instructions, criteria, task, subject, **kwargs):
        states.append(task)
        return answer(q)
    monkeypatch.setattr(surface, "jev_choice", hosted)
    task = "Review a Python code change using sk-" + "a" * 32
    assert surface.cmd_route(task, as_json=True) == 0
    result = json.loads(capsys.readouterr().out)
    assert states == ["Review a Python code change using [REDACTED-TOKEN]"] * 2
    assert result["sensitive"] is True
    assert result["status"] == "ROUTED"
    assert "task_preview" not in result
    assert task not in Path(surface.ROUTES).read_text()


@pytest.mark.parametrize("task", [
    "Review a patient medical record diagnosis",
    "Review a Python change for someone@example.com",
    "Review a Python change for $12000",
])
def test_unredacted_private_details_defer(surface, monkeypatch, capsys, task):
    forbid_local(monkeypatch, surface)

    def unexpected(*args, **kwargs):
        pytest.fail("Private details reached hosted JEV")
    monkeypatch.setattr(surface, "jev_choice", unexpected)
    assert surface.cmd_route(task, as_json=True) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "DEFERRED"
    assert result["load"] is None
    assert "task_preview" not in result


def test_missing_redactor_defers_instead_of_sending_raw_task(surface, monkeypatch, capsys, tmp_path):
    forbid_local(monkeypatch, surface)
    monkeypatch.setattr(surface, "RIGCAP", str(tmp_path))
    monkeypatch.setattr(surface, "jev_choice", answer)
    assert surface.cmd_route("Review a Python code change", as_json=True) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "DEFERRED"
    assert result["load"] is None


def test_local_endpoint_override_cannot_reach_provider(surface, monkeypatch, tmp_path):
    from rig_capabilities import s1gate
    monkeypatch.setattr(s1gate, "JEV_ENDPOINT", "http://127.0.0.1:8932/v1/systemone")
    monkeypatch.setattr(s1gate, "DB_PATH", tmp_path / "decisions.db")
    monkeypatch.setattr(s1gate, "ask", lambda *a, **k: {
        "answers": {"meta": {"type": "choice", "choice": "when-shipping-code", "confidence": 0.99}},
        "model": "openjev-test",
    })
    result = surface.jev_choice("meta", "Choose the area", {"when-shipping-code": "Code"},
                                "Review a Python code change", "public-test")
    assert result["ok"] is False
    assert "hosted" in result["error"].lower()


@pytest.mark.parametrize("change", [
    {"choice": "unknown-option"},
    {"confidence": float("nan")},
    {"confidence": 1.5},
    {"probabilities": {"when-shipping-code": "invalid"}},
])
def test_invalid_hosted_response_defers(surface, monkeypatch, capsys, tmp_path, change):
    from rig_capabilities import s1gate
    monkeypatch.setattr(s1gate, "JEV_ENDPOINT", "https://api.typesafe.ai/v1/systemone")
    monkeypatch.setattr(s1gate, "DB_PATH", tmp_path / "decisions.db")
    monkeypatch.setattr(s1gate, "CACHE_ENABLED", False)
    malformed = {"type": "choice", "choice": "when-shipping-code", "confidence": 0.99, **change}
    monkeypatch.setattr(s1gate, "ask", lambda *a, **k: {
        "answers": {"meta": malformed}, "model": "jev-test",
    })
    assert surface.cmd_route("Review a public Python change", as_json=True) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "DEFERRED"
    assert result["load"] is None


def test_model_override_still_requests_hosted_jev(surface, monkeypatch, capsys, tmp_path):
    from rig_capabilities import s1gate
    monkeypatch.setattr(s1gate, "JEV_ENDPOINT", "https://api.typesafe.ai/v1/systemone")
    monkeypatch.setattr(s1gate, "JEV_MODEL", "openjev-latest")
    monkeypatch.setattr(s1gate, "DB_PATH", tmp_path / "decisions.db")
    monkeypatch.setattr(s1gate, "CACHE_ENABLED", False)
    requested_models = []

    def hosted(state, questions, **kwargs):
        requested_models.append(kwargs["model"])
        q = next(iter(questions))
        return {"answers": {q: {"type": "choice", "confidence": 0.99,
                               "choice": {"meta": "when-shipping-code", "skill": "code-review"}[q]}},
                "model": "jev-test"}

    monkeypatch.setattr(s1gate, "ask", hosted)
    assert surface.cmd_route("Review a public Python change", as_json=True) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "ROUTED"
    assert result["load"] == "code-review"
    assert requested_models == ["jev-latest", "jev-latest"]
