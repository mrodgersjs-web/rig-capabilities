#!/usr/bin/env python3
# done_when: cmd:python3 scripts/hook_fires_misc.py done-gate.py
"""done-gate -- deterministic belts on done-claims; Jev only at escalation.

Claude Code Stop-hook core (harness-neutral: reads a JSON payload with
`transcript_path` + `stop_hook_active` on stdin, or `{"tail": "..."}` for
manual tests).

Ladder (per Mike's determinism doctrine, 2026-10-02):
  L0  regex belts (runner ran / pass line / fail line / done-word)
  L3  Jev, exactly one question set per stop, only for the class the belts
      cannot settle ("unverified_done"), asked in BOTH option orders and
      averaged (position-bias control; jevbench flagged 72% vs 21% swings
      from option order alone). Disagreement between orders is recorded as
      `order_mixed` so the calibration loop can find biased questions.

Classes:
  skip             no done-claim in the final assistant block
  verified         claim + runner ran + success line present
  failed_suite     claim + runner ran + failure line present (the "tests pass" lie)
  unverified_done  claim + no runner evidence at all

Exit contract (same as jev-bash-gate.sh):
  0  proceed.  2  BLOCK (stderr feeds back into the SAME session as a
  correction). Internal errors fail OPEN (exit 0). DONE_GATE=0 kills it.
  DONE_GATE_ENFORCE=0 (default) = shadow mode: decide, log, never block.
  stop_hook_active=true never re-blocks (prevents a stop-loop); it warns once.

Every decision is appended to ~/.rig/s1gate/done-gate.jsonl. The Jev calls
themselves land in ~/.rig/s1gate/decisions.db via rig-s1gate, so the whole
calibration loop (label / calibrate / stats) works on them unchanged.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime

HOOKS_DIR = os.path.dirname(os.path.realpath(__file__))
REDACT = os.path.join(HOOKS_DIR, "redact_state.py")
GATE_BIN = os.environ.get("S1GATE_BIN", os.path.expanduser("~/.rig/bin/rig-s1gate"))
SHADOW_LOG = os.path.expanduser("~/.rig/s1gate/done-gate.jsonl")

# --- L0 belts ---------------------------------------------------------------

DONE_WORDS = re.compile(
    r"\b(done|complete(?:d)?|finished|wrapped up|fixed|solved|patched|shipped|"
    r"deployed|resolved|implemented|added|created|updated|refactored|migrated|"
    r"verified|passes?d?|green|merged|landed|ready)\b", re.I)
STRONG_DONE = re.compile(
    r"(all done|that'?s\s+(?:done|complete|fixed)|task complete|"
    r"\bdone[.!]?\s*$|completed[.!]?\s*$|ready (?:to|for) (?:review|merge|ship)|"
    r"all (?:tests|checks) pass(?:ed)?\b)", re.I | re.M)

RUNNER_RE = re.compile(
    r"(npm\s+(?:test|run\s+(?:test|lint|build|check))|"
    r"\b(?:jest|vitest|pytest|rspec|go\s+test|cargo\s+test|bun\s+test|deno\s+test)\b|"
    r"make\s+(?:test|check|build)|just\s+test|tsc\s+--noEmit|"
    r"eslint\b|prettier\s+--check|mypy\b|flake8\b|pyright\b|black\s+--check|"
    r"python3?\s+-m\s+(?:pytest|unittest))", re.I)
SUCCESS_RE = re.compile(
    r"\d+\s+(?:tests?|assertions?|cases?)\s+(?:passed|ok|succeeded)\b|"
    r"all\s+(?:tests\s+)?pass(?:ed)?\b|completed\s+successfully|"
    r"exited\s+with\s+code\s+0\b|no\s+failures\b|"
    r"0\s+fail(?:ed|ures?)\b", re.I)
FAILED_RE = re.compile(
    r"\b\d+\s+(?:tests?|cases?|assertions?)\s+failed\b|\bFAILED\b|"
    r"\bfailures?:\s*[1-9]|exit(?:ed)?\s+with\s+code\s+[1-9]\b|"
    r"\bAssertionError\b|\bSyntaxError\b|command failed with exit code [1-9]", re.I)


def _content_text(content):
    """Anthropic content blocks -> text. tool_use carries name + command; tool_result its body."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out = []
        for pt in content:
            if not isinstance(pt, dict):
                out.append(str(pt))
                continue
            t = pt.get("type")
            if t == "text":
                out.append(str(pt.get("text", "")))
            elif t == "tool_use":
                inp = pt.get("input")
                cmd = inp.get("command") if isinstance(inp, dict) else None
                out.append("TOOL_USE %s %s" % (pt.get("name", ""), cmd or ""))
            elif t == "tool_result":
                c = pt.get("content")
                if isinstance(c, list):
                    out.append("\n".join(str(x.get("text", "")) for x in c if isinstance(x, dict))[:2000])
                else:
                    out.append(str(c or "")[:2000])
        return "\n".join(out)
    return str(content or "")


def load_transcript(path):
    """Return list of (role, text) for the tail after the last user message."""
    msgs = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()[-500:]
    except Exception:
        return []
    for line in lines:
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("type") not in ("user", "assistant"):
            continue
        m = d.get("message")
        role = (m or {}).get("role") if isinstance(m, dict) else d.get("type")
        content = (m or {}).get("content") if isinstance(m, dict) else m
        msgs.append((role, _content_text(content)))
    cut = 0
    for i, (role, _t) in enumerate(msgs):
        if role == "user":
            cut = i
    return msgs[cut:]


class Belts:
    def __init__(self):
        self.last_assistant = ""
        self.slice_text = ""
        self.runner_lines = []
        self.success = False
        self.failed = False

    @classmethod
    def extract(cls, payload):
        b = cls()
        transcript = (payload or {}).get("transcript_path")
        tail = (payload or {}).get("tail")
        slice_text = ""
        if transcript:
            slice_text = "\n".join(t for _r, t in load_transcript(transcript))
        elif isinstance(tail, str):
            slice_text = tail
        if not slice_text.strip():
            return b
        last_assistant = ""
        assistant_blocks = re.findall(r"", slice_text)  # placeholder no-op
        _ = assistant_blocks
        # last assistant text = everything after the final USER line boundary we
        # approximated above; transcripts already carry roles, so find it there.
        b.slice_text = slice_text
        b.last_assistant = slice_text.splitlines()[-30:]  # bottom of slice
        b.last_assistant = "\n".join(b.last_assistant)
        runners = []
        for m in RUNNER_RE.finditer(slice_text):
            runners.append(m.group(0).strip())
        b.runner_lines = list(dict.fromkeys(runners))[:8]
        b.success = bool(SUCCESS_RE.search(slice_text))
        b.failed = bool(FAILED_RE.search(slice_text)) and not b.success
        return b

    def decide(self):
        if not DONE_WORDS.search(self.last_assistant):
            return "skip"
        if not (STRONG_DONE.search(self.last_assistant) or len(self.last_assistant) < 400):
            return "skip"
        if self.runner_lines and self.success:
            return "verified"
        if self.runner_lines and self.failed:
            return "failed_suite"
        return "unverified_done"


# --- redaction ---------------------------------------------------------------

def redact(text):
    try:
        with open(REDACT, encoding="utf-8") as f:
            ns = {}
            exec(compile(f.read(), REDACT, "exec"), ns)
        return ns["redact"](text)
    except Exception:
        return text  # never break the gate because the redactor failed


# --- Jev layer: done.claim rubric, both orders, via rig-s1gate ----------------

def jev_both_orders(state, session):
    """Run rubric done.claim and its mirror; log rows; return verdict parts.

    rig-s1gate owns: endpoint, keychain, retries, cache, decisions.db logging
    (so rows are labelable with `rig-s1gate label`). We pass rubric names
    done.claim (normal order) and done.claim.mirror (choice criteria reversed).
    """
    if not os.path.isfile(GATE_BIN):
        return {"available": False, "reason": "gate binary missing"}
    out = {}
    for order, rubric in (("normal", "done.claim"), ("mirror", "done.claim.mirror")):
        try:
            r = subprocess.run(
                [GATE_BIN, "check", rubric, "--stdin", "--json",
                 "--subject", "done-gate:%s" % session],
                input=state, capture_output=True, text=True, timeout=12)
            try:
                body = json.loads(r.stdout or "{}")
            except Exception:
                body = {"parse_error": (r.stdout or "")[:120], "stderr": (r.stderr or "")[:120]}
            out[order] = {"rc": r.returncode, **{k: body.get(k) for k in
                          ("verdict", "answers", "advisory", "decision_id", "latency_ms", "model", "error")}}
        except Exception as e:
            out[order] = {"rc": -1, "error": str(e)[:120]}
    out["available"] = True
    return out


def consensus(out):
    """kind consensus + noul average + order-mix flag from the two orders."""
    kinds, nouls = [], []
    for order in ("normal", "mirror"):
        ans = (out.get(order) or {}).get("answers") or {}
        k = (ans.get("kind") or {}).get("choice")
        n = (ans.get("needs_evidence") or {}).get("noul")
        if k:
            kinds.append(k)
        if isinstance(n, (int, float)):
            nouls.append(float(n))
    majority = None
    if kinds:
        majority = max(set(kinds), key=kinds.count)
    avg = sum(nouls) / len(nouls) if nouls else None
    return {
        "kind": majority,
        "avg_noul": round(avg, 3) if avg is not None else None,
        "order_mixed": len(set(kinds)) > 1,
        "decisions": [ (out.get(o) or {}).get("decision_id") for o in ("normal", "mirror") ],
    }


def main():
    if os.environ.get("DONE_GATE") == "0":
        return 0
    enforce = os.environ.get("DONE_GATE_ENFORCE", "0") == "1"
    raw = sys.stdin.read()
    payload = {}
    if raw.strip():
        try:
            payload = json.loads(raw)
        except Exception:
            payload = {}
    stop_active = bool(payload.get("stop_hook_active"))
    session = str(payload.get("session_id", "?"))[:12]

    b = Belts.extract(payload)
    cls = b.decide()
    row = {"ts": datetime.now().isoformat(timespec="seconds"), "class": cls,
           "session": session, "stop_active": stop_active, "enforce": enforce,
           "runners": b.runner_lines}

    if cls in ("skip", "verified"):
        with open(SHADOW_LOG, "a") as f:
            f.write(json.dumps(row) + "\n")
        return 0

    if cls == "failed_suite":
        row["reason"] = "claim with failed runner output in slice"
        with open(SHADOW_LOG, "a") as f:
            f.write(json.dumps(row) + "\n")
        if enforce and not stop_active:
            sys.stderr.write(
                "done-gate BLOCK: the closing message says done, but the slice shows a "
                "FAILED runner result (%s). Report what actually failed and stop -- or "
                "fix it and re-run until a success line is in the slice.\n" % ", ".join(b.runner_lines[:3]))
            return 2
        sys.stderr.write("done-gate WARN (shadow): done-claim over a failing suite; log row written.\n")
        return 0

    # unverified_done
    if stop_active:
        with open(SHADOW_LOG, "a") as f:
            f.write(json.dumps({**row, "skipped": "stop_hook_active"}) + "\n")
        return 0

    state = redact("LAST ASSISTANT MESSAGE:\n%s\n\nRUNNER COMMANDS SEEN: %s\n" % (
        (b.last_assistant or "")[:1500], ", ".join(b.runner_lines) or "none"))
    out = jev_both_orders(state, session)
    con = consensus(out) if out.get("available") else {}
    row.update({"jev": out, **con})
    with open(SHADOW_LOG, "a") as f:
        f.write(json.dumps(row) + "\n")

    if enforce and con.get("kind") == "claim_needs_evidence" and (con.get("avg_noul") or 0) >= 0.55:
        sys.stderr.write(
            "done-gate BLOCK: closing message claims a produced result, no check ran in this slice "
            "(kind=%s, avg_noul=%.2f, orders agree=%s). "
            "Options: run the check now, or restate the outcome as 'unverified: <what was not run>' "
            "with the next verification step. Decision ids %s -- label them with "
            "`rig-s1gate label <id> good|bad`.\n" % (
                con.get("kind"), con.get("avg_noul"), not con.get("order_mixed"),
                ", ".join(str(d) for d in con.get("decisions", []))))
        return 2
    if enforce:
        sys.stderr.write("done-gate WARN (unverified_done, advisory): no runner evidence; "
                         "run a check or mark the claim unverified. Shadow row logged.\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)  # fail-open, always