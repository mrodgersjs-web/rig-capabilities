#!/bin/bash
# V9-r2: run 4 frontier research strands sequentially, capture stdout,
# extract a deliverable .md per strand from the final answer.
set -u
REPO="$HOME/Developer/rig-capabilities"
LOGD="$REPO/.context/frontier"
OUTD="$REPO/intel/frontier"
mkdir -p "$LOGD" "$OUTD"
DAY=2026-08-31

run_strand() {
  local slug="$1" prompt="$2"
  local log="$LOGD/$slug.log"
  echo "[frontier] $slug start $(date +%H:%M:%S)" >> "$LOGD/progress.log"
  frontier --mode react --cwd "$REPO" --no-tui -y -p "$prompt" > "$log" 2>&1
  echo "[frontier] $slug exit $? $(date +%H:%M:%S)" >> "$LOGD/progress.log"
  python3 - "$log" "$OUTD/$DAY-$slug.md" "$slug" <<'PY'
import re, sys, pathlib
log, out, slug = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3]
if out.exists() and len(out.read_text()) > 2000:
    sys.exit(0)
t = pathlib.Path(log).read_text(errors="ignore")
# take the last markdown heading to end of stream = final answer body
starts = [m.start() for m in re.finditer(r"(?m)^#{1,2} \S", t)]
body = t[starts[-1]:] if starts else ""
if len(body) < 1200:  # fall back: whole tail
    body = t[-12000:]
fm = (f"---\nname: frontier-{slug}\n"
      "description: Frontier react research strand — " + slug.replace('-', ' ') + "\n"
      "source: frontier\noutcome: research-intel: " + slug.replace('-', ' ') + "\n"
      "verified_on: 2026-08-31\nquality_floor: 0.6\n---\n\n")
out.write_text(fm + body.strip() + "\n")
print("wrote", out, len(body))
PY
}

run_strand skill-organization "You are doing deep web research. Topic: how to organize large libraries of agent skills in 2026 — the Anthropic agent-skills SKILL.md format, progressive disclosure (metadata -> instructions -> resources), folder layouts, naming, and discovery indexes for libraries of 1000+ skills. Use web_search and web_fetch on primary sources (anthropic docs/skills repo, agentskills spec, OpenAI/Google equivalent guidance, notable OSS skill collections). Your FINAL ANSWER must be the complete deliverable: a markdown report titled '## Skill organization — deep research' with sections: Formats and frontmatter contracts; Progressive disclosure mechanics; Folder/naming conventions at scale; Discovery index patterns; and a final Sources section listing every URL you actually used with a one-line note. Write it ALL into the final answer text; do not rely on file writes."

run_strand skill-routing "You are doing deep web research. Topic: skill routing and ranking architectures for coding agents in 2026 — how agents pick the right skill out of large libraries: metadata BM25 vs dense embedding retrieval, hybrid fusion (RRF), knowledge-graph expansion, intent routing, MCP resource discovery, and context-budget-aware selection. Use web_search and web_fetch on primary sources (Anthropic skills docs, MCP spec, vector/hybrid retrieval engineering posts, Voyager and similar literature). Your FINAL ANSWER must be the complete deliverable: a markdown report titled '## Skill routing — deep research' with sections: Routing pipelines observed in shipped systems; Retrieval tiers and fusion; Graph and metadata signals; Budget-aware selection; Anti-patterns; and Sources with URLs."

run_strand self-improvement-loops "You are doing deep web research. Topic: self-improvement loops for AI agents and skill libraries, 2024-2026: Voyager's skill library growth, Reflexion, ADAS/meta-agent searches, Gödel machines, data flywheels, and practical '1000x round' style quality engines — what has actually been shipped vs paper-only, and what gate discipline (done-tests, graduation, rejection) successful systems use. Use web_search and web_fetch on primary sources (arXiv papers, official blog posts, repos). Your FINAL ANSWER must be the complete deliverable: a markdown report titled '## Self-improvement loops — deep research' with sections: Shipped vs paper-only; Loop architectures; Gate and graduation discipline; Failure modes; Applicability to a skill store with runnable done-tests; and Sources with URLs."

run_strand skill-evaluation "You are doing deep web research. Topic: how agent skills and prompts are evaluated in 2026 — done-tests / executable acceptance criteria, rubric scoring, LLM-as-judge with calibration, plant-failure/adversarial verification (making gates prove they can fail), benchmark suites for MCP/skill servers, and eval-driven skill iteration. Use web_search and web_fetch on primary sources (Anthropic/OpenAI eval docs, promptfoo/Braintrust/RAGAS docs, papers on LLM-as-judge validity). Your FINAL ANSWER must be the complete deliverable: a markdown report titled '## Skill evaluation — deep research' with sections: Done-test patterns; Rubric + judge calibration; Plant-failure verification; MCP/skill benchmarking; Eval-driven iteration; and Sources with URLs."

echo "[frontier] all strands done $(date +%H:%M:%S)" >> "$LOGD/progress.log"
