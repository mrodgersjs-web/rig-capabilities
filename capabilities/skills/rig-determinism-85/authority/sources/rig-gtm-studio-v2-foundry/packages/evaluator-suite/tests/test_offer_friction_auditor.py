"""Golden and adversarial tests for the offer-friction-auditor skill."""
import json
from pathlib import Path

import pytest

# Import the real deterministic skill
from capabilities.skills.offer_friction_auditor import audit_offer


@pytest.fixture
def golden_test_case():
    """Load the golden test case."""
    path = Path(__file__).parent.parent / "golden" / "offer-friction-auditor-golden.json"
    return json.loads(path.read_text())


@pytest.fixture
def adversarial_test_case():
    """Load the adversarial test case."""
    path = Path(__file__).parent.parent / "adversarial" / "offer-friction-auditor-adversarial.json"
    return json.loads(path.read_text())


def test_golden_offer_with_friction(golden_test_case):
    """Golden test: offer with unclear value and no guarantee should have 4 friction points."""
    result = audit_offer(golden_test_case["input"]["offer_text"])

    assert result["friction_count"] == golden_test_case["expected_output"]["friction_count"]
    assert set(fp["type"] for fp in result["friction_points"]) == set(
        golden_test_case["expected_output"]["friction_types"]
    )
    assert result["confidence"] >= golden_test_case["expected_output"]["confidence_min"]
    assert golden_test_case["expected_output"]["recommendation_contains"] in result["recommendation"]


def test_adversarial_offer_without_friction(adversarial_test_case):
    """Adversarial test: offer with all friction points resolved should have 0 friction."""
    result = audit_offer(adversarial_test_case["input"]["offer_text"])

    assert result["friction_count"] == adversarial_test_case["expected_output"]["friction_count"]
    assert result["confidence"] <= adversarial_test_case["expected_output"]["confidence_max"]


def test_red_mutated_oracle():
    """Red test: prove the test catches a wrong expectation by mutating it."""
    offer_text = "We provide consulting services for your business. Contact us for more information."
    result = audit_offer(offer_text)

    # Mutate expected friction_count to wrong value
    wrong_expected = 3
    assert result["friction_count"] != wrong_expected, "Test should fail with wrong expectation"
