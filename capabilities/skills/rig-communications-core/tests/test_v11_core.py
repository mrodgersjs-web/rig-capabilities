from rig_comm import evaluate
from rig_comm.doctrine import validate_doctrine
from rig_comm.integrations import CommunicationGuard


def test_evaluate_blocks_banned_phrase():
    report = evaluate("Hope this finds you well. Just checking in on this.", channel="email")
    assert not report.can_ship
    assert report.banned_phrases


def test_evaluate_returns_structured_report():
    text = (
        "Your team is losing 30% of engineering time to review churn. "
        "You are likely seeing throughput decay. "
        "If this is not useful, ignore this. "
        "This is only for teams actively measuring release velocity. "
        "One question: should we test the dependency hotspot first?"
    )
    report = evaluate(text, channel="email")
    payload = report.to_dict()
    assert payload["channel"] == "email"
    assert "comm_raw_score" in payload


def test_guard_revise_loop():
    def revise(text, feedback, attempt):
        return text.replace("just checking in", "") + " If this is not useful, ignore this."

    guard = CommunicationGuard(channel="email", max_attempts=2, revise_fn=revise)
    result = guard.guard("just checking in")
    assert result.attempts >= 1
    assert isinstance(result.report.blocks, list)


def test_doctrine_validator_passes_weight_checks():
    report = validate_doctrine()
    assert report.passed
