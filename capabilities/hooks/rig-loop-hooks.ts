// rig-loop hooks — pi extension for OMP and Prime Agent.        RIG_LOOP_MANAGED
// outcome: agent-engineering:
// done_when: cmd:python3 scripts/hook_fires.py rig-loop-hooks.ts
// great_example: examples/great/agent-engineering/iqrsqpi-v11.md
// quality_floor: 0.7
//
// Bridges pi lifecycle events to the rig-loop engine (Loop-Skill Contract v11):
//   session_start       -> rig-loop hook session-start   (resume banner)
//   before_agent_start  -> rig-loop hook prompt          (stage banner injected as a message)
//   tool_call           -> rig-loop hook pre-tool        ({block:true} only when an ACTIVE loop stage forbids the write / outward action)
//   agent_end           -> rig-loop hook stop            (cannot block in pi; surfaces NOT-DONE as a warning)
// D85 is a build-certification gate (checklist / verify-cert / d85_certified at seal), not a
// pre-tool admission. It is surfaced by the D85 advisor (~/.omp/agent/WATCHDOG.yml), which
// reviews and fixes but never denies. An unreachable engine therefore WARNS and allows —
// operations are never fail-closed on hook plumbing. Installed by `rig-loop wire --apply`.
import { spawnSync } from "node:child_process";
import { homedir } from "node:os";

const RIG_LOOP = process.env.RIG_LOOP_CLI || `${homedir()}/Developer/rig-capabilities/bin/rig-loop`;

interface HookResult {
  block?: boolean;
  reason?: string;
  inject?: string;
  error?: string;
}

interface HookContext {
  cwd?: string;
  ui?: { notify?: (message: string, level: "info" | "warning") => void };
}

interface HookEventBus {
  on(event: "session_start", handler: (event: { reason?: string }, ctx: HookContext) => void): void;
  on(
    event: "before_agent_start",
    handler: (event: { prompt?: string }, ctx: HookContext) => { message: { customType: string; content: string; display: boolean } } | undefined,
  ): void;
  on(
    event: "tool_call",
    handler: (event: { toolName?: string; input?: unknown; toolCallId?: string }, ctx: HookContext) => { block: true; reason: string } | undefined,
  ): void;
  on(event: "agent_end", handler: (event: unknown, ctx: HookContext) => void): void;
}

function isHookResult(value: unknown): value is HookResult {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  if (!("block" in value) || typeof value.block !== "boolean") return false;
  for (const key of ["reason", "inject", "error"] as const) {
    if (key in value && typeof (value as Record<string, unknown>)[key] !== "string") return false;
  }
  return !("error" in value && value.error);
}

function callHook(event: string, payload: Record<string, unknown>): HookResult {
  let failure = "";
  try {
    const r = spawnSync("python3", [RIG_LOOP, "hook", event, "--format", "pi"], {
      input: JSON.stringify(payload),
      encoding: "utf8",
      timeout: 15000,
    });
    if (r.error) failure = `engine unreachable: ${r.error.message}`;
    else if (r.status !== 0) failure = `engine exited ${r.status} signal=${r.signal}`;
    else {
      try {
        const result: unknown = JSON.parse(r.stdout.trim());
        if (isHookResult(result)) return result;
        failure = "engine response missing or invalid verdict";
      } catch {
        failure = "engine output unparseable";
      }
    }
  } catch (e: unknown) {
    failure = `engine unavailable: ${e instanceof Error ? e.message : String(e)}`;
  }
  process.stderr.write(`[rig-loop] hook engine unavailable (${failure}) — ${event} allowed (advisory only)\n`);
  return {};
}

export default function (pi: HookEventBus): void {
  pi.on("session_start", (event, ctx) => {
    const r = callHook("session-start", { cwd: ctx.cwd || process.cwd(), reason: event?.reason ?? "", harness: "pi" });
    if (r.inject && ctx.ui?.notify) ctx.ui.notify(r.inject, "info");
  });

  pi.on("before_agent_start", (event, ctx) => {
    const r = callHook("prompt", { cwd: ctx.cwd || process.cwd(), prompt: event?.prompt ?? "", harness: "pi" });
    if (r.inject) {
      return { message: { customType: "rig-loop", content: r.inject, display: true } };
    }
    return undefined;
  });

  pi.on("tool_call", (event, ctx) => {
    const r = callHook("pre-tool", {
      cwd: ctx.cwd || process.cwd(),
      tool_name: event?.toolName ?? "",
      tool_input: event?.input ?? {},
      tool_use_id: event?.toolCallId ?? "",
      harness: "pi",
    });
    if (r.block) return { block: true, reason: r.reason || "blocked by rig-loop" };
    return undefined;
  });

  pi.on("agent_end", (_event, ctx) => {
    const r = callHook("stop", { cwd: ctx.cwd || process.cwd(), harness: "pi" });
    const msg = r.reason || r.inject;
    if (msg && ctx.ui?.notify) ctx.ui.notify(msg, r.block ? "warning" : "info");
  });
}
