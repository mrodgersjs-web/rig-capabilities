import register from "../capabilities/hooks/rig-loop-hooks.ts";

type Handler = (event: unknown, ctx: unknown) => unknown;

const cwd = process.argv[2];
if (!cwd) throw new Error("usage: rig_loop_hooks_fixture.ts <cwd>");

const handlers: Record<string, Handler> = {};
register({
  on(event: string, handler: Handler) {
    handlers[event] = handler;
  },
});

const toolCall = handlers.tool_call;
if (!toolCall) throw new Error("tool_call handler was not registered");

const denied = toolCall(
  { toolName: "Write", input: { file_path: `${cwd}/src/x.ts` }, toolCallId: "deny-fixture" },
  { cwd },
);
if (
  !denied ||
  typeof denied !== "object" ||
  !("block" in denied) ||
  denied.block !== true ||
  !("reason" in denied) ||
  typeof denied.reason !== "string" ||
  !denied.reason.includes("WRITE BLOCKED")
) {
  throw new Error(`forbidden write was not blocked: ${JSON.stringify(denied)}`);
}

const allowed = toolCall(
  { toolName: "Read", input: { file_path: `${cwd}/src/x.ts` }, toolCallId: "allow-fixture" },
  { cwd },
);
if (allowed !== undefined) {
  throw new Error(`permissible read was not allowed: ${JSON.stringify(allowed)}`);
}

console.log("deny=block allow=undefined");
