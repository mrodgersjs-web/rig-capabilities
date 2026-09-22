"""W03 CLI -- imports the handler directly. Exit codes are the contract:
0 ok · 1 refused/conflict · 3 usage. The console and MCP arrive at the same
execute(); this file adds no logic of its own."""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime.commands import execute, DEFAULT_DB
from runtime.ledger import Ledger


def _actor(kind):
    return {"kind": kind, "id": kind + "-cli"}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="uplan", description="UltraPlan command CLI")
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--as", dest="actor", default="cli",
                    help="authenticated actor kind (human|cli|mcp|ui|worker) -- set by the transport's auth, not by wishful callers")
    ap.add_argument("--seq", type=int, default=None, help="expected_seq guard")
    ap.add_argument("--fence", nargs=2, metavar=("KEY", "TOKEN"))
    ap.add_argument("--idem", default=None)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("create"); p.add_argument("mission_id"); p.add_argument("goal")
    p = sub.add_parser("advance"); p.add_argument("mission_id"); p.add_argument("--to", required=True)
    for name in ("park", "resume", "cancel", "abandon", "complete"):
        p = sub.add_parser(name); p.add_argument("mission_id")
    p = sub.add_parser("receipt"); p.add_argument("mission_id"); p.add_argument("effect", help="json object")
    p = sub.add_parser("status"); p.add_argument("mission_id")
    p = sub.add_parser("verify"); p.add_argument("mission_id")
    p = sub.add_parser("replay"); p.add_argument("mission_id")

    args = ap.parse_args(argv)

    if args.cmd in ("status", "verify", "replay"):
        lg = Ledger(args.db)
        if args.cmd == "status":
            print(json.dumps(lg.rebuild_projection(args.mission_id)))
            return 0
        if args.cmd == "verify":
            ok = lg.verify_chain(args.mission_id)
            print("chain-intact" if ok else "CHAIN BROKEN")
            return 0 if ok else 1
        lg.db.execute("DELETE FROM missions WHERE mission_id=?", (args.mission_id,))
        proj = lg.rebuild_projection(args.mission_id)
        live = lg.db.execute("SELECT state,seq,hash FROM missions WHERE mission_id=?",
                             (args.mission_id,)).fetchone()
        same = live and live["hash"] == proj["hash"] and live["seq"] == proj["seq"]
        print(json.dumps({"rebuilt": proj, "matches_live_projection": bool(same)}))
        return 0 if same else 1

    ctype = {"create": "mission.create", "advance": "stage.advance", "park": "stage.park",
             "resume": "stage.resume", "cancel": "mission.cancel", "abandon": "mission.abandon",
             "complete": "mission.complete", "receipt": "receipt.attach"}[args.cmd]
    payload = {}
    if args.cmd == "create":
        payload = {"goal": args.goal}
    elif args.cmd == "advance":
        payload = {"to": args.to}
    elif args.cmd == "receipt":
        payload = json.loads(args.effect)
    if args.fence:
        payload["fence_key"], payload["fence_token"] = args.fence
    command = {"schema_version": "1", "ts": _now(), "actor": args.actor,
               "mission_id": args.mission_id, "command_id": str(uuid.uuid4()),
               "idempotency_key": args.idem or "cli-" + str(uuid.uuid4())[:12],
               "type": ctype, "payload": payload}
    if args.seq is not None:
        command["expected_seq"] = args.seq
    res = execute(command, _actor(args.actor), db_path=args.db)
    print(json.dumps(res))
    return 0 if res.get("ok") else 1


def _now():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


if __name__ == "__main__":
    sys.exit(main())
