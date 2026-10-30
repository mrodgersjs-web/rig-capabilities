"""Operator CLI. Explicit commands perform probes, bundle builds, or dispatch."""
import argparse
import json
import sys
import uuid
from pathlib import Path

from .baseline import build_profile_bundle, profile_release_id
from .dispatcher import Dispatcher
from .daemon import FleetDaemon
from .inventory import InventoryProbe
from .registry import NODE_REGISTRY
from .store import FleetStore


def store(path): return FleetStore(path, profile_release_id())


def main(argv=None):
    parser = argparse.ArgumentParser(prog='rig-hq-fleet')
    parser.add_argument('--database', default=str(Path.home()/'.rig/jake/aos/hq-workspace/fleet.sqlite3'))
    commands = parser.add_subparsers(dest='command', required=True)
    bundle = commands.add_parser('bundle'); bundle.add_argument('--output', required=True)
    inventory = commands.add_parser('inventory'); inventory.add_argument('--node', choices=NODE_REGISTRY, required=True)
    commands.add_parser('inventory-all'); commands.add_parser('dispatch-once'); commands.add_parser('refresh-running'); commands.add_parser('daemon')
    configure = commands.add_parser('configure-coordinator')
    configure.add_argument('--handle', required=True); configure.add_argument('--run-id', required=True)
    submit = commands.add_parser('submit')
    submit.add_argument('--kind', choices=('interactive','diagnostics','research','bulk_scan'), required=True)
    submit.add_argument('--role', choices=('planner','provisioner','replication','repair','verifier','rollback'), required=True)
    submit.add_argument('--target', choices=('auto','local128','rig256gb','rig96gb'), default='auto')
    submit.add_argument('--writer-scope', default=''); submit.add_argument('--idempotency-key'); submit.add_argument('--task')
    for name in ('status', 'result'):
        command = commands.add_parser(name); command.add_argument('--job', required=True)
    args = parser.parse_args(argv)
    if args.command == 'bundle': result = build_profile_bundle(args.output)
    else:
        database = store(args.database)
        if args.command == 'inventory': result = database.record_inventory(args.node, InventoryProbe().collect(args.node))
        elif args.command == 'inventory-all': result = [database.record_inventory(node, InventoryProbe().collect(node)) for node in NODE_REGISTRY]
        elif args.command == 'dispatch-once': result = Dispatcher(database).launch_one()
        elif args.command == 'refresh-running': result = [Dispatcher(database).refresh(job) for job in database.list_jobs(200) if job['state'] == 'running']
        elif args.command == 'daemon':
            FleetDaemon(database).run(); result = {'stopped': True}
        elif args.command == 'configure-coordinator': result = database.configure_coordinator(args.handle, args.run_id)
        elif args.command == 'submit':
            task = args.task if args.task is not None else sys.stdin.read()
            result = database.enqueue({'task': task, 'target': args.target, 'writer_scope': args.writer_scope,
                'idempotency_key': args.idempotency_key or str(uuid.uuid4()), 'capability': args.role, 'kind': args.kind})
        else:
            result = database.get_job(args.job)
            if result is None: raise SystemExit('job not found')
            if args.command == 'result': result = {key: result[key] for key in ('id','state','node_id','result','error','receipt','finished_at')}
    print(json.dumps({'ok': True, 'result': result}, sort_keys=True))


if __name__ == '__main__': main()
