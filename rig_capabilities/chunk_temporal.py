"""chunk_temporal.py — the durable lane for chunk fan-out.

Doctrine placement (RIG_OWNER_ROUTING_DOCTRINE.md row 3): Temporal owns durable
clock-critical catch-up/recovery with Pydantic AI in ACTIVITIES. Ordinary run-to-completion
belongs to Kestra (row 2), so do not move everyday fan-out here just because it is shinier.

Shape follows the live house pattern (`jacob-x-studio/automation/durable/`): workflow code is
deterministic and does no I/O and no model call; every side effect and every PAIR request
happens in an activity with an explicit RetryPolicy and timeout.

DEPLOYMENT IS THE WHOLE POINT, AND IT IS NOT DONE HERE. Verified 2026-09-15: all three live
Temporal queues (jacob-recruiting-v1, cockpit-refresh-v1, rig-meta-harness) poll from THIS
128GB Mac, so wiring more work onto them would add local load rather than remove it. To
actually free this box the worker process must run ON a remote node, calling that node's own
loopback PAIR (PAIR is loopback-only and cannot be reached across the LAN).

Starting a worker, registering a schedule, or loading a launchd plist are outward activations
and each needs its own Gate-D approval. This module stays dormant until then: importing it
starts nothing.

Run the smoke test with the lane venv (the only interpreter that has both SDKs):
    ~/.rig/state/venvs/chunk-lane/bin/python -m rig_capabilities.chunk_temporal smoke
"""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker

TEMPORAL_TARGET = "127.0.0.1:7233"
TASK_QUEUE = "rig-chunk-fanout-v1"


@dataclass
class ChunkJob:
    """One unit handed to the durable lane. `model` is chosen by rig_capabilities.chunk at plan
    time, because model choice IS node choice under PAIR."""

    chunk_id: str
    prompt: str
    model: str
    max_tokens: int = 512


@dataclass
class ChunkResult:
    chunk_id: str
    status: int
    output: str
    scheduled_on: str = ""


@activity.defn
async def dispatch_chunk(job: ChunkJob) -> ChunkResult:
    """Send one chunk to the LOCAL PAIR of whichever machine this worker runs on.

    Imported lazily and called off the event loop: `chunk._post_chat` is blocking urllib, and
    blocking an activity's loop stalls heartbeats.
    """
    from rig_capabilities import chunk as C

    status, text = await asyncio.to_thread(
        C._post_chat, C.PAIR_BASE, job.model, job.prompt, max_tokens=job.max_tokens, timeout=300
    )
    return ChunkResult(chunk_id=job.chunk_id, status=status, output=text)


@activity.defn
async def prove_placement(models: list[str]) -> dict[str, Any]:
    """Read PAIR's own ledger and report which node each model most recently ran on. Evidence
    for the offload claim; never a pass on its own."""
    from rig_capabilities import chunk as C

    placements = await asyncio.to_thread(C.observed_placements)
    local = await asyncio.to_thread(C.local_node_uuid)
    return {
        "local_node_uuid": local,
        "by_model": {m: sorted(placements.get(m, set())) for m in models},
        "all_remote": all(placements.get(m) and not (placements[m] & {local}) for m in models),
    }


@workflow.defn
class ChunkFanoutWorkflow:
    """Fan chunks out concurrently, then prove where they ran. Deterministic: no I/O here."""

    @workflow.run
    async def run(self, jobs: list[ChunkJob]) -> dict[str, Any]:
        retry = RetryPolicy(
            initial_interval=timedelta(seconds=2),
            backoff_coefficient=2.0,
            maximum_attempts=3,
        )
        pending = [
            workflow.execute_activity(
                dispatch_chunk,
                job,
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=retry,
            )
            for job in jobs
        ]
        results: list[ChunkResult] = list(await asyncio.gather(*pending))
        proof = await workflow.execute_activity(
            prove_placement,
            [job.model for job in jobs],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )
        return {
            "dispatched": len(results),
            "completed": sum(1 for r in results if r.status == 200),
            "failed": sum(1 for r in results if r.status != 200),
            "placement": proof,
            "results": [r.__dict__ for r in results],
        }


async def run_worker(*, target: str = TEMPORAL_TARGET, queue: str = TASK_QUEUE) -> None:
    """Poll forever. Intended to run ON a remote fleet node — running it here defeats the
    purpose. Activation is a Gate-D action."""
    client = await Client.connect(target)
    async with Worker(client, task_queue=queue, workflows=[ChunkFanoutWorkflow], activities=[dispatch_chunk, prove_placement]):
        await asyncio.Event().wait()


async def smoke(*, target: str = TEMPORAL_TARGET) -> dict[str, Any]:
    """Ephemeral proof the lane executes: a worker on a throwaway queue, one workflow, then
    shutdown. Registers no schedule and loads no plist."""
    queue = f"{TASK_QUEUE}-smoke"
    client = await Client.connect(target)
    jobs = [
        ChunkJob(chunk_id="t1", prompt="Name one primary color. One word.", model="qwen3.5:9b", max_tokens=64),
        ChunkJob(chunk_id="t2", prompt="What is 2+2? Digits only.", model="qwen3:4b", max_tokens=64),
    ]
    async with Worker(client, task_queue=queue, workflows=[ChunkFanoutWorkflow], activities=[dispatch_chunk, prove_placement]):
        return await client.execute_workflow(
            ChunkFanoutWorkflow.run,
            jobs,
            id=f"chunk-fanout-smoke-{int(asyncio.get_running_loop().time() * 1000)}",
            task_queue=queue,
        )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "smoke":
        import json

        print(json.dumps(asyncio.run(smoke()), indent=2, default=str))
    elif len(sys.argv) > 1 and sys.argv[1] == "worker":
        asyncio.run(run_worker())
    else:
        print(__doc__)
        raise SystemExit(2)
