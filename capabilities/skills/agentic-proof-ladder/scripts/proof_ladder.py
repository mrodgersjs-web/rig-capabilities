#!/usr/bin/env python3
"""Validate an agentic-setup proof receipt against the L0-L5 ladder. Fail closed.

Ladder (agentic-systems-setup):
  L0 docs    official install/quickstart page fetched on the receipt date; URL, sha256, pinned version
  L1 install installed in the named route; command, exit 0, observed version
  L2 hello   hello run against a deterministic fake/test model; command, exit 0, assertion, observed
  L3 local   same hello against a LOCAL endpoint (loopback or LAN, never a paid vendor host);
             command, exit 0, endpoint, model, observed non-empty content
  L4 feature a durable or observed feature exercised (kill-and-resume, retry, checkpoint, trace);
             feature, command, exit 0, observed, run_id
  L5 deploy  deployed or published; REQUIRES a Gate-D approval_id, target, command, exit 0

Rules (each violation prints "P<n> ..."):
  P1 receipt shape: framework, skill, route, date, levels{} present
  P2 contiguity: a claimed level needs every lower level claimed (a BLOCKED level ends the ladder)
  P3 required fields per level present and non-empty; claimed levels must have exit 0
  P4 L0 docs must be https URLs fetched on the receipt date with a sha
  P5 L2 model must be deterministic (fake/test/stub/echo/function)
  P6 L3 endpoint must be local (127.0.0.1, localhost, 192.168.x, 10.x, host.docker.internal)
  P7 L5 without approval_id is a deploy without Gate-D
  P8 blocked entries need level, reason, and check, and a level cannot be claimed and blocked
  P9 no raw secret value in the receipt (token-shaped strings)

Step-list receipts (the worker format: a JSON LIST of {step, command, exit_code, observed, at})
are accepted in STEP mode: every row must carry those five fields with non-empty command and
observed text and an integer or null exit code (S1; null = never returned, never a success), and no token-shaped secret (P9). STEP mode cannot
prove contiguity or Gate-D, so it reports the level tokens (L0-L5) named by steps that exited 0
and says so; it never prints a ladder level. Anything that is neither a dict nor a list is P1.

Usage: proof_ladder.py RECEIPT.json [--plant NAME]
Plants mutate an in-memory copy; exit 2 = CAUGHT, 0 = ESCAPED:
  skip_level->P2, missing_field->P3, stale_docs->P4, paid_model_l2->P5, paid_endpoint_l3->P6,
  deploy_no_approval->P7, secret_in_receipt->P9
Exit 0 clean (prints the highest proven level), 2 violations, 1 usage. Stdlib only.
"""
from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

LEVELS = ["L0", "L1", "L2", "L3", "L4", "L5"]
REQUIRED = {
    "L0": ["docs", "version_pinned"],
    "L1": ["command", "exit", "version_observed"],
    "L2": ["command", "exit", "model", "assertion", "observed"],
    "L3": ["command", "exit", "endpoint", "model", "observed"],
    "L4": ["feature", "command", "exit", "observed", "run_id"],
    "L5": ["approval_id", "target", "command", "exit"],
}
FAKE = re.compile(r"(?i)\b(fake|test|stub|echo|function|scripted|deterministic|mock)")
LOCAL = re.compile(r"^https?://(127\.0\.0\.1|localhost|0\.0\.0\.0|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|host\.docker\.internal)(:\d+)?(/|$)")
SECRET = re.compile(r"\bsk-(?:proj-|ant-|or-v1-)?[A-Za-z0-9_-]{20,}|\blsv2_[A-Za-z0-9_]{20,}|\btr_(?:dev|prod)_[A-Za-z0-9]{16,}|\bpnu_[A-Za-z0-9]{20,}|\bgh[pousr]_[A-Za-z0-9]{30,}")
PLANTS = {"skip_level": "P2", "missing_field": "P3", "stale_docs": "P4", "paid_model_l2": "P5",
          "paid_endpoint_l3": "P6", "deploy_no_approval": "P7", "secret_in_receipt": "P9"}


def empty(v) -> bool:
    return v is None or (isinstance(v, (str, list, dict)) and len(v) == 0)


def check(r: dict) -> tuple[list[str], str]:
    v: list[str] = []
    for k in ("framework", "skill", "route", "date", "levels"):
        if empty(r.get(k)):
            v.append(f"P1 receipt: missing {k}")
    levels = r.get("levels") if isinstance(r.get("levels"), dict) else {}
    blocked = {b.get("level"): b for b in r.get("blocked", []) if isinstance(b, dict)}
    claimed = [lv for lv in LEVELS if lv in levels]
    for lv in claimed:
        idx = LEVELS.index(lv)
        for lower in LEVELS[:idx]:
            if lower not in levels:
                v.append(f"P2 {lv}: claimed without {lower}")
                break
        body = levels[lv] if isinstance(levels[lv], dict) else {}
        for f in REQUIRED[lv]:
            if f not in body or (f != "exit" and empty(body.get(f))):
                v.append(f"P3 {lv}: missing {f}")
        if "exit" in REQUIRED[lv] and "exit" in body and body.get("exit") != 0:
            v.append(f"P3 {lv}: claimed with exit {body.get('exit')}")
    l0 = levels.get("L0") or {}
    for d in l0.get("docs", []) if isinstance(l0, dict) else []:
        if not str(d.get("url", "")).startswith("https://") or d.get("fetched") != r.get("date") or empty(d.get("sha256_12")):
            v.append(f"P4 L0: doc {d.get('url')} not fetched on {r.get('date')} with a sha")
    if "L2" in levels and not FAKE.search(str((levels["L2"] or {}).get("model", ""))):
        v.append(f"P5 L2: model {levels['L2'].get('model')!r} is not a deterministic fake")
    if "L3" in levels and not LOCAL.match(str((levels["L3"] or {}).get("endpoint", ""))):
        v.append(f"P6 L3: endpoint {levels['L3'].get('endpoint')!r} is not a local route")
    if "L5" in levels and empty((levels["L5"] or {}).get("approval_id")):
        v.append("P7 L5: deploy recorded without a Gate-D approval_id")
    for lv, b in blocked.items():
        if lv not in LEVELS or empty(b.get("reason")) or empty(b.get("check")):
            v.append(f"P8 blocked {lv}: needs level, reason, and check")
        if lv in levels:
            v.append(f"P8 {lv}: both claimed and blocked")
    if SECRET.search(json.dumps(r)):
        v.append("P9 receipt: contains a token-shaped secret value")
    top = "none"
    for lv in LEVELS:
        if lv in levels:
            top = lv
        else:
            break
    return v, top


def plant(r: dict, name: str) -> dict:
    r = copy.deepcopy(r)
    lv = r.setdefault("levels", {})
    if name == "skip_level":
        lv.pop("L1", None)
    elif name == "missing_field":
        (lv.get("L2") or lv.setdefault("L2", {})).pop("assertion", None)
    elif name == "stale_docs":
        for d in (lv.get("L0") or {}).get("docs", []):
            d["fetched"] = "2020-01-01"
    elif name == "paid_model_l2":
        lv.setdefault("L2", {})["model"] = "gpt-4o"
    elif name == "paid_endpoint_l3":
        lv.setdefault("L3", {})["endpoint"] = "https://api.openai.com/v1"
    elif name == "deploy_no_approval":
        lv["L5"] = {"approval_id": "", "target": "cloud", "command": "deploy", "exit": 0}
    elif name == "secret_in_receipt":
        r["note"] = "key " + "sk-proj-" + "PLANTEDFIXTURE" * 3
    return r


STEP_FIELDS = ("step", "command", "exit_code", "observed", "at")
LEVEL_TOKEN = re.compile(r"\bL([0-5])\b")


def check_steps(rows: list) -> tuple[list[str], list[str]]:
    v: list[str] = []
    levels = set()
    for i, r in enumerate(rows, 1):
        if not isinstance(r, dict):
            v.append(f"S1 row {i}: not an object")
            continue
        missing = [f for f in STEP_FIELDS if f not in r]
        if missing:
            v.append(f"S1 row {i}: missing {', '.join(missing)}")
        ec = r.get("exit_code")
        if ec is not None and not isinstance(ec, int):
            v.append(f"S1 row {i}: exit_code is neither an integer nor null")
        # null = the step never returned (hung, blocked, still running): honest, never a success
        if empty(r.get("command")) or empty(r.get("observed")):
            v.append(f"S1 row {i}: empty command or observed")
        if r.get("exit_code") == 0:
            levels.update("L" + m for m in LEVEL_TOKEN.findall(str(r.get("step", ""))))
    if SECRET.search(json.dumps(rows)):
        v.append("P9 receipt: contains a token-shaped secret value")
    return v, sorted(levels)


def main(argv: list[str]) -> int:
    if not argv or argv[0].startswith("-"):
        print("usage: proof_ladder.py RECEIPT.json [--plant NAME]", file=sys.stderr)
        return 1
    try:
        r = json.loads(Path(argv[0]).read_text())
    except (OSError, ValueError) as e:
        print(f"usage: receipt unreadable: {e}", file=sys.stderr)
        return 1
    if isinstance(r, list):
        if "--plant" in argv:
            rows = copy.deepcopy(r) + [{"step": "L2 planted", "command": "", "observed": "x", "at": "2026-09-28"}]
            hits = [x for x in check_steps(rows)[0] if x.startswith("S1 ")]
            print(f"PLANT step_row_broken: expected S1: {'CAUGHT' if hits else 'ESCAPED'}")
            return 2 if hits else 0
        viol, named = check_steps(r)
        for x in viol:
            print(x)
        print(f"proof_ladder STEP mode: {len(viol)} violation(s); {len(r)} steps; level tokens in exit-0 steps {named or 'none'} "
              "(step lists cannot prove contiguity or Gate-D; convert to a ladder receipt to claim a level)")
        return 2 if viol else 0
    if not isinstance(r, dict):
        print("P1 receipt: neither a ladder object nor a step list")
        return 2
    if "--plant" in argv:
        name = argv[argv.index("--plant") + 1] if argv.index("--plant") + 1 < len(argv) else ""
        if name not in PLANTS:
            print(f"usage: plant one of {sorted(PLANTS)}", file=sys.stderr)
            return 1
        planted = plant(r, name)
        if json.dumps(planted, sort_keys=True) == json.dumps(r, sort_keys=True):
            print(f"PLANT {name}: bytes did not move; refusing to report")
            return 0
        hits = [x for x in check(planted)[0] if x.startswith(PLANTS[name] + " ")]
        print(f"PLANT {name}: expected {PLANTS[name]}: {'CAUGHT' if hits else 'ESCAPED'}")
        return 2 if hits else 0
    viol, top = check(r)
    for x in viol:
        print(x)
    blocked = [f"{b.get('level')}:{b.get('reason')}" for b in r.get("blocked", []) if isinstance(b, dict)]
    print(f"proof_ladder {r.get('framework')}: {len(viol)} violation(s); highest proven level {top}; blocked {blocked or 'none'}")
    return 2 if viol else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
