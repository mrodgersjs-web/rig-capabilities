"""Done-tests for rig_capabilities.chunk.

Two halves, deliberately:

  * must-stay-local / must-refuse — the gate exists to keep design, control-plane, outward
    effects, secrets and unverifiable work with Mike. Each case names WHY.
  * must-fan-out — a gate that holds everything back is as useless as no gate; these prove
    delegable work is actually delegated. (The real over-trigger this caught: an acceptance
    line reading "single word naming a color" was held as an API-naming decision.)

The OFFLOAD_VIOLATION case is the kept planted failure: a PAIR history whose `scheduledOn`
is this box must turn the offload verdict RED. A verify() that cannot go red proves nothing.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rig_capabilities import chunk as C

LOCAL = "874b90fa-2c6c-4f73-b3f6-cfeed9e780a9"
REMOTE = "b26a4433-0653-47f1-bdc7-16b44b0f816e"


def mk(**over: object) -> C.Chunk:
    base: dict[str, object] = {
        "id": "c1",
        "title": "Summarize one scraper log",
        "prompt": "Summarize the attached log in one sentence.",
        "work_class": "summarize",
        "acceptance": "one sentence under 30 words",
        "reversible": True,
        "failure_cost": 0.1,
    }
    base.update(over)
    return C.Chunk.from_obj(base)


# Each case trips exactly ONE trigger and asserts the matched text, so a regression in any
# single alternation fails its own case. (First cut asserted only the lane; every case tripped
# two or three patterns, so neutering one still passed — a plant that cannot fire.)
@pytest.mark.parametrize(
    ("label", "over", "trigger"),
    [
        ("design-verb", {"title": "Design the dispatcher module", "prompt": "Produce the structure we commit to."}, "design"),
        ("api-surface", {"title": "Decide the public api surface", "prompt": "Pick the endpoints."}, "api surface"),
        ("schema", {"prompt": "Update the schema for chunk runs."}, "schema"),
        ("migration", {"prompt": "Write the migration for the runs table."}, "migration"),
        ("rename", {"title": "Rename the dispatch verb", "prompt": "Update the callers."}, "rename"),
        ("naming-convention", {"prompt": "Pick the naming convention for run ids."}, "naming convention"),
        ("name-the-endpoint", {"prompt": "Name the endpoint for chunk dispatch."}, "name the endpoint"),
        ("control-plane", {"prompt": "Set the retry policy for remote jobs."}, "retry policy"),
        ("budget", {"prompt": "Raise the budget for remote runs."}, "budget"),
        ("outward-effect", {"prompt": "Publish the summary."}, "publish"),
        ("effect-in-acceptance", {"acceptance": "the post is published and live"}, "published"),
        ("secrets", {"prompt": "Read the private key from disk."}, "private key"),
        ("doctrine", {"prompt": "Update AGENTS.md with the new rule."}, "agents.md"),
        ("irreversible", {"reversible": False}, "irreversible"),
        ("high-failure-cost", {"failure_cost": 0.5}, "failure_cost=0.5"),
        ("unverifiable", {"acceptance": "   "}, "no-acceptance-check"),
    ],
)
def test_critical_work_stays_local(label: str, over: dict[str, object], trigger: str) -> None:
    verdict = C.classify(mk(**over))
    assert verdict.lane == "local", f"{label} should stay with Mike, got {verdict}"
    assert verdict.reasons and all(r.startswith("critical:") for r in verdict.reasons)
    assert trigger in " ".join(verdict.reasons), f"{label} lost its trigger {trigger!r}: {verdict.reasons}"


@pytest.mark.parametrize(
    ("label", "over"),
    [
        ("plain-summary", {}),
        ("naming-in-prose", {"acceptance": "single word naming a color"}),
        ("extract", {"work_class": "extract", "prompt": "Pull every URL out of this text."}),
        ("code-chunk", {"work_class": "code", "prompt": "Write a stdlib-only CSV row counter.", "acceptance": "counts rows on the fixture"}),
        ("boundary-cost", {"failure_cost": 0.49}),
    ],
)
def test_delegable_work_fans_out(label: str, over: dict[str, object]) -> None:
    verdict = C.classify(mk(**over))
    assert verdict.lane == "fanout", f"{label} should be delegated, got {verdict.reasons}"


@pytest.mark.parametrize(
    ("label", "obj"),
    [
        ("no-id", {"title": "t", "prompt": "p"}),
        ("no-prompt", {"id": "c", "title": "t"}),
        ("blank-title", {"id": "c", "title": "   ", "prompt": "p"}),
        ("cost-out-of-range", {"id": "c", "title": "t", "prompt": "p", "failure_cost": 1.5}),
        ("cost-bool", {"id": "c", "title": "t", "prompt": "p", "failure_cost": True}),
        ("reversible-not-bool", {"id": "c", "title": "t", "prompt": "p", "reversible": "yes"}),
        ("unknown-work-class", {"id": "c", "title": "t", "prompt": "p", "work_class": "telepathy"}),
    ],
)
def test_unjudgeable_chunks_are_refused(label: str, obj: dict[str, object]) -> None:
    with pytest.raises(C.ChunkError):
        C.Chunk.from_obj(obj)


def test_model_choice_prefers_proven_remote_placement() -> None:
    available = ["qwen3.5:9b", "qwen3:4b"]
    placements = {"qwen3.5:9b": {REMOTE}, "qwen3:4b": {LOCAL}}
    model, placement = C.pick_model(mk(), available, placements, LOCAL)
    assert (model, placement) == ("qwen3.5:9b", "offload-proven")


def test_model_only_seen_locally_is_reported_local_only() -> None:
    model, placement = C.pick_model(mk(), ["qwen3.5:9b"], {"qwen3.5:9b": {LOCAL}}, LOCAL)
    assert (model, placement) == ("qwen3.5:9b", "local-only")


def test_unavailable_model_is_refused_not_guessed() -> None:
    with pytest.raises(C.ChunkError, match="no model for work_class"):
        C.pick_model(mk(work_class="longctx"), ["qwen3:4b"], {}, LOCAL)


def _history(tmp_path: Path, rows: list[dict[str, object]]) -> Path:
    path = tmp_path / "workloads-history.json"
    path.write_text(json.dumps(rows))
    return path


def _members(tmp_path: Path) -> Path:
    path = tmp_path / "members.json"
    path.write_text(json.dumps([
        {"id": "local", "nodeUuid": LOCAL, "ipAddress": "127.0.0.1"},
        {"id": "studio", "nodeUuid": REMOTE, "ipAddress": "192.168.68.52"},
    ]))
    return path


def _dispatch(model: str = "qwen3.5:9b") -> dict[str, object]:
    return {
        "run_id": "r1",
        "results": [{"chunk_id": "c1", "model": model, "state": "completed", "started_ms": 1_000_000, "finished_ms": 1_005_000}],
    }


def test_remote_placement_is_proven_from_pair_ledger(tmp_path: Path) -> None:
    history = _history(tmp_path, [{"model": "qwen3.5:9b", "startedAt": 1_000_500, "scheduledOn": REMOTE, "state": "completed"}])
    report = C.verify(_dispatch(), history=history, members=_members(tmp_path), settle_s=0)
    assert report["overall"] == "OFFLOAD_PROVEN"
    assert report["proven"] == 1 and report["violations"] == 0


def test_work_that_ran_here_is_a_violation_not_a_pass(tmp_path: Path) -> None:
    """PLANTED FAILURE, kept as a fixture: PAIR says it ran on this box, so the offload
    claim is false and the gate must go red."""
    history = _history(tmp_path, [{"model": "qwen3.5:9b", "startedAt": 1_000_500, "scheduledOn": LOCAL, "state": "completed"}])
    report = C.verify(_dispatch(), history=history, members=_members(tmp_path), settle_s=0)
    assert report["overall"] == "OFFLOAD_VIOLATION"
    assert report["violations"] == 1


def test_missing_evidence_is_unproven_never_proven(tmp_path: Path) -> None:
    report = C.verify(_dispatch(), history=_history(tmp_path, []), members=_members(tmp_path), settle_s=0)
    assert report["overall"] == "UNPROVEN"
    assert report["proven"] == 0


def test_stale_row_outside_the_window_does_not_count(tmp_path: Path) -> None:
    history = _history(tmp_path, [{"model": "qwen3.5:9b", "startedAt": 500_000, "scheduledOn": REMOTE, "state": "completed"}])
    report = C.verify(_dispatch(), history=history, members=_members(tmp_path), settle_s=0)
    assert report["overall"] == "UNPROVEN"


def test_reused_artifact_cannot_claim_fresh_offload(tmp_path: Path) -> None:
    obj = {"run_id": "r1", "results": [{"chunk_id": "c1", "model": "qwen3.5:9b", "state": "reused"}]}
    report = C.verify(obj, history=_history(tmp_path, []), members=_members(tmp_path), settle_s=0)
    assert report["overall"] == "UNPROVEN"


def test_local_node_requires_a_loopback_member(tmp_path: Path) -> None:
    path = tmp_path / "members.json"
    path.write_text(json.dumps([{"id": "studio", "nodeUuid": REMOTE, "ipAddress": "192.168.68.52"}]))
    with pytest.raises(C.ChunkError, match="no loopback member"):
        C.local_node_uuid(members=path)


def test_plan_rejects_a_mission_without_chunks() -> None:
    with pytest.raises(C.ChunkError, match="no chunks"):
        C.plan({"mission_id": "m1", "chunks": []})


def test_owner_routing_is_delegated_to_the_doctrine_router(tmp_path: Path) -> None:
    """Carrier selection must never be re-implemented here; a missing router is reported as
    review-required rather than guessed."""
    assert C.owner_for("anything", router=tmp_path / "absent").startswith("review-required")
