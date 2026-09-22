from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple

from .gates import BANNED_PHRASES


@dataclass
class DoctrineViolation:
    code: str
    message: str


@dataclass
class DoctrineReport:
    passed: bool
    violations: List[DoctrineViolation] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "passed": self.passed,
            "violations": [{"code": v.code, "message": v.message} for v in self.violations],
        }


FORMULA_WEIGHTS: Dict[str, Tuple[float, ...]] = {
    "comm_raw_score": (0.14, 0.12, 0.11, 0.10, 0.09, 0.09, 0.08, 0.08, 0.07, 0.06, 0.04, 0.02),
    "email_voltage_score": (0.22, 0.18, 0.16, 0.14, 0.12, 0.10, 0.08),
    "email_reply_score": (0.20, 0.15, 0.15, 0.15, 0.12, 0.10, 0.08, 0.05),
    "bdf30": (0.25, 0.20, 0.15, 0.15, 0.10, 0.10, 0.05),
    "customer_facing_artifact_score": (0.18, 0.18, 0.14, 0.14, 0.12, 0.10, 0.08, 0.06),
}


def _validate_weight_sums(tolerance: float = 1e-6) -> List[DoctrineViolation]:
    violations: List[DoctrineViolation] = []
    for name, weights in FORMULA_WEIGHTS.items():
        total = sum(weights)
        if abs(total - 1.0) > tolerance:
            violations.append(DoctrineViolation("FORMULA_WEIGHT_SUM", f"{name} weights sum to {total:.6f}, expected 1.0"))
    return violations


def _validate_banned_phrases_in_artifacts(artifacts: Dict[str, str]) -> List[DoctrineViolation]:
    violations: List[DoctrineViolation] = []
    for artifact_name, text in artifacts.items():
        lines = text.lower().splitlines()
        for line in lines:
            for phrase in BANNED_PHRASES:
                if phrase not in line:
                    continue
                instructional_context = any(
                    marker in line
                    for marker in (
                        f"not \"{phrase}\"",
                        f"not '{phrase}'",
                        f'not {phrase}',
                        "banned phrase",
                        "automatic block",
                    )
                )
                if instructional_context:
                    continue
                violations.append(
                    DoctrineViolation(
                        "BANNED_PHRASE_IN_ARTIFACT",
                        f"{artifact_name} contains banned phrase: '{phrase}'",
                    )
                )
    return violations


def validate_doctrine(artifacts: Dict[str, str] | None = None) -> DoctrineReport:
    artifacts = artifacts or {}
    violations = []
    violations.extend(_validate_weight_sums())
    violations.extend(_validate_banned_phrases_in_artifacts(artifacts))
    return DoctrineReport(passed=len(violations) == 0, violations=violations)
