// rig-loop hooks — pi extension for OMP and Prime Agent.        RIG_LOOP_MANAGED
// outcome: agent-engineering:
// done_when: cmd:python3 scripts/hook_fires.py rig-loop-hooks.ts
// great_example: examples/great/agent-engineering/iqrsqpi-v11.md
// quality_floor: 0.7
//
// Bridges pi lifecycle events to the rig-loop engine (Loop-Skill Contract v11):
//   session_start       -> rig-loop hook session-start   (resume banner)
//   before_agent_start  -> rig-loop hook prompt          (stage banner injected as a message)
//   tool_call           -> rig-loop hook pre-tool        ({block:true} when the stage forbids the write / outward action)
//   agent_end           -> rig-loop hook stop            (cannot block in pi; surfaces NOT-DONE as a warning)
// With no active loop run every call is a silent no-op. Installed by `rig-loop wire --apply`.
import { spawnSync } from "node:child_process";
import { homedir } from "node:os";

const RIG_LOOP = process.env.RIG_LOOP_CLI || `${homedir()}/Developer/rig-capabilities/bin/rig-loop`;

type HookResult = { block?: boolean; reason?: string; inject?: string; error?: string };

function callHook(event: string, payload: Record<string, unknown>): HookResult {
  try {
    const r = spawnSync("python3", [RIG_LOOP, "hook", event, "--format", "pi"], {
      input: JSON.stringify(payload),
      encoding: "utf8",
      timeout: 15000,
    });
    if (!r.stdout) return {};
    return JSON.parse(r.stdout.trim().split("\n").pop() || "{}") as HookResult;
  } catch {
    return {};
  }
}

function cwdOf(ctx: any): string {
  try {
    return (ctx && ctx.cwd) || process.cwd();
  } catch {
    return process.cwd();
  }
}

export default function (pi: any): void {
  pi.on("session_start", (event: any, ctx: any) => {
    const r = callHook("session-start", { cwd: cwdOf(ctx), reason: event?.reason ?? "", harness: "pi" });
    if (r.inject && ctx?.ui?.notify) ctx.ui.notify(r.inject, "info");
  });

  pi.on("before_agent_start", (event: any, ctx: any) => {
    const r = callHook("prompt", { cwd: cwdOf(ctx), prompt: event?.prompt ?? "", harness: "pi" });
    if (r.inject) {
      return { message: { customType: "rig-loop", content: r.inject, display: true } };
    }
    return undefined;
  });

  pi.on("tool_call", (event: any, ctx: any) => {
    const r = callHook("pre-tool", {
      cwd: cwdOf(ctx),
      tool_name: event?.toolName ?? "",
      tool_input: event?.input ?? {},
      tool_use_id: event?.toolCallId ?? "",
      harness: "pi",
    });
    if (r.block) return { block: true, reason: r.reason || "blocked by rig-loop" };
    return undefined;
  });

  pi.on("agent_end", (_event: any, ctx: any) => {
    const r = callHook("stop", { cwd: cwdOf(ctx), harness: "pi" });
    const msg = r.reason || r.inject;
    if (msg && ctx?.ui?.notify) ctx.ui.notify(msg, r.block ? "warning" : "info");
  });
}
