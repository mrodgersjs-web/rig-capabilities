"""Task-queue worker process (supervised by launchd on rig256gb). One process serves
all seven GTM entity workflows on queue 'gtm'; Temporal relocations make it stateless."""
from __future__ import annotations
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from . import config
from .activities import ALL_ACTIVITIES
from .workflows import (UpworkBidder, EmailOutreach, LeadSourcer, LinkedinGtm,
                        GtmLead, GtmHead, GtmWatchdog, WorkerLoop)
from .w1a_sentinel import SentinelVerifier, SENTINEL_ACTIVITIES
from .w1a_dossier import DossierBuilder, DOSSIER_ACTIVITIES


async def main() -> None:
    client = await Client.connect(config.TEMPORAL_ADDR, namespace=config.NAMESPACE)
    worker = Worker(client, task_queue=config.TASK_QUEUE,
                    workflows=[UpworkBidder, EmailOutreach, LeadSourcer, LinkedinGtm, WorkerLoop,
                               GtmLead, GtmHead, GtmWatchdog,
                               SentinelVerifier, DossierBuilder],
                    activities=ALL_ACTIVITIES + SENTINEL_ACTIVITIES + DOSSIER_ACTIVITIES)
    print("gtm worker up on", config.TASK_QUEUE, flush=True)
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
