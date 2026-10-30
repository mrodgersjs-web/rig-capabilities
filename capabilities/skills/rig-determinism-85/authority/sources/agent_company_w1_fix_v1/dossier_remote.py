"""W1a dossier-builder: ONE remote script (runs on the laptop via sshio.run_py,
same shape as measure_remote.REMOTE) implementing dossier_select / dossier_build /
dossier_verify over PAYLOAD. Research tools are read-only; NO touches, NO sends —
dossier file writing + Twenty note attachment only.

Known Twenty v2.50.1 shapes (probed against the live server 2026-10-22):
  GraphQL endpoint is /graphql (measure_remote's /api/graphql 404s on this build)
  plural query field is `people` (not `persons`); stage filter uses {in: [...]}
  createNote(data:{title, bodyV2:{markdown}}) then createNoteTarget(data:{noteId,
  targetPersonId}) — nested noteTargets writes are rejected on createNote.
"""
from __future__ import annotations

REMOTE = r'''
import json, os, re, subprocess, sys
p = json.loads(os.environ["PAYLOAD"]); cmd = p["cmd"]
CP = "/Users/rig128gb/.rig/live/control-plane"; AC = CP + "/agent-company"; GTM = CP + "/gtm"
DOSS = GTM + "/dossiers"
REPO = "/Users/rig128gb/rig-builds/agent-company-w1-fix"
BIN = "/Users/rig128gb/.rig/bin"
sys.path.insert(0, AC)
try:  # ssh sessions get keychain rc=36; _api_key() is env-first, so seed from the secrets file
    for _ln in open(os.path.expanduser("~/.rig/secrets/twenty-crm.env")):
        if _ln.startswith("TWENTY_API_KEY="):
            os.environ["TWENTY_API_KEY"] = _ln.split("=", 1)[1].strip().strip('"').strip("'")
            break
except Exception:
    pass
from twenty_client import TwentyClient
T = TwentyClient()  # _req throttles ~1 req/s and handles Bearer auth
NOTE_PREFIX = "GTM dossier "

def gql(query, variables=None):
    body = {"query": query}
    if variables: body["variables"] = variables
    d = T._req("POST", "/graphql", body)
    if d.get("errors"):
        raise RuntimeError(str(d["errors"][0].get("message"))[:200])
    return d["data"]

def slug(email):
    return re.sub(r"[^a-z0-9]+", "-", email.lower()).strip("-") or "unknown"

def candidate_leads():
    """(id, email) for stage IDENTIFIED/ENRICHED_VERIFIED, deterministic order."""
    d = gql("query { people(filter: {stage: {in: [IDENTIFIED, ENRICHED_VERIFIED]}}, first: 1000, "
            "orderBy: {createdAt: AscNullsFirst}) { edges { node { id emails { primaryEmail } } } } }")
    out = []
    for e in d["people"]["edges"]:
        em = ((e["node"].get("emails") or {}).get("primaryEmail") or "").strip().lower()
        if em:
            out.append((e["node"]["id"], em))
    return out

def has_dossier_note(ids):
    """Set of person ids that already carry a GTM dossier note."""
    covered = set()
    for i in range(0, len(ids), 200):
        chunk = ids[i:i+200]
        d = gql("query($ids: [ID!]) { noteTargets(filter: {targetPersonId: {in: $ids}}, first: 1000) "
                "{ edges { node { targetPersonId note { title } } } } }", {"ids": chunk})
        for e in d["noteTargets"]["edges"]:
            n = e["node"].get("note") or {}
            if (n.get("title") or "").startswith(NOTE_PREFIX):
                covered.add(e["node"]["targetPersonId"])
    return covered

def run_tool(argv, timeout):
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        return (r.stdout or "")[:6000]
    except Exception:
        return ""

def dossier_select(limit):
    cands = candidate_leads()
    covered = has_dossier_note([c[0] for c in cands])
    leads = [{"id": pid, "email": em} for pid, em in cands if pid not in covered][:limit]
    return {"ok": True, "leads": leads}

def dossier_build(email):
    from datetime import datetime
    email = email.lower().strip()
    person = T.get(email)
    if not person:
        return {"ok": False, "error": "no person for " + email}
    pid = person.get("id")
    name = ((person.get("name") or {}).get("firstName") or "").strip() + " " + \
           ((person.get("name") or {}).get("lastName") or "").strip()
    name = name.strip().strip('"') or "(unknown)"
    job = (person.get("jobTitle") or "").strip()
    li = ((person.get("linkedinLink") or {}).get("primaryLinkUrl") or "").strip()
    domain = email.split("@")[-1] if "@" in email else ""
    site = "https://" + domain if domain else ""
    company = ""
    if person.get("companyId"):
        try:
            company = (T._req("GET", "/rest/companies/" + person["companyId"]).get("data") or {}).get("name") or ""
        except Exception:
            pass
    icp = person.get("icpScore")
    # pass 1: gather + list gaps
    rec = {"company": company, "website": li, "role": job, "pain": "", "fit": ""}
    gaps = [k for k, v in (("company", company), ("website", li), ("role", job),
                           ("pain", ""), ("fit", icp)) if not v]
    evidence = ["- evidence: crm Twenty person " + pid + " record (GET /rest/people, stage "
                + str(person.get("stage")) + ")",
                "- evidence: crm field jobTitle: " + (job or "(empty on record)"),
                "- evidence: crm field source: " + str(person.get("source") or "(empty)") +
                ", channel: " + str(person.get("channel") or "(empty)")]
    passes = 1
    # pass 2: fill gaps via read-only research tools
    if gaps:
        passes = 2
        q = (company or domain or email) + " " + (job or name)
        rag = run_tool([BIN + "/rig-rag", "search", q.strip(), "-k", "3"], 60)
        m = re.search(r"(\[[0-9]\] (\S+): (.+?))\n    (.+)", rag)
        if m:
            src, path, snippet = m.group(2), m.group(3).strip(), m.group(4).strip()
            evidence.append("- evidence: rig-rag (%s) %s: %s" % (src, path, snippet[:180]))
        url = li or site
        if url:
            page = run_tool([BIN + "/reach", "read", url], 60)
            body = re.sub(r"^(Title|URL Source|Published Time|Markdown Content)[:].*$", "",
                          page, flags=re.M)
            first = next((ln.strip() for ln in body.splitlines()
                          if len(ln.strip()) > 40 and "Warning:" not in ln
                          and "Security Checkpoint" not in ln), "")
            if first:
                evidence.append("- evidence: reach read %s: %s" % (url, first[:180]))
                rec["pain"] = first[:200]
                rec["website"] = url
    # pass 3: fit line + remaining gaps marked UNKNOWN (no guessing)
    passes = 3
    if icp is not None:
        rec["fit"] = "crm icpScore " + str(icp)
    else:
        rec["fit"] = "unscored (source=" + str(person.get("source") or "")[:60] + ")"
    gaps = sorted(g for g in ("company", "website", "role", "pain", "fit") if not rec.get(g))
    angle = ("Angle: " + (("%s at %s — " % (name, company)) if company else ("%s — " % name)) +
             (rec["pain"][:120] if rec["pain"] else
              "RIG agentic setup/ops work; open with the one concrete observation on record."))
    L = ["# Dossier — %s <%s>" % (name, email), "",
         "- email: " + email,
         "- person_id: " + pid,
         "- crm_stage: " + str(person.get("stage")),
         "- dossier_passes: %d" % passes,
         "- built_at: " + datetime.now().astimezone().isoformat(timespec="seconds"),
         "",
         "## Identity",
         "- name: " + name,
         "- role: " + (rec["role"] or "UNKNOWN"),
         "- company: " + (rec["company"] or "UNKNOWN"),
         "- website: " + (rec["website"] or "UNKNOWN"),
         "- linkedin: " + (li or "none on record"),
         "- location: UNKNOWN (not on record)",
         "",
         "## Source and channel",
         "- source: " + str(person.get("source") or "UNKNOWN"),
         "- channel: " + str(person.get("channel") or "UNKNOWN"),
         "- owner_agent: " + str(person.get("ownerAgent") or "UNKNOWN"),
         "- last_touch_at: " + str(person.get("lastTouchAt") or "never"),
         "",
         "## ICP score",
         "- icpScore: " + (str(icp) if icp is not None else "UNKNOWN"),
         "- note: scored by icp-scorer when present; dossier never changes the stage",
         "",
         "## Evidence"] + evidence + [
         "",
         "## Suggested angle",
         "- " + angle,
         "- Why: every fact above names its source; gaps are explicit UNKNOWNs, not guesses",
         "",
         "## Open gaps"] + ["- %s: UNKNOWN" % g for g in gaps] + [
         "",
         "---",
         "Generated by dossier-builder (W1a). Research + storage only: no touch, no send."]
    text = "\n".join(L) + "\n"
    path = DOSS + "/" + slug(email) + ".md"
    os.makedirs(DOSS, exist_ok=True)
    open(path, "w").write(text)
    # store on the Twenty record: note + noteTarget (two calls; nested write unsupported)
    note_body = "Dossier: " + path + "\n\n" + "\n".join(L[:15])
    d = gql("mutation($d: NoteCreateInput!) { createNote(data: $d) { id } }",
            {"d": {"title": NOTE_PREFIX + email, "bodyV2": {"markdown": note_body}}})
    nid = d["createNote"]["id"]
    gql("mutation($d: NoteTargetCreateInput!) { createNoteTarget(data: $d) { id } }",
        {"d": {"noteId": nid, "targetPersonId": pid}})
    return {"ok": True, "email": email, "path": path, "lines": len(text.splitlines()),
            "passes": passes, "note_id": nid, "gaps": gaps}

def dossier_verify(limit):
    r = subprocess.run([sys.executable, REPO + "/tests/check_dossiers.py"],
                       capture_output=True, text=True, timeout=300, cwd=REPO)
    return {"ok": r.returncode == 0, "exit": r.returncode,
            "output": ((r.stdout or "") + (r.stderr or ""))[-4000:]}

if cmd == "dossier_select":
    out = dossier_select(int(p.get("limit", 25)))
elif cmd == "dossier_build":
    out = dossier_build(str(p["email"]))
elif cmd == "dossier_verify":
    out = dossier_verify(int(p.get("limit", 25)))
else:
    out = {"ok": False, "error": "unknown cmd " + str(cmd)}
print(json.dumps(out))
'''
