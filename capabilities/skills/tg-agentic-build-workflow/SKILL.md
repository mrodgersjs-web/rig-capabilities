---
name: tg-agentic-build-workflow
description: >
  Sub-skill of tubeguruji-doctrine: how the TubeGuruji corpus builds apps WITH
  coding agents (2025-26 lane) — plan-first prompting, review-the-plan gates,
  paste-error-to-fix loops, agent-generated landing pages, CodeRabbit PR review,
  and the agent platforms used (Cursor, Codex, Factory.ai, Google Antigravity,
  Claude Code, Replit Agent 4, Traycer, Jolli AI).
tags: [rig, doctrine, agentic-coding, codex, claude-code, tubeguruji]
metadata:
  source: "corpus — kxM_oEMn3IM (Codex plan mode), iVVG9wOXEqQ (Traycer plan→prompts), 5VK8rc3GXdc (Replit Agent 4 lifecycle), ciXiibK7Gds (Factory.ai whole-app build), WmWJNSxCiZc (Claude Code + Jolli AI + CodeRabbit), O_f55bWzsik (agent plan acceptance), rcEUVADmH2g + ruIK7LFBjHI (mid-build agent prompting), 31-Qfr2Pc5Q (review plan before proceed), ERHqeU9zzp8 (Cursor-built trip planner)"
  extracted: "2026-09-25"
  parent: tubeguruji-doctrine
  subs: [tg-agent-prompt-craft]
outcome: "An app feature built by a coding agent through a review-gated loop (plan reviewed → implemented → errors pasted back → verified), with agent-generated surfaces integrated rather than re-written."
activation: "Load when a coding agent is doing implementation work on a skeleton build, when setting up the agent workflow for a project, or when an agent build keeps thrashing."
instruction: >
  Run agents in plan mode by default; review the plan before implementation is a
  hard gate, not a suggestion. Feed failures back to the SAME session as pasted
  errors instead of restarting. Let agents generate boilerplate surfaces (landing
  pages) and review diffs automatically (CodeRabbit pattern), but keep skeleton
  and quota decisions human.
applies_when:
  env: "repo with a coding agent wired (Claude Code, Codex, Cursor, Factory.ai, Antigravity, Replit)"
  runtime: "agent CLI/IDE + dev server"
  deps: "optional: Jolli AI (persistent project memory), CodeRabbit (PR review), Arcjet/docs prompts as agent inputs"
  params: "plan mode on; one feature per task; error paste-backs in context"
  budget: "agent time is cheap; human review minutes are the scarce budget"
  scale: "single app, single agent primary"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
flow:
  - Brief the agent with the skeleton stage and named vendors (state which model/service to use in the prompt, kxM_oEMn3IM).
  - Run plan mode so the agent asks questions before writing code (kxM_oEMn3IM Codex "plan mode"; Traycer plans then emits implementation prompts, iVVG9wOXEqQ).
  - REVIEW the plan before proceeding — corpus rule verbatim: "make sure to review the task and implementation plan before proceed further" (31-Qfr2Pc5Q); accept plans only when they match intent ("proposed changes… feel good to me", O_f55bWzsik).
  - Implement one feature per task; let the agent generate whole surfaces where they are boilerplate (landing pages AI-generated in -h1O73T0jmo, 31-Qfr2Pc5Q, 5VK8rc3GXdc, iVVG9wOXEqQ).
  - On failure, paste the runtime error into a new task for the SAME agent ("just inform to the AI model to fix this issue", 5VK8rc3GXdc; Replit parallel agents with paste-error-to-fix).
  - Review diffs after each feature; auto-review via CodeRabbit is the corpus pattern (WmWJNSxCiZc, YbUJpaOlUbk, BamV5jDeJeU).
  - Keep persistent project context across tasks (Jolli AI memory, WmWJNSxCiZc) or an equivalent local memory file.
done_when:
  - "grep:capabilities/skills/tg-agentic-build-workflow/SKILL.md:plan mode"
  - "grep:capabilities/skills/tg-agentic-build-workflow/SKILL.md:CodeRabbit"
  - "grep:data/corpora/how-to/manifest.jsonl:kxM_oEMn3IM"
out_of_scope:
  - multi-agent fleet orchestration (RIG fleet doctrine covers that)
  - letting the agent choose quota/monetization/production deploy decisions
  - pushes and deploys (Gate-D, always human)
quality_floor: "An agent feature shipped without a reviewed plan or without the error-fix loop exercised is RED; 'the agent said it works' is not verification."
---

# Agentic Build Workflow

## The corpus shifted from teaching code to teaching agent operation

2022-24 videos are hand-typed builds. From 2025 the builds themselves are
agent-driven, and the teaching point becomes the loop: how you brief, review,
correct, and accept agent work. The instructor dictates prompts mid-video to add a
caption-edit dialog (rcEUVADmH2g), narrates Codex fixing a focus-border bug and
broken formatting (ruIK7LFBjHI), and records the model suggesting file organization
(sXRDL-EPtrM).

## The loop (five moves)

1. **Brief with named vendors.** Say which model/service to use in the prompt
   (kxM_oEMn3IM) — the agent should not be choosing your stack.
2. **Plan first.** Codex "plan mode" so it asks before implementing (kxM_oEMn3IM);
   or a planner agent that emits implementation prompts (Traycer, iVVG9wOXEqQ).
3. **Review the plan — hard gate.** "Make sure to review the task and
   implementation plan before proceed further" (31-Qfr2Pc5Q). Accept only when the
   plan matches intent (O_f55bWzsik).
4. **Paste errors back; don't restart.** Runtime error → new task for the same
   agent with the error pasted (5VK8rc3GXdc). Replit Agent 4's whole UX is built on
   this: task list draft → plan → active, parallel agents, live preview while fixes
   run, publish gated by a security scan (5VK8rc3GXdc).
5. **Auto-review diffs.** CodeRabbit reviews the PR after each feature
   (WmWJNSxCiZc — the corpus' truest agentic workflow: Claude Code + Jolli AI
   persistent memory + CodeRabbit; also YbUJpaOlUbk, BamV5jDeJeU).

## Platform notes (as used, not as benchmarks)

| Platform | Corpus use |
|---|---|
| Codex | plan-mode feature work (kxM_oEMn3IM, ruIK7LFBjHI) |
| Cursor | whole-app builds (ERHqeU9zzp8 trip planner, YbUJpaOlUbk job-application SaaS) |
| Factory.ai | entire app "without writing any code" (ciXiibK7Gds) |
| Google Antigravity (CLI) | app scaffolds + task plans to review (31-Qfr2Pc5Q, 2yd4grkXyUU) |
| Claude Code | theme-builder build with Jolli AI + CodeRabbit (WmWJNSxCiZc) |
| Replit Agent 4 | plan/design/implement/publish in one platform (5VK8rc3GXdc) |
| Traycer AI | plan → implementation prompts for another agent (iVVG9wOXEqQ) |
| Jolli AI | persistent memory/project context for the coding agent (WmWJNSxCiZc) |
| Eraser agent skill | repo analysis → diagrams/docs via API token (jphLnnxM-z4) |
| WhatsApp MCP | agent surface pairing via phone-number + code (2yd4grkXyUU) |

## What stays human

The corpus keeps humans on: plan acceptance, quota numbers, monetization, and the
publish button (Replit's publish runs a security scan; the human still clicks it).
RIG adds hard law: pushes, deploys, purchases, and publishes stop at Gate-D
regardless of what the agent can do.
