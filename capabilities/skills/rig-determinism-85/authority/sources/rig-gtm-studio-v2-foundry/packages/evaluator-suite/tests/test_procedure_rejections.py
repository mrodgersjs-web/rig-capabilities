"""Mixed actionable/non-actionable lesson compilation contracts."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, Path(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _claim(claim_id: str, text: str, epistemic_type: str, start: int) -> dict:
    return {
        "claim_id": claim_id,
        "video_id": "video00001",
        "channel_id": "channel-1",
        "text": text,
        "epistemic_type": epistemic_type,
        "start_time": start,
        "end_time": start + 5,
        "transcript_hash": f"hash-{claim_id}",
    }


def test_mixed_lessons_compile_actionable_and_retain_rejections():
    lessons_module = _load(
        "lesson_compiler", "packages/lesson-compiler/src/compiler.py"
    )
    procedures_module = _load(
        "procedure_compiler", "packages/procedure-compiler/src/compiler.py"
    )
    claims = [
        _claim("o1", "First inspect the offer", "testable_procedure", 0),
        _claim("o2", "Then rewrite the offer", "testable_procedure", 5),
        _claim("p1", "I think this price feels high", "opinion", 10),
        _claim("p2", "This pricing idea may work", "opinion", 15),
    ]
    lessons = lessons_module.compile_lessons(claims)
    result = procedures_module.compile_procedures_with_rejections(lessons, claims)

    assert len(result["compiled"]) == 1
    assert len(result["rejected"]) == 1
    assert result["rejected"][0]["reason"] == "no_testable_procedure"
    assert all(
        step["claim_id"] and step["video_id"] is not None
        for step in result["compiled"][0]["steps"]
    )
