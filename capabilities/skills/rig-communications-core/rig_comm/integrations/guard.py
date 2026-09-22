from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Callable, Dict, Generator, Optional

from ..core import Report, evaluate


ReviseFn = Callable[[str, Dict[str, object], int], str]


@dataclass
class GuardResult:
    text: str
    passed: bool
    attempts: int
    report: Report

    def to_dict(self) -> Dict[str, object]:
        return {
            "text": self.text,
            "passed": self.passed,
            "attempts": self.attempts,
            "report": self.report.to_dict(),
        }


class CommunicationGuard:
    def __init__(self, channel: str = "email", max_attempts: int = 2, revise_fn: Optional[ReviseFn] = None):
        self.channel = channel
        self.max_attempts = max(1, max_attempts)
        self.revise_fn = revise_fn

    def guard(self, text: str, channel: Optional[str] = None) -> GuardResult:
        current = text
        active_channel = channel or self.channel
        for attempt in range(1, self.max_attempts + 1):
            report = evaluate(current, channel=active_channel)
            if report.can_ship:
                return GuardResult(text=current, passed=True, attempts=attempt, report=report)
            if not self.revise_fn:
                return GuardResult(text=current, passed=False, attempts=attempt, report=report)
            feedback = {
                "blocks": report.blocks,
                "warnings": report.warnings,
                "banned_phrases": report.banned_phrases,
                "channel": active_channel,
            }
            current = self.revise_fn(current, feedback, attempt)

        final = evaluate(current, channel=active_channel)
        return GuardResult(text=current, passed=final.can_ship, attempts=self.max_attempts, report=final)

    def __call__(self, fn: Callable[..., str]) -> Callable[..., GuardResult]:
        def wrapped(*args, **kwargs):
            drafted = fn(*args, **kwargs)
            return self.guard(drafted)

        return wrapped

    @contextmanager
    def context(self) -> Generator["CommunicationGuard", None, None]:
        yield self


def guard_function(fn: Callable[..., str], **guard_kwargs) -> Callable[..., GuardResult]:
    return CommunicationGuard(**guard_kwargs)(fn)
