#!/usr/bin/env python3
"""measure_baseline.py — measured manual-authoring baseline for the Workflow Design Studio.

UNIT (defined in SPEC.md): one hand-authored value a human must get right with no tool help:
a schema field, a JSON leaf key, an RRULE clause, a TOML config key, one done_when check,
or one operator command invocation.

Sources are LIVE artifacts on this machine (read-only):
  A. Aside routines   — ~/.aside/u/0/state.db (routines table, active rows)
  B. grokbot behavior — ~/rig-builds/grokbot-allmodels/lanes.yaml + ~/.grok/config.toml [model.X] blocks
  C. Jake loop        — ~/Developer/rig-capabilities/capabilities/loops/*.md (real loop cards)

Output: metrics/baseline.json (and a human summary on stdout).
"""
import json, os, re, sqlite3, sys, glob, statistics

HOME = os.path.expanduser("~")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "baseline.json")

def leaf_keys(d, prefix=""):
    n = 0
    if isinstance(d, dict):
        for k, v in d.items():
            n += leaf_keys(v, prefix + "." + str(k))
    elif isinstance(d, list):
        for v in d:
            n += leaf_keys(v, prefix + "[]")
    else:
        n = 1
    return n

result = {"unit_definition": "one hand-authored value: schema field | JSON leaf key | RRULE clause | TOML key | done_when check | operator command"}

# ---------- A. Aside routine ----------
db = sqlite3.connect(f"file:{HOME}/.aside/u/0/state.db?mode=ro", uri=True)
db.row_factory = sqlite3.Row
rows = db.execute("SELECT * FROM routines WHERE deleted_at IS NULL AND status='active'").fetchall()
SYSTEM = {"id", "created_at", "updated_at", "next_run_at", "revision", "deleted_at", "paused_at", "sync_definition"}
a_units, a_prompt_chars, a_meta, a_sc, a_rrule = [], [], [], [], []
for r in rows:
    d = dict(r)
    cols = sum(1 for k, v in d.items() if k not in SYSTEM and v not in (None, ""))
    meta = json.loads(d.get("metadata") or "{}")
    sc = json.loads(d.get("session_config") or "{}")
    rrule_units = len(re.split(r"[;\n]", d.get("rrule") or ""))  # DTSTART + RRULE + each clause
    units = cols + leaf_keys(meta) + leaf_keys(sc) + rrule_units
    a_units.append(units); a_prompt_chars.append(len(d.get("prompt") or ""))
    a_meta.append(leaf_keys(meta)); a_sc.append(leaf_keys(sc)); a_rrule.append(rrule_units)
result["A_aside_routine"] = {
    "population": len(rows),
    "units_per_routine_avg": round(statistics.mean(a_units), 1),
    "units_per_routine_median": int(statistics.median(a_units)),
    "breakdown_avg": {
        "hand_authored_columns": round(statistics.mean([u - m - s - rr for u, m, s, rr in zip(a_units, a_meta, a_sc, a_rrule)]), 1),
        "metadata_json_leaf_keys": round(statistics.mean(a_meta), 1),
        "session_config_json_leaf_keys": round(statistics.mean(a_sc), 1),
        "rrule_dtstart_clauses": round(statistics.mean(a_rrule), 1),
    },
    "prompt_body_chars_avg": round(statistics.mean(a_prompt_chars)),
    "prompt_counts_as": "1 authored artifact (reported separately in chars)",
}

# ---------- B. grokbot behavior ----------
try:
    import yaml
    lanes_doc = yaml.safe_load(open(f"{HOME}/rig-builds/grokbot-allmodels/lanes.yaml"))
    lanes = lanes_doc.get("lanes", [])
    lane_keys = [len(l) for l in lanes]
    pools = lanes_doc.get("pools", {})
    pool_member_keys = sum(len(v) for v in pools.values())
except Exception as e:
    lanes, lane_keys, pool_member_keys = [], [], 0
    result["B_error"] = str(e)
toml = open(f"{HOME}/.grok/config.toml").read()
model_blocks = re.findall(r"\[model\.[^\]]+\](.*?)(?=\n\[|\Z)", toml, re.S)
block_keys = [len(re.findall(r"^\s*[A-Za-z_]+\s*=", b, re.M)) for b in model_blocks]
gen_doc = open(f"{HOME}/rig-builds/grokbot-allmodels/gen.py").read(4000)
# operator commands a human runs today to ship one behavior (from gen.py docstring: inputs -> outputs -> install)
gen_commands = 3  # gen.py candidate run | diff/review out/report.json + coverage.md | promote candidate -> live router
result["B_grokbot_behavior"] = {
    "lanes_in_live_additions": len(lanes),
    "lane_entry_keys_avg": round(statistics.mean(lane_keys), 1) if lane_keys else 0,
    "pool_membership_keys_total": pool_member_keys,
    "config_toml_model_blocks": len(model_blocks),
    "config_toml_block_keys_avg": round(statistics.mean(block_keys), 1) if block_keys else 0,
    "operator_commands_per_ship": gen_commands,
    "note": "litellm.yaml is GENERATED (header: do not hand-edit); a behavior change edits lanes.yaml + config.toml then re-runs gen.py",
}

# ---------- C. Jake loop card ----------
cards = [p for p in glob.glob(f"{HOME}/Developer/rig-capabilities/capabilities/loops/*.md") if ".bak" not in p and os.path.isfile(p)]
c_front, c_done, c_lines = [], [], []
for p in cards:
    txt = open(p).read()
    if not txt.startswith("---"): continue
    fm = txt.split("---", 2)[1]
    top_keys = [l.split(":")[0].strip() for l in fm.splitlines() if l and not l.startswith((" ", "\t", "-")) and ":" in l]
    done = len(re.findall(r"^\s*-\s+(file|cmd|grep|exists):", fm, re.M))
    c_front.append(len(top_keys)); c_done.append(done); c_lines.append(txt.count("\n"))
result["C_jake_loop_card"] = {
    "cards_measured": len(c_front),
    "frontmatter_keys_avg": round(statistics.mean(c_front), 1),
    "done_when_checks_avg": round(statistics.mean(c_done), 1),
    "card_lines_avg": round(statistics.mean(c_lines)),
    "plus": "harness YAML + compiled goalspec pair (out/harness-goalspecs *.json+*.yaml) when the loop uses a harness",
}

json.dump(result, open(OUT, "w"), indent=2)
print(json.dumps(result, indent=2))
