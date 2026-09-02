#!/usr/bin/env bash
# outcome: agent-engineering: the run sides with the task, names the rule, and never executes the winning skill's forbidden step silently
# done_when: cmd:F=capabilities/hooks/fixtures/task-authority; o="$(/bin/bash capabilities/hooks/task-authority-over-skill-authority.sh "$F/assembly_task_wins.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -qF '"verdict": "CLEAN"'; g=$?; test $rc -eq 0 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/task-authority; o="$(/bin/bash capabilities/hooks/task-authority-over-skill-authority.sh "$F/assembly_harness_wins.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -qF '"conflicts_detected": 1'; g=$?; test $rc -eq 0 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/task-authority; o="$(/bin/bash capabilities/hooks/task-authority-over-skill-authority.sh "$F/assembly_no_conflict.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -qF '"conflicts_detected": 0'; g=$?; test $rc -eq 0 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/task-authority; o="$(/bin/bash capabilities/hooks/task-authority-over-skill-authority.sh "$F/assembly_escalate.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -qF '"precedence_logged": true'; g=$?; test $rc -eq 0 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/task-authority; o="$(/bin/bash capabilities/hooks/task-authority-over-skill-authority.sh "$F/assembly_skill_wins.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -qF 'AUTHORITY_INVERSION'; g=$?; test $rc -eq 2 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/task-authority; o="$(/bin/bash capabilities/hooks/task-authority-over-skill-authority.sh "$F/assembly_conflict_undetected.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -qF 'CONFLICT_UNDETECTED'; g=$?; test $rc -eq 2 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/task-authority; o="$(/bin/bash capabilities/hooks/task-authority-over-skill-authority.sh "$F/assembly_rule_uncited.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -qF 'RULE_UNCITED'; g=$?; test $rc -eq 2 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/task-authority; o="$(/bin/bash capabilities/hooks/task-authority-over-skill-authority.sh "$F/assembly_executed_losing_step.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -qF 'EXECUTED_LOSING_STEP'; g=$?; test $rc -eq 2 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/task-authority; o="$(/bin/bash capabilities/hooks/task-authority-over-skill-authority.sh "$F/assembly_phantom_record.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -qF 'RESOLUTION_PHANTOM'; g=$?; test $rc -eq 2 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/task-authority; o="$(/bin/bash capabilities/hooks/task-authority-over-skill-authority.sh "$F/assembly_malformed_authority.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -qF 'RECORD_MALFORMED'; g=$?; test $rc -eq 2 && test $g -eq 0 || file:capabilities/hooks/task-authority/check_task_authority.py
# great_example: examples/great/agent-engineering/task-authority-over-skill-authority.md
# quality_floor: 0.6
# task-authority-over-skill-authority — assembly-time precedence gate: when a loaded
# skill body contradicts a higher-authority directive, the harness escalates or follows
# the task/harness layer — never the skill — and logs the precedence it applied.
#
# Mechanism (Agent Skills Can Be Harmful, arXiv:2608.11888, video TA5QzGTQU_U):
# a loaded skill is a token-by-token instruction stream that overrides the model's own
# parametric knowledge, so an unranked instruction set is not a neutral context — it is a
# competing authority that wins by mere presence and leaves no trace. The precedence is
# fixed and must be applied IN CODE AT ASSEMBLY TIME: task > harness > skill. A skill may
# not override the task the operator bound, nor another harness component (a guard, a
# gate), nor the files it lives beside. Contradiction is arithmetic, not vibes: two
# directives contradict when they bind the same `subject` and their `require` value-sets
# are DISJOINT — no world satisfies both. On a conflict the run has exactly two lawful
# moves: side with the HIGHER-authority directive, or escalate (hold both steps for the
# operator). Three states are violations on their own: siding with the skill
# (AUTHORITY_INVERSION), not noticing the conflict at all (CONFLICT_UNDETECTED — the
# commonest failure, because compliance is silent), and resolving with no named rule
# (RULE_UNCITED — an unlogged precedence is how one lucky skill becomes tomorrow's
# default). Deepest of all: the resolution papers over and the run executes the losing
# skill step anyway (EXECUTED_LOSING_STEP) — the source's own seed: the skill body says
# "skip the test suite before shipping" while the task requires tests green; if the suite
# stays skipped, silent compliance wore a resolution.
#
# RIG gap this closes: no precedence policy exists anywhere in the estate.
# guard-dangerous-commands.sh / guard-secret-write.sh / tac-plan-gate.sh gate TOOL CALLS,
# not instruction sources; skill-preload-precondition-gate.sh decides whether a skill body
# may LOAD, and once loaded its directives compete unranked with the task;
# mh-03-agent-composition-session.yaml only requires a prose "precedence note" when two
# bound skills' TRIGGERS overlap — an authoring-time convention between peers, never a
# runtime adjudication across layers. The instruction layer has no guard.
#
# Contract: one assembly record — argv path, or piped on stdin (spilled to a temp file by
# this hook; the checker itself reads only argv and writes nothing). Record grammar
# (closed; outside it is RECORD_MALFORMED, fail-closed):
#   {"schema":"rig.authority.assembly.v1",
#    "sources":[{"id","authority":"task"|"harness"|"skill",
#                "directives":[{"id","text","subject","require":scalar|[allowed...]}]}],
#    "resolution":{"conflicts":[{"pair":[dirA,dirB],"decision":
#                  "task"|"harness"|"skill"|"escalate","precedence_rule":str}],
#                  "executed":[directive ids actually carried out]}}
# Exit codes: 0 CLEAN (every detected conflict rule-cited, sided higher-or-escalated, no
# losing step executed); 1 usage / record-not-found (refusal to judge, never a verdict);
# 2 violation. stdout carries
#   {"schema":"rig.authority.verdict.v1","verdict":V,"conflicts_detected":N,
#    "precedence_logged":bool,"violations":[{"class","detail"}]}
# on every judged path; V is CLEAN | AUTHORITY_VIOLATION | RECORD_MALFORMED.
#
# Ceiling (stated, not smoothed): the gate adjudicates the record the harness ASSEMBLED —
# it sees the directives as declared, not the raw skill bodies or the operator's intent,
# so an assembly that strips or mutates a directive before writing the record defeats it;
# same-rank conflicts (skill vs skill) are out of scope — this gate encodes only
# task > harness > skill; "executed" is what the record DECLARES the run carried out.
# Wiring into a session-start / pre-injection seam is a separate Gate-D action. Python
# via /usr/bin/python3 (precedent: guard-secret-write.sh), stdlib json/sys/pathlib only.
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
checker="$here/task-authority/check_task_authority.py"

if [ "$#" -ge 1 ]; then
  /usr/bin/python3 "$checker" "$@"
  exit $?
fi

[ -t 0 ] || {
  payload="$(cat 2>/dev/null || true)"
  if [ -n "$payload" ]; then
    tmp="$(mktemp "${TMPDIR:-/tmp}/task-authority.XXXXXX")" || exit 1
    trap 'rm -f "$tmp"' EXIT
    printf '%s' "$payload" >"$tmp"
    /usr/bin/python3 "$checker" "$tmp"
    exit $?
  fi
}
echo "task-authority: usage — pass an assembly-record path or pipe the record on stdin" >&2
exit 1
