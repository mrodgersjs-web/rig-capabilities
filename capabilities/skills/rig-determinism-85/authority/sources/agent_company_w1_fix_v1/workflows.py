"""GTM agent company: Temporal entity workflows (Layer 0 engine bodies).

One long-running workflow per agent, continue-as-new daily, never ends.
Wake sources: durable timer (cadence), signals (wake/lead directives), lead reassign.
Single-writer: workflow id == agent name is the lock (RUN_WAR_POLICY reject-duplicate).
"""
from __future__ import annotations
import asyncio
from datetime import datetime, timedelta, timezone
from temporalio import workflow
with workflow.unsafe.imports_passed_through():
    from . import config
    from temporalio.common import RetryPolicy

CAN_S = 20 * 3600  # continue-as-new after ~20h


def _now() -> float:
    return workflow.now().timestamp()


@workflow.defn
class UpworkBidder:
    """Owns Upwork proposals. Bid cycle = pre-fill gated drafts; submit is human+gate as today."""

    def __init__(self):
        self._wake = False
        self.beat: dict = {"agent": "upwork-bidder", "state": "init"}
        self.cycles = 0
        self.targets: dict = {}
        self.directive: str | None = None

    @workflow.signal
    def wake(self): self._wake = True

    @workflow.signal
    def reassign(self, payload: dict):
        self.directive = payload.get("text")
        self._wake = True

    @workflow.signal
    def set_targets(self, payload: dict):
        self.targets = payload; self._wake = True

    @workflow.query
    def status(self) -> dict:
        return {"beat": self.beat, "cycles": self.cycles, "directive": self.directive,
                "targets": self.targets, "last": _now()}

    @workflow.run
    async def run(self):
        while True:
            cadence = self.targets.get("cadence_s", 3600)
            try:
                await workflow.wait_condition(lambda: self._wake, timeout=cadence)
            except asyncio.TimeoutError:
                pass
            self._wake = False
            await workflow.execute_activity(
                "bidder_cycle",
                start_to_close_timeout=timedelta(minutes=3),
                retry_policy=RetryPolicy(maximum_attempts=3,
                                                  initial_interval=timedelta(seconds=10)),
            )
            self.cycles += 1
            self.beat = {"agent": "upwork-bidder", "state": "ok", "ts": workflow.now().isoformat()}
            if (workflow.now() - workflow.info().start_time).total_seconds() > CAN_S:
                workflow.continue_as_new()


@workflow.defn
class EmailOutreach:
    """Owns Oxygen first-touches. Sends stay inside existing guards (window 06:00-23:30, credits, dedupe)."""

    def __init__(self):
        self._wake = False
        self.beat: dict = {"agent": "email-outreach", "state": "init"}
        self.cycles = 0
        self.targets: dict = {}
        self.directive: str | None = None

    @workflow.signal
    def wake(self): self._wake = True

    @workflow.signal
    def reassign(self, payload: dict):
        self.directive = payload.get("text"); self._wake = True

    @workflow.signal
    def set_targets(self, payload: dict):
        self.targets = payload; self._wake = True

    @workflow.query
    def status(self) -> dict:
        return {"beat": self.beat, "cycles": self.cycles, "directive": self.directive,
                "targets": self.targets, "last": _now()}

    @workflow.run
    async def run(self):
        while True:
            cadence = self.targets.get("cadence_s", 900)
            try:
                await workflow.wait_condition(lambda: self._wake, timeout=cadence)
            except asyncio.TimeoutError:
                pass
            self._wake = False
            await workflow.execute_activity(
                "outreach_cycle",
                start_to_close_timeout=timedelta(minutes=3),
                retry_policy=RetryPolicy(maximum_attempts=3,
                                                  initial_interval=timedelta(seconds=10)),
            )
            self.cycles += 1
            self.beat = {"agent": "email-outreach", "state": "ok", "ts": workflow.now().isoformat()}
            if (workflow.now() - workflow.info().start_time).total_seconds() > CAN_S:
                workflow.continue_as_new()


@workflow.defn
class LeadSourcer:
    """Owns net-new verified lead staging into gtm/leads/*."""

    def __init__(self):
        self._wake = False
        self.beat: dict = {"agent": "lead-sourcer", "state": "init"}
        self.cycles = 0
        self.targets: dict = {}
        self.directive: str | None = None

    @workflow.signal
    def wake(self): self._wake = True

    @workflow.signal
    def reassign(self, payload: dict):
        self.directive = payload.get("text"); self._wake = True

    @workflow.signal
    def set_targets(self, payload: dict):
        self.targets = payload; self._wake = True

    @workflow.query
    def status(self) -> dict:
        return {"beat": self.beat, "cycles": self.cycles, "directive": self.directive,
                "targets": self.targets, "last": _now()}

    @workflow.run
    async def run(self):
        while True:
            cadence = self.targets.get("cadence_s", 7200)
            try:
                await workflow.wait_condition(lambda: self._wake, timeout=cadence)
            except asyncio.TimeoutError:
                pass
            self._wake = False
            await workflow.execute_activity(
                "sourcer_cycle",
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(maximum_attempts=3,
                                                  initial_interval=timedelta(seconds=10)),
            )
            self.cycles += 1
            self.beat = {"agent": "lead-sourcer", "state": "ok", "ts": workflow.now().isoformat()}
            if (workflow.now() - workflow.info().start_time).total_seconds() > CAN_S:
                workflow.continue_as_new()


@workflow.defn
class LinkedinGtm:
    """Read/measure + drafts only. Writes need exact-text Mike approval (unchanged)."""

    def __init__(self):
        self._wake = False
        self.beat: dict = {"agent": "linkedin-gtm", "state": "init"}
        self.cycles = 0
        self.targets: dict = {}
        self.directive: str | None = None

    @workflow.signal
    def wake(self): self._wake = True

    @workflow.signal
    def reassign(self, payload: dict):
        self.directive = payload.get("text"); self._wake = True

    @workflow.signal
    def set_targets(self, payload: dict):
        self.targets = payload; self._wake = True

    @workflow.query
    def status(self) -> dict:
        return {"beat": self.beat, "cycles": self.cycles, "directive": self.directive,
                "targets": self.targets, "last": _now()}

    @workflow.run
    async def run(self):
        while True:
            cadence = self.targets.get("cadence_s", 7200)
            try:
                await workflow.wait_condition(lambda: self._wake, timeout=cadence)
            except asyncio.TimeoutError:
                pass
            self._wake = False
            await workflow.execute_activity(
                "linkedin_cycle",
                start_to_close_timeout=timedelta(minutes=3),
                retry_policy=RetryPolicy(maximum_attempts=3,
                                                  initial_interval=timedelta(seconds=10)),
            )
            self.cycles += 1
            self.beat = {"agent": "linkedin-gtm", "state": "ok", "ts": workflow.now().isoformat()}
            if (workflow.now() - workflow.info().start_time).total_seconds() > CAN_S:
                workflow.continue_as_new()


@workflow.defn
class GtmLead:
    """Layer 2, reads only. Daily 07:30 stand-up: KPI vs target, signals, council cards, standup file."""

    def __init__(self):
        self._wake = False
        self.beat: dict = {"agent": "gtm-lead", "state": "init"}
        self.standups = 0
        self.escalations: list = []

    @workflow.signal
    def wake(self): self._wake = True

    @workflow.signal
    def escalate(self, payload: dict):
        self.escalations.append(payload); self._wake = True

    @workflow.query
    def status(self) -> dict:
        return {"beat": self.beat, "standups": self.standups, "escalations": self.escalations[-5:]}

    @workflow.run
    async def run(self):
        first = True
        while True:
            delay = 60 if first else 1800  # fixed 30-min loop (was UTC 07:30 wall-clock targeting)
            try:
                await workflow.wait_condition(lambda: self._wake, timeout=delay)
            except asyncio.TimeoutError:
                pass
            self._wake = False
            first = False
            await workflow.execute_activity(
                "standup",
                self.escalations[-20:],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(maximum_attempts=3,
                                                  initial_interval=timedelta(seconds=10)),
            )
            self.standups += 1
            self.beat = {"agent": "gtm-lead", "state": "ok", "ts": workflow.now().isoformat()}
            if (workflow.now() - workflow.info().start_time).total_seconds() > CAN_S:
                workflow.continue_as_new()


@workflow.defn
class GtmHead:
    """Layer 3, reads only. Weekly review (Thu) + monthly plan (1st); writes targets; budget guard."""

    def __init__(self):
        self._wake = False
        self.beat: dict = {"agent": "gtm-head", "state": "init"}
        self.reviews = 0
        self.plans = 0

    @workflow.signal
    def wake(self): self._wake = True

    @workflow.query
    def status(self) -> dict:
        return {"beat": self.beat, "reviews": self.reviews, "plans": self.plans}

    def _secs_to_next(self) -> int:
        now = workflow.now()
        # weekly Thursday 08:00, monthly 1st 07:00 - wake at whichever comes first
        cand = []
        d = now
        for _ in range(40):
            d = d + timedelta(days=1)
            if d.weekday() == config.AGENTS["gtm-head"]["weekly_day"]:
                cand.append(d.replace(hour=8, minute=0, second=0, microsecond=0)); break
        d = now
        for _ in range(40):
            d = d + timedelta(days=1)
            if d.day == 1:
                cand.append(d.replace(hour=7, minute=0, second=0, microsecond=0)); break
        return max(60, int((min(cand) - now).total_seconds()))

    @workflow.run
    async def run(self):
        first = True
        while True:
            delay = 120 if first else self._secs_to_next()
            try:
                await workflow.wait_condition(lambda: self._wake, timeout=delay)
            except asyncio.TimeoutError:
                pass
            self._wake = False
            kind = "first" if first else "scheduled"
            first = False
            await workflow.execute_activity(
                "head_cycle", kind,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(maximum_attempts=3,
                                                  initial_interval=timedelta(seconds=10)),
            )
            self.reviews += 1
            self.beat = {"agent": "gtm-head", "state": "ok", "ts": workflow.now().isoformat()}
            if (workflow.now() - workflow.info().start_time).total_seconds() > CAN_S:
                workflow.continue_as_new()


@workflow.defn
class GtmWatchdog:
    """Every 15 min: read every agent heartbeat; missed wake -> raise to lead + log."""

    def __init__(self):
        self._wake = False
        self.checks = 0
        self.last_misses: list = []

    @workflow.signal
    def wake(self): self._wake = True

    @workflow.query
    def status(self) -> dict:
        return {"checks": self.checks, "last_misses": self.last_misses}

    @workflow.run
    async def run(self):
        while True:
            try:
                await workflow.wait_condition(lambda: self._wake, timeout=900)
            except asyncio.TimeoutError:
                pass
            self._wake = False
            misses = await workflow.execute_activity(
                "watchdog_check",
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=RetryPolicy(maximum_attempts=3,
                                                  initial_interval=timedelta(seconds=10)),
            )
            self.checks += 1
            self.last_misses = misses or []
            if self.last_misses:
                await workflow.execute_activity(
                    "watchdog_raise", self.last_misses,
                    start_to_close_timeout=timedelta(minutes=2))
            if (workflow.now() - workflow.info().start_time).total_seconds() > CAN_S:
                workflow.continue_as_new()


@workflow.defn
class WorkerLoop:
    """Generic worker: one entity workflow per agent id, activity chosen by start args.
    Covers enrich-verify, icp-scorer, reply-handler, linkedin-events, phone-calls,
    web-analytics, website-cro — each a measure+heartbeat+KPI-ledger loop."""

    def __init__(self):
        self._wake = False
        self.beat: dict = {"state": "init"}
        self.cycles = 0
        self.targets: dict = {}
        self.directive: str | None = None
        self.agent = "?"
        self.last_error: str | None = None

    @workflow.signal
    def wake(self): self._wake = True

    @workflow.signal
    def reassign(self, payload: dict):
        self.directive = payload.get("text"); self._wake = True

    @workflow.signal
    def set_targets(self, payload: dict):
        self.targets = payload; self._wake = True

    @workflow.query
    def status(self) -> dict:
        return {"agent": self.agent, "beat": self.beat, "cycles": self.cycles,
                "directive": self.directive, "error": self.last_error,
                "targets": self.targets, "last": _now()}

    @workflow.run
    async def run(self, agent: str, activity: str, cadence_s: int):
        self.agent = agent
        while True:
            cadence = self.targets.get("cadence_s", cadence_s)
            try:
                await workflow.wait_condition(lambda: self._wake, timeout=cadence)
            except asyncio.TimeoutError:
                pass
            self._wake = False
            try:
                beat = await workflow.execute_activity(
                    activity,
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=RetryPolicy(maximum_attempts=3,
                                             initial_interval=timedelta(seconds=10)),
                )
                self.cycles += 1
                self.last_error = None
                self.beat = {"agent": agent, "state": "ok", "ts": workflow.now().isoformat()}
            except Exception as ex:
                self.last_error = str(ex)[:300]
            if (workflow.now() - workflow.info().start_time).total_seconds() > CAN_S:
                workflow.continue_as_new()
