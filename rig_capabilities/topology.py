"""Declared-topology edge-check for agent dispatch — stdlib only, pure.

A loop that runs more than one agent must DECLARE the graph its agents may
communicate on — topology kind, fixed agent count, per-agent input/output
contracts, and the allowed message edges — and dispatch is legal only along
a declared edge. Before an agent is invoked, the loop asserts:

  1. the edge it is about to traverse exists in the declared graph;
  2. what it will pass matches the callee's declared input contract (and the
     sender's declared output contract);
  3. the edge does not introduce a cycle — a node waiting on its own
     descendant is a deadlock, not orchestration.

Graph shape (JSON, or fenced ```rig-topology blocks inside a markdown loop):

  {
    "topology": "boss" | "orchestrator" | "flat-swarm",
    "root": "<agent id>",                 # required for boss/orchestrator
    "agent_count": <int>,                 # the count is FIXED by the declaration
    "agents": [
      {"id": ..., "family": ..., "input_contract": [...], "output_contract": [...]}
    ],
    "edges": [
      {"from": ..., "to": ..., "payload": ..., "kind": "dispatch"|"deliver"}
    ]
  }

Edge kinds: `dispatch` opens a wait (the sender holds for the callee's
answer); `deliver` closes one (a response travelling back). Deadlock is a
cycle of DISPATCH edges, so cycle detection runs on dispatch edges only —
that is exactly "a graph node waiting on its own descendant". A graph that
validates clean is acyclic on waiting by construction.

Verdict vocabulary (machine-readable strings; validate() returns a list):

  declaration_missing:<key>          required key absent — nothing downstream is trustworthy
  topology_undeclared:<value>        topology outside the closed enum
  agent_malformed:<index>            agent row is not a mapping with a string id
  duplicate_agent:<id>               two agents share one id
  agent_count_mismatch:<n>!=<m>      declared count != actual agents
  root_undeclared:<value>            root absent/unlisted where the topology demands it
  undefined_edge:<from>-><to>        edge endpoints are not declared agents
  edge_kind_invalid:<from>-><to>:<kind>   kind outside dispatch|deliver
  duplicate_edge:<from>-><to>:<payload>   same triple declared twice
  contract_mismatch:<from>-><to>:<payload>:<not_in_output|not_in_input|payload_missing>
  unreachable_agent:<id>             declared agent no legal message can ever reach
  cycle_at:<node1,node2,...>         dispatch-edge cycle through these nodes

Purity: validate() and check_dispatch() never write, never mutate their
input, never network, never sleep. mutate() is a pure fixture generator that
operates on a deep copy (it exists so a declared graph can prove — from the
loop file itself — that each verdict class actually fires).

Exit codes (CLI): 0 = clean, or a planted-fault expectation met; 1 = refused
(any verdict without --expect, or an --expect prefix absent from the verdicts);
2 = argparse usage error or unparseable graph (never green-on-noise).

Mechanism attribution: video ids lNlMXsUQggc, Z90xlttVx3Y;
arXiv:2608.21156, arXiv:2608.27969.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys

TOPOLOGIES = ("boss", "orchestrator", "flat-swarm")
EDGE_KINDS = ("dispatch", "deliver")
REQUIRED_KEYS = ("topology", "agent_count", "agents", "edges")
MUTATIONS = ("cycle", "ghost", "contract", "unreachable")

_FENCE = re.compile(r"```rig-topology\s*\n(.*?)```", re.S)


def _is_str(v) -> bool:
    return isinstance(v, str) and v.strip() != ""


def _contracts(agent, key: str) -> tuple:
    c = agent.get(key) if isinstance(agent, dict) else None
    if not isinstance(c, list):
        return ()
    return tuple(x for x in c if _is_str(x))


def extract_graphs(markdown: str) -> list:
    """Parse every ```rig-topology fenced block in a markdown loop file.

    Raises ValueError on a block that is not a JSON object — an unparseable
    declaration is a broken declaration, not an absent one.
    """
    graphs = []
    for i, block in enumerate(_FENCE.findall(markdown)):
        try:
            g = json.loads(block)
        except ValueError as e:
            raise ValueError(f"rig-topology block #{i + 1} is not valid JSON: {e}")
        if not isinstance(g, dict):
            raise ValueError(f"rig-topology block #{i + 1} is not a JSON object")
        graphs.append(g)
    return graphs


def _agent_rows(graph):
    """Return (ids, agents_by_id, malformed_indices). Tolerant of junk rows."""
    ids, bad = [], []
    for i, a in enumerate(graph.get("agents") or []):
        if isinstance(a, dict) and _is_str(a.get("id")):
            ids.append(a["id"])
        else:
            bad.append(i)
    return ids, {a["id"]: a for a in (graph.get("agents") or [])
                 if isinstance(a, dict) and _is_str(a.get("id"))}, bad

def _dispatch_cycles(adj, nodes):
    """Cycles in the dispatch sub-graph, each reported once as a node list."""
    WHITE, GREY, BLACK = 0, 1, 2
    color = {n: WHITE for n in nodes}
    cycles, seen = [], set()
    for start in nodes:
        if color[start] != WHITE:
            continue
        color[start] = GREY
        path = [start]
        stack = [(start, iter(adj.get(start, ())))]
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                color[node] = BLACK
                stack.pop()
                path.pop()
                continue
            if color[nxt] == GREY:
                cyc = path[path.index(nxt):]
                key = frozenset(cyc)
                if key not in seen:
                    seen.add(key)
                    cycles.append(cyc)
            elif color[nxt] == WHITE:
                color[nxt] = GREY
                path.append(nxt)
                stack.append((nxt, iter(adj.get(nxt, ()))))
    return cycles


def validate(graph) -> list:
    """Verdicts for a declared topology graph. [] = the declaration is sound.

    Never mutates `graph`, never touches the filesystem or network.
    """
    if not isinstance(graph, dict):
        return ["declaration_missing:mapping"]
    missing = [k for k in REQUIRED_KEYS if k not in graph]
    if missing:
        # A declaration with a missing limb cannot be edge-checked at all.
        return [f"declaration_missing:{k}" for k in missing]

    v: list = []
    if graph["topology"] not in TOPOLOGIES:
        v.append(f"topology_undeclared:{graph['topology']}")

    if not isinstance(graph["agents"], list):
        v.append("agent_malformed:not_a_list")
        ids, by_id, bad = [], {}, []
    else:
        ids, by_id, bad = _agent_rows(graph)
        for i in bad:
            v.append(f"agent_malformed:{i}")
        for aid in sorted({i for i in ids if ids.count(i) > 1}):
            v.append(f"duplicate_agent:{aid}")

    declared_n = graph["agent_count"]
    if not isinstance(declared_n, int) or declared_n != len(ids):
        v.append(f"agent_count_mismatch:{declared_n}!={len(ids)}")

    root = graph.get("root")
    root_ok = _is_str(root) and root in by_id
    if graph["topology"] in ("boss", "orchestrator"):
        if not root_ok:
            v.append(f"root_undeclared:{root if _is_str(root) else 'none'}")
    elif root is not None and not root_ok:
        v.append(f"root_undeclared:{root}")

    if not isinstance(graph["edges"], list):
        v.append("undefined_edge:edges:not_a_list")
        return v

    seen_triples = set()
    adj: dict = {}
    live_edges = []  # endpoint-valid edges, for reachability + cycles
    for e in graph["edges"]:
        if not isinstance(e, dict):
            v.append("undefined_edge:malformed_row")
            continue
        src, dst = e.get("from"), e.get("to")
        payload, kind = e.get("payload"), e.get("kind", "dispatch")
        endpoints_ok = _is_str(src) and _is_str(dst) and src in by_id and dst in by_id
        if not endpoints_ok:
            v.append(f"undefined_edge:{src}->{dst}")
        if kind not in EDGE_KINDS:
            v.append(f"edge_kind_invalid:{src}->{dst}:{kind}")
            continue  # an edge whose kind is unknown cannot be trusted in either graph
        triple = (src, dst, payload)
        if triple in seen_triples:
            v.append(f"duplicate_edge:{src}->{dst}:{payload}")
        seen_triples.add(triple)
        if endpoints_ok:
            live_edges.append(e)
            if kind == "dispatch":
                adj.setdefault(src, []).append(dst)
            # Contracts are what cross the edge, whatever its kind.
            if not _is_str(payload):
                v.append(f"contract_mismatch:{src}->{dst}:none:payload_missing")
            else:
                if payload not in _contracts(by_id[src], "output_contract"):
                    v.append(f"contract_mismatch:{src}->{dst}:{payload}:not_in_output")
                if payload not in _contracts(by_id[dst], "input_contract"):
                    v.append(f"contract_mismatch:{src}->{dst}:{payload}:not_in_input")

    # A declared agent that no legal message can ever reach is the row-level
    # failure mode: "a handoff packet whose declared reviewer is unreachable
    # on every allowed edge". Seeds: the root; for flat-swarm (no root), the
    # senders — agents nobody dispatches to.
    if by_id:
        dispatched_targets = {e["to"] for e in live_edges if e.get("kind", "dispatch") == "dispatch"}
        if root_ok:
            seeds = {root}
        else:
            seeds = {i for i in ids if i not in dispatched_targets}
        reachable = set(seeds)
        grew = True
        while grew:
            grew = False
            for e in live_edges:
                if e["from"] in reachable and e["to"] not in reachable:
                    reachable.add(e["to"])
                    grew = True
        for aid in ids:
            if aid not in reachable:
                v.append(f"unreachable_agent:{aid}")

        for cyc in _dispatch_cycles(adj, ids):
            v.append("cycle_at:" + ",".join(cyc))
    return v


def check_dispatch(graph, src: str, dst: str, payload: str) -> list:
    """Verdicts for the ONE edge dispatch is about to traverse. [] = legal.

    This is the pre-invocation assert. It returns verdicts; refusing is the
    caller's dispatch loop's job — exit 1, name the verdict, do NOT silently
    reorder, re-route, or drop the hop.
    """
    v: list = []
    if not isinstance(graph, dict):
        return ["declaration_missing:mapping"]
    _, by_id, _ = _agent_rows(graph)
    if src not in by_id or dst not in by_id:
        v.append(f"undefined_edge:{src}->{dst}")
    edges = graph.get("edges") if isinstance(graph.get("edges"), list) else []
    if not any(isinstance(e, dict) and e.get("from") == src and e.get("to") == dst
               and e.get("payload") == payload for e in edges):
        v.append(f"undefined_edge:{src}->{dst}")
    if src in by_id and payload not in _contracts(by_id[src], "output_contract"):
        v.append(f"contract_mismatch:{src}->{dst}:{payload}:not_in_output")
    if dst in by_id and payload not in _contracts(by_id[dst], "input_contract"):
        v.append(f"contract_mismatch:{src}->{dst}:{payload}:not_in_input")
    # Deduplicate: an unknown endpoint yields one undefined_edge, not two.
    return list(dict.fromkeys(v))


def mutate(graph, kind: str) -> dict:
    """Pure fixture generator: a deep copy with one named defect planted.

    `cycle`        — close a dispatch loop along the declared agent order.
    `ghost`        — add an edge from an undeclared node.
    `contract`     — strip one input type from the first declared agent.
    `unreachable`  — remove every dispatch edge into the first non-root agent.
    """
    if kind not in MUTATIONS:
        raise ValueError(f"unknown mutation '{kind}'. Options: {list(MUTATIONS)}")
    g = copy.deepcopy(graph)
    agents = g.get("agents") or []
    if not agents:
        raise ValueError("cannot mutate a graph with no declared agents")
    first, last = agents[0].get("id"), agents[-1].get("id")
    if kind == "cycle":
        pay = next((e.get("payload") for e in g["edges"]
                    if isinstance(e, dict) and e.get("from") == last
                    and e.get("kind") == "deliver" and _is_str(e.get("payload"))), None)
        if pay is None:
            ins = _contracts(agents[0], "input_contract")
            pay = ins[0] if ins else "undeclared_payload"
        g["edges"].append({"from": last, "to": first, "payload": pay, "kind": "dispatch"})
    elif kind == "ghost":
        ins = _contracts(agents[0], "input_contract")
        g["edges"].append({"from": "ghost-node", "to": first,
                           "payload": ins[0] if ins else "undeclared_payload",
                           "kind": "dispatch"})
    elif kind == "contract":
        ic = list(_contracts(agents[0], "input_contract"))
        g["agents"][0]["input_contract"] = ic[1:]
    elif kind == "unreachable":
        root = g.get("root")
        target = next((a.get("id") for a in agents
                       if _is_str(a.get("id")) and a.get("id") != root), None)
        g["edges"] = [e for e in g["edges"]
                      if not (isinstance(e, dict) and e.get("to") == target
                              and e.get("kind", "dispatch") == "dispatch")]
    return g


def _load(path: str):
    """Read a .json graph or a .md loop file's declared graphs. None = unparseable."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if path.endswith(".md"):
        try:
            graphs = extract_graphs(text)
        except ValueError as e:
            print(f"graph_unparseable:{path}: {e}")
            return None
        if not graphs:
            print(f"graph_unparseable:{path}: no ```rig-topology block found")
            return None
        return graphs
    try:
        return [json.loads(text)]
    except ValueError as e:
        print(f"graph_unparseable:{path}: {e}")
        return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="python3 -m rig_capabilities.topology",
        description="Edge-check agent dispatch against a declared topology.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    pv = sub.add_parser("validate", help="validate every declared graph in a .json/.md file")
    pv.add_argument("path")
    pv.add_argument("--mutate", choices=MUTATIONS,
                    help="plant one named defect first (on a copy) — for plant-failure checks")
    pv.add_argument("--expect", action="append", default=[], metavar="PREFIX",
                    help="exit 0 only if a verdict with this prefix fires (repeatable)")

    pd = sub.add_parser("dispatch", help="pre-invocation check of one hop: src -> dst : payload")
    pd.add_argument("path")
    pd.add_argument("src")
    pd.add_argument("dst")
    pd.add_argument("payload")
    pd.add_argument("--expect", action="append", default=[], metavar="PREFIX")

    args = ap.parse_args(argv)
    graphs = _load(args.path)
    if graphs is None:
        return 2

    if args.cmd == "validate":
        if args.mutate:
            graphs = [mutate(g, args.mutate) for g in graphs]
        verdicts = [x for g in graphs for x in validate(g)]
        for x in verdicts:
            print(x)
        if not verdicts:
            print(f"OK {args.path} ({len(graphs)} declared graph(s), acyclic on dispatch)")
        if args.expect:
            return 0 if all(any(x.startswith(e) for x in verdicts) for e in args.expect) else 1
        return 1 if verdicts else 0

    # dispatch: the whole declaration must validate before any hop is trusted
    graph = graphs[0]
    graph_v = validate(graph)
    edge_v = check_dispatch(graph, args.src, args.dst, args.payload)
    for x in graph_v:
        print(f"graph {x}")
    for x in edge_v:
        print(f"refuse {x}")
    if not graph_v and not edge_v:
        print(f"LEGAL {args.src} -> {args.dst} : {args.payload}")
    if args.expect:
        return 0 if (not graph_v
                     and all(any(x.startswith(e) for x in edge_v) for e in args.expect)) else 1
    return 1 if (graph_v or edge_v) else 0


if __name__ == "__main__":
    sys.exit(main())
