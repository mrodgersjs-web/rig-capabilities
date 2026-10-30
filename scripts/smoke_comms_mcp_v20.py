import json, subprocess, sys
SKILL = "/Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-communications-core"
reqs = [
 {"jsonrpc":"2.0","id":1,"method":"initialize"},
 {"jsonrpc":"2.0","id":2,"method":"tools/list"},
 {"jsonrpc":"2.0","id":3,"method":"resources/list"},
 {"jsonrpc":"2.0","id":4,"method":"resources/read","params":{"uri":"comms://fingerprint"}},
 {"jsonrpc":"2.0","id":5,"method":"resources/read","params":{"uri":"comms://nope"}},
 {"jsonrpc":"2.0","id":6,"method":"prompts/list"},
 {"jsonrpc":"2.0","id":7,"method":"prompts/get","params":{"name":"verify"}},
 {"jsonrpc":"2.0","id":8,"method":"prompts/get","params":{"name":"sim-hostile"}},
 {"jsonrpc":"2.0","id":9,"method":"tools/call","params":{"name":"comms.intent_check","arguments":{"intent":{"objective":"ask","desired_recipient_state":{"do":["reply yes"]},"context":{"stakes":"high"}}}}},
 {"jsonrpc":"2.0","id":10,"method":"tools/call","params":{"name":"comms.energy","arguments":{"scores":{"fidelity":0.5},"stakes":"high"}}},
 {"jsonrpc":"2.0","id":11,"method":"tools/call","params":{"name":"comms.gates","arguments":{"surface":"love-notes","artifact":"x"}}},
 {"jsonrpc":"2.0","id":12,"method":"tools/call","params":{"name":"comms.golden"}},
 {"jsonrpc":"2.0","id":13,"method":"tools/call","params":{"name":"comms.verdict","arguments":{"role":"architect","decision":"pass","scores":{"fidelity":0.97,"audience":0.9,"clarity":0.9,"warmth":0.8,"competence":0.85,"evidence":0.95,"voice":0.9,"risk":0.95,"moving_parts":0.9,"first_sentence_value":True,"provenance_backed":True,"screenshot_safety":True,"voice_drift":0.1},"stakes":"low"}}},
 {"jsonrpc":"2.0","id":14,"method":"tools/call","params":{"name":"comms.outcome","arguments":{"action":"brier","archetype":"none-yet"}}},
]
inp = "".join(json.dumps(r) + "\n" for r in reqs)
p = subprocess.run([sys.executable, "-m", "rig_comms.mcp"], input=inp, capture_output=True,
                   text=True, timeout=60, cwd=SKILL)
resp = {}
for l in p.stdout.splitlines():
    d = json.loads(l)
    if d.get("id") is not None:
        resp[d["id"]] = d
def res(i):
    r = resp[i]
    return r.get("error") or r.get("result")
tl = res(2)["tools"]; print("tools:", len(tl))
print("resources:", [r["uri"] for r in res(3)["resources"]])
print("fp version:", json.loads(res(4)["contents"][0]["text"])["version"])
print("bad resource code:", res(5)["code"])
print("prompts:", len(res(6)["prompts"]))
print("verify prompt GEV:", "sole termination" in res(7)["messages"][0]["content"]["text"])
print("sim-hostile:", "hostile" in res(8)["messages"][0]["content"]["text"])
ic = json.loads(res(9)["content"][0]["text"]); print("intent_check valid:", ic["valid"], "vehicle:", ic["vehicle_preview"]["vehicle"])
en = json.loads(res(10)["content"][0]["text"]); print("energy red on fidelity 0.5:", not en["floors_ok"])
g = res(11); txt = g.get("message") or g.get("content",[{}])[0].get("text","")
print("love-notes PRIVACY_LOCK:", "PRIVACY_LOCK" in txt, "| code:", g.get("code"))
gd = json.loads(res(12)["content"][0]["text"]); print("golden via MCP:", gd["green"], gd["total"])
v = json.loads(res(13)["content"][0]["text"]); print("architect pass refused:", v["verdict"]["admitted"] is False, "|", v["verdict"]["reason"][:20])
ob = json.loads(res(14)["content"][0]["text"]); print("brier honest empty:", ob["brier"] is None)
init = res(1); print("caps:", sorted(init["capabilities"].keys()), "| version:", init["serverInfo"]["version"], "| instr has PRIVACY_LOCK:", "PRIVACY_LOCK" in init.get("instructions",""))
print("stderr:", (p.stderr.strip()[:300] or "clean"), "| exit:", p.returncode)
