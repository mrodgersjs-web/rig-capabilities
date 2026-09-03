"""rig-lattice — one CLI over the whole RIG Lattice System.

    lattice summary                the geometry, as numbers
    lattice cell <cell_id>         parse + resolve + dump the cell contract
    lattice cells                  all 588 canonical ids
    bms score --failure-cost ...   criteria -> confidence -> build mode
    route <intent> [--step I1]     free text -> cell + mode + archetype + budget
    audit <path|->                 40-engine audit: per-engine sigma, RIG-L, BDF
    deviate <path|->               dv deviation pipeline
    des2 <path>                    DES-squared amplification report
    idea score --title T ...       booster score + 4 gates + verdict
    idea grid --candidates FILE    25-niche MAP-Elites menu
    run <path> --confidence C      full L1->L7 orchestration
    engines                        the 40-engine roster
    doctor                         imports, counts, compile freshness, env

Every subcommand takes --json for machine-readable output.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from rig_lattice import __version__


# ── output helpers ─────────────────────────────────────────────────────────

def _emit(data, as_json: bool, human=None) -> int:
    if as_json:
        print(json.dumps(data, indent=2, default=str))
    elif human is not None:
        human(data)
    else:
        print(json.dumps(data, indent=2, default=str))
    return 0


def _read_source(source: str) -> str:
    """Read an artifact from a path or '-' for stdin."""
    if source == "-":
        return sys.stdin.read()
    path = Path(source)
    if not path.exists():
        raise SystemExit(f"no such file: {source}")
    return path.read_text()


# ── lattice ────────────────────────────────────────────────────────────────

def cmd_lattice(args) -> int:
    from rig_lattice.lattice import generator, resolve

    if args.lattice_cmd == "summary":
        data = generator.summary()

        def human(d):
            print(
                f"RIG 3D Lattice v{d['version']}: "
                f"{d['levels']} levels x {d['diamonds']} diamonds x "
                f"{d['bms_modes']} BMS modes x {d['steps']} steps"
            )
            print(
                f"  {d['primary']} primary coordinates -> {d['cells']} cells, "
                f"{d['archetypes']} archetypes"
            )

        return _emit(data, args.json, human)

    if args.lattice_cmd == "cells":
        ids = list(generator.all_cells())
        if args.json:
            return _emit(ids, True)
        print("\n".join(ids))
        return 0

    # cell <cell_id>
    resolved = resolve(args.cell_id)
    data = resolved.to_dict()
    try:
        data["contract"] = generator.load_cell(args.cell_id)
    except RuntimeError as exc:
        data["contract_error"] = str(exc)

    def human(d):
        print(f"{d['cell_id']}  (input: {args.cell_id})")
        print(f"  primary_coordinate:     {d['primary_coordinate']}")
        print(f"  archetype:              {d['archetype']}")
        print(f"  fallback_archetype:     {d['fallback_archetype']}")
        print(f"  diamond_plane:          {d['diamond_plane']}")
        print(f"  step_name:              {d['step_name']}")
        print(f"  bms_name:               {d['bms_name']} ({d['bms_threshold']})")
        print(f"  cost_band:              {d['cost_band']}")
        print(f"  approval:               {d['approval']}")
        print(f"  deterministic:          {d['deterministic']}")
        print(f"  model_in_decision_path: {d['model_in_decision_path']}")

    return _emit(data, args.json, human)


# ── bms ────────────────────────────────────────────────────────────────────

def cmd_bms(args) -> int:
    from rig_lattice.lattice.bms import compute_bms

    result = compute_bms(
        failure_cost=args.failure_cost,
        reversibility=args.reversibility,
        mechanism_clarity=args.mechanism_clarity,
        past_failure_rate=args.past_failure_rate,
        data_volume=args.data_volume,
        level=args.level,
    )
    data = result.to_dict()

    def human(d):
        print(f"BMS {d['confidence']:.4f} -> {d['mode']} {d['mode_name']}")
        print(f"  raw:                    {d['raw']}")
        print(f"  adjustments:            {json.dumps(d['adjustments'])}")
        print(f"  level:                  {d['level']}")
        print(f"  threshold:              {d['threshold']}")
        print(f"  cost_band:              {d['cost_band']} (budget ${d['budget_usd']:.2f})")
        print(f"  deterministic:          {d['deterministic']}")
        print(f"  approval_required:      {d['approval_required']}")

    return _emit(data, args.json, human)


# ── route ──────────────────────────────────────────────────────────────────

def cmd_route(args) -> int:
    from rig_lattice.lattice.wire import route_intent

    result = route_intent(
        args.intent,
        step=args.step,
        domain=args.domain,
        failure_cost=args.failure_cost,
        reversibility=args.reversibility,
        mechanism_clarity=args.mechanism_clarity,
    )
    data = result.to_dict()

    def human(d):
        print(f"{d['cell_id']}  -> archetype {d['archetype']}")
        print(f"  mode:              {d['mode']} (budget ${d['budget_usd']:.2f})")
        print(f"  deterministic:     {d['deterministic']}")
        print(f"  approval_required: {d['approval_required']}")
        print(f"  rationale:         {d['rationale']}")

    return _emit(data, args.json, human)


# ── audit ──────────────────────────────────────────────────────────────────

def cmd_audit(args) -> int:
    from rig_lattice.deviator.auditor import audit_all

    text = _read_source(args.source)
    result = audit_all(text, llm_enabled=args.llm, engines=args.engines or None)

    def human(d):
        print(f"RIG-L {d.get('rig_l', 0):+.2f}   BDF {d.get('bdf', 0):+.2f}   "
              f"status {d.get('status')}   hard_blocks {d.get('hard_blocks')}")
        engines = d.get("engines", {})
        for slug, r in sorted(engines.items(), key=lambda kv: kv[1].get("sigma", 0)):
            print(
                f"  {r.get('codename', slug):26} {r.get('layer', ''):9} "
                f"sigma {r.get('sigma', 0):+7.2f}  {r.get('status', '')}"
            )

    return _emit(result, args.json, human)


# ── deviate ────────────────────────────────────────────────────────────────

def cmd_deviate(args) -> int:
    from rig_lattice.deviator import dv

    argv = [args.source, "--sigma", str(args.sigma)]
    if args.json:
        argv.append("--json")
    return dv.main(argv)


# ── des2 ───────────────────────────────────────────────────────────────────

def cmd_des2(args) -> int:
    from rig_lattice.deviator.auditor import audit_all
    from rig_lattice.deviator.des_squared import amplify

    text = _read_source(args.source)
    audit = audit_all(text, llm_enabled=False)
    result = amplify(audit, text)

    def human(d):
        print(f"DES-squared amplification: {json.dumps(d, indent=2, default=str)}")

    return _emit(result, args.json, human)


# ── idea ───────────────────────────────────────────────────────────────────

def cmd_idea(args) -> int:
    if args.idea_cmd == "score":
        from rig_lattice.idea.booster import evaluate

        corpus: list[str] = []
        if args.corpus:
            corpus_path = Path(args.corpus)
            if not corpus_path.exists():
                raise SystemExit(f"no such corpus file: {args.corpus}")
            corpus = [
                line.strip()
                for line in corpus_path.read_text().splitlines()
                if line.strip()
            ]

        idea = {
            "title": args.title,
            "content": args.content,
            "context": args.context,
            # Counts, not contents: the CLI takes --sources N as the number of
            # receipts so a verdict can be reproduced from the flags alone.
            "sources": [f"source-{i + 1}" for i in range(args.sources)],
            "claims": [f"claim-{i + 1}" for i in range(args.claims)],
            "mechanisms": [f"mechanism-{i + 1}" for i in range(args.mechanisms)],
            "corpus": corpus,
            "cost_band": args.cost_band,
            "time_to_value": args.time_to_value,
        }
        result = evaluate(idea)

        def human(d):
            print(f"verdict: {d['verdict']}")
            print(f"  creativity {d['creativity_score']:.4f}  "
                  f"deviation {d['deviation_score']:.4f}")
            for name, dim in d["dimensions"].items():
                print(f"  {name:18} {dim:.4f}")
            for gate in d["gates"]:
                mark = "PASS" if gate["passed"] else gate["action"].upper()
                print(f"  [{mark:6}] {gate['gate']}: {gate['reason']}")

        return _emit(result, args.json, human)

    # idea grid
    from rig_lattice.idea.mapelites import grid_coverage, mapelites_grid

    path = Path(args.candidates)
    if not path.exists():
        raise SystemExit(f"no such candidates file: {args.candidates}")
    payload = json.loads(path.read_text())
    candidates = payload if isinstance(payload, list) else payload.get("candidates", [])
    grid = mapelites_grid(candidates, seed=args.seed)
    data = {"seed": args.seed, **grid_coverage(grid), "elites": grid}

    def human(d):
        print(f"MAP-Elites seed={d['seed']}  "
              f"{d['niches_filled']}/{d['niches_total']} niches "
              f"({d['coverage']:.0%})")
        for niche, elite in d["elites"].items():
            print(f"  {niche}  C={elite['creativity_score']:.4f}  "
                  f"{elite['title'][:52]}  <- {elite['operator'][:32]}")

    return _emit(data, args.json, human)


# ── run ────────────────────────────────────────────────────────────────────

def cmd_run(args) -> int:
    from rig_lattice.system.orchestrator import run_system

    stdin_text = sys.stdin.read() if args.source == "-" else ""
    result = run_system(
        source=args.source,
        stdin_text=stdin_text,
        confidence=args.confidence,
        force_a4=args.force_a4,
        tier=args.tier,
    )
    data = result.to_dict()

    def human(d):
        print(f"mission {d['mission_id']}  mode {d['bms_mode']}  ok={d['ok']}")
        print(f"  levels {d['levels_completed']}/{d['levels_total']}  "
              f"{d['total_elapsed_ms']:.1f} ms")
        if d["short_circuited_at"]:
            print(f"  short-circuited at {d['short_circuited_at']}")
        for lv in d["level_runs"]:
            print(f"  {lv['level']:4} {lv['mode']:3} ok={str(lv['ok']):5} "
                  f"{lv['reason'][:60]}")

    return _emit(data, args.json, human)


# ── engines ────────────────────────────────────────────────────────────────

def cmd_engines(args) -> int:
    from rig_lattice.core.registry import ENGINE_REGISTRY

    rows = [
        {
            "id": e.id,
            "codename": e.name,
            "slug": e.slug,
            "layer": e.layer,
            "target": e.target,
            "threshold": e.threshold,
            "is_gate": e.is_gate,
        }
        for e in ENGINE_REGISTRY
    ]

    def human(d):
        print(f"{'id':>3}  {'codename':28} {'slug':30} {'layer':10} "
              f"{'target':8} {'thr':>5}  gate")
        for r in d:
            print(f"{r['id']:>3}  {r['codename']:28} {r['slug']:30} "
                  f"{r['layer']:10} {r['target']:8} {r['threshold']:>5.1f}  "
                  f"{'YES' if r['is_gate'] else ''}")

    return _emit(rows, args.json, human)


# ── doctor ─────────────────────────────────────────────────────────────────

def cmd_doctor(args) -> int:
    from rig_lattice._paths import CRITERIA_DIR, RUNS_DIR
    from rig_lattice.core.registry import ENGINE_REGISTRY
    from rig_lattice.lattice import all_cells, archetypes, primary_coordinates
    from rig_lattice.lattice.generator import CELLS_INDEX

    checks: list[dict] = []

    def check(name: str, ok: bool, detail: str) -> None:
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    cells = all_cells()
    check("cells_588", len(cells) == 588 and len(set(cells)) == 588,
          f"{len(cells)} cells, {len(set(cells))} unique")
    check("primary_84", len(primary_coordinates()) == 84,
          f"{len(primary_coordinates())} primary coordinates")
    check("archetypes_28", len(set(archetypes())) == 28,
          f"{len(set(archetypes()))} archetypes")
    check("engines_40", len(ENGINE_REGISTRY) == 40,
          f"{len(ENGINE_REGISTRY)} engines in the registry")

    yaml_packs = sorted(p.stem for p in CRITERIA_DIR.glob("*.yaml"))
    json_packs = sorted(p.stem for p in CRITERIA_DIR.glob("*.json"))
    check("criteria_compiled", yaml_packs == json_packs,
          f"{len(yaml_packs)} yaml / {len(json_packs)} json"
          + ("" if yaml_packs == json_packs else " — run scripts/compile_criteria.py"))
    check("cells_index", CELLS_INDEX.exists(),
          str(CELLS_INDEX) if CELLS_INDEX.exists() else "missing cells.json")

    engine_import_errors: list[str] = []
    for layer in ("cognitive", "nature", "physics"):
        try:
            __import__(f"rig_lattice.engines.{layer}")
        except Exception as exc:  # pragma: no cover - import health check
            engine_import_errors.append(f"{layer}: {exc}")
    check("engine_layers_import", not engine_import_errors,
          "; ".join(engine_import_errors) or "cognitive, nature, physics import")

    try:
        import yaml  # noqa: F401

        pyyaml = "installed (dev-time only)"
    except ImportError:
        pyyaml = "absent — fine, runtime reads compiled JSON"
    check("pyyaml_optional", True, pyyaml)

    check("runs_dir_writable", os.access(RUNS_DIR.parent, os.W_OK),
          f"{RUNS_DIR} (override with RIG_LATTICE_RUNS_DIR)")

    env = {
        key: os.environ.get(key) or "<unset>"
        for key in (
            "RIG_LATTICE_LLM_URL",
            "RIG_LATTICE_LLM_MODEL",
            "RIG_LATTICE_RUNS_DIR",
            "RIG_DV_LLM_URL",
            "RIG_DV_OFFLINE",
            "RIG_DV_AUTO_APPROVE",
        )
    }
    data = {
        "version": __version__,
        "ok": all(c["ok"] for c in checks),
        "checks": checks,
        "env": env,
    }

    def human(d):
        print(f"rig-lattice {d['version']}  ->  {'OK' if d['ok'] else 'PROBLEMS'}")
        for c in d["checks"]:
            print(f"  [{'ok' if c['ok'] else 'FAIL'}] {c['check']:22} {c['detail']}")
        print("  env:")
        for k, v in d["env"].items():
            print(f"    {k:24} {v}")

    _emit(data, args.json, human)
    return 0 if data["ok"] else 1


# ── parser ─────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    # --json is attached to every (sub)parser through this parent, so it works
    # wherever the user puts it: `rig-lattice --json lattice summary` and
    # `rig-lattice lattice summary --json` both parse.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="machine-readable output",
    )

    p = argparse.ArgumentParser(
        prog="rig-lattice",
        parents=[common],
        description="RIG Lattice System — 588-cell router, 40 engines, idea gates",
    )
    p.add_argument("--version", action="version", version=f"rig-lattice {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    # lattice
    lat = sub.add_parser("lattice", parents=[common],
                          help="lattice geometry and cell contracts")
    lat_sub = lat.add_subparsers(dest="lattice_cmd", required=True)
    lat_sub.add_parser("summary", parents=[common], help="the geometry as numbers")
    lat_sub.add_parser("cells", parents=[common], help="all 588 canonical cell ids")
    cell = lat_sub.add_parser("cell", parents=[common], help="resolve one cell id")
    cell.add_argument("cell_id", help="any accepted dialect, e.g. L3-D2-A2-R")
    lat.set_defaults(func=cmd_lattice)

    # bms
    bms = sub.add_parser("bms", parents=[common], help="BMS confidence scoring")
    bms_sub = bms.add_subparsers(dest="bms_cmd", required=True)
    score = bms_sub.add_parser("score", parents=[common],
                                help="criteria -> confidence -> mode")
    score.add_argument("--failure-cost", type=float, default=0.5)
    score.add_argument("--reversibility", type=float, default=0.5)
    score.add_argument("--mechanism-clarity", type=float, default=0.5)
    score.add_argument("--past-failure-rate", type=float, default=0.0)
    score.add_argument("--data-volume", type=float, default=0.5)
    score.add_argument("--level", default="L2", help="L1..L7 (altitude bonus)")
    bms.set_defaults(func=cmd_bms)

    # route
    route = sub.add_parser("route", parents=[common], help="free text -> lattice cell")
    route.add_argument("intent")
    route.add_argument("--step", default="I1", help="IQRSQPI step (default I1)")
    route.add_argument("--domain", default="")
    route.add_argument("--failure-cost", type=float, default=0.5)
    route.add_argument("--reversibility", type=float, default=0.5)
    route.add_argument("--mechanism-clarity", type=float, default=0.5)
    route.set_defaults(func=cmd_route)

    # audit
    audit = sub.add_parser("audit", parents=[common], help="40-engine strict audit")
    audit.add_argument("source", help="path or '-' for stdin")
    audit.add_argument("--tier", default="client")
    audit.add_argument("--engines", nargs="*", help="limit to these slugs")
    audit.add_argument("--llm", action="store_true",
                        help="enable llm_judge questions (needs RIG_LATTICE_LLM_URL)")
    audit.set_defaults(func=cmd_audit)

    # deviate
    dev = sub.add_parser("deviate", parents=[common], help="dv deviation pipeline")
    dev.add_argument("source", help="path or '-' for stdin")
    dev.add_argument("--sigma", type=int, default=20)
    dev.set_defaults(func=cmd_deviate)

    # des2
    des2 = sub.add_parser("des2", parents=[common],
                           help="DES-squared amplification report")
    des2.add_argument("source", help="path or '-' for stdin")
    des2.set_defaults(func=cmd_des2)

    # idea
    idea = sub.add_parser("idea", parents=[common],
                           help="deterministic idea scoring and generation")
    idea_sub = idea.add_subparsers(dest="idea_cmd", required=True)
    isc = idea_sub.add_parser("score", parents=[common],
                               help="booster score + 4 gates + verdict")
    isc.add_argument("--title", required=True)
    isc.add_argument("--content", default="")
    isc.add_argument("--context", default="")
    isc.add_argument("--sources", type=int, default=0, help="number of cited sources")
    isc.add_argument("--claims", type=int, default=0, help="number of claims")
    isc.add_argument("--mechanisms", type=int, default=0, help="number of mechanisms")
    isc.add_argument("--corpus", help="file of reference lines, one per line")
    isc.add_argument("--cost-band", type=float, default=0.5)
    isc.add_argument("--time-to-value", type=float, default=0.5)
    grid = idea_sub.add_parser("grid", parents=[common],
                                help="25-niche MAP-Elites menu")
    grid.add_argument("--candidates", required=True, help="JSON list of ideas")
    grid.add_argument("--seed", type=int, required=True, help="required: runs replay")
    idea.set_defaults(func=cmd_idea)

    # run
    run = sub.add_parser("run", parents=[common], help="full L1->L7 orchestration")
    run.add_argument("source", help="path or '-' for stdin")
    run.add_argument("--confidence", type=float, default=0.75)
    run.add_argument("--force-a4", action="store_true")
    run.add_argument("--tier", default="client")
    run.set_defaults(func=cmd_run)

    # engines
    eng = sub.add_parser("engines", parents=[common], help="the 40-engine roster")
    eng.set_defaults(func=cmd_engines)

    # doctor
    doc = sub.add_parser("doctor", parents=[common],
                          help="imports, counts, compile freshness, env")
    doc.set_defaults(func=cmd_doctor)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
