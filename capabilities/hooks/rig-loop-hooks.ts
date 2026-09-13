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
// D85 advises at session start; ordinary tools are not D85-admitted.
import { spawnSync } from "node:child_process";
import { homedir } from "node:os";

const RIG_LOOP = process.env.RIG_LOOP_CLI || `${homedir()}/Developer/rig-capabilities/bin/rig-loop`;

type HookResult = { block?: boolean; reason?: string; inject?: string; error?: string };

// Fail-closed, matching rig_capabilities/loops.py dispatch_hook: when the D85
// engine cannot answer (missing CLI, spawn error, timeout, unparseable output),
// MUTATION-class tool calls are denied and read-only tools pass with a stderr
// warning. Tool-NAME classification only — command-level scanning stays in the
// Python engine (documented ceiling, same as the shell layer).
const MUTATION_TOOLS = new Set([
  "write", "edit", "multiedit", "multi_edit", "notebookedit", "notebook_edit",
  "apply_patch", "applypatch", "str_replace_editor", "create_file",
  "bash", "shell", "run_command", "exec", "terminal", "execute_command",
  "eval", "python", "python_repl", "execute_code", "run_code", "code_interpreter",
]);

function callHook(event: string, payload: Record<string, unknown>): HookResult {
  let r: ReturnType<typeof spawnSync> | null = null;
  let failure = "";
  try {
    r = spawnSync("python3", [RIG_LOOP, "hook", event, "--format", "pi"], {
      input: JSON.stringify(payload),
      encoding: "utf8",
      timeout: 15000,
    });
    if (r.error) failure = `engine unreachable: ${r.error.message}`;
    else if (r.status !== 0) failure = `engine exited ${r.status} signal=${r.signal}`;
    else {
      try {
        const result: unknown = JSON.parse(r.stdout.trim());
        if (
          !result || typeof result !== "object" || Array.isArray(result) ||
          !("block" in result) || typeof result.block !== "boolean" ||
          ["reason", "inject", "error"].some(
            key => key in result && typeof (result as Record<string, unknown>)[key] !== "string",
          ) ||
          ("error" in result && result.error)
        ) {
          failure = "engine response missing or invalid verdict";
        } else {
          return result as HookResult;
        }
      } catch {
        failure = "engine output unparseable";
      }
    }
  } catch (e: any) {
    failure = `engine unavailable: ${e?.message ?? String(e)}`;
  }
  const tool = String(payload.tool_name || "").trim().toLowerCase().replaceAll("-", "_");
  const mutation = event === "pre-tool" && (!tool || MUTATION_TOOLS.has(tool));
  if (mutation) {
    return {
      block: true,
      reason:
        `[d85] gate engine unavailable (${failure}) — mutation-class tool denied, fail closed. ` +
        `Repair ${RIG_LOOP} / rig_capabilities/d85_admission.py in an explicitly authorized break-glass session.`,
    };
  }
  process.stderr.write(`[d85] gate engine unavailable (${failure}) — read-only tool allowed\n`);
  return {};
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
