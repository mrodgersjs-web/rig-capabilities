#!/usr/bin/env python3
"""Build the jev-audit queue from BUILD-MANIFEST.yaml rows that claim to be built.
Repro preference: named unittest > receipt JSON > commit (either repo) > UNVERIFIABLE."""
import json, re, yaml

CAP = "/Users/rig128gb/Developer/rig-capabilities"
UP = "/Users/rig128gb/Developer/ultraplan"
CAP_TESTS = ("test_ultra_gates", "test_s1gate", "test_ultra_cell", "test_ultra_plan_forecast",
             "test_mcp_s1gate", "test_ultra_cli", "test_ultra_polarity", "test_loops",
             "test_build_proofs")

d = yaml.safe_load(open("BUILD-MANIFEST.yaml"))
queue, unver = [], 0
for it in d["items"]:
    st, iid, title = it["status"], it["id"], it["title"]
    if st == "inventoried":
        continue
    ev = (it.get("evidence") or "") + " " + (it.get("note") or "")
    repro = None
    if iid.startswith("UP.W06.TAC"):
        # an unrelated ultraplan commit hash does NOT evidence a TAC corpus item
        if "SHA256SUMS" in ev:
            repro = "cd /Users/rig128gb/Desktop/TAC-Technology-Operating-System && shasum -a 256 -c 07-evidence/SHA256SUMS.txt | tail -2"
        else:
            repro = "python3 -c 'print(\"UNVERIFIABLE: TAC artifact not yet produced\")' && exit 3"
        queue.append({"id": iid, "claim": "The evidence command recorded for manifest item %s reproduces green on disk today" % iid, "repro_cmd": repro, "title": title})
        continue
    mrep = re.search(r"repro=(.+)$", ev)
    if mrep:
        queue.append({"id": iid, "claim": "The evidence command recorded for manifest item %s reproduces green on disk today" % iid, "repro_cmd": mrep.group(1).strip(), "title": title})
        continue
    m = re.search(r"(tests\.)?(test_[a-z_]+(?:\.[A-Za-z_]+)?(?:\.[a-z_0-9]+)?)(?!\.py)", ev)
    mr = re.search(r"receipt-([a-z0-9-]+)\.json", ev)
    ms = re.search(r"\b[0-9a-f]{7,10}\b", ev)
    if m:
        name = m.group(0).removesuffix(".py")
        if not name.startswith("tests."):
            name = "tests." + name.split(".", 1)[0] if "." not in name else name
        mod = name.split(".")[1] if name.startswith("tests.") else name.split(".")[0]
        repo = CAP if mod in CAP_TESTS else UP
        repro = "cd %s && python3 -m unittest %s" % (repo, name)
    elif mr:
        rec = "%s/data/receipt-%s.json" % (UP, mr.group(1))
        repro = ("python3 -c \"import json; d=json.load(open('%s')); "
                 "assert d['results'][0]['ok']; print(d['cell'],'ok=True')\"" % rec)
    elif ms:
        sha = ms.group(0)
        repro = "git -C %s show --stat -s %s || git -C %s show --stat -s %s" % (CAP, sha, UP, sha)
    if repro is None:
        unver += 1
        repro = "python3 -c 'print(\"UNVERIFIABLE: no test, receipt, or commit named\")' && exit 3"
    queue.append({"id": iid, "claim": "The evidence command recorded for manifest item %s reproduces green on disk today" % iid, "repro_cmd": repro, "title": title})
json.dump(queue, open("audit-queue.json", "w"), indent=1)
print(len(queue), "rows;", unver, "unverifiable-by-design (audit REDs them honestly)")
