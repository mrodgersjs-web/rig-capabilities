"""W1a dossier-builder workflow: orchestration only, zero I/O.
All CRM/research effects live in dossier_remote.REMOTE (executed on the laptop)."""
from __future__ import annotations
import asyncio
from datetime import timedelta
from temporalio import activity, workflow
with workflow.unsafe.imports_passed_through():
    from temporalio.common import RetryPolicy
    from . import config, sshio
    from .dossier_remote import REMOTE as DOSSIER_PY

CAN_S = 20 * 3600


@activity.defn(name="dossier_select")
async def dossier_select(limit: int) -> dict:
    return await sshio.run_py(DOSSIER_PY, {"cmd": "dossier_select", "limit": limit}, timeout=120)


@activity.defn(name="dossier_build")
async def dossier_build(email: str) -> dict:
    return await sshio.run_py(DOSSIER_PY, {"cmd": "dossier_build", "email": email}, timeout=420)


@activity.defn(name="dossier_verify")
async def dossier_verify(limit: int) -> dict:
    return await sshio.run_py(DOSSIER_PY, {"cmd": "dossier_verify", "limit": limit}, timeout=360)


@workflow.defn(name="DossierBuilder")
class DossierBuilder:
    """First 25 lead dossiers on real Twenty records, stored on the record BEFORE any
    touch. Information-gap loop capped at 3 passes inside the remote script."""

    def __init__(self):
        self._wake = False
        self._reset = False
        self.beat: dict = {"agent": "dossier-builder", "state": "init"}
        self.last_select: dict | None = None
        self.built: list[dict] = []
        self.verify: dict | None = None

    @workflow.signal
    def wake(self): self._wake = True

    @workflow.signal
    def reset(self):
        self._reset = True
        self._wake = True

    @workflow.query
    def status(self) -> dict:
        return {"beat": self.beat, "last_select": self.last_select,
                "built": len(self.built), "last_built": self.built[-3:] if self.built else [],
                "verify": self.verify, "last": workflow.now().timestamp()}

    async def _cycle(self, limit: int):
        sel = await workflow.execute_activity(
            "dossier_select", limit,
            start_to_close_timeout=timedelta(minutes=3),
            retry_policy=RetryPolicy(maximum_attempts=2, initial_interval=timedelta(seconds=15)))
        self.last_select = sel
        for lead in (sel or {}).get("leads", []):
            row = await workflow.execute_activity(
                "dossier_build", lead["email"],
                start_to_close_timeout=timedelta(minutes=8),
                retry_policy=RetryPolicy(maximum_attempts=2, initial_interval=timedelta(seconds=30)))
            self.built.append(row)
        self.verify = await workflow.execute_activity(
            "dossier_verify", limit,
            start_to_close_timeout=timedelta(minutes=7),
            retry_policy=RetryPolicy(maximum_attempts=1))  # one real check run
        self.beat = {"agent": "dossier-builder", "state": "ok" if (self.verify or {}).get("ok") else "verify_failed",
                     "built": len(self.built), "ts": workflow.now().isoformat()}

    @workflow.run
    async def run(self, limit: int = 25):
        await self._cycle(limit)
        while True:
            try:
                await workflow.wait_condition(lambda: self._wake, timeout=timedelta(hours=1))
            except asyncio.TimeoutError:
                pass
            self._wake = False
            if self._reset:
                workflow.continue_as_new(limit)
            await self._cycle(limit)
            if (workflow.now() - workflow.info().start_time).total_seconds() > CAN_S:
                workflow.continue_as_new(limit)


DOSSIER_ACTIVITIES = [dossier_select, dossier_build, dossier_verify]
