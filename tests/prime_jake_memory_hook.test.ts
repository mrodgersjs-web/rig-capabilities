// prime-jake-memory hook: invoke() must return the adapter's JSON on success and a
// labelled error (no backend fallback) on adapter failure.
// Run with: bun test tests/prime_jake_memory_hook.test.ts
import { describe, expect, test } from "bun:test";
import { EventEmitter } from "node:events";
import { PassThrough } from "node:stream";
import register, { invoke, registerMemory } from "../capabilities/hooks/prime-jake-memory.ts";

function fakeSpawn(stdout: string, exitCode: number) {
	return (() => {
		const child: any = new EventEmitter();
		child.pid = undefined;
		child.stdout = new PassThrough();
		child.stderr = new PassThrough();
		child.stdin = new PassThrough();
		queueMicrotask(() => {
			child.stdout.write(stdout);
			child.stdout.end();
			child.emit("close", exitCode);
		});
		return child;
	}) as any;
}

describe("prime-jake-memory invoke", () => {
	test("adapter JSON passes through on exit 0", async () => {
		const out = await invoke("omp", "turn", { prompt: "x" }, fakeSpawn('{"status":"ok","metadata":"m","reference_text":"r"}', 0));
		expect(out.status).toBe("ok");
		expect(out.reference_text).toBe("r");
	});
	test("non-zero exit becomes an explicit error with no fallback", async () => {
		const out = await invoke("omp", "turn", { prompt: "x" }, fakeSpawn("", 1));
		expect(out.status).toBe("error");
		expect(out.metadata).toContain("No direct backend fallback");
	});
	test("garbage stdout becomes an explicit error", async () => {
		const out = await invoke("omp", "startup", {}, fakeSpawn("not json", 0));
		expect(out.status).toBe("error");
	});
	test("extension registers supported preparation/reset/shutdown lifecycle handlers", () => {
		const seen: string[] = [];
		register({ on(name: string) { seen.push(name); }, registerTool() {} });
		expect(seen).toEqual(["input", "agent_start", "session_switch", "session_shutdown", "session_start", "before_agent_start"]);
	});
});

describe("Memory OS preparation lifecycle", () => {
	function harness(failed = false) {
		let calls = 0;
		let session = "a";
		const events = new Map<string, Function>();
		const ctx = { cwd: "/test", sessionManager: { getSessionId: () => session } };
		const lookup: any = async () => {
			calls++;
			return failed ? { status: "error", reference_text: "unavailable; retry next turn" }
				: { status: "ok", reference_text: "scoped untrusted reference" };
		};
		registerMemory({ on: (name: string, fn: Function) => events.set(name, fn) }, "omp", lookup);
		return { events, ctx, calls: () => calls, session: (value: string) => { session = value; },
			turn: (prompt = "same") => events.get("before_agent_start")!({ prompt }, ctx) };
	}
	test("policy reprepare shares concurrent and settled retrieval", async () => {
		const h = harness();
		await Promise.all([h.turn(), h.turn()]); await h.turn();
		expect(h.calls()).toBe(1);
	});
	test("same text refreshes on actual input and agent turn", async () => {
		const h = harness(); await h.turn();
		h.events.get("input")!({ source: "rpc", text: "same" }, h.ctx);
		await h.turn(); expect(h.calls()).toBe(2);
		h.events.get("agent_start")!({}, h.ctx);
		await h.turn(); expect(h.calls()).toBe(3);
	});
	test("session identity, switch and startup refresh retrieval", async () => {
		const h = harness(); await h.turn();
		h.session("b"); await h.turn(); expect(h.calls()).toBe(2);
		h.events.get("session_switch")!({}, h.ctx);
		await h.turn(); expect(h.calls()).toBe(3);
		await h.events.get("session_start")!({}, h.ctx); // startup lookup is separate
		await h.turn(); expect(h.calls()).toBe(5);
	});
	test("failure remains visible and retries only on the next input", async () => {
		const h = harness(true);
		expect((await h.turn()).message.content).toContain("retry next turn");
		await h.turn(); expect(h.calls()).toBe(1);
		h.events.get("input")!({}, h.ctx); await h.turn(); expect(h.calls()).toBe(2);
	});
	test("changed prompt or cwd refreshes retrieval", async () => {
		const h = harness(); await h.turn("a"); await h.turn("b");
		h.ctx.cwd = "/other"; await h.turn("b"); expect(h.calls()).toBe(3);
	});
	test("normal shutdown cancels and drains owned in-flight lookup", async () => {
		const events = new Map<string, Function>();
		let aborted = false;
		const lookup: any = (_r: string, _e: string, _p: any, _x: any, options: any) => new Promise(resolve => {
			options.signal.addEventListener("abort", () => { aborted = true; resolve({ status: "error", reference_text: "stale reference" }); });
		});
		registerMemory({ on: (name: string, fn: Function) => events.set(name, fn) }, "omp", lookup);
		const pending = events.get("before_agent_start")!({ prompt: "test" }, { cwd: "/test" });
		await events.get("session_shutdown")!();
		expect(aborted).toBe(true);
		expect((await pending).message.content).toContain("unavailable");
	});
});
