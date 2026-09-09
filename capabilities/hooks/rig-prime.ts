// rig-prime (repo copy) — D85 deterministic-admission bridge for Orca/OMP.
//
// Live OMP config points here. Thin bridge: every gate invocation shells out to
// the single CLI implementation; this file contains no gate logic.
// Exit 0 = admit, exit 2 = BLOCK (fail closed). Any other exit is surfaced as an error.

import { execFile } from "node:child_process";

// Resolved per call so tests can override via env; the default is the production path.
const DEFAULT_CLI = "/Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-determinism-85/bin/rig-determinism-85";

interface ExtensionUI {
	notify?: (message: string, level: string) => void;
}
interface ExtensionContext {
	cwd?: string;
	ui?: ExtensionUI;
}
interface ToolResult {
	content: { type: "text"; text: string }[];
	isError?: boolean;
}
interface ExtensionAPI {
	zod: {
		object: (shape: Record<string, unknown>) => unknown;
		enum: (values: string[]) => { optional: () => unknown };
		string: () => { optional: () => { describe: (d: string) => unknown }; describe: (d: string) => unknown };
	};
	setLabel: (label: string) => void;
	on: (event: string, handler: (event: unknown, ctx: ExtensionContext) => Promise<unknown> | unknown) => void;
	registerTool: (definition: Record<string, unknown>) => void;
	registerCommand: (name: string, definition: { description: string; handler: (args: string, ctx: ExtensionContext) => Promise<string> | string }) => void;
}

interface D85Params {
	action: "inventory" | "classify" | "score" | "gate-d" | "wiring" | "select" | "checklist" | "estate-validate";
	process_id?: string;
	action_file?: string;
	build_file?: string;
	root?: string;
}
export function runGate(args: string[], timeoutMs = 60_000): Promise<[number, string]> {
	const cli = process.env.RIG_D85_CLI ?? DEFAULT_CLI;
	const { promise, resolve } = Promise.withResolvers<[number, string]>();
	try {
		execFile(cli, args, { timeout: timeoutMs, maxBuffer: 4 * 1024 * 1024 }, (error, stdout, stderr) => {
			// Fail closed: a spawn failure (ENOENT), timeout kill, or signal exit is
			// never code 0 — map it to -1 so callers treat it as an error, not admit.
			const code = error ? (typeof (error as { code?: number }).code === "number" ? (error as { code: number }).code : -1) : 0;
			const out = (stdout || stderr || (error ? `error: ${error.message}` : "")).trim();
			resolve([code, out]);
		});
	} catch (error) {
		resolve([-1, `error: ${String(error).slice(0, 200)}`]);
	}
	return promise;
}

export default function rigPrime(pi: ExtensionAPI): void {
	const z = pi.zod;
	pi.setLabel("RIG D85");

	pi.registerTool({
		name: "rig_d85",
		label: "RIG D85 Gate",
		description:
			"Deterministic-admission gates. action='score' runs the four-ratio D85 check, " +
			"action='gate-d' arms the exact-action outward gate (needs process_id + action_file), " +
			"action='wiring' verifies all four agent surfaces carry the doctrine marker, " +
			"action='select' maps an evidence file to the standard framework, " +
			"action='checklist' certifies a build checklist bound to a process inventory " +
			"(needs build_file + process_id; stale/mismatched/unbound all BLOCK), " +
			"action='estate-validate' checks the estate ledger's internal consistency. " +
			"BLOCK (exit 2) is terminal for the current attempt.",
		parameters: z.object({
			action: z.enum(["inventory", "classify", "score", "gate-d", "wiring", "select", "checklist", "estate-validate"]),
			process_id: z.string().optional().describe("process id from authority/registry.json"),
			action_file: z.string().optional().describe("path to exact pre-tool action envelope JSON (gate-d only)"),
			build_file: z.string().optional().describe("path to submitted build checklist JSON (checklist only)"),
			root: z.string().optional().describe("root dir resolving relative archify_diagram_path (checklist only)"),
		}),
		approval: (args: unknown) => ((args as D85Params | null)?.action === "gate-d" ? "write" : "read"),
		async execute(_id: string, rawParams: unknown): Promise<ToolResult> {
			const params = rawParams as D85Params;
			const args: string[] = [params.action];
			if (params.action === "select") {
				if (!params.build_file) {
					return { content: [{ type: "text", text: "select requires build_file (evidence file)" }], isError: true };
				}
				args.push(params.build_file);
			} else if (params.action === "checklist") {
				if (!params.build_file || !params.process_id) {
					return { content: [{ type: "text", text: "checklist requires build_file and process_id" }], isError: true };
				}
				args.push(params.build_file, "--process-id", params.process_id);
				if (params.root) args.push("--root", params.root);
			} else if (params.action === "estate-validate") {
				// no args — reads the skill-local ledger
			} else if (params.action !== "wiring") {
				if (!params.process_id) {
					return { content: [{ type: "text", text: `${params.action} requires process_id` }], isError: true };
				}
				args.push(params.process_id);
			}
			if (params.action === "gate-d") {
				if (!params.action_file) {
					return { content: [{ type: "text", text: "gate-d requires action_file" }], isError: true };
				}
				args.push("--action", params.action_file);
			}
			const [code, out] = await runGate(args);
			const text = out || "(no output)";
			// exit 2 = deterministic BLOCK — a valid verdict, not a tool error.
			return code === 0 || code === 2
				? { content: [{ type: "text", text }] }
				: { content: [{ type: "text", text: `gate runner failed (exit ${code}):\n${text}` }], isError: true };
		},
	});

	pi.registerCommand("d85", {
		description: "Run a D85 gate: /d85 score <process_id> | /d85 gate-d <process_id> <action_file> | /d85 select <evidence_file> | /d85 checklist <build_file> --process-id <id> | /d85 wiring",
		handler: async (argsStr: string, ctx: ExtensionContext) => {
			const argv = argsStr.trim().split(/\s+/).filter(Boolean);
			if (argv.length === 0) return "usage: /d85 <inventory|classify|score|gate-d|wiring> [process_id] [--action file]";
			const [code, out] = await runGate(argv);
			ctx.ui?.notify?.(out.slice(0, 2000), code === 0 ? "info" : "warn");
			return out;
		},
	});
}
