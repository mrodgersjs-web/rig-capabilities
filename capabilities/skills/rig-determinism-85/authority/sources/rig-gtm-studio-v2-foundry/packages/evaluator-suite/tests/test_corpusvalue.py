"""Deterministic component tests for the CorpusValue pilot scorer."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


@pytest.fixture
def scorer():
    path = Path("corpora/tools/corpusvalue_pilot.py")
    spec = importlib.util.spec_from_file_location("corpusvalue_pilot", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _payload(**overrides):
    payload = {
        "video_id": "abcdefghijk",
        "title": "Fixture",
        "segment_count": 1,
        "is_generated": False,
        "segments": [{"start": 0, "duration": 1, "text": "fixture text"}],
    }
    payload.update(overrides)
    return payload


def _fixed_components(monkeypatch, scorer):
    monkeypatch.setattr(scorer, "score_practical_specificity", lambda text: 0.8)
    monkeypatch.setattr(scorer, "score_rig_applicability", lambda text: 0.6)
    monkeypatch.setattr(scorer, "score_evidence_density", lambda text: 0.4)
    monkeypatch.setattr(scorer, "score_transcript_quality", lambda payload: 0.2)
    monkeypatch.setattr(scorer, "duplication_penalty", lambda text, texts: 0.1)
    monkeypatch.setattr(scorer, "unsupported_claim_penalty", lambda text: 0.05)


def test_missing_metadata_is_unscored_and_weights_are_renormalized(
    scorer, monkeypatch
):
    _fixed_components(monkeypatch, scorer)
    result = scorer.corpusvalue(_payload(), set(), ["fixture text"])

    # (0.25*.8 + 0.20*.6 + 0.15*.4 + 0.10*.2) / 0.70 - .15
    assert result["score"] == pytest.approx(0.421, abs=0.0005)
    assert result["components"]["source_diversity"] is None
    assert result["components"]["recency"] is None
    assert set(result["unscored_components"]) == {"diversity", "recency"}


def test_known_single_channel_and_date_keep_original_weights(scorer, monkeypatch):
    _fixed_components(monkeypatch, scorer)
    payload = _payload(channel_id="channel-1", published_date="2026-09-01")
    result = scorer.corpusvalue(payload, {"channel-1"}, ["fixture text"])

    # .25*.8 + .20*0 + .20*.6 + .15*.4 + .10*.2 + .10*1 - .15
    assert result["score"] == pytest.approx(0.35, abs=0.0005)
    assert result["unscored_components"] == []
    assert result["components"]["source_diversity"] == 0.0
    assert result["components"]["recency"] == 1.0


def test_penalties_detect_near_duplicate_and_absolute_claim(scorer):
    text = "one two three four five six seven eight nine ten"
    near_duplicate = text + " eleven"
    assert scorer.duplication_penalty(text, [text, near_duplicate]) == 0.1
    assert scorer.unsupported_claim_penalty("This always works") == 0.05
    assert scorer.unsupported_claim_penalty("This may work") == 0.0


def test_future_publication_date_is_unscored(scorer):
    assert scorer.score_recency("2026-09-16") is None


def test_manifest_missing_video_fails_closed(tmp_path, scorer, monkeypatch):
    transcript_dir = tmp_path / "raw"
    transcript_dir.mkdir()
    (transcript_dir / "abcdefghijk.json").write_text(json.dumps(_payload()))
    manifest = tmp_path / "manifest.txt"
    manifest.write_text("abcdefghijk\nmissing0001\n")
    monkeypatch.setattr(
        sys,
        "argv",
        ["corpusvalue_pilot.py", str(transcript_dir), str(manifest)],
    )

    assert scorer.main() == 2
    assert not (transcript_dir / "_corpusvalue_pilot.json").exists()
