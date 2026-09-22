"""
RIG Communication Protocol V10 — Prediction Swarm
8 buyer personas forecasting trust delta, conversion, and engagement probabilities.
"""
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class PersonaPrediction:
    """A single persona's forecast for a communication artifact."""
    persona: str
    read_past_line_2: bool
    trust_delta: float  # -1.0 to +1.0
    reply_probability: float
    share_probability: float
    comment_probability: float
    forward_probability: float
    meeting_probability: float

PERSONAS = [
    "Skeptical Buyer",
    "Busy Founder",
    "Technical Evaluator",
    "Budget Holder",
    "Industry Lurker",
    "Competitor Analyst",
    "Junior Employee",
    "Senior Executive",
]


class PredictionSwarm:
    """8-persona prediction swarm with Brier calibration."""

    def __init__(self):
        self.predictions: List[PersonaPrediction] = []
        self.brier_history: List[float] = []

    def add_prediction(self, prediction: PersonaPrediction):
        self.predictions.append(prediction)

    def predicted_success(self) -> float:
        """Aggregate predicted success across all personas."""
        if not self.predictions:
            return 0.0

        return (
            0.22 * self._avg("reply_probability")
            + 0.18 * self._avg_trust()
            + 0.16 * self._avg_trust()  # TrustBuild double-weighted through trust delta
            + 0.14 * self._avg("meeting_probability")
            + 0.12 * self._avg("forward_probability")
            + 0.10 * (self._avg("read_past_line_2"))
            + 0.08 * self._avg("meeting_probability")  # Relationship advance proxy
        )

    def has_trust_decay(self) -> bool:
        """Check if any persona predicts trust decay."""
        return any(p.trust_delta < 0 for p in self.predictions)

    def swarm_consensus(self) -> float:
        """
        How aligned are persona predictions?
        High consensus = low variance in trust_delta.
        """
        if not self.predictions:
            return 0.0
        deltas = [p.trust_delta for p in self.predictions]
        variance = (
            sum((d - sum(deltas) / len(deltas)) ** 2 for d in deltas) / len(deltas)
        )
        # Normalize: 0 variance = 1.0 consensus, high variance = low consensus
        return max(0.0, 1.0 - variance * 3)

    def brier_score(self, predictions: Dict[str, float], outcomes: Dict[str, float]) -> float:
        """
        Compute Brier Score: mean((prediction - outcome)^2)
        Lower is better. 0 = perfect calibration.
        """
        common_keys = set(predictions.keys()) & set(outcomes.keys())
        if not common_keys:
            return 1.0
        score = sum(
            (predictions[k] - outcomes[k]) ** 2 for k in common_keys
        ) / len(common_keys)
        self.brier_history.append(score)
        return score

    def _avg(self, field: str) -> float:
        vals = []
        for p in self.predictions:
            val = getattr(p, field, None)
            if isinstance(val, bool):
                vals.append(1.0 if val else 0.0)
            else:
                vals.append(float(val))
        return sum(vals) / len(vals) if vals else 0.0

    def _avg_trust(self) -> float:
        return self._avg("trust_delta")


def example_swarm() -> PredictionSwarm:
    """Sarah Chen cold email example swarm."""
    swarm = PredictionSwarm()

    personas = [
        ("Skeptical Buyer", True, 0.3, 0.25, 0.05, 0.10, 0.05, 0.20),
        ("Busy Founder", True, 0.2, 0.30, 0.10, 0.05, 0.15, 0.25),
        ("Technical Evaluator", True, 0.4, 0.35, 0.05, 0.15, 0.20, 0.30),
        ("Budget Holder", True, 0.3, 0.20, 0.05, 0.05, 0.10, 0.15),
        ("Industry Lurker", True, 0.1, 0.05, 0.30, 0.20, 0.25, 0.05),
        ("Competitor Analyst", True, -0.1, 0.05, 0.05, 0.05, 0.10, 0.05),
        ("Junior Employee", True, 0.3, 0.10, 0.20, 0.15, 0.30, 0.10),
        ("Senior Executive", True, 0.2, 0.25, 0.05, 0.05, 0.10, 0.20),
    ]

    for p in personas:
        swarm.add_prediction(PersonaPrediction(
            persona=p[0], read_past_line_2=p[1], trust_delta=p[2],
            reply_probability=p[3], share_probability=p[4],
            comment_probability=p[5], forward_probability=p[6],
            meeting_probability=p[7],
        ))

    return swarm


if __name__ == "__main__":
    swarm = example_swarm()
    print(f"Predicted Success: {swarm.predicted_success():.3f}")
    print(f"Swarm Consensus: {swarm.swarm_consensus():.3f}")
    print(f"Trust Decay: {swarm.has_trust_decay()}")
