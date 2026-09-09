import { afterAll, expect, test } from "bun:test";
import { mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const temp = mkdtempSync(join(tmpdir(), "d85-extension-"));
const cli = join(temp, "engine.py");
const previous = process.env.RIG_LOOP_CLI;
process.env.RIG_LOOP_CLI = cli;
// The extension binds its CLI at module load, after the isolated fixture path is set.
const { default: register } = await import("./rig-loop-hooks.ts");
if (previous === undefined) delete process.env.RIG_LOOP_CLI;
else process.env.RIG_LOOP_CLI = previous;

type Handler = (event: { toolName: string; input: { path: string } }, ctx: { cwd: string }) => { block: boolean; reason: string } | undefined;
const handlers: Record<string, Handler> = {};
register({ on(name: string, handler: Handler) { handlers[name] = handler; } });
afterAll(() => rmSync(temp, { recursive: true, force: true }));

function response(stdout: string, exit = 0) {
  writeFileSync(cli, `import sys\nsys.stdout.write(${JSON.stringify(stdout)})\nsys.exit(${exit})\n`);
}

function call(toolName: string) {
  return handlers.tool_call({ toolName, input: { path: join(temp, "protected.txt") } }, { cwd: temp });
}

test("real extension enforces a valid deny and permits a valid allow", () => {
  response('{"block":true,"reason":"fixture denial"}');
  expect(call("write")).toEqual({ block: true, reason: "fixture denial" });
  response('{"block":false}');
  expect(call("write")).toBeUndefined();
});

for (const output of ["", "not json", "null", "[]", "false", "{}", '{"block":"false"}', '{"block":null}', '{"block":false,"error":"failed"}', '{"block":false,"reason":42}', 'noise\n{"block":false}']) {
  test(`invalid engine response ${JSON.stringify(output)} fails closed without blocking reads`, () => {
    response(output);
    expect(call("write")?.block).toBe(true);
    expect(call("read")).toBeUndefined();
  });
}

test("a failed engine cannot authorize through valid-looking stdout", () => {
  response('{"block":false}', 1);
  expect(call("bash")?.block).toBe(true);
  expect(call("read")).toBeUndefined();
});

test("missing engine covers every Python mutation alias and normalization", () => {
  rmSync(cli, { force: true });
  for (const tool of [
    "write", "edit", "MultiEdit", "multi_edit", "notebookedit", "notebook_edit",
    "apply_patch", "applypatch", "str_replace_editor", "create_file",
    "bash", "shell", "run_command", "exec", "terminal", "execute_command",
    "eval", "python", "python_repl", "execute_code", "run_code", "code_interpreter",
    "  Multi-Edit  ", " RUN-COMMAND ", "", "   ",
  ]) expect(call(tool)?.block).toBe(true);
  expect(call("read")).toBeUndefined();
});

test("timed-out engine fails closed for mutations", () => {
  writeFileSync(cli, "import time\ntime.sleep(30)\n");
  expect(call("eval")?.block).toBe(true);
}, 20000);
