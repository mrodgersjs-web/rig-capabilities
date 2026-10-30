"""Start the seven GTM entity workflows (id = agent name = single-writer lock).
Idempotent: running ids are reported, not restarted."""
from __future__ import annotations
import asyncio
from temporalio.client import Client
from temporalio.api.enums.v1 import WorkflowIdReusePolicy as WorkflowIDReusePolicy
from . import config
from .workflows import (UpworkBidder, EmailOutreach, LeadSourcer, LinkedinGtm,
                        GtmLead, GtmHead, GtmWatchdog, WorkerLoop)
from .w1a_sentinel import SentinelVerifier
from .w1a_dossier import DossierBuilder

MAP = {
    "upwork-bidder": UpworkBidder, "email-outreach": EmailOutreach,
    "lead-sourcer": LeadSourcer, "linkedin-gtm": LinkedinGtm,
    "gtm-lead": GtmLead, "gtm-head": GtmHead, "gtm-watchdog": GtmWatchdog,
    "sentinel-verifier": SentinelVerifier, "dossier-builder": DossierBuilder,
}
# static args per workflow run signature (DossierBuilder.run(limit))
ARGS = {"dossier-builder": [25]}
# 7 new W1b workers on the generic loop: (activity, cadence from config)
LOOP = {
    "enrich-verify": "enrich_cycle", "icp-scorer": "icp_cycle",
    "reply-handler": "reply_cycle", "linkedin-events": "linkedin_events_cycle",
    "phone-calls": "phone_cycle", "web-analytics": "web_analytics_cycle",
    "website-cro": "cro_cycle",
}


async def main() -> None:
    client = await Client.connect(config.TEMPORAL_ADDR, namespace=config.NAMESPACE)
    todo = dict(MAP)
    for wid, act in LOOP.items():
        todo[wid] = ("loop", act)
    for wid, wf in todo.items():
        try:
            args: list = list(ARGS.get(wid, []))
            if isinstance(wf, tuple):
                act = wf[1]
                args = [wid, act, config.AGENTS[wid]["cadence_s"]]
                wf = WorkerLoop
            h = await client.start_workflow(
                wf.run, args=args, id=wid, task_queue=config.TASK_QUEUE,
                id_reuse_policy=WorkflowIDReusePolicy.WORKFLOW_ID_REUSE_POLICY_ALLOW_DUPLICATE,
            )
            print(f"started {wid} run={h.result_run_id}")
        except Exception as ex:
            s = str(ex)
            if "ALREADY_EXISTS" in s or "already started" in s.lower() or "WorkflowAlreadyStarted" in type(ex).__name__:
                print(f"already running {wid}")
            else:
                print(f"FAILED {wid}: {type(ex).__name__} {s[:200]}")


if __name__ == "__main__":
    asyncio.run(main())
