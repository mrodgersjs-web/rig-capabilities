#!/usr/bin/env python3
"""Traject sync: jobs/queue.json + documents + contacts + to-do <-> the Vercel app.

    python3 scripts/traject_sync.py push|pull|both [--allow-empty] [--fixture] | selfcheck

push      uploads the A/B/C rows (exactly the 12 app fields), the document copies (resume,
          why-i-left, game plan, practice session when written), the app content (app-content/:
          practice question, Lucy watch list), the 12 recommendation drafts, the contact map
          (outreach/contact-map.json projected to the spec shape - evidence dropped), today's
          to-do list (app-content/todo.json) and the per-job apply kits (resume PDF + cover
          letter body) - content goes up sanitized (banned phrases masked to [private]);
          drafts, documents, contacts, to-do and kits are strict-gated
pull      writes the app's status/notes/applied_at back into jobs/queue.json, James's
          recommendation reviews into outreach/recommendation-review.json, his to-do ticks into
          app-content/todo-state.json and his outreach log into outreach/contact-state.json
          (all atomic, merge by id, re-read first)
both      push, then pull. Run this after anything updates queue.json.
selfcheck the leak gate: must go red on planted text, green on clean text (and on "multiple")
--fixture develop against app/cloud/fixtures/{contact-map,todo}.json instead of the real
          files (the fixtures are never deployed; the real files replace them when they land)

Ownership: local owns the job fields and the row set; the app owns status, notes, applied_at.
Document copies are cut at their marked internal/private sections before upload.
Leak gate: nothing is uploaded until every uploaded string passes it; a hit refuses the push
with exit 2 and names the row/field and the rule, never the matched text. Documents are
scanned as visible text (HTML tags dropped, whitespace collapsed). Rules by field:
  document html      : banned words, "274", any "$" amount
  job prose fields   : banned words, "274", any "$" amount  (title, company, location,
                       fit_reasons, notes)
  job salary_text    : banned words only (verbatim posting pay may quote amounts, incl. $170K)
  machine fields     : not scanned (id, url, workplace, status, fit_tier, applied_at are
                       identifiers, not text; a hex id may legally contain "274")
Apply kit resume rule (coordinator, 2026-09-25): packets/<id>/James-Loehr-Resume.pdf files are
stale (tailored from the old v11 base). A packet PDF is served only when
packets/<id>/RESUME-BASE-v19.ok exists (written by the RETAILOR-V19 lane after its checks);
otherwise the kit serves deliverables/James-Loehr-Resume-FINAL.pdf (FINAL v19) for that job.
The marker is re-checked on every push.
Secrets come from the macOS keychain (com.rig.env.JAMES_TRAJECT_SYNC_KEY) and are never printed.
"""
import base64
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "app"))
import traject  # noqa: E402  load_queue / save_queue / md_to_html: one queue IO, one renderer

URL = os.environ.get("TRAJECT_URL", "https://james-traject.vercel.app").rstrip("/")
SYNC_KEYCHAIN = "com.rig.env.JAMES_TRAJECT_SYNC_KEY"
DOC_SRC = {
    "resume": ("resume/james-loehr-resume.md", "My resume"),
    "why": ("strategy/why-i-left.md", "Why I left - what to say"),
    "plan": ("strategy/one-pager.md", "My game plan"),
    "practice": ("prep/practice-session-1.md", "My practice session"),
}
FIELDS = ["id", "title", "company", "location", "workplace", "url", "salary_text",
          "fit_tier", "fit_reasons", "status", "notes", "applied_at"]
PROSE = ["title", "company", "location", "fit_reasons", "notes"]
TIERS = ("A", "B", "C")

CONTACT_MAP_SRC = os.path.join(ROOT, "outreach", "contact-map.json")
TODO_SRC = os.path.join(ROOT, "app-content", "todo.json")
PREP_SRC = os.path.join(ROOT, "app-content", "interview-prep.json")
TODO_STATE = os.path.join(ROOT, "app-content", "todo-state.json")
CONTACT_STATE = os.path.join(ROOT, "outreach", "contact-state.json")
FIXTURES = os.path.join(ROOT, "app", "cloud", "fixtures")
PACKETS = os.path.join(ROOT, "packets")
FINAL_RESUME = os.path.join(ROOT, "deliverables", "James-Loehr-Resume-FINAL.pdf")
V19_MARKER = "RESUME-BASE-v19.ok"  # coordinator rule 2026-09-25: packet PDF is served only with it

# --- leak gate ---------------------------------------------------------------
# Word tokens match whole words only. "LTIP" as a bare substring matched "multiple"
# in 186 queue rows (measured 2026-09-23) and would brick every push.
WORD = [
    (r"\bpushed\s+out\b", "banned phrase: pushed out"),
    (r"\baligned\s+with\b", "banned phrase: aligned with"),
    (r"\bLTIP\b", "banned word: LTIP"),
    (r"\bcomp\s+band\b", "banned phrase: comp band"),
    (r"\bjames-os\b", "banned word: james-os"),
    (r"\bseverance\b", "banned word: severance"),
]
NUM_274 = (r"(?<!\d)274(?!\d)", "banned number: 274")
MONEY = (r"\$\s*\d", "money amount ($)")
# Extended rules for contacts / to-do / kit text (briefs/CONTACTS-TODO-SPEC.md): the banned
# phrases above plus agent-facing wording that must never reach James's phone.
EXTRA = [
    (r"\bcurrently\s+at\s+avis\b", "banned phrase: currently at avis"),
    (r"\bsince\s+1998\b", "banned phrase: since 1998"),
    (r"\b2[05]\s*\+\s*years\b", "banned claim: NN+ years"),
    (r"\blucy\s+rule\b", "agent text: Lucy rule"),
    (r"\blucy\s+[0-9a-f]{6,}\b", "agent text: Lucy rule id"),
    (r"\bsrc\s+video\b", "agent text: SRC video"),
    (r"\.md\b", "file path"),
]
# Wording words (Mike: "plain words only on screen"). Hard-blocking for message text James
# sends; for interview-prep coaching prose they are warnings only (a "Don't say" tab may
# legitimately quote what not to claim) and the lane is asked to reword them.
EXTRA_SOFT = [
    (r"\bfroze\b|\bfreeze\b|\bfrozen\b", "screen wording: freeze"),
    (r"\bunverified\b", "screen wording: unverified"),
    (r"\btier\b", "screen wording: tier"),
    (r"\breq\b", "screen wording: req"),
    (r"\bon\s+hold\b", "screen wording: hold"),
]
EMAIL_RE = re.compile(r"\b\S+@\S+\.\S+\b")

CUT_FROM = re.compile(r"^##\s+(sources used|.*internal)", re.I)  # resume's own internal tail
CUT_HEADS = ("your numbers", "never say")  # comp block / banned-words box
BANNED_BOX = re.compile(r"\s*\(Banned words:[^)]*\)")


def as_text(v):
    if v is None:
        return ""
    return " ".join(str(x) for x in v) if isinstance(v, list) else str(v)


def scan(label, text, money=False, num274=False, extra=False):
    """Rule labels only - the matched text may itself be the leak, so it is never echoed.

    Scans the visible text: tags are dropped and whitespace collapsed so a phrase split
    across a line wrap or an HTML tag (which the real one-pager did) still matches.
    """
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]*>", " ", text or ""))
    hits = []
    for pat, name in WORD:
        if re.search(pat, text or "", re.I):
            hits.append("%s: %s" % (label, name))
    if extra:
        for pat, name in EXTRA:
            if re.search(pat, text or "", re.I):
                hits.append("%s: %s" % (label, name))
    if num274 and re.search(NUM_274[0], text or ""):
        hits.append("%s: %s" % (label, NUM_274[1]))
    if money and re.search(MONEY[0], text or ""):
        hits.append("%s: %s" % (label, MONEY[1]))
    return hits


def scan_msg(label, text, signature=False, char_limit=None, word_limit=None):
    """Message-class text (contacts, to-do, kits): extended rules + the email rule.

    Emails are allowed only in contact.email and in James's own signature line: with
    signature=True the trailing block after the last blank line is exempt from the email
    scan when it is his signature (contains "James"), so "Best,\\nJames Loehr <his email>"
    passes while a mid-message address does not.
    """
    text = text or ""
    hits = scan(label, text, money=True, num274=True, extra=True) + soft_hits(text)
    body = text
    if signature:
        tail_at = text.rfind("\n\n")
        tail = text[tail_at + 2:] if tail_at >= 0 else ""
        if re.search(r"\bjames\b", tail, re.I):
            body = text[:tail_at] if tail_at >= 0 else ""
    if EMAIL_RE.search(body or ""):
        hits.append("%s: email address outside contact.email" % label)
    if char_limit is not None and len(text) > char_limit:
        hits.append("%s: over %d characters" % (label, char_limit))
    if word_limit is not None and len(text.split()) > word_limit:
        hits.append("%s: over %d words" % (label, word_limit))
    return hits


def soft_hits(text):
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]*>", " ", text or ""))
    return ["%s" % name for pat, name in EXTRA_SOFT if re.search(pat, text or "", re.I)]


def content_redact(content):
    """Content goes up sanitized (the addendum's "sanitized sync"): banned phrases become a
    visible [private] marker. Money and "274" are NOT auto-masked - a comp number in these
    files means the source needs a human look, so those still refuse the push. Documents and
    job rows keep the strict rule (a planted phrase there fails the push)."""
    def fix(v):
        if not isinstance(v, str):
            return v
        for pat, _ in WORD:
            v = re.sub(pat, "[private]", v, flags=re.I)
        return v

    c = dict(content or {})
    day = dict(c.get("day") or {})
    day["theme"] = fix(day.get("theme"))
    day["checklist"] = [dict(it, text=fix(it.get("text")), note=fix(it.get("note")))
                        if isinstance(it, dict) else fix(it) for it in (day.get("checklist") or [])]
    pr = dict(c.get("practice") or {})
    pr["question"] = fix(pr.get("question"))
    pr["tips"] = fix(pr.get("tips"))
    c["watch"] = [dict(v, title=fix(v.get("title")), why=fix(v.get("why")), task=fix(v.get("task")))
                  if isinstance(v, dict) else v for v in (c.get("watch") or [])]
    c["day"], c["practice"] = day, pr
    return c


def content_problems(content):
    """app-content/* (My day + practice) is document-class text: no words, no 274, no money."""
    bad = []
    c = content or {}
    day = c.get("day") or {}
    bad += scan("content day.theme", as_text(day.get("theme")), money=True, num274=True)
    for i, it in enumerate(day.get("checklist") or []):
        bad += scan("content day.checklist[%d]" % i, as_text(it), money=True, num274=True)
    pr = c.get("practice") or {}
    bad += scan("content practice.question", as_text(pr.get("question")), money=True, num274=True)
    bad += scan("content practice.tips", as_text(pr.get("tips")), money=True, num274=True)
    for i, v in enumerate(c.get("watch") or []):
        if isinstance(v, dict):
            for k in ("title", "why", "task", "day"):
                bad += scan("content watch[%d].%s" % (i, k), as_text(v.get(k)), money=True, num274=True)
        else:
            bad += scan("content watch[%d]" % i, as_text(v), money=True, num274=True)
    return bad


def review_problems(review):
    """Review items are strict-gated like recommendation drafts: banned words, "274", money."""
    bad = []
    for it in (review or {}).get("items") or []:
        for k in ("title", "text", "question", "context", "name", "person_title", "relationship"):
            bad += scan("review %s field %s" % (it.get("id"), k), as_text(it.get(k)), money=True, num274=True)
        for i, c in enumerate(it.get("choices") or []):
            bad += scan("review %s choice %d" % (it.get("id"), i), as_text(c), money=True, num274=True)
    return bad


def pdf_bytes_problems(label, raw):
    """Best-effort: scan the PDF's own strings plus decompressed content streams (fonts and
    compressed streams can hide text; this catches the readable layers). No email rule: a
    resume header carries James's own contact block by design."""
    texts = []
    for m in re.finditer(rb"stream\r?\n([\s\S]*?)endstream", raw):
        try:
            texts.append(zlib.decompress(m.group(1)))
        except Exception:
            pass
    texts.append(raw)
    strings = re.findall(rb"\((?:\\.|[^\\()])*\)", b"\n".join(texts))
    # only printable ASCII literals are text; font/binary chunks produce false "274"/"$" hits
    strings = [s for s in strings if re.match(rb"^[\x20-\x7e\t]*$", s)]
    blob = b" ".join(strings).decode("latin-1", "replace")
    return scan(label + " (extracted strings)", blob, money=True, num274=True, extra=True)


def pdf_problems(pdf_b64):
    if not pdf_b64:
        return []
    return pdf_bytes_problems("resume PDF", base64.b64decode(pdf_b64))


def rec_problems(recs):
    """Recommendation drafts are strict-gated like documents (no masking: James edits this text)."""
    bad = []
    for p in (recs or {}).get("people") or []:
        for k in ("name", "title", "relationship", "text"):
            bad += scan("recommendation %s field %s" % (p.get("id"), k), as_text(p.get(k)), money=True, num274=True)
    return bad


def sanitize(jobs, docs, content=None, recs=None, review=None, contacts=None, todo=None, kits=None, prep=None):
    bad = []
    for j in jobs:
        extra = sorted(set(j) - set(FIELDS))
        if extra:
            bad.append("row %s: non-app fields %s" % (j.get("id"), extra))
        for k in PROSE:
            bad += scan("row %s field %s" % (j.get("id"), k), as_text(j.get(k)), money=True, num274=True)
        bad += scan("row %s field salary_text" % j.get("id"), as_text(j.get("salary_text")))
    for key, d in docs.items():
        bad += scan("doc %s" % key, as_text(d.get("html")), money=True, num274=True)
    bad += content_problems(content)
    bad += rec_problems(recs)
    bad += review_problems(review)
    bad += pdf_problems((review or {}).get("pdf_b64"))
    if contacts is not None:
        bad += contacts_problems(contacts)
    if todo is not None:
        bad += todo_problems(todo)
    if prep is not None:
        bad += prep_problems(prep)[0]
    for jid, k in (kits or {}).items():
        bad += scan_msg("kit %s cover_letter" % jid, as_text(k.get("cover_letter")),
                        signature=True, word_limit=120)
    return bad


def cloud_doc(md):
    """Structural cuts only: marked internal tails and the two private sections."""
    md = BANNED_BOX.sub(" ", md)  # the box wraps across lines in the source
    out, cutting = [], False
    for line in md.splitlines():
        if line.startswith("## "):
            if CUT_FROM.match(line):
                break
            cutting = line[3:].strip().lower().startswith(CUT_HEADS)
        if not cutting:
            out.append(line)
    return "\n".join(out)


def project(row):
    out = {k: row[k] for k in FIELDS if k in row}
    out.setdefault("fit_reasons", [])
    out.setdefault("notes", "")
    out.setdefault("applied_at", None)
    return out


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def atomic_write_json(path, data):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)  # atomic
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# --- contacts + to-do projection (briefs/CONTACTS-TODO-SPEC.md shapes only) ---
# The cloud projection drops `evidence` and any key not in the spec. Contact ids are
# stable across rebuilds (job_id:role:slug(name)) so "sent" state survives pushes.
MSG_KEYS = ["connect_note", "dm", "email_subject", "email_body", "intro_blurb",
            "comment", "comment_post_url", "followup"]
CONTACT_KEYS = ["id", "role", "role_label", "name", "first_name", "title", "degree",
                "confidence", "why", "linkedin_url", "linkedin_search_url", "email", "step"]
JOB_KEYS = ["job_id", "company", "title", "location", "apply_url", "posting_url",
            "deadline", "priority", "status", "plan"]
ITEM_KEYS = ["id", "n", "kind", "title", "detail", "person", "job_id", "contact_id",
             "copy_text", "copy_label", "links", "minutes"]


def project_contact_map(raw):
    jobs = []
    for j in (raw or {}).get("jobs") or []:
        contacts = []
        for c in j.get("contacts") or []:
            out = {k: c.get(k) for k in CONTACT_KEYS if c.get(k) is not None}
            via = c.get("via") or {}
            out["via"] = {"name": str(via.get("name") or ""), "role": str(via.get("role") or "")}
            msgs = c.get("messages") or {}
            out["messages"] = {k: str(msgs.get(k) or "") for k in MSG_KEYS}
            if out.get("id"):
                contacts.append(out)
        jobs.append({
            **{k: j.get(k) for k in JOB_KEYS if j.get(k) is not None},
            "contacts": contacts,
            "diy_links": [{"label": str(d.get("label") or ""), "url": str(d.get("url") or "")}
                          for d in j.get("diy_links") or [] if d],
        })
    return {"generated_at": str((raw or {}).get("generated_at") or ""), "jobs": jobs}


def project_todo(raw):
    def item(it):
        if not isinstance(it, dict) or not it.get("id"):
            return None
        out = {k: it.get(k) for k in ITEM_KEYS if it.get(k) is not None}
        out["links"] = [{"label": str(l.get("label") or ""), "url": str(l.get("url") or "")}
                        for l in it.get("links") or [] if l]
        return out

    items = [x for x in (item(i) for i in (raw or {}).get("items") or []) if x]
    later = [x for x in (item(i) for i in (raw or {}).get("later") or []) if x]
    return {"date": str((raw or {}).get("date") or ""), "title": str((raw or {}).get("title") or ""),
            "intro": str((raw or {}).get("intro") or ""), "items": items, "later": later}


def contacts_problems(cmap):
    """Contact-map text is message-class: extended rules, the email rule, length limits."""
    bad = []
    for j in (cmap or {}).get("jobs") or []:
        jid = j.get("job_id")
        for k in ("company", "title", "location", "plan", "status"):
            bad += scan_msg("contact job %s field %s" % (jid, k), as_text(j.get(k)))
        for c in j.get("contacts") or []:
            cid = c.get("id")
            for k in ("role_label", "name", "first_name", "title", "why"):
                bad += scan_msg("contact %s field %s" % (cid, k), as_text(c.get(k)))
            bad += scan("contact %s field email" % cid, as_text(c.get("email")),
                        money=True, num274=True, extra=True)
            m = c.get("messages") or {}
            bad += scan_msg("contact %s connect_note" % cid, as_text(m.get("connect_note")), char_limit=200)
            bad += scan_msg("contact %s dm" % cid, as_text(m.get("dm")), signature=True, char_limit=600)
            bad += scan_msg("contact %s email_subject" % cid, as_text(m.get("email_subject")))
            bad += scan_msg("contact %s email_body" % cid, as_text(m.get("email_body")),
                            signature=True, word_limit=120)
            bad += scan_msg("contact %s intro_blurb" % cid, as_text(m.get("intro_blurb")), char_limit=500)
            bad += scan_msg("contact %s comment" % cid, as_text(m.get("comment")))
            bad += scan_msg("contact %s followup" % cid, as_text(m.get("followup")),
                            signature=True, char_limit=300)
        for i, d in enumerate(j.get("diy_links") or []):
            bad += scan_msg("contact job %s diy_links[%d].label" % (jid, i), as_text(d.get("label")))
    return bad


def todo_problems(todo):
    bad = []
    t = todo or {}
    for k in ("title", "intro"):
        bad += scan_msg("todo %s" % k, as_text(t.get(k)))
    for group in ("items", "later"):
        for it in t.get(group) or []:
            iid = it.get("id")
            for k in ("title", "detail", "person", "copy_label"):
                bad += scan_msg("todo %s field %s" % (iid, k), as_text(it.get(k)))
            text = as_text(it.get("copy_text"))
            if not text:
                continue
            if it.get("kind") == "connect":
                bad += scan_msg("todo %s copy_text" % iid, text, char_limit=200)  # free-account limit
            elif it.get("kind") == "email":
                bad += scan_msg("todo %s copy_text" % iid, text, signature=True, word_limit=120)
            else:
                bad += scan_msg("todo %s copy_text" % iid, text, signature=True, char_limit=600)
            for i, ln in enumerate(it.get("links") or []):
                bad += scan_msg("todo %s links[%d].label" % (iid, i), as_text(ln.get("label")))
    return bad


def prep_problems(prep):
    """Interview prep is document-class text: every string at any depth gets the banned
    words, 274 and money rules (the Salary talk script must quote wording, never numbers).
    Hard hits refuse the push; plain-words wording hits come back as warnings only - the
    file belongs to the INTERVIEW-PREP lane and a coaching "Don't say" tab may quote what
    not to claim, so those are reported for rewording instead of blocking James's app."""
    bad, warn = [], []

    def walk(node, path):
        if isinstance(node, str):
            bad.extend(scan("prep %s" % path, node, money=True, num274=True, extra=True))
            warn.extend("prep %s: %s" % (path, h) for h in soft_hits(node))
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, "%s.%s" % (path, k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, "%s[%d]" % (path, i))

    walk(prep or {}, "root")
    return bad, warn


def extract_cover_letter(md):
    """The letter body only (the blockquote) plus the email subject line. Everything else
    in cover-letter.md is agent-facing (verification notes, Lucy ids, word counts) and is
    never pushed."""
    subject = ""
    m = re.search(r"\*\*Subject[^*]*\*\*:?\s*([^\n]*)", md)
    if m:
        subject = m.group(1).strip()
    lines = [re.sub(r"\*\*(.+?)\*\*", r"\1", ln[1:]).replace("`", "").strip()
             for ln in md.splitlines() if ln.startswith(">")]
    return subject, "\n".join(lines).strip()


def build_kits():
    """Apply kits per job: cover-letter body + resume PDF per the coordinator's resume rule
    (packet PDF only when RESUME-BASE-v19.ok exists, else FINAL v19). Markers are re-checked
    on every push, so a newly retailed packet is picked up automatically."""
    kits, pdfs, problems = {}, {}, []
    if not os.path.isdir(PACKETS):
        return kits, pdfs, problems
    for jid in sorted(os.listdir(PACKETS)):
        pdir = os.path.join(PACKETS, jid)
        if jid.startswith("_") or not os.path.isdir(pdir):
            continue
        try:
            with open(os.path.join(pdir, "cover-letter.md"), encoding="utf-8") as f:
                subject, body = extract_cover_letter(f.read())
        except OSError:
            continue
        if not body:
            problems.append("kit %s: cover letter body not found in cover-letter.md" % jid)
            continue
        tailored = os.path.exists(os.path.join(pdir, V19_MARKER))
        pdf_path = os.path.join(pdir, "James-Loehr-Resume.pdf") if tailored else FINAL_RESUME
        try:
            with open(pdf_path, "rb") as f:
                raw = f.read()
        except OSError:
            problems.append("kit %s: resume PDF missing (%s)" % (jid, os.path.basename(pdf_path)))
            continue
        kits[jid] = {"subject": subject, "cover_letter": body,
                     "resume": "tailored" if tailored else "final",
                     "pdf_sha256": hashlib.sha256(raw).hexdigest()}
        pdfs[jid] = base64.b64encode(raw).decode()
        problems += scan_msg("kit %s cover_letter" % jid, body, signature=True, word_limit=120)
        problems += pdf_bytes_problems("kit %s resume PDF" % jid, raw)
    return kits, pdfs, problems


def build(fixture=False):
    """Assemble the whole push payload. fixture=True develops against
    app/cloud/fixtures/ instead of the real outreach/contact-map.json + app-content/todo.json."""
    jobs = [project(j) for j in traject.load_queue() if j.get("fit_tier") in TIERS]
    docs = {}
    for key, (path, title) in DOC_SRC.items():
        try:
            with open(os.path.join(ROOT, path), encoding="utf-8") as f:
                md = cloud_doc(f.read())
        except OSError:
            continue  # not written yet (e.g. prep/practice-session-1.md)
        docs[key] = {"title": title, "html": traject.md_to_html(md)}
    recs = {"people": [{"id": p.get("id"), "name": p.get("name"), "title": p.get("title"),
                        "relationship": p.get("relationship"), "text": p.get("text")}
                       for p in traject.load_recommenders()]}
    cmap = load_json(os.path.join(FIXTURES, "contact-map.json") if fixture else CONTACT_MAP_SRC)
    todo = load_json(os.path.join(FIXTURES, "todo.json") if fixture else TODO_SRC)
    kits, pdfs, kit_bad = build_kits()
    return {
        "jobs": jobs, "docs": docs, "content": content_redact(traject.load_content()),
        "recs": recs, "review": build_review(),
        "contacts": project_contact_map(cmap) if cmap else None,
        "todo": project_todo(todo) if todo else None,
        "prep": load_json(PREP_SRC),
        "prep_warn": prep_problems(load_json(PREP_SRC))[1] if load_json(PREP_SRC) else [],
        "kits": kits, "pdfs": pdfs, "kit_bad": kit_bad,
    }


def build_review():
    """The /review board payload: the item list (read at push time - questions-resume.json may
    land any minute) plus the send-ready resume PDF bytes."""
    pdf_b64 = ""
    pdf_path = traject.resume_pdf_path()
    try:
        with open(pdf_path, "rb") as f:
            pdf_b64 = base64.b64encode(f.read()).decode()
    except OSError:
        print("review: resume PDF not present yet (/doc/resume-pdf will 404)", file=sys.stderr)
    return {"items": traject.load_review_items(), "pdf_b64": pdf_b64}


def keychain():
    r = subprocess.run(["security", "find-generic-password", "-s", SYNC_KEYCHAIN, "-w"],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        die("BLOCKED: %s not in the keychain (add with: security add-generic-password "
            "-s %s -a james -w)" % (SYNC_KEYCHAIN, SYNC_KEYCHAIN))
    return r.stdout.strip()


def http(method, path, data=None):
    req = urllib.request.Request(URL + path, method=method)
    req.add_header("X-Sync-Key", keychain())
    if data is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode("utf-8")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        die("%s %s -> HTTP %d %s" % (method, path, e.code, e.read().decode("utf-8", "replace")[:300]))
    except urllib.error.URLError as e:
        die("%s %s -> %s" % (method, path, e.reason))


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def push(allow_empty=False, fixture=False):
    b = build(fixture)
    if not b["jobs"] and not allow_empty:
        die("refusing to push 0 rows (queue.json empty or unreadable); --allow-empty overrides")
    bad = sanitize(b["jobs"], b["docs"], b["content"], b["recs"], b["review"],
                   b["contacts"], b["todo"], b["kits"], b["prep"]) + b["kit_bad"]
    if bad:
        for x in bad:
            print("LEAK GATE " + x, file=sys.stderr)
        die("push refused: %d leak-gate hit(s); nothing uploaded" % len(bad), 2)
    for w in b.get("prep_warn") or []:
        print("PREP WORDING (ask INTERVIEW-PREP lane to reword) " + w, file=sys.stderr)
    payload = {"pushed_at": now(), "jobs": b["jobs"], "docs": b["docs"], "content": b["content"],
               "recommendations": b["recs"], "review_items": b["review"]["items"],
               "resume_pdf_b64": b["review"]["pdf_b64"]}
    if b["contacts"] is not None:
        payload["contacts"] = b["contacts"]
    if b["todo"] is not None:
        payload["todo"] = b["todo"]
    if b["prep"] is not None:
        payload["prep"] = b["prep"]
    if b["kits"]:
        payload["kits"] = {"items": b["kits"]}
    r = http("POST", "/api/sync", payload)
    # Kit PDFs go up one per request (35 base64 PDFs exceed the serverless body limit in a
    # single push); the server reports what it already has so re-pushes upload nothing.
    have = r.get("kit_pdfs") or {}
    sent = 0
    for jid, b64 in b["pdfs"].items():
        if have.get(jid) == b["kits"][jid]["pdf_sha256"]:
            continue
        http("POST", "/api/sync", {"kit_pdf": {"job_id": jid, "pdf_b64": b64,
                                               "sha256": b["kits"][jid]["pdf_sha256"]}})
        sent += 1
    print("push ok: %d rows, %d documents, content=%s, %d recommenders, %d review items, "
          "%d contacts jobs, %d todo items, prep=%s, %d kits (+%d pdfs)%s -> %s at %s"
          % (r["rows"], r["docs"], "yes" if r.get("content") else "none", r.get("recommenders", 0),
             r.get("review_items", 0), len((b["contacts"] or {}).get("jobs") or []),
             len((b["todo"] or {}).get("items") or []),
             "yes" if b["prep"] is not None else "none",
             len(b["kits"]), sent, " [FIXTURE DATA]" if fixture else "", URL, r["received_at"]))


def pull():
    r = http("GET", "/api/sync")
    app = {j["id"]: j for j in r.get("jobs", []) if j.get("id")}
    jobs = traject.load_queue()  # re-read immediately before the atomic write
    changed = 0
    for j in jobs:
        a = app.get(j.get("id"))
        if not a:
            continue
        for k in ("status", "notes", "applied_at"):
            if a.get(k) is not None and j.get(k) != a.get(k):
                j[k] = a[k]
                changed += 1
    traject.save_queue(jobs)
    n_people = traject.save_review(r.get("reviews") or {})
    review_answers = r.get("review_answers") or {}
    n_answers = traject.save_review_answers(review_answers)
    rec_map = {"approve": "approved", "send_back": "needs_changes", "skip": "skip"}
    legacy = {}
    for iid, rec in review_answers.items():
        if not str(iid).startswith("rec:"):
            continue
        if rec.get("decision") in rec_map:
            legacy[str(iid)[4:]] = {"name": rec.get("title") or iid, "decision": rec_map[rec.get("decision")],
                                    "feedback": rec.get("feedback") or "", "known_as": rec.get("known_as") or "",
                                    "text": rec.get("text") or ""}
    if legacy:
        traject.save_review(legacy)
    # James's own state: to-do ticks + outreach log (app-owned, merged, atomic).
    n_todo = merge_state(TODO_STATE, r.get("todo_state") or {})
    n_contact = merge_state(CONTACT_STATE, r.get("contact_state") or {})
    print("pull ok: %d app fields over %d local rows (app has %d rows); recommendation-review.json "
          "holds %d people; review/answers.json holds %d items; todo-state.json %d entries; "
          "contact-state.json %d entries"
          % (changed, len(jobs), len(app), n_people, n_answers, n_todo, n_contact))


def merge_state(path, incoming):
    """App-owned state mirrored locally (the app is the source of truth for these two
    files), atomic write, re-read first."""
    load_json(path)  # re-read before the write: other writers exist
    if not isinstance(incoming, dict):
        incoming = {}
    atomic_write_json(path, incoming)
    return len(incoming)


def selfcheck():
    """The gate must go red on planted text and stay green on clean text and on 'multiple'."""
    row = {"id": "selfcheck", "title": "Director, Operations", "company": "Acme", "location": "Denver, CO",
           "workplace": "hybrid", "url": "https://example.com/j/274", "salary_text": "$150,000-$170,000",
           "fit_tier": "A", "fit_reasons": ["multi-site operations"], "status": "new", "notes": "", "applied_at": None}
    docs = {"plan": {"title": "t", "html": "<p>A clean page about the plan.</p>"}}
    assert not sanitize([row], docs), "clean payload must pass (incl. 'multiple', salary_text $170K, id/url '274')"
    bad = dict(row, title="Director after being pushed out")
    assert sanitize([bad], docs), "planted phrase must be caught"
    bad = dict(row, notes="ask for $275K")
    assert sanitize([bad], docs), "planted money in a prose field must be caught"
    bad = dict(row, title="Managing Director 274 markets")
    assert sanitize([bad], docs), "planted number must be caught"
    baddocs = {"plan": {"title": "t", "html": "<p>Walk away below $170K base.</p>"}}
    assert sanitize([row], baddocs), "money inside a document must be caught"
    baddocs = {"plan": {"title": "t", "html": "<p>they were \"pushed</p><p>   out\" quietly</p>"}}
    assert sanitize([row], baddocs), "phrase split across a tag must be caught"
    assert sanitize([row], docs, {"day": {"checklist": ["aim is $275K"], "schedule": []},
                                  "practice": {"question": "", "tips": ""}}), "money in My day must be caught"
    assert sanitize([row], docs, None, {"people": [{"id": "x", "name": "A", "title": "B",
                                                    "relationship": "C", "text": "aim is $275K"}]}), \
        "money in a recommendation draft must be caught"
    masked = content_redact({"day": {"theme": "", "checklist": [{"text": "gather LTIP documents", "note": ""}]},
                             "practice": {"question": "why did you leave", "tips": ""}})
    assert "[private]" in masked["day"]["checklist"][0]["text"], "content phrase must be masked"
    assert not sanitize([row], docs, masked), "masked content must then pass"
    wrapped = cloud_doc('# P\n\n## The five rules\n\n1. Go. (Banned words: "pushed\n   out".)\n')
    assert "pushed" not in wrapped and "out\"" not in wrapped, "wrapped banned box not stripped"
    cut = cloud_doc("# P\n\n## Your numbers (private)\n\n- Aim: $275K.\n\n## The five rules\n\n1. Go.")
    assert "$" not in cut and "The five rules" in cut, "private section cut is broken"
    # contacts / to-do / kit text: extended rules + the email rule + length limits
    clean_c = {"jobs": [{"job_id": "x", "company": "Acme", "title": "Director", "location": "Denver",
                         "plan": "Apply today, then connect.", "status": "READY",
                         "contacts": [{"id": "x:h:m", "role": "hiring_manager", "role_label": "Likely boss",
                                       "name": "Ann Lee", "first_name": "Ann", "title": "VP Ops",
                                       "degree": "2nd", "confidence": "med", "why": "Likely boss.",
                                       "linkedin_url": "", "linkedin_search_url": "https://x",
                                       "email": "ann@example.com", "step": 1,
                                       "via": {"name": "Ann Lee", "role": "hiring_manager"},
                                       "messages": {"connect_note": "Hi Ann - quick note.", "dm": "",
                                                    "email_subject": "", "email_body": "Hi Ann.\n\nBest,\nJames",
                                                    "intro_blurb": "", "comment": "", "comment_post_url": "",
                                                    "followup": ""}}],
                         "diy_links": [{"label": "People you know at Acme", "url": "https://x"}]}]}
    assert not contacts_problems(clean_c), "clean contact map must pass"
    bad_c = json.loads(json.dumps(clean_c))
    bad_c["jobs"][0]["contacts"][0]["messages"]["connect_note"] = "Hi Ann - I am currently at Avis and keen."
    assert contacts_problems(bad_c), "planted currently-at-Avis must be caught"
    bad_c = json.loads(json.dumps(clean_c))
    bad_c["jobs"][0]["contacts"][0]["messages"]["dm"] = "Write me at james@example.org any time."
    assert contacts_problems(bad_c), "planted email outside contact.email must be caught"
    bad_c = json.loads(json.dumps(clean_c))
    bad_c["jobs"][0]["contacts"][0]["messages"]["connect_note"] = "x" * 201
    assert contacts_problems(bad_c), "connect note over 200 characters must be caught"
    bad_c = json.loads(json.dumps(clean_c))
    bad_c["jobs"][0]["contacts"][0]["messages"]["email_body"] = "word " * 121 + "\n\nBest,\nJames"
    assert contacts_problems(bad_c), "email body over 120 words must be caught"
    clean_t = {"date": "2026-09-25", "title": "Friday", "intro": "Go.",
               "items": [{"id": "a", "n": 1, "kind": "connect", "title": "Connect",
                          "detail": "Copy, open, paste.", "person": "Ann", "job_id": "x",
                          "contact_id": "x:h:m", "copy_text": "Hi Ann - quick note.",
                          "copy_label": "Copy note", "links": [], "minutes": 5}], "later": []}
    assert not todo_problems(clean_t), "clean todo must pass"
    bad_t = json.loads(json.dumps(clean_t))
    bad_t["items"][0]["copy_text"] = "18+ years, aiming for $275K."
    assert todo_problems(bad_t), "planted money in a todo item must be caught"
    bad_t = json.loads(json.dumps(clean_t))
    bad_t["items"][0]["copy_text"] = "x" * 201
    assert todo_problems(bad_t), "connect copy over 200 characters must be caught"
    bad_t = json.loads(json.dumps(clean_t))
    bad_t["items"][0]["title"] = "Apply since 1998 to this role"
    assert todo_problems(bad_t), "planted since-1998 must be caught"
    clean_p = {
        "generated_at": "t",
        "general": {"tabs": [{"id": "ninety", "label": "Your 90 seconds",
                              "sections": [{"heading": "H", "body": ["Say it in 90 seconds."]}]}]},
        "rooms": [{"id": "r1", "company": "Acme", "job_ids": ["x"], "title": "Director",
                   "subtitle": "You meet the team Friday.", "stage": "interviewing", "tabs": []}],
    }
    assert not prep_problems(clean_p)[0] and not prep_problems(clean_p)[1], "clean interview prep must pass"
    bad_p = json.loads(json.dumps(clean_p))
    bad_p["rooms"][0]["tabs"] = [
        {"id": "s", "label": "Salary talk",
         "sections": [{"heading": "Words", "body": ["Aim: $275K."]}]},
    ]
    assert prep_problems(bad_p)[0], "money in interview prep must be caught"
    soft_p = json.loads(json.dumps(clean_p))
    soft_p["rooms"][0]["subtitle"] = "Its link is unverified until the freeze ends."
    assert not prep_problems(soft_p)[0] and prep_problems(soft_p)[1], \
        "prep wording words must warn but not block"
    sig = dict(clean_c["jobs"][0]["contacts"][0]["messages"],
               email_body="Hi Ann.\n\nJames Loehr\n(402) 555-0100\njames@example.org")
    sig_c = json.loads(json.dumps(clean_c))
    sig_c["jobs"][0]["contacts"][0]["messages"] = sig
    assert not contacts_problems(sig_c), "James's own signature email must pass"
    body = dict(sig, email_body="Write to james@example.org any time.\n\nJames Loehr")
    mid_c = json.loads(json.dumps(clean_c))
    mid_c["jobs"][0]["contacts"][0]["messages"] = body
    assert contacts_problems(mid_c), "a mid-message email must still be caught"
    subj, body = extract_cover_letter("# Cover letter\n\n**Subject (email only):** Director - James\n\n"
                                      "> The letter body. (Lucy 0972fdad7c)\n\n79 words. S1 (Lucy x).")
    assert subj == "Director - James" and body == "The letter body. (Lucy 0972fdad7c)", \
        "cover letter extraction must keep only the letter body"
    assert scan_msg("kit", body), "agent text inside a letter body must be caught"
    good_kit = {"x": {"cover_letter": "I am applying for this role and would love a short call."}}
    assert not sanitize([row], docs, None, None, None, None, None, good_kit), "clean kit must pass"
    bad_kit = {"x": {"cover_letter": "18+ years since 1998 and counting."}}
    assert sanitize([row], docs, None, None, None, None, None, bad_kit), "planted kit phrase must be caught"
    print("selfcheck ok: gate red on phrase/money/number, doc money and tag-split phrase, "
          "contacts/todo/kit rules (email, lengths), green on clean text")


def die(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    verb = args[0] if args else "both"
    allow_empty = "--allow-empty" in sys.argv
    fixture = "--fixture" in sys.argv
    if verb == "push":
        push(allow_empty, fixture)
    elif verb == "pull":
        pull()
    elif verb == "both":
        push(allow_empty, fixture)
        pull()
    elif verb == "selfcheck":
        selfcheck()
    else:
        die("usage: traject_sync.py push|pull|both|selfcheck [--allow-empty] [--fixture]")


if __name__ == "__main__":
    main()
