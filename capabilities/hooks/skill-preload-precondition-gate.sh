#!/usr/bin/env bash
# outcome: agent-engineering:
# done_when: cmd:F=capabilities/hooks/fixtures/skill-preload-precondition-gate; o="$(/bin/bash capabilities/hooks/skill-preload-precondition-gate.sh <"$F/pack_compatible.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -qF '"verdict": "PREFILTER_CLEAR"'; g=$?; printf '%s' "$o" | grep -qF '"filtered_nothing": true'; h=$?; test $rc -eq 0 && test $g -eq 0 && test $h -eq 0 || cmd:F=capabilities/hooks/fixtures/skill-preload-precondition-gate; o="$(/bin/bash capabilities/hooks/skill-preload-precondition-gate.sh <"$F/pack_missing_applies_when.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -qF 'MISSING_PRECONDITION:slot.applies_when'; g=$?; test $rc -eq 2 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/skill-preload-precondition-gate; o="$(/bin/bash capabilities/hooks/skill-preload-precondition-gate.sh <"$F/pack_missing_state_field.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -qF 'MISSING_PRECONDITION:state.container_runtime'; g=$?; test $rc -eq 2 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/skill-preload-precondition-gate; o="$(/bin/bash capabilities/hooks/skill-preload-precondition-gate.sh <"$F/pack_missing_counterpart.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -qF 'MISSING_PRECONDITION:counterpart.rig-doctor'; g=$?; test $rc -eq 2 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/skill-preload-precondition-gate; T="${TMPDIR:-/tmp}/sppg-unsat-$$"; RIG_PRELOAD_STATE="$F/state_live.json" /bin/bash capabilities/hooks/skill-preload-precondition-gate.sh <"$F/pack_unsat_all.json" >"$T" 2>&1; rc=$?; grep -qF '"loadable": 0' "$T"; g=$?; grep -qF '"drop_count": 3' "$T"; h=$?; rm -f "$T"; test $rc -eq 3 && test $g -eq 0 && test $h -eq 0 || cmd:F=capabilities/hooks/fixtures/skill-preload-precondition-gate; o="$(/bin/bash capabilities/hooks/skill-preload-precondition-gate.sh <"$F/pack_band_empty.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -qF 'UNSATISFIABLE_PRECONDITION:version_band.python_version'; g=$?; test $rc -eq 3 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/skill-preload-precondition-gate; o="$(/bin/bash capabilities/hooks/skill-preload-precondition-gate.sh <"$F/pack_conflict_artifact_path.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -qF 'CONFLICT:artifact-path'; g=$?; test $rc -eq 4 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/skill-preload-precondition-gate; o="$(/bin/bash capabilities/hooks/skill-preload-precondition-gate.sh <"$F/pack_conflict_counterpart.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -qF 'CONFLICT:counterpart.rig-capabilities'; g=$?; test $rc -eq 4 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/skill-preload-precondition-gate; o="$(/bin/bash capabilities/hooks/skill-preload-precondition-gate.sh <"$F/pack_malformed.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -qF '"verdict": "GATE_MALFORMED"'; g=$?; test $rc -eq 1 && test $g -eq 0 || cmd:test -x capabilities/hooks/skill-preload-precondition-gate.sh || file:capabilities/hooks/skill-preload-precondition-gate.sh
# great_example: examples/great/agent-engineering/skill-preload-precondition-gate.md
# quality_floor: 0.6
# skill-preload-precondition-gate.sh — pre-load gate: no skill/harness body reaches context
# until its declared preconditions are EVALUATED against live state and every default it
# carries is checked against the task's binding requirements. Fails CLOSED and names the class.
#
# Mechanism (Towards a Systems Foundation for Agentic Skills, arXiv:2608.29596, video
# Kbxg-_CXs78; Agent Skills Can Be Harmful, arXiv:2608.11888, video TA5QzGTQU_U; WikiSkill,
# arXiv:2608.27454, video sHeITqLW2BY; Steering-Tool-Use-Propensity, arXiv:2608.25198, video
# C-Mk88De36M):
# a skill is a six-tuple <A activation, I instruction, C applicability, P permitted tools, pi
# control flow, E expected effects> and "a skill activates conditional based on the agent state
# x of t and the activation goal g" — alpha(s, x_t, g) == 1 is the ONLY thing that makes it
# loadable. The harmful-skills study supplies the second leg: "relevance is not compatibility
# of the system" and "we have to have skill task compatability checks" — before execution,
# enumerate the task's binding requirements (API surface, calculation, output format, file
# path, installed dependencies, runtime state, budget), check every default the skill carries
# against each one, return COMPATIBLE or CONFLICT-with-field, and block on CONFLICT. That study
# confirmed 307 skill-induced failures from skills ALREADY filtered for topical relevance
# (24 wrong-artifact-location, 13 environment-mismatch among them), so relevance ranking is
# not an admission test. WikiSkill (arXiv:2608.27454) says where the decision lives: "the frozen
# LLM receives the final accepted skills directly in its prompt from the harness" — admission is
# a HARNESS act, and its "records here of which skills were tried and their outcomes" is why this
# gate emits a named reasons list, not a bare refusal. C-Mk88De36M is the counter-example on the
# other side of the boundary: a model-level propensity knob (alpha on a residual-stream
# direction) can raise or suppress tool calls with no adjudication at all, which is exactly why
# the admission decision has to live in a deterministic harness gate beside guards like
# guard-dangerous-commands.sh.
#
# RIG gap this closes: capabilities_search / capabilities_context_pack / capabilities_route
# rank by BM25 + dense embedding + outcome-lane routing + graph expansion and evaluate ZERO
# preconditions at the moment of injection. `rig_capabilities/skill_contract.py` checks that a
# skill DECLARES `activation` + `applies_when` at authoring time (ABSENT/MALFORMED => not
# loadable) and `commands/rig-capabilities-register.md` documents the C slot — that is
# declaredness, never evaluation: nothing asks whether the predicate HOLDS against the live
# state, and nothing checks a skill's carried defaults against the task's binding requirements
# before its body reaches context. Relevance is still the pack surface's only admission signal.
# This gate is that missing prefilter, and it refuses with THREE classes that must not be
# collapsed into one "invalid" — collapsing them is the failure mode this row exists to kill:
#   MISSING_PRECONDITION        the asset cannot be adjudicated: a required slot is absent, no
#                               activation predicate is declared, a condition names a field no
#                               supplied state or task carries, a version band is unparseable,
#                               or a counterpart the asset depends on is not present at all.
#                               There is no basis to assert alpha == 1, so alpha != 1.
#   UNSATISFIABLE_PRECONDITION  the declaration is complete and evaluable and is FALSE: a
#                               condition does not hold against x_t/g, the asset's band is
#                               provably empty, or the live version violates it. The asset is
#                               sound; this state is simply not its state.
#   CONFLICT:<field>            applicable but INCOMPATIBLE with THIS task: a default the asset
#                               carries (artifact path, output format, calculation, budget,
#                               runtime) contradicts a binding requirement, or a present
#                               counterpart's version falls outside the asset's band. CONFLICT
#                               blocks; it is never downgraded to a warning.
# The three classes are also separated WITHIN the same target: a counterpart that is absent is
# MISSING, a counterpart present and outside the band is CONFLICT — same field, different
# remedy (supply the dependency vs. refuse the pairing).
#
# Contract (house shape: JSON on stdin, machine-readable refusal on stderr, exit = the class):
#   0  PREFILTER_CLEAR            every candidate cleared both checks — a prefilter verdict,
#                                 never PASS (the vocabulary is closed and asserted)
#   1  GATE_MALFORMED             the request is unparseable or outside the condition grammar
#   2  REFUSED/PREFILTER_DROPPED with MISSING_PRECONDITION
#   3  ... with UNSATISFIABLE_PRECONDITION
#   4  ... with CONFLICT
# stdout carries one machine-readable verdict object on every path that is not a crash:
#   {"schema":"rig.preload.verdict.v1","verdict":V,"evaluated":N,"loadable":n,
#    "loadable_ids":[...],"drop_count":D,"dropped":{class:count},"filtered_nothing":bool,
#    "never_pass":true,"reasons":[{"asset":id,"class":C,"code":"<CLASS>:<target>","detail":...}]}
# V is PREFILTER_CLEAR | NO_REQUEST | GATE_MALFORMED | REFUSED:<class> |
# PREFILTER_DROPPED:<class>. `drop_count` is always present and `filtered_nothing: true` makes
# a pack that filtered nothing visible in pack provenance — a prefilter that dropped zero
# assets must LOOK different from one that never ran.
#
# Request grammar (closed; anything outside it is GATE_MALFORMED exit 1, fail closed):
#   {"required_slots": [...],                the three slots this gate needs are never opt-out
#    "task":  {"id":T,"goal":G,"requirements":{F:REQ},"counterparts":[{"id","version"}]},
#    "state": {x_t...},                      or $RIG_PRELOAD_STATE (JSON file) = the harness seam
#    "candidates":[{"id","activation","applies_when":[COND...],"defaults":{F:V},
#                   "counterparts":[{"id","version_band"}]}]}
#   COND = {"field":NAME, "exists":true | "equals":V | "one_of":[...] |
#           "version_band":">=3.9,<4" | "matches":"<regex>"}      (exactly one operator)
#   NAME resolves task.<k> / state.<k> / self.<k>; a bare NAME tries state then task. An
#   unresolvable name is NEVER silently read as false — that is MISSING, not UNSATISFIABLE.
#   REQ  = scalar | [allowed...] | {"one_of":[...]} | {"max":n} | {"band":">=1,<2"}
#   Matching: both sides path-like -> the required path must be a PREFIX of the skill's default
#   (a skill that mandates dist/ cannot satisfy a task bound to build/); otherwise equality.
#
# Ceiling (stated, not smoothed): the gate evaluates what the request DECLARES as live state.
# $RIG_PRELOAD_STATE is the seam through which a harness supplies real state, but the gate
# cannot itself observe the repo, the container, or a skill body it was not given — a state
# document that lies will admit an asset this gate should drop. Band emptiness is detected by
# pairwise lower/upper contradiction plus pinned `==` consistency, not by solving; a band that
# is non-empty but has no installed satisfier is reported against the live version as
# UNSATISFIABLE, which is the same exit class by a different route. It complements
# skill_contract.py rather than duplicating it: that module proves an asset DECLARED C at
# authoring time; this gate proves C HOLDS here, now, for this task. Wiring this hook into a
# session-start / pre-injection point is a separate Gate-D action, and the always-loaded-token
# saving it protects (the study's 182 high-confidence efficiency regressions all came from
# skills a relevance filter had already admitted; 114 of them were excessive procedure) is only
# real once it is wired. Python via /usr/bin/python3 (precedent: guard-secret-write.sh,
# rail-registry-four-way-gate.sh), stdlib json/os/re/sys only, per house rule.
set -uo pipefail

payload="$(cat 2>/dev/null || true)"

# Embedded validator: loaded with `read -d ''` rather than `$(cat <<'PYEOF')` because bash's
# command-substitution scanner mis-tracks apostrophes inside a quoted heredoc body.
# `read -d ''` exits 1 at EOF by design; there is no `set -e` here, so that is not an error.
IFS= read -r -d '' PRELOAD_GATE_PY <<'PYEOF'
import json, os, re, sys

MISSING = "MISSING_PRECONDITION"
UNSAT = "UNSATISFIABLE_PRECONDITION"
CONFLICT = "CONFLICT"
CLASSES = (MISSING, UNSAT, CONFLICT)
CLASS_EXIT = {MISSING: 2, UNSAT: 3, CONFLICT: 4}
VERDICT_RE = re.compile(
    r"^(PREFILTER_CLEAR|NO_REQUEST|GATE_MALFORMED"
    r"|(REFUSED|PREFILTER_DROPPED):(MISSING_PRECONDITION"
    r"|UNSATISFIABLE_PRECONDITION|CONFLICT))$")
COND_KEYS = ("exists", "equals", "one_of", "version_band", "matches")
REQ_KEYS = ("one_of", "max", "band")
# The three slots this gate needs: A (activation), C (applies_when), and the defaults that
# make the asset compatibility-checkable. Declaring `required_slots` cannot drop them.
CORE_SLOTS = ("activation", "applies_when", "defaults")


def emit(req_id, verdict, evaluated, loadable_ids, reasons):
    """One machine-readable verdict object, closed vocabulary. PASS is unconstructible."""
    if not VERDICT_RE.match(verdict):
        verdict = "GATE_MALFORMED"
    dropped = {}
    for r in reasons:
        dropped[r["class"]] = dropped.get(r["class"], 0) + 1
    print(json.dumps({"schema": "rig.preload.verdict.v1", "request": req_id,
                      "verdict": verdict, "evaluated": evaluated,
                      "loadable": len(loadable_ids), "loadable_ids": loadable_ids,
                      "drop_count": len(reasons), "dropped": dropped,
                      "filtered_nothing": bool(evaluated) and not reasons,
                      "never_pass": True, "reasons": reasons}))
    return "GATE_MALFORMED" in verdict


def die(reason, detail):
    sys.stderr.write("PRELOAD-GATE: GATE_MALFORMED %s — %s\n" % (reason, detail))
    emit("", "GATE_MALFORMED", 0, [], [])
    sys.exit(1)


# -- version bands -----------------------------------------------------------------------
def vparse(raw):
    """'3.13.1' -> (3,13,1); 'v1.4' -> (1,4); None when no leading number exists."""
    s = re.sub(r"^[^0-9]*", "", str(raw if raw is not None else "").strip())
    if not s:
        return None
    parts = []
    for chunk in re.split(r"[._+-]", s):
        m = re.match(r"^\d+", chunk)
        if m is None:
            break
        parts.append(int(m.group(0)))
    return tuple(parts) if parts else None


def vcmp(a, b):
    n = max(len(a), len(b))
    a, b = a + (0,) * (n - len(a)), b + (0,) * (n - len(b))
    return (a > b) - (a < b)


def band_parse(spec):
    """'>=3.9,<4' -> [('>=',(3,9)),('<',(4,))]. None = unparseable (a missing declaration)."""
    if not isinstance(spec, str) or not spec.strip():
        return None
    clauses = []
    for raw in spec.split(","):
        m = re.match(r"^\s*(>=|<=|==|!=|>|<)\s*([^\s,]+)\s*$", raw)
        if not m:
            return None
        ver = vparse(m.group(2))
        if ver is None:
            return None
        clauses.append((m.group(1), ver))
    return clauses or None


def band_satisfies(version, clauses):
    v = vparse(version)
    if v is None:
        return False
    for op, want in clauses:
        c = vcmp(v, want)
        if not {">=": c >= 0, ">": c > 0, "<=": c <= 0,
                "<": c < 0, "==": c == 0, "!=": c != 0}[op]:
            return False
    return True


def band_is_empty(clauses):
    """Pairwise emptiness, not a solver: a lower bound that cannot coexist with an upper one,
    two contradictory pins, or a pin another clause rejects."""
    for op_lo, lo in clauses:
        if op_lo not in (">=", ">"):
            continue
        for op_hi, hi in clauses:
            if op_hi not in ("<=", "<"):
                continue
            c = vcmp(lo, hi)
            if c > 0 or (c == 0 and (op_lo == ">" or op_hi == "<")):
                return True
    pins = [v for op, v in clauses if op == "=="]
    for pin in pins:
        for op, want in clauses:
            if op == "==":
                if vcmp(pin, want) != 0:
                    return True
            elif not band_satisfies(pin, [(op, want)]):
                return True
    return False


# -- resolution --------------------------------------------------------------------------
def resolve(field, cand, task, state):
    """(found, value). task./state./self. are explicit namespaces; a bare name tries state,
    then task. Unresolvable is reported, never coerced to false."""
    for prefix, bag in (("task.", task), ("state.", state), ("self.", cand)):
        if field.startswith(prefix):
            cur = bag
            for part in field[len(prefix):].split("."):
                if not isinstance(cur, dict) or part not in cur:
                    return False, None
                cur = cur[part]
            return True, cur
    if field in state:
        return True, state[field]
    if field in task:
        return True, task[field]
    return False, None


def flat(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return ",".join(flat(v) for v in value)
    return str(value)


def path_under(default, required):
    def norm(p):
        return "/" + "/".join(x for x in p.strip().split("/") if x and x != ".") + "/"
    return norm(default).startswith(norm(required))


def requirement_holds(req, default):
    """(holds, kind). kind names the requirement form so the refusal says HOW it failed."""
    if isinstance(req, dict):
        stray = set(req) - set(REQ_KEYS)
        if stray:
            raise ValueError("unknown_requirement_form:" + ",".join(sorted(stray)))
        if "one_of" in req:
            return any(flat(default) == flat(v) for v in req["one_of"]), "one_of"
        if "max" in req:
            try:
                return float(flat(default)) <= float(req["max"]), "max"
            except ValueError:
                return False, "max"
        clauses = band_parse(req["band"])
        if clauses is None:
            raise ValueError("malformed_requirement_band")
        return band_satisfies(default, clauses), "band"
    if isinstance(req, list):
        return any(flat(default) == flat(v) for v in req), "allowed_list"
    d, r = flat(default), flat(req)
    if "/" in d or "/" in r:
        return path_under(d, r), "path-prefix"
    return d == r, "equals"


# -- the gate ----------------------------------------------------------------------------
def adjudicate(cand, task, state, slots, task_reqs, counterparts, die_):
    """Every finding for one candidate. Never raises: grammar faults exit(1) via die_."""
    cid = str(cand["id"])
    found = []

    # 1) Declaredness. No activation predicate => alpha cannot be evaluated => not loadable.
    for slot in slots:
        val = cand.get(slot)
        empty = val is None or val == "" or val == []
        if slot == "applies_when" and isinstance(val, list):
            empty = len(val) == 0          # an empty predicate set never yields alpha == 1
        if empty:
            found.append((MISSING, "slot." + slot,
                          "asset declares no %s — alpha(s,x,g) cannot be evaluated" % slot))

    # 2) Activation predicate alpha(s, x_t, g) against live state and the active goal.
    for idx, cond in enumerate(cand.get("applies_when") or []):
        if not isinstance(cond, dict) or "field" not in cond:
            die_("condition_not_an_object", "%s[%d]=%s" % (cid, idx, str(cond)[:60]))
        hits = [k for k in COND_KEYS if k in cond]
        if len(hits) != 1:
            die_("condition_grammar", "%s[%d] carries %d operators, expected exactly 1"
                 % (cid, idx, len(hits)))
        op = hits[0]
        field = str(cond["field"])
        ok, value = resolve(field, cand, task, state)
        if not ok:
            found.append((MISSING, field if "." in field else "state." + field,
                          "condition #%d names a field no supplied state or task carries"
                          % idx))
            continue
        label = field if field.startswith(("task.", "state.", "self.")) else "state." + field
        if op == "exists":
            if value in (None, "", False):
                found.append((UNSAT, label,
                              "condition #%d requires %s present and set" % (idx, field)))
        elif op == "equals":
            if flat(value) != flat(cond["equals"]):
                found.append((UNSAT, label, "condition #%d wants %s=%s, live %s=%s"
                              % (idx, field, flat(cond["equals"]), field, flat(value))))
        elif op == "one_of":
            if not isinstance(cond["one_of"], list):
                die_("one_of_not_a_list", "%s[%d]" % (cid, idx))
            allowed = [flat(v) for v in cond["one_of"]]
            if flat(value) not in allowed:
                found.append((UNSAT, label, "condition #%d: %s=%s is outside %s"
                              % (idx, field, flat(value), allowed)))
        elif op == "matches":
            try:
                hit = re.search(str(cond["matches"]), flat(value)) is not None
            except re.error as exc:
                die_("bad_regex", "%s[%d]: %s" % (cid, idx, exc))
            if not hit:
                found.append((UNSAT, label, "condition #%d: %s=%r does not match /%s/"
                              % (idx, field, flat(value), cond["matches"])))
        else:                                    # version_band over a live version
            clauses = band_parse(cond["version_band"])
            target = "version_band." + field
            if clauses is None:
                found.append((MISSING, target,
                              "condition #%d declares the unparseable band %r — nothing was "
                              "evaluated, so nothing was refuted" % (idx, cond["version_band"])))
            elif band_is_empty(clauses):
                found.append((UNSAT, target,
                              "condition #%d band %s is empty: no version can satisfy it"
                              % (idx, cond["version_band"])))
            elif not band_satisfies(value, clauses):
                found.append((UNSAT, target,
                              "live %s=%s violates the asset's band %s"
                              % (field, flat(value), cond["version_band"])))

    # 3) Compatibility: every default the asset carries vs this task's binding requirement.
    defaults = cand.get("defaults")
    if defaults is None:
        pass                                   # declaredness already reported it above
    elif not isinstance(defaults, dict):
        die_("defaults_not_an_object", "%s.defaults" % cid)
    else:
        for field in sorted(defaults):
            if field not in task_reqs:
                continue
            try:
                holds, kind = requirement_holds(task_reqs[field], defaults[field])
            except ValueError as exc:
                die_(str(exc), "field %s requirement %s default %s"
                     % (field, task_reqs[field], defaults[field]))
            if not holds:
                found.append((CONFLICT, field,
                              "the skill mandates %s, this task is bound to %s (%s)"
                              % (flat(defaults[field]), flat(task_reqs[field]), kind)))

    # 3b) Counterparts: absent is MISSING, present-and-outside-band is CONFLICT. Same target,
    # two different remedies — the distinction IS the asset of this gate.
    for cp in cand.get("counterparts") or []:
        if not isinstance(cp, dict) or "id" not in cp:
            die_("candidate_counterpart_missing_id", str(cp)[:80])
        cpid = str(cp["id"])
        if cpid not in counterparts:
            found.append((MISSING, "counterpart." + cpid,
                          "the asset needs %s and this run does not carry it" % cpid))
            continue
        if "version_band" not in cp:
            continue
        actual = counterparts[cpid].get("version")
        clauses = band_parse(cp["version_band"])
        if clauses is None:
            found.append((MISSING, "counterpart." + cpid,
                          "declares the unparseable band %r" % cp["version_band"]))
        elif band_is_empty(clauses):
            found.append((UNSAT, "counterpart." + cpid,
                          "declares the empty band %s" % cp["version_band"]))
        elif not band_satisfies(actual, clauses):
            found.append((CONFLICT, "counterpart." + cpid,
                          "%s is at %s, the asset requires %s"
                          % (cpid, flat(actual), cp["version_band"])))
    return cid, found


def main():
    raw = sys.stdin.read()
    if not raw.strip():
        sys.stderr.write("PRELOAD-GATE: nothing requested; nothing loaded.\n")
        emit("", "NO_REQUEST", 0, [], [])
        return 0
    try:
        req = json.loads(raw)
    except ValueError as exc:
        die("unparseable_payload", str(exc))
    if not isinstance(req, dict):
        die("payload_not_object", "expected a JSON object")
    task = req.get("task") or {}
    state = req.get("state")
    if state is None:
        path = os.environ.get("RIG_PRELOAD_STATE", "")
        if path and os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    state = json.load(fh)
            except ValueError as exc:
                die("state_file_unparseable", "%s: %s" % (path, exc))
        else:
            die("no_live_state", "request carries no `state` and $RIG_PRELOAD_STATE names none")
    if not isinstance(task, dict) or not isinstance(state, dict):
        die("task_or_state_not_object", "both must be JSON objects")
    cands = req.get("candidates")
    if not isinstance(cands, list) or not cands:
        die("no_candidates", "`candidates` must be a non-empty list")
    slots = req.get("required_slots", list(CORE_SLOTS))
    if not isinstance(slots, list) or not all(isinstance(s, str) for s in slots):
        die("required_slots_not_a_list_of_strings", type(slots).__name__)
    slots = list(dict.fromkeys(slots + list(CORE_SLOTS)))
    task_reqs = task.get("requirements") or {}
    if not isinstance(task_reqs, dict):
        die("requirements_not_object", "task.requirements must be an object")
    counterparts = {}
    for src in (task.get("counterparts") or [], state.get("counterparts") or []):
        if not isinstance(src, list):
            die("counterparts_not_a_list", "counterparts must be a list")
        for cp in src:
            if not isinstance(cp, dict) or "id" not in cp:
                die("counterpart_missing_id", str(cp)[:80])
            counterparts[str(cp["id"])] = cp
    req_id = str(task.get("id") or "preload")

    loadable_ids, reasons, order = [], [], {}
    for cand in cands:
        if not isinstance(cand, dict) or not cand.get("id"):
            die("candidate_missing_id", str(cand)[:80])
        cid, found = adjudicate(cand, task, state, slots, task_reqs, counterparts, die)
        order[cid] = len(order)
        if not found:
            loadable_ids.append(cid)
            continue
        cls = next(c for c in CLASSES if any(f[0] == c for f in found))
        for f in found:
            if f[0] == cls:
                reasons.append({"asset": cid, "class": cls,
                                "code": "%s:%s" % (cls, f[1]), "detail": f[2]})

    reasons.sort(key=lambda r: (CLASSES.index(r["class"]), order.get(r["asset"], 0), r["code"]))
    if not reasons:
        verdict, code = "PREFILTER_CLEAR", 0
    else:
        # The FIRST refusal in candidate order names the exit class, so a partially-loadable
        # pack still reports non-zero and the class is never lost.
        head = min(reasons, key=lambda r: (order.get(r["asset"], 0), CLASSES.index(r["class"])))
        verdict = ("REFUSED" if not loadable_ids else "PREFILTER_DROPPED") + ":" + head["class"]
        code = CLASS_EXIT[head["class"]]

    malformed = emit(req_id, verdict, len(cands), loadable_ids, reasons)
    if malformed:
        return 1
    for r in reasons:
        sys.stderr.write("PRELOAD-GATE: %s %s — %s\n" % (r["code"], r["asset"], r["detail"]))
    sys.stderr.write("PRELOAD-GATE: %s — %d of %d asset(s) refused pre-load; this is a "
                     "prefilter verdict, never PASS\n" % (verdict, len(reasons), len(cands)))
    return code


sys.exit(main())
PYEOF
printf '%s' "$payload" | /usr/bin/python3 -c "$PRELOAD_GATE_PY"
exit $?
