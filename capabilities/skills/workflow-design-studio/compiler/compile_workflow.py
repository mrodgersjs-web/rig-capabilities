#!/usr/bin/env python3
"""compile_workflow.py — Workflow Design Studio compiler (A1 PYTHON_ONLY).

Reads one registry entry (plain-language workflow card, YAML) and emits DRAFT artifacts
for three runtime surfaces:

  aside/   — Aside routine record (routines-table shape: rrule + metadata + session_config)
  grokbot/ — router lanes fragment (grokbot-allmodels lanes.yaml shape) + [model.X] TOML block
  jake/    — loop card (rig loop-card frontmatter shape) + prime-agent heartbeat spec

Rules:
  - Deterministic: same registry bytes -> byte-identical outputs (no wall-clock, sorted keys).
  - No model in the decision path: frozen vocabularies + allowlists only. An unknown value
    is a hard error (exit 2), never a guess.
  - DRAFT ONLY: this tool never writes outside its own out/ directory. Embedding into
    state.db / litellm.yaml / config.toml / jake loops is a human step (EMBED.md runbook).

Usage:
  python3 compile_workflow.py registry/<id>.yaml           # compile to out/<id>/
  python3 compile_workflow.py registry/<id>.yaml --check   # validate + print plan, write nothing
"""
import argparse, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
try:
    import yaml
except ImportError:
    sys.exit("compile_workflow: PyYAML required (project env has it)")

HOME = os.path.expanduser("~")
CATALOG = f"{HOME}/rig-builds/grokbot-allmodels/catalog/aside-models.json"
ROUTER = f"{HOME}/.rig/grokbot-router/litellm.yaml"

FREQ = {"DAILY", "WEEKLY"}
DAYS = {"MO", "TU", "WE", "TH", "FR", "SA", "SU"}
THINKING = {"minimal", "low", "medium", "high", "xhigh"}
PERMISSIONS = {"read-only", "full-access"}
TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")

REQUIRED = ["id", "name", "owner", "intent", "schedule", "model", "permissions",
            "steps", "gates", "outputs", "outward", "gate_d_required"]
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,48}$")


class CompileError(Exception):
    pass


def fail(msg):
    raise CompileError(msg)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load_registry(path):
    with open(path) as f:
        reg = yaml.safe_load(f)
    if not isinstance(reg, dict):
        fail("registry entry must be a mapping")
    missing = [k for k in REQUIRED if k not in reg]
    if missing:
        fail(f"missing registry fields: {missing}")
    if not ID_RE.match(str(reg["id"])):
        fail(f"id {reg['id']!r} must match {ID_RE.pattern}")
    sch = reg["schedule"]
    for k in ("freq", "time", "timezone", "start_date"):
        if k not in sch:
            fail(f"schedule.{k} is required")
    if sch["freq"] not in FREQ:
        fail(f"schedule.freq {sch['freq']!r} not in frozen vocabulary {sorted(FREQ)}")
    if sch["freq"] == "WEEKLY":
        days = sch.get("days") or []
        if not days or any(d not in DAYS for d in days):
            fail(f"schedule.days {days!r} must be a non-empty subset of {sorted(DAYS)}")
    if not TIME_RE.match(str(sch["time"])):
        fail(f"schedule.time {sch['time']!r} must be HH:MM")
    if not re.match(r"^[A-Za-z]+/[A-Za-z_+-]+$", str(sch["timezone"])):
        fail(f"schedule.timezone {sch['timezone']!r} must be Area/Location")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(sch["start_date"])):
        fail("schedule.start_date must be YYYY-MM-DD")
    m = reg["model"]
    for k in ("aside_provider", "aside_model", "grokbot_lane", "grokbot_route_model"):
        if k not in m:
            fail(f"model.{k} is required")
    if m.get("thinking", "medium") not in THINKING:
        fail(f"model.thinking {m.get('thinking')!r} not in {sorted(THINKING)}")
    if reg["permissions"] not in PERMISSIONS:
        fail(f"permissions {reg['permissions']!r} not in {sorted(PERMISSIONS)}")
    for k in ("steps", "gates", "outputs"):
        if not isinstance(reg[k], list) or not reg[k]:
            fail(f"{k} must be a non-empty list of plain-language lines")
    if not isinstance(reg["outward"], bool) or not isinstance(reg["gate_d_required"], bool):
        fail("outward and gate_d_required must be booleans")
    if reg["outward"] and not reg["gate_d_required"]:
        fail("outward=true requires gate_d_required=true (Gate-D)")
    return reg


def check_routes(reg):
    """Allowlist resolution against live, read-only sources. Unknown = hard error."""
    m = reg["model"]
    aside_id = f"{m['aside_provider']}/{m['aside_model']}"
    if os.path.exists(CATALOG):
        cat = json.load(open(CATALOG))
        providers = cat.get("providers", {}) if isinstance(cat, dict) else {}
        models = providers.get(m["aside_provider"])
        if models is None:
            fail(f"UNRESOLVED_ROUTE: provider {m['aside_provider']!r} not in grokbot catalog/aside-models.json")
        if m["aside_model"] not in models:
            fail(f"UNRESOLVED_ROUTE: {aside_id} not in grokbot catalog (provider models: {models[:6]}...)")
    lane = m["grokbot_lane"]
    if not re.match(r"^[a-z0-9][a-z0-9-]{2,48}$", lane):
        fail(f"model.grokbot_lane {lane!r} must be a lowercase lane name")
    route = m["grokbot_route_model"]
    if os.path.exists(ROUTER):
        rtxt = open(ROUTER).read()
        if f"model_name: {route}" not in rtxt:
            fail(f"UNRESOLVED_ROUTE: model_name '{route}' not in live litellm.yaml model_list")
    return aside_id, lane, route


def build_rrule(sch):
    hh, mm = str(sch["time"]).split(":")
    dt = str(sch["start_date"]).replace("-", "") + "T" + hh + mm + "00"
    dtstart = f"DTSTART;TZID={sch['timezone']}:{dt}"
    if sch["freq"] == "DAILY":
        rule = f"RRULE:FREQ=DAILY;BYHOUR={int(hh)};BYMINUTE={int(mm)}"
    else:
        rule = f"RRULE:FREQ=WEEKLY;BYDAY={','.join(sch['days'])};BYHOUR={int(hh)};BYMINUTE={int(mm)}"
    return dtstart + "\n" + rule


def cron(sch):
    hh, mm = str(sch["time"]).split(":")
    if sch["freq"] == "DAILY":
        return f"{int(mm)} {int(hh)} * * *"
    daymap = {"MO": 1, "TU": 2, "WE": 3, "TH": 4, "FR": 5, "SA": 6, "SU": 7}
    days = ",".join(str(daymap[d]) for d in sch["days"])
    return f"{int(mm)} {int(hh)} * * {days}"


def prompt_body(reg):
    lines = [f"# {reg['name']}", "", f"Intent: {reg['intent']}", "", "Steps:"]
    lines += [f"{i+1}. {s}" for i, s in enumerate(reg["steps"])]
    lines += ["", "Stop and report when:"] + [f"- {g}" for g in reg["gates"]]
    lines += ["", "Produce:"] + [f"- {o}" for o in reg["outputs"]]
    if not reg["outward"]:
        lines += ["", "Boundary: read-only run. Nothing outward. Any outward action waits for a human Gate-D approval."]
    return "\n".join(lines) + "\n"


def render_aside(reg, rrule, body, aside_id):
    m = reg["model"]
    rid = "wds" + sha(reg["id"].encode())[:13]
    record = {
        "id": rid,
        "id_note": "DRAFT placeholder id; the embed step mints the real routine id",
        "type": "child",
        "environment": "device",
        "name": reg["name"],
        "prompt": body,
        "rrule": rrule,
        "parent_session_id": None,
        "project_id": None,
        "channel_id": None,
        "status": "draft",
        "next_run_at": None,
        "metadata": {
            "origin": {"type": "workflow-design-studio-compile", "registry_id": reg["id"]},
            "memoryPath": f"/Users/rig128gb/.aside/u/0/memory/routines/{rid}/MEMORY.md",
        },
        "session_config": {
            "model": {
                "provider": m["aside_provider"],
                "modelId": aside_id.split("/", 1)[1],
                "thinkingLevel": m.get("thinking", "medium"),
                "fastMode": False,
            },
            "harnessId": "v1",
            "permissionMode": reg["permissions"],
            "strictModelSelection": True,
        },
        "gate_d_required": reg["gate_d_required"],
    }
    return json.dumps(record, indent=2, sort_keys=False) + "\n"


def render_grokbot(reg, lane, route):
    m = reg["model"]
    frag = {
        "lanes": [{
            "name": lane,
            "model": m.get("grokbot_model", route),
            "via": m.get("grokbot_via", "cliproxy"),
            "tier": m.get("grokbot_tier", "local"),
            "aside": m.get("grokbot_aside", f"{reg['model']['aside_provider']}/{reg['model']['aside_model']}"),
        }],
        "pools": {m.get("grokbot_pool", "rig-local-first"): [lane]},
    }
    lanes_yaml = (
        "# DRAFT fragment from workflow-design-studio (append-only; lanes.yaml is gen.py input)\n"
        "# Merge under `lanes:` / `pools:`, then run gen.py to build a candidate litellm.yaml.\n"
        + yaml.safe_dump(frag, sort_keys=False)
    )
    toml = (
        "# DRAFT [model.X] block for ~/.grok/config.toml (human places it; nothing auto-applied)\n"
        f'[model.{lane}]\n'
        f'model = "{route}"\n'
        f'base_url = "{m.get("grokbot_base_url", "http://127.0.0.1:18768/v1")}"\n'
        f'name = "{reg["name"]} · {route}"\n'
        f'description = "workflow-design-studio draft for {reg["id"]} — bound to existing router alias {route}"\n'
        f'api_key = "local-only"\n'
        f'api_backend = "chat_completions"\n'
        f'max_completion_tokens = {int(m.get("max_completion_tokens", 32768))}\n'
        f'context_window = {int(m.get("context_window", 200000))}\n'
    )
    return lanes_yaml, toml


def render_loop_card(reg, body, cron_str, out_rel):
    checks = [f"  - file:{out_rel}/aside/routine.json",
              f"  - file:{out_rel}/grokbot/lanes.fragment.yaml",
              f"  - file:{out_rel}/jake/loop-card.md",
              f"  - cmd:python3 compiler/compile_workflow.py registry/{reg['id']}.yaml --check"]
    checks += [f"  - grep:{out_rel}/aside/routine.json:{g.split()[0]}" for g in reg["gates"][:2]]
    fm = ["---",
          f'outcome: "{reg["intent"].replace(chr(34), chr(39))}"',
          "done_when:"] + checks + [
          "state: DORMANT",
          f"gate_d_required: {str(reg['gate_d_required']).lower()}",
          f'cadence: "{cron_str}"',
          "quality_floor: 0.7",
          "---", ""]
    card = "\n".join(fm)
    card += f"\n# {reg['name']} — loop card (DRAFT, workflow-design-studio)\n\n"
    card += f"**Cadence:** `{cron_str}` ({reg['schedule']['timezone']}) — compiled from `registry/{reg['id']}.yaml`.\n"
    card += "**Mode:** DRAFT. Staging this card into `capabilities/loops/` or registering the recurring job is a Gate-D action.\n\n"
    card += "## Body (shared with the routine prompt — single source, compiled)\n\n" + body + "\n"
    card += "\n## Termination\n\nA run that cannot produce every `outputs` item names the missing item and FAILs. " \
            "No prose-only completions. Nothing outward without a human Gate-D approval id.\n"
    return card


def render_heartbeat(reg, cron_str):
    return json.dumps({
        "tool": "rlm_heartbeat.create",
        "status": "draft",
        "args": {
            "label": reg["id"],
            "interval": cron_str,
            "instruction": f"Run the {reg['name']} workflow: {reg['intent']} Produce: "
                           + "; ".join(reg["outputs"]) + ". Nothing outward without Gate-D.",
            "delivery_mode": "follow_up",
        },
    }, indent=2) + "\n"


def render_temporal(reg, cron_str):
    'Surface 4: Temporal always-on schedule (lane_schedules.py shape), DRAFT, paused.'
    sch = reg["schedule"]
    sid = "wds-" + reg["id"] + "-v1"
    spec_py = f'''# DRAFT Temporal schedule registration for {reg["id"]} (workflow-design-studio)
# Shape mirrors ~/.rig/runtimes/temporal-runners/lane_schedules.py. NOTHING REGISTERED.
# from temporalio.client import Schedule, ScheduleActionStartWorkflow, ScheduleSpec, ScheduleState
# sid = "{sid}"
# Schedule(
#     action=ScheduleActionStartWorkflow(<workflow>, id="{sid}", task_queue="<queue>",
#                                        execution_timeout=timedelta(minutes=<budget>)),
#     spec=ScheduleSpec(cron_expressions=["{cron_str}"], time_zone_name="{sch['timezone']}"),
#     state=ScheduleState(paused=True, note="DRAFT workflow-design-studio; unpause is a Gate-D action"),
# )
'''
    sched_json = json.dumps({
        "schedule_id": sid, "status": "draft", "paused": True,
        "cron_expressions": [cron_str], "time_zone_name": sch["timezone"],
        "task_queue": "<queue: pick at embed>", "execution_timeout_minutes": int(reg.get("budget_minutes", 90)),
        "note": "DRAFT; registering or unpausing is a Gate-D action",
    }, indent=2) + "\n"
    return spec_py, sched_json


def render_goalspec(reg):
    'Surface 5: goal-harness spec (out/harness-goalspecs shape), DRAFT.'
    gates = []
    for i, g in enumerate(reg["gates"], 1):
        gates.append({
            "id": f"E{i}", "category": "Done Gate", "name": g[:80],
            "description": g, "command": f"see out/{reg['id']}/EMBED.md gate E{i}",
            "failure_tier": "halt", "required": True, "required_verdict": "GO", "weight": 1.0,
        })
    gates.append({
        "id": f"E{len(reg['gates'])+1}", "category": "Compile Integrity",
        "name": "compiler --check passes and MANIFEST hashes match",
        "description": "python3 compiler/compile_workflow.py registry/" + reg["id"] + ".yaml --check exits 0; MANIFEST.json artifact hashes re-verify",
        "command": "compile_workflow.py --check; sha256sum -c MANIFEST.json",
        "failure_tier": "halt", "required": True, "required_verdict": "GO", "weight": 1.0,
    })
    spec = {"goals": [{
        "id": f"GL-{reg['id'].upper()}",
        "name": reg["name"],
        "description": f"{reg['intent']} [ {reg['id']} ] — compiled from registry/{reg['id']}.yaml by workflow-design-studio",
        "anchor": "L4-D3-A1-I", "bms_mode": "A1", "gate": "",
        "gates": gates,
    }]}
    return json.dumps(spec, indent=2) + "\n"


def render_jake_brain(reg, body, cron_str):
    'Surface 6: jake-brain loop card + COORD note. We never write app/jake_brain/**.'
    intent_q = reg["intent"].replace(chr(34), chr(39))
    card = f'''---
outcome: "{intent_q}"
done_when:
  - file:registry/{reg['id']}.yaml
  - cmd:python3 compiler/compile_workflow.py registry/{reg['id']}.yaml --check
state: DORMANT
gate_d_required: {str(reg['gate_d_required']).lower()}
cadence: "{cron_str}"
quality_floor: 0.7
---

# {reg['name']} — jake-brain loop card (DRAFT)

**Cadence:** `{cron_str}` ({reg['schedule']['timezone']}). Compiled, not hand-written.
**Placement:** by the worker who owns `app/jake_brain/**` (see COORD.md). This studio writes
nothing into app/jake_brain/** or app/jake_brain_nightly/**.

## Body (shared compiled source)

{body}
'''
    coord = f'''# COORD.md — handoff to the app/jake_brain owner

From: Jordan Jr (workflow-design-studio), 2026-10-26.
We compiled a DRAFT jake-brain loop card for `{reg['id']}` at `out/{reg['id']}/jake-brain/loop-card.md`.
Per mandate we wrote nothing into `app/jake_brain/**` or `app/jake_brain_nightly/**` — those belong to you.

Ask: place the card in your loop-card store under your own review, or reply with the schema delta
needed for it to fit. Schedule: `{cron_str}` ({reg['schedule']['timezone']}); keep it `state: DORMANT`
until a human arms it (Gate-D on the recurring job).
'''
    return card, coord


def render_chat_brief(reg):
    'Surface 7: Aside chat brief (aside_chat_new / driver brief), DRAFT.'
    brief_md = f'''# Aside chat brief — {reg['name']} (DRAFT, never opened by this studio)

Title: {reg['name']}
Mode: read-only brief; no outward sends. Opening this chat is a human step.

Brief (paste to aside_chat_new):

{reg['intent']}
Run every {reg['schedule']['freq'].lower()} at {reg['schedule']['time']} {reg['schedule']['timezone']}.
Steps: {' | '.join(reg['steps'])}
Report: {' | '.join(reg['outputs'])}
Nothing outward without Mike's typed Gate-D approval.
'''
    brief_json = json.dumps({
        "tool": "aside_chat_new", "status": "draft",
        "title": reg["name"], "brief_file": f"out/{reg['id']}/aside-chat/brief.md",
        "quiet_hours": "binds", "routine_unpause": "never via chat",
    }, indent=2) + "\n"
    return brief_md, brief_json


def registry_row(reg, cron_str, lane, aside_id):
    return (
        "# design row (SSOT: registry/registry.yaml)\n"
        f"id: {reg['id']}\n"
        f"name: {reg['name']}\n"
        "surface: [aside-routine, grokbot-behavior, jake-loop, temporal-schedule, goalspec, jake-brain-loop, aside-chat-brief]\n"
        f"schedule: \"{cron_str} {reg['schedule']['timezone']}\"\n"
        f"owner: {reg['owner']}\n"
        f"done-test: python3 compiler/compile_workflow.py registry/{reg['id']}.yaml --check (and recompile MANIFEST diff must be empty)\n"
        "last-drift-check: never — run compiler/drift_doctor.py\n"
        "embed_state: draft (7 surfaces compiled, nothing installed)\n"
        f"routes: {{aside: {aside_id}, grokbot_lane: {lane}}}\n"
    )


def render_embed(reg, out_rel, lane, route, aside_id):
    return f'''# EMBED runbook — {reg['id']} (human step; every action below is OUTWARD-adjacent and stays un-applied)

Drafts for all SEVEN surfaces are compiled under `{out_rel}/`. Nothing below has been done.

## 1. Aside routine
- Review `{out_rel}/aside/routine.json` (prompt, rrule, session_config).
- Insert via the Aside routine surface with a minted id, `status='active'`, real `memoryPath` created.
- Quiet-hours / routine rules still bind; a paused routine is never auto-unpaused.

## 2. grokbot behavior
- Merge `{out_rel}/grokbot/lanes.fragment.yaml` into ~/rig-builds/grokbot-allmodels/lanes.yaml (append-only).
- Run gen.py -> candidate litellm.yaml; review out/report.json + coverage.md; promote on approval.
- Place `{out_rel}/grokbot/config-model-block.toml` into ~/.grok/config.toml ([model.{lane}] -> router alias {route}).

## 3. Jake harness/brain loop
- Review `{out_rel}/jake/loop-card.md`; or arm the heartbeat with `{out_rel}/jake/heartbeat.json`.
- Stays `state: DORMANT` until a human flips it (Gate-D on the recurring job).

## 4. Temporal always-on schedule
- Review `{out_rel}/temporal/schedule-spec.py` + `schedule.json`; register with paused=True via the runner's own env.
- Unpausing is a Gate-D action.

## 5. goal-harness spec
- Review `{out_rel}/goalspec/harness-goalspec.draft.json`; promote into out/harness-goalspecs via the owner's compile flow.

## 6. jake-brain loop card
- Hand `{out_rel}/jake-brain/loop-card.md` + `COORD.md` to the app/jake_brain owner. This studio writes nothing there.

## 7. Aside chat brief
- Open the chat yourself with `{out_rel}/aside-chat/brief.md` via aside_chat_new when you want it live.

Route bindings resolved at compile time: aside={aside_id}, lane={lane}, router_model={route}.
'''


def compile_entry(path, check_only=False):
    reg = load_registry(path)
    aside_id, lane, route = check_routes(reg)
    rrule = build_rrule(reg["schedule"])
    body = prompt_body(reg)
    cron_str = cron(reg["schedule"])
    out_rel = f"out/{reg['id']}"
    temporal_py, temporal_json = render_temporal(reg, cron_str)
    brain_card, coord = render_jake_brain(reg, body, cron_str)
    chat_md, chat_json = render_chat_brief(reg)
    files = {
        "aside/routine.json": render_aside(reg, rrule, body, aside_id),
        "grokbot/lanes.fragment.yaml": render_grokbot(reg, lane, route)[0],
        "grokbot/config-model-block.toml": render_grokbot(reg, lane, route)[1],
        "jake/loop-card.md": render_loop_card(reg, body, cron_str, out_rel),
        "jake/heartbeat.json": render_heartbeat(reg, cron_str),
        "temporal/schedule-spec.py": temporal_py,
        "temporal/schedule.json": temporal_json,
        "goalspec/harness-goalspec.draft.json": render_goalspec(reg),
        "jake-brain/loop-card.md": brain_card,
        "jake-brain/COORD.md": coord,
        "aside-chat/brief.md": chat_md,
        "aside-chat/brief.json": chat_json,
        "registry/row.yaml": registry_row(reg, cron_str, lane, aside_id),
        "EMBED.md": render_embed(reg, out_rel, lane, route, aside_id),
    }
    manifest = {
        "compiler": "workflow-design-studio compile_workflow.py",
        "mode": "A1 PYTHON_ONLY (L4-D3-A1-I1, BMS 0.89)",
        "registry_id": reg["id"],
        "registry_sha256": sha(open(path, "rb").read()),
        "routes": {"aside": aside_id, "grokbot_lane": lane, "router_model": route},
        "artifacts": {k: sha(v.encode()) for k, v in sorted(files.items())},
    }
    files["MANIFEST.json"] = json.dumps(manifest, indent=2) + "\n"
    if check_only:
        print(f"CHECK OK {reg['id']}: {len(files)} artifacts would be written to {out_rel}/")
        return
    if DRY_RUN:
        print(f"DRY RUN {reg['id']} — nothing written. Embed plan (all DRAFT until a human applies):")
        for k in sorted(files):
            print(f"  {out_rel}/{k}")
        print("  embed targets (human, Gate-D where outward): state.db routines | lanes.yaml+gen.py | "
              "config.toml | capabilities/loops/ or rlm_heartbeat | temporal schedule | "
              "out/harness-goalspecs | app/jake_brain via owner | aside_chat_new")
        return
    dest = os.path.join(ROOT, out_rel)
    for sub in ("aside", "grokbot", "jake", "temporal", "goalspec", "jake-brain", "aside-chat", "registry"):
        os.makedirs(os.path.join(dest, sub), exist_ok=True)
    for rel, content in files.items():
        with open(os.path.join(dest, rel), "w") as f:
            f.write(content)
    print(f"COMPILED {reg['id']} -> {out_rel}/ ({len(files)} files)")
    for k, v in sorted(manifest["artifacts"].items()):
        print(f"  {v[:12]}  {k}")


DRY_RUN = False


def main(argv):
    global DRY_RUN
    ap = argparse.ArgumentParser()
    ap.add_argument("registry")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="preview the embed plan; write nothing")
    a = ap.parse_args(argv)
    DRY_RUN = a.dry_run
    try:
        compile_entry(a.registry, check_only=a.check)
    except CompileError as e:
        print(f"COMPILE REFUSED: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
